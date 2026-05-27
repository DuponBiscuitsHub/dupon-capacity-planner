"use client";

import { useState } from "react";
import styles from "./silos.module.css";
import { Silo, TruckDelivery } from "@/types/silos";

export default function SilosPage() {
  // 1. Estado de Silos Inicial (Fiel al Contexto de la Fábrica)
  const [silos, setSilos] = useState<Silo[]>([
    {
      id: "silo-h1",
      name: "Silo Harina #1",
      material: "harina",
      capacityKg: 25000,
      currentLevelKg: 9200, // Silo crítico (autonomía ~18h)
      safetyLevelKg: 5000,
      hourlyConsumptionKg: 500,
    },
    {
      id: "silo-h2",
      name: "Silo Harina #2",
      material: "harina",
      capacityKg: 25000,
      currentLevelKg: 18500,
      safetyLevelKg: 5000,
      hourlyConsumptionKg: 400,
    },
    {
      id: "silo-h3",
      name: "Silo Harina #3",
      material: "harina",
      capacityKg: 25000,
      currentLevelKg: 7800,
      safetyLevelKg: 5000,
      hourlyConsumptionKg: 300,
    },
    {
      id: "silo-a1",
      name: "Silo Azúcar #1",
      material: "azucar",
      capacityKg: 30000,
      currentLevelKg: 22400,
      safetyLevelKg: 6000,
      hourlyConsumptionKg: 250,
    },
    {
      id: "silo-c1",
      name: "Silo Coco #1",
      material: "aceite_coco",
      capacityKg: 15000,
      currentLevelKg: 11200,
      safetyLevelKg: 3000,
      hourlyConsumptionKg: 120,
    },
  ]);

  // 2. Estado de Camiones Programados desde Odoo / Logística
  const [trucks, setTrucks] = useState<TruckDelivery[]>([
    {
      id: "tr-001",
      material: "harina",
      quantityKg: 15000,
      scheduledTime: "Hoy - 18:00h",
      recommendedTime: "Hoy - 18:00h",
      status: "scheduled",
    },
    {
      id: "tr-002",
      material: "azucar",
      quantityKg: 20000,
      scheduledTime: "Mañana - 09:30h",
      recommendedTime: "Mañana - 11:00h",
      status: "scheduled",
    },
    {
      id: "tr-003",
      material: "harina",
      quantityKg: 15000,
      scheduledTime: "Viernes - 14:00h",
      recommendedTime: "Viernes - 12:30h",
      status: "scheduled",
    },
  ]);

  // 3. Simulación Interactiva de Descarga de Camión
  const handleSimulateUnload = (truckId: string, material: string, quantityKg: number) => {
    // Buscar silos compatibles con el material
    const compatibleSilos = silos.filter((s) => s.material === material);
    
    if (compatibleSilos.length === 0) return;

    // Algoritmo logístico básico: Encontrar el silo compatible con mayor espacio disponible (Headspace)
    let selectedSilo = compatibleSilos[0];
    let maxHeadspace = selectedSilo.capacityKg - selectedSilo.currentLevelKg;

    for (let i = 1; i < compatibleSilos.length; i++) {
      const headspace = compatibleSilos[i].capacityKg - compatibleSilos[i].currentLevelKg;
      if (headspace > maxHeadspace) {
        selectedSilo = compatibleSilos[i];
        maxHeadspace = headspace;
      }
    }

    // Actualizar el volumen del silo seleccionado (sin desbordar la capacidad física)
    setSilos((prevSilos) =>
      prevSilos.map((s) => {
        if (s.id === selectedSilo.id) {
          const newLevel = Math.min(s.capacityKg, s.currentLevelKg + quantityKg);
          return { ...s, currentLevelKg: newLevel };
        }
        return s;
      })
    );

    // Marcar el camión como completado
    setTrucks((prevTrucks) =>
      prevTrucks.map((t) => {
        if (t.id === truckId) {
          return { ...t, status: "completed" };
        }
        return t;
      })
    );
  };

  // Helper: Obtener clase CSS de color según autonomía del silo
  const getSiloStatusClasses = (currentLevel: number, capacity: number, autonomyHours: number) => {
    const percentage = (currentLevel / capacity) * 100;
    
    if (autonomyHours < 12 || percentage < 25) {
      return {
        fluidClass: styles.tankFluidDanger,
        badgeClass: "badge-danger",
        pulserClass: "pulse-danger",
        textStyle: { color: "var(--color-danger)" }
      };
    } else if (autonomyHours <= 24 || percentage < 45) {
      return {
        fluidClass: styles.tankFluidWarning,
        badgeClass: "badge-warning",
        pulserClass: "pulse-warning",
        textStyle: { color: "var(--color-warning)" }
      };
    } else {
      return {
        fluidClass: styles.tankFluidGreen,
        badgeClass: "badge-success",
        pulserClass: "",
        textStyle: { color: "var(--color-success)" }
      };
    }
  };

  return (
    <div className={styles.container}>
      
      {/* 📊 SECCIÓN 1: Cuadro SCADA - Estado de Silos en Vivo */}
      <section className={styles.silosGrid}>
        {silos.map((silo) => {
          const percentage = (silo.currentLevelKg / silo.capacityKg) * 100;
          const autonomyHours = Math.max(0, silo.currentLevelKg / silo.hourlyConsumptionKg);
          const status = getSiloStatusClasses(silo.currentLevelKg, silo.capacityKg, autonomyHours);

          return (
            <div key={silo.id} className={`${styles.siloCard} glass-panel`}>
              <span className={styles.siloMaterialLabel}>{silo.material.replace("_", " ")}</span>
              <h3 className={styles.siloTitle}>{silo.name}</h3>
              
              {/* Tanque Animado */}
              <div className={styles.tankOuter}>
                <div 
                  className={`${styles.tankFluid} ${status.fluidClass}`} 
                  style={{ height: `${percentage}%` }}
                ></div>
              </div>

              {/* Métricas Numéricas */}
              <div className={styles.siloInfo}>
                <span className={styles.siloPercentage}>{percentage.toFixed(0)}%</span>
                <span className={styles.siloVolume}>
                  {silo.currentLevelKg.toLocaleString()} / {silo.capacityKg.toLocaleString()} kg
                </span>
                <div style={{ marginTop: "0.25rem" }}>
                  <span className={`badge ${status.badgeClass}`} style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
                    {status.pulserClass && <span className={status.pulserClass} style={{ width: "6px", height: "6px", borderRadius: "50%" }}></span>}
                    {autonomyHours.toFixed(1)} hrs left
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </section>

      {/* 🔌 SECCIÓN 2: Split Layout (Curva de Decaimiento + Planificador Cisternas) */}
      <div className={styles.splitLayout}>
        
        {/* Panel Izquierdo: Curva de Decaimiento Predictiva (Gráfica SVG) */}
        <section className={`${styles.chartCard} glass-panel`}>
          <h3 className={styles.sectionTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--color-primary)" }}>
              <path d="M3 3v18h18" />
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" />
            </svg>
            Curva de Decaimiento Proyectada a 72h - Silo Harina #1
          </h3>
          
          <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "-0.5rem" }}>
            Muestra el vaciado predictivo del Silo #1 en función de la velocidad y merma teórica de las líneas de galletas.
          </p>

          {/* Gráfica SVG Nativa Premium */}
          <div className={styles.svgContainer}>
            <svg viewBox="0 0 500 180" width="100%" height="100%">
              {/* Ejes y Cuadrícula */}
              <line x1="40" y1="20" x2="40" y2="150" stroke="var(--border-light)" strokeWidth="1" />
              <line x1="40" y1="150" x2="480" y2="150" stroke="var(--border-light)" strokeWidth="1" />
              
              <line x1="40" y1="60" x2="480" y2="60" stroke="var(--border-light)" strokeWidth="1" strokeDasharray="3 3" />
              <line x1="40" y1="110" x2="480" y2="110" stroke="var(--border-light)" strokeWidth="1" strokeDasharray="3 3" />

              {/* Leyenda y Marcadores de Eje Y (Volumen) */}
              <text x="10" y="25" fill="var(--text-muted)" fontSize="9">100%</text>
              <text x="15" y="85" fill="var(--text-muted)" fontSize="9">50%</text>
              <text x="15" y="145" fill="var(--text-muted)" fontSize="9">0%</text>

              {/* Marcadores de Eje X (Tiempo) */}
              <text x="35" y="165" fill="var(--text-muted)" fontSize="9">Ahora</text>
              <text x="140" y="165" fill="var(--text-muted)" fontSize="9">+12h</text>
              <text x="250" y="165" fill="var(--text-muted)" fontSize="9">+24h (Mañana)</text>
              <text x="360" y="165" fill="var(--text-muted)" fontSize="9">+48h</text>
              <text x="450" y="165" fill="var(--text-muted)" fontSize="9">+72h</text>

              {/* Línea Roja de Stock Mínimo de Seguridad (20% del Silo) */}
              <line x1="40" y1="124" x2="480" y2="124" stroke="var(--color-danger)" strokeWidth="1.5" strokeDasharray="4 2" />
              <text x="400" y="120" fill="var(--color-danger)" fontSize="8" fontWeight="600">Límite de Seguridad (5,000 kg)</text>

              {/* Curva de Decaimiento Proyectada (Con desfase dinámico) */}
              {/* Harina #1: 9,200kg (37% en t=0) -> Vaciado estimado en 18h (cruza límite de seguridad) */}
              <path 
                d="M 40 102 L 150 124 L 200 150 L 480 150" 
                fill="none" 
                stroke="var(--color-warning)" 
                strokeWidth="3" 
                strokeLinecap="round" 
              />
              
              {/* Punto de Ruptura (Cruce de la curva) */}
              <circle cx="150" cy="124" r="5" fill="var(--color-danger)" />
              <text x="160" y="120" fill="var(--color-danger)" fontSize="9" fontWeight="700">Ruptura: +18.4h</text>
            </svg>
          </div>

          <div className={styles.legend}>
            <div className={styles.legendItem}>
              <span style={{ width: "12px", height: "4px", backgroundColor: "var(--color-warning)", borderRadius: "2px" }}></span>
              <span>Nivel Proyectado</span>
            </div>
            <div className={styles.legendItem}>
              <span style={{ width: "12px", height: "0px", borderTop: "2px dashed var(--color-danger)", display: "inline-block" }}></span>
              <span>Límite de Rotura</span>
            </div>
          </div>
        </section>

        {/* Panel Derecho: Logística de Entrada - Camiones Cisterna (Odoo) */}
        <section className={`${styles.trucksCard} glass-panel`}>
          <h3 className={styles.sectionTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--color-success)" }}>
              <rect x="1" y="3" width="15" height="13" />
              <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
              <circle cx="5.5" cy="18.5" r="2.5" />
              <circle cx="18.5" cy="18.5" r="2.5" />
            </svg>
            Planificador de Cisternas Inbound - Odoo Purchase Orders
          </h3>
          
          <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "-0.5rem" }}>
            Recepción dinámica de compras. Al simular la descarga, el camión inyecta el material al silo con mayor espacio libre.
          </p>

          <div className={styles.tableWrapper}>
            <table className={styles.truckTable}>
              <thead>
                <tr>
                  <th className={styles.th}>Materia Prima</th>
                  <th className={styles.th}>Volumen</th>
                  <th className={styles.th}>Odoo Est.</th>
                  <th className={styles.th}>Recom. APS</th>
                  <th className={styles.th}>Acción</th>
                </tr>
              </thead>
              <tbody>
                {trucks.map((truck) => (
                  <tr key={truck.id} style={{ opacity: truck.status === "completed" ? 0.5 : 1 }}>
                    <td className={styles.td}>
                      <span className={truck.material === "harina" ? "badge badge-primary" : "badge badge-warning"}>
                        {truck.material.replace("_", " ")}
                      </span>
                    </td>
                    <td className={styles.td}><strong>{truck.quantityKg.toLocaleString()} kg</strong></td>
                    <td className={styles.td} style={{ color: "var(--text-secondary)" }}>{truck.scheduledTime}</td>
                    <td className={styles.td} style={{ color: "var(--color-success)", fontWeight: 600 }}>{truck.recommendedTime}</td>
                    <td className={styles.td}>
                      {truck.status === "completed" ? (
                        <span className="badge badge-success" style={{ fontSize: "0.7rem", padding: "0.2rem 0.5rem" }}>Completado</span>
                      ) : (
                        <button
                          className={styles.simulateBtn}
                          onClick={() => handleSimulateUnload(truck.id, truck.material, truck.quantityKg)}
                        >
                          Simular Descarga
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

      </div>

    </div>
  );
}
