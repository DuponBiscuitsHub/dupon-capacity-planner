"use client";

import { useState } from "react";
import styles from "../silos.module.css";
import { useLanguage } from "../../../i18n/context";
import { type PlanRow, apiFetch } from "./silosShared";

export default function EditDateModal({
  editRow,
  onClose,
  onSaved,
}: {
  editRow: PlanRow;
  onClose: () => void;
  onSaved: () => void;
}) {
  const { t } = useLanguage();
  const [sending, setSending] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  // Prefill with current PO date
  const initialDate = (() => {
    const current = editRow.po_date_planned || "";
    if (current) {
      const d = new Date(current);
      const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
      return local.toISOString().slice(0, 16);
    }
    return "";
  })();

  const [editDate, setEditDate] = useState(initialDate);

  async function submitEdit() {
    if (!editRow.po_line_odoo_id || !editDate) return;
    setSending(true);
    try {
      const isoDate = new Date(editDate).toISOString();
      await apiFetch<{ success: boolean }>(`/api/v1/delivery-planning/update-date`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          po_line_odoo_id: editRow.po_line_odoo_id,
          new_date: isoDate,
        }),
      });
      setToast(t("planUpdated"));
      onSaved();
      setTimeout(() => setToast(null), 3000);
    } catch (e) {
      setToast(e instanceof Error ? e.message : "Error");
      setTimeout(() => setToast(null), 4000);
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <div className={styles.editOverlay} onClick={onClose}>
        <div className={styles.editModal} onClick={(e) => e.stopPropagation()}>
          <h3 className={styles.editTitle}>
            {editRow.po_name}
          </h3>

          {/* Metadata: proveedor + referencia RM */}
          <div className={styles.editMeta}>
            {editRow.partner_name && (
              <span className={styles.editMetaChip}>🏭 {editRow.partner_name}</span>
            )}
            {editRow.product_ref && (
              <span className={styles.editMetaChip}>📦 {editRow.product_ref}</span>
            )}
          </div>

          {editRow.edit_warning === "poEditWarningConfirmed" && (
            <div className={styles.editWarning}>
              ⚠️ {t("planWarningConfirmed")}
            </div>
          )}

          {/* Fecha propuesta por la app (read-only) */}
          <div className={styles.editLabel}>
            {t("planColAppDate")}
            <div className={styles.editSuggestedRow}>
              <span className={styles.editSuggestedDate}>
                {editRow.app_suggested_date
                  ? new Date(editRow.app_suggested_date).toLocaleString(
                      undefined, { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" }
                    )
                  : t("planNoSuggested")}
              </span>
              {editRow.app_suggested_date && (
                <button
                  type="button"
                  className={styles.editUseSuggestedBtn}
                  onClick={() => {
                    const d = new Date(editRow.app_suggested_date!);
                    const pad = (n: number) => String(n).padStart(2, "0");
                    const local = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
                    setEditDate(local);
                  }}
                >
                  ↓ {t("planUseSuggested")}
                </button>
              )}
            </div>
          </div>

          {/* Fecha actual PO (editable) */}
          <label className={styles.editLabel}>
            {t("planColPODate")}
            <input
              type="datetime-local"
              className={styles.editDateInput}
              value={editDate}
              onChange={(e) => setEditDate(e.target.value)}
            />
          </label>

          <div className={styles.editActions}>
            <button
              className={styles.editCancelBtn}
              onClick={onClose}
              disabled={sending}
            >
              {t("planCancel")}
            </button>
            <button
              className={styles.editConfirmBtn}
              onClick={submitEdit}
              disabled={sending || !editDate}
            >
              {sending ? "…" : t("planConfirmSend")}
            </button>
          </div>
        </div>
      </div>

      {/* Toast */}
      {toast && <div className={styles.editToast}>{toast}</div>}
    </>
  );
}
