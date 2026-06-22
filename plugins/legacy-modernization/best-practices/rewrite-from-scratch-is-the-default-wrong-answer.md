# Rewrite-from-scratch is the default wrong answer

**Status:** Absolute rule. **Constitution:** §2 #2.

## Use when
Any legacy-modernization deliverable where this question is in play — read, applied, and cited whole.

## The rule
The big-bang rewrite throws away years of embedded edge-case knowledge and ships nothing until the end. Reach for incremental modernization first; a full rebuild must *earn* its risk against a real, named driver.

## Why it matters
This is a house opinion distilled into a citable rule. Engineers and leaders act on these deliverables; a modernization that ignores this rule doesn't fail loudly — it fails quietly, months later, at the cutover or in production. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Run the rewrite-vs-refactor tree before proposing a rebuild; default to incremental.
- If a rewrite is chosen, keep characterization tests as the spec of the behavior being replaced.
- Name the specific driver that makes incremental impossible — 'it's old' is not a driver.
- Cite a source + date for any external figure, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`modernization-strategist`](../agents/modernization-strategist.md) to sequence them.

## The anti-pattern this prevents
Proposing a from-scratch rewrite by reflex, repeating the original's bugs while shipping nothing for months — the second-system effect, on a deadline. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #2 — the house opinion this rule encodes.
- [`../knowledge/legacy-modernization-decision-trees.md`](../knowledge/legacy-modernization-decision-trees.md) — the rewrite-vs-refactor tree.
