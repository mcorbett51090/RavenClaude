import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwind from "@astrojs/tailwind";
import node from "@astrojs/node";

// output: 'server' is REQUIRED — /api/cube-token must run per-request
// server-side (it reads the caller's session and mints a short-lived JWT).
// The @astrojs/node adapter (standalone mode) is the documented default; if
// your deployment target is Vercel/Cloudflare/Netlify, swap this for that
// platform's adapter package — the API route code itself is unaffected,
// only this file's `adapter` line changes. See README.md's CSP caveat
// before assuming middleware alone covers every response path on every
// adapter.
export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  integrations: [react(), tailwind()],
});
