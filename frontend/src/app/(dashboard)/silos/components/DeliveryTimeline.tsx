"use client";

import { useMemo } from "react";
import styles from "../silos.module.css";
import { useLanguage } from "../../../i18n/context";
import { type SiloStatus, type PlanRow, fmtKg, fmtPct, dayLabel } from "./silosShared";

// ── PO pill (traffic light) ───────────────────────────────────────────────────

function POPill({ row, onEdit }: { row: PlanRow; onEdit: (r: PlanRow) => void }) {
  const { t } = useLanguage();

  // Background = timing vs app calculation
  const bgCls =
    row.timing_color === "green"  ? styles.pillBgGreen :
    row.timing_color === "orange" ? styles.pillBgOrange :
                                     styles.pillBgRed;

  // Border-left = vendor confirmation
  const borderCls = row.vendor_confirmed
    ? styles.pillBorderConfirmed
    : styles.pillBorderUnconfirmed;

  const isClickable = row.can_edit && !!row.po_line_odoo_id;

  return (
    <div
      className={`${styles.pill} ${bgCls} ${borderCls} ${isClickable ? styles.pillClickable : ""}`}
      title={`${row.po_name ?? t("planNoPO")} · ${fmtKg(row.po_qty_kg)}`}
      onClick={isClickable ? () => onEdit(row) : undefined}
      role={isClickable ? "button" : undefined}
      tabIndex={isClickable ? 0 : undefined}
    >
      {row.po_name && <span className={styles.pillPo}>{row.po_name}</span>}
      <span className={styles.pillQty}>{fmtKg(row.po_qty_kg)}</span>
    </div>
  );
}

// ── Delivery Timeline (Gantt horizontal) ──────────────────────────────────────

export default function DeliveryTimeline({
  silos,
  planRows,
  materialFilter,
  forecastDays,
  onEdit,
}: {
  silos: SiloStatus[];
  planRows: PlanRow[];
  materialFilter: Set<string>;
  forecastDays: number;
  onEdit: (row: PlanRow) => void;
}) {
  const { t } = useLanguage();
  const locale = t("_locale") || "es-ES";
  const today = useMemo(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  }, []);

  const days = useMemo(() => {
    return Array.from({ length: forecastDays }, (_, i) => {
      const d = new Date(today);
      d.setDate(d.getDate() + i);
      return d;
    });
  }, [today, forecastDays]);

  const rows = silos.filter(s =>
    materialFilter.size === 0 || materialFilter.has(s.material_type)
  );

  // Asignar cada PlanRow al primer silo de su material_type
  const firstSiloByMaterial: Record<string, string> = {};
  for (const s of rows) {
    if (!(s.material_type in firstSiloByMaterial)) {
      firstSiloByMaterial[s.material_type] = s.silo_code;
    }
  }

  const byKey: Record<string, PlanRow[]> = {};
  for (const pr of planRows) {
    if (materialFilter.size > 0 && !materialFilter.has(pr.material_type)) continue;
    const dateStr = pr.po_date_planned || pr.app_suggested_date;
    if (!dateStr) continue;
    const date = new Date(dateStr);
    date.setHours(0, 0, 0, 0);
    const siloCode = firstSiloByMaterial[pr.material_type];
    if (!siloCode) continue;
    const key = `${siloCode}_${date.toISOString().slice(0, 10)}`;
    byKey[key] = byKey[key] ?? [];
    byKey[key].push(pr);
  }

  return (
    <div className={styles.timeline}>
      <div className={styles.timelineHeader}>
        <div className={styles.timelineYLabel} />
        {days.map(d => {
          const isToday = d.toDateString() === today.toDateString();
          return (
            <div key={d.toISOString()} className={`${styles.timelineDayCol} ${isToday ? styles.timelineToday : ""}`}>
              <span className={styles.timelineDayLabel}>{dayLabel(d, locale)}</span>
            </div>
          );
        })}
      </div>

      {rows.map(silo => (
        <div key={silo.silo_code} className={styles.timelineRow}>
          <div className={styles.timelineYLabel}>
            <span className={styles.timelineRowCode}>{silo.silo_code}</span>
            <span className={styles.timelineRowStatus}
              style={{ color:
                silo.status === "critical" ? "var(--color-danger)" :
                silo.status === "warning"  ? "var(--color-warning)" :
                                             "var(--text-muted)" }}>
              {fmtPct(silo.fill_pct)}
            </span>
          </div>
          {days.map(d => {
            const key = `${silo.silo_code}_${d.toISOString().slice(0, 10)}`;
            const entries = byKey[key] ?? [];
            const isToday = d.toDateString() === today.toDateString();
            return (
              <div key={d.toISOString()} className={`${styles.timelineCell} ${isToday ? styles.timelineTodayCell : ""}`}>
                {entries.map((pr, idx) => (
                  <POPill key={pr.po_line_odoo_id ?? `no-po-${idx}`} row={pr} onEdit={onEdit} />
                ))}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}
