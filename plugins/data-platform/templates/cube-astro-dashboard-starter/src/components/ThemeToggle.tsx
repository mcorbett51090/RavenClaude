"use client";

import { useEffect, useState } from "react";
import { cn } from "./ui/cn";

const STORAGE_KEY = "theme"; // matches the inline init script in DashboardLayout.astro

/**
 * Explicit light/dark override (FORGE dashboard-top1pct P2-18, 2026-09-03) —
 * see the Next.js starter's identical component for the full rationale.
 * `role="switch"` + `aria-checked` so a screen reader announces the current
 * state, matching this starter's existing status-bearing controls.
 */
export function ThemeToggle() {
  const [isDark, setIsDark] = useState<boolean | null>(null);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  function toggle() {
    const next = !document.documentElement.classList.contains("dark");
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem(STORAGE_KEY, next ? "dark" : "light");
    } catch {
      // localStorage can throw in a locked-down embed context — non-fatal,
      // the toggle just won't persist across a reload.
    }
    setIsDark(next);
  }

  if (isDark === null) {
    return <div className="h-6 w-11" aria-hidden="true" />;
  }

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isDark}
      aria-label={isDark ? "Switch to light theme" : "Switch to dark theme"}
      onClick={toggle}
      className={cn(
        "relative h-6 w-11 rounded-full transition-colors",
        isDark ? "bg-tremor-brand-DEFAULT" : "bg-tremor-border-DEFAULT",
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          "absolute top-0.5 h-5 w-5 rounded-full bg-tremor-background-DEFAULT transition-transform",
          isDark ? "translate-x-[1.375rem]" : "translate-x-0.5",
        )}
      />
    </button>
  );
}
