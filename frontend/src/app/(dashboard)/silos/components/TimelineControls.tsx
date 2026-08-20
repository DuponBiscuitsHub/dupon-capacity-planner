"use client";

import styles from "../silos.module.css";
import { useLanguage } from "../../../i18n/context";
import { getMatLabelLong } from "./silosShared";

// ── Forecast dropdown ─────────────────────────────────────────────────────────

const FORECAST_OPTIONS = [15, 30, 45];

export function ForecastDropdown({
  forecastDays,
  setForecastDays,
  t,
}: {
  forecastDays: number;
  setForecastDays: (v: number) => void;
  t: (k: string) => string;
}) {
  return (
    <select
      className={styles.forecastSelect}
      value={forecastDays}
      onChange={(e) => setForecastDays(Number(e.target.value))}
    >
      {FORECAST_OPTIONS.map((d) => (
        <option key={d} value={d}>
          {t("planForecast")}: {t("planDays").replace("{n}", String(d))}
        </option>
      ))}
    </select>
  );
}

// ── Material filter ────────────────────────────────────────────────────────────

const MATERIALS = ["harina", "azucar", "aceite"];

export function MaterialFilter({
  value,
  onChange,
}: {
  value: Set<string>;
  onChange: (v: Set<string>) => void;
}) {
  const { t } = useLanguage();

  const toggle = (m: string) => {
    const next = new Set(value);
    next.has(m) ? next.delete(m) : next.add(m);
    onChange(next);
  };

  return (
    <div className={styles.filterRow}>
      {MATERIALS.map(m => (
        <button
          key={m}
          id={`filter-${m}`}
          className={`${styles.filterBtn} ${value.has(m) ? styles.filterActive : ""}`}
          onClick={() => toggle(m)}
        >
          {getMatLabelLong(m, t)}
        </button>
      ))}
      {value.size > 0 && (
        <button className={styles.filterClear} onClick={() => onChange(new Set())}>
          {t("silosFilterAll")}
        </button>
      )}
    </div>
  );
}
