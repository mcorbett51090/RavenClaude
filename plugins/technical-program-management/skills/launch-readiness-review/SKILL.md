---
name: launch-readiness-review
description: "Run a go/no-go launch-readiness review against written, pre-agreed criteria and design a staged rollout with a tested rollback. Use as a launch approaches — define measurable, owner-assigned criteria first, then facilitate the decision and record any waiver with its risk acceptance."
---

# Skill: Launch-readiness review

Turn "we think we're ready" into a documented go/no-go and a staged rollout. A
launch decision made on vibe is an accident waiting for a retro.

## When to use

- A program milestone or product is approaching go-live.
- A team wants to "just ship it" with no agreed bar for ready.
- A big-bang launch is planned with no rollout stages or rollback.

## Procedure

1. **Define criteria before the review.** Each go/no-go criterion is measurable and
   owner-assigned, agreed in advance. Use the
   [`launch-readiness-checklist`](../../templates/launch-readiness-checklist.md)
   template. Criteria invented in the room are bias, not a bar.
2. **Facilitate the go/no-go.** Walk each criterion: GO / NO-GO / waived. Traverse
   the go/no-go tree in
   [`../../knowledge/tpm-engagement-decision-trees.md`](../../knowledge/tpm-engagement-decision-trees.md).
3. **Reach an explicit decision with an owner.** Record who made the call. A waived
   criterion is recorded with its **risk acceptance** and who accepted it — never
   silently dropped.
4. **Design the staged rollout.** Canary → percentage ramp → full, each stage gated
   on a specific metric (error rate / latency / conversion) that must hold to
   advance.
5. **Test the rollback.** Name the rollback path and who can pull it, and verify it
   works *before* go-live. An untested rollback is not a plan.

## Output

A completed readiness checklist, a recorded go/no-go decision (with any waiver +
risk acceptance), and a staged rollout + tested rollback plan.

## Anti-patterns (the hook flags these)

- A launch checklist with no go/no-go criteria or pass/fail bar.
- A "we'll watch it closely" gate (no metric, no threshold).
- A rollout with no stages or an untested rollback.
