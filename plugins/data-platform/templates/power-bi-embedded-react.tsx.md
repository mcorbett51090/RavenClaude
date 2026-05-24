# Power BI Embedded App-Owns-Data (React component) — seam-marked stub

> **Status:** v0.1.0 conceptual stub. Documents the seams; not compiling code.
> **Promoted to runnable `.tsx` in v0.2.0** after a real Microsoft-stack engagement validates the seams.
>
> **Last reviewed:** 2026-05-21
>
> ⚠ **Coordinate with `power-platform/power-bi-engineer`.** This template owns the embed pattern + integration into a non-Microsoft data stack. The power-platform plugin owns DAX, semantic model, PBIP source control, refresh/gateway issues.
>
> Companion docs:
>   - [`../knowledge/power-bi-embedded-for-consultants.md`](../knowledge/power-bi-embedded-for-consultants.md)
>   - [`../skills/embed-csp-and-iframe-sandboxing/SKILL.md`](../skills/embed-csp-and-iframe-sandboxing/SKILL.md)

## The seams this component owns

1. **MSAL acquisition seam** — host app's backend acquires an Azure AD token via `client_credentials` flow using the service principal
2. **Embed token issuance seam** — host app calls Power BI REST API `/groups/{workspaceId}/reports/{reportId}/GenerateToken` with `EffectiveIdentity` to issue a short-lived embed token
3. **powerbi-client SDK initialization seam** — frontend uses `@powerbi/client` library to render
4. **RLS via EffectiveIdentity seam** — DAX role + username carried in the embed token

## The component skeleton (illustrative)

```tsx
import { models, service, factories } from "powerbi-client";
import { useEffect, useRef } from "react";

interface PowerBIEmbedProps {
  /** Power BI workspace (group) ID */
  workspaceId: string;
  /** Power BI report ID */
  reportId: string;
  /** Power BI dataset ID (for EffectiveIdentity binding) */
  datasetId: string;
  /** Tenant ID from host app's session (used as the DAX USERNAME() value) */
  tenantId: string;
  /** DAX role name to apply (e.g., "Tenant_Viewer_Role") */
  daxRole: string;
  /** Host backend endpoint that returns an embed token */
  embedTokenEndpoint: string;
  height?: number;
}

export function PowerBIEmbed({
  workspaceId,
  reportId,
  datasetId,
  tenantId,
  daxRole,
  embedTokenEndpoint,
  height = 800,
}: PowerBIEmbedProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // SEAM 1 + 2: Acquire embed token from host backend
    // The backend handles MSAL (service principal credentials) and calls
    // the Power BI REST API. Frontend never sees the AAD token.
    fetch(embedTokenEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        workspaceId,
        reportId,
        datasetId,
        // SEAM 4: EffectiveIdentity for RLS — backend constructs this
        // from the tenantId in the authenticated session
        effectiveIdentity: {
          username: tenantId,
          roles: [daxRole],
          datasets: [datasetId],
        },
      }),
    })
      .then((r) => r.json())
      .then(({ embedToken, embedUrl }) => {
        // SEAM 3: powerbi-client SDK initialization
        const config: models.IReportEmbedConfiguration = {
          type: "report",
          id: reportId,
          embedUrl,
          accessToken: embedToken,
          tokenType: models.TokenType.Embed,
          settings: {
            panes: {
              filters: { visible: false },
              pageNavigation: { visible: true },
            },
            background: models.BackgroundType.Transparent,
          },
        };

        const powerbi = new service.Service(
          factories.hpmFactory,
          factories.wpmpFactory,
          factories.routerFactory
        );

        powerbi.embed(containerRef.current!, config);
      });

    // Cleanup on unmount
    return () => {
      const powerbi = new service.Service(
        factories.hpmFactory,
        factories.wpmpFactory,
        factories.routerFactory
      );
      if (containerRef.current) powerbi.reset(containerRef.current);
    };
  }, [workspaceId, reportId, datasetId, tenantId, daxRole, embedTokenEndpoint]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: `${height}px` }}
      data-testid="powerbi-embed"
    />
  );
}
```

## The host-backend endpoint (separate Node/TS module)

```typescript
// pbi-embed-token-endpoint.ts (host backend, not committed in this template)
//
// Requires:
//   PBI_TENANT_ID — Azure AD tenant
//   PBI_CLIENT_ID — service principal app ID
//   PBI_CLIENT_SECRET — service principal secret
//   These are SEPARATE from the host app's JWT-signing key.

import { ConfidentialClientApplication } from "@azure/msal-node";

export async function generateEmbedToken(input: {
  workspaceId: string;
  reportId: string;
  datasetId: string;
  effectiveIdentity: {
    username: string;
    roles: string[];
    datasets: string[];
  };
}) {
  const msalClient = new ConfidentialClientApplication({
    auth: {
      clientId: process.env.PBI_CLIENT_ID!,
      clientSecret: process.env.PBI_CLIENT_SECRET!,
      authority: `https://login.microsoftonline.com/${process.env.PBI_TENANT_ID}`,
    },
  });

  const tokenResponse = await msalClient.acquireTokenByClientCredential({
    scopes: ["https://analysis.windows.net/powerbi/api/.default"],
  });

  const embedTokenResponse = await fetch(
    `https://api.powerbi.com/v1.0/myorg/groups/${input.workspaceId}/reports/${input.reportId}/GenerateToken`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${tokenResponse!.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        accessLevel: "View",
        identities: [input.effectiveIdentity],
        lifetimeInMinutes: 10, // SHORT-LIVED per house opinion #4
      }),
    }
  );

  const { token, embedUrl } = await embedTokenResponse.json();
  return { embedToken: token, embedUrl };
}
```

## Why this is a stub in v0.1.0

1. **MSAL library version drift** — `@azure/msal-node` ships breaking changes regularly
2. **powerbi-client library version drift** — Microsoft updates the embed SDK frequently
3. **Real engagement validation** — the specific EffectiveIdentity shape varies by Power BI tenant configuration; the canonical pattern needs a real engagement to validate
4. **Coordination with power-platform plugin** — DAX role authoring + semantic model setup are owned there; this template assumes the role exists

## Acceptance criteria for promotion to v0.2.0

- [ ] Real M365-stack engagement uses this seam structure
- [ ] Service principal added to Power BI workspace (Workspace contributor role)
- [ ] DAX role authored and tested by `power-platform/power-bi-engineer`
- [ ] CSP nonce values configured (Power BI requires nonce-based script-src)
- [ ] CSP `frame-ancestors` includes Power BI embed domains
- [ ] Cross-boundary denial test: role-coverage test passes for every DAX role
- [ ] Embed token expiration short (5-15 min)

## Pricing reminder (per `power-bi-embedded-for-consultants.md`)

- **F2 capacity:** ~$262.80/mo PAYG, ~$156/mo reserved (verify before quoting)
- **Pro license** (for report builders, NOT viewers): $14/mo (raised from $10 April 2025)
- **App-Owns-Data** means viewers do NOT need PBI Pro licenses — capacity covers them. This is why F-SKU is cost-effective for customer-facing embeds.
- **Practitioner ISV guide recommends F4+ for real production loads** (F2 fine for dev / small demos)

## Security-review checklist (for runnable .tsx version)

- [ ] Service principal credentials in env vars (NOT inline)
- [ ] MSAL `client_credentials` flow used (NOT delegated)
- [ ] Embed token `lifetimeInMinutes` ≤ 15
- [ ] EffectiveIdentity username is the tenant_id from authenticated session (NEVER from request body)
- [ ] DAX role coverage tested in CI
- [ ] CSP nonce-based script-src configured
- [ ] CSP `frame-ancestors` allowlist
- [ ] iframe `sandbox` attributes per the embed-csp-and-iframe-sandboxing skill
- [ ] Service principal has only `Workspace.Contributor` role (least privilege)
- [ ] Coordinate with `power-platform/power-bi-engineer` for DAX role auditing

## Refresh triggers

- `@azure/msal-node` or `powerbi-client` major-version bump
- Power BI Embedded pricing restructure (Microsoft does annual changes)
- Fabric OneLake security model evolves (workspace roles + OneSecurity)
- Real engagement promotes this to runnable `.tsx`
- App-Owns-Data flow contract changes
