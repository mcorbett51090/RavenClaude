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
//
// How it authenticates to Superset (review E-8): Superset's guest_token
// endpoint wants a caller "authenticated with the can_grant_guest_token
// permission" (superset-embedded-sdk README) — a Superset-issued access
// token, not a JWT signed with this host's own JWT_SIGNING_KEY. So this
// module logs in as a Superset service account first.
//
// ENVIRONMENT (server only, never in a client bundle):
//   SUPERSET_SERVICE_USERNAME / SUPERSET_SERVICE_PASSWORD — a Superset
//     database-auth user whose role holds can_grant_guest_token.
// ---------------------------------------------------------------------------

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

// SEAM 1 [unverified - not run against a live Superset]: service-account
// login. POST /api/v1/security/login returns { access_token }.
// ⛔ If your Superset has WTF_CSRF_ENABLED and guest_token is not in
// WTF_CSRF_EXEMPT_LIST, the guest_token POST also needs a CSRF token: GET
// /api/v1/security/csrf_token/ with this bearer, then send its `result` as
// the X-CSRFToken header together with the session cookie that response set.
async function loginServiceAccount(supersetBase: string): Promise<string> {
  const username = process.env.SUPERSET_SERVICE_USERNAME;
  const password = process.env.SUPERSET_SERVICE_PASSWORD;
  if (!username || !password) {
    throw new Error("SUPERSET_SERVICE_USERNAME and SUPERSET_SERVICE_PASSWORD must be set.");
  }
  const res = await fetch(`${supersetBase}/api/v1/security/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, provider: "db", refresh: false }),
  });
  if (!res.ok) {
    throw new Error(`Superset service-account login failed: ${res.status}`);
  }
  const { access_token: accessToken } = (await res.json()) as { access_token?: unknown };
  if (typeof accessToken !== "string" || accessToken === "") {
    throw new Error("Superset login returned no access_token.");
  }
  return accessToken;
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

  const accessToken = await loginServiceAccount(input.supersetDomain.replace(/\/$/, ""));

  // SEAM 2: Superset guest-token exchange — server-to-server only, with the
  // service account's Superset access token.
  const res = await fetch(
    `${input.supersetDomain.replace(/\/$/, "")}/api/v1/security/guest_token/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
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
