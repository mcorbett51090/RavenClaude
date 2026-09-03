"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { LocaleContext as LocaleContextValue } from "@/lib/locale";

const LocaleReactContext = createContext<LocaleContextValue | null>(null);

export interface LocaleProviderProps extends LocaleContextValue {
  children: ReactNode;
}

/**
 * Threads the server-resolved {locale, timezone} pair to every widget below
 * it via context (FORGE dashboard-top1pct P2-15). Identical to the Next.js
 * starter's LocaleProvider.tsx (plain React, no framework coupling).
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
