"use client";

import { CubeProvider } from "@cubejs-client/react";
import { Grid, Col } from "./ui";
import { getCubeClient } from "@/lib/cube-client";
import { KpiCard } from "./KpiCard";
import { RevenueChart } from "./RevenueChart";
import { ExportBar } from "./ExportBar";
import { LocaleProvider } from "./LocaleProvider";
import { FreshnessBadge } from "./FreshnessBadge";

// This starter's own declared SLA — see the Next.js starter's identical
// constant for the full rationale (best-practices/dashboard-set-data-
// freshness-slas.md: "declare a freshness SLA per source/dashboard").
const DASHBOARD_FRESHNESS_SLA_MINUTES = 12 * 60;

export interface DashboardIslandProps {
  /** Server-resolved in index.astro's frontmatter (lib/locale.ts) and passed
   *  as a plain prop — Astro serializes island props for client:load
   *  hydration, so this must stay a plain string. (P2-15) */
  locale: string;
  timezone: string;
}

/**
 * The mountable island — hydrated once on the page via `client:load` (or
 * `client:visible` if it's below the fold on a longer marketing page; that
 * trades a later data fetch for not paying the Cube/Recharts JS cost on
 * every visitor who never scrolls to it). CubeProvider lives at this level,
 * not per-widget.
 *
 * Title/Subtitle deliberately live OUTSIDE this island now, in
 * src/pages/index.astro (found in this plugin's own
 * dashboard-architecture-audit dogfood pass, FORGE dashboard-top1pct P1-10,
 * 2026-09-03): they're static text with no data dependency, and Astro
 * renders a framework component with no client:* directive to static HTML
 * at zero JS cost — keeping them here forfeited exactly the "zero JS unless
 * explicitly marked" value proposition this starter's own README argues
 * for. Only the genuinely data-fetching widgets (the KPI grid, the chart)
 * need to hydrate.
 */
export function DashboardIsland({ locale, timezone }: DashboardIslandProps) {
  const cubeApi = getCubeClient();

  // No outer p-6 wrapper here — src/pages/index.astro owns the page-level
  // padding now that Title/Subtitle render there too; a second p-6 here
  // would double the padding around this island's own content.
  return (
    <LocaleProvider locale={locale} timezone={timezone}>
      <CubeProvider cubeApi={cubeApi}>
        <div className="mb-2">
          <FreshnessBadge
            measure="orders.last_updated_at"
            slaMinutes={DASHBOARD_FRESHNESS_SLA_MINUTES}
          />
        </div>
        <ExportBar />

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
      </CubeProvider>
    </LocaleProvider>
  );
}
