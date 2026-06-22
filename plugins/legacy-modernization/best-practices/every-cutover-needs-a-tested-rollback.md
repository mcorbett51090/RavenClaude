# Every cutover needs a tested rollback

**Status:** Absolute rule. **Constitution:** §2 #6.

## Use when
Any legacy-modernization deliverable where this question is in play — read, applied, and cited whole.

## The rule
Data migration runs in parallel (dual-write / shadow) and is reconciled *before* the cutover, and the cutover runbook includes a rollback that has actually been exercised. A cutover you can't undo is a bet, not a plan.

## Why it matters
This is a house opinion distilled into a citable rule. Engineers and leaders act on these deliverables; a modernization that ignores this rule doesn't fail loudly — it fails quietly, months later, at the cutover or in production. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Run old and new in parallel and reconcile to tolerance before any traffic moves.
- Write go/no-go gates and *rehearse* the rollback in a non-prod or canary run before the real switch.
- Shift traffic incrementally, watching reconciliation and SLOs, ready to flip back.
- Cite a source + date for any external figure, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`modernization-strategist`](../agents/modernization-strategist.md) to sequence them.

## The anti-pattern this prevents
Cutting over on a theorized-but-never-tested rollback, then discovering at 2am that the rollback path itself is broken. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #6 — the house opinion this rule encodes.
- [`../skills/data-migration-and-cutover/SKILL.md`](../skills/data-migration-and-cutover/SKILL.md) — the method that applies it.
- [`../templates/cutover-runbook.md`](../templates/cutover-runbook.md) — the runbook it produces.
