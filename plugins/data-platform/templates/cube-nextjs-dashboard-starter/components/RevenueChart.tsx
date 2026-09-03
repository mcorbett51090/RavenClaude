"use client";

import { Card, Title, Text } from "./ui";
import { useCubeQuery } from "@cubejs-client/react";
import {
  AreaChart,
  ResponsiveContainer,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Area,
} from "recharts";
import { getCubeClient } from "@/lib/cube-client";
import { useLocale } from "./LocaleProvider";

export interface RevenueChartProps {
  title: string;
  measure: string;
  timeDimension: string;
  granularity?: "day" | "week" | "month";
  /** Cube relative date range this chart covers — required for provenance (see below). */
  dateRange?: string;
}

/**
 * Deliberately uses recharts directly (not Tremor's chart wrapper) to honor
 * dashboard-builder's documented stack: "Cube OSS + Next.js + local
 * Tremor-Raw components + Recharts + shadcn/ui" — the local ui/ primitives
 * own the KPI/card chrome (see KpiCard.tsx), recharts owns time-series/area
 * charts where finer control is useful.
 *
 * Provenance (best-practices/dashboard-provenance-on-every-widget.md,
 * ABSOLUTE): source measure + date range are shown in the footer. A chart
 * has no single-number "comparison baseline" the way a KpiCard does — the
 * chart's own X axis IS the comparison across the window, so the rule's
 * intent is satisfied by the bounded, visible date range rather than a
 * separate baseline label.
 *
 * Accessibility (WCAG 2.2 AA, best-practices/dashboard-meet-the-accessibility-floor.md):
 * the chart region carries an aria-label summarizing what it shows (an SVG
 * chart has no accessible text content on its own), a visually-hidden
 * <table> gives screen-reader users the same data Recharts renders visually,
 * loading/error states use role="status"/role="alert" instead of plain text
 * a screen reader has no reason to announce, and the error state pairs an
 * icon with text rather than color alone.
 */
export function RevenueChart({
  title,
  measure,
  timeDimension,
  granularity = "day",
  dateRange = "last 90 days",
}: RevenueChartProps) {
  const { locale, timezone } = useLocale();
  const { resultSet, isLoading, error } = useCubeQuery(
    {
      measures: [measure],
      timeDimensions: [{ dimension: timeDimension, granularity, dateRange }],
      order: { [timeDimension]: "asc" },
      timezone,
    },
    // Tagged per widget instance (FORGE dashboard-top1pct P2-17) — see
    // KpiCard.tsx's identical comment for why this isn't a shared client.
    { cubeApi: getCubeClient(`revenue-chart.${measure}`) },
  );
  // Locale-aware axis tick formatting (P2-15) — Cube's chartPivot() `x`
  // values are date strings; format them in the viewer's locale rather than
  // rendering the raw ISO string every viewer would otherwise see alike.
  const formatTick = (x: string) => {
    const d = new Date(x);
    return Number.isNaN(d.getTime())
      ? x
      : new Intl.DateTimeFormat(locale, {
          month: "short",
          day: "numeric",
          timeZone: timezone,
        }).format(d);
  };

  if (error) {
    return (
      <Card role="alert">
        <Text color="rose">
          <span aria-hidden="true">⚠ </span>Query failed: {error.message}
        </Text>
      </Card>
    );
  }

  const data = (resultSet?.chartPivot() ?? []).map((row) => ({
    x: row.x,
    value: Number(row[measure] ?? 0),
  }));
  const chartLabel = `${title}: ${measure} over ${dateRange}, ${data.length} data points`;

  return (
    <Card>
      <Title>{title}</Title>
      <div style={{ width: "100%", height: 280, marginTop: 16 }} role="img" aria-label={chartLabel}>
        {isLoading ? (
          <div role="status" aria-live="polite">
            <Text>Loading…</Text>
          </div>
        ) : (
          <>
            <ResponsiveContainer>
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="x" tick={{ fontSize: 11 }} tickFormatter={formatTick} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                {/* CSS custom properties, not literal hex (FORGE dashboard-top1pct
                    P2-18) — Recharts' SVG stroke/fill attributes accept a
                    var(...) reference directly in all evergreen browsers, so
                    this chart line re-themes with the same .dark toggle /
                    host-override seam as every Tailwind-class-driven element. */}
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="var(--tremor-brand-DEFAULT)"
                  fill="var(--tremor-brand-muted)"
                />
              </AreaChart>
            </ResponsiveContainer>
            {/* Screen-reader-only data table — the same rows Recharts renders visually,
                for AT users who can't read the SVG. `sr-only` matches Tailwind's default
                utility (border-0 clip-path pattern); no extra CSS needed if this starter's
                globals.css already ships it (Tailwind's own convention). */}
            <table className="sr-only">
              <caption>{chartLabel}</caption>
              <thead>
                <tr>
                  <th scope="col">{timeDimension}</th>
                  <th scope="col">{measure}</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr key={row.x}>
                    <td>{row.x}</td>
                    <td>{row.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
      <Text data-provenance-footer className="mt-1 text-xs text-tremor-content-subtle">
        source: {measure} · {dateRange} ({timezone})
      </Text>
    </Card>
  );
}
