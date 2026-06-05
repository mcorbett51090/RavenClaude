# Upgrade asks are percent increases, not arbitrary round numbers

**Status:** Pattern
**Domain:** Nonprofit donor cultivation
**Applies to:** `nonprofit-fundraising`

---

## Why this exists

The most common upgrade-ask error is the round-number trap: a donor who gave $120 last year is asked for $150 because $150 feels like a natural next step. That ask ignores the donor's giving history and anchors to a round number rather than a meaningful upgrade. A 10–15% ask increase over the prior gift is psychologically accessible ("a little more than last time") and mathematically predictable across the donor file. Round-number asks also reveal to the donor that the organization doesn't remember exactly what they gave — it undermines the cultivation relationship. An ask that reflects the donor's exact prior gift is a signal that the relationship is tracked and valued.

## How to apply

Set upgrade ask amounts as a percentage above the prior gift, anchored to the exact gift amount. Use a 15% uplift as the default; use 10% for donors who have been declining or are known to be in a constrained giving season.

```
Upgrade ask formula:
  Default upgrade: prior_gift × 1.15, rounded to the nearest $5 or $10
  Conservative upgrade: prior_gift × 1.10
  Aspirational upgrade: prior_gift × 1.25 (for mid-level donors showing rising capacity signals)

Examples:
  Prior gift $120 → default ask: $138 → round to $140
  Prior gift $500 → default ask: $575 → present as $575 (don't round down to $550)
  Prior gift $1,200 → default ask: $1,380 → may use $1,500 if wealth signals support it
  Prior gift $250 → conservative ask (declining trend): $275

Personalized ask language: "Your generous gift of $120 last year helped us [specific outcome].
  Would you consider a gift of $140 this year to [specific next goal]?"
```

**Do:**
- Merge the prior gift amount into every renewal letter and ask — the ask amount should reference it.
- Use 10–15% as the default range and vary within it based on capacity and engagement signals.
- Document the upgrade ask amount used in the CRM so the next cycle builds on it.

**Don't:**
- Ask a prior-year donor for a round number that ignores their exact gift history.
- Use the same upgrade percentage for a first-time donor and a 10-year loyal donor without checking capacity signals.
- Upgrade-ask a donor who has been declining in giving without first reactivating and re-engaging them.

## Edge cases / when the rule does NOT apply

First-time donors do not have a prior gift to anchor on — use the modal gift amount for their acquisition channel as the renewal anchor. For major-gift donors ($10k+), the upgrade conversation is part of a formal cultivation and capacity-assessment process; the percentage formula applies only to the annual-fund upgrade cadence.

## See also

- [`../agents/nonprofit-finance-analyst.md`](../agents/nonprofit-finance-analyst.md) — tracks upgrade rates and gift-size progression in the development scorecard.
- [`./segment-donors-by-value-recency-and-engagement.md`](./segment-donors-by-value-recency-and-engagement.md) — the companion rule on tiering the donor base so upgrade-ask strategy is segment-appropriate.

## Provenance

Codifies standard annual-fund ask-string design practice. The round-number-ask error is consistently observed in renewal programs where the CRM is not used to personalize ask amounts; the percentage-anchor method is the industry-standard corrective.

---

_Last reviewed: 2026-06-05 by `claude`_
