// ---------------------------------------------------------------------------
// Pure staleness logic (FORGE dashboard-top1pct P2-16, 2026-09-03), split
// out of components/FreshnessBadge.tsx so it's testable without rendering
// React or mocking Cube — see test/freshness.test.ts.
// ---------------------------------------------------------------------------

export interface FreshnessState {
  isStale: boolean;
  ageMinutes: number;
  formattedTime: string;
}

/**
 * Given the last-updated timestamp a Cube `max()` measure returned, the
 * dashboard's declared SLA (minutes), and "now" (injected so this is
 * deterministic and testable), returns whether the widget is past its SLA
 * and a locale/timezone-formatted display string.
 */
export function computeFreshnessState(
  lastUpdated: Date,
  slaMinutes: number,
  now: Date,
  locale: string,
  timezone: string,
): FreshnessState {
  const ageMinutes = (now.getTime() - lastUpdated.getTime()) / 60_000;
  const isStale = ageMinutes > slaMinutes;
  const formattedTime = new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: timezone,
  }).format(lastUpdated);
  return { isStale, ageMinutes, formattedTime };
}
