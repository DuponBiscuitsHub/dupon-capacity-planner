"use client";

import { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import styles from "./page.module.css";
import { useCompany } from "../context/CompanyContext";
import { useLanguage } from "../i18n/context";
import { apiFetch } from "@/lib/api";

// Lazy-load Chart.js component (solo client-side)
const StockProjectionChart = dynamic(
  () => import("./components/StockProjectionChart"),
  { ssr: false },
);

// ── Types ──────────────────────────────────────────────────────────────────────

interface SiloStatus {
  silo_code: string;
  name: string;
  material_type: string;
  capacity_kg: number;
  current_stock_kg: number | null;
  fill_pct: number | null;
  autonomy_hours: number | null;
  status: "ok" | "warning" | "critical" | "unknown";
}

interface Delivery {
  id: number;
  silo_code: string;
  material_type: string;
  suggested_date: string;
  qty_kg: number;
  status: string;
  po_name: string | null;
  po_state: string | null;
}

interface ProjectionPoint {
  date: string;
  stock_kg: number;
}

interface PoEvent {
  date: string;
  qty_kg: number;
  po_name: string;
}

interface SiloProjection {
  silo_code: string;
  material_type: string;
  capacity_kg: number;
  safety_stock_kg: number;
  consumption_kg_day: number;
  points: ProjectionPoint[];
  po_events: PoEvent[];
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function fmtKg(kg: number): string {
  return kg >= 1000 ? `${(kg / 1000).toFixed(1)} t` : `${Math.round(kg)} kg`;
}

function getMaterialLabel(material: string, t: (key: string) => string): string {
  const MAP: Record<string, string> = {
    harina: t("matHarina"),
    azucar: t("matAzucar"),
    aceite: t("matAceite"),
  };
  return MAP[material] ?? material.toUpperCase();
}

// ── Vertical Bar Gauge ─────────────────────────────────────────────────────────

function SiloBarGauge({
  silo,
  nextDelivery,
  tToday,
  tTomorrow,
  tNoDelivery,
  tSafety,
  t,
}: {
  silo: SiloStatus;
  nextDelivery?: Delivery;
  tToday: string;
  tTomorrow: string;
  tNoDelivery: string;
  tSafety: string;
  t: (key: string) => string;
}) {
  const pct = silo.fill_pct ?? 0;

  const fillColor =
    silo.status === "critical" ? "var(--color-danger)" :
    silo.status === "warning"  ? "var(--color-warning)" :
                                 "var(--color-success)";

  const labelColor =
    silo.status === "critical" ? styles.matLabelDanger :
    silo.status === "warning"  ? styles.matLabelWarning :
                                 styles.matLabelOk;

  const cardBorder =
    silo.status === "critical" ? styles.cardCritical :
    silo.status === "warning"  ? styles.cardWarning   :
    silo.status === "ok"       ? styles.cardOk        : "";

  const kg    = silo.current_stock_kg;
  const capKg = silo.capacity_kg;

  function fmtDeliveryDate(iso: string): string {
    const d = new Date(iso);
    const today = new Date();
    const diffDays = Math.round((d.getTime() - today.getTime()) / 86400000);
    const locale = t("_locale") || "es-ES";
    const time = d.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
    if (diffDays === 0) return `${tToday} ${time}`;
    if (diffDays === 1) return `${tTomorrow} ${time}`;
    return d.toLocaleDateString(locale, { day: "2-digit", month: "2-digit" }) + " " + time;
  }

  return (
    <div
      className={`${styles.siloCard} ${cardBorder}`}
      id={`silo-${silo.silo_code.toLowerCase()}`}
    >
      <div className={`${styles.matLabel} ${labelColor}`}>
        {getMaterialLabel(silo.material_type, t)}
      </div>
      <div className={styles.siloName}>{silo.name}</div>

      <div className={styles.barOuter}>
        <div
          className={styles.barFill}
          style={{ height: `${Math.min(pct, 100)}%`, background: fillColor }}
        />
        <div className={styles.safetyLine} title={tSafety} />
      </div>

      <div
        className={styles.pctValue}
        style={{ color: pct < 20 ? "var(--color-danger)" : pct < 40 ? "var(--color-warning)" : "var(--text-primary)" }}
      >
        {kg !== null ? `${Math.round(pct)}%` : "—"}
      </div>

      {kg !== null && (
        <div className={styles.kgValue}>
          {fmtKg(kg)} / {fmtKg(capKg)}
        </div>
      )}

      {nextDelivery ? (
        <div className={styles.nextDelivery}>
          <span className={styles.ndIcon}>📦</span>
          <span>{fmtDeliveryDate(nextDelivery.suggested_date)}</span>
        </div>
      ) : (
        <div className={styles.nextDeliveryEmpty}>{tNoDelivery}</div>
      )}
    </div>
  );
}

// ── Alert Bar ──────────────────────────────────────────────────────────────────

function AlertBar({
  silos,
  tCritical,
  tLow,
}: {
  silos: SiloStatus[];
  tCritical: string;
  tLow: string;
}) {
  const critical = silos.filter(s => s.status === "critical");
  const warning  = silos.filter(s => s.status === "warning");
  if (!critical.length && !warning.length) return null;

  return (
    <div className={critical.length ? styles.alertDanger : styles.alertWarning}>
      <span>{critical.length ? "🔴" : "⚠️"}</span>
      <span>
        {critical.length > 0 && (
          <strong>{critical.map(s => s.silo_code).join(", ")} — {tCritical}</strong>
        )}
        {critical.length > 0 && warning.length > 0 && "  ·  "}
        {warning.length > 0 && `${warning.map(s => s.silo_code).join(", ")} — ${tLow}`}
      </span>
    </div>
  );
}

// ── Dashboard Page ─────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { companyId } = useCompany();
  const { t } = useLanguage();
  const [silos, setSilos]             = useState<SiloStatus[]>([]);
  const [deliveries, setDeliveries]   = useState<Delivery[]>([]);
  const [projections, setProjections] = useState<SiloProjection[]>([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [s, d, p] = await Promise.all([
        apiFetch<SiloStatus[]>(`/api/v1/silos?company_id=${companyId}`),
        apiFetch<Delivery[]>(`/api/v1/deliveries?company_id=${companyId}`),
        apiFetch<SiloProjection[]>(`/api/v1/silos/projection?company_id=${companyId}`),
      ]);
      setSilos(s);
      setDeliveries(d);
      setProjections(p);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setLoading(false);
    }
  }, [companyId, t]);

  useEffect(() => { load(); }, [load]);

  const nextBySilo: Record<string, Delivery> = {};
  for (const d of deliveries) {
    if (!nextBySilo[d.silo_code]) nextBySilo[d.silo_code] = d;
  }

  if (loading) return <div className={styles.loading}>{t("loading")}</div>;
  if (error)   return <div className={styles.errorBox}>{error}</div>;

  return (
    <div className={styles.page}>
      <AlertBar
        silos={silos}
        tCritical={t("dashAlertCritical")}
        tLow={t("dashAlertLow")}
      />

      <section className={styles.gaugesSection}>
        {silos.map(silo => (
          <SiloBarGauge
            key={silo.silo_code}
            silo={silo}
            nextDelivery={nextBySilo[silo.silo_code]}
            tToday={t("dashToday")}
            tTomorrow={t("dashTomorrow")}
            tNoDelivery={t("dashNoDelivery")}
            tSafety={t("siloSafetyStock")}
            t={t}
          />
        ))}
      </section>

      <section className={styles.chartSection}>
        <h2 className={styles.chartTitle}>{t("chartTitle")}</h2>
        <StockProjectionChart projections={projections} t={t} />
      </section>

      <section className={styles.statsRow}>
        <div className={styles.statCard}>
          <span className={styles.statNum}>{silos.filter(s => s.status === "ok").length}</span>
          <span className={styles.statLabel}>{t("dashStatOk")}</span>
        </div>
        <div className={styles.statCard}>
          <span className={`${styles.statNum} ${styles.numWarning}`}>
            {silos.filter(s => s.status === "warning").length}
          </span>
          <span className={styles.statLabel}>{t("dashStatLow")}</span>
        </div>
        <div className={styles.statCard}>
          <span className={`${styles.statNum} ${styles.numDanger}`}>
            {silos.filter(s => s.status === "critical").length}
          </span>
          <span className={styles.statLabel}>{t("dashStatCritical")}</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statNum}>{deliveries.length}</span>
          <span className={styles.statLabel}>{t("dashStatDeliveries")}</span>
        </div>
      </section>
    </div>
  );
}
