"use client";

import { useState } from "react";
import styles from "./users.module.css";
import { useLanguage } from "../../i18n/context";

// Definition of the User Profile interface
interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: "admin" | "planner" | "commercial" | "viewer";
  companyName: string;
  status: "active" | "suspended";
}

export default function UsersPage() {
  const { t } = useLanguage();
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 1. Initial Users State (RBAC Roles and Multicompany affiliation)
  const [users, setUsers] = useState<UserProfile[]>([
    {
      id: "usr-1",
      name: "Marc Pakipy",
      email: "marc.pakipy@dupon.com",
      role: "admin",
      companyName: "Dupon Ibèrica 🇪🇸",
      status: "active",
    },
    {
      id: "usr-2",
      name: "Jean Dupont",
      email: "jean.dupont@dupon.be",
      role: "planner",
      companyName: "Dupon Belgique 🇧🇪",
      status: "active",
    },
    {
      id: "usr-3",
      name: "Sophie Lemaire",
      email: "sophie.lemaire@dupon.fr",
      role: "commercial",
      companyName: "Dupon France 🇫🇷",
      status: "active",
    },
    {
      id: "usr-4",
      name: "Thomas Schmidt",
      email: "t.schmidt@dupon.de",
      role: "viewer",
      companyName: "Dupon France 🇫🇷",
      status: "active",
    },
  ]);

  // 2. Local states for new user registration form
  const [newName, setNewName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState<"admin" | "planner" | "commercial" | "viewer">("planner");
  const [newCompany, setNewCompany] = useState("Dupon Ibèrica 🇪🇸");

  // 3. Create user and inject dynamically into state
  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault();

    if (!newName || !newEmail) {
      alert("Por favor, rellena todos los campos obligatorios.");
      return;
    }

    const newUser: UserProfile = {
      id: `usr-${Date.now()}`,
      name: newName,
      email: newEmail,
      role: newRole,
      companyName: newCompany,
      status: "active",
    };

    setUsers((prevUsers) => [newUser, ...prevUsers]);
    
    // Reset form and close modal overlay
    setNewName("");
    setNewEmail("");
    setNewRole("planner");
    setIsModalOpen(false);
  };

  // Helper: Resolve HSL badge style according to RBAC role
  const getRoleBadge = (role: string) => {
    switch (role) {
      case "admin":
        return <span className="badge badge-primary">Admin</span>;
      case "planner":
        return <span className="badge badge-warning">Planner</span>;
      case "commercial":
        return <span className="badge badge-success">Commercial</span>;
      case "viewer":
        default:
          return <span className="badge" style={{ backgroundColor: "var(--border-light)", color: "var(--text-secondary)", border: "1px solid var(--border-light)" }}>Viewer</span>;
    }
  };

  return (
    <div className={styles.container}>
      
      {// Section Header
      }
      <section className={styles.headerSection}>
        <div className={styles.titleArea}>
          <h1 className={styles.title}>{t("titleUsers")}</h1>
          <p className={styles.subtitle}>
            Administración de permisos, asignación multicompañía y roles de seguridad para la consola de planificación.
          </p>
        </div>

        <button 
          className={styles.addUserBtn}
          onClick={() => setIsModalOpen(true)}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          {t("btnRegisterUser")}
        </button>
      </section>

      {// Users Data Grid
      }
      <section className={`${styles.usersCard} glass-panel`}>
        <div className={styles.tableWrapper}>
          <table className={styles.usersTable}>
            <thead>
              <tr>
                <th className={styles.th}>Nombre & Email</th>
                <th className={styles.th}>Rol Operativo (RBAC)</th>
                <th className={styles.th}>Filiación Logística</th>
                <th className={styles.th}>Estado</th>
                <th className={styles.th} style={{ textAlign: "right" }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td className={styles.td}>
                    <div className={styles.userInfo}>
                      <span className={styles.userName}>{user.name}</span>
                      <span className={styles.userEmail}>{user.email}</span>
                    </div>
                  </td>
                  <td className={styles.td}>{getRoleBadge(user.role)}</td>
                  <td className={styles.td}>
                    <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>{user.companyName}</span>
                  </td>
                  <td className={styles.td}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span className="badge-success" style={{ width: "8px", height: "8px", borderRadius: "50%", display: "inline-block" }}></span>
                      <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Activo</span>
                    </div>
                  </td>
                  <td className={styles.td} style={{ textAlign: "right" }}>
                    <button className="simulateBtn" style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem", background: "none", border: "1px solid var(--border-light)", color: "var(--text-secondary)" }}>
                      Editar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {// Interactive Modal Window (Overlay with Glassmorphic Card)
      }
      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={`${styles.modalCard} glass-panel`}>
            <header className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>Registrar Nuevo Operador</h3>
              <button 
                className={styles.closeBtn}
                onClick={() => setIsModalOpen(false)}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </header>

            <form className={styles.form} onSubmit={handleCreateUser}>
              <div className={styles.formGroup}>
                <label className={styles.label} htmlFor="name">Nombre y Apellidos</label>
                <input
                  id="name"
                  type="text"
                  placeholder="ej. Carlos García"
                  className={styles.input}
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label} htmlFor="email">Correo Electrónico</label>
                <input
                  id="email"
                  type="email"
                  placeholder="ej. garcia@dupon.com"
                  className={styles.input}
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label} htmlFor="role">Rol Operativo (Privilegios RBAC)</label>
                <select
                  id="role"
                  className={styles.select}
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value as any)}
                >
                  <option value="admin">Administrador (Acceso Total)</option>
                  <option value="planner">Planificador (Silos & Aluminios)</option>
                  <option value="commercial">Comercial (CTP Ventas)</option>
                  <option value="viewer">Viewer (Lectura Pantallas)</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label} htmlFor="company">Compañía de Asignación</label>
                <select
                  id="company"
                  className={styles.select}
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
                >
                  <option value="Dupon Ibèrica 🇪🇸">Dupon Ibèrica 🇪🇸</option>
                  <option value="Dupon France 🇫🇷">Dupon France 🇫🇷</option>
                  <option value="Dupon Belgique 🇧🇪">Dupon Belgique 🇧🇪</option>
                </select>
              </div>

              <footer className={styles.modalActions}>
                <button 
                  type="button" 
                  className={styles.cancelBtn}
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancelar
                </button>
                <button type="submit" className={styles.addUserBtn}>
                  {t("btnRegisterUser")}
                </button>
              </footer>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
