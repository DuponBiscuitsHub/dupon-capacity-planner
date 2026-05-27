"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { LanguageType, translations } from "./translations";

interface LanguageContextProps {
  language: LanguageType;
  setLanguage: (lang: LanguageType) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextProps | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<LanguageType>("es");

  // Al inicializar en el navegador, recuperar la preferencia guardada en localStorage
  useEffect(() => {
    const savedLang = localStorage.getItem("dcp-language") as LanguageType;
    if (savedLang && ["es", "en", "fr", "de", "be", "ca"].includes(savedLang)) {
      setLanguageState(savedLang);
    }
  }, []);

  // Guardar la preferencia al cambiar
  const setLanguage = (lang: LanguageType) => {
    setLanguageState(lang);
    localStorage.setItem("dcp-language", lang);
  };

  // Función traductora desacoplada
  const t = (key: string): string => {
    const entry = translations[key];
    if (!entry) {
      // Fallback si la clave no existe en el diccionario
      return key;
    }
    return entry[language] || entry["es"]; // Fallback a Español si falta traducción
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

// Hook de fácil inyección en componentes
export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage debe usarse dentro de un LanguageProvider");
  }
  return context;
}
