"use client";

import { useCallback, useEffect, useState } from "react";
import styles from "../config.module.css";
import { useLanguage } from "../../../i18n/context";
import { apiFetch, MATERIAL_ORDER, type RecipeRate } from "./shared";

export default function RecipesTab() {
  const { t } = useLanguage();
  const [rates, setRates] = useState<RecipeRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editKg, setEditKg] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const loadRates = useCallback(async () => {
    try {
      const data = await apiFetch<RecipeRate[]>("/api/v1/config/recipes");
      setRates(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { loadRates(); }, [loadRates]);

  const startEdit = (rate: RecipeRate) => {
    setEditingId(rate.id);
    setEditKg(String(rate.kg_per_day));
    setInfo(null);
  };

  const cancelEdit = () => { setEditingId(null); setEditKg(""); };

  const saveEdit = async (id: number) => {
    const kg = parseFloat(editKg);
    if (isNaN(kg) || kg <= 0) { setError(t("errorLoading")); return; }
    setSaving(true);
    try {
      await apiFetch(`/api/v1/config/recipes/${id}`, {
        method: "PUT",
        body: JSON.stringify({ kg_per_day: kg }),
      });
      setInfo(t("actionSave") + " ✓");
      cancelEdit();
      loadRates();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.loadingRow}>{t("loading")}</div>;

  const byFormat: Record<string, RecipeRate[]> = {};
  for (const r of rates) { byFormat[r.format_code] = byFormat[r.format_code] ?? []; byFormat[r.format_code].push(r); }
  const formatCodes = Object.keys(byFormat).sort();

  return (
    <div className={styles.tabContent}>
      <div className={styles.tabHeader}>
        <h2 className={styles.tabTitle}>{t("configRecipesTitle")}</h2>
        <span className={styles.tabHint}>{t("configRecipesHint")}</span>
      </div>
      {error && <div className={styles.errorMsg} role="alert">{error}<button onClick={() => setError(null)} style={{marginLeft:"0.5rem"}}>✕</button></div>}
      {info && <div className={styles.infoMsg}>{info}</div>}
      <div className={styles.recipeGrid}>
        <div className={styles.recipeHeaderRow}>
          <span className={styles.recipeHeaderCell}>{t("configColFormat")}</span>
          {MATERIAL_ORDER.map((m) => <span key={m} className={styles.recipeHeaderCell}>{m}</span>)}
        </div>
        {formatCodes.map((code) => (
          <div key={code} className={styles.recipeRow}>
            <span className={styles.recipeName}>{code.replace(/_/g, " ")}</span>
            {MATERIAL_ORDER.map((mat) => {
              const cell = byFormat[code].find((r) => r.material_type === mat);
              if (!cell) return <span key={mat} className={styles.recipeCell}>—</span>;
              const isEditing = editingId === cell.id;
              return (
                <span key={mat} className={styles.recipeCell}>
                  {isEditing ? (
                    <span className={styles.editCell}>
                      <input id={`edit-${cell.id}`} type="number" min="0" step="1"
                        value={editKg} onChange={(e) => setEditKg(e.target.value)}
                        className={styles.recipeInput} autoFocus />
                      <button id={`save-${cell.id}`} onClick={() => saveEdit(cell.id)}
                        disabled={saving} className={styles.saveBtn}>{saving ? "…" : "✓"}</button>
                      <button onClick={cancelEdit} className={styles.cancelBtn}>✕</button>
                    </span>
                  ) : (
                    <span className={styles.editableValue} onClick={() => startEdit(cell)} title={t("actionEdit")}>
                      {cell.kg_per_day}
                    </span>
                  )}
                </span>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
