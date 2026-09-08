"use client";

import { Card, Metric, Text, Flex, BadgeDelta } from "@tremor/react";
import { useCubeQuery } from "@cubejs-client/react";
import { getCubeClient } from "@/lib/cube-client";

export interface KpiCardProps {
  title: string;
  /** A single Cube measure name, e.g. "orders.total_revenue". */
  measure: string;
  /** Optional comparison measure for a period-over-period delta badge. */
  comparisonMeasure?: string;
  formatValue?: (value: number) => string;
}

const defaultFormat = (value: number) =>
  new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);

/**
 * A single-metric KPI tile. Per data-platform CLAUDE.md §3 #7 ("provenance on
 * every claim"), the measure name itself is shown as a `Text` sub-line so the
 * viewer can trace the number back to its Cube source query.
 *
 * Copied unchanged from ../../cube-nextjs-dashboard-starter/components/KpiCard.tsx
 * — this is plain React with no Next.js dependency, so it ports as an Astro
 * island with no modification.
 */
export function KpiCard({
  title,
  measure,
  comparisonMeasure,
  formatValue = defaultFormat,
}: KpiCardProps) {
  const cubeApi = getCubeClient();
  const measures = comparisonMeasure ? [measure, comparisonMeasure] : [measure];
  const { resultSet, isLoading, error } = useCubeQuery({ measures }, { cubeApi });

  if (error) {
    return (
      <Card>
        <Text color="rose">Query failed: {error.message}</Text>
      </Card>
    );
  }

  const row = resultSet?.tablePivot()[0];
  const value = row ? Number(row[measure]) : undefined;
  const comparison = comparisonMeasure && row ? Number(row[comparisonMeasure]) : undefined;
  const deltaPct =
    value !== undefined && comparison !== undefined && comparison !== 0
      ? ((value - comparison) / comparison) * 100
      : undefined;

  return (
    <Card>
      <Flex justifyContent="between" alignItems="start">
        <div>
          <Text>{title}</Text>
          <Metric>{isLoading || value === undefined ? "—" : formatValue(value)}</Metric>
        </div>
        {deltaPct !== undefined && (
          <BadgeDelta deltaType={deltaPct >= 0 ? "increase" : "decrease"}>
            {Math.abs(deltaPct).toFixed(1)}%
          </BadgeDelta>
        )}
      </Flex>
      <Text className="mt-2 text-xs text-tremor-content-subtle">source: {measure}</Text>
    </Card>
  );
}
