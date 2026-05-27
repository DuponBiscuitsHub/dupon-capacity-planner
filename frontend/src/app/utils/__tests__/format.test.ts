import { describe, it, expect } from "vitest";
import { formatNumber, formatEuro } from "../format";

describe("Formatting Utilities - Hydration Mismatch Safety", () => {
  
  describe("formatNumber", () => {
    it("should format standard positive integers with thousands separators", () => {
      expect(formatNumber(1250000)).toBe("1.250.000");
      expect(formatNumber(15000)).toBe("15.000");
      expect(formatNumber(999)).toBe("999");
    });

    it("should format numbers with decimal parts correctly using commas", () => {
      expect(formatNumber(1234.56)).toBe("1.234,56");
      expect(formatNumber(0.75)).toBe("0,75");
      expect(formatNumber(1000000.001)).toBe("1.000.000,001");
    });

    it("should handle negative numbers cleanly", () => {
      expect(formatNumber(-450.25)).toBe("-450,25");
      expect(formatNumber(-1250000)).toBe("-1.250.000");
    });

    it("should return '0' for boundary, missing, or invalid values", () => {
      // @ts-expect-error testing runtime robustness
      expect(formatNumber(null)).toBe("0");
      // @ts-expect-error testing runtime robustness
      expect(formatNumber(undefined)).toBe("0");
      expect(formatNumber(NaN)).toBe("0");
      expect(formatNumber(0)).toBe("0");
    });
  });

  describe("formatEuro", () => {
    it("should append the euro symbol with standard space separation", () => {
      expect(formatEuro(15000)).toBe("15.000 €");
      expect(formatEuro(0)).toBe("0 €");
      expect(formatEuro(1250.75)).toBe("1.250,75 €");
      expect(formatEuro(-50)).toBe("-50 €");
    });
  });
});
