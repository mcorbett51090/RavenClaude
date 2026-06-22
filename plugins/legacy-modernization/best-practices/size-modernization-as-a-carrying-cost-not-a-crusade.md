# Size modernization as a carrying cost, not a crusade

**Status:** Absolute rule. **Constitution:** §2 #7.

## Use when
Any legacy-modernization deliverable where this question is in play — read, applied, and cited whole.

## The rule
Legacy is not modernized for its own sake — it is traded against the roadmap. Quantify the carrying cost (change-failure rate, lead time, incident load, hiring drag) so the investment is a business decision, not an aesthetic one.

## Why it matters
This is a house opinion distilled into a citable rule. Engineers and leaders act on these deliverables; a modernization that ignores this rule doesn't fail loudly — it fails quietly, months later, at the cutover or in production. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Quantify the cost of *not* modernizing this capability before recommending that you do.
- Express the recommendation as a trade against the roadmap, with the driver named.
- Sequence for value-first delivery so increments pay back early.
- Cite a source + date for any external figure, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`modernization-strategist`](../agents/modernization-strategist.md) to sequence them.

## The anti-pattern this prevents
Modernizing because the code is ugly, with no business case — burning roadmap budget on an aesthetic with no measured return. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #7 — the house opinion this rule encodes.
- [`../skills/assess-legacy-estate/SKILL.md`](../skills/assess-legacy-estate/SKILL.md) — the method that applies it.
