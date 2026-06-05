# State the billing model before recommending a metered Graph API — PAYG is a cost decision, not a config detail

**Status:** Absolute rule
**Domain:** Microsoft Graph / cost and licensing
**Applies to:** `microsoft-graph`

---

## Why this exists

Some Microsoft Graph APIs are **metered** — they bill the Azure subscription associated with the app registration per API call, above any included license entitlement. Examples include Graph connectors capacity, Teams Export (meeting transcripts), and certain Identity Protection APIs. An engineer who recommends these APIs without surfacing the billing model creates an architecture that silently accumulates Azure charges the consumer did not budget for. The CLAUDE.md house opinion is explicit: "volatile claims carry a retrieval date" and "never ship `/beta` to production without flagging it" — the metered-API billing is the cost equivalent.

## How to apply

Before recommending any Graph API, verify whether it is metered:

1. Check the Microsoft Learn page for the API resource for a "Billing" or "Licensing" section.
2. Look for `@microsoft.graph.tips` or the API's licensing requirements table.
3. If metered, the recommendation must include:

```
⚠️ Licensing impact: This API is metered — charges are billed to the Azure subscription
linked to the app registration at [rate, unit, retrieval date: YYYY-MM-DD, source URL].
Verify the current rate before recommending at scale.
```

Known metered APIs as of 2026-05-30 `[verify-at-build]`:
- Teams Export API (messages, meeting transcripts) — per API call
- Microsoft Graph Connectors (external items) — per connector capacity unit
- Entra ID Protection risk detection queries (some tiers) — per query above included
- Syntex / SharePoint Premium APIs — per document processed

**Do:**
- Attach a `[verify-at-build]` tag to any metered-API rate claim — rates can change quarterly.
- Recommend the consumer set up Azure Cost Management alerts on the Graph PAYG resource before enabling a metered API in production.
- Confirm whether the consumer's existing license (M365 E5, Teams Premium, etc.) includes a free tier for the metered API before billing applies.

**Don't:**
- Recommend the Teams Export API for a use case that can be served by change notifications + standard message read — Export is priced per-call and should be the last resort, not the first.
- Assume a metered API's free tier covers the consumer's scale — the free tier is often per-tenant, not per-call volume.
- Omit the billing note because the rate "seems small" — at production call volumes small per-call rates become significant monthly costs.

## Edge cases / when the rule does NOT apply

Standard Graph APIs (user read, mail read, calendar read, group management) are not metered and do not require a billing note. The rule targets explicitly metered APIs only.

## See also

- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns Graph API recommendations and is the primary enforcer of this rule
- [`./api-v1-not-beta-in-production.md`](./api-v1-not-beta-in-production.md) — the parallel rule about the risk-disclosure obligation for `/beta` endpoints

## Provenance

Codifies CLAUDE.md §3 #9 ("volatile claims carry a retrieval date") extended to billing-model claims; Microsoft Graph PAYG API documentation (metered API billing model, 2026).

---

_Last reviewed: 2026-06-05 by `claude`_
