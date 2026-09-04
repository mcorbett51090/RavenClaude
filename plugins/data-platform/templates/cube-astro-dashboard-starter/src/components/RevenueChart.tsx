"use client";

import { Card, Title, Text } from "@tremor/react";
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
}

/**
 * Copied unchanged from ../../cube-nextjs-dashboard-starter/components/RevenueChart.tsx
 * — plain React (recharts + Tremor card chrome), no Next.js dependency.
 */
export function RevenueChart({
  title,
  measure,
  timeDimension,
  granularity = "day",
}: RevenueChartProps) {
  const cubeApi = getCubeClient();
  const { resultSet, isLoading, error } = useCubeQuery(
    {
      measures: [measure],
      timeDimensions: [{ dimension: timeDimension, granularity }],
      order: { [timeDimension]: "asc" },
    },
    { cubeApi },
  );

  if (error) {
    return (
      <Card>
        <Text color="rose">Query failed: {error.message}</Text>
      </Card>
    );
  }

  const data = (resultSet?.chartPivot() ?? []).map((row) => ({
    x: row.x,
    value: Number(row[measure] ?? 0),
  }));

  return (
    <Card>
      <Title>{title}</Title>
      <div style={{ width: "100%", height: 280, marginTop: 16 }}>
        {isLoading ? (
          <Text>Loading…</Text>
        ) : (
          <ResponsiveContainer>
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="x" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="#bfdbfe" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
      <Text className="mt-1 text-xs text-tremor-content-subtle">source: {measure}</Text>
    </Card>
  );
}
