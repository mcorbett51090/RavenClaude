import { DashboardShell } from "@/components/DashboardShell";
import { getSession } from "@/lib/session";

/**
 * Server component: resolves the authenticated tenant before rendering
 * anything client-side, so an unauthenticated request never reaches a Cube
 * query. getSession() is a documented seam (see lib/session.ts) — wiring it
 * to real auth is the first thing a real engagement should do with this
 * scaffold.
 */
export default async function DashboardPage() {
  const session = await getSession();

  return <DashboardShell tenantLabel={`Tenant: ${session.tenantId}`} />;
}
