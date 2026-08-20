import { describe, it, expect } from "vitest";
import { translations, LanguageType } from "../translations";

describe("i18n Translations Dictionary Integrity", () => {
  const expectedLanguages: LanguageType[] = ["es", "ca", "en"];
  const allKeys = Object.keys(translations);

  it("should have translation keys loaded", () => {
    expect(allKeys.length).toBeGreaterThan(0);
  });

  it("should have all 3 supported languages in every translation key", () => {
    for (const key of allKeys) {
      const transObj = translations[key];
      expect(typeof transObj).toBe("object");
      expect(transObj).not.toBeNull();

      for (const lang of expectedLanguages) {
        expect(transObj, `key "${key}" missing language "${lang}"`).toHaveProperty(lang);
        expect(typeof transObj[lang]).toBe("string");
        expect(transObj[lang].trim().length, `key "${key}" has empty string for "${lang}"`).toBeGreaterThan(0);
      }
    }
  });

  it("should not have unexpected languages beyond es, ca, en", () => {
    for (const key of allKeys) {
      const langs = Object.keys(translations[key]);
      for (const lang of langs) {
        expect(expectedLanguages).toContain(lang);
      }
    }
  });

  describe("Catalan i18n — Silo vocabulary", () => {
    it("should translate navSilos to 'Sitges & Lliuraments'", () => {
      expect(translations.navSilos.ca).toBe("Sitges & Lliuraments");
    });

    it("should translate titleSilos with 'Sitges'", () => {
      expect(translations.titleSilos.ca).toContain("Sitges");
    });
  });

  describe("Core navigation keys exist", () => {
    const navKeys = ["navDashboard", "navSilos", "navConfig", "navLogout"];

    it.each(navKeys)("should have key '%s' with all 3 languages", (key) => {
      expect(translations).toHaveProperty(key);
      for (const lang of expectedLanguages) {
        expect(translations[key]).toHaveProperty(lang);
      }
    });
  });

  describe("Core config keys exist", () => {
    const configKeys = [
      "configLines", "configSilos", "configUsers",
      "configSave", "configCancel", "configEdit",
    ];

    it.each(configKeys)("should have key '%s' with all 3 languages", (key) => {
      expect(translations).toHaveProperty(key);
      for (const lang of expectedLanguages) {
        expect(translations[key]).toHaveProperty(lang);
      }
    });
  });
});
