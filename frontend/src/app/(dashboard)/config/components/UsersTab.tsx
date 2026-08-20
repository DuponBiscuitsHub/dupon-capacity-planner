"use client";

import { useCallback, useEffect, useState } from "react";
import styles from "../config.module.css";
import { useLanguage } from "../../../i18n/context";
import { apiFetch, type UserItem } from "./shared";

export default function UsersTab() {
  const { t } = useLanguage();
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [newUser, setNewUser] = useState({ username: "", password: "", role: "user" });

  const fetchUsers = useCallback(async () => {
    try {
      const data = await apiFetch<UserItem[]>("/api/v1/users");
      setUsers(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setCreating(true);
    try {
      const created = await apiFetch<UserItem>("/api/v1/users", {
        method: "POST",
        body: JSON.stringify(newUser),
      });
      setUsers((prev) => [...prev, created]);
      setNewUser({ username: "", password: "", role: "user" });
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    } finally {
      setCreating(false);
    }
  };

  const handleDeactivate = async (id: number) => {
    setError(null);
    try {
      await apiFetch<void>(`/api/v1/users/${id}`, { method: "DELETE" });
      setUsers((prev) => prev.map((u) => (u.id === id ? { ...u, is_active: false } : u)));
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorLoading"));
    }
  };

  if (loading) return <div className={styles.loading}>{t("loading")}</div>;

  return (
    <div className={styles.tabContent}>
      {error && <div role="alert" className={styles.errorMsg}>{error}</div>}

      <form id="form-create-user" onSubmit={handleCreate} className={styles.createForm}>
        <h3 className={styles.formTitle}>{t("usersCreateTitle")}</h3>
        <div className={styles.formRow}>
          <input id="input-new-username" type="text" required placeholder={t("usersPlaceholderUser")} className={styles.textInput}
            value={newUser.username} onChange={(e) => setNewUser((v) => ({ ...v, username: e.target.value }))} />
          <input id="input-new-password" type="password" required placeholder={t("usersPlaceholderPass")} minLength={8}
            className={styles.textInput} value={newUser.password}
            onChange={(e) => setNewUser((v) => ({ ...v, password: e.target.value }))} />
          <select id="select-new-role" className={styles.selectInput} value={newUser.role}
            onChange={(e) => setNewUser((v) => ({ ...v, role: e.target.value }))}>
            <option value="user">{t("usersRoleUser")}</option>
            <option value="it">{t("usersRoleIt")}</option>
          </select>
          <button id="btn-create-user" type="submit" disabled={creating} className={styles.saveBtn}>
            {creating ? t("usersCreating") : t("usersCreate2")}
          </button>
        </div>
      </form>

      <div className={styles.tableWrap}>
        <table id="table-users" className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>{t("configColUser")}</th>
              <th className={styles.th}>{t("configColRole")}</th>
              <th className={styles.th}>{t("configColStatus")}</th>
              <th className={styles.th}></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className={`${styles.tr} ${!u.is_active ? styles.inactiveRow : ""}`}>
                <td className={styles.td}>{u.username}</td>
                <td className={styles.td}>
                  <span className={u.role === "it" ? styles.roleIt : styles.roleUser}>
                    {u.role === "it" ? t("usersRoleIt") : t("usersRoleUser")}
                  </span>
                </td>
                <td className={styles.td}>
                  <span className={u.is_active ? styles.activeTag : styles.idleTag}>
                    {u.is_active ? t("statusActive") : t("statusInactive")}
                  </span>
                </td>
                <td className={styles.tdActions}>
                  {u.is_active && (
                    <button
                      id={`btn-deactivate-${u.id}`}
                      className={styles.deactivateBtn}
                      onClick={() => handleDeactivate(u.id)}
                    >
                      {t("actionDeactivate")}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
