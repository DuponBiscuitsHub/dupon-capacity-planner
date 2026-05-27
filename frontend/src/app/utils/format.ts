/**
 * Consistent formatting utilities to prevent Next.js hydration mismatch errors (SSR vs Client).
 */

/**
 * Formats a number with dots (.) as thousand separators and commas (,) as decimal separators.
 * This guarantees identical string rendering on both server and client regardless of system locale.
 * 
 * Example: 1250000 -> "1.250.000"
 * 
 * @param num Number to format
 * @returns Formatted string
 */
export function formatNumber(num: number): string {
  if (num === null || num === undefined || isNaN(num)) return "0";
  
  // Split integer and decimal parts
  const parts = num.toString().split(".");
  
  // Format integer part with dots for thousand separators
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  
  // Return joined parts with comma
  return parts.join(",");
}

/**
 * Formats a number as Euro currency consistently.
 * 
 * Example: 15000 -> "15.000 €"
 * 
 * @param num Amount to format
 * @returns Formatted Euro currency string
 */
export function formatEuro(num: number): string {
  return `${formatNumber(num)} €`;
}
