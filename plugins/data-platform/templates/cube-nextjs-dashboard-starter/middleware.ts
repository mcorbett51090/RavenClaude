import { NextRequest, NextResponse } from "next/server";

// CSP moved here from next.config.js's headers() (FORGE dashboard-top1pct P0-5,
// 2026-09-03) — next.config.js is evaluated ONCE at `next build` time, and its
// headers() return value is baked into .next/routes-manifest.json permanently.
// Confirmed empirically this session: building with CUBE_API_ORIGIN unset froze
// `connect-src 'self' http://localhost:4000` into the manifest; a later `next
// start` with CUBE_API_ORIGIN set to the real origin was silently ignored. Reading
// process.env.CUBE_API_ORIGIN here (middleware runs per-request, never baked into
// a build-time manifest) fixes it for real, not by inference.
//
// script-src/style-src nonce pattern is Next.js's own documented CSP recipe
// (docs/02-app/.../15-content-security-policy.mdx, verified via Context7
// 2026-09-03) — a per-request nonce is generated, propagated to Server
// Components via the `x-nonce` request header, and set on both request and
// response Content-Security-Policy headers.
//
// ⛔ CUBE_API_ORIGIN must be scheme+host[:port] ONLY — no path, query, or
// fragment, e.g. "https://cube.client-domain.com". Validated below via
// safeOrigin(), not just documented: this value is interpolated directly into
// a header the browser parses as policy, and CSP honors only the FIRST
// occurrence of a directive — an unvalidated value containing `;` could
// inject an early directive (e.g. a permissive frame-ancestors) that silently
// overrides the real one later in the string. URL.origin cannot contain `;`
// or whitespace, so parsing + re-serializing through it closes the class
// rather than blacklisting a character (found in security review, 2026-09-03).
function safeOrigin(raw: string | undefined, fallback: string): string {
  try {
    const u = new URL(raw ?? "");
    if (u.pathname !== "/" || u.search || u.hash) return fallback;
    return u.origin;
  } catch {
    return fallback;
  }
}

// A request that never renders our HTML (an /api/* route, or a prefetch that
// won't be shown to the user) does not need — and, for prefetches, MUST NOT
// carry — a per-request nonce (a prefetched document's nonce would mismatch
// the document actually rendered). It still gets a real CSP, just without a
// nonce: found in security review (2026-09-03) that dropping the header
// entirely on these paths was broader than the actual problem, and that the
// matcher's `api` exclusion below was unanchored (matched `/api-docs`, not
// just `/api/`).
function buildCsp(cubeApiOrigin: string, isProd: boolean, nonce: string | null): string {
  const scriptSrc = nonce
    ? `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isProd ? "" : " 'unsafe-eval'"};`
    : "script-src 'self';";
  // style-src-attr / style-src-elem, NOT a bare nonced style-src (found in
  // security review, 2026-09-03): a nonce authorizes inline <style> ELEMENTS
  // only (CSP Level 3) — it does NOT authorize inline style="" ATTRIBUTES,
  // which is exactly what this app's own RevenueChart.tsx and Recharts render
  // at runtime. A bare `style-src 'self' 'nonce-x'` blocks every inline style
  // attribute in this app and collapses the chart to 0px height. Chromium
  // honors the two specific *-attr/*-elem directives (verified: browsers that
  // support them ignore the style-src fallback once a more specific directive
  // is present); Firefox does not support style-src-attr/style-src-elem at
  // all and falls back to the (permissive) style-src line, which is exactly
  // this starter's pre-P0-5 behavior — no regression there. style-src-elem is
  // gated on isProd because next dev injects styles via JS-created <style>
  // elements that would otherwise trip it.
  const styleSrc = [
    "style-src 'self' 'unsafe-inline';",
    "style-src-attr 'unsafe-inline';",
    isProd ? "style-src-elem 'self';" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const cspHeader = `
    default-src 'self';
    ${scriptSrc}
    ${styleSrc}
    connect-src 'self' ${cubeApiOrigin};
    img-src 'self' data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'self';
  `;
  return cspHeader.replace(/\s{2,}/g, " ").trim();
}

export function middleware(request: NextRequest) {
  const cubeApiOrigin = safeOrigin(process.env.CUBE_API_ORIGIN, "http://localhost:4000");
  const isProd = process.env.NODE_ENV === "production";

  const isPrefetch =
    request.headers.has("next-router-prefetch") || request.headers.get("purpose") === "prefetch";
  // Anchored to a trailing "/" so "/api-docs"/"/apidashboard" are NOT treated
  // as the API route (found in security review, 2026-09-03 — the matcher
  // regex below has the same unanchored-prefix bug and is fixed alongside).
  const isApiRoute =
    request.nextUrl.pathname === "/api" || request.nextUrl.pathname.startsWith("/api/");
  const nonce =
    isPrefetch || isApiRoute ? null : Buffer.from(crypto.randomUUID()).toString("base64");

  const contentSecurityPolicyHeaderValue = buildCsp(cubeApiOrigin, isProd, nonce);

  const requestHeaders = new Headers(request.headers);
  if (nonce) requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("Content-Security-Policy", contentSecurityPolicyHeaderValue);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", contentSecurityPolicyHeaderValue);
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  return response;
}

export const config = {
  matcher: [
    {
      // Only truly static, non-HTML assets are excluded from running the
      // middleware at all — /api/* and prefetches still run it (see isApiRoute
      // / isPrefetch above), they just get a nonce-free baseline CSP instead
      // of no header at all.
      source: "/((?!_next/static|_next/image|favicon.ico).*)",
    },
  ],
};
