# Color contrast is measurable — verify the ratio, don't eyeball it.

**Status:** Absolute rule. **Constitution:** §3 #5, §4.

## Use when
Any accessibility engineering deliverable where this question is in play — read, applied, and cited whole.

## The rule
WCAG contrast is a computed ratio from relative luminance, not a vibe; normal text needs >=4.5:1 (AA) and large text >=3:1, with 7:1 / 4.5:1 for AAA — compute it from the hex values and never approve color on appearance.

## Why it matters
This is house opinion §3 #5, distilled into a citable rule. Practitioners act on these deliverables, so a framing error here is not academic — it sends real operating decisions the wrong way. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Make every number in the deliverable carry a definition, a window, and a baseline (§3 #1).
- Cite a source + date for any external benchmark, or mark it `[unverified — training knowledge]` (§3 #8).
- When this rule and another both apply, route to [`accessibility-lead`](../agents/accessibility-lead.md) to sequence them — overlapping signals usually mean two drivers at once.
- Keep user PII out of the deliverable; route professional/legal determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected metric movement.

## The anti-pattern this prevents
The §4 failure mode: acting as if "color contrast is measurable — verify the ratio, don't eyeball it." weren't true — the most common way an analysis quietly misleads the practitioner who acts on it. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #5 — the house opinion this rule encodes.
- [`../knowledge/accessibility-engineering-decision-trees.md`](../knowledge/accessibility-engineering-decision-trees.md) — the decision trees that route to it.
