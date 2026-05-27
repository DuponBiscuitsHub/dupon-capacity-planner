"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type CompanyType = "iberica" | "france" | "belgica";

interface CompanyContextProps {
  selectedCompany: CompanyType;
  setSelectedCompany: (company: CompanyType) => void;
}

const CompanyContext = createContext<CompanyContextProps | undefined>(undefined);

export function CompanyProvider({ children }: { children: React.ReactNode }) {
  const [selectedCompany, setSelectedCompanyState] = useState<CompanyType>("iberica");

  // Recuperar preferencia de compañía al cargar
  useEffect(() => {
    const savedCompany = localStorage.getItem("dcp-company") as CompanyType;
    if (savedCompany && ["iberica", "france", "belgica"].includes(savedCompany)) {
      setSelectedCompanyState(savedCompany);
    }
  }, []);

  // Cambiar y persistir compañía
  const setSelectedCompany = (company: CompanyType) => {
    setSelectedCompanyState(company);
    localStorage.setItem("dcp-company", company);
  };

  return (
    <CompanyContext.Provider value={{ selectedCompany, setSelectedCompany }}>
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
