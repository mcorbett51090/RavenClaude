// Executable unit test for the pure staleness logic FreshnessBadge.tsx's
// rendering directly branches on (FORGE dashboard-top1pct P2-16, 2026-09-03).
//
// Tests lib/freshness.ts's computeFreshnessState(), not a full DOM/browser
// render of the component — this sandbox cannot spawn headless Chromium
// (a documented, session-wide limitation; see the Astro starter's own README
// for the fuller writeup). The component's conditional render
// (`isStale ? <stale JSX> : <fresh JSX>`) reads the exact `isStale` boolean
// this function returns, so proving the function's boundary behavior proves
// the branch the component takes — the honest limit is that the actual
// rendered markup (icon + text + WCAG attributes) is asserted by inspection
// of FreshnessBadge.tsx's source, not by a rendered snapshot.
//
// Run: npm test (from this starter's own directory)

import { describe, it, expect } from "vitest";
import { computeFreshnessState } from "../lib/freshness";

const NOW = new Date("2026-09-03T12:00:00.000Z");
const SLA_MINUTES = 12 * 60; // this starter's own declared 12h SLA

describe("computeFreshnessState", () => {
  it("is NOT stale when the data is well within the SLA (positive control)", () => {
    const lastUpdated = new Date("2026-09-03T11:00:00.000Z"); // 1h ago
    const state = computeFreshnessState(lastUpdated, SLA_MINUTES, NOW, "en-US", "UTC");
    expect(state.isStale).toBe(false);
    expect(state.ageMinutes).toBeCloseTo(60, 0);
  });

  it("is stale when seeded fixture data is past the SLA", () => {
    // Seeded fixture: last updated 18 hours ago, SLA is 12 hours.
    const lastUpdated = new Date("2026-09-02T18:00:00.000Z");
    const state = computeFreshnessState(lastUpdated, SLA_MINUTES, NOW, "en-US", "UTC");
    expect(state.isStale).toBe(true);
    expect(state.ageMinutes).toBeCloseTo(18 * 60, 0);
  });

  it("is exactly at the boundary — not yet stale (age === SLA is not > SLA)", () => {
    const lastUpdated = new Date(NOW.getTime() - SLA_MINUTES * 60_000);
    const state = computeFreshnessState(lastUpdated, SLA_MINUTES, NOW, "en-US", "UTC");
    expect(state.isStale).toBe(false);
  });

  it("respects the locale + timezone passed in (P2-15 threading) — the formatted string changes", () => {
    const lastUpdated = new Date("2026-09-03T11:00:00.000Z");
    const enUS = computeFreshnessState(lastUpdated, SLA_MINUTES, NOW, "en-US", "America/New_York");
    const deDE = computeFreshnessState(lastUpdated, SLA_MINUTES, NOW, "de-DE", "Europe/Berlin");
    expect(enUS.formattedTime).not.toBe(deDE.formattedTime);
  });
});
