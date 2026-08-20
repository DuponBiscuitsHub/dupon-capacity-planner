"use client";

import { useEffect, useRef } from "react";
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
  Legend,
);

// ── Types ───────────────────────────────────────────────────────────────────────

interface SiloProjection {
  silo_code: string;
  material_type: string;
  capacity_kg: number;
  safety_stock_kg: number;
  consumption_kg_day: number;
  points: { date: string; stock_kg: number }[];
  po_events: { date: string; qty_kg: number; po_name: string }[];
}

interface Props {
  projections: SiloProjection[];
  t: (key: string) => string;
}

// ── Color palette ───────────────────────────────────────────────────────────────

const SILO_COLORS: Record<string, { line: string; fill: string }> = {
  "S-H1":  { line: "hsl(40, 75%, 55%)",   fill: "hsla(40, 75%, 55%, 0.12)" },
  "S-H2":  { line: "hsl(30, 70%, 50%)",   fill: "hsla(30, 70%, 50%, 0.12)" },
  "S-H3":  { line: "hsl(50, 65%, 48%)",   fill: "hsla(50, 65%, 48%, 0.12)" },
  "S-AZ":  { line: "hsl(200, 70%, 55%)",  fill: "hsla(200, 70%, 55%, 0.12)" },
  "S-AC":  { line: "hsl(152, 60%, 45%)",  fill: "hsla(152, 60%, 45%, 0.12)" },
};

const DEFAULT_COLOR = { line: "hsl(260, 50%, 60%)", fill: "hsla(260, 50%, 60%, 0.12)" };

function getColor(siloCode: string) {
  return SILO_COLORS[siloCode] ?? DEFAULT_COLOR;
}

// ── Chart label helpers ─────────────────────────────────────────────────────────

function formatDateLabel(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

function kgToTons(kg: number): number {
  return Math.round(kg / 100) / 10; // 1 decimal
}

// ── Component ───────────────────────────────────────────────────────────────────

export default function StockProjectionChart({ projections, t }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!canvasRef.current || projections.length === 0) return;

    // Destroy previous chart instance
    if (chartRef.current) {
      chartRef.current.destroy();
      chartRef.current = null;
    }

    const first = projections[0];
    const labels = first.points.map((p) => formatDateLabel(p.date));

    // Global capacity & safety lines (max across all silos)
    const maxCapacity = Math.max(...projections.map((p) => p.capacity_kg));
    const maxSafety   = Math.max(...projections.map((p) => p.safety_stock_kg));

    const datasets = [
      // Capacity reference line (dashed)
      {
        label: t("chartCapacity"),
        data: labels.map(() => kgToTons(maxCapacity)),
        borderColor: "hsla(220, 20%, 55%, 0.5)",
        borderDash: [6, 4],
        borderWidth: 1.5,
        pointRadius: 0,
        fill: false,
        order: 10,
      },
      // Safety stock reference line (dashed)
      {
        label: t("chartSafety"),
        data: labels.map(() => kgToTons(maxSafety)),
        borderColor: "hsla(0, 70%, 55%, 0.5)",
        borderDash: [4, 4],
        borderWidth: 1.5,
        pointRadius: 0,
        fill: false,
        order: 10,
      },
      // Silo projection lines
      ...projections.map((proj) => {
        const color = getColor(proj.silo_code);
        return {
          label: proj.silo_code,
          data: proj.points.map((p) => kgToTons(p.stock_kg)),
          borderColor: color.line,
          backgroundColor: color.fill,
          borderWidth: 2.5,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: color.line,
          tension: 0.3,
          fill: true,
          order: 1,
        };
      }),
    ];

    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            position: "top",
            labels: {
              color: "hsl(220, 15%, 70%)",
              usePointStyle: true,
              pointStyle: "circle",
              padding: 16,
              font: { size: 12, family: "'Inter', system-ui, sans-serif" },
              filter: (item) => {
                // Hide capacity/safety from legend if desired
                return true;
              },
            },
          },
          tooltip: {
            backgroundColor: "hsla(222, 22%, 14%, 0.95)",
            titleColor: "#e8eaf0",
            bodyColor: "hsl(220, 15%, 70%)",
            borderColor: "hsla(220, 30%, 35%, 0.4)",
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            titleFont: { weight: "bold" as const, size: 13 },
            bodyFont: { size: 12 },
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} t`,
            },
          },
        },
        scales: {
          x: {
            grid: {
              color: "hsla(220, 20%, 30%, 0.3)",
            },
            ticks: {
              color: "hsl(220, 15%, 60%)",
              font: { size: 11 },
            },
          },
          y: {
            min: 0,
            title: {
              display: true,
              text: t("chartStock"),
              color: "hsl(220, 15%, 60%)",
              font: { size: 12 },
            },
            grid: {
              color: "hsla(220, 20%, 30%, 0.3)",
            },
            ticks: {
              color: "hsl(220, 15%, 60%)",
              font: { size: 11 },
              callback: (val) => `${val} t`,
            },
          },
        },
      },
    });

    return () => {
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, [projections, t]);

  if (projections.length === 0) {
    return <p style={{ color: "var(--text-muted)", textAlign: "center" }}>{t("chartNoData")}</p>;
  }

  return (
    <div style={{ position: "relative", width: "100%", height: "340px" }}>
      <canvas ref={canvasRef} />
    </div>
  );
}
