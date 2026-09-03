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
const CUBE_API_ORIGIN = import.meta.env.CUBE_API_ORIGIN || "http://localhost:4000";

export const onRequest = defineMiddleware(async (_context, next) => {
  const response = await next();
  response.headers.set(
    "Content-Security-Policy",
    [
      "default-src 'self'",
      `connect-src 'self' ${CUBE_API_ORIGIN}`,
      "frame-ancestors 'self'",
      "img-src 'self' data:",
      "object-src 'none'",
      "base-uri 'self'",
    ].join("; "),
  );
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  return response;
});
