import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwind from "@astrojs/tailwind";
import node from "@astrojs/node";

// output: 'server' is REQUIRED — /api/cube-token must run per-request
// server-side (it reads the caller's session and mints a short-lived JWT).
// The @astrojs/node adapter (standalone mode) is the documented default.
//
// ⛔ "Only the adapter line changes" is NO LONGER TRUE for Workers-class
// targets since P0-5's env-var fix (found in security review, 2026-09-03):
// src/pages/api/cube-token.ts and src/middleware.ts now read
// JWT_SIGNING_KEY/JWT_ISSUER/JWT_KEY_VERSION/CUBE_API_ORIGIN via bare
// process.env (the fix for import.meta.env's build-time-freeze bug — see
// those files' own headers). On @astrojs/node, process.env is the real Node
// global and this just works. On @astrojs/cloudflare, there is NO
// process.env without the `nodejs_compat` flag, and even with it, it is not
// populated from Worker environment bindings. The failure is silent and
// fails closed, not open: CUBE_API_ORIGIN resolves to the localhost
// fallback (CSP then blocks real Cube API calls), and JWT_SIGNING_KEY is
// undefined (the token route 500s) — but nothing warns you. If you swap to
// a Workers-class adapter, also swap these reads to
// `Astro.locals.runtime.env.X` (Cloudflare) or the equivalent platform
// binding — do NOT restore an `import.meta.env` fallback, that reintroduces
// the build-time freeze this fix closed. See README.md's CSP caveat too,
// before assuming middleware alone covers every response path on every
// adapter.
export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  integrations: [react(), tailwind()],
});
