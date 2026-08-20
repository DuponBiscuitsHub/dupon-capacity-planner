"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

export interface CompanyInfo {
  id: number;
  name: string;
  short_code: string | null;
}

interface CompanyContextProps {
  companyId: number;
  companies: CompanyInfo[];
  setCompanyId: (id: number) => void;
  loading: boolean;
}

const CompanyContext = createContext<CompanyContextProps | undefined>(undefined);

export function CompanyProvider({ children }: { children: React.ReactNode }) {
  const [companyId, setCompanyIdState] = useState<number>(1);
  const [companies, setCompanies] = useState<CompanyInfo[]>([]);
  const [loading, setLoading] = useState(true);

  // Cargar lista de compañías del backend
  const loadCompanies = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/companies`, {
        credentials: "include",
      });
      if (res.ok) {
        const data = (await res.json()) as CompanyInfo[];
        setCompanies(data);
      }
    } catch {
      // Sin backend o sin auth — no hacemos nada
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCompanies();
  }, [loadCompanies]);

  // Recuperar preferencia de compañía de localStorage
  useEffect(() => {
    const saved = localStorage.getItem("dcp-company-id");
    if (saved) {
      const parsed = parseInt(saved, 10);
      if (!isNaN(parsed) && parsed > 0) {
        setCompanyIdState(parsed);
      }
    }
  }, []);

  const setCompanyId = (id: number) => {
    setCompanyIdState(id);
    localStorage.setItem("dcp-company-id", String(id));
  };

  return (
    <CompanyContext.Provider value={{ companyId, companies, setCompanyId, loading }}>
      {children}
    </CompanyContext.Provider>
  );
}

export function useCompany() {
  const context = useContext(CompanyContext);
  if (context === undefined) {
    throw new Error("useCompany debe usarse dentro de un CompanyProvider");
  }
  return context;
}
