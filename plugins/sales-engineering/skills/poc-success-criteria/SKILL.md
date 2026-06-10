---
name: poc-success-criteria
description: Decide if a POC is warranted and, if so, write measurable success + exit criteria a champion signs before kickoff, scope a time-boxed plan, and build the evaluation scorecard that converts a passed POC to a technical win. Reach for this when a prospect asks for a proof-of-concept or pilot, or when an SE needs to keep a POC from sprawling. Used by `poc-evaluation-lead` (primary) and `sales-engineer`.
---

# Skill: poc-success-criteria

> **Invoked by:** `poc-evaluation-lead` (primary); `sales-engineer` when a deal turns toward a POC.
>
> **When to invoke:** "the prospect wants a POC"; "what are the success criteria?"; "scope this pilot"; "the POC is done — did we win?".
>
> **Output:** a go/no-go verdict, signed success + exit criteria, a time-boxed scope, and (on completion) a scorecard — using [`../../templates/poc-success-criteria.md`](../../templates/poc-success-criteria.md).

## Procedure

1. **Gate first.** Traverse the build-the-POC? tree in [`../../knowledge/se-engagement-decision-trees.md`](../../knowledge/se-engagement-decision-trees.md): qualified pain? a champion who'll drive it? explicit decision criteria? a *reachable* definition of success? If any is missing, recommend the cheaper alternative (tailored demo, reference call, guided sandbox) and stop.
2. **Write 3-6 measurable success criteria** tied to the discovered pain. Each must be **testable** ("imports a 1M-row file in < 5 min", not "is fast") and **owned** (who verifies it). Per [`../../knowledge/poc-and-evaluation-best-practices.md`](../../knowledge/poc-and-evaluation-best-practices.md).
3. **Write the matching exit/kill rules.** Each criterion gets a pass/fail test; the POC overall gets a kill rule (what ends it early) and an extend rule (the one condition under which you add time). A POC you can't fail is one you can't win.
4. **Time-box and scope.** Set the duration, in-scope/out-of-scope, the data + environment prerequisites, and the milestone checkpoints. Name what is explicitly **not** being proven so the POC doesn't drift into an unpaid implementation.
5. **Get the champion's signature** on the criteria + scope before kickoff. Unsigned criteria move the moment results arrive.
6. **Score honestly on completion.** Criterion-by-criterion pass / partial / fail against the signed definitions. Route a failed criterion to a workaround, a roadmap item, or an honest no — never restate a fail as a pass.

## Output

The signed success/exit criteria + scoped, time-boxed plan; on completion, the scorecard + a technical-win summary the champion takes internally.

## Anti-patterns this skill prevents

- An open-ended POC with no written success criteria ("we'll know it when we see it").
- Success criteria with no exit/kill rule (un-failable → un-winnable).
- Scope creep into a free implementation.
- Starting before the champion signs.
- Spinning a failed criterion as a pass.
