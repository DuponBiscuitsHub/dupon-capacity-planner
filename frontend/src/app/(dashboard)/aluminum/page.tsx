"use client";

import { useState } from "react";
import styles from "./aluminum.module.css";
import { Machine, FormatSaturation, PlantAllocation } from "@/types/aluminum";
import { useCompany } from "../../context/CompanyContext";
import { useLanguage } from "../../i18n/context";

export default function AluminumPage() {
  const { selectedCompany } = useCompany();
  const { t } = useLanguage();

  // 1. Estado para el simulador de pico de demanda externa
  const [isSimulatorActive, setIsSimulatorActive] = useState(false);

  // 2. Datos de los 5 Troqueles Físicos de Planta
  const [machines] = useState<Machine[]>([
    { id: "tr-01", name: "Troquel #01", type: "troquel", status: "running", activeFormat: "F3", weeklyCapacityPacks: 120000, weeklyLoadPacks: 98000 },
    { id: "tr-02", name: "Troquel #02", type: "troquel", status: "running", activeFormat: "F1", weeklyCapacityPacks: 100000, weeklyLoadPacks: 65000 },
    { id: "tr-03", name: "Troquel #03", type: "troquel", status: "idle", activeFormat: "-", weeklyCapacityPacks: 100000, weeklyLoadPacks: 0 },
    { id: "tr-04", name: "Troquel #04", type: "troquel", status: "running", activeFormat: "F5", weeklyCapacityPacks: 120000, weeklyLoadPacks: 88000 },
    { id: "tr-05", name: "Troquel #05", type: "troquel", status: "maintenance", activeFormat: "-", weeklyCapacityPacks: 100000, weeklyLoadPacks: 0 },
  ]);

  // RESTRICTION CHECK: Aluminios es exclusivo de Dupon Ibèrica
  // Si la compañía activa no es 'iberica', bloqueamos la interfaz con un candado elegante
  if (selectedCompany !== "iberica") {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "70vh" }}>
        <div className="glass-panel" style={{ maxWidth: "500px", padding: "3rem 2.5rem", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: "1.5rem", boxShadow: "var(--shadow-premium)" }}>
          <div className="pulse-danger" style={{ width: "64px", height: "64px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-primary)" }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>
          <h2 style={{ fontSize: "1.35rem", fontWeight: "700", letterSpacing: "-0.02em" }}>
            {t("aluminumRestrictedTitle")}
          </h2>
          <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
            {t("aluminumRestrictedDesc")}
          </p>
        </div>
      </div>
    );
  }

  // 3. Cargas y Mapa de Calor Dinámicos según el estado del simulador
  const formatSaturations: FormatSaturation[] = isSimulatorActive
    ? [
        { format: "F1", name: "F1 (Individual)", troquelLoadPercent: 62, enrolladoraLoadPercent: 68 },
        { format: "F2", name: "F2 (Minipack)", troquelLoadPercent: 78, enrolladoraLoadPercent: 72 },
        { format: "F3", name: "F3 (Familiar)", troquelLoadPercent: 96, enrolladoraLoadPercent: 98 },
        { format: "F4", name: "F4 (Tubular)", troquelLoadPercent: 45, enrolladoraLoadPercent: 48 },
        { format: "F5", name: "F5 (Tripack)", troquelLoadPercent: 92, enrolladoraLoadPercent: 86 },
        { format: "F6", name: "F6 (Especial)", troquelLoadPercent: 82, enrolladoraLoadPercent: 78 },
      ]
    : [
        { format: "F1", name: "F1 (Individual)", troquelLoadPercent: 45, enrolladoraLoadPercent: 52 },
        { format: "F2", name: "F2 (Minipack)", troquelLoadPercent: 58, enrolladoraLoadPercent: 60 },
        { format: "F3", name: "F3 (Familiar)", troquelLoadPercent: 80, enrolladoraLoadPercent: 82 },
        { format: "F4", name: "F4 (Tubular)", troquelLoadPercent: 30, enrolladoraLoadPercent: 35 },
        { format: "F5", name: "F5 (Tripack)", troquelLoadPercent: 68, enrolladoraLoadPercent: 58 },
        { format: "F6", name: "F6 (Especial)", troquelLoadPercent: 65, enrolladoraLoadPercent: 55 },
      ];

  // 4. Reparto de Capacidad de Producción (Iberica vs Otras Plantas)
  const allocations: PlantAllocation[] = isSimulatorActive
    ? [
        { plantName: "Planta Iberica (Local A17)", sharePercent: 45, volumePacks: 180000 },
        { plantName: "Planta Francia (Externo)", sharePercent: 35, volumePacks: 140000 },
        { plantName: "Planta Bélgica (Externo)", sharePercent: 20, volumePacks: 80000 },
      ]
    : [
        { plantName: "Planta Iberica (Local A17)", sharePercent: 65, volumePacks: 260000 },
        { plantName: "Planta Francia (Externo)", sharePercent: 25, volumePacks: 100000 },
        { plantName: "Planta Bélgica (Externo)", sharePercent: 10, volumePacks: 40000 },
      ];

  const getHeatmapClass = (percent: number) => {
    if (percent >= 90) return styles.heatmapCellDanger;
    if (percent >= 75) return styles.heatmapCellWarning;
    return styles.heatmapCellGreen;
  };

  const getMachineStatusBadge = (status: string) => {
    switch (status) {
      case "running":
        return <span className="badge badge-success">En Marcha</span>;
      case "idle":
        return <span className="badge badge-primary">Disponible</span>;
      case "maintenance":
        return <span className="badge badge-danger">Mantenimiento</span>;
      default:
        return <span className="badge">Desconectado</span>;
    }
  };

  const ibericaShare = allocations[0].sharePercent;
  const externalShare = allocations[1].sharePercent + allocations[2].sharePercent;

  return (
    <div className={styles.container}>
      
      {/* 🚀 1. Barra de Simulación Interactiva */}
      <section className={styles.topBar}>
        <div className={styles.topBarText}>
          <h3 className={styles.topBarTitle}>Panel de Control y Simulación del Taller</h3>
          <p className={styles.topBarDesc}>
            Conmuta la demanda agregada para simular el impacto de pedidos excepcionales de otras plantas del grupo en troqueladoras y enrolladoras.
          </p>
        </div>
        
        <button 
          className={`${styles.toggleBtn} ${isSimulatorActive ? styles.toggleBtnActive : ""}`}
          onClick={() => setIsSimulatorActive(!isSimulatorActive)}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          {isSimulatorActive ? "DESACTIVAR PICO DE DEMANDA" : "SIMULAR PICO DE DEMANDA (+35%)"}
        </button>
      </section>

      {/* Alerta de conflicto dinámica en cabecera */}
      {isSimulatorActive && (
        <div className="badge badge-danger pulse-danger" style={{ width: "100%", padding: "1rem", borderRadius: "10px", textTransform: "none", fontSize: "0.9rem", fontWeight: "600", justifyContent: "flex-start", gap: "0.75rem" }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <span>
            <strong>ALERTA DE CONFLICTO OPERATIVO:</strong> El incremento de demanda externa satura el taller de aluminio para los formatos **F3** y **F5**. La cuota asignada a la planta local Iberica cae del **65% al 45%**, retrasando la fabricación de envoltorios para la galleta ensamblada A17.
          </span>
        </div>
      )}

      {/* 🌀 2. Layout Principal de Dos Columnas */}
      <div className={styles.splitLayout}>
        
        {/* Columna Izquierda: Mapa de Calor de Saturación por Formato */}
        <section className={`${styles.heatMapCard} glass-panel`}>
          <h3 className={styles.sectionTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--color-warning)" }}>
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <line x1="9" y1="3" x2="9" y2="21" />
              <line x1="15" y1="3" x2="15" y2="21" />
              <line x1="3" y1="9" x2="21" y2="9" />
              <line x1="3" y1="15" x2="21" y2="15" />
            </svg>
            Mapa de Calor de Saturación Semanal por Formato (APS)
          </h3>
          
          <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "-0.5rem" }}>
            Visualiza la tasa de ocupación agregada proyectada para los 5 troqueles y las 34 enrolladoras en base a la planificación.
          </p>

          <div className={styles.tableWrapper}>
            <table className={styles.heatMapTable}>
              <thead>
                <tr>
                  <th className={`${styles.th} ${styles.thLeft}`}>Formato Físico</th>
                  <th className={styles.th}>Capacidad Troqueles</th>
                  <th className={styles.th}>Capacidad Enrolladoras</th>
                </tr>
              </thead>
              <tbody>
                {formatSaturations.map((item) => (
                  <tr key={item.format}>
                    <td className={`${styles.td} ${styles.tdLeft}`}>{item.name}</td>
                    <td className={styles.td}>
                      <span className={`${styles.heatmapCell} ${getHeatmapClass(item.troquelLoadPercent)}`}>
                        {item.troquelLoadPercent}%
                      </span>
                    </td>
                    <td className={styles.td}>
                      <span className={`${styles.heatmapCell} ${getHeatmapClass(item.enrolladoraLoadPercent)}`}>
                        {item.enrolladoraLoadPercent}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Columna Derecha: Estado de los Troqueles + Reparto de Cuota SVG */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          
          {/* Fichas de Troqueles Físicos */}
          <section className={`${styles.machinesCard} glass-panel`}>
            <h3 className={styles.sectionTitle}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--color-primary)" }}>
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
              Taller de Troqueles Físicos
            </h3>
            
            <div className={styles.machinesGrid}>
              {machines.map((m) => (
                <div key={m.id} className={styles.machineMiniCard}>
                  <span className={styles.machineTitle}>{m.name}</span>
                  {getMachineStatusBadge(m.status)}
                  <span className="badge badge-primary" style={{ fontSize: "0.7rem" }}>
                    Formato: {m.activeFormat}
                  </span>
                </div>
              ))}
            </div>

            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", textAlign: "center" }}>
              Enrolladoras (34 activas): Carga monitoreada y balanceada automáticamente por formato.
            </p>
          </section>

          {/* Gráfica Circular de Distribución de Capacidad del Grupo (SVG) */}
          <section className={`${styles.machinesCard} glass-panel`}>
            <h3 className={styles.sectionTitle}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--color-success)" }}>
                <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
                <path d="M22 12A10 10 0 0 0 12 2v10z" />
              </svg>
              Reparto de Capacidad de Producción Semanal
            </h3>

            <div className={styles.chartContainer}>
              {/* Gráfico circular SVG Reactivo */}
              <div className={styles.svgWrapper}>
                <svg viewBox="0 0 100 100" width="100%" height="100%">
                  <circle cx="50" cy="50" r="40" fill="none" stroke="var(--border-light)" strokeWidth="15" />
                  
                  <circle 
                    cx="50" 
                    cy="50" 
                    r="40" 
                    fill="none" 
                    stroke="var(--color-success)" 
                    strokeWidth="15" 
                    strokeDasharray={`${ibericaShare * 2.51} 251`} 
                    strokeDashoffset="0"
                    transform="rotate(-90 50 50)" 
                    style={{ transition: "stroke-dasharray 0.8s ease" }}
                  />

                  <circle 
                    cx="50" 
                    cy="50" 
                    r="40" 
                    fill="none" 
                    stroke="var(--color-primary)" 
                    strokeWidth="15" 
                    strokeDasharray={`${externalShare * 2.51} 251`} 
                    strokeDashoffset={`${-ibericaShare * 2.51}`}
                    transform="rotate(-90 50 50)" 
                    style={{ transition: "stroke-dasharray 0.8s ease, stroke-dashoffset 0.8s ease" }}
                  />
                  
                  <text x="50" y="47" textAnchor="middle" fill="var(--text-primary)" fontSize="10" fontWeight="700">IBERICA</text>
                  <text x="50" y="60" textAnchor="middle" fill="var(--color-success)" fontSize="11" fontWeight="800">
                    {ibericaShare}%
                  </text>
                </svg>
              </div>

              {/* Detalles de Distribución */}
              <div className={styles.allocationDetails}>
                {allocations.map((item, idx) => (
                  <div key={item.plantName} className={styles.allocationItem}>
                    <div style={{ display: "flex", alignItems: "center" }}>
                      <span className={styles.dot} style={{ backgroundColor: idx === 0 ? "var(--color-success)" : "var(--color-primary)" }}></span>
                      <span style={{ fontWeight: 600 }}>{item.plantName.split(" ")[1]}</span>
                    </div>
                    <div>
                      <strong>{item.sharePercent}%</strong> <span style={{ color: "var(--text-muted)", fontSize: "0.7rem" }}>({(item.volumePacks / 1000).toFixed(0)}k u)</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

        </div>

      </div>

    </div>
  );
}
