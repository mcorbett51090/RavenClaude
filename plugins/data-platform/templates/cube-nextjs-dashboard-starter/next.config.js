/** @type {import('next').NextConfig} */
// CSP lives in middleware.ts, NOT here (moved there in FORGE dashboard-top1pct
// P0-5, 2026-09-03). next.config.js's headers() is evaluated ONCE at `next
// build` time and baked into .next/routes-manifest.json permanently — confirmed
// empirically this session: a build with CUBE_API_ORIGIN unset froze
// `connect-src` to `http://localhost:4000` in the manifest forever, regardless
// of what CUBE_API_ORIGIN was set to at `next start` runtime. middleware.ts
// runs per-request, so it reads the real runtime value every time. See
// ../../skills/embed-csp-and-iframe-sandboxing/SKILL.md "Cube (with custom
// React UI)" for the connect-src rationale.
//
// ⛔ Next.js 16 deprecates the `middleware` filename/export in favor of
// `proxy`, and `proxy` does not support the `edge` runtime (per the Next 16
// upgrade guide). Not a blocker today — this starter is pinned to Next 14.2.x
// and that major bump is deliberately deferred (see README's npm-audit
// caveat) — but a future Next 16 migration should rename middleware.ts to
// proxy.ts as part of that bump, not as a surprise second rewrite.
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
