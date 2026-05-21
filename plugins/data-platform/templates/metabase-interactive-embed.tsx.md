# Metabase Interactive Embedding (React component) — seam-marked stub

> **Status:** v0.1.0 conceptual stub. Documents the seams; not compiling code.
> **Promoted to runnable `.tsx` in v0.2.0** after a real engagement validates the seams.
>
> **Last reviewed:** 2026-05-21
>
> ⚠ **Pricing reminder:** Metabase Interactive Embedding requires **Pro at $575/mo + $12/viewer/month** (10 users included). Static Guest Embeds are free on OSS but include the "Powered by Metabase" badge. The data-platform house opinion #2 resists per-viewer-priced BI tools for SMB consulting — surface the math (~$144/viewer/yr × viewer count) before defaulting to this template.

## The seams this component owns

1. **JWT signing seam** — host app signs a JWT with Metabase's `embedding-secret-key` (NOT the host app's general JWT-signing key)
2. **Iframe URL composition seam** — JWT becomes a URL parameter on Metabase's `/embed/dashboard/` or `/embed/question/` endpoint
3. **Locked-parameter seam** — Metabase Pro+ supports locked parameters that the embed URL cannot change (the tenant scope rule)
4. **Theme override seam** — Metabase iframe params for theme, hide-controls, hide-title

## The component skeleton (illustrative)

```tsx
import jwt from "jsonwebtoken";
import { useMemo } from "react";

interface MetabaseEmbedProps {
  /** Metabase dashboard ID */
  dashboardId: number;
  /** Tenant ID from host app's session */
  tenantId: string;
  /** Metabase site URL */
  metabaseUrl: string;
  /** Optional theme params */
  theme?: "light" | "night";
  height?: number;
}

export function MetabaseEmbed({
  dashboardId,
  tenantId,
  metabaseUrl,
  theme = "light",
  height = 800,
}: MetabaseEmbedProps) {
  const iframeUrl = useMemo(() => {
    // SEAM 1: JWT signing with Metabase's embedding-secret-key
    // CRITICAL: this key is SEPARATE from the host app's general JWT-signing key
    // It comes from Metabase Admin → Settings → Embedding → Embedding secret key
    const payload = {
      resource: { dashboard: dashboardId },
      // SEAM 3: Locked parameter — the tenant_id the iframe cannot change
      params: {
        tenant_id: tenantId,
      },
      exp: Math.round(Date.now() / 1000) + 10 * 60, // 10 min expiration
    };

    const token = jwt.sign(payload, process.env.METABASE_EMBEDDING_SECRET_KEY!, {
      algorithm: "HS256",
    });

    // SEAM 2: Iframe URL composition
    // SEAM 4: Theme + display params
    const params = new URLSearchParams({
      theme,
      // Other display params:
      // bordered: "false",
      // titled: "false",
    });

    return `${metabaseUrl}/embed/dashboard/${token}#${params.toString()}`;
  }, [dashboardId, tenantId, metabaseUrl, theme]);

  return (
    <iframe
      src={iframeUrl}
      width="100%"
      height={height}
      frameBorder="0"
      // Sandbox attributes per embed-csp-and-iframe-sandboxing skill
      sandbox="allow-scripts allow-same-origin allow-forms"
      title="Embedded Metabase dashboard"
      data-testid="metabase-interactive-embed"
    />
  );
}
```

## Key Metabase-specific details

### The locked parameter pattern is the tenant control

Metabase's locked parameters are how you enforce tenant scope. Configure on the Metabase side:

1. Open the dashboard or question in Metabase
2. Click "Embedding settings"
3. Add a parameter `tenant_id` and set it to "Locked"
4. The dashboard's underlying SQL must reference `{{tenant_id}}` in its WHERE clause

When the JWT signs with `params.tenant_id = "tenant-A-uuid"`, Metabase substitutes that into the query and the viewer cannot override it.

### Embedding secret key — a separate key from your JWT-issuer

This is a Metabase-specific signing key, distinct from the host app's general JWT-issuer key (`JWT_SIGNING_KEY` in [`jwt-issuer.ts`](jwt-issuer.ts)). Provision it as `METABASE_EMBEDDING_SECRET_KEY` in env vars; the data-platform-smells hook flags inline secrets.

### Sandbox (Pro+) is the row-level enforcement

For multi-tenant Metabase deployments where dashboard authors don't want to write `WHERE {{tenant_id}}` on every query, Metabase's **Sandbox feature** (Pro+) provides automatic row-level scoping based on user attributes. The locked parameter approach above is the simpler v0.1.0 pattern.

## Why this is a stub in v0.1.0

1. **Pricing reality** — Metabase Pro Interactive Embedding ($575/mo + $12/viewer) is rarely the right choice for SMB consulting. Shipping a fully-compiled component for an option the plugin actively resists feels backward.
2. **Static Guest Embed (free OSS)** is the more common pattern, and it doesn't need this component (URL-only embed)
3. **Pre-engagement validation** — like Superset, the component drifts with Metabase SDK versions

## Acceptance criteria for promotion to v0.2.0

- [ ] Real engagement uses Metabase Pro Interactive Embedding
- [ ] Pricing math signed off by the client (per-viewer cost surfaced explicitly)
- [ ] Sandbox vs locked-parameter decision documented
- [ ] CSP `frame-ancestors` + iframe `sandbox` posture validated by `ravenclaude-core/security-reviewer`
- [ ] Cross-boundary denial test passing (Metabase locked param prevents tenant-A viewer from seeing tenant-B data)

## When to recommend Metabase Static Guest Embed (free OSS) instead

If the engagement's dashboard does NOT need:
- Per-viewer authentication
- User-specific filtering
- Locked parameters

…then Metabase OSS Static Guest Embeds are free and don't need this component. Just sign a JWT-bearer URL on the host app and `<iframe src="{signedUrl}" />`. See Metabase OSS docs.

## Security-review checklist (for runnable .tsx version)

- [ ] `METABASE_EMBEDDING_SECRET_KEY` in env vars (NOT inline)
- [ ] JWT expiration short (5-15 min)
- [ ] Locked parameter enforced (tenant_id cannot be changed by iframe URL manipulation)
- [ ] CSP `frame-ancestors` allowlist documented
- [ ] iframe `sandbox` attributes set per the embed-csp-and-iframe-sandboxing skill
- [ ] Static Guest Embed considered as alternative if the engagement doesn't need Interactive

## Refresh triggers

- Metabase pricing changes (currently Pro $575/mo + $12/user — verify before quoting)
- Metabase SDK / embedding API major-version bump
- Real engagement promotes this to runnable `.tsx`
- Metabase ships a free Interactive Embedding tier (would change the recommendation calculus materially)
