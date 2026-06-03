# Slack as a data source

> **Last reviewed:** 2026-06-03. Sources: Slack API documentation (api.slack.com) `[unverified — training knowledge; confirm API method names, rate-limit tiers, and scopes at build time]`. Refresh when: (a) Slack changes the `conversations.history` method behavior or pagination model, (b) Slack rate-limit tiers are updated, or (c) the channel-access model changes for Slack Connect / external shared channels.

## Governance stance — the most important thing in this file

**Raw Slack message bodies NEVER land in the warehouse. This is permanent and non-negotiable.**

The decision is recorded in the build plan (§1 Decision C′, §2 Conflict 1 tie-break). Rationale: the PII blast radius of dumping raw Slack channel messages into Snowflake is enormous and permanent. Every analyst, every Sigma viewer, every future connector inherits that exposure. "Mask it downstream" means the sensitive text already lives in RAW and must be governed forever — deletion at scale on Snowflake is expensive and error-prone.

For CS health, the valuable Slack signal is almost entirely derived: message volume trend, escalation-keyword density, mention counts, coarse sentiment, and the presence/absence of a channel (dead channel is itself a churn signal). The literal message text adds near-zero incremental information to a churn tier.

**What lands in the warehouse:** only computed, per-channel signals. The raw extractor computes metrics in-memory and writes only `(account_key, channel_id, signal_date, msg_count, escalation_hits, mention_count, sentiment_score)` — never the message bodies.

## Connector strategy — BUILD (derived-signal extractor)

No managed Fivetran/Airbyte Slack connector is appropriate here, because standard connectors land raw message content. This is a **BUILD** — a Codex-authored Python signal extractor that enforces the governance stance by design: it never writes message bodies to any persistent store.

## Auth and Slack app setup

- **Slack Bot Token (xoxb-)** — OAuth 2.0 app-level token; required scopes:
  - `channels:history` — read message history in public channels (the primary data source)
  - `channels:read` — list channels and metadata
  - `users:read` — resolve user IDs to names (needed for mention-count signal only)
  - For Slack Connect / external channels (customer-shared channels): `groups:history`, `groups:read` may also be needed `[unverified — confirm scope names for private + shared channels]`
- The Slack app must be **manually added to each customer channel** by a workspace admin; the bot cannot join channels autonomously
- Store the bot token in a secrets vault; never in the repo or Codex output

## The `slack_channel_account_map` seed table — required

Slack has no native account concept. There is no API call that returns "channels belonging to Salesforce Account X." The mapping is a human-maintained seed table.

```sql
-- infra/ddl/slack_channel_account_map.sql
create or replace table raw.slack_channel_account_map (
    channel_id        varchar not null primary key,   -- Slack channel ID (e.g., C0123ABC456)
    channel_name      varchar,                         -- human-readable; for display only
    account_name      varchar,                         -- display name; the canonical key is account_key
    account_key       varchar,                         -- FK to dim_account.account_key; NULL = unmapped
    channel_type      varchar,                         -- 'customer_shared' | 'internal_cs' | 'unknown'
    confirmed_by      varchar,                         -- email of the human who confirmed this mapping
    confirmed_at      timestamp,
    added_at          timestamp default current_timestamp,
    notes             varchar
);
```

**Seeding:** seed manually for the top ~20 accounts by ARR before Phase 0 exit. The account team typically knows which channels are active customer channels from the naming convention (`#customer-acme`, `#ext-acme-cs`, `#support-acme-corp`, etc.).

**Weekly diff script:** a Codex-built weekly script lists all channels the bot can see, identifies channels matching the naming convention that are NOT yet in the map, and posts proposed new mappings to an internal ops channel for human confirmation. This keeps the map current without requiring a human to remember to update it.

```python
# Weekly diff script shape — posts unmapped candidates for human confirmation
# Never auto-inserts; always routes to human review
new_channels = slack_client.list_channels()
unmapped = [c for c in new_channels if c['id'] not in existing_map_ids
            and looks_like_customer_channel(c['name'])]
if unmapped:
    slack_client.post_to_ops_channel(
        message=f"{len(unmapped)} new channels may be customer channels — please confirm:\n"
                + format_candidates(unmapped)
    )
```

## Signal extraction — what the extractor computes

The extractor pages `conversations.history` for each mapped channel, computes signals in memory, and writes only the aggregate row. It never writes individual messages.

| Signal | Computation | CS-health interpretation |
|---|---|---|
| `msg_count` | Total messages in the period (per-channel, per-day) | Volume trend; spike may indicate escalation or active engagement |
| `escalation_hits` | Count of messages matching escalation-keyword list (configurable; e.g., "down", "broken", "urgent", "outage", "frustrated") | Escalation density; a proxy for unresolved issues |
| `mention_count` | Count of `@here`, `@channel`, and internal-team user mentions | High mention rate = urgency signaling |
| `sentiment_score` | Coarse positive/negative/neutral classification using a local model or keyword heuristic (NOT an external API call — message bodies must not leave the extractor process) | Coarse directional signal; not a substitute for NPS |
| **absence signal** | Channel has 0 messages for N consecutive days | A dead customer channel is itself a churn signal |

**Sentiment implementation note:** use a local, offline model (e.g., a rule-based keyword classifier or a small local embedding model) or a Snowflake Cortex function applied in-warehouse to a pre-computed feature vector — never send raw message bodies to an external API. The governance stance applies to every egress path, not just Snowflake.

## API method — `conversations.history`

- **Method:** `conversations.history` `[unverified — confirm method name and parameter names in current Slack API docs]`
- **Pagination:** cursor-based (`next_cursor` in response metadata); page through until `has_more = false`
- **Watermark:** use `oldest` (Unix timestamp) parameter to pull only messages since the last sync
- **Rate limits:** Slack uses a tier system; `conversations.history` is typically **Tier 3 (50+ calls/minute)** `[unverified — verify current Slack API rate-limit tiers at api.slack.com/docs/rate-limits]`
- Apply exponential backoff on `429` responses; honor `Retry-After` header

```python
# Extractor pseudocode shape — Codex fills in the real implementation
for channel_id, account_key in channel_account_map.items():
    messages = []
    cursor = None
    while True:
        response = slack_client.conversations_history(
            channel=channel_id,
            oldest=watermark.read(channel_id),   # Unix timestamp
            cursor=cursor,
            limit=200,
        )
        messages.extend(response['messages'])
        cursor = response.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            break

    # Compute signals IN MEMORY — never write messages
    signals = compute_signals(messages, account_key, channel_id)
    upsert.merge(
        table='raw.slack_channel_signals',
        records=[signals],
        primary_key=('channel_id', 'signal_date'),
    )
    watermark.advance(channel_id, current_run_at)
    # messages variable goes out of scope — never persisted
```

## The absence signal — dead channels as churn data

A Slack channel that has gone silent is data. A customer who used to have an active `#customer-acme` channel and has not posted in 30 days may be disengaged. The CS-health mart should surface this explicitly:

- `slack_last_message_date` — the date of the most recent message in the mapped channel
- `slack_channel_days_silent` — `current_date - slack_last_message_date`
- Include this in the `slack_escalation_signal` derived tier: a channel silent for >30 days for a non-new account = Yellow or Red contribution

The absence signal catches a pattern that all other positive signals miss: the disengaged customer who never escalates because they've already stopped using the product.

## dbt modeling — raw signal table + mart integration

```sql
-- raw.slack_channel_signals lands from the extractor
-- One row per (channel_id, signal_date)
create or replace table raw.slack_channel_signals (
    channel_id        varchar not null,
    account_key       varchar,                   -- FK via slack_channel_account_map
    signal_date       date not null,
    msg_count         integer,
    escalation_hits   integer,
    mention_count     integer,
    sentiment_score   float,                     -- null if not computable
    extracted_at      timestamp default current_timestamp,
    primary key (channel_id, signal_date)
);
```

| Model | Purpose |
|---|---|
| `stg_slack__channel_signals` | Typed, 1:1 with raw; joins to `slack_channel_account_map` to add `account_key` |
| `int_slack__account_signals` | Aggregate from channel → account grain (one account may have multiple channels; sum/average as appropriate) |
| `fct_account_health_snapshot` | Mart — contributes `slack_message_volume_7d`, `slack_escalation_signals_7d`, `slack_escalation_signal` sub-indicator |

## Governance and compliance checklist

- [ ] No raw message bodies in any Snowflake table, ever — the extractor is the only enforcement point
- [ ] `slack_channel_account_map` is human-confirmed, not auto-generated from naming heuristics
- [ ] Sentiment computation is offline — no message bodies sent to external APIs
- [ ] Slack workspace admin has confirmed that mining customer-shared channels is legally and contractually permissible for this engagement (Open Question #2 from the build plan)
- [ ] Bot token stored in vault; rotation plan documented
- [ ] Retention policy for `slack_channel_signals` aligns with the engagement's compliance regime

## Common gotchas

1. **Bot not in the channel** — `conversations.history` returns `not_in_channel` error if the bot hasn't been added. The weekly diff script's unmapped-channel alert will surface this for new channels, but pre-existing channels require a workspace admin to `/invite` the bot.
2. **Slack Connect channels (external shared channels)** — channels shared with external organizations (`#ext-*`) may require different scopes and have different privacy implications. Confirm the workspace admin's intent before adding the bot.
3. **Channel naming convention drift** — the mapping heuristic assumes a naming convention; if the team creates `#acme-support` instead of `#customer-acme`, the diff script won't surface it. Review the mapping monthly during Phase 1.
4. **Message threading** — threaded replies may be returned or excluded depending on `inclusive` parameter and API version `[unverified — confirm threading behavior in current Slack API]`. Decide whether to include thread messages in the signal count.
5. **Rate limits on large workspaces** — if there are 200+ active customer channels, the nightly signal extraction may take significant time. Implement channel-level parallelism within rate-limit budget.
6. **Absence vs. archived** — a channel with zero messages may be newly created (pre-launch) or archived. Check `is_archived` on the channel object before flagging a channel as a churn signal.

## Refresh triggers

- Slack changes the `conversations.history` method signature or rate-limit tiers
- Slack Connect behavior for shared channels changes
- Escalation keyword list needs tuning after Phase 1 calibration
- New naming conventions adopted by the team that the diff script doesn't cover
