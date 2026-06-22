# An anti-corruption layer guards the new from the old

**Status:** Pattern. **Constitution:** §2 #5.

## Use when
Any legacy-modernization deliverable where this question is in play — read, applied, and cited whole.

## The rule
When new and old coexist, translate at the boundary so the legacy model's quirks don't leak into the new design. The anti-corruption layer is what lets the new code stay clean while the old code still runs.

## Why it matters
This is a house opinion distilled into a citable rule. Engineers and leaders act on these deliverables; a modernization that ignores this rule doesn't fail loudly — it fails quietly, months later, at the cutover or in production. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Put a translation boundary (ACL) between the legacy model and the new model wherever they exchange data.
- Design the new model around the *need*, then translate the legacy shape into it — not the reverse.
- Treat ACL translation rules as code: tested, reviewed, and removed when the legacy side dies.
- Cite a source + date for any external figure, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`modernization-strategist`](../agents/modernization-strategist.md) to sequence them.

## The anti-pattern this prevents
Letting the legacy data model leak straight into the new system, so you rebuild the old mess with newer syntax. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #5 — the house opinion this rule encodes.
- [`../knowledge/modernization-patterns-reference.md`](../knowledge/modernization-patterns-reference.md) — the ACL pattern.
