"use client";

import { useCallback, useEffect, useState } from "react";
import styles from "../config.module.css";
import { useLanguage } from "../../../i18n/context";
import { apiFetch, type SiloConfig } from "./shared";

export default function SilosTab() {
  const { t } = useLanguage();
  const [silos, setSilos] = useState<SiloConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<Partial<SiloConfig>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await apiFetch<SiloConfig[]>("/api/v1/config/silos");
      setSilos(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const startEdit = (silo: SiloConfig) => {
    setEditingId(silo.id);
    setEditValues({ safety_stock_kg: silo.safety_stock_kg, capacity_kg: silo.capacity_kg });
  };

  const saveEdit = async (silo: SiloConfig) => {
    setSaving(true);
    setError(null);
    try {
      const updated = await apiFetch<SiloConfig>(`/api/v1/config/silos/${silo.id}`, {
        method: "PUT",
        body: JSON.stringify(editValues),
      });
      setSilos((prev) => prev.map((s) => (s.id === silo.id ? updated : s)));
      setEditingId(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.loading}>{t("loading")}</div>;

  return (
    <div className={styles.tabContent}>
      <p className={styles.tabDesc}>{t("configSilosDesc")}</p>
      {error && <div role="alert" className={styles.errorMsg}>{error}</div>}
      <div className={styles.tableWrap}>
        <table id="table-silos-config" className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>{t("configColCode")}</th>
              <th className={styles.th}>{t("configColMaterial")}</th>
              <th className={styles.th}>{t("configColCapacity")}</th>
              <th className={styles.th}>{t("configColSafety")}</th>
              <th className={styles.th}></th>
            </tr>
          </thead>
          <tbody>
            {silos.map((silo) => (
              <tr key={silo.id} className={styles.tr}>
                <td className={styles.td}><strong>{silo.silo_code}</strong><br /><span className={styles.siloName}>{silo.name}</span></td>
                <td className={styles.td}><span className={styles.materialTag}>{silo.material_type}</span></td>
                <td className={styles.td}>
                  {editingId === silo.id ? (
                    <input type="number" min={0} step={1000} className={styles.numberInput}
                      value={editValues.capacity_kg ?? 0}
                      onChange={(e) => setEditValues((v) => ({ ...v, capacity_kg: Number(e.target.value) }))}
                    />
                  ) : (
                    <span>{silo.capacity_kg.toLocaleString()}</span>
                  )}
                </td>
                <td className={styles.td}>
                  {editingId === silo.id ? (
                    <input id={`input-safety-${silo.id}`} type="number" min={0} step={500} className={styles.numberInput}
                      value={editValues.safety_stock_kg ?? 0}
                      onChange={(e) => setEditValues((v) => ({ ...v, safety_stock_kg: Number(e.target.value) }))}
                    />
                  ) : (
                    <span>{silo.safety_stock_kg.toLocaleString()}</span>
                  )}
                </td>
                <td className={styles.tdActions}>
                  {editingId === silo.id ? (
                    <div className={styles.editActions}>
                      <button id={`btn-save-silo-${silo.id}`} className={styles.saveBtn} disabled={saving}
                        onClick={() => saveEdit(silo)}>{saving ? t("actionSaving") : t("actionSave")}</button>
                      <button className={styles.cancelBtn} onClick={() => setEditingId(null)}>{t("actionCancel")}</button>
                    </div>
                  ) : (
                    <button id={`btn-edit-silo-${silo.id}`} className={styles.editBtn} onClick={() => startEdit(silo)}>{t("actionEdit")}</button>
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
