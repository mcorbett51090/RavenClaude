"use client";

import { Card, Metric, Text, Flex, BadgeDelta } from "./ui";
import { useCubeQuery } from "@cubejs-client/react";
import { getCubeClient } from "@/lib/cube-client";
import { useLocale } from "./LocaleProvider";

export interface KpiCardProps {
  title: string;
  /** A single Cube measure name, e.g. "orders.total_revenue". */
  measure: string;
  /** Required for provenance — the date-bounded window this KPI reflects (best-practices/dashboard-provenance-on-every-widget.md). */
  timeDimension: string;
  /** Cube relative date range for the current period, e.g. "last 30 days". */
  dateRange?: string;
  /** Cube relative date range for the comparison baseline, e.g. "from 60 days ago to 31 days ago". */
  comparisonDateRange?: string;
  /** Human-readable label for the comparison baseline shown alongside the delta. */
  comparisonLabel?: string;
  formatValue?: (value: number) => string;
}

// Locale is threaded via useLocale() (FORGE dashboard-top1pct P2-15) rather
// than hard-coded — see best-practices/dashboard-render-in-the-viewer-
// locale-and-tenant-timezone.md. formatValue is still overridable per-widget
// when a caller needs a different format than the locale default.
function formatForLocale(locale: string) {
  return (value: number) =>
    new Intl.NumberFormat(locale, { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

/**
 * A single-metric KPI tile. Provenance (best-practices/dashboard-provenance-on-every-widget.md,
 * an ABSOLUTE rule) requires source query + date range + comparison baseline on every widget
 * making a comparison/trend/KPI claim — this component surfaces all three, not just the
 * measure name (a prior version claimed the rule satisfied while carrying no timeDimensions
 * and no baseline label; fixed in FORGE dashboard-top1pct P1-8, 2026-09-03). Two independent
 * Cube queries run the current window and the comparison window — simpler and more legible
 * for a starter than Cube's multi-query compareDateRange API, at the cost of a second request.
 */
export function KpiCard({
  title,
  measure,
  timeDimension,
  dateRange = "last 30 days",
  comparisonDateRange = "from 60 days ago to 31 days ago",
  comparisonLabel = "vs prior 30 days",
  formatValue,
}: KpiCardProps) {
  // Tagged per query, not per component (FORGE dashboard-top1pct P2-17,
  // 2026-09-03) — see knowledge/dashboard-query-cost-instrumentation.md.
  // "current" and "comparison" are two DIFFERENT queries a viewer's session
  // issues for the same KPI tile; a shared tag would collapse them into one
  // line in Cube's Query History, hiding that a KpiCard costs two queries.
  const { locale, timezone } = useLocale();
  const format = formatValue ?? formatForLocale(locale);
  const current = useCubeQuery(
    {
      measures: [measure],
      timeDimensions: [{ dimension: timeDimension, dateRange }],
      timezone,
    },
    { cubeApi: getCubeClient(`kpi-card.${measure}.current`) },
  );
  const comparison = useCubeQuery(
    {
      measures: [measure],
      timeDimensions: [{ dimension: timeDimension, dateRange: comparisonDateRange }],
      timezone,
    },
    { cubeApi: getCubeClient(`kpi-card.${measure}.comparison`) },
  );

  const isLoading = current.isLoading || comparison.isLoading;
  const error = current.error ?? comparison.error;

  if (error) {
    return (
      <Card role="alert">
        {/* Icon + text, not color alone (WCAG 2.2 AA — best-practices/dashboard-meet-the-accessibility-floor.md) */}
        <Text color="rose">
          <span aria-hidden="true">⚠ </span>Query failed: {error.message}
        </Text>
      </Card>
    );
  }

  const currentRow = current.resultSet?.tablePivot()[0];
  const value = currentRow ? Number(currentRow[measure]) : undefined;
  const comparisonRow = comparison.resultSet?.tablePivot()[0];
  const comparisonValue = comparisonRow ? Number(comparisonRow[measure]) : undefined;
  const deltaPct =
    value !== undefined && comparisonValue !== undefined && comparisonValue !== 0
      ? ((value - comparisonValue) / comparisonValue) * 100
      : undefined;

  // Distinct zero-data state, separate from "still loading" (found in this
  // plugin's own dashboard-architecture-audit dogfood pass, FORGE
  // dashboard-top1pct P1-10, 2026-09-03): a tenant with genuinely zero
  // orders previously saw the same "—" placeholder as a still-loading
  // widget, with no way to tell the two apart — a broken-looking blank
  // rather than an explained empty state.
  const isZero = !isLoading && value !== undefined && value === 0;

  return (
    <Card>
      {/* aria-live announces the value once it resolves; role="status" makes the whole
          region a polite live region without needing a separate visually-hidden node. */}
      <div role="status" aria-live="polite" aria-busy={isLoading}>
        <Flex justifyContent="between" alignItems="start">
          <div>
            <Text>{title}</Text>
            <Metric>{isLoading || value === undefined ? "—" : format(value)}</Metric>
          </div>
          {deltaPct !== undefined && (
            <BadgeDelta deltaType={deltaPct >= 0 ? "increase" : "decrease"}>
              {Math.abs(deltaPct).toFixed(1)}%
            </BadgeDelta>
          )}
        </Flex>
        {isZero && (
          <Text className="mt-1 text-xs text-tremor-content-subtle">
            No data yet for this period — check back once activity starts, or widen the date range.
          </Text>
        )}
      </div>
      {/* Provenance footer: source measure + the exact date ranges both numbers cover +
          the named comparison baseline — all three required by the absolute rule above.
          The timezone is named too (P2-15) — a bare date range is ambiguous once more
          than one timezone is in play; see best-practices/dashboard-render-in-the-viewer-
          locale-and-tenant-timezone.md. */}
      <Text data-provenance-footer className="mt-2 text-xs text-tremor-content-subtle">
        source: {measure} · {dateRange} ({timezone})
        {deltaPct !== undefined ? ` · ${comparisonLabel}` : ""}
      </Text>
    </Card>
  );
}
