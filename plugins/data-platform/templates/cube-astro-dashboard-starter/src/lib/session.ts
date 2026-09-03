// ---------------------------------------------------------------------------
// SEAM: resolve the authenticated tenant + user from the current request.
// Identical contract to the Next.js starter's lib/session.ts — see that
// file's header for the full rationale (this is copied, not reinvented, so
// the two starters stay behaviorally consistent).
//
// THE ONE RULE THAT MATTERS: tenantId must come from a server-verified
// session/token, NEVER from a client-supplied header, query param, or
// request body.
// ---------------------------------------------------------------------------

export interface Session {
  userId: string;
  tenantId: string;
}

/**
 * Placeholder implementation — throws so a misconfigured deployment fails
 * loudly rather than silently serving an unscoped dashboard. Replace with a
 * real session lookup (reading Astro's `context.cookies`/`context.request`
 * from the calling API route) before deploying.
 */
export async function getSession(): Promise<Session> {
  throw new Error(
    "src/lib/session.ts is a documented seam, not an implementation. " +
      "Wire getSession() to your host app's real authentication before deploying.",
  );
}
