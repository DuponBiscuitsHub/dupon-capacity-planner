"use client";

import { useCallback, useEffect, useState } from "react";
import styles from "../config.module.css";
import { useLanguage } from "../../../i18n/context";
import { apiFetch, type LineCapacity } from "./shared";

export default function LinesTab() {
  const { t } = useLanguage();
  const [lines, setLines] = useState<LineCapacity[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingCode, setEditingCode] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<Partial<LineCapacity>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await apiFetch<LineCapacity[]>("/api/v1/config/lines");
      setLines(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const startEdit = (line: LineCapacity) => {
    setEditingCode(line.line_code);
    setEditValues({ capacity_kg_h: line.capacity_kg_h, is_active: line.is_active });
  };

  const cancelEdit = () => { setEditingCode(null); setEditValues({}); };

  const saveEdit = async (code: string) => {
    setSaving(true);
    setError(null);
    try {
      const updated = await apiFetch<LineCapacity>(`/api/v1/config/lines/${code}`, {
        method: "PUT",
        body: JSON.stringify({ capacity_kg_h: editValues.capacity_kg_h, is_active: editValues.is_active }),
      });
      setLines((prev) => prev.map((l) => (l.line_code === code ? updated : l)));
      setEditingCode(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.loading}>{t("loading")}</div>;

  return (
    <div className={styles.tabContent}>
      <p className={styles.tabDesc}>{t("configLinesDesc")}</p>
      {error && <div role="alert" className={styles.errorMsg}>{error}</div>}
      <div className={styles.tableWrap}>
        <table id="table-lines" className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>{t("configColLine")}</th>
              <th className={styles.th}>{t("configColStatus")}</th>
              <th className={styles.th}>{t("configColKgH")}</th>
              <th className={styles.th}></th>
            </tr>
          </thead>
          <tbody>
            {lines.map((line) => (
              <tr key={line.line_code} className={styles.tr}>
                <td className={styles.td}>
                  <strong>{line.line_code}</strong>
                </td>
                <td className={styles.td}>
                  {editingCode === line.line_code ? (
                    <label className={styles.toggle}>
                      <input
                        type="checkbox"
                        checked={!!editValues.is_active}
                        onChange={(e) => setEditValues((v) => ({ ...v, is_active: e.target.checked }))}
                      />
                      <span>{editValues.is_active ? t("statusProducing") : t("statusIdle")}</span>
                    </label>
                  ) : (
                    <span className={line.is_active ? styles.activeTag : styles.idleTag}>
                      {line.is_active ? t("statusProducingBullet") : t("statusIdleBullet")}
                    </span>
                  )}
                </td>
                <td className={styles.td}>
                  {editingCode === line.line_code ? (
                    <input
                      id={`input-kgh-${line.line_code}`}
                      type="number"
                      min={0}
                      step={10}
                      className={styles.numberInput}
                      value={editValues.capacity_kg_h ?? 0}
                      onChange={(e) =>
                        setEditValues((v) => ({ ...v, capacity_kg_h: Number(e.target.value) }))
                      }
                    />
                  ) : (
                    <span className={styles.kgValue}>{line.capacity_kg_h.toLocaleString()} kg/h</span>
                  )}
                </td>
                <td className={styles.tdActions}>
                  {editingCode === line.line_code ? (
                    <div className={styles.editActions}>
                      <button
                        id={`btn-save-${line.line_code}`}
                        className={styles.saveBtn}
                        disabled={saving}
                        onClick={() => saveEdit(line.line_code)}
                      >
                        {saving ? t("actionSaving") : t("actionSave")}
                      </button>
                      <button className={styles.cancelBtn} onClick={cancelEdit}>
                        {t("actionCancel")}
                      </button>
                    </div>
                  ) : (
                    <button
                      id={`btn-edit-${line.line_code}`}
                      className={styles.editBtn}
                      onClick={() => startEdit(line)}
                    >
                      {t("actionEdit")}
                    </button>
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
