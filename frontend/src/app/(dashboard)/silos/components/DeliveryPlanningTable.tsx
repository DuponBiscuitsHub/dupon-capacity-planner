"use client";

import { useLanguage } from "../../../i18n/context";
import { type PlanRow, fmtKg } from "./silosShared";
import styles from "./DeliveryPlanningTable.module.css";

// ── Helpers ─────────────────────────────────────────────────────────────────────

function fmtDate(iso: string | null, locale: string): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString(locale, {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

const MATERIAL_ICON: Record<string, string> = {
  harina: "🌾",
  azucar: "🍬",
  aceite: "🫒",
};

// ── Component ───────────────────────────────────────────────────────────────────

interface Props {
  planRows: PlanRow[];
  forecastDays: number;
  onEdit: (row: PlanRow) => void;
}

export default function DeliveryPlanningTable({ planRows, forecastDays, onEdit }: Props) {
  const { t } = useLanguage();
  const locale = t("_locale") || "es-ES";

  const STATE_LABELS: Record<string, string> = {
    draft: t("planStateDraft"),
    sent: t("planStateSent"),
    purchase: t("planStatePurchase"),
    done: t("planStateDone"),
  };

  // Filtrar por ventana de forecast
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() + forecastDays);
  const rows = planRows.filter((r) => {
    const refDate = r.po_date_planned || r.app_suggested_date;
    if (!refDate) return true;
    return new Date(refDate) <= cutoff;
  });

  return (
    <div className={styles.wrapper}>
      <div className={styles.tableScroll}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{t("planColMaterial")}</th>
              <th>{t("planColPO")}</th>
              <th>{t("planColQty")}</th>
              <th>{t("planColPODate")}</th>
              <th>{t("planColAppDate")}</th>
              <th>{t("planColState")}</th>
              <th>{t("planColAction")}</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td colSpan={7} className={styles.emptyRow}>
                  {t("planNoPO")}
                </td>
              </tr>
            )}
            {rows.map((row, i) => (
              <tr
                key={row.po_line_odoo_id ?? `no-po-${i}`}
                className={styles[`row_${row.timing_color}`]}
              >
                <td className={styles.materialCell}>
                  <span className={styles.materialIcon}>
                    {MATERIAL_ICON[row.material_type] ?? "📦"}
                  </span>
                  {t(`mat${row.material_type.charAt(0).toUpperCase() + row.material_type.slice(1)}`)}
                </td>
                <td className={styles.poCell}>
                  {row.po_name ?? t("planNoPO")}
                </td>
                <td>{fmtKg(row.po_qty_kg)}</td>
                <td>{fmtDate(row.po_date_planned, locale)}</td>
                <td className={styles.appDateCell}>
                  {fmtDate(row.app_suggested_date, locale)}
                </td>
                <td>
                  <span className={`${styles.stateBadge} ${styles[`state_${row.po_state ?? "none"}`]}`}>
                    {row.po_state ? STATE_LABELS[row.po_state] ?? row.po_state : "—"}
                  </span>
                </td>
                <td>
                  {row.can_edit && row.po_line_odoo_id && (
                    <button
                      className={styles.editBtn}
                      onClick={() => onEdit(row)}
                      title={t("planBtnEditDate")}
                    >
                      ✏️
                    </button>
                  )}
                  {!row.can_edit && row.po_state === "done" && (
                    <span className={styles.blockedIcon} title={t("planBlockedDone")}>
                      🔒
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
