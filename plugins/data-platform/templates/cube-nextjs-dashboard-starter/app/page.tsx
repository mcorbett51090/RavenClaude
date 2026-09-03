import { DashboardShell } from "@/components/DashboardShell";
import { getSession } from "@/lib/session";

// This page resolves the caller's authenticated session on every request —
// it can never be statically prerendered (Next.js's default `output: export`-
// style build-time prerender pass would call getSession() with no request in
// flight, which the seam correctly rejects). `force-dynamic` is the correct
// fix, not a workaround: a session-gated dashboard route is dynamic by
// definition, in a real host app too.
export const dynamic = "force-dynamic";

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
