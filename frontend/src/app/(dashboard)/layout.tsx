"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./layout.module.css";

// Definición de interfaces para los ítems de navegación
interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  // Lista de rutas principales y sus iconos vectoriales SVG limpios
  const navItems: NavItem[] = [
    {
      label: "Dashboard",
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
      label: "RM & Silos",
      href: "/silos",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
          <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3" />
        </svg>
      ),
    },
    {
      label: "Aluminios",
      href: "/aluminum",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
      ),
    },
    {
      label: "Capacidad CTP",
      href: "/commercial",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
      ),
    },
    {
      label: "Simulador",
      href: "/simulation",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
          <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
          <line x1="12" y1="22.08" x2="12" y2="12" />
        </svg>
      ),
    },
  ];

  // Resolver título de cabecera dinámicamente según la ruta
  const getHeaderTitle = () => {
    switch (pathname) {
      case "/":
        return "Dashboard General de Operaciones";
      case "/silos":
        return "Planificador de Silos y Materias Primas Pesadas";
      case "/aluminum":
        return "Planificador de Troquelado y Enrolladoras de Aluminio";
      case "/commercial":
        return "Consola Comercial Capable-to-Promise (CTP)";
      case "/simulation":
        return "Entorno Sandbox - Simulación de Escenarios Futuros";
      default:
        return "Consola Operativa";
    }
  };

  return (
    <div className={styles.container}>
      {/* Sidebar Izquierda */}
      <aside className={styles.sidebar}>
        <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
          <header className={styles.logoSection}>
            <div className={styles.logoSub}>Dupon Biscuits</div>
            <h1 className={styles.logoTitle}>Capacity Planner</h1>
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
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sección Logout */}
        <div className={styles.logoutSection}>
          <Link href="/login" className={styles.logoutLink}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            <span>Cerrar Sesión</span>
          </Link>
        </div>
      </aside>

      {/* Panel Principal */}
      <div className={styles.mainArea}>
        {/* Cabezal de Estado */}
        <header className={styles.header}>
          <h2 className={styles.headerTitle}>{getHeaderTitle()}</h2>
          <div className={styles.headerStatusGroup}>
            {/* Estado de Odoo API */}
            <div className={styles.statusIndicator}>
              <span className={`${styles.pulseDot} badge-success`} style={{ animation: "pulse-alert-glow 2s infinite" }}></span>
              <span>Odoo: Conectado (Lectura)</span>
            </div>
            
            {/* Estado de Turno */}
            <div className="badge badge-primary">
              Turno A (Mañana)
            </div>
          </div>
        </header>

        {/* Contenido Dinámico de la Página */}
        <main className={styles.content}>
          {children}
        </main>
      </div>
    </div>
  );
}
