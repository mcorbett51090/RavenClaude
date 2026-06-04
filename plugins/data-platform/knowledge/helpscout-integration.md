---
name: helpscout-integration
description: "Help Scout (Mailbox API / Inbox API 2.0) support-ticket ingestion. Lightweight SMB-positioned vendor — **no first-class SLA object** (build your own targets per mailbox/tag). Rate-limit docs disagree (200 vs 400 req/min — preserved discrepancy below); writes count double. List Conversations page size is **25**, not the default 50. Account-scoped tags + inbox-scoped custom fields (a key normalization split)."
last_reviewed: 2026-06-04
confidence: medium
---

# Help Scout integration

> **Last reviewed:** 2026-06-04. Sources: Help Scout Developer Docs (Mailbox / Inbox API 2.0 — list, pagination, rate-limiting, custom fields), Help Scout's own customer-facing tags + custom-fields blog, Fivetran directory. Refresh when: (a) Help Scout publishes a first-class SLA object (would change the whole derivation pattern), (b) the 200-vs-400 req/min docs discrepancy resolves to a single canonical number, (c) page-size defaults change, or (d) tags transitions to inbox-scoped (currently account-scoped).

## Connector strategy — BUY (where supported) or BUILD

- **Fivetran** — Help Scout appears in the directory (Help Scout ↔ HubSpot / Intercom warehouse joins). Connector exists at directory level. `[verify-at-use — 2026-06-04]`
- **Airbyte** — source connector exists in the catalog but certification depth wasn't deeply verified at last check. **Verify status/certification before relying on it.**
- **Hightouch** — not enumerated as a first-party Help Scout destination at last check; verify.
- **Planhat** — Help Scout integration not enumerated at last check; verify against Planhat's integration catalog.

**Build verdict:** for an estate where Help Scout is the only support tool and Fivetran's connector covers conversations + threads + customers, BUY. For a multi-vendor conformed-model build, a thin custom puller is straightforward (the Mailbox API is well-shaped and well-paginated) and avoids waiting on connector certification.

## API extraction pattern

### Endpoint + watermark

- **Endpoint:** `GET /v2/conversations` with `modifiedSince=<ISO8601>` watermark.
- **Filters:** `mailbox`, `folder`, `status`, `tag`, `assigned_to`, `number`, `customFieldsByIds`. `[verify-at-use — 2026-06-04]`

### Pagination

| Endpoint | Default page size | Notes |
|---|---|---|
| **List Conversations** | **25 items per page** | the surprise — not 50 |
| Other list endpoints | 50 items per page | `[verify-at-use — 2026-06-04]` |

Response includes `_links` (`self`, `next`, `previous`, `first`, `last`) for navigation. **Follow `_links.next`** — don't compute page numbers.

### Rate limits — the docs discrepancy

**Two numbers in circulation. Preserve the discrepancy until you can confirm against the live customer account.**

| Source | Number | Notes |
|---|---|---|
| Official docs (`X-RateLimit-Limit-minute` header) | **200 req/min** | `[verify-at-use — 2026-06-04]` |
| Community libraries + third-party integration guides | **400 req/min total** | **writes count double** (so effective: 400 reads, or 200 writes, or a mix). `[verify-at-use — 2026-06-04]` |

**Working resolution:** treat **200 req/min as the safe ceiling per resource type** and back off on 429. The actual account-level allowance varies by plan tier and the docs lag the implementation. **Do not hard-code 400.**

### Side-loading

- Mailbox API uses `embed=` for hierarchical responses — e.g., `embed=threads` on a conversation fetches the message threads inline. **Critical for first-response derivation** (avoids N+1 calls per conversation).

## Schema shape — entity → conformed-field map

| Conformed concept | Help Scout entity | Key fields |
|---|---|---|
| Ticket (= conversation) | `conversations` | `id`, `number`, `threads[]`, `type`, `folderId`, `status` (active/pending/closed/spam), `state`, `subject`, `preview`, `mailboxId`, `assignee{}`, `createdBy{}`, `createdAt`, `closedAt`, `closedBy`, `customerWaitingSince{}`, `tags[]`, `customFields[]` |
| Conversation event | `threads` (sub-resource) | `id`, `type` (customer / message / note / etc.), `body`, `createdAt`, `createdBy` |
| User | `users` (agents) + `customers` (end-users) | `id`, `firstName`, `lastName`, `email`, `organization` |
| Tag dictionary | account-scoped, paginated | `id`, `name`, `color` |
| Custom fields | **inbox-scoped** (NOT account-scoped) | `id`, `name`, `value` |
| SLA | **not first-class — derive per-mailbox / per-tag** | — |

**Critical normalization split:** **tags are account-scoped** (track across mailboxes — ideal for cross-inbox theme rollup); **custom fields are inbox-scoped** (different inboxes can carry different custom-field schemas). Persist the inbox/custom-field relationship as a dimension. `[verify-at-use — 2026-06-04]`

## Ticket-aging derivation

- `createdAt` → `closedAt` = total resolution.
- **First-response:** first `thread` where `type='message'` and `createdBy.type='user'` (agent reply), minus `createdAt`. Pull threads via `embed=threads`.
- **`customerWaitingSince`** is a useful pre-computed "time since last agent action," good for the "awaiting agent" aging bucket.

## SLA-breach detection — the build-your-own callout

> **No first-class SLA object in Help Scout.**
>
> Help Scout is intentionally simpler here — positioned for SMB and lighter than Zendesk/JSM/SFDC. **Derive SLA in the warehouse:**
> - Define your own targets per `mailboxId` / `tag` policy in a `dim_sla_target` table.
> - Compute `breach = (now > createdAt + target_first_response_hours) AND (first_response_at IS NULL)`.
> - Compute the resolution-side analogue against `target_resolution_hours`.

`[verify-at-use — 2026-06-04]` — no contradicting source; Help Scout's positioning makes a future first-class SLA object unlikely.

## Themes / tags & escalation

- **Tags account-scoped** → ideal for cross-inbox theme rollup.
- **Tags require a separate paginated call** — the Tags API switched from single-response to paginated. Older integrations that fetched all tags in one call now miss data. `[verify-at-use — 2026-06-04]`
- **Escalation:** no flag. Derive from `assignee` change to an escalation user/team, status flip, or tag like `escalated`.

## Linking to SFDC Account / Planhat Company

Bridge candidates (in precedence order):

1. **Help Scout customer custom field populated with SFDC `Account.Id`** via your integration that creates the customer → `match_method='external_id'`, confidence 1.0
2. **`customers.email` → domain → SFDC `Account.Website`** → `match_method='email_domain'`, confidence 0.8
3. **`customers.organization`** (free-text, fragile) → SFDC `Account.Name` → stewardship review only.

## Common gotchas

1. **The list-conversations page size is 25, not 50.** Throughput-estimation surprise — easy to plan a sweep that takes 2× as long as expected. `[verify-at-use — 2026-06-04]`
2. **Tags require a separate paginated call.** The Tags API switched from single-response to paginated. Update old integrations or you miss data. `[verify-at-use — 2026-06-04]`
3. **No SLA semantics.** Build your own targets per `mailboxId`/`tag` and compute breach in dbt.
4. **Write requests count double** toward the rate limit (per community guidance). `[verify-at-use — 2026-06-04]`
5. **Account-scoped tags + inbox-scoped custom fields** — two scopes, two normalization patterns. Don't conflate them in the dimension model.
6. **`customers.organization` is free-text.** Never trust it for auto-bridging to SFDC.

## Recommended sync configuration

- **Cadence:** every 1–2 hours for conversations; daily for tags / users / mailboxes / customers.
- **Backfill:** 12+ months for resolution-time distributions and tag-theme rollups.
- **Incremental cursor:** `modifiedSince` on conversations; `_links.next` for pagination.
- **`embed=threads`:** mandatory on conversation fetches for first-response derivation.
- **Rate-limit headroom:** plan against 200 req/min per resource type; back off on 429 regardless of what the community guide claims.

## Refresh triggers

- Help Scout publishes a first-class SLA object (would obsolete the build-your-own derivation).
- 200-vs-400 req/min docs discrepancy resolves.
- Page-size defaults change.
- Tags become inbox-scoped (would break account-scoped theme rollups).
- A canonical dbt package for Help Scout emerges.

## References

All URLs accessed 2026-06-04.

- https://developer.helpscout.com/mailbox-api/endpoints/conversations/list/ — List Conversations
- https://developer.helpscout.com/mailbox-api/ — Inbox API 2.0 overview
- https://developer.helpscout.com/mailbox-api/overview/rate-limiting/ — Rate limiting (200 req/min docs)
- https://developer.helpscout.com/mailbox-api/overview/pagination/ — Pagination
- https://docs.helpscout.com/article/593-custom-fields — Custom fields (inbox-scoped)
- https://articles.helpscout.com/blog/help-scout-tags-custom-fields/ — Tags vs custom fields (account vs inbox scope)
- https://fivetran.com/directory/help-scout/hubspot — Fivetran directory entry
- https://fivetran.com/directory/help-scout/intercom — Fivetran directory entry
