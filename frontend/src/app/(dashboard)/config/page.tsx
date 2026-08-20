"use client";

import { useState } from "react";
import styles from "./config.module.css";
import { useLanguage } from "../../i18n/context";
import LinesTab from "./components/LinesTab";
import SilosTab from "./components/SilosTab";
import UsersTab from "./components/UsersTab";
import RecipesTab from "./components/RecipesTab";
import LineFormatsTab from "./components/LineFormatsTab";

type Tab = "lines" | "silos" | "users" | "recipes" | "lineFormats";

export default function ConfigPage() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<Tab>("lines");

  const tabs: { id: Tab; labelKey: string }[] = [
    { id: "lines",       labelKey: "configTabLines" },
    { id: "silos",       labelKey: "configTabSilos" },
    { id: "users",       labelKey: "configTabUsers" },
    { id: "recipes",     labelKey: "configTabRecipes" },
    { id: "lineFormats", labelKey: "configTabLineFormats" },
  ];

  return (
    <div className={styles.page}>
      <div className={styles.tabBar}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            className={`${styles.tabBtn} ${activeTab === tab.id ? styles.tabActive : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {t(tab.labelKey)}
          </button>
        ))}
      </div>

      <div className={styles.tabPanel}>
        {activeTab === "lines"       && <LinesTab />}
        {activeTab === "silos"       && <SilosTab />}
        {activeTab === "users"       && <UsersTab />}
        {activeTab === "recipes"     && <RecipesTab />}
        {activeTab === "lineFormats" && <LineFormatsTab />}
      </div>
    </div>
  );
}
