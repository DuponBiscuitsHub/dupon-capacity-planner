/**
 * Shared types and helpers for config tab components.
 *
 * Centralizes TypeScript interfaces used across all config tabs
 * (Lines, Silos, Users, Recipes, LineFormats).
 */

export { apiFetch } from "@/lib/api";


export interface LineCapacity {
  line_code: string;
  company_id: number;
  capacity_kg_h: number;
  is_active: boolean;
}

export interface SiloConfig {
  id: number;
  silo_code: string;
  name: string;
  material_type: string;
  capacity_kg: number;
  safety_stock_kg: number;
  company_id: number;
}

export interface UserItem {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
}

export interface RecipeRate {
  id: number;
  format_code: string;
  material_type: string;
  kg_per_day: number;
  company_id: number;
}

export interface LineFormatItem {
  id: number;
  line_code: string;
  format_code: string;
  machines: number;
  company_id: number;
}

export const MATERIAL_ORDER = [
  "harina", "azucar", "aceite", "lecitina", "sal",
  "carbonat", "caramelina", "maltitol", "cacao", "colorante", "oli_bany",
];

// Las únicas líneas rotativas: pueden tener múltiples cabezales
export const ROTARY_LINES = new Set(["L01", "L02", "L06"]);
