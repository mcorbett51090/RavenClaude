# Recommend a managed handoff path when the client will operate the stack post-engagement

**Status:** Pattern
**Domain:** Engagement delivery / client handoff
**Applies to:** `data-platform`

---

## Why this exists

Self-hosted Superset, Metabase, or Cube is cheapest while a consultant operates it. The moment the client takes over, ops burden transfers — and a client without a data engineer on staff will not patch containers, rotate credentials, or manage Postgres upgrades. The result is an abandoned dashboard within 18 months or a support dependency that the consultant didn't price. Recommending a managed SaaS path (Cube Cloud, Metabase Cloud, Supabase, Neon) at engagement design time — even when it costs more per month — is often the difference between a renewal and a churn.

## How to apply

In `stack-decision-record.md`, add a Handoff section:

```markdown
## Client Handoff Plan

**Will the client operate this stack post-engagement?** Yes / No / Unknown

If yes:
**Recommended managed path:**
- Cube Cloud (replaces self-hosted Cube): [tier + estimated cost]
- Supabase Pro (replaces self-hosted Postgres): already managed
- Metabase Cloud (replaces self-hosted Metabase): [tier + estimated cost]

**Ops burden transferred to client on self-hosted path:**
- Container/VM uptime + patching: ~[N] hours/month
- Credential rotation: [frequency]
- Postgres major version upgrades: [annually + downtime risk]

**Decision:** [ ] Managed path recommended  [ ] Self-hosted with documented client agreement

If self-hosted is chosen: client signs off on the ops burden list above.
```

**Do:**
- Present the managed vs self-hosted trade-off explicitly in the engagement proposal, not as an afterthought.
- Price the managed path's monthly cost against the ops-labor cost for the client.
- Document the decision in `stack-decision-record.md` with the client's sign-off.

**Don't:**
- Recommend self-hosted without surfacing the post-engagement ops burden.
- Assume a client has internal ops capacity without asking.
- Treat "cheapest" as the only axis — include client renewal probability in the trade-off.

## Edge cases / when the rule does NOT apply

- Engagements where a dedicated data/DevOps engineer is confirmed on the client's staff — managed vs self-hosted is then a cost decision, not an ops-risk decision.
- Short-lived engagements (prototype / one-time analysis) where there is no ongoing operation planned.

## See also

- [`../agents/dashboard-builder.md`](../agents/dashboard-builder.md) — selects dashboard framework; should surface managed options
- [`./connector-document-the-handoff-at-design-time.md`](./connector-document-the-handoff-at-design-time.md) — the companion rule for ELT pipeline handoff documentation

## Provenance

Codifies data-platform CLAUDE.md §3 house opinion #8: "The escape hatch matters. Recommend a managed SaaS (Cube Cloud, Power BI Embedded F2) when a client wants to take over post-engagement."

---

_Last reviewed: 2026-06-05 by `claude`_
