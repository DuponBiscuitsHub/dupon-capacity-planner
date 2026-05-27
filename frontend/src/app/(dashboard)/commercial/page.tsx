"use client";

import { useState } from "react";
import styles from "./commercial.module.css";
import { useLanguage } from "../../i18n/context";
import { useCompany } from "../../context/CompanyContext";
import { formatNumber } from "@/app/utils/format";

interface SalesOrder {
  id: string;
  client: string;
  product: string;
  quantity: number;
  date: string;
  risk: "ok" | "warn" | "crit";
  detailEs: string;
  detailEn: string;
}

export default function CommercialPage() {
  const { t, language } = useLanguage();
  const { selectedCompany } = useCompany();

  // Consultation form local states
  const [product, setProduct] = useState("A17-A");
  const [quantity, setQuantity] = useState<number>(30000);
  const [deliveryDate, setDeliveryDate] = useState("2026-06-02");

  // Capable-To-Promise (CTP) capacity diagnosis state
  const [isCalculated, setIsCalculated] = useState(true);
  const [ctpStatus, setCtpStatus] = useState<"feasible" | "risk" | "unfeasible">("feasible");
  const [rawMaterialsLevel, setRawMaterialsLevel] = useState<"success" | "warning" | "danger">("success");
  const [aluminumLevel, setAluminumLevel] = useState<"success" | "warning" | "danger">("success");
  const [lineLevel, setLineLevel] = useState<"success" | "warning" | "danger">("success");

  // Simulated active Sales Orders fetched from Odoo
  const [salesOrders, setSalesOrders] = useState<SalesOrder[]>([
    {
      id: "SO-2026-041",
      client: "Supermarchés Match 🇫🇷",
      product: "A17-B",
      quantity: 65000,
      date: "2026-05-30",
      risk: "warn",
      detailEs: "Saturación del formato F3 de aluminio en taller Iberica.",
      detailEn: "Saturation of aluminum format F3 in Iberica workshop.",
    },
    {
      id: "SO-2026-042",
      client: "Mercadona S.A. 🇪🇸",
      product: "A17-A",
      quantity: 120000,
      date: "2026-06-01",
      risk: "crit",
      detailEs: "Riesgo crítico: Rotura de Silo de Harina #1 proyectada para esa fecha.",
      detailEn: "Critical risk: Projected outage of Flour Silo #1 for that date.",
    },
    {
      id: "SO-2026-043",
      client: "Colruyt Group 🇧🇪",
      product: "A17-C",
      quantity: 25000,
      date: "2026-06-04",
      risk: "ok",
      detailEs: "Capacidad y materias primas aseguradas para producción.",
      detailEn: "Capacity and raw materials secured for production.",
    },
    {
      id: "SO-2026-044",
      client: "Aldi Nord GmbH 🇩🇪",
      product: "A17-A",
      quantity: 38000,
      date: "2026-06-05",
      risk: "ok",
      detailEs: "Capacidad disponible en Línea de Ensamble A17-1.",
      detailEn: "Capacity available in Assembly Line A17-1.",
    },
    {
      id: "SO-2026-045",
      client: "Consum S. Coop. 🇪🇸",
      product: "A17-B",
      quantity: 55000,
      date: "2026-06-06",
      risk: "warn",
      detailEs: "Saturación de formato F3 en enrolladora #12.",
      detailEn: "Format F3 saturation in winding machine #12.",
    },
  ]);

  // Execute CTP simulation engine based on operational business rules
  const handleCheckCapacity = (e: React.FormEvent) => {
    e.preventDefault();
    setIsCalculated(true);

    if (quantity > 80000) {
      // Simulate flour silo outage for large volume requests
      setCtpStatus("unfeasible");
      setRawMaterialsLevel("danger");
      setAluminumLevel(product === "A17-C" ? "danger" : "warning");
      setLineLevel("warning");
    } else if (quantity > 40000) {
      // Simulate high F3/F5 aluminum saturation
      setCtpStatus("risk");
      setRawMaterialsLevel("success");
      setAluminumLevel("danger");
      setLineLevel("warning");
    } else {
      // Standard quantity is feasible immediately
      setCtpStatus("feasible");
      setRawMaterialsLevel("success");
      setAluminumLevel("success");
      setLineLevel("success");
    }
  };

  // Get CSS class based on restriction status level
  const getBarClass = (level: "success" | "warning" | "danger") => {
    if (level === "success") return styles.barSuccess;
    if (level === "warning") return styles.barWarning;
    return styles.barDanger;
  };

  // Get bar fill percentage based on simulated capacity remaining
  const getBarWidth = (level: "success" | "warning" | "danger") => {
    if (level === "success") return "85%";
    if (level === "warning") return "45%";
    return "12%";
  };

  // Get translated detail for risk analysis log
  const getOrderDetail = (order: SalesOrder) => {
    return language === "en" ? order.detailEn : order.detailEs;
  };

  return (
    <div className={styles.container}>
      {/* Top Panel: Form Consultation and CTP Diagnosis */}
      <div className={styles.mainGrid}>
        
        {/* CTP Query Form */}
        <section className={`${styles.formCard} glass-panel`}>
          <h3 className={styles.cardTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            {t("commFormHeader")}
          </h3>

          <form onSubmit={handleCheckCapacity} style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            <div className={styles.formGroup}>
              <label className={styles.label}>{t("commSelectProduct")}</label>
              <select 
                value={product} 
                onChange={(e) => setProduct(e.target.value)} 
                className={styles.select}
              >
                <option value="A17-A">A17-A - Galleta Turno Mañana (F1 - Harina/Azúcar estándar)</option>
                <option value="A17-B">A17-B - Galleta Turno Tarde (F3 - Harina media)</option>
                <option value="A17-C">A17-C - Galleta Chocolate Premium (F5 - Harina/Azúcar alta)</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>{t("commQuantity")}</label>
              <input 
                type="number" 
                value={quantity} 
                onChange={(e) => setQuantity(Number(e.target.value))} 
                min={1000} 
                max={500000}
                className={styles.input} 
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>{t("commDeliveryDate")}</label>
              <input 
                type="date" 
                value={deliveryDate} 
                onChange={(e) => setDeliveryDate(e.target.value)} 
                className={styles.input} 
                required
              />
            </div>

            <button type="submit" className={styles.btnSubmit}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              {t("commBtnCheck")}
            </button>
          </form>
        </section>

        {/* CTP Interactive Diagnosis Card */}
        <section className={`${styles.diagnosticCard} glass-panel`}>
          <h3 className={styles.cardTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            {t("commResultTitle")}
          </h3>

          {isCalculated ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", height: "100%", justifyContent: "space-between" }}>
              {/* CTP Status badge */}
              <div className={`${styles.stateDisplay} ${
                ctpStatus === "feasible" ? styles.stateDisplaySuccess : 
                ctpStatus === "risk" ? styles.stateDisplayWarning : 
                styles.stateDisplayDanger
              }`}>
                <span className={styles.stateLabel}>Resultado Predictivo CTP:</span>
                <span className={`badge ${
                  ctpStatus === "feasible" ? "badge-success" : 
                  ctpStatus === "risk" ? "badge-warning" : 
                  "badge-danger"
                } ${styles.stateBadge}`}>
                  {ctpStatus === "feasible" ? t("commStatusFeasible") : 
                   ctpStatus === "risk" ? t("commStatusRisk") : 
                   t("commStatusUnfeasible")}
                </span>
              </div>

              {/* Technical description */}
              <p className={styles.diagnosticDesc}>
                {ctpStatus === "feasible" ? t("commDiagnosticOk") : 
                 ctpStatus === "risk" ? t("commDiagnosticRisk") : 
                 t("commDiagnosticFail")}
              </p>

              {/* Operational constraints progress bars */}
              <div className={styles.checksContainer}>
                
                {/* 1. Raw Materials */}
                <div className={styles.checkRow}>
                  <div className={styles.checkHeader}>
                    <span className={styles.checkName}>{t("commCheckRaw")}</span>
                    <span className={`${styles.checkStatusText} ${
                      rawMaterialsLevel === "success" ? "text-success" : 
                      rawMaterialsLevel === "warning" ? "text-warning" : 
                      "text-danger"
                    }`} style={{ color: `var(--color-${rawMaterialsLevel})` }}>
                      {rawMaterialsLevel === "success" ? "Disponible" : 
                       rawMaterialsLevel === "warning" ? "Bajo en Silo #2" : 
                       "Ruptura Proyectada"}
                    </span>
                  </div>
                  <div className={styles.progressBarOuter}>
                    <div 
                      className={`${styles.progressBarInner} ${getBarClass(rawMaterialsLevel)}`}
                      style={{ width: getBarWidth(rawMaterialsLevel) }}
                    ></div>
                  </div>
                </div>

                {/* 2. Aluminum Processing Capacity */}
                <div className={styles.checkRow}>
                  <div className={styles.checkHeader}>
                    <span className={styles.checkName}>
                      {t("commCheckAlu")} 
                      {selectedCompany !== "iberica" && " (Grupo Iberica)"}
                    </span>
                    <span className={styles.checkStatusText} style={{ color: `var(--color-${aluminumLevel})` }}>
                      {aluminumLevel === "success" ? "Capacidad OK" : 
                       aluminumLevel === "warning" ? "Saturación Media" : 
                       "Formatos Colisionados"}
                    </span>
                  </div>
                  <div className={styles.progressBarOuter}>
                    <div 
                      className={`${styles.progressBarInner} ${getBarClass(aluminumLevel)}`}
                      style={{ width: getBarWidth(aluminumLevel) }}
                    ></div>
                  </div>
                </div>

                {/* 3. Assembly Slots */}
                <div className={styles.checkRow}>
                  <div className={styles.checkHeader}>
                    <span className={styles.checkName}>{t("commCheckLine")}</span>
                    <span className={styles.checkStatusText} style={{ color: `var(--color-${lineLevel})` }}>
                      {lineLevel === "success" ? "Slot Libre" : 
                       lineLevel === "warning" ? "Turno Ajustado" : 
                       "Saturación Máxima"}
                    </span>
                  </div>
                  <div className={styles.progressBarOuter}>
                    <div 
                      className={`${styles.progressBarInner} ${getBarClass(lineLevel)}`}
                      style={{ width: getBarWidth(lineLevel) }}
                    ></div>
                  </div>
                </div>

              </div>
            </div>
          ) : (
            <div style={{ display: "flex", flex: 1, alignItems: "center", justifyContent: "center", color: "var(--text-secondary)" }}>
              <span>Completa la consulta de la izquierda para evaluar la capacidad</span>
            </div>
          )}
        </section>

      </div>

      {/* Bottom Panel: Confirmed sales orders list and Odoo sync engine log */}
      <section className={`${styles.tableCard} glass-panel`}>
        <h3 className={styles.cardTitle}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
          {t("commRiskListTitle")}
        </h3>

        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("commColOrder")}</th>
                <th>{t("commColClient")}</th>
                <th>Producto</th>
                <th>{t("commColQty")}</th>
                <th>Fecha Límite</th>
                <th>{t("commColRisk")}</th>
                <th>Diagnóstico Odoo APS</th>
              </tr>
            </thead>
            <tbody>
              {salesOrders.map((order) => (
                <tr key={order.id}>
                  <td style={{ fontWeight: 600, color: "var(--color-primary)" }}>{order.id}</td>
                  <td>{order.client}</td>
                  <td>
                    <span className={styles.productBadge}>{order.product}</span>
                  </td>
                  <td style={{ fontFamily: "monospace", fontSize: "0.95rem" }}>
                    {formatNumber(order.quantity)} packs
                  </td>
                  <td>{order.date}</td>
                  <td>
                    <div className={styles.statusIndicator}>
                      <span className={`${styles.pulseDot} ${
                        order.risk === "ok" ? styles.pulseDotSuccess : 
                        order.risk === "warn" ? styles.pulseDotWarning : 
                        styles.pulseDotDanger
                      }`}></span>
                      <span style={{ 
                        color: order.risk === "ok" ? "var(--color-success)" : 
                                order.risk === "warn" ? "var(--color-warning)" : 
                                "var(--color-danger)"
                      }}>
                        {order.risk === "ok" ? t("commStatusOk") : 
                         order.risk === "warn" ? t("commStatusWarn") : 
                         t("commStatusCrit")}
                      </span>
                    </div>
                  </td>
                  <td style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                    {getOrderDetail(order)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
