"use client";

import { useCallback, useEffect, useState } from "react";
import styles from "./OdooStatusDot.module.css";
import { useLanguage } from "../../i18n/context";
import { apiFetch } from "@/lib/api";

type OdooHealth = {
  odoo_reachable: boolean;
  latency_ms: number | null;
  odoo_mode: string;
  error: string | null;
};

type Status = "connected" | "disconnected" | "checking" | "mock" | "unknown";

const CHECK_INTERVAL_MS = 5 * 60 * 1000; // 5 min

export default function OdooStatusDot() {
  const { t } = useLanguage();
  const [status, setStatus] = useState<Status>("unknown");
  const [latency, setLatency] = useState<number | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const check = useCallback(async () => {
    setStatus("checking");
    try {
      const data = await apiFetch<OdooHealth>("/api/v1/sync/health");
      if (data.odoo_mode === "mock") {
        setStatus("mock");
        setLatency(null);
      } else if (data.odoo_reachable) {
        setStatus("connected");
        setLatency(data.latency_ms);
      } else {
        setStatus("disconnected");
        setLatency(null);
      }
    } catch {
      setStatus("disconnected");
      setLatency(null);
    }
  }, []);

  useEffect(() => {
    check();
    const id = setInterval(check, CHECK_INTERVAL_MS);
    return () => clearInterval(id);
  }, [check]);

  const tooltipText = (() => {
    switch (status) {
      case "connected":
        return latency !== null
          ? t("odooStatusConnected").replace("{ms}", String(latency))
          : t("odooStatusConnected").replace(" ({ms}ms)", "");
      case "disconnected":
        return t("odooStatusDisconnected");
      case "mock":
        return t("odooStatusMock");
      case "checking":
        return t("odooStatusChecking");
      default:
        return t("odooStatusChecking");
    }
  })();

  const dotClass = (() => {
    switch (status) {
      case "connected":
        return styles.dotConnected;
      case "disconnected":
        return styles.dotDisconnected;
      case "mock":
        return styles.dotMock;
      default:
        return styles.dotUnknown;
    }
  })();

  return (
    <div
      className={styles.wrapper}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      aria-label={tooltipText}
    >
      <span className={`${styles.dot} ${dotClass}`} />
      {showTooltip && (
        <div className={styles.tooltip}>{tooltipText}</div>
      )}
    </div>
  );
}
