// ---------------------------------------------------------------------------
// Metabase Interactive Embedding — server-only URL builder.
// ---------------------------------------------------------------------------
// SECURITY (split out after mandatory security review): this used to live in
// the same module as the client component. A prose warning is not a build
// boundary — under a bundler that inlines `process.env` (Vite/CRA/webpack
// DefinePlugin), colocating a server-only secret read with a client
// component risks shipping METABASE_EMBEDDING_SECRET_KEY to the browser.
// `import "server-only"` makes any accidental client import a BUILD ERROR
// on frameworks that support the package (Next.js App Router does; if your
// framework doesn't recognize the package it's a harmless no-op import — the
// module-split itself is the real control, this import is defense in depth).
// ---------------------------------------------------------------------------
import "server-only";

import jwt from "jsonwebtoken";

export interface BuildMetabaseEmbedUrlInput {
  dashboardId: number;
  tenantId: string;
  metabaseUrl: string;
  theme?: "light" | "night";
  bordered?: boolean;
  titled?: boolean;
}

/**
 * Builds a Metabase Interactive Embed URL with `tenant_id` LOCKED so the
 * embedded viewer cannot override it. Call this ONLY from a server route
 * that has resolved `tenantId` from an authenticated session — never from
 * client input. See "The locked parameter pattern is the tenant control" in
 * metabase-interactive-embed.tsx.md for the required Metabase-side
 * configuration (a dashboard whose SQL references `{{tenant_id}}`, with that
 * parameter marked Locked in Metabase's embedding settings).
 */
export function buildMetabaseEmbedUrl({
  dashboardId,
  tenantId,
  metabaseUrl,
  theme = "light",
  bordered = false,
  titled = false,
}: BuildMetabaseEmbedUrlInput): string {
  if (!process.env.METABASE_EMBEDDING_SECRET_KEY) {
    throw new Error("METABASE_EMBEDDING_SECRET_KEY is not set — refusing to build an embed URL.");
  }

  const payload = {
    resource: { dashboard: dashboardId },
    params: {
      tenant_id: tenantId,
    },
    exp: Math.round(Date.now() / 1000) + 10 * 60, // 10 min expiration
  };

  const token = jwt.sign(payload, process.env.METABASE_EMBEDDING_SECRET_KEY, {
    algorithm: "HS256",
  });

  const params = new URLSearchParams({
    theme,
    bordered: String(bordered),
    titled: String(titled),
  });

  return `${metabaseUrl.replace(/\/$/, "")}/embed/dashboard/${token}#${params.toString()}`;
}
