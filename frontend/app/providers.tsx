"use client";

/**
 * Providers wrapper — scaffold pro budoucí app-level contexty
 * (např. auth, toast, realtime events).
 *
 * Theme toggle byl odstraněn — matrix theme je default a jediný.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
