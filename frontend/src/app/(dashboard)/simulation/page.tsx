"use client";

import { useState, useEffect } from "react";
import styles from "./simulation.module.css";
import { useLanguage } from "../../i18n/context";
import { formatNumber, formatEuro } from "@/app/utils/format";

interface SimulationAlert {
  type: "info" | "warning" | "danger";
  textEs: string;
  textEn: string;
  time: string;
}

export default function SimulationPage() {
  const { t } = useLanguage();

  // Local control slider states
  const [efficiencyLoss, setEfficiencyLoss] = useState<number>(0);
  const [supplierDelay, setSupplierDelay] = useState<number>(0);
  const [emergencyOrders, setEmergencyOrders] = useState<number>(0);

  // States for simulated metrics outputs
  const [simOtd, setSimOtd] = useState(96.4);
  const [simOee, setSimOee] = useState(84.5);
  const [simDowntime, setSimDowntime] = useState(4.2);
  const [simCost, setSimCost] = useState(0);

  // Dynamic simulation alert alerts list
  const [alerts, setAlerts] = useState<SimulationAlert[]>([]);

  // Recalculate simulation metrics reactively when slider parameters change
  useEffect(() => {
    // Mathematical models to simulate physical degradation of capacity
    const oeeLoss = (efficiencyLoss * 0.18) + (emergencyOrders * 0.4);
    const calculatedOee = Math.max(45, Math.min(95, 84.5 - oeeLoss));

    const otdLoss = (supplierDelay * 3.2) + (emergencyOrders * 3.8) + (efficiencyLoss * 0.08);
    const calculatedOtd = Math.max(30, Math.min(98, 96.4 - otdLoss));

    const extraDowntime = (supplierDelay * 5.5) + (efficiencyLoss * 0.25) + (emergencyOrders * 1.5);
    const calculatedDowntime = 4.2 + extraDowntime;

    const extraCost = (emergencyOrders * 3500) + (supplierDelay * 1800) + (efficiencyLoss * 180);

    setSimOee(Number(calculatedOee.toFixed(1)));
    setSimOtd(Number(calculatedOtd.toFixed(1)));
    setSimDowntime(Number(calculatedDowntime.toFixed(1)));
    setSimCost(extraCost);

    // Build specific simulation alerts based on thresholds
    const tempAlerts: SimulationAlert[] = [];

    if (efficiencyLoss === 0 && supplierDelay === 0 && emergencyOrders === 0) {
      tempAlerts.push({
        type: "info",
        textEs: "SISTEMA ESTABLE: Las condiciones simuladas coinciden con el plan activo de Odoo. No se reportan desvíos operativos.",
        textEn: "STABLE SYSTEM: Simulated conditions match the active plan in Odoo. No operational deviations reported.",
        time: "10:48:00",
      });
    } else {
      if (efficiencyLoss > 30) {
        tempAlerts.push({
          type: "danger",
          textEs: `ALERTA DE CAPACIDAD: La pérdida del ${efficiencyLoss}% en enrolladora #12 satura la cola de bobinado F3. Acumulación de bobinas A15 en zona de espera.`,
          textEn: `CAPACITY ALERT: The ${efficiencyLoss}% efficiency loss in winding machine #12 saturates the F3 coil queue. Accumulation of A15 coils in buffer.`,
          time: "10:48:15",
        });
      } else if (efficiencyLoss > 0) {
        tempAlerts.push({
          type: "warning",
          textEs: "ADVERTENCIA DE RENDIMIENTO: Pérdida moderada de eficiencia en taller de aluminio. Incremento en el consumo de setup times.",
          textEn: "PERFORMANCE WARNING: Moderate efficiency loss in aluminum workshop. Increased setup times consumption.",
          time: "10:48:12",
        });
      }

      if (supplierDelay > 3) {
        tempAlerts.push({
          type: "danger",
          textEs: `RUPTURA DE METAL: El retraso de ${supplierDelay} días en proveedor A13 detiene la carga en troqueladora #2. Parada inminente de Línea A17-2 por falta de sleeves.`,
          textEn: `METAL OUTAGE: The ${supplierDelay}-day delay in supplier A13 stops load on die #2. Imminent assembly Line A17-2 shutdown due to lack of sleeves.`,
          time: "10:48:22",
        });
      } else if (supplierDelay > 0) {
        tempAlerts.push({
          type: "warning",
          textEs: `LOGÍSTICA INBOUND: Demora en llegada de camiones con bobina primaria. Autonomía del stock A13 reducida a menos de 24h.`,
          textEn: `INBOUND LOGISTICS: Delay in primary coil truck arrival. A13 stock autonomy reduced to less than 24h.`,
          time: "10:48:18",
        });
      }

      if (emergencyOrders > 2) {
        tempAlerts.push({
          type: "danger",
          textEs: `COLISIÓN DE PEDIDOS: ${emergencyOrders} órdenes de emergencia fuerzan la reprogramación de turnos y colisionan con el OTD de Dupon France.`,
          textEn: `ORDER COLLISION: ${emergencyOrders} emergency orders force shift rescheduling and collide with Dupon France OTD.`,
          time: "10:48:30",
        });
      } else if (emergencyOrders > 0) {
        tempAlerts.push({
          type: "info",
          textEs: `PLANIFICACIÓN DE VENTAS: Se simula la inserción de ${emergencyOrders} pedidos adicionales en la línea. Consumo de capacidad libre al 85%.`,
          textEn: `SALES PLANNING: Simulating insertion of ${emergencyOrders} additional orders on line. Free capacity consumption at 85%.`,
          time: "10:48:25",
        });
      }
    }

    setAlerts(tempAlerts);
  }, [efficiencyLoss, supplierDelay, emergencyOrders]);

  // Format delta metrics comparison
  const renderDelta = (current: number, base: number, isLowerBetter = false) => {
    const diff = Number((current - base).toFixed(1));
    if (diff === 0) return <span className={`${styles.metricDiff} ${styles.diffNeutral}`}>0.0%</span>;

    const isWorse = isLowerBetter ? diff > 0 : diff < 0;
    const sign = diff > 0 ? "+" : "";

    return (
      <span className={`${styles.metricDiff} ${isWorse ? styles.diffWorse : styles.diffBetter}`}>
        {sign}{diff}%
      </span>
    );
  };

  // Format simulated financial cost differences
  const renderCostDelta = (current: number) => {
    if (current === 0) return <span className={`${styles.metricDiff} ${styles.diffNeutral}`}>0€</span>;
    return (
      <span className={`${styles.metricDiff} ${styles.diffWorse}`}>
        +{formatNumber(current)}€
      </span>
    );
  };

  return (
    <div className={styles.container}>
      <div className={styles.mainGrid}>
        
        {/* Left Panel: Simulation Slider Controls */}
        <section className={`${styles.controlsCard} glass-panel`}>
          <h3 className={styles.cardTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
            </svg>
            {t("simParamsTitle")}
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
            
            {/* 1. Winding Machine Efficiency */}
            <div className={styles.controlGroup}>
              <div className={styles.controlHeader}>
                <label className={styles.label}>{t("simSliderOee")}</label>
                <span className={styles.valueBadge}>{efficiencyLoss}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={efficiencyLoss}
                onChange={(e) => setEfficiencyLoss(Number(e.target.value))}
                className={styles.rangeInput}
              />
              <p className={styles.controlDesc}>{t("simDescOee")}</p>
            </div>

            {/* 2. Primary Coil Delay */}
            <div className={styles.controlGroup}>
              <div className={styles.controlHeader}>
                <label className={styles.label}>{t("simSliderDelay")}</label>
                <span className={styles.valueBadge}>{supplierDelay} d</span>
              </div>
              <input
                type="range"
                min="0"
                max="10"
                step="1"
                value={supplierDelay}
                onChange={(e) => setSupplierDelay(Number(e.target.value))}
                className={styles.rangeInput}
              />
              <p className={styles.controlDesc}>{t("simDescDelay")}</p>
            </div>

            {/* 3. Emergency Sales Orders */}
            <div className={styles.controlGroup}>
              <div className={styles.controlHeader}>
                <label className={styles.label}>{t("simSliderEmergency")}</label>
                <span className={styles.valueBadge}>+{emergencyOrders}</span>
              </div>
              <input
                type="range"
                min="0"
                max="5"
                step="1"
                value={emergencyOrders}
                onChange={(e) => setEmergencyOrders(Number(e.target.value))}
                className={styles.rangeInput}
              />
              <p className={styles.controlDesc}>{t("simDescEmergency")}</p>
            </div>

          </div>
        </section>

        {/* Right Panel: Side-by-Side Plan Comparison Workspace */}
        <section className={styles.workspace}>
          
          <h3 className={styles.comparisonTitle}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 3H1v18h22V7h-7V3z" />
              <path d="M9 12v5M13 10v7M17 14v3" />
            </svg>
            {t("simCompareTitle")}
          </h3>

          <div className={styles.sandboxCardsGrid}>
            
            {/* ACTIVE OFFICIAL PLAN (Odoo ERP SSoT) */}
            <div className={`${styles.planCard} ${styles.activePlanCard} glass-panel`}>
              <div className={styles.planHeader}>
                <span className={styles.planTypeBadge} style={{ color: "var(--color-success)" }}>
                  {t("simActivePlan")}
                </span>
                <span className="badge badge-success">OFICIAL</span>
              </div>

              <div className={styles.metricsGrid}>
                <div className={styles.metricBox}>
                  <span className={styles.metricName}>{t("simMetricOtd")}</span>
                  <span className={styles.metricValue} style={{ color: "var(--color-success)" }}>96.4%</span>
                  <span className={`${styles.metricDiff} ${styles.diffNeutral}`}>Base SSoT</span>
                </div>

                <div className={styles.metricBox}>
                  <span className={styles.metricName}>{t("simMetricOee")}</span>
                  <span className={styles.metricValue}>84.5%</span>
                  <span className={`${styles.metricDiff} ${styles.diffNeutral}`}>Estable</span>
                </div>

                <div className={styles.metricBox}>
                  <span className={styles.metricName}>{t("simMetricDowntime")}</span>
                  <span className={styles.metricValue}>4.2h</span>
                  <span className={`${styles.metricDiff} ${styles.diffNeutral}`}>Mantenimiento</span>
                </div>

                <div className={styles.metricBox}>
                  <span className={styles.metricName}>{t("simMetricCost")}</span>
                  <span className={styles.metricValue}>0 €</span>
                  <span className={`${styles.metricDiff} ${styles.diffNeutral}`}>Presupuestado</span>
                </div>
              </div>
            </div>

            {/* SIMULATED SANDBOX PLAN (Reactive updates) */}
            <div className={`${styles.planCard} ${styles.simPlanCard} glass-panel`}>
              <div className={styles.planHeader}>
                <span className={styles.planTypeBadge} style={{ color: "var(--color-primary)" }}>
                  {t("simSimPlan")}
                </span>
                <span className="badge badge-primary">SANDBOX ACTIVADO</span>
              </div>

              <div className={styles.metricsGrid}>
                <div className={styles.metricBox}>
                  <span className={styles.metricName}>{t("simMetricOtd")}</span>
                  <span className={styles.metricValue} style={{ 
                    color: simOtd > 85 ? "var(--color-success)" : 
                           simOtd > 70 ? "var(--color-warning)" : 
                           "var(--color-danger)"
                  }}>{simOtd}%</span>
                  {renderDelta(simOtd, 96.4)}
                </div>

                <div className={styles.metricBox}>
                  <span className={styles.metricName}>{t("simMetricOee")}</span>
                  <span className={styles.metricValue}>{simOee}%</span>
                  {renderDelta(simOee, 84.5)}
                </div>

                <div className={styles.metricBox}>
                  <span className={styles.metricName}>{t("simMetricDowntime")}</span>
                  <span className={styles.metricValue} style={{ 
                    color: simDowntime > 15 ? "var(--color-danger)" : 
                           simDowntime > 8 ? "var(--color-warning)" : 
                           "var(--text-primary)"
                  }}>{simDowntime}h</span>
                  {renderDelta(simDowntime, 4.2, true)}
                </div>

                <div className={styles.metricBox}>
                  <span className={styles.metricName}>{t("simMetricCost")}</span>
                  <span className={styles.metricValue} style={{ 
                    color: simCost > 10000 ? "var(--color-danger)" : 
                           simCost > 3000 ? "var(--color-warning)" : 
                           "var(--text-primary)"
                  }}>+{formatNumber(simCost)} €</span>
                  {renderCostDelta(simCost)}
                </div>
              </div>
            </div>

          </div>

          {/* Predictive Cascading Event Console */}
          <div className={`${styles.eventsCard} glass-panel`}>
            <h4 className={styles.cardTitle} style={{ fontSize: "1rem" }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" strokeWidth="2" />
                <line x1="12" y1="9" x2="12" y2="13" strokeWidth="2" />
                <line x1="12" y1="17" x2="12.01" y2="17" strokeWidth="2" />
              </svg>
              Impacto en la Cadena de Suministro Proyectado (APS Predictivo)
            </h4>

            <div className={styles.eventList}>
              {alerts.map((alert, index) => (
                <div key={index} className={`${styles.eventRow} ${
                  alert.type === "danger" ? styles.eventRowDanger : 
                  alert.type === "warning" ? styles.eventRowWarning : 
                  styles.eventRowInfo
                }`}>
                  <span className={styles.eventIcon}>
                    {alert.type === "danger" ? "🛑" : alert.type === "warning" ? "⚠️" : "ℹ️"}
                  </span>
                  <span className={styles.eventText}>
                    {t(alert.textEs) || alert.textEs}
                  </span>
                  <span className={styles.eventTime}>{alert.time}</span>
                </div>
              ))}
            </div>
          </div>

        </section>

      </div>
    </div>
  );
}
