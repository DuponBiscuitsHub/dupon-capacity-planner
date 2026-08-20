"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./layout.module.css";
import { useLanguage } from "../i18n/context";
import { LanguageType } from "../i18n/translations";
import { useCompany } from "../context/CompanyContext";
import { API_BASE } from "@/lib/api";
import dynamic from "next/dynamic";

const OdooStatusDot = dynamic(
  () => import("./components/OdooStatusDot"),
  { ssr: false }
);

interface CurrentUser {
  username: string;
  role: string;
}

interface NavItem {
  labelKey: string;
  href: string;
  icon: React.ReactNode;
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { language, setLanguage, t } = useLanguage();
  const { companyId, companies, setCompanyId } = useCompany();
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);

  // Auth: verificar sesión activa con el backend (cookie HttpOnly, no document.cookie)
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/auth/me`, { credentials: "include" })
      .then((res) => {
        if (!res.ok) throw new Error("unauthenticated");
        return res.json() as Promise<CurrentUser>;
      })
      .then(setCurrentUser)
      .catch(() => router.replace("/login"));
  }, [router]);

  const handleLogout = async (e: React.MouseEvent) => {
    e.preventDefault();
    try {
      await fetch(`${API_BASE}/api/v1/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } finally {
      router.replace("/login");
    }
  };

  const navItems: NavItem[] = [
    {
      labelKey: "navDashboard",
      href: "/",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="9" />
          <rect x="14" y="3" width="7" height="5" />
          <rect x="14" y="12" width="7" height="9" />
          <rect x="3" y="16" width="7" height="5" />
        </svg>
      ),
    },
    {
      labelKey: "navSilos",
      href: "/silos",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
          <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3" />
        </svg>
      ),
    },
    // Config solo visible para rol IT
    ...(currentUser?.role === "it"
      ? [
          {
            labelKey: "navConfig",
            href: "/config",
            icon: (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
            ),
          },
        ]
      : []),
  ];

  const getHeaderTitle = () => {
    switch (pathname) {
      case "/": return t("titleDashboard");
      case "/silos": return t("titleSilos");
      case "/config": return t("titleConfig");
      default: return "DCP";
    }
  };

  return (
    <div className={styles.container}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
        <header className={styles.logoSection}>
            <div className={styles.logoRow}>
              <div className={styles.logoIcon}>D</div>
              <div>
                <div className={styles.logoTitle}>Factory Edge</div>
                <div className={styles.logoSub}>Dupon Biscuits Ibérica SAU</div>
              </div>
            </div>
          </header>

          <nav className={styles.navSection}>
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`${styles.navLink} ${isActive ? styles.activeNavLink : ""}`}
                >
                  {item.icon}
                  <span>{t(item.labelKey)}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer sidebar: usuario + logout */}
        <div className={styles.logoutSection}>
          {currentUser && (
            <div style={{ fontSize: "0.75rem", opacity: 0.6, marginBottom: "0.5rem", paddingLeft: "0.5rem" }}>
              {currentUser.username}
              <span style={{ marginLeft: "0.4rem", opacity: 0.5 }}>({currentUser.role})</span>
            </div>
          )}
          <button id="btn-logout" onClick={handleLogout} className={styles.logoutLink} style={{ width: "100%", cursor: "pointer", border: "none", background: "none" }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            <span>{t("navLogout")}</span>
          </button>
        </div>
      </aside>

      {/* Main area */}
      <div className={styles.mainArea}>
        <header className={styles.header}>
          <h2 className={styles.headerTitle}>{getHeaderTitle()}</h2>
          <div className={styles.headerStatusGroup}>
            {/* Odoo connectivity indicator */}
            <OdooStatusDot />
            {companies.length > 1 && (
              <div className={styles.languageSelectorWrapper}>
                <select
                  id="select-company"
                  value={companyId}
                  onChange={(e) => setCompanyId(parseInt(e.target.value, 10))}
                  className={styles.languageSelect}
                >
                  {companies.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.short_code ?? c.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            {/* Selector idioma — ES, CA, EN */}
            <div className={styles.languageSelectorWrapper}>
              <select
                id="select-language"
                value={language}
                onChange={(e) => setLanguage(e.target.value as LanguageType)}
                className={styles.languageSelect}
              >
                <option value="es">ES 🇪🇸</option>
                <option value="ca">CA</option>
                <option value="en">EN 🇬🇧</option>
              </select>
            </div>
          </div>
        </header>

        <main className={styles.content}>{children}</main>
      </div>
    </div>
  );
}
