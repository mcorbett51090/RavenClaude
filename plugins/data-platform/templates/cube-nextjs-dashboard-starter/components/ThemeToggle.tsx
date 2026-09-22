"use client";

import { useEffect, useState } from "react";
import { cn } from "./ui/cn";

const STORAGE_KEY = "theme"; // matches the inline init script in app/layout.tsx

/**
 * Explicit light/dark override (FORGE dashboard-top1pct P2-18, 2026-09-03) —
 * system preference is the default (see app/layout.tsx's inline init
 * script), this is the "let the user override" half web-design's
 * design-tokens-scaffolding skill calls for. `role="switch"` + `aria-checked`
 * (not a plain button + icon swap) so a screen reader announces the current
 * state, not just "button" — the same discipline every other status-bearing
 * control in this starter already follows (FreshnessBadge's role="status",
 * KpiCard's error role="alert").
 */
export function ThemeToggle() {
  // Starts `null` (unknown) rather than assuming light — the inline init
  // script in layout.tsx already set the real class on <html> before this
  // component ever mounts; reading it here on mount avoids a mismatch
  // between what's ACTUALLY applied and what this toggle displays.
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
      // localStorage can throw in a locked-down embed context (private
      // browsing, a sandboxed iframe) — the toggle still works for this
      // page load, it just won't persist across a reload. Not fatal.
    }
    setIsDark(next);
  }

  if (isDark === null) {
    // Avoid rendering a guessed state before the real one is known —
    // a fixed-size placeholder keeps layout stable (no shift once the
    // real toggle mounts).
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
