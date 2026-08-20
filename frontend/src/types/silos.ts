/* Definición de Interfaces para el Módulo de Silos */

export type MaterialType = 'harina' | 'azucar' | 'aceite_coco';

export interface Silo {
  id: string;
  name: string;
  material: MaterialType;
  capacityKg: number;
  currentLevelKg: number;
  safetyLevelKg: number;
  hourlyConsumptionKg: number; // Consumo dinámico calculado por hora
  calibrationFactor: number;
  useManualOverride?: boolean;
  manualOverrideFactor?: number;
}

export interface TruckDelivery {
  id: string;
  material: MaterialType;
  quantityKg: number;
  scheduledTime: string;      // Fecha/Hora programada en Odoo
  recommendedTime: string;    // Ventana óptima recomendada por el APS
  status: 'scheduled' | 'recommended' | 'completed' | 'delayed';
}

export interface SiloForecastPoint {
  time: string; // Hora en formato HH:MM
  levelKg: number;
}
