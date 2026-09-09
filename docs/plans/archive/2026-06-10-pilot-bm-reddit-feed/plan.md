# FORGE plan — Bermuda Reddit feed for Pilot.BM (seed-first, live as gated v2)

> Synthesized from the FORGE run (scope + G1 verification + two cross-model panels + gap-delta). **G1 overturned the idea's premise:** a live Reddit feed on a *commercial* site is gated behind Reddit pre-approval + likely a paid contract + a no-ads-clause conflict. The synthesis ships value NOW with zero ToS risk and treats "live" as a gated upgrade.

## The wall G1 found (verified-ish — see confidence flags)
- **Reddit Responsible Builder Policy (Nov 2025):** pre-approval required for ALL API access; 2–4 wk review; "personal scripts won't qualify." `[secondary sources: replydaddy, molehill.io — primary terms 403'd]`
- **Commercial use** = "any use by/for a business." Pilot.BM is commercial → contract path, not free tier. Call volume cost is trivial (~$0.69/mo); the *approval + contract* is the gate.
- **No-ads clause:** can't display Reddit content alongside display ads on the same site. **Directly conflicts with Pilot.BM's ad/affiliate monetization.** `[strongly indicated by both panels; VERIFY against Reddit's Developer Terms before relying on it — this is the load-bearing business risk]`
- **Public `.json` endpoint:** panels DISAGREED — Panel A: 403/dead since 2026-05-30; Panel B: alive at ~10 req/min unauthenticated. `[unverified — conflict]` Both agree: **not a production-safe path for a commercial brand** (doesn't exempt commercial-use/pre-approval; anti-bot + brand risk).
- **NSFW** `over_18` is a reliable filter field. Attribution = title links to the Reddit post + subreddit name shown, no content modification.

## Recommendation — V1: the `seed` feed (ships now, pure static, zero ToS risk)
A hand-curated "best of r/Bermuda" per section, committed as JSON, rendered by an Astro component. **No serverless, no API, no hosting change** — works on the in-flight GitHub Pages deploy today.
- `src/data/reddit-seed/{visit,move,live}.json` — 3–6 curated posts per section: title, permalink (links to the real Reddit post), subreddit, score-at-curation, date, one-line why-relevant.
- A `RedditFeed.astro` (+ small island) per-section widget — tasteful, brand-matched, with a "Source: r/Bermuda on Reddit" attribution footer + link-out. Titles + link-out only, **never** republished bodies (user copyright).
- Curation is the brand-safety layer: only posts you'd put your name next to. Refreshed by hand (or a future cron) — for a low-volume subreddit, monthly-ish is fine.
- This is honestly MORE on-brand than a raw feed (curated = the high-end ethos).

## V2 (gated, ONLY if Reddit commercial access + ads-conflict resolved): live Worker
Panel A's design, behind a feature flag / source-adapter (`seed` | `oauth` | `proxy`):
- **Hosting (Panel B's lower-churn call):** keep GitHub Pages + a **standalone Cloudflare Worker** (`reddit-proxy.pilot.bm`) — do NOT rip out the in-flight Pages deploy. (Full Cloudflare Pages migration is a separate later decision.)
- **Cron-refreshed KV cache** (every 30–60 min), NOT live-per-request — low-volume subreddit, avoids the free-tier regional-cache-miss + 10ms-CPU issues; the HTTP Worker only reads KV. Keys in the Worker env, never the browser.
- Same curation filter (NSFW hard-screen → removed/locked/stickied/min-score → flair-allowlist/keyword → brand denylist → dedup → top-N) + an evergreen KV fallback (the seed) so an empty/rate-limited/down Reddit never breaks a page.
- **Blocked-until:** (1) Reddit commercial API approval (apply day one; 2–4 wk), (2) a definitive read of the no-ads clause vs the site's ad monetization (may force: no display ads on feed pages, or no live feed).

## Dependency DAG
```
V1: reddit-seed JSON (hand-curated) → RedditFeed.astro + per-section islands → wire into visit/move/live → ships on GitHub Pages
V2 (gated): Reddit commercial approval + ads-clause ruling → Cloudflare Worker + KV cron + source-adapter flag → flip env var
```

## Alternatives considered
- **Migrate to Cloudflare Pages (Panel A)** vs **keep Pages + standalone Worker (Panel B, chosen for V2)** — don't churn the in-flight deploy.
- **Live-per-request** vs **cron-cache (chosen)** — regional cache misses + CPU cap make live-per-request worse on free tier.
- **Multi-subreddit v1** vs **r/Bermuda-only (chosen v1)** — less complexity/calls.
- **Raw feed** vs **curated (chosen, owner-locked)** — brand safety.

## Risks
- **No-ads clause vs monetization (highest):** if confirmed, the live feed and display ads are mutually exclusive on the same pages. V1 seed sidesteps it (it's not "Reddit API content"). Mitigation: VERIFY the clause before any V2 commitment.
- **Commercial approval may be denied / slow / paid:** V1 ships regardless; V2 is genuinely optional.
- **Seed staleness:** hand-curated → refresh cadence is a chore. Mitigation: low-volume subreddit tolerates monthly; a future cron can automate once access lands.
- **`.json` status unresolved:** doesn't matter — V1 doesn't use it; V2 uses the official OAuth path.

## DoD (V1)
- 3 seed JSON files + `RedditFeed.astro` + per-section wiring + attribution; `npm run build` succeeds; builds on GitHub Pages; tasteful empty/short states. A PR in the Pilot.BM repo (owner merges). V2 documented as a gated follow-up in `docs/`.
