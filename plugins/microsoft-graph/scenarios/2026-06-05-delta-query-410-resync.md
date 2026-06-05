---
scenario_id: 2026-06-05-delta-query-410-resync
contributed_at: 2026-06-05
plugin: microsoft-graph
product: graph-api
product_version: "v1.0"
scope: likely-general
tags: [delta-query, paging, deltatoken, 410-gone, resync]
confidence: medium
reviewed: false
---

## Problem

A user-provisioning connector kept a local mirror of the tenant directory using a delta query, persisting the `@odata.deltaLink` between runs and reading only changes each cycle. After the connector was paused for a long maintenance window (well over a week), the next run failed: the stored deltaLink returned `410 Gone`. The connector's error handler treated any non-200 as fatal and alerted on-call, who assumed data loss. There was none — `410` on a delta query is a documented "you must resync" signal, not an error to page a human over.

## Constraints context

- Directory objects (`/users` delta). Delta **tokens for directory objects are valid for ~7 days** `[verify-at-use]`; the maintenance pause exceeded that, so the token aged out.
- The connector persisted the deltaLink but had no "if 410, restart from a full sync" branch — it only handled `@odata.nextLink` (paging) and a terminal `@odata.deltaLink` (steady state).
- The local mirror had also accumulated local edits, so a naive "delete everything and re-pull" would have lost un-synced local state.

## Attempts

- Tried: retrying the stored deltaLink with backoff (the generic 5xx/429 retry path). Failed — `410 Gone` is permanent for that token; retrying the same expired token will always 410. The retry loop just delayed the real fix.
- Tried: treating 410 as fatal and alerting. Wrong response — 410 on delta is expected after a long gap or a server-side `syncStateNotFound`/maintenance event, and the response includes a **`Location` header with a fresh delta URL (empty `$deltatoken`)** to restart enumeration from scratch.
- Tried (worked): added a `410` branch — on 410, follow the `Location` header (or re-issue the base delta request) to do a **full re-enumeration**, page it to exhaustion, then **reconcile** the returned set against the local mirror per the documented resync semantics: for `resyncChangesApplyDifferences`, replace local items with the server version (including deletes) and re-upload known local changes; for `resyncChangesUploadDifferences`, upload local items the server didn't return and keep both copies when unsure.

## Resolution

`410 Gone` on a delta query is a **resync instruction, not a failure** — it means "this token is too old / server state moved; start a fresh full enumeration from the `Location` URL and reconcile." Delta tokens expire (directory objects ~7 days; Outlook entities have a cache-size-bound, non-fixed limit; an expired Outlook token surfaces as a 40x with `syncStateNotFound`) `[verify-at-use]`, so any long-lived delta consumer **must** have a resync branch. The reconcile step (apply-differences vs upload-differences) is what preserves local edits instead of clobbering them.

**Action for the next engineer:** any delta-based mirror needs three branches, not two — `@odata.nextLink` (keep paging), `@odata.deltaLink` (steady state, persist it), and **`410 Gone` (resync: follow `Location`, full enumerate, reconcile)**. Treating 410 as fatal is the bug. Also build for **replays** (the same change can appear twice) and **eventual-consistency delays** (a just-made change may not appear immediately; retry the link later).

**Sources (retrieved 2026-06-05):**
- Use delta query to track changes — Limitations: synchronization reset (410 Gone), token duration — https://learn.microsoft.com/graph/delta-query-overview#limitations
- driveItem: delta — resyncChangesApplyDifferences / resyncChangesUploadDifferences semantics — https://learn.microsoft.com/graph/api/driveitem-delta?view=graph-rest-1.0

Token-duration numbers are volatile and resource-specific — `[verify-at-use]`. Cross-reference: [`../best-practices/api-delta-for-what-changed.md`](../best-practices/api-delta-for-what-changed.md), [`../best-practices/api-page-to-exhaustion.md`](../best-practices/api-page-to-exhaustion.md), the [`delta-query-and-change-notifications`](../skills/delta-query-and-change-notifications/SKILL.md) skill, and [`workloads-notifications-decision-trees.md`](../knowledge/workloads-notifications-decision-trees.md).
