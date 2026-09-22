"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { LocaleContext as LocaleContextValue } from "@/lib/locale";

const LocaleReactContext = createContext<LocaleContextValue | null>(null);

export interface LocaleProviderProps extends LocaleContextValue {
  children: ReactNode;
}

/**
 * Threads the server-resolved {locale, timezone} pair to every widget below
 * it via context — every widget reads the SAME pair, so a future audit
 * doesn't find one KPI card in a different timezone than its neighbor.
 * (FORGE dashboard-top1pct P2-15.)
 */
export function LocaleProvider({ locale, timezone, children }: LocaleProviderProps) {
  return (
    <LocaleReactContext.Provider value={{ locale, timezone }}>
      {children}
    </LocaleReactContext.Provider>
  );
}

export function useLocale(): LocaleContextValue {
  const ctx = useContext(LocaleReactContext);
  if (!ctx) {
    throw new Error("useLocale() must be called within a <LocaleProvider>.");
  }
  return ctx;
}
