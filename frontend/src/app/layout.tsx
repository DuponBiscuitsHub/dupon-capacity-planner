import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import { LanguageProvider } from "./i18n/context";
import { CompanyProvider } from "./context/CompanyContext";

// Optimized loading of Google Font Outfit
const outfit = Outfit({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-outfit",
});

export const metadata: Metadata = {
  title: "Dupon Capacity Planner",
  description: "Advanced Planning System (APS) external console connected to Odoo ERP for real-time capacity simulation and analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className={outfit.variable}>
      <body>
        {/* Global i18n translation and multicompany contexts */}
        <LanguageProvider>
          <CompanyProvider>
            {children}
          </CompanyProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
