# Superset embed (React iframe component) — seam-marked stub

> **Status:** v0.1.0 conceptual stub. Documents the seams; not compiling code.
> **Promoted to runnable `.tsx` in v0.2.0** after a real engagement validates the seams.
>
> **Last reviewed:** 2026-05-21
>
> Companion docs:
>   - [`../skills/jwt-embed-issuance/SKILL.md`](../skills/jwt-embed-issuance/SKILL.md) — JWT issuance
>   - [`../skills/embed-csp-and-iframe-sandboxing/SKILL.md`](../skills/embed-csp-and-iframe-sandboxing/SKILL.md) — CSP / sandbox boundary
>   - [`../knowledge/embedded-analytics-landscape-2026.md`](../knowledge/embedded-analytics-landscape-2026.md) — Superset position in the landscape

## The seams this component owns

A Superset embed React component handles four distinct concerns. Each is a seam to mark explicitly:

1. **JWT acquisition seam** — calls the host app's JWT-issuer endpoint to get a short-lived token with tenant claims
2. **Guest token exchange seam** — POSTs the JWT to Superset's `/api/v1/security/guest_token` endpoint to receive a Superset-specific guest token
3. **SDK initialization seam** — invokes `embedDashboard()` from `@superset-ui/embedded-sdk` with the guest token, target div, and dashboard UUID
4. **Theme + height override seam** — passes Superset-side theme params via the guest token's `extra` field; listens for postMessage resize events

## The component skeleton (illustrative)

```tsx
import { embedDashboard } from "@superset-ui/embedded-sdk";
import { useEffect, useRef } from "react";

interface SupersetEmbedProps {
  /** Superset dashboard UUID — the engagement-specific dashboard to render */
  dashboardId: string;
  /** Tenant ID from the host app's session — NEVER from URL/body */
  tenantId: string;
  /** User ID for the audit trail */
  userId: string;
  /** Superset instance URL */
  supersetDomain: string;
  /** Optional theme + height overrides */
  height?: number;
  themeOverride?: SupersetTheme;
}

export function SupersetEmbed({
  dashboardId,
  tenantId,
  userId,
  supersetDomain,
  height = 800,
  themeOverride,
}: SupersetEmbedProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // SEAM 1: JWT acquisition from host app
    // (route through the data-platform/templates/jwt-issuer.ts endpoint)
    fetchHostAppJWT({ userId, tenantId, audience: "superset" })
      .then(async (hostJwt) => {
        // SEAM 2: Guest token exchange
        // Superset validates the host JWT and issues its own guest token
        // with the tenant_id as an RLS clause
        const guestToken = await fetch(`${supersetDomain}/api/v1/security/guest_token`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${hostJwt}` },
          body: JSON.stringify({
            resources: [{ type: "dashboard", id: dashboardId }],
            rls: [{ clause: `tenant_id = '${tenantId}'` }],
            user: { username: userId, first_name: "", last_name: "" },
          }),
        }).then((r) => r.json()).then((d) => d.token);

        // SEAM 3: SDK initialization
        embedDashboard({
          id: dashboardId,
          supersetDomain,
          mountPoint: containerRef.current!,
          fetchGuestToken: () => Promise.resolve(guestToken),
          dashboardUiConfig: {
            hideTitle: true,
            hideChartControls: false,
            ...(themeOverride && { theme: themeOverride }),
          },
        });

        // SEAM 4: Theme + height override (postMessage listener)
        // Superset emits resize events; the host can listen and adjust
        window.addEventListener("message", (event) => {
          if (event.origin !== supersetDomain) return; // origin check
          if (event.data?.type === "resize") {
            // adjust container height
          }
        });
      });
  }, [dashboardId, tenantId, userId, supersetDomain]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: `${height}px` }}
      data-testid="superset-embed"
    />
  );
}
```

## Why this is a stub in v0.1.0

The component above is *illustrative* — it documents the seams the runnable version will need to compile in v0.2.0. Reasons to stay at stub:

1. **Superset SDK version drift** — `@superset-ui/embedded-sdk` ships breaking changes between releases; pinning a specific version in v0.1.0 risks being outdated by the first real engagement
2. **React + Next.js version coupling** — compiling code commits to a specific React (18 vs 19) and Next.js version
3. **Theme system coupling** — Superset's theme model evolves; the override seam looks different in 2026 than in 2025
4. **Marketplace pattern** — every existing plugin's templates are conceptual markdown, not compiling code. The expert-reviewed plan kept the .tsx.md format to match.

## Acceptance criteria for promotion to v0.2.0

- [ ] Real engagement uses this seam structure
- [ ] Superset SDK version pinned and tested
- [ ] React + Next.js versions confirmed (likely React 19 + Next 14+)
- [ ] CSP `frame-ancestors` + iframe `sandbox` posture validated by `ravenclaude-core/security-reviewer`
- [ ] Cross-boundary denial test passing (Superset RLS clause enforces tenant scope)

## Security-review checklist (for the runnable .tsx version, when promoted)

- [ ] JWT from host app, never client-constructed
- [ ] Tenant ID from JWT claim, never from URL / route params / body
- [ ] Guest token expiration short (5-15 min)
- [ ] postMessage origin check (the `event.origin !== supersetDomain` clause above)
- [ ] CSP `frame-ancestors` allowlist documented for the host page
- [ ] iframe `sandbox` attributes per `embed-csp-and-iframe-sandboxing` skill

## Refresh triggers

- Superset SDK major-version bump
- Real engagement promotes this to runnable `.tsx`
- React or Next.js version-bump that affects iframe / postMessage semantics
- Superset embedding model evolves (e.g., web-component vs iframe transition)
