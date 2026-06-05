# Milestone definitions must include a done criteria, not just a date

**Status:** Absolute rule
**Domain:** Game production
**Applies to:** `game-development`

---

## Why this exists

A milestone with a date but no done criteria is a scheduling event, not a production gate. "Alpha by October 15" means nothing unless the team has agreed on what Alpha means: is it first-playable with core loop? Is it content-complete for one chapter? Does it pass a specific stability bar? Without a written done criteria, "we hit Alpha" can mean the producer checked off a calendar box while half the team is still firefighting from the prior milestone. The absence of done criteria is how scope creep is invisible: each milestone "passes" on schedule while the actual feature and quality bar silently shifts. Done criteria make the milestone a real gate that either passes or doesn't — and that clarity is what allows the team to prioritize ruthlessly.

## How to apply

For each milestone in the production schedule, write a done criteria document with explicit, testable conditions. The milestone doesn't pass until the criteria are met, regardless of the date.

```
Milestone done-criteria template:

  Milestone: ALPHA
  Date target: [date]

  Done criteria (ALL must be true to pass):
    1. Core loop playable end-to-end without a crash in a 20-minute session ✓/✗
    2. Tutorial completable by a first-time tester without designer assistance ✓/✗
    3. Economy: at least one full source-to-sink cycle operational ✓/✗
    4. Art: placeholder assets flagged with a tracking tag; no unlabeled placeholders ✓/✗
    5. Performance: target device (lowest-spec target) maintains >= 30fps in core gameplay ✓/✗
    6. Crash-free rate in last 5 full playthroughs: 100% ✓/✗

  Optional / tracked-but-not-gating criteria (for visibility, not pass/fail):
    — Story sequence: first chapter blocked out (even with placeholder dialogue) ✓/✗
    — Audio: placeholder music and SFX in all combat encounters ✓/✗

  Gate rule: milestone passes when ALL required criteria are ✓.
  If any required criterion is ✗ on the target date: milestone slips; communicate to stakeholders.
  "We'll clean it up next sprint" is not a pass.
```

**Do:**
- Write done criteria for every milestone before the production schedule is shared with stakeholders.
- Include testable performance and stability criteria, not just feature-list checks.
- Distinguish "required for pass" from "tracked but not gating" criteria — both are visible, only the first gates the milestone.

**Don't:**
- Declare a milestone passed because the date arrived, regardless of the criteria state.
- Write done criteria as vague qualitative statements ("gameplay feels good") — they must be testable.
- Set done criteria only for the final milestone; every milestone in the production arc needs them.

## Edge cases / when the rule does NOT apply

Game jams with 48–72-hour timelines have no meaningful milestone gates — the jam itself is the gate. Pre-production (concept → greenlight) phases may use a pitch criteria document instead of milestone done criteria; the principle is the same but the format differs.

## See also

- [`../agents/gamedev-producer.md`](../agents/gamedev-producer.md) — owns the production schedule and milestone definitions.
- [`./scope-is-the-enemy-burn-down-risk-not-just-tasks.md`](./scope-is-the-enemy-burn-down-risk-not-just-tasks.md) — the companion rule on scope management that the done criteria enforce.

## Provenance

Codifies the done-criteria-as-gate discipline in game production. The date-without-criteria milestone is the most common production-planning error; it makes scope slip invisible until the game is "in alpha" for six months.

---

_Last reviewed: 2026-06-05 by `claude`_
