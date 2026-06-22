---
description: Run a go/no-go launch-readiness review against written, pre-agreed criteria and design a staged rollout with a tested rollback — reach an explicit decision with an owner and record any waiver with its risk acceptance.
argument-hint: "[the launch, e.g. 'billing platform go-live next Thursday']"
---

# Run launch readiness

You are running `/technical-program-management:run-launch-readiness`. Run the
go/no-go for `$ARGUMENTS` using the `program-launch-coordinator` discipline: a
launch decided on vibe is an accident waiting for a retro.

## Steps

1. **Define go/no-go criteria first** — measurable + owner-assigned, agreed before
   the review. Use the
   [`launch-readiness-checklist`](../templates/launch-readiness-checklist.md)
   template. Criteria invented in the room are bias, not a bar.
2. **Facilitate the review** — walk each criterion GO / NO-GO / waived (go/no-go
   tree in [`../knowledge/tpm-engagement-decision-trees.md`](../knowledge/tpm-engagement-decision-trees.md)).
3. **Reach an explicit decision with an owner.** Record any waiver with its **risk
   acceptance** and who accepted it.
4. **Design the staged rollout** — canary → ramp → full, each gated on a metric.
5. **Verify the rollback is tested** before go-live and name who can pull it.

## Guardrails

- No criteria written and agreed in advance → not ready to decide; define them first.
- "We'll watch it closely" is not a gate — a gate is a metric and a threshold.
