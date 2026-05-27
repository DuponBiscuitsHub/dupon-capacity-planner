import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

// Carga optimizada de la tipografía Google Font Outfit
const outfit = Outfit({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-outfit",
});

export const metadata: Metadata = {
  title: "Dupon Capacity Planner",
  description: "Advanced Planning System (APS) externo e interactivo conectado a Odoo ERP para la simulación y análisis de capacidad de planta en tiempo real.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className={outfit.variable}>
      <body>
        {children}
      </body>
    </html>
  );
}
