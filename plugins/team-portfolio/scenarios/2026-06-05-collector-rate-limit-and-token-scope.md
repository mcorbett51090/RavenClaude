---
scenario_id: 2026-06-05-collector-rate-limit-and-token-scope
contributed_at: 2026-06-05
plugin: team-portfolio
product: collector
product_version: "n/a"
scope: likely-general
tags: [rate-limit, token-scope, 403, fine-grained-pat, private-repo]
confidence: medium
---

## Problem

The nightly collector started producing reports where the **first few repos in `team-portfolio.json` looked normal but every repo near the bottom of the list showed zero events** — and two private repos that had always reported now showed nothing. The `weekly-tracker.md` carried no obvious crash. The operator's worry was the usual wrong one ("did three teams stop working at once?"), when the real story was two *different* mechanical failures stacked on top of each other: a rate-limit exhaustion and a token-scope gap.

## Context

- ~12 repos tracked (mix of public + private), collection running from a GitHub Action.
- A new contributor's onboarding had added 4 repos to `repos[]` in one batch, roughly doubling the per-run API call volume.
- The token in `PORTFOLIO_TOKEN` was a **fine-grained PAT**; the two newly-failing private repos had been transferred into a different org during a reorg and were never added to the PAT's repository-access list.

## Attempts

- Tried: read `portfolio-activity.json` `errors[]` first (the diagnostic the reports under-surface — CLAUDE.md §5, and the report only prints a banner when `authenticated` is false or `errors[]` is non-empty). Found **two distinct error classes**: several `HTTP 403 (rate limit exceeded)` on the tail repos, and `HTTP 403 (Forbidden)` on the two transferred private repos. Outcome: the two failures look identical at a glance (both `403`) but have different causes and different fixes — this is the trap.
- Tried: distinguished them by the response, not the status code. A rate-limit `403` carries `x-ratelimit-remaining: 0` and an `x-ratelimit-reset` epoch [verify-at-use — header names per GitHub REST docs]; a scope `403` does not — it is a permissions denial. The collector's `_respect_rate_limit()` already pauses when `x-ratelimit-remaining <= 1`, but only **between paginated pages within one repo** — it does not re-budget the *whole run* across 12 repos, so a doubled repo list can still exhaust the hourly budget mid-run. Outcome: the tail-zero pattern is rate-limit; the two-private-repos-zero pattern is scope.
- Tried (rate-limit fix): confirmed the run was actually authenticated (`authenticated: true` in the artifact) — an **unauthenticated** run is capped far lower (60 requests/hour [verify-at-use — GitHub REST primary rate limit]) versus 5,000/hour authenticated [verify-at-use], so the first question is always "did the token resolve?" It had. The exhaustion was real volume, so we (a) confirmed the cron interval and `window_days` weren't double-counting, and (b) accepted that 12 repos × 3 endpoints × pagination is near the per-run ceiling and split the busiest repos' lookback shorter. Did NOT add a second token or raise `MAX_PAGES` — that masks the signal.
- Tried (scope fix): added the two transferred repos to the fine-grained PAT's repository-access list (least privilege, read-only — CLAUDE.md §4 #3), re-ran, confirmed both reappeared and `errors[]` was empty.

## Resolution

Two `403`s, two causes, two fixes — **never treat `403` as one thing**. A rate-limit `403` (tail repos zero, `x-ratelimit-remaining: 0`) is solved by reducing per-run volume or confirming authentication, *not* by adding token scope; a permissions `403` (specific repos zero, no rate-limit headers) is solved by granting the token access to exactly those repos, *not* by slowing the run.

**Action for the next operator:** read `errors[]`, then **split the `403`s by whether `x-ratelimit-remaining` is `0`**. Traverse [`../knowledge/team-portfolio-decision-trees.md`](../knowledge/team-portfolio-decision-trees.md) "Collection Problem — Diagnose Why Counts Are Wrong": a `403` access-denied routes to the token-scope leaf, a rate-limit hit routes to the authentication/cadence leaf. For token *type* selection on a new repo, see the "Token provisioning" tree (built-in `GITHUB_TOKEN` only reaches the workflow's own repo and public repos — private cross-org repos need a fine-grained PAT scoped to them). Confirm the run was authenticated before blaming volume: an unauthenticated run is the more common root cause of "everything near the bottom went to zero," and the report's unauthenticated banner is the tell — see [`../best-practices/unauthenticated-runs-produce-incomplete-counts-say-so.md`](../best-practices/unauthenticated-runs-produce-incomplete-counts-say-so.md) and [`../best-practices/rotate-portfolio-token-on-team-member-departure.md`](../best-practices/rotate-portfolio-token-on-team-member-departure.md).
