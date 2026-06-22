---
description: "Assess a legacy system and recommend a modernization strategy with the 6 R's. Reach for this on 'rewrite or refactor?' or 'is this worth modernizing?'."
argument-hint: "[the system / capability and its pain]"
---

# Assess legacy

You are running `/legacy-modernization:assess-legacy` for `$ARGUMENTS`. Run it the way the `modernization-strategist` would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2.

## Steps (traverse top-to-bottom; do not skip)
1. Inventory the capability — dependencies, runtime, data stores, owner, and the pain it causes (cite the signal, §2 #7).
2. Name the driver — the specific reason to change it now; no driver → retain.
3. Pick the R per capability — traverse the 6-R's tree in [`../knowledge/legacy-modernization-decision-trees.md`](../knowledge/legacy-modernization-decision-trees.md).
4. Make the carrying-cost case — cost of not modernizing vs cost/risk of doing it.
5. Sequence value-first — increments ship early, riskiest unknowns first, rollback cheap.

## Output
A 6-R's recommendation with the named driver and a value-first roadmap, in the [`../templates/modernization-assessment.md`](../templates/modernization-assessment.md) shape. See [`../skills/assess-legacy-estate/SKILL.md`](../skills/assess-legacy-estate/SKILL.md).

## Guardrails
- Rewrite-from-scratch is the default wrong answer (§2 #2) — it must earn its risk.
- Cite a source + date for every external figure (or mark it `[unverified]` / `[ESTIMATE]`).
- End with owner / date / expected movement on each recommendation.
