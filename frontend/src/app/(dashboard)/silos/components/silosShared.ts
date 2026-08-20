/**
 * Shared types and helpers for silos page components.
 */

export { API_BASE, apiFetch } from "@/lib/api";

export interface SiloStatus {
  silo_code: string;
  name: string;
  material_type: string;
  capacity_kg: number;
  current_stock_kg: number | null;
  fill_pct: number | null;
  autonomy_hours: number | null;
  status: "ok" | "warning" | "critical" | "unknown";
}

export interface PlanRow {
  material_type: string;
  po_line_odoo_id: number | null;
  order_odoo_id: number | null;
  po_name: string | null;
  partner_name: string | null;
  product_ref: string | null;
  vendor_confirmed: boolean;
  timing_color: "green" | "orange" | "red";
  po_qty_kg: number | null;
  po_date_planned: string | null;
  po_state: string | null;
  app_suggested_date: string | null;
  can_edit: boolean;
  edit_warning: string | null;
}


export function fmtKg(kg: number | null): string {
  if (kg === null) return "—";
  return kg >= 1000 ? `${(kg / 1000).toFixed(1)} t` : `${Math.round(kg)} kg`;
}

export function fmtPct(pct: number | null): string {
  return pct !== null ? `${Math.round(pct)}%` : "—";
}

export function dayLabel(d: Date, locale: string): string {
  return d.toLocaleDateString(locale, { day: "2-digit", month: "2-digit" });
}

export function getMatLabelShort(material: string, t: (k: string) => string): string {
  const MAP: Record<string, string> = {
    harina: t("matHarina"),
    azucar: t("matAzucar"),
    aceite: t("matAceite"),
  };
  return MAP[material] ?? material.toUpperCase();
}

export function getMatLabelLong(material: string, t: (k: string) => string): string {
  const MAP: Record<string, string> = {
    harina: t("matHarinaLong"),
    azucar: t("matAzucarLong"),
    aceite: t("matAceiteLong"),
  };
  return MAP[material] ?? material;
}
