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

export interface RevenueChartProps {
  title: string;
  measure: string;
  timeDimension: string;
  granularity?: "day" | "week" | "month";
  /** Cube relative date range this chart covers — required for provenance (see below). */
  dateRange?: string;
}

/**
 * Deliberately uses recharts directly (not a Tremor-style chart wrapper) —
 * the local `ui/` primitives (see KpiCard.tsx) own the KPI/card chrome,
 * recharts owns time-series/area charts where finer control is useful.
 * Copied from the Next.js starter's RevenueChart.tsx (plain React, no
 * Next.js dependency) — see this starter's README "What's reused vs. new".
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
  const cubeApi = getCubeClient();
  const { resultSet, isLoading, error } = useCubeQuery(
    {
      measures: [measure],
      timeDimensions: [{ dimension: timeDimension, granularity, dateRange }],
      order: { [timeDimension]: "asc" },
    },
    { cubeApi },
  );

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
                <XAxis dataKey="x" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="#bfdbfe" />
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
      <Text className="mt-1 text-xs text-tremor-content-subtle">
        source: {measure} · {dateRange}
      </Text>
    </Card>
  );
}
