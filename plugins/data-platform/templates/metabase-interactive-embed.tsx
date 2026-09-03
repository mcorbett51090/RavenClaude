// ---------------------------------------------------------------------------
// Metabase Interactive Embedding (React CLIENT component) — RUNNABLE,
// promoted from metabase-interactive-embed.tsx.md at v0.2.0.
// ---------------------------------------------------------------------------
// SECURITY: the signing secret + URL-building logic now live in the
// server-only sibling ./metabase-embed-url.server.ts (see that file's header
// for why the split matters). This file imports NOTHING that touches
// METABASE_EMBEDDING_SECRET_KEY, so it is safe to bundle for the client.
//
// ⚠ Pricing reminder (re-verify before quoting): Metabase Interactive
// Embedding requires Pro at $575/mo + $12/viewer/month — see
// embedded-analytics-landscape-2026.md. Static Guest Embeds are free on OSS
// but carry the "Powered by Metabase" badge and don't need this component —
// see "When to use Static Guest Embed instead" below.
//
// KNOWN GAP: not yet run against a live Metabase Pro instance.
// ---------------------------------------------------------------------------

import { useMemo } from "react";

/**
 * Renders a Metabase Interactive Embed. `embedUrl` must come from a server
 * route that called ./metabase-embed-url.server.ts's buildMetabaseEmbedUrl()
 * — never construct it client-side.
 */
export function MetabaseEmbed({ embedUrl, height = 800 }: { embedUrl: string; height?: number }) {
  const src = useMemo(() => embedUrl, [embedUrl]);

  return (
    <iframe
      src={src}
      width="100%"
      height={height}
      style={{ border: "none" }}
      sandbox="allow-scripts allow-same-origin allow-forms"
      title="Embedded Metabase dashboard"
      data-testid="metabase-interactive-embed"
    />
  );
}

// ---------------------------------------------------------------------------
// When to use Metabase Static Guest Embed (free OSS) instead:
//   If the engagement's dashboard does NOT need per-viewer auth,
//   user-specific filtering, or locked parameters, sign a JWT-bearer URL on
//   the host app and render a plain <iframe src={signedUrl} /> — no need for
//   this component or the Pro-tier pricing. See Metabase OSS docs.
// ---------------------------------------------------------------------------
