"use client";

import styles from "../silos.module.css";
import { type SiloStatus, fmtKg, getMatLabelShort } from "./silosShared";

export function SiloGaugeLarge({ silo, t }: { silo: SiloStatus; t: (k: string) => string }) {
  const pct = silo.fill_pct ?? 0;

  const fillColor =
    silo.status === "critical" ? "var(--color-danger)" :
    silo.status === "warning"  ? "var(--color-warning)" :
                                 "var(--color-success)";

  const statusCls =
    silo.status === "critical" ? styles.gaugeCritical :
    silo.status === "warning"  ? styles.gaugeWarning  :
    silo.status === "ok"       ? styles.gaugeOk       : "";

  const matLabelCls =
    silo.status === "critical" ? styles.matLabelDanger :
    silo.status === "warning"  ? styles.matLabelWarning :
                                 styles.matLabelOk;

  return (
    <div className={`${styles.gaugeCard} ${statusCls}`}>
      <div className={`${styles.matLabel} ${matLabelCls}`}>
        {getMatLabelShort(silo.material_type, t)}
      </div>
      <div className={styles.gaugeName}>{silo.name}</div>

      <div className={styles.barOuter}>
        <div
          className={styles.barFill}
          style={{ height: `${Math.min(pct, 100)}%`, background: fillColor }}
        />
        <div className={styles.safetyLine} title={t("siloSafetyStock")} />
      </div>

      <div className={styles.gaugeInfo}>
        <div
          className={styles.pctValue}
          style={{ color: pct < 20 ? "var(--color-danger)" : pct < 40 ? "var(--color-warning)" : "var(--text-primary)" }}
        >
          {silo.current_stock_kg !== null ? `${Math.round(pct)}%` : "—"}
        </div>
        {silo.current_stock_kg !== null && (
          <div className={styles.kgValue}>
            {fmtKg(silo.current_stock_kg)} / {fmtKg(silo.capacity_kg)}
          </div>
        )}
      </div>
    </div>
  );
}

export function MaterialSection({ label, silos, t }: { label: string; silos: SiloStatus[]; t: (k: string) => string }) {
  return (
    <div className={styles.materialBlock}>
      <div className={styles.materialLabel}>{label}</div>
      <div className={styles.gaugesRow}>
        {silos.map(s => <SiloGaugeLarge key={s.silo_code} silo={s} t={t} />)}
      </div>
    </div>
  );
}
