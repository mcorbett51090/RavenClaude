# llm-stats.com as a data source for `agent-routing-matrix.json` — verified findings

**Date:** 2026-09-02 · **Trigger:** owner asked whether llm-stats.com data could ground/enrich
`plugins/ravenclaude-core/knowledge/agent-routing-matrix.json` (the FORGE-built task→{agent, model,
effort} routing table, v0.311.0). This note exists so the next session doesn't re-derive these facts
from scratch, and so it doesn't repeat the mistake this session made along the way (below).

## What's real (this-session HTTP checks, not WebFetch summarization)

- `curl https://llm-stats.com` → 200, ~1.86 MB **server-rendered** HTML (not a client-only SPA shell —
  real model names are present in the raw response, e.g. `Claude Opus 5`, `Claude Sonnet 5`,
  `Claude Fable 5.1`, `Claude Mythos Preview`, `Claude Opus 4.8`, alongside older `Claude 3.x` rows).
- The site tracks per-model: benchmark scores (GPQA Diamond, SWE-Bench Verified, a "Coding Arena"
  head-to-head), $/M-token pricing, context window, throughput/TTFT, params, license, provider.
- A real data API exists, backed by **ZeroEval** (a separate, real AI-monitoring/eval company —
  confirmed at `docs.zeroeval.com`, which has no llm-stats.com branding of its own, so this looks like
  llm-stats.com white-labeling ZeroEval's backend rather than ZeroEval hosting llm-stats.com's brand).
  Verified endpoint: `curl https://api.zeroeval.com/stats/v1/models` → **HTTP 401** (route exists,
  requires a bearer token — not a 404, so this is a real, live API surface).
- `llm-stats.com/developer` (200 OK, real page) documents the intended endpoint set:
  `/stats/v1/models`, `/stats/v1/models/{id}`, `/stats/v1/benchmarks`, `/stats/v1/scores`,
  `/stats/v1/rankings`, `/stats/v1/updates` — all under `api.zeroeval.com`, per a literal
  `href="https://api.zeroeval.com/stats/v1/models"` in that page's raw HTML.
- Auth: bearer API key, free signup ("Sign in to get your API key" / "Completely free with no usage
  limits" per the page text — **this specific claim is WebFetch-summarized, not independently
  verified**, since obtaining a key requires an account this session did not create).

## A diagnosis, and the control that backs it (not just an assertion)

WebFetch's job is "fetch + summarize with a small model," and on this site that step **fabricated
specific technical details** on top of otherwise-real content, twice, in a way that looked equally
confident both times:

1. First fetch stated the API was documented at `docs.zeroeval.com/llm-gateway/introduction`.
2. A later fetch of `llm-stats.com/developer` (correctly) named the endpoint **paths**
   (`/stats/v1/models` etc.) but not the **host** — acting on the plausible `docs.zeroeval.com` root
   from finding (1), a follow-up guessed `llm-stats.com/stats/v1/models` as the full URL.

**control:** `curl https://docs.zeroeval.com/llm-gateway/introduction` → **404** (negative);
`curl https://llm-stats.com/stats/v1/models` → **404** (negative, wrong host); **positive control on
the same subject** — `curl https://api.zeroeval.com/stats/v1/models` → **401** (route exists, enforces
auth at the *correct* host), and a raw-HTML `grep` of `llm-stats.com/developer` shows the literal
`href="https://api.zeroeval.com/stats/v1/models"` in-page, independent of any summarization. The 401
is what proves the probe mechanism was capable of returning something other than 404 — so the two
earlier 404s are evidence the claimed URLs were genuinely wrong, not just unreached.

**The generalizable lesson:** a WebFetch summary of a **real, content-rich page** can still invent a
specific URL/endpoint that sounds exactly as credible as the true ones sitting next to it in the same
summary. The fix that worked here was not "fetch again and hope" — it was dropping to raw `curl` +
`grep` on the actual page source and testing candidate hosts directly against real HTTP status codes.
Two more WebFetch passes on the same URL would not have caught this; the correction only came from
bypassing WebFetch's summarization layer entirely for the load-bearing claims.

## Recommendation, unchanged from the chat analysis, now on firmer footing

Use llm-stats.com **narrowly**, once a human obtains a free API key at `https://llm-stats.com/developer`
(signup is a human action — not done here):

- **Do**: cite `api.zeroeval.com/stats/v1/models` pricing data (dated, `[web-sourced]`) to strengthen
  `cost-heuristic` rationale in `agent-routing-matrix.json`, and SWE-Bench Verified / Coding Arena scores
  to strengthen `capability-fact` rationale in `coding-implementation`/`coding-debugging-design` — both
  already-existing `basis` categories, so this needs no schema change.
- **Do**: use it as an optional cross-check in the existing weekly researcher sweep against
  `model-catalog.json`'s `current`/`stale` lists — via the real API, never via a raw-HTML scrape.
- **Don't**: add a numeric confidence field to the matrix itself — Gate 255 check C bans this by design
  (a rank + cited `basis`, never a float), and that design intent predates and is independent of this
  finding.
- **Don't**: trust a WebFetch summary of this site (or any Next.js-SSR page mixing real data with a
  plausible-sounding surrounding narrative) for a specific URL, endpoint, or numeric claim without a
  raw `curl`/`grep` check first — this session is the worked example of why.

## What's still open (human-only residue, not done here)

1. Sign up at `https://llm-stats.com/developer` for a free API key.
2. Hand the key to a future session (as an env var, never pasted into a knowledge file) to pull real
   pricing/benchmark numbers and land them as cited `rationale` upgrades in
   `plugins/ravenclaude-core/knowledge/agent-routing-matrix.json` (a `plugins/` change → needs a PR
   per `AGENTS.md` PR conventions, branch `feat/ravenclaude-core-agent-routing-matrix-llm-stats-cites`).
