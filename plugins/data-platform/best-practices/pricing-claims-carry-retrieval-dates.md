# Every pricing claim carries a retrieval date and is re-verified before client delivery

**Status:** Absolute rule
**Domain:** Vendor pricing / claims hygiene
**Applies to:** `data-platform`

---

## Why this exists

SaaS pricing in the data-platform space changes quarterly — sometimes mid-quarter with no public announcement. Fivetran's 2026 per-connection minimum and MAR-count-deletes change, Metabase's Pro tier restructuring, Snowflake's on-demand pricing adjustments — all happened within a single calendar year. A consultant who quotes last year's pricing loses client trust or loses margin on a fixed-fee engagement. A knowledge file or stack-decision-record that doesn't carry a retrieval date becomes a liability the moment the vendor's pricing page changes.

## How to apply

**In knowledge files and decision records:**

```markdown
| Vendor | Tier | Price | Retrieved |
|---|---|---|---|
| Supabase | Pro | $25/mo | 2026-05-21 |
| Cube Cloud | Starter | $99/mo (verify-at-build) | 2026-04-10 |
| Fivetran | MAR-based | $0.35-1.00/MAR + $5/connection min (Jan 2026) | 2026-05-30 |
```

**In stack-decision-record.md:**

```markdown
## Pricing claims
All figures are `[verify-at-build]` unless a retrieval date within 30 days is attached.

| Item | Quoted figure | Retrieved | Source URL |
|---|---|---|---|
| Metabase Pro | $500/mo (5 users) | 2026-05-15 | https://www.metabase.com/pricing |
```

**Before client delivery:**
- [ ] Any pricing figure older than 30 days → re-verify against the vendor's pricing page.
- [ ] Tag refreshed claims with the new retrieval date.
- [ ] If a price has changed, update the stack-decision-record before the client call.

**Do:**
- Write retrieval dates inline, not in a separate footnote that can be separated from the claim.
- Use `[verify-at-build]` as a sentinel for any figure you could not verify at authoring time.
- Re-verify before every new engagement even if the doc is recent — pricing is vendor-controlled.

**Don't:**
- Quote a pricing figure from memory (training data) without a same-session retrieval check.
- Strip retrieval dates during document editing.
- Present a pricing comparison to a client without a "prices accurate as of [date]" footer.

## Edge cases / when the rule does NOT apply

Internal proofs-of-concept and developer sandboxes where pricing is not relevant to the deliverable are exempt — but any output that could be shown to a client inherits the rule.

## See also

- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) — surfaces Fivetran/Airbyte cost trade-offs frequently
- [`./connector-avoid-per-viewer-and-per-row-pricing-traps.md`](./connector-avoid-per-viewer-and-per-row-pricing-traps.md) — the per-viewer and per-MAR pricing anti-pattern

## Provenance

Codifies data-platform CLAUDE.md §3 house opinion #9 ("Pricing changes quarterly. Every pricing claim in this plugin has a retrieval date. Re-verify before quoting a client.") and §4 anti-patterns ("Pricing claims in plugin content that don't carry a retrieval date").

---

_Last reviewed: 2026-06-05 by `claude`_
