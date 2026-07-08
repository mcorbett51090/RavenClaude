# Event schema spec — `<Object Action>`

> The detailed schema for a single event, referenced from the [`tracking-plan.md`](tracking-plan.md) row. Use for complex/revenue/PII-bearing events where the one-line plan row isn't enough. This is what the CI schema-validation gate checks against.

**Event name:** `<Object Action>` (object-action, plan case) · **Owner:** <name> · **Version:** <1> · **Status:** draft / approved / instrumented / validated

## When it fires

- **Trigger:** <the exact user/system action that fires this event>
- **Fires on:** <client-side / server-side — and WHY (e.g. "server-side: revenue event, must survive ITP/ad-blockers")>
- **Fires once per:** <de-dup boundary — e.g. "per successful charge; idempotency key = charge_id">

## Properties

| Property | Type | Required | Enum / format | Example | Notes |
|---|---|---|---|---|---|
| <plan> | string | ✅ | <enum: free\|pro\|enterprise> | `pro` | <the subscription tier> |
| <mrr> | number | ✅ | <positive, USD cents> | `4900` | <monthly recurring revenue> |
| <source> | string | ⬜ | <enum: web\|ios\|android> | `web` | <origin surface> |

> Every property is typed and consistent with the plan's property-naming convention. No untyped / free-text properties.

## Identity

- **Identity call fired with this event:** <Identify(userId, traits) / alias / Group / none>
- **anonymousId ↔ userId:** <how this event stitches — e.g. "alias(anonymousId → userId) fires here on signup">

## Privacy

- **PII flags:** <none / lists any PII property — should normally be NONE; PII belongs in Identify traits>
- **Consent category:** <analytics / marketing / functional>
- **Lawful basis (if any PII/marketing):** <consent / legitimate interest / contract>
- **Consent gating:** <which Consent Mode v2 signal / TCF purpose / GPC handling gates this event at the source>

## Destinations

- **Routes to:** <warehouse · ad platforms · tools>
- **Delivery mode:** <server-side/cloud-mode where accuracy matters · device-mode>
- **Reverse ETL:** <N/A · or the warehouse audience/trait this feeds via Hightouch / Census>

## Validation & QA

- **CI schema check:** <JSON Schema / Segment Protocols / typed-library type that fails a PR on a mismatch>
- **Stream QA:** <debugger confirmation · schema diff vs this spec · dedup check> — result: <pending / pass>

## Change log

| Version | Date | Change | By |
|---|---|---|---|
| 1 | <YYYY-MM-DD> | initial | <name> |
