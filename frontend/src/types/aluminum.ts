/* Definición de Interfaces para el Módulo de Aluminio */

export type MachineType = 'troquel' | 'enrolladora';
export type FormatType = 'F1' | 'F2' | 'F3' | 'F4' | 'F5' | 'F6';
export type MachineStatus = 'running' | 'idle' | 'maintenance';

export interface Machine {
  id: string;
  name: string;
  type: MachineType;
  status: MachineStatus;
  activeFormat: FormatType | '-';
  weeklyCapacityPacks: number;
  weeklyLoadPacks: number;
}

export interface FormatSaturation {
  format: FormatType;
  name: string;
  troquelLoadPercent: number;
  enrolladoraLoadPercent: number;
}

export interface PlantAllocation {
  plantName: string;
  sharePercent: number;
  volumePacks: number;
}
