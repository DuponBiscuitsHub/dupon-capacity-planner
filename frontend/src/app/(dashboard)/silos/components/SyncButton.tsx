"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import styles from "../silos.module.css";
import { useCompany } from "../../../context/CompanyContext";
import { useLanguage } from "../../../i18n/context";
import { apiFetch } from "./silosShared";

// ── Sync Overlay ───────────────────────────────────────────────────────────────

function SyncOverlay({ state, t }: {
  state: "syncing" | "recalc" | "done" | "error";
  t: (k: string) => string;
}) {
  const isSpinning = state === "syncing" || state === "recalc";
  const isError    = state === "error";

  const stepText =
    state === "recalc" ? t("syncOverlayStepRecalc") : t("syncOverlayStepSync");

  return createPortal(
    <div className={styles.syncOverlay} role="dialog" aria-live="polite">
      <div className={styles.syncOverlayCard}>

        {/* Ring — parado en error, girando en sync/recalc/done */}
        <div className={`${styles.syncRing} ${isError ? styles.syncRingError : ""}`}>
          <div className={`${styles.syncRingInner} ${isSpinning ? styles.syncRingSpinning : ""}`} />
        </div>

        {/* Título principal */}
        <p className={`${styles.syncOverlayTitle} ${isError ? styles.syncTitleError : ""}`}>
          {isError ? t("syncOverlayErrTitle") : t("syncOverlayTitle")}
        </p>

        {/* Subtexto según estado */}
        {isSpinning && (
          <p className={styles.syncOverlayStep}>{stepText}</p>
        )}
        {isError && (
          <p className={`${styles.syncOverlayStep} ${styles.syncOverlayErr}`}>
            {t("syncOverlayErrHint")}
          </p>
        )}
        {/* state==="done": overlay se cierra solo, sin texto adicional */}
      </div>
    </div>,
    document.body
  );
}

// ── Sync Button ─────────────────────────────────────────────────────────────────

export default function SyncButton({ onDone }: { onDone: () => void }) {
  const { companyId } = useCompany();
  const { t } = useLanguage();
  const [state, setState] = useState<"idle" | "syncing" | "recalc" | "done" | "error">("idle");
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleSync = async () => {
    if (state !== "idle" && state !== "done" && state !== "error") return;
    setState("syncing");
    try {
      await apiFetch("/api/v1/sync/run", { method: "POST" });
      setState("recalc");
      await apiFetch(`/api/v1/deliveries/recalculate?company_id=${companyId}`, { method: "POST" });
      setState("done");
      // Refresca datos silenciosamente mientras se muestra el overlay "done"
      onDone();
      timerRef.current = setTimeout(() => setState("idle"), 1800);
    } catch {
      setState("error");
      timerRef.current = setTimeout(() => setState("idle"), 3000);
    }
  };

  useEffect(() => () => { if (timerRef.current) clearTimeout(timerRef.current); }, []);

  const isOverlayVisible = state !== "idle";

  return (
    <>
      <button
        id="btn-sync"
        className={state === "done" ? styles.syncDone : state === "error" ? styles.syncError : styles.syncBtn}
        onClick={handleSync}
        disabled={state === "syncing" || state === "recalc"}
      >
        {t("silosSyncBtn")}
      </button>
      {isOverlayVisible && <SyncOverlay state={state as "syncing" | "recalc" | "done" | "error"} t={t} />}
    </>
  );
}
