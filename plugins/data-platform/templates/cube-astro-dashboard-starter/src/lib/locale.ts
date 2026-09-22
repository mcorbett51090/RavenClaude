// ---------------------------------------------------------------------------
// Locale + timezone resolution — Astro-side twin of the Next.js starter's
// lib/locale.ts (FORGE dashboard-top1pct P2-15, 2026-09-03). See
// best-practices/dashboard-render-in-the-viewer-locale-and-tenant-
// timezone.md and knowledge/dashboard-timezone-decision-2026.md.
// ---------------------------------------------------------------------------

export interface LocaleContext {
  /** BCP-47 locale tag, e.g. "en-US" or "de-DE". */
  locale: string;
  /** IANA timezone, e.g. "America/New_York". Reaches Cube's query-level
   *  `timezone` field — an unset timezone silently falls into UTC. */
  timezone: string;
}

export const DEFAULT_LOCALE_CONTEXT: LocaleContext = { locale: "en-US", timezone: "UTC" };

export function resolveLocaleContext(session: {
  locale?: string;
  timezone?: string;
}): LocaleContext {
  return {
    locale: session.locale ?? DEFAULT_LOCALE_CONTEXT.locale,
    timezone: session.timezone ?? DEFAULT_LOCALE_CONTEXT.timezone,
  };
}
