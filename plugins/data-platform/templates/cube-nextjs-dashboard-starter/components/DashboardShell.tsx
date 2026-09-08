"use client";

import { CubeProvider } from "@cubejs-client/react";
import { Grid, Col, Title, Subtitle } from "@tremor/react";
import { getCubeClient } from "@/lib/cube-client";
import { KpiCard } from "./KpiCard";
import { RevenueChart } from "./RevenueChart";

export interface DashboardShellProps {
  tenantLabel: string;
}

/**
 * The dashboard shell — wraps children in CubeProvider (once, at the shell
 * level, not per-widget) and lays out the example widgets against
 * ../cube-schema-starter.yml's `orders` cube. Swap the measure/dimension
 * strings for your engagement's real cube once it's scaffolded via the
 * cube-schema-scaffolding skill.
 */
export function DashboardShell({ tenantLabel }: DashboardShellProps) {
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
