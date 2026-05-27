import { describe, it, expect } from "vitest";
import { translations, LanguageType } from "../translations";

describe("i18n Translations Dictionary Integrity", () => {
  const expectedLanguages: LanguageType[] = ["es", "en", "fr", "de", "be", "ca"];

  it("should have all 6 supported languages in every translation key", () => {
    const keys = Object.keys(translations);
    
    // Assert there are translation keys loaded
    expect(keys.length).toBeGreaterThan(0);

    for (const key of keys) {
      const transObj = translations[key];
      
      // Every translation must be an object
      expect(typeof transObj).toBe("object");
      expect(transObj).not.toBeNull();

      // Every translation key must have exactly the 6 languages
      for (const lang of expectedLanguages) {
        expect(transObj).toHaveProperty(lang);
        expect(typeof transObj[lang]).toBe("string");
        expect(transObj[lang].trim().length).toBeGreaterThan(0);
      }
    }
  });

  describe("Catalan i18n Vocabulary (Silo -> Sitge / Sitges Plural)", () => {
    it("should map navSilos correctly to 'MP & Sitges'", () => {
      expect(translations.navSilos.ca).toBe("MP & Sitges");
    });

    it("should map titleSilos correctly to 'Planificador de Sitges i Matèries Primeres Pesades'", () => {
      expect(translations.titleSilos.ca).toBe("Planificador de Sitges i Matèries Primeres Pesades");
    });

    it("should map siloCritical correctly to 'Sitge Crític (Farina)'", () => {
      expect(translations.siloCritical.ca).toBe("Sitge Crític (Farina)");
    });

    it("should map siloSubtext correctly to contain 'Sitge #1'", () => {
      expect(translations.siloSubtext.ca).toContain("Sitge #1");
    });

    it("should map siloAlertTitle correctly to 'Sitge de Farina #1 en Decaïment'", () => {
      expect(translations.siloAlertTitle.ca).toBe("Sitge de Farina #1 en Decaïment");
    });

    it("should map commDiagnosticFail correctly to contain 'Sitge de Farina #1'", () => {
      expect(translations.commDiagnosticFail.ca).toContain("Sitge de Farina #1");
    });
  });

  describe("Global Operator Button Translation ('Registrar Usuari')", () => {
    it("should map btnRegisterUser to 'Registrar Usuari' globally across all 6 languages", () => {
      for (const lang of expectedLanguages) {
        expect(translations.btnRegisterUser[lang]).toBe("Registrar Usuari");
      }
    });
  });

  describe("Catalan Login Alerts", () => {
    it("should correctly translate loginErrorEmpty starting with 'Si us plau'", () => {
      expect(translations.loginErrorEmpty.ca).toBe("Si us plau, introdueix el teu usuari i contrasenya.");
      expect(translations.loginErrorEmpty.ca.startsWith("Si us plau")).toBe(true);
    });
  });
});
