import styles from "./page.module.css";

export default function DashboardPage() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      
      {/* 1. Tarjetas de KPIs Generales (Grid de Alta Densidad) */}
      <section className={styles.metricsGrid}>
        
        {/* KPI: OEE Global */}
        <div className={`${styles.kpiCard} glass-panel glass-panel-hover`}>
          <div className={styles.kpiHeader}>
            <span>OEE Global Planta</span>
            <span className="badge badge-success">Óptimo</span>
          </div>
          <div className={styles.kpiValue}>84.5%</div>
          <div className={styles.kpiSubtext}>Eficiencia agregada de las 3 líneas</div>
        </div>

        {/* KPI: Autonomía de Harina */}
        <div className={`${styles.kpiCard} glass-panel glass-panel-hover`}>
          <div className={styles.kpiHeader}>
            <span>Silo Crítico (Harina)</span>
            <span className="badge badge-warning" style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
              <span className="pulse-warning" style={{ width: "6px", height: "6px", borderRadius: "50%" }}></span>
              18 horas
            </span>
          </div>
          <div className={styles.kpiValue}>14,200 kg</div>
          <div className={styles.kpiSubtext}>Silo #1 cruza línea roja mañana 04:32h</div>
        </div>

        {/* KPI: Carga de Troqueles */}
        <div className={`${styles.kpiCard} glass-panel glass-panel-hover`}>
          <div className={styles.kpiHeader}>
            <span>Carga Aluminio</span>
            <span className="badge badge-primary">Estable</span>
          </div>
          <div className={styles.kpiValue}>72.0%</div>
          <div className={styles.kpiSubtext}>Troqueles y enrolladoras ocupados</div>
        </div>

        {/* KPI: Riesgo de Pedidos */}
        <div className={`${styles.kpiCard} glass-panel glass-panel-hover`}>
          <div className={styles.kpiHeader}>
            <span>Pedidos en Riesgo</span>
            <span className="badge badge-danger" style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
              <span className="pulse-danger" style={{ width: "6px", height: "6px", borderRadius: "50%" }}></span>
              3 Pedidos
            </span>
          </div>
          <div className={styles.kpiValue}>4.2%</div>
          <div className={styles.kpiSubtext}>Exceden capacidad de entrega comprometida</div>
        </div>

      </section>

      {/* 2. Sección Inferior (Líneas Activas + Alertas de Fábrica) */}
      <div className={styles.bottomSection}>
        
        {/* Panel Izquierdo: Estado de Líneas de Producción */}
        <section className={`${styles.linesCard} glass-panel`}>
          <h3 className={styles.sectionTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--color-primary)" }}>
              <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
              <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
              <line x1="6" y1="6" x2="6.01" y2="6" />
              <line x1="6" y1="18" x2="6.01" y2="18" />
            </svg>
            Monitoreo en Tiempo Real - Líneas de Ensamble A17
          </h3>
          
          <div className={styles.linesList}>
            
            {/* Línea 1 */}
            <div className={styles.lineRow}>
              <div className={styles.lineInfo}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "var(--color-success)" }}></span>
                  <span className={styles.lineName}>Línea 1 (Galleta Ensamblada A17)</span>
                </div>
                <div className={styles.lineDetails}>
                  Orden Activa: <strong>#MO98242</strong> | Formato: F3 (Familiar) | Receta: Galleta Tradicional
                </div>
              </div>
              <div className={styles.lineSpeedSection}>
                <span className={styles.lineSpeed}>420 u/m</span>
                <span className={styles.lineSpeedUnit}>Velocidad de Empaque</span>
              </div>
            </div>

            {/* Línea 2 */}
            <div className={styles.lineRow}>
              <div className={styles.lineInfo}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "var(--color-success)" }}></span>
                  <span className={styles.lineName}>Línea 2 (Galleta Ensamblada A17)</span>
                </div>
                <div className={styles.lineDetails}>
                  Orden Activa: <strong>#MO98245</strong> | Formato: F1 (Individual) | Receta: Galleta Rellena Coco
                </div>
              </div>
              <div className={styles.lineSpeedSection}>
                <span className={styles.lineSpeed}>380 u/m</span>
                <span className={styles.lineSpeedUnit}>Velocidad de Empaque</span>
              </div>
            </div>

            {/* Línea 3 */}
            <div className={styles.lineRow} style={{ opacity: 0.65 }}>
              <div className={styles.lineInfo}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "var(--text-muted)" }}></span>
                  <span className={styles.lineName}>Línea 3 (Galleta Ensamblada A17)</span>
                </div>
                <div className={styles.lineDetails}>
                  Estado: <strong>Inactiva (Parada de Mantenimiento)</strong> | Reinicio estimado: 16:00h
                </div>
              </div>
              <div className={styles.lineSpeedSection}>
                <span className={styles.lineSpeed} style={{ color: "var(--text-muted)" }}>0 u/m</span>
                <span className={styles.lineSpeedUnit}>Velocidad de Empaque</span>
              </div>
            </div>

          </div>
        </section>

        {/* Panel Derecho: Alertas del Planificador (Silos & Aluminio) */}
        <section className={`${styles.alertsCard} glass-panel`}>
          <h3 className={styles.sectionTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--color-danger)" }}>
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
            Alertas Predictivas del APS
          </h3>
          
          <div className={styles.alertsList}>
            
            {/* Alerta de Harina (Fase 1) */}
            <div className={styles.alertItem}>
              <span className={styles.alertIcon} style={{ color: "var(--color-warning)" }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              </span>
              <div className={styles.alertContent}>
                <span className={styles.alertTitle} style={{ color: "var(--color-warning)" }}>Silo de Harina #1 en Decaimiento</span>
                <span className={styles.alertDescription}>
                  Consumo dinámico de Línea 1 proyecta vaciado en **18 horas**. Ventana óptima para recibir el camión cisterna: **Hoy a las 18:00h** (capacidad útil disponible para vaciar 25 t).
                </span>
                <span className={styles.alertMeta}>Modulo: RM & Silos Planner | Hace 5 min</span>
              </div>
            </div>

            {/* Alerta de Aluminio / CTP (Fase 2 & 3) */}
            <div className={`${styles.alertItem} styles.alertItemDanger`}>
              <span className={styles.alertIcon} style={{ color: "var(--color-danger)" }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </span>
              <div className={styles.alertContent}>
                <span className={styles.alertTitle} style={{ color: "var(--color-danger)" }}>Ruptura Proyectada de Sleeve F3</span>
                <span className={styles.alertDescription}>
                  El pedido de venta **#SO4322 (A17 Familiar)** excede el stock proyectado de envoltorios A16. El taller de aluminio reporta saturación en enrolladoras para el formato F3. Riesgo de demora de entrega: **+2 días**.
                </span>
                <span className={styles.alertMeta}>Modulo: Aluminum & CTP | Hace 12 min</span>
              </div>
            </div>

          </div>
        </section>

      </div>

    </div>
  );
}
