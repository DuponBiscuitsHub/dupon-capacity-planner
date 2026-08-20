"""
app/core/odoo_client.py — Cliente JSON-RPC 2.0 para Odoo.

Síncrono (usa httpx.Client, no AsyncClient).
El sync engine corre en un thread pool (run_in_executor), no necesita async.

Paradigma: OOP — tiene estado: uid de sesión y modo (mock/real).
"""
import logging
from typing import Any

import httpx

from app.core.config import settings

_logger = logging.getLogger("app.odoo_client")


class OdooClient:
    """Cliente JSON-RPC 2.0 síncrono para la API externa de Odoo.

    Mantiene el uid de autenticación entre llamadas para evitar re-autenticar
    en cada sync. Una instancia por OdooSyncEngine (un sync, una instancia).
    """

    def __init__(self, base_url: str, db: str, user: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.db = db
        self.user = user
        self.api_key = api_key
        self.uid: int | None = None
        self._timeout = settings.ODOO_TIMEOUT_SECONDS

    # ── Auth ──────────────────────────────────────────────────────────────────

    def authenticate(self) -> int:
        """Autentica contra Odoo y cachea el uid.

        Reutiliza el uid si ya fue autenticado en esta instancia.
        """
        if self.uid is not None:
            return self.uid

        _logger.info(
            "Authenticating against Odoo",
            extra={"db": self.db, "user": self.user},
        )
        result = self._json_rpc("/jsonrpc", {
            "service": "common",
            "method": "authenticate",
            "args": [self.db, self.user, self.api_key, {}],
        })
        if not result:
            raise RuntimeError(
                f"Odoo authentication failed for user '{self.user}' on db '{self.db}'."
            )
        self.uid = int(result)
        _logger.info("Odoo auth OK", extra={"uid": self.uid})
        return self.uid

    # ── Public API ────────────────────────────────────────────────────────────

    def search_read(
        self,
        model: str,
        domain: list | None = None,
        fields: list | None = None,
        limit: int = 0,
        offset: int = 0,
    ) -> list[dict]:
        """Ejecuta search_read en Odoo.

        Returns:
            Lista de dicts con los campos solicitados.
        """
        uid = self.authenticate()
        return self._execute_kw(uid, model, "search_read", [domain or []], {
            "fields": fields or [],
            "limit": limit,
            "offset": offset,
        })

    def search_count(self, model: str, domain: list | None = None) -> int:
        uid = self.authenticate()
        return int(self._execute_kw(uid, model, "search_count", [domain or []], {}))

    def write(self, model: str, ids: list[int], vals: dict) -> bool:
        """Escribe campos en registros existentes de Odoo.

        Args:
            model: Modelo Odoo (ej. 'purchase.order.line')
            ids: Lista de IDs de registros a actualizar
            vals: Dict de campo→valor a escribir

        Returns:
            True si la escritura fue exitosa.
        """
        uid = self.authenticate()
        _logger.info(
            "Odoo write",
            extra={"model": model, "ids": ids, "fields": list(vals.keys())},
        )
        result = self._execute_kw(uid, model, "write", [ids, vals], {})
        return bool(result)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _execute_kw(
        self, uid: int, model: str, method: str, args: list, kwargs: dict
    ) -> Any:
        return self._json_rpc("/jsonrpc", {
            "service": "object",
            "method": "execute_kw",
            "args": [self.db, uid, self.api_key, model, method, args, kwargs],
        })

    def _json_rpc(self, endpoint: str, params: dict) -> Any:
        url = f"{self.base_url}{endpoint}"
        payload = {"jsonrpc": "2.0", "method": "call", "id": 1, "params": params}

        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.post(url, json=payload, headers={"Content-Type": "application/json"})
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"Odoo timeout on {endpoint}: {exc}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Odoo connection error on {endpoint}: {exc}") from exc

        if resp.status_code != 200:
            raise RuntimeError(f"Odoo HTTP {resp.status_code} on {endpoint}: {resp.text[:200]}")

        data = resp.json()
        if "error" in data:
            msg = (
                data["error"].get("data", {}).get("message")
                or data["error"].get("message", "Unknown RPC error")
            )
            raise RuntimeError(f"Odoo RPC error: {msg}")

        return data.get("result")
