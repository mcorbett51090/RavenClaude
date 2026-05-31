---
description: Scaffold a Microsoft Graph delta-query sync — do one baseline round paging to the @odata.deltaLink, persist that link verbatim, then ride incremental rounds that return only adds/updates/@removed deletes, instead of re-pulling the whole collection on a timer.
argument-hint: "[the resource, e.g. 'keep a local mirror of all users in sync']"
---

# Scaffold a delta sync

You are running `/microsoft-graph:scaffold-delta-sync`. Build the change-tracking sync for what the user described (`$ARGUMENTS`), following this plugin's `graph-api-engineer` discipline — track what changed, don't re-pull the collection.

## When to use this

You need to keep a local view in sync with a Graph collection and can *pull* on an interval. If you must react within seconds or avoid any polling, use `/microsoft-graph:build-change-notifications` (push) instead. Periodic full re-reads to diff client-side are the anti-pattern this command replaces.

## Steps

1. **Run the initial baseline round** — `GET /resource/delta`, drain every `@odata.nextLink`, stop when you receive a `@odata.deltaLink` (`api-delta-for-what-changed.md`). To skip the baseline and get only future changes, use `$deltatoken=latest`.
2. **Persist the entire `@odata.deltaLink` URL verbatim** — the token is opaque and encodes your `$select`/query params; specify those only in the *initial* request, never repeat them on subsequent calls (same file).
3. **Ride incremental rounds** — GET the saved deltaLink; it returns only changes plus a new deltaLink to persist for next time (same file).
4. **Handle `@removed` for deletes** (`reason: changed` = restorable, `deleted` = permanent) and `propertyName@delta` annotations (e.g. `members@delta`) for relationship changes; merge defensively — an item can appear more than once (same file).
5. **Page each round to exhaustion** — a delta page can be empty and *still* carry a nextLink; the baseline ends on deltaLink, not absence of nextLink (`api-page-to-exhaustion.md`).
6. **Mind the resource constraints** — for `user`/`group`, `$expand`/`$top` aren't supported on delta and `$filter` is limited; not every resource supports delta (`api-delta-for-what-changed.md`). This also serves as the backstop for a paused change-notification subscription.

## Guardrails

- Never re-read the whole collection on a timer to find changes — that's the self-inflicted throttling this command exists to prevent.
- Never assume order (delta makes no `$orderby` guarantee) or parse the deltatoken by hand — treat it as opaque.
- Delta-supported resources and per-resource query restrictions are volatile — tag `[verify-at-build]`. This plugin is advisory: emit the SDK/endpoint snippet the engineer runs with their own credentials.
