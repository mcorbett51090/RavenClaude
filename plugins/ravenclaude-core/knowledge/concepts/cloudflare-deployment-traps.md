---
id: cloudflare-deployment-traps
title: "Cloudflare deployment traps that cost a day"
category: "Shipping lessons"
kind: ravenclaude-built
order: 23
summary: "Six Cloudflare Pages behaviours that each cost real debugging time. They share one shape: every failure is silent and plausible, so you diagnose a wrong thing confidently for hours."
see_also: [cloudflare-how-users-find-you, build-time-vs-runtime-config, claim-grounding]
last_verified: 2026-07-21
refresh_when: "Cloudflare Pages changes when bindings and secrets attach, adds named environments beyond production/preview, or starts documenting Functions propagation and the POST content-type rejection."
sources:
  - label: "Cloudflare Pages — Functions bindings ('Redeploy your project for the binding to take effect')"
    url: "https://developers.cloudflare.com/pages/functions/bindings/"
  - label: "Cloudflare Pages — Wrangler configuration (production and preview are the only two environments)"
    url: "https://developers.cloudflare.com/pages/functions/wrangler-configuration/"
  - label: "Wrangler commands — pages secret put"
    url: "https://developers.cloudflare.com/workers/wrangler/commands/pages/"
  - label: "Wrangler — environments and the --env flag"
    url: "https://developers.cloudflare.com/workers/wrangler/environments/"
  - label: "Cloudflare SSL — certificate and hostname priority (SNI selection)"
    url: "https://developers.cloudflare.com/ssl/reference/certificate-and-hostname-priority/"
  - label: "Cloudflare D1 — local development (preview_database_id)"
    url: "https://developers.cloudflare.com/d1/configuration/local-development/"
---

Each of these was paid for with real debugging time on a live Cloudflare Pages project. None of them throws. That is the point — read the last section before you decide these are trivia.

**1 — Secrets and D1 bindings attach at DEPLOY time.** Setting a secret or adding a binding changes nothing about what is currently running. Cloudflare says it plainly, once per binding type: *"Redeploy your project for the binding to take effect."* So the loop that feels obvious — set the secret, hit the endpoint, still broken, set it again — is testing the **old** value every time, and you will conclude the secret is wrong when it was right on the first try. Set it, **deploy**, then test.

**2 — Functions propagate after static assets.** On a fresh deploy the pages render perfectly while every `/api/*` route still 404s, for roughly 30–60 seconds. You will spend that window convinced you broke routing. Deploy, wait, *then* diagnose — a 404 inside the propagation window is not evidence of anything. `[unverified — field-observed; the Pages known-issues page documents no propagation lag, so treat the exact window as an observation, not a contract]`

**3 — Cloudflare routes by TLS SNI, so a forged `Host:` header proves nothing.** Certificate and zone selection happen during the TLS handshake, on the SNI hostname: *"Certificates and settings that match the SNI hostname exactly take precedence"*, and *"If no SNI is presented, Cloudflare uses certificate based on the IP address."* The HTTP `Host` header arrives **after** that choice is already made. This invalidates a whole category of test people write — `curl -H "Host: my-app.example.com" https://some-other-host/` does not put you on that zone's Worker, it puts you on whatever zone the SNI selected, holding a header nobody routed on. If you want to test a hostname, resolve to it or use `--resolve`; do not fake the header.

**4 — Pages rejects a POST with no `content-type` before your Function runs.** It comes back as its own 403, treated as a cross-site form submission — and because the rejection is upstream of your code, **your handler's logs show nothing at all**. That silence reads exactly like "my route isn't wired up," which is the wrong hunt. Always send an explicit `content-type` on POST, including from `fetch`, scripts and health checks. `[unverified — field-observed; not documented in the Pages known-issues page]`

**5 — `--env preview` on `wrangler pages secret put` is undocumented but load-bearing.** The Pages command reference lists only `[KEY]` and `--project-name` for `pages secret put`; `--env` is a *global* Wrangler flag, and omitting it means Wrangler "uses the top-level configuration." Pages, meanwhile, has exactly two environments — *"`production` and `preview` are the only two options available via `[env.<ENVIRONMENT>]`."* Net effect: the secret lands in one environment and you assume both. Preview then runs with a missing or stale value while production is fine, and the difference is invisible until a preview deploy behaves nothing like the branch it came from. Set it once per environment, explicitly.

**6 — `preview_database_id` does not bind a preview deployment.** It is a *local development* key — D1's docs describe it as "a user-defined ID for your local test database." It is not how a deployed Pages preview picks a database, and nothing errors when you use it that way; the preview simply keeps whatever it had, which is usually **production**. That is a preview branch writing to the real database while everyone believes it is isolated. The documented Pages shape is an explicit environment override:

```toml
[[env.preview.d1_databases]]
binding = "DB"
database_name = "my-app-preview"
database_id = "<PREVIEW_DATABASE_ID>"
```

**The unifying lesson, which is the actually portable part.** Every one of these fails **silently and plausibly**: no exception, no warning, and a symptom that points confidently at something else — a wrong secret, a broken route, an unwired handler, an isolated preview. That is why they cost a day rather than a minute. The defence is not memorising six Cloudflare facts; it is the habit of asking, before you start bisecting: *what would this look like if my mental model of when config attaches were wrong?* Deploy before you test a secret. Wait before you diagnose a 404. Don't trust a header the platform didn't route on. Don't trust a preview you never proved was pointed somewhere else.

```mermaid
flowchart TD
  S[You change something] --> W{When does it take effect?}
  W -->|secret or binding| D[Next DEPLOY · not now]
  W -->|Functions| P[~30-60s AFTER static assets]
  D --> T1[Trap · you test the OLD value]
  P --> T2[Trap · /api 404s on a good deploy]
  R[You write a test] --> H{What does the platform route on?}
  H -->|TLS SNI| T3[Trap · forged Host header proves nothing]
  H -->|no content-type on POST| T4[Trap · 403 before your code · no logs]
  C[You set config] --> E{Which environment?}
  E -->|--env omitted| T5[Trap · secret in one env only]
  E -->|preview_database_id| T6[Trap · preview bound to PRODUCTION db]
  T1 --> L[All six fail SILENTLY and PLAUSIBLY]
  T2 --> L
  T3 --> L
  T4 --> L
  T5 --> L
  T6 --> L
  class T1,T2,T3,T4,T5,T6 built
  class L fact
```

<!-- mini -->
```mermaid-mini
flowchart LR
  C[change config] --> D[deploy] --> T[then test]
  X[test before deploy] -.-> W[wrong conclusion]
  class D,T fact
  class W built
```
