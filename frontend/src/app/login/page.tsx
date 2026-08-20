"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "../i18n/context";
import styles from "./login.module.css";
import { API_BASE } from "@/lib/api";

// ── Brand panel decoración ─────────────────────────────────────────────────
function BrandPanel() {
  return (
    <div className={styles.brandPanel}>
      {/* Logo mark */}
      <div style={{ marginBottom: "2rem" }}>
        <div style={{
          width: 44, height: 44, borderRadius: 10,
          background: "var(--color-primary)",
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 4px 16px hsla(152,69%,41%,0.4)",
          marginBottom: "1.5rem",
        }}>
          {/* Icono silo/fábrica */}
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <ellipse cx="12" cy="5" rx="9" ry="3" />
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
            <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3" />
          </svg>
        </div>

        <div className={styles.brandTitle}>
          DCP<br />Planner
        </div>
        <div className={styles.brandSub}>
          Raw Material Planning<br />
          para Dupon Biscuits Ibérica
        </div>
      </div>

      <div className={styles.brandBadge}>
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <circle cx="12" cy="12" r="10" /><path d="m9 12 2 2 4-4" />
        </svg>
        Factory Edge · v2.0
      </div>

      {/* Decorative dots */}
      <div className={styles.brandDecor}>
        {Array.from({ length: 20 }).map((_, i) => (
          <span key={i} />
        ))}
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────
export default function LoginPage() {
  const { t } = useLanguage();
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    startTransition(async () => {
      try {
        // OAuth2PasswordRequestForm espera application/x-www-form-urlencoded
        const body = new URLSearchParams({ username, password });
        const resp = await fetch(`${API_BASE}/api/v1/auth/login`, {
          method: "POST",
          credentials: "include", // para que el browser acepte la cookie HttpOnly
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: body.toString(),
        });

        if (!resp.ok) {
          setError(t("loginError"));
          return;
        }

        // El backend emitió la cookie dcp_token HttpOnly → redirigir al dashboard
        router.replace("/");
      } catch {
        setError(t("errorLoading"));
      }
    });
  };

  return (
    <div className={styles.container}>
      {/* Panel izquierdo de marca */}
      <BrandPanel />

      {/* Formulario derecho */}
      <div className={styles.card}>
        <div className={styles.logoSection}>
          <div className={styles.logoMark}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <ellipse cx="12" cy="5" rx="9" ry="3" />
              <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3" />
            </svg>
          </div>
          <h1 className={styles.title}>{t("loginTitle")}</h1>
          <p className={styles.subtitle}>Dupon Biscuits · Ibérica</p>
        </div>

        <form id="form-login" onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.fieldGroup}>
            <label htmlFor="input-username" className={styles.label}>
              {t("loginUserLabel")}
            </label>
            <input
              id="input-username"
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={styles.input}
              placeholder="usuario"
            />
          </div>

          <div className={styles.fieldGroup}>
            <label htmlFor="input-password" className={styles.label}>
              {t("loginPassLabel")}
            </label>
            <input
              id="input-password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.input}
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div id="login-error" role="alert" className={styles.errorBanner}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {error}
            </div>
          )}

          <button
            id="btn-login"
            type="submit"
            disabled={isPending}
            className={styles.submitBtn}
          >
            {isPending ? (
              <>
                <span style={{
                  display: "inline-block", width: 14, height: 14,
                  border: "2px solid rgba(255,255,255,0.35)", borderTopColor: "#fff",
                  borderRadius: "50%", animation: "spin 0.7s linear infinite",
                }} />
                {t("loading")}
              </>
            ) : t("loginBtn")}
          </button>
        </form>

        <footer className={styles.footer}>{t("loginFooter")}</footer>
      </div>
    </div>
  );
}
