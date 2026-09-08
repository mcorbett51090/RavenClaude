// ---------------------------------------------------------------------------
// Locale + timezone resolution (FORGE dashboard-top1pct P2-15, 2026-09-03).
// See best-practices/dashboard-render-in-the-viewer-locale-and-tenant-
// timezone.md and knowledge/dashboard-timezone-decision-2026.md for the
// full "why" — this implements the tenant-configured fork: locale/timezone
// travel on the same server-verified session as tenant_id.
// ---------------------------------------------------------------------------

export interface LocaleContext {
  /** BCP-47 locale tag, e.g. "en-US" or "de-DE". */
  locale: string;
  /** IANA timezone, e.g. "America/New_York". Reaches Cube's query-level
   *  `timezone` field — an unset timezone silently falls into UTC (the
   *  warehouse-UTC fork), not a neutral no-op. */
  timezone: string;
}

export const DEFAULT_LOCALE_CONTEXT: LocaleContext = { locale: "en-US", timezone: "UTC" };

/**
 * Resolves the viewer's locale/timezone from the session's own optional
 * fields (populated from tenant configuration in a real engagement),
 * falling back to the default (warehouse-UTC, en-US) when unset. Kept as a
 * one-line seam rather than inlined at every call site so a future swap to
 * the viewer-browser fork (see the knowledge file) touches one function.
 */
export function resolveLocaleContext(session: {
  locale?: string;
  timezone?: string;
}): LocaleContext {
  return {
    locale: session.locale ?? DEFAULT_LOCALE_CONTEXT.locale,
    timezone: session.timezone ?? DEFAULT_LOCALE_CONTEXT.timezone,
  };
}
