---
name: front-integration
description: "Front (multi-channel inbox) support-ticket ingestion. Hierarchical tags via `parent_tag_id` — useful for theme taxonomy out of the box. Multi-channel (email + SMS + WhatsApp + Twitter etc.) means **channel must be carried into aging buckets** (response targets vary by channel). Two-tier rate limit: global (plan-dependent, ~50/min entry) + burst (≤5 req/sec, exports capped at 1/sec). Always follow `_pagination.next` — never trust result counts. Tags API now paginated."
last_reviewed: 2026-06-04
confidence: medium
---

# Front integration

> **Last reviewed:** 2026-06-04. Sources: Front Help (rate limit), Front Developer Docs (rate limits, pagination), Rollout's Front API essential guide, Hightouch destinations list. Refresh when: (a) the two-tier rate-limit shape changes, (b) Front publishes a first-class SLA payload, (c) the multi-channel set changes materially (new channel types affect aging-bucket dimensions), or (d) the hierarchical-tag model is replaced.

## Connector strategy — VERIFY first, then BUY or BUILD

- **Fivetran** — directory lists Front (general directory entry) — connector availability confirmed at a directory level only. **`[verify-at-use — 2026-06-04]` — verify against Fivetran's Front connector page before promising features.**
- **Airbyte** — Front source connector availability not enumerated at last check; verify.
- **Hightouch** — Front available as a destination per Hightouch destinations list. `[verify-at-use — 2026-06-04]`
- **Planhat** — Front integration not enumerated at last check; verify.

**Practical path:** for a multi-vendor conformed-model build, a thin custom Front puller is well-shaped — Front's `/conversations` endpoint with `q[after]=<epoch_seconds>` watermark + cursor pagination is straightforward to engineer.

## API extraction pattern

### Endpoint + watermark

- **Endpoint:** `GET /conversations` (or `/inboxes/{id}/conversations` for per-inbox).
- **Watermark:** `q[after]=<epoch_seconds>`.
- **Tags API** is **paginated** — no longer one-shot. Older integrations that fetched all tags in one call miss data. `[verify-at-use — 2026-06-04]`

### Pagination

- **Cursor via `page_token` query param.**
- Response includes `_pagination` object with `next` URL.
- **`limit` query param max = 100.** `[verify-at-use — 2026-06-04]`
- **Discipline:** **always use the `next` link, never trust result counts.** Front's docs are emphatic on this. `[verify-at-use — 2026-06-04]`

### Two-tier rate limits (the key gotcha)

Front enforces **two independent limits** — code retry against both.

| Tier | Limit | Notes |
|---|---|---|
| **Global** | combined across all endpoints, plan-dependent | starts at **~50 req/min** on entry plans `[verify-at-use — 2026-06-04]` |
| **Burst** | **≤5 req/sec per resource type** | `[verify-at-use — 2026-06-04]` |
| **Export endpoints (burst sub-tier)** | **1 req/sec** | `[verify-at-use — 2026-06-04]` |

**Headers to adapt against:** `X-RateLimit-*` series. **A spiky import can hit burst without touching the global** — retry logic must cover both failure modes.

## Schema shape — entity → conformed-field map

| Conformed concept | Front entity | Key fields |
|---|---|---|
| Ticket (= conversation) | `conversations` | `id`, `subject`, `status` (assigned / unassigned / archived / deleted), `assignee.id`, `recipient`, `tags[]`, **`inboxes[]`** (multi-inbox), `created_at`, `is_private`, `links[]` (external linkages) |
| Conversation event | `messages` (sub-resource on conversation) | `id`, `type` (email / sms / custom), **`is_inbound`**, `created_at`, `author.id`, `body` |
| User | `teammates` (agents) + `contacts` (end-users) | `id`, `email`, `handles[]` |
| Tag dictionary | account-scoped, **hierarchical** | `id`, `name`, **`parent_tag_id`** (Front tags are a tree) |
| Channel | `inboxes` — first-class | `id`, `type` (email / sms / whatsapp / twitter / messenger / custom), `name` |
| SLA | **rule-driven** — surfaced via tag application + `metrics` | per-team |

## The multi-channel surface (carry channel into aging)

Front's distinguishing feature is **multi-channel inboxes** — email, SMS, WhatsApp, Twitter, Messenger, custom. **Response targets typically vary by channel** (an SMS reply expected in minutes; an email reply in hours).

**Warehouse implication:** the conformed `channel` enum on `fct_ticket` is **non-negotiable** for Front-driven dashboards. Aging buckets and SLA-derivation must group by channel, not collapse it.

Channel comes from the `inbox.type` of the inbox the conversation lives in. For multi-inbox conversations, pick the primary (or first) inbox's type — and **note the multi-inbox dedup risk** below.

## Hierarchical tags — a theme-taxonomy gift

**Front tags are hierarchical** — `Billing > Refunds > Disputed`. **This is a major schema advantage** for theme normalization:

- Persist `parent_tag_id` and you get a **free taxonomy** — no alias-map needed.
- The `dim_tag` table is naturally a tree; walk it for theme rollup.
- Front tag display already shows the path (`"Billing > Refunds"`) — preserve that hierarchy.

Contrast with Zendesk/Freshdesk/Help Scout (flat tags requiring alias-map + theme-rollup logic). `[verify-at-use — 2026-06-04]`

## Ticket-aging derivation

- `created_at` → first outbound message (`messages[i].is_inbound = false`) = **first response**.
- **Carry channel into aging buckets** — never collapse.
- Status transitions to derive resolution: `assigned` / `archived` semantics differ from "closed" — clarify with the tenant which state is "resolved" for SLA purposes.

## SLA-breach detection

Front's SLA implementation is **rules-based** — breach signals come through:

- **Tag application** (e.g., auto-applied `sla-breached` tag).
- **Rule-fire events**.

There is **no single SLA payload endpoint** comparable to JSM's `/sla`. `[verify-at-use — 2026-06-04]` — Front convention; verify per tenant.

**Pattern:** detect the `sla-breached`-class tag (tenant-configured); cross-reference with rule-fire audit if available.

## Themes / tags & escalation

- Themes — use the **hierarchical tag tree** directly.
- **Escalation:** tag application (e.g., `escalated`), assignee change to escalation team, or status reset from `archived` to `assigned`.

## Linking to SFDC Account / Planhat Company

`contacts.handles[]` (emails, phone numbers, social handles) → match-back to SFDC `Contact` → `Account`. Front contacts can carry custom fields; **the durable path is to populate `contacts.custom_fields.sfdc_account_id`** via your Salesforce↔Front integration.

Precedence:

1. `contacts.custom_fields.sfdc_account_id` → `match_method='external_id'`, confidence 1.0
2. `contacts.handles[]` email → domain → SFDC `Account.Website` → `match_method='email_domain'`, confidence 0.8
3. Manual override.

## Common gotchas

1. **Two rate limits, two failure modes.** A spiky import can hit burst without touching the global. Code retry against both. `[verify-at-use — 2026-06-04]`
2. **Don't trust result counts; follow `next`.** Front's pagination docs are emphatic. `[verify-at-use — 2026-06-04]`
3. **Multi-inbox conversations** — a single conversation can live in multiple inboxes. If you fan out aging per inbox, you'll **double-count**. **Key on `conversations.id`** and treat `inboxes[]` as a many-to-many join.
4. **Tags-API pagination changed** — older integrations that fetched all tags in one call now miss data. Refresh the loader if it predates the change. `[verify-at-use — 2026-06-04]`
5. **Exports at 1 req/sec.** For very high volumes, the listing endpoints with pagination are faster than the export endpoint despite the apparent batch advantage.
6. **Channel matters for SLA.** SMS and email have different target-response expectations — never aggregate aging across channels without a channel breakdown.

## Recommended sync configuration

- **Cadence:** every 1–2 hours for conversations; daily for tags / teammates / inboxes / contacts.
- **Backfill:** 12+ months for resolution-time distributions per channel.
- **Pagination:** follow `_pagination.next` strictly; `limit=100` max.
- **Channel dimension:** materialize `dim_channel(inbox_id, channel_type)` and carry into every aging/SLA query.
- **Tag hierarchy:** materialize `dim_tag` as a tree (`tag_id`, `parent_tag_id`, `tag_path`).

## Refresh triggers

- Two-tier rate-limit shape changes.
- Front publishes a first-class SLA payload endpoint.
- New channel types added that affect aging-bucket dimensions.
- Hierarchical tag model replaced.
- Fivetran/Airbyte connector certification status changes meaningfully.

## References

All URLs accessed 2026-06-04.

- https://help.front.com/en/articles/2438 — Front's API rate limit (customer-facing)
- https://dev.frontapp.com/docs/rate-limiting — Rate limits (developer docs)
- https://dev.frontapp.com/docs/pagination — Pagination (`page_token`, `_pagination.next`)
- https://rollout.com/integration-guides/front/api-essentials — Front API essential guide
- https://hightouch.com/docs/destinations/overview — Hightouch destinations
