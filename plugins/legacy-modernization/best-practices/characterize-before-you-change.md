# Characterize before you change

**Status:** Absolute rule. **Constitution:** §2 #1.

## Use when
Any legacy-modernization deliverable where this question is in play — read, applied, and cited whole.

## The rule
A legacy system's behavior *is* its spec — including the bugs people now depend on. Pin current behavior with characterization / golden-master tests before touching anything, or you are refactoring blind.

## Why it matters
This is a house opinion distilled into a citable rule. Engineers and leaders act on these deliverables; a modernization that ignores this rule doesn't fail loudly — it fails quietly, months later, at the cutover or in production. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Stand up tests that capture *current* behavior (not desired behavior) around the change area.
- Use approval/golden-master snapshots where outputs are large or unspecified.
- Cover the blast radius of the change, not the whole system.
- Cite a source + date for any external figure, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`modernization-strategist`](../agents/modernization-strategist.md) to sequence them.

## The anti-pattern this prevents
Editing untested legacy code in place and discovering the behavior change only when a user reports it — the most common way a 'safe refactor' silently breaks production. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #1 — the house opinion this rule encodes.
- [`../skills/characterization-testing/SKILL.md`](../skills/characterization-testing/SKILL.md) — the method that applies it.
