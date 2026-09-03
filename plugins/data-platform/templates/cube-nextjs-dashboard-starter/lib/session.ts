// ---------------------------------------------------------------------------
// SEAM: resolve the authenticated tenant + user from the current request.
// ---------------------------------------------------------------------------
// This scaffold is deliberately auth-provider-agnostic — a real engagement
// wires this to whatever the host app already uses (NextAuth, Clerk, a
// custom session cookie, an upstream gateway header, etc.).
//
// THE ONE RULE THAT MATTERS: tenantId must come from a server-verified
// session/token, NEVER from a client-supplied header, query param, or
// request body. A dashboard built on a spoofable tenantId has no tenant
// isolation regardless of what the Cube access_policy or RLS policy say
// downstream — see data-platform CLAUDE.md §3 #3 and §4 ("App-code tenant
// filters are never the load-bearing control on a viewer-facing read path").
// ---------------------------------------------------------------------------

export interface Session {
  userId: string;
  tenantId: string;
}

/**
 * Placeholder implementation — throws so a misconfigured deployment fails
 * loudly rather than silently serving an unscoped dashboard. Replace with a
 * real session lookup before deploying.
 */
export async function getSession(): Promise<Session> {
  throw new Error(
    "lib/session.ts is a documented seam, not an implementation. " +
      "Wire getSession() to your host app's real authentication before deploying.",
  );
}
