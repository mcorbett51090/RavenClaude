# Strangle, don't stop the world

**Status:** Absolute rule. **Constitution:** §2 #4.

## Use when
Any legacy-modernization deliverable where this question is in play — read, applied, and cited whole.

## The rule
Replace the old system one capability at a time behind a facade, routing traffic incrementally, so value lands continuously and rollback is always one route-flip away — never a months-long freeze ending in a single terrifying switch.

## Why it matters
This is a house opinion distilled into a citable rule. Engineers and leaders act on these deliverables; a modernization that ignores this rule doesn't fail loudly — it fails quietly, months later, at the cutover or in production. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Place a facade/abstraction so capabilities can route to old or new independently.
- Migrate one capability at a time; keep the old path live as the rollback until the new one proves out.
- Commit to *retiring* each migrated legacy path, not just adding the new one alongside.
- Cite a source + date for any external figure, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`modernization-strategist`](../agents/modernization-strategist.md) to sequence them.

## The anti-pattern this prevents
A multi-month feature freeze culminating in a single big-bang cutover with no incremental rollback — the highest-risk way to ship a modernization. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #4 — the house opinion this rule encodes.
- [`../skills/strangler-fig-migration/SKILL.md`](../skills/strangler-fig-migration/SKILL.md) — the method that applies it.
