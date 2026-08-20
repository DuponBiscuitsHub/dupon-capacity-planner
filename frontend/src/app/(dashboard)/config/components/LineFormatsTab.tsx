"use client";

import { useCallback, useEffect, useState } from "react";
import styles from "../config.module.css";
import { useLanguage } from "../../../i18n/context";
import { apiFetch, ROTARY_LINES, type LineFormatItem } from "./shared";

export default function LineFormatsTab() {
  const { t } = useLanguage();
  const [items, setItems] = useState<LineFormatItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editMachines, setEditMachines] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await apiFetch<LineFormatItem[]>("/api/v1/config/line-formats");
      setItems(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const save = async (id: number) => {
    const m = parseInt(editMachines, 10);
    if (isNaN(m) || m <= 0) { setError(t("errorLoading")); return; }
    setSaving(true);
    try {
      await apiFetch(`/api/v1/config/line-formats/${id}`, {
        method: "PUT",
        body: JSON.stringify({ machines: m }),
      });
      setEditingId(null);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.loadingRow}>{t("loading")}</div>;

  const byLine: Record<string, LineFormatItem[]> = {};
  for (const it of items) { byLine[it.line_code] = byLine[it.line_code] ?? []; byLine[it.line_code].push(it); }
  const lineCodes = Object.keys(byLine).sort();

  return (
    <div className={styles.tabContent}>
      <div className={styles.tabHeader}>
        <h2 className={styles.tabTitle}>{t("configLineFormatsTitle")}</h2>
        <span className={styles.tabHint}>{t("configLineFormatsHint")}</span>
      </div>
      {error && <div className={styles.errorMsg} role="alert">{error}<button onClick={() => setError(null)} style={{marginLeft:"0.5rem"}}>✕</button></div>}
      <table className={styles.dataTable}>
        <thead>
          <tr>
            <th>{t("configColLine")}</th>
            <th>{t("configColType")}</th>
            <th>{t("configColFormat")}</th>
            <th>{t("configColMachines")}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {lineCodes.map((line) => {
            const isRotary = ROTARY_LINES.has(line);
            const typeBadge = isRotary ? t("lineTypeRotary") : t("lineTypeLinear");
            const typeCls   = isRotary ? styles.badgeRotary : styles.badgeLinear;
            return byLine[line].map((lf, i) => (
              <tr key={lf.id}>
                {i === 0 && <td rowSpan={byLine[line].length} className={styles.lineCell}>{line}</td>}
                {i === 0 && (
                  <td rowSpan={byLine[line].length}>
                    <span className={`${styles.typeBadge} ${typeCls}`}>{typeBadge}</span>
                  </td>
                )}
                <td>{lf.format_code.replace(/_/g, " ")}</td>
                <td>
                  {editingId === lf.id ? (
                    <input type="number" min="1" max="9" value={editMachines}
                      onChange={(e) => setEditMachines(e.target.value)}
                      className={styles.recipeInput} autoFocus />
                  ) : (
                    lf.machines
                  )}
                </td>
                <td>
                  {isRotary ? (
                    editingId === lf.id ? (
                      <>
                        <button onClick={() => save(lf.id)} disabled={saving}
                          className={styles.saveBtn}>{saving ? "…" : "✓"}</button>
                        <button onClick={() => setEditingId(null)}
                          className={styles.cancelBtn}>✕</button>
                      </>
                    ) : (
                      <button onClick={() => { setEditingId(lf.id); setEditMachines(String(lf.machines)); }}
                        className={styles.editBtn}>✏️</button>
                    )
                  ) : (
                    // Hornos lineales: siempre 1 máquina, no editable
                    <span className={styles.lockIcon} title={t("lineTypeLinear")}>🔒</span>
                  )}
                </td>
              </tr>
            ));
          })}
        </tbody>
      </table>
    </div>
  );
}
