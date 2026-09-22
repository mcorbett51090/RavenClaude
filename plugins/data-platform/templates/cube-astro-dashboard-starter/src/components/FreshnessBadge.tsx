"use client";

import { Text } from "./ui";
import { useCubeQuery } from "@cubejs-client/react";
import { getCubeClient } from "@/lib/cube-client";
import { useLocale } from "./LocaleProvider";
import { computeFreshnessState } from "@/lib/freshness";

export interface FreshnessBadgeProps {
  /** A Cube `max()` measure over a fact table's updated_at column, e.g. "orders.last_updated_at". */
  measure: string;
  /** The declared SLA for this dashboard, in minutes — no universal default; per
   *  best-practices/dashboard-set-data-freshness-slas.md, the SLA is per-source/per-dashboard. */
  slaMinutes: number;
}

/**
 * Identical to the Next.js starter's FreshnessBadge.tsx (plain React, no
 * framework coupling) — implements the dashboard-side degradation contract
 * (FORGE dashboard-top1pct P2-16, 2026-09-03 — see best-practices/
 * dashboard-set-data-freshness-slas.md's "dashboard-side degradation
 * contract" section).
 */
export function FreshnessBadge({ measure, slaMinutes }: FreshnessBadgeProps) {
  const { locale, timezone } = useLocale();
  // Tagged (FORGE dashboard-top1pct P2-17) — see KpiCard.tsx's identical comment.
  const { resultSet, isLoading, error } = useCubeQuery(
    { measures: [measure], timezone },
    { cubeApi: getCubeClient(`freshness-badge.${measure}`) },
  );

  if (error) {
    return (
      <Text role="alert" color="rose" className="text-xs">
        <span aria-hidden="true">⚠ </span>Freshness check failed: {error.message}
      </Text>
    );
  }

  if (isLoading) {
    return (
      <Text role="status" aria-live="polite" className="text-xs text-tremor-content-subtle">
        Checking freshness…
      </Text>
    );
  }

  const raw = resultSet?.tablePivot()[0]?.[measure];
  const lastUpdated = raw ? new Date(String(raw)) : undefined;
  if (!lastUpdated || Number.isNaN(lastUpdated.getTime())) {
    return (
      <Text role="status" className="text-xs text-tremor-content-subtle">
        As-of time unavailable — no rows yet.
      </Text>
    );
  }

  const { isStale, formattedTime } = computeFreshnessState(
    lastUpdated,
    slaMinutes,
    new Date(),
    locale,
    timezone,
  );

  return (
    <Text
      role="status"
      color={isStale ? "rose" : "default"}
      className={isStale ? "text-xs font-medium" : "text-xs text-tremor-content-subtle"}
    >
      {isStale ? (
        <>
          <span aria-hidden="true">⚠ </span>Stale — current as of {formattedTime} ({timezone}),
          exceeds the {slaMinutes >= 60 ? `${Math.round(slaMinutes / 60)}h` : `${slaMinutes}min`}{" "}
          SLA
        </>
      ) : (
        <>
          Current as of {formattedTime} ({timezone})
        </>
      )}
    </Text>
  );
}
