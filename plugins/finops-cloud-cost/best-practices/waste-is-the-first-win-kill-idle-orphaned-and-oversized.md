# Waste is the first win — kill idle, orphaned, and oversized.

**Status:** Absolute rule. **Constitution:** §3 #5, §4.

## Use when
Any finops & cloud cost deliverable where this question is in play — read, applied, and cited whole.

## The rule
Idle instances, orphaned volumes/IPs, oversized resources, and zombie environments are pure savings with no trade-off; harvest them before negotiating discounts or re-architecting. The cheapest resource is the one you turned off.

## Why it matters
This is house opinion §3 #5, distilled into a citable rule. Practitioners act on these deliverables, so a framing error here is not academic — it sends real operating decisions the wrong way. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Make every number in the deliverable carry a definition, a window, and a baseline (§3 #1).
- Cite a source + date for any external benchmark, or mark it `[unverified — training knowledge]` (§3 #8).
- When this rule and another both apply, route to [`finops-lead`](../agents/finops-lead.md) to sequence them — overlapping signals usually mean two drivers at once.
- Keep billing/account PII out of the deliverable; route professional/legal determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected metric movement.

## The anti-pattern this prevents
The §4 failure mode: acting as if "waste is the first win — kill idle, orphaned, and oversized." weren't true — the most common way an analysis quietly misleads the practitioner who acts on it. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #5 — the house opinion this rule encodes.
- [`../knowledge/finops-cloud-cost-decision-trees.md`](../knowledge/finops-cloud-cost-decision-trees.md) — the decision trees that route to it.
