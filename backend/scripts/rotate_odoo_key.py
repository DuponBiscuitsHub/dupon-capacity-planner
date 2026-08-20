"""
scripts/rotate_odoo_key.py — CLI para rotar la API key de Odoo en .env.

Caso de uso principal: tras un rebuild de staging, la API key anterior
se invalida. Este script actualiza .env y verifica la conexión.

Uso:
  cd backend

  # Solo cambiar la API key:
  python -m scripts.rotate_odoo_key --key "nueva_api_key_abc123"

  # Cambiar key + DB (post-rebuild staging):
  python -m scripts.rotate_odoo_key \\
    --key "nueva_api_key" \\
    --db "dupon-biscuits-iberica-sa-build-00016699"

  # Cambiar todo (nueva instancia staging):
  python -m scripts.rotate_odoo_key \\
    --key "nueva_api_key" \\
    --url "https://dupon-staging4.processcontrol.sh" \\
    --db "dupon-biscuits-iberica-sa-build-00016699"

  # Interactivo (pide la key por stdin, sin eco):
  python -m scripts.rotate_odoo_key

  # Solo verificar la conexión actual (sin cambiar nada):
  python -m scripts.rotate_odoo_key --verify
"""
import argparse
import getpass
import os
import re
import sys
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Variables que este script puede tocar (nada más)
_ALLOWED_VARS = {"ODOO_API_KEY", "ODOO_URL", "ODOO_DB", "ODOO_USER"}


def _read_env(path: Path) -> list[str]:
    """Lee el .env como lista de líneas preservando formato."""
    if not path.exists():
        print(f"ERROR: {path} no encontrado.", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def _update_env_var(lines: list[str], var: str, value: str) -> list[str]:
    """Reemplaza el valor de una variable en las líneas del .env.

    Solo toca líneas que empiezan con VAR= (no comentadas).
    """
    pattern = re.compile(rf"^{re.escape(var)}\s*=.*$")
    found = False
    result = []
    for line in lines:
        stripped = line.rstrip("\n")
        if pattern.match(stripped):
            result.append(f"{var}={value}\n")
            found = True
        else:
            result.append(line if line.endswith("\n") else line + "\n")
    if not found:
        # Variable no existía, la añadimos al final
        result.append(f"{var}={value}\n")
    return result


def _write_env(path: Path, lines: list[str]) -> None:
    """Escribe las líneas al .env."""
    path.write_text("".join(lines), encoding="utf-8")


def _verify_connection(env_path: Path) -> bool:
    """Intenta authenticate() con los valores actuales del .env."""
    # Importar después de sys.path para que encuentre app.*
    sys.path.insert(0, str(env_path.parent))

    # Leer los valores directamente del .env (sin cargar config.py global)
    env_vars: dict[str, str] = {}
    for line in _read_env(env_path):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _, v = stripped.partition("=")
            env_vars[k.strip()] = v.strip().strip('"').strip("'")

    odoo_url = env_vars.get("ODOO_URL", "")
    odoo_db = env_vars.get("ODOO_DB", "")
    odoo_user = env_vars.get("ODOO_USER", "")
    odoo_key = env_vars.get("ODOO_API_KEY", "")

    if not all([odoo_url, odoo_db, odoo_user, odoo_key]):
        print("ERROR: Faltan variables ODOO_* en .env.", file=sys.stderr)
        return False

    print(f"  URL:  {odoo_url}")
    print(f"  DB:   {odoo_db}")
    print(f"  User: {odoo_user}")
    print(f"  Key:  {odoo_key[:8]}...{odoo_key[-4:]}")
    print()

    try:
        import httpx

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "id": 1,
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [odoo_db, odoo_user, odoo_key, {}],
            },
        }
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                f"{odoo_url}/jsonrpc",
                json=payload,
                headers={"Content-Type": "application/json"},
            )

        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            return False

        data = resp.json()
        if "error" in data:
            msg = (
                data["error"].get("data", {}).get("message")
                or data["error"].get("message", "Unknown error")
            )
            print(f"❌ Odoo RPC error: {msg}", file=sys.stderr)
            return False

        uid = data.get("result")
        if not uid:
            print("❌ Autenticación fallida (uid vacío). API key incorrecta o usuario sin acceso.", file=sys.stderr)
            return False

        print(f"✅ Conexión OK — uid={uid}")
        return True

    except httpx.TimeoutException:
        print("❌ Timeout al conectar con Odoo (15s).", file=sys.stderr)
        return False
    except httpx.RequestError as exc:
        print(f"❌ Error de conexión: {exc}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"❌ Error inesperado: {exc}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rotar la API key de Odoo en backend/.env y verificar conexión.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python -m scripts.rotate_odoo_key --key "abc123"
  python -m scripts.rotate_odoo_key --key "abc123" --db "nueva-bd-staging"
  python -m scripts.rotate_odoo_key --verify
  python -m scripts.rotate_odoo_key   # interactivo
        """,
    )
    parser.add_argument("--key", help="Nueva ODOO_API_KEY")
    parser.add_argument("--url", help="Nueva ODOO_URL (opcional)")
    parser.add_argument("--db", help="Nuevo ODOO_DB (opcional)")
    parser.add_argument("--user", help="Nuevo ODOO_USER (opcional)")
    parser.add_argument(
        "--verify", action="store_true",
        help="Solo verificar la conexión actual sin cambiar nada",
    )
    args = parser.parse_args()

    if args.verify:
        print("🔍 Verificando conexión con Odoo...\n")
        ok = _verify_connection(_ENV_PATH)
        sys.exit(0 if ok else 1)

    # Si no se pasa --key, pedir interactivamente
    new_key = args.key
    if not new_key:
        new_key = getpass.getpass("Nueva ODOO_API_KEY: ").strip()
        if not new_key:
            print("ERROR: API key no puede estar vacía.", file=sys.stderr)
            sys.exit(1)

    # Leer y actualizar .env
    lines = _read_env(_ENV_PATH)
    changes: list[str] = []

    lines = _update_env_var(lines, "ODOO_API_KEY", new_key)
    changes.append(f"  ODOO_API_KEY = {new_key[:8]}...{new_key[-4:]}")

    if args.url:
        lines = _update_env_var(lines, "ODOO_URL", args.url)
        changes.append(f"  ODOO_URL     = {args.url}")

    if args.db:
        lines = _update_env_var(lines, "ODOO_DB", args.db)
        changes.append(f"  ODOO_DB      = {args.db}")

    if args.user:
        lines = _update_env_var(lines, "ODOO_USER", args.user)
        changes.append(f"  ODOO_USER    = {args.user}")

    # Escribir cambios
    _write_env(_ENV_PATH, lines)
    print("📝 .env actualizado:")
    for c in changes:
        print(c)
    print()

    # Verificar conexión
    print("🔍 Verificando conexión con Odoo...\n")
    ok = _verify_connection(_ENV_PATH)

    if not ok:
        print("\n⚠️  El .env se ha actualizado pero la conexión ha fallado.")
        print("    Verifica la API key, URL y DB name.")
        sys.exit(1)


if __name__ == "__main__":
    main()
