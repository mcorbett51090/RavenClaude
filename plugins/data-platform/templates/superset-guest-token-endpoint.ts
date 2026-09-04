// ---------------------------------------------------------------------------
// Superset guest-token endpoint (host-backend Node/TS module)
// ---------------------------------------------------------------------------
// Companion to superset-embed-iframe.tsx. The client NEVER calls Superset's
// /api/v1/security/guest_token/ directly (that was a HIGH-severity finding
// from this plugin's mandatory security review — a client-controlled
// tenantId reaching the RLS clause is an authorization bypass regardless of
// what a docstring says the caller "should" pass). This module is the only
// thing that talks to Superset's guest-token endpoint, and it resolves
// tenantId from a SERVER-VERIFIED session, never from caller input.
//
// Wire this into your framework's own server-route convention (Next.js API
// route, Express handler, etc.) — see the exported `handleGuestTokenRequest`
// for the shape.
// ---------------------------------------------------------------------------

import { issueEmbedToken } from "./jwt-issuer";

// tenantId format guard — defense in depth even though this module is the
// only caller and already resolves tenantId server-side. A tenantId that
// doesn't match this shape is refused rather than interpolated into the RLS
// clause string.
const TENANT_ID_PATTERN = /^[A-Za-z0-9_-]{1,64}$/;

export interface SessionLookup {
  userId: string;
  tenantId: string;
}

export interface GuestTokenRequestInput {
  dashboardId: string;
  supersetDomain: string;
  /** Resolves the caller's session server-side. Never trust a client-supplied tenantId/userId. */
  getSession: () => Promise<SessionLookup>;
}

export interface GuestTokenResult {
  guestToken: string;
}

export async function handleGuestTokenRequest(
  input: GuestTokenRequestInput,
): Promise<GuestTokenResult> {
  const { userId, tenantId } = await input.getSession();

  if (!TENANT_ID_PATTERN.test(tenantId)) {
    throw new Error(
      `Refusing to build an RLS clause: tenantId "${tenantId}" doesn't match the expected shape.`,
    );
  }

  // SEAM 1: host JWT, minted server-side via the existing jwt-issuer.ts pattern.
  const hostJwt = await issueEmbedToken({ userId, tenantId, audience: "superset" });

  // SEAM 2: Superset guest-token exchange — server-to-server only.
  const res = await fetch(
    `${input.supersetDomain.replace(/\/$/, "")}/api/v1/security/guest_token/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${hostJwt}` },
      body: JSON.stringify({
        resources: [{ type: "dashboard", id: input.dashboardId }],
        // tenantId is validated above; still parameterized-in-spirit (a fixed
        // pattern, not free-form interpolation) rather than trusted verbatim.
        rls: [{ clause: `tenant_id = '${tenantId}'` }],
        user: { username: userId, first_name: "", last_name: "" },
      }),
    },
  );
  if (!res.ok) {
    throw new Error(`Superset guest_token request failed: ${res.status}`);
  }

  const { token } = await res.json();
  return { guestToken: token };
}
