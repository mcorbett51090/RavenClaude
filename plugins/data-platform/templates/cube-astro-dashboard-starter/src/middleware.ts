import { defineMiddleware } from "astro:middleware";

// CSP for the no-iframe (direct-API) Cube embed pattern — see
// ../skills/embed-csp-and-iframe-sandboxing/SKILL.md "Cube (with custom
// React UI)". connect-src is the load-bearing directive here.
//
// ⛔ See README.md's CSP caveat: this covers every response that goes
// through the SSR runtime. A response served directly from a CDN/edge
// cache outside that runtime (adapter-dependent) will NOT carry this
// header — set it at the host/CDN config level too if that applies to
// your deployment.
//
// process.env, NOT import.meta.env (FORGE dashboard-top1pct P0-5, 2026-09-03):
// confirmed empirically this session that `import.meta.env.X || <fallback>`
// gets frozen to its literal fallback at BUILD time when X is unset during
// `astro build` (Vite's dead-code-elimination collapses the `||` expression
// to a constant) — a production build without CUBE_API_ORIGIN set at BUILD
// time would ship a CSP pointing at localhost:4000 forever, regardless of
// what's set at deploy/runtime. process.env sidesteps Vite's static-replace
// plugin entirely (it only targets import.meta.env.*).
//
// ⛔ CUBE_API_ORIGIN must be scheme+host[:port] ONLY — no path, query, or
// fragment, e.g. "https://cube.client-domain.com". Validated below via
// safeOrigin(), not just documented: this value is interpolated directly
// into a header the browser parses as policy, and CSP honors only the FIRST
// occurrence of a directive — an unvalidated value containing `;` could
// inject an early directive that silently overrides the real one later in
// the string (found in security review, 2026-09-03). URL.origin cannot
// contain `;` or whitespace, so parsing + re-serializing through it closes
// the class rather than blacklisting a character.
//
// script-src uses a per-request nonce (2026-09-16 starter-smoke follow-up):
// Astro 4.x has no native security.csp hash support (5.9+), and the layout's
// theme-init <script is:inline> plus Astro/React island bootstrap inlines are
// blocked by bare `script-src 'self'`. We (1) stash the nonce on Astro.locals
// for scripts we author, and (2) rewrite HTML responses to stamp the same
// nonce onto any <script> Astro injects without one. External module scripts
// stay covered by `'self'`. Do NOT add `'unsafe-inline'`.
//
// style-src-attr, NOT a bare style-src 'unsafe-inline' (tightened per
// security review, 2026-09-03): a plain `style-src 'self' 'unsafe-inline'`
// permits both inline <style> ELEMENTS and style="" ATTRIBUTES. Recharts only
// needs the latter (inline style attributes on SVG chart elements at
// runtime, computed pixel values a hash could never cover build-time or
// not). Splitting into style-src (element-authorizing fallback, kept
// permissive only because Astro 4.x has no hash mechanism to tighten it
// further) + style-src-attr 'unsafe-inline' (what's actually needed) is
// strictly tighter than the single blanket line this starter shipped with
// at first — re-verify if Astro is ever bumped past 5.9 and native CSP
// hashing becomes available for style-src-elem too.
function safeOrigin(raw: string | undefined, fallback: string): string {
  try {
    const u = new URL(raw ?? "");
    if (u.pathname !== "/" || u.search || u.hash) return fallback;
    return u.origin;
  } catch {
    return fallback;
  }
}

function buildCsp(cubeApiOrigin: string, nonce: string): string {
  return [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}'`,
    "style-src 'self' 'unsafe-inline'",
    "style-src-attr 'unsafe-inline'",
    `connect-src 'self' ${cubeApiOrigin}`,
    "frame-ancestors 'self'",
    "img-src 'self' data:",
    "object-src 'none'",
    "base-uri 'self'",
  ].join("; ");
}

/** Stamp nonce onto <script> tags that lack one (Astro-injected inlines). */
function applyScriptNonces(html: string, nonce: string): string {
  return html.replace(/<script(?![^>]*\bnonce=)(\s|>)/gi, `<script nonce="${nonce}"$1`);
}

export const onRequest = defineMiddleware(async (context, next) => {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  context.locals.cspNonce = nonce;

  const cubeApiOrigin = safeOrigin(process.env.CUBE_API_ORIGIN, "http://localhost:4000");
  const csp = buildCsp(cubeApiOrigin, nonce);
  const response = await next();

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("text/html")) {
    const html = await response.text();
    const rewritten = applyScriptNonces(html, nonce);
    const headers = new Headers(response.headers);
    headers.set("Content-Security-Policy", csp);
    headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
    return new Response(rewritten, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  }

  response.headers.set("Content-Security-Policy", csp);
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  return response;
});
