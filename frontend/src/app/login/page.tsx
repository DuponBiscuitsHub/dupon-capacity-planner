"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./login.module.css";
import { useLanguage } from "../i18n/context";
import { LanguageType } from "../i18n/translations";

export default function LoginPage() {
  const router = useRouter();
  const { t, language, setLanguage } = useLanguage();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Simple local validation
    if (!username || !password) {
      setError(t("loginErrorEmpty"));
      return;
    }

    setLoading(true);

    // Simulated local MVP authentication with 1.2s delay
    setTimeout(() => {
      setLoading(false);
      
      // SECURITY FIRST: Set secure session cookie with strict flags
      // In production, the BFF should set this as HttpOnly and Secure via Set-Cookie headers
      // TODO(security): BFF will take over cookie management to prevent XSS-based session harvesting
      document.cookie = "dcp_session=active_token; Path=/; SameSite=Strict; Secure";
      
      // Route directly to dashboard home
      router.push("/");
    }, 1200);
  };

  return (
    <div className={styles.container}>
      {/* Floating Language Selector (Top-right corner) */}
      <div className={styles.floatingSelectors}>
        {/* Language Selector */}
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value as LanguageType)}
          className={styles.floatingSelect}
        >
          <option value="es">Español 🇪🇸</option>
          <option value="en">English 🇬🇧</option>
          <option value="fr">Français 🇫🇷</option>
          <option value="de">Deutsch 🇩🇪</option>
          <option value="be">Belgisch 🇧🇪</option>
          <option value="ca">Català 🇦🇩</option>
        </select>
      </div>

      {/* Decorative background orbs */}
      <div className={styles.backgroundOrb}></div>
      <div className={styles.backgroundOrb2}></div>

      {/* Glassmorphic Login Card */}
      <main className={`${styles.card} glass-panel`}>
        <header className={styles.header}>
          <div className={styles.logoSub}>Dupon Biscuits</div>
          <h1 className={styles.logoText}>Capacity Planner</h1>
          <h2 className={styles.title}>{t("loginTitle")}</h2>
        </header>

        <form className={styles.form} onSubmit={handleSubmit}>
          {error && (
            <div className="badge badge-danger" style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", justifyContent: "center", textTransform: "none", fontSize: "0.85rem" }}>
              {error}
            </div>
          )}

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="username">{t("loginUserLabel")}</label>
            <input
              id="username"
              type="text"
              placeholder="ejemplo@dupon.com"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="password">{t("loginPassLabel")}</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          <button className={styles.submitBtn} type="submit" disabled={loading}>
            {loading ? "..." : t("loginBtn")}
          </button>
        </form>

        <footer className={styles.footer}>
          {t("loginFooter")}
        </footer>
      </main>
    </div>
  );
}
