# Refactoring and behavior change never share a commit

**Status:** Absolute rule. **Constitution:** §2 #3.

## Use when
Any legacy-modernization deliverable where this question is in play — read, applied, and cited whole.

## The rule
A behavior-preserving refactor and a functional change are two different risks. Mixing them makes the diff un-reviewable and a bisect useless. Separate commits, ideally separate PRs.

## Why it matters
This is a house opinion distilled into a citable rule. Engineers and leaders act on these deliverables; a modernization that ignores this rule doesn't fail loudly — it fails quietly, months later, at the cutover or in production. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Land the refactor first, green, in its own commit; make the behavior change after, separately.
- If a review can't tell which lines change behavior, the commit is wrong-shaped — split it.
- Keep each step small enough to revert in a single commit.
- Cite a source + date for any external figure, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`modernization-strategist`](../agents/modernization-strategist.md) to sequence them.

## The anti-pattern this prevents
Shipping a 'cleanup + fix + feature' mega-commit that nobody can review and no bisect can untangle when it breaks. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #3 — the house opinion this rule encodes.
- [`../agents/refactoring-engineer.md`](../agents/refactoring-engineer.md) — the agent that enforces it.
