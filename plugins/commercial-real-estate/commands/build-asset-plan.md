---
description: "Sequence lease rollovers, recovery improvements, and capex against a quarterly NOI target for an owned asset, deciding lease-up vs strategic vacancy on each rollover."
argument-hint: "[the asset and NOI goal, e.g. 'grow this retail center NOI 8% in 24 months']"
---

# Build an asset business plan

You are running `/commercial-real-estate:build-asset-plan` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Anchor the quarterly NOI target to the acquisition model.
2. Sequence the levers by NOI impact and dependency (§3 #7).
3. On each rollover, compare a fast fill NER to holding for credit/term (§3 #5).
4. Set up the realized-vs-underwritten variance tracker.

## Output
A dated asset plan with NOI checkpoints and a variance tracker. Use [`../templates/asset-business-plan.md`](../templates/asset-business-plan.md).

## Guardrails
- Don't fill vacancy at any NER just to hit occupancy.
- Name every NOI variance as a leasing, opex, or recovery story.
