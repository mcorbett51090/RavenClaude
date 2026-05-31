---
description: Build a resilient Microsoft Graph call — $select only what you need, filter server-side, page @odata.nextLink to exhaustion, $batch independent calls, and honor 429/Retry-After with backoff — via the SDK, not hand-rolled HTTP.
argument-hint: "[the operation, e.g. 'list all disabled users with their mail']"
---

# Build a Graph call

You are running `/microsoft-graph:build-graph-call`. Build the Graph query/call for what the user described (`$ARGUMENTS`), following this plugin's `graph-api-engineer` discipline — shape the query, page to exhaustion, batch the round-trips, and survive throttling.

## When to use this

You're writing or reviewing a Graph API read/write. If the question is "which permission / delegated or app," run `/microsoft-graph:design-graph-auth` first. If the need is "what changed since last time," use `/microsoft-graph:scaffold-delta-sync` instead of polling.

## Steps

1. **`$select` the explicit, minimal property list** on every collection read — never `GET` a collection bare (it over-fetches, and on directory objects the field you need is silently absent until selected) (`api-select-only-what-you-need.md`).
2. **Push predicates server-side** with `$filter`/`$search`; never page a whole collection to filter three rows in app code (same file).
3. **Page `@odata.nextLink` to exhaustion** — a first page is not "all results"; use the nextLink URL verbatim and re-send custom headers each page (`api-page-to-exhaustion.md`).
4. **`$batch` independent calls** (up to 20) to cut round-trips — correlate responses by `id` and inspect *each* sub-response's status; a 200 envelope says nothing about the parts (`api-batch-to-cut-round-trips.md`).
5. **Honor throttling as a contract** — on 429/503 wait the `Retry-After` value verbatim, else exponential backoff with jitter; remember batched sub-requests are not auto-retried (`api-honor-throttling-and-retry-after.md`).
6. **Use the SDK, not raw HTTP** — its `PageIterator`, retry handler, and MSAL token attachment ship the resilience for free; raw HTTP is the justified exception (`api-use-the-sdk-not-raw-http-for-resilience.md`).

## Guardrails

- Never read `value` once and assume completeness, parse out `$skiptoken` by hand, or retry a 429 immediately (the failed call still accrues against the limit).
- Never ship a `/beta` endpoint to production without flagging it; quote throttling limits / permission names with a retrieval date and tag volatile facts `[verify-at-build]`.
- This plugin is advisory: emit the SDK snippet + endpoint the engineer runs with their own credentials. Permission scope / consent design routes to `graph-identity-engineer` and the verdict to `ravenclaude-core/security-reviewer`.
