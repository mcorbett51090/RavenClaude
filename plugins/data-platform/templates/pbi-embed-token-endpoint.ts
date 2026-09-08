// ---------------------------------------------------------------------------
// Power BI Embedded — host-backend embed-token endpoint (Node/TS module)
// ---------------------------------------------------------------------------
// SECURITY (revised after mandatory security review): the caller supplies
// only {workspaceId, reportId, datasetId}. EffectiveIdentity (username +
// roles) is resolved by getEffectiveIdentityForSession(), a seam analogous
// to the Cube starter's lib/session.ts — it must be wired to the host app's
// real session lookup. This function fails closed by throwing until wired,
// and again if the resolved roles array is empty (an identity with no DAX
// role applies no row filter — that failure mode looks like a config quirk,
// not an attack, which is exactly why it must be refused rather than
// silently permitted).
//
// ENVIRONMENT (separate from the host app's own JWT-signing key in
// jwt-issuer.ts):
//   PBI_TENANT_ID     — Azure AD tenant
//   PBI_CLIENT_ID     — service principal app ID
//   PBI_CLIENT_SECRET — service principal secret
//
// Least privilege: the service principal should hold ONLY
// Workspace.Contributor on the target workspace — see power-bi-engineer for
// provisioning specifics.
// ---------------------------------------------------------------------------

import { ConfidentialClientApplication } from "@azure/msal-node";

export interface EffectiveIdentity {
  username: string;
  roles: string[];
  datasets: string[];
}

export interface GenerateEmbedTokenInput {
  workspaceId: string;
  reportId: string;
  datasetId: string;
}

export interface EmbedTokenResult {
  embedToken: string;
  embedUrl: string;
}

const EMBED_TOKEN_LIFETIME_MINUTES = 10; // short-lived per data-platform CLAUDE.md §3 #4

function getMsalClient(): ConfidentialClientApplication {
  if (!process.env.PBI_CLIENT_ID || !process.env.PBI_CLIENT_SECRET || !process.env.PBI_TENANT_ID) {
    throw new Error(
      "PBI_TENANT_ID / PBI_CLIENT_ID / PBI_CLIENT_SECRET must be set. Refusing to acquire a token.",
    );
  }
  return new ConfidentialClientApplication({
    auth: {
      clientId: process.env.PBI_CLIENT_ID,
      clientSecret: process.env.PBI_CLIENT_SECRET,
      authority: `https://login.microsoftonline.com/${process.env.PBI_TENANT_ID}`,
    },
  });
}

/**
 * SEAM: resolve the caller's DAX EffectiveIdentity server-side. A real
 * engagement wires this to the host app's session (tenantId -> DAX
 * USERNAME(), plus whichever DAX role that tenant should see) and, ideally,
 * an allowlist confirming the session's tenant is actually entitled to
 * `workspaceId`/`reportId`. Placeholder throws so a caller can't silently
 * ship this unwired.
 */
export async function getEffectiveIdentityForSession(_input: GenerateEmbedTokenInput): Promise<{
  username: string;
  roles: string[];
}> {
  throw new Error(
    "getEffectiveIdentityForSession() is a documented seam, not an implementation. " +
      "Wire it to your host app's real session + tenant-to-DAX-role mapping before deploying.",
  );
}

/**
 * Generates a short-lived Power BI embed token. Call this from a server-side
 * route that has already authenticated the caller — the function itself
 * resolves the DAX identity from the session (via getEffectiveIdentityForSession),
 * never from caller-supplied input, and refuses to issue a token for an
 * identity with zero DAX roles.
 */
export async function generateEmbedToken(
  input: GenerateEmbedTokenInput,
): Promise<EmbedTokenResult> {
  const identity = await getEffectiveIdentityForSession(input);

  if (!identity.roles || identity.roles.length === 0) {
    throw new Error(
      "Refusing to issue an embed token for an identity with no DAX role — " +
        "a roleless EffectiveIdentity applies no row filter.",
    );
  }

  const effectiveIdentity: EffectiveIdentity = {
    username: identity.username,
    roles: identity.roles,
    datasets: [input.datasetId],
  };

  const msalClient = getMsalClient();

  const tokenResponse = await msalClient.acquireTokenByClientCredential({
    scopes: ["https://analysis.windows.net/powerbi/api/.default"],
  });
  if (!tokenResponse) {
    throw new Error("Failed to acquire an AAD token for the Power BI service principal.");
  }

  const embedTokenResponse = await fetch(
    `https://api.powerbi.com/v1.0/myorg/groups/${input.workspaceId}/reports/${input.reportId}/GenerateToken`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${tokenResponse.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        accessLevel: "View",
        identities: [effectiveIdentity],
        lifetimeInMinutes: EMBED_TOKEN_LIFETIME_MINUTES,
      }),
    },
  );

  if (!embedTokenResponse.ok) {
    throw new Error(`Power BI GenerateToken failed: ${embedTokenResponse.status}`);
  }

  const { token, embedUrl } = await embedTokenResponse.json();
  return { embedToken: token, embedUrl };
}
