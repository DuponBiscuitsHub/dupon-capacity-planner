"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import styles from "./silos.module.css";
import { useCompany } from "../../context/CompanyContext";
import { useLanguage } from "../../i18n/context";
import { type SiloStatus, type PlanRow, apiFetch, getMatLabelLong } from "./components/silosShared";
import { MaterialSection } from "./components/SiloGauge";
import DeliveryTimeline from "./components/DeliveryTimeline";
import DeliveryPlanningTable from "./components/DeliveryPlanningTable";
import SyncButton from "./components/SyncButton";
import { ForecastDropdown, MaterialFilter } from "./components/TimelineControls";
import EditDateModal from "./components/EditDateModal";

export default function SilosPage() {
  const { companyId } = useCompany();
  const { t } = useLanguage();
  const [silos, setSilos]             = useState<SiloStatus[]>([]);
  const [planRows, setPlanRows]       = useState<PlanRow[]>([]);
  const [loading, setLoading]         = useState(true);
  const [refreshing, setRefreshing]   = useState(false);
  const [error, setError]             = useState<string | null>(null);
  const [matFilter, setMatFilter]     = useState<Set<string>>(new Set());
  const [forecastDays, setForecastDays] = useState(30);
  const [lastSyncAt, setLastSyncAt]   = useState<string | null>(null);
  const [editRow, setEditRow]         = useState<PlanRow | null>(null);

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    else setRefreshing(true);
    try {
      const [s, plan, syncInfo] = await Promise.all([
        apiFetch<SiloStatus[]>(`/api/v1/silos?company_id=${companyId}`),
        apiFetch<PlanRow[]>(`/api/v1/delivery-planning?company_id=${companyId}`),
        apiFetch<{ last_sync_at: string | null }>(`/api/v1/sync/last`),
      ]);
      setSilos(s);
      setPlanRows(plan);
      setLastSyncAt(syncInfo.last_sync_at);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [companyId, t]);

  useEffect(() => { load(); }, [load]);

  const byMaterial: Record<string, SiloStatus[]> = {};
  for (const s of silos) {
    byMaterial[s.material_type] = byMaterial[s.material_type] ?? [];
    byMaterial[s.material_type].push(s);
  }

  // ── Last sync label ───────────────────────────────────────────────────────
  const lastSyncLabel = useMemo(() => {
    if (!lastSyncAt) return t("silosSyncNever") ?? "—";
    const diff = Date.now() - new Date(lastSyncAt).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return t("silosSyncJustNow") ?? "< 1 min";
    if (mins < 60) return `${mins} min`;
    const hrs = Math.floor(mins / 60);
    return `${hrs}h ${mins % 60}m`;
  }, [lastSyncAt, t]);

  if (loading) return <div className={styles.loading}>{t("loading")}</div>;
  if (error)   return <div className={styles.errorMsg}>{t("errorLoading")}: {error}</div>;

  return (
    <div className={styles.page}>

      {/* ── Sección silos por material ── */}
      <section className={styles.silosSection}>
        {Object.entries(byMaterial).map(([mat, matSilos]) => (
          <MaterialSection
            key={mat}
            label={getMatLabelLong(mat, t)}
            silos={matSilos}
            t={t}
          />
        ))}
      </section>

      {/* ── Sección timeline entregas ── */}
      <section className={styles.timelineSection}>
        <div className={styles.timelineHeader2}>
          <div className={styles.timelineTitle}>
            <span>{t("silosDeliveryPlanning")}</span>
            <span className={styles.timelineSubtitle}>
              {t("silosNextDays").replace("{n}", String(forecastDays))}
            </span>
            {lastSyncAt && (
              <span className={styles.lastSyncLabel}>
                🔄 {lastSyncLabel}
              </span>
            )}
          </div>
          <div className={styles.timelineActions}>
            <ForecastDropdown forecastDays={forecastDays} setForecastDays={setForecastDays} t={t} />
            <MaterialFilter value={matFilter} onChange={setMatFilter} />
            <SyncButton onDone={() => load(true)} />
          </div>
        </div>

        <div className={styles.timelineWrapper}>
          <DeliveryTimeline
            silos={silos}
            planRows={planRows}
            materialFilter={matFilter}
            forecastDays={forecastDays}
            onEdit={setEditRow}
          />
        </div>
      </section>

      {/* ── Sección Delivery Planning Table ── */}
      <section className={styles.planningSection}>
        <div className={styles.planningHeader}>
          <h2 className={styles.planningTitle}>{t("planTitle")}</h2>
        </div>
        <DeliveryPlanningTable planRows={planRows} forecastDays={forecastDays} onEdit={setEditRow} />
      </section>

      {/* ── Edit date modal ── */}
      {editRow && (
        <EditDateModal
          editRow={editRow}
          onClose={() => setEditRow(null)}
          onSaved={() => { setEditRow(null); load(true); }}
        />
      )}

    </div>
  );
}
