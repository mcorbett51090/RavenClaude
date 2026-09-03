"use client";

import { CubeProvider } from "@cubejs-client/react";
import { Grid, Col, Title, Subtitle } from "@tremor/react";
import { getCubeClient } from "@/lib/cube-client";
import { KpiCard } from "./KpiCard";
import { RevenueChart } from "./RevenueChart";

export interface DashboardIslandProps {
  tenantLabel: string;
}

/**
 * The mountable island — hydrated once on the page via `client:load` (or
 * `client:visible` if it's below the fold on a longer marketing page; that
 * trades a later data fetch for not paying the Cube/Tremor/Recharts JS cost
 * on every visitor who never scrolls to it). CubeProvider lives at this
 * level, not per-widget.
 *
 * `tenantLabel` is passed in from the Astro page, which itself resolved it
 * server-side in frontmatter — see src/pages/index.astro. Note this differs
 * from tenant SCOPE (which the JWT/access_policy enforce) — this prop is
 * display-only text, never used for query scoping.
 */
export function DashboardIsland({ tenantLabel }: DashboardIslandProps) {
  const cubeApi = getCubeClient();

  return (
    <CubeProvider cubeApi={cubeApi}>
      <div className="p-6">
        <Title>Dashboard</Title>
        <Subtitle>{tenantLabel}</Subtitle>

        <Grid numItemsMd={3} className="mt-6 gap-4">
          <Col numColSpanMd={1}>
            <KpiCard title="Total revenue" measure="orders.total_revenue" />
          </Col>
          <Col numColSpanMd={1}>
            <KpiCard title="Orders" measure="orders.count" />
          </Col>
          <Col numColSpanMd={1}>
            <KpiCard title="Unique customers" measure="orders.unique_customers" />
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
  );
}
