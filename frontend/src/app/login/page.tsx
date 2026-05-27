"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./login.module.css";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validación básica local
    if (!username || !password) {
      setError("Por favor, introduce tu usuario y contraseña.");
      return;
    }

    setLoading(true);

    // Simulación de autenticación local del MVP (1.5s de delay)
    setTimeout(() => {
      setLoading(false);
      // Redirigir directamente al panel de control (Dashboard)
      router.push("/");
    }, 1200);
  };

  return (
    <div className={styles.container}>
      {/* Esferas decorativas en background */}
      <div className={styles.backgroundOrb}></div>
      <div className={styles.backgroundOrb2}></div>

      {/* Tarjeta de login Glassmorphic */}
      <main className={`${styles.card} glass-panel`}>
        <header className={styles.header}>
          <div className={styles.logoSub}>Dupon Biscuits</div>
          <h1 className={styles.logoText}>Capacity Planner</h1>
          <h2 className={styles.title}>Acceso de Operaciones</h2>
        </header>

        <form className={styles.form} onSubmit={handleSubmit}>
          {error && (
            <div className="badge badge-danger" style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", justifyContent: "center", textTransform: "none", fontSize: "0.85rem" }}>
              {error}
            </div>
          )}

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="username">Usuario o Email</label>
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
            <label className={styles.label} htmlFor="password">Contraseña</label>
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
            {loading ? "Autenticando..." : "Ingresar a Consola"}
          </button>
        </form>

        <footer className={styles.footer}>
          Dupon Capacity Planner v1.0.0 &copy; 2026. <br />
          Conectado de forma segura a <strong>Odoo ERP</strong>.
        </footer>
      </main>
    </div>
  );
}
