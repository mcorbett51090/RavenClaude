"use client";

import { CubeProvider } from "@cubejs-client/react";
import { Grid, Col, Title, Subtitle, Flex } from "./ui";
import { getCubeClient } from "@/lib/cube-client";
import { KpiCard } from "./KpiCard";
import { RevenueChart } from "./RevenueChart";
import { ExportBar } from "./ExportBar";
import { LocaleProvider } from "./LocaleProvider";
import { FreshnessBadge } from "./FreshnessBadge";
import { ThemeToggle } from "./ThemeToggle";

// This starter's own declared SLA (best-practices/dashboard-set-data-freshness-slas.md:
// "declare a freshness SLA per source/dashboard" — there is no universal default). Matches
// the 12h warn_after threshold that best-practice file's own dbt source-freshness example uses.
const DASHBOARD_FRESHNESS_SLA_MINUTES = 12 * 60;

export interface DashboardShellProps {
  tenantLabel: string;
  /** Server-resolved locale/timezone (lib/locale.ts) — threaded to every
   *  widget via LocaleProvider so a future audit doesn't find one KPI card
   *  in a different timezone than its neighbor. (P2-15) */
  locale: string;
  timezone: string;
}

/**
 * The dashboard shell — wraps children in CubeProvider (once, at the shell
 * level, not per-widget) and lays out the example widgets against
 * ../cube-schema-starter.yml's `orders` cube. Swap the measure/dimension
 * strings for your engagement's real cube once it's scaffolded via the
 * cube-schema-scaffolding skill.
 */
export function DashboardShell({ tenantLabel, locale, timezone }: DashboardShellProps) {
  const cubeApi = getCubeClient();

  return (
    <LocaleProvider locale={locale} timezone={timezone}>
      <CubeProvider cubeApi={cubeApi}>
        <div className="p-6">
          <Flex justifyContent="between" alignItems="start">
            <div>
              <Title>Dashboard</Title>
              <Subtitle>{tenantLabel}</Subtitle>
            </div>
            {/* Explicit light/dark override (FORGE dashboard-top1pct P2-18) —
                system preference is the default, set before first paint by
                the inline script in app/layout.tsx. */}
            <ThemeToggle />
          </Flex>

          <div className="mt-2">
            <FreshnessBadge
              measure="orders.last_updated_at"
              slaMinutes={DASHBOARD_FRESHNESS_SLA_MINUTES}
            />
          </div>

          <div className="mt-4">
            <ExportBar />
          </div>

          <Grid numItemsMd={3} className="mt-6 gap-4">
            <Col numColSpanMd={1}>
              <KpiCard
                title="Total revenue"
                measure="orders.total_revenue"
                timeDimension="orders.order_date"
              />
            </Col>
            <Col numColSpanMd={1}>
              <KpiCard title="Orders" measure="orders.count" timeDimension="orders.order_date" />
            </Col>
            <Col numColSpanMd={1}>
              <KpiCard
                title="Unique customers"
                measure="orders.unique_customers"
                timeDimension="orders.order_date"
              />
            </Col>
          </Grid>

          <div className="mt-4">
            <RevenueChart
              title="Revenue over time"
              measure="orders.total_revenue"
              timeDimension="orders.order_date"
            />
          </div>
        </div>
      </CubeProvider>
    </LocaleProvider>
  );
}
