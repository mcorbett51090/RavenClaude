---
description: "Run a cost through the 2 CFR 200 allowable/allocable/reasonable test against the award terms, and return a cited, advisory determination."
argument-hint: "[the cost + the award type/terms + period of performance + any indirect/match context]"
---

You are running `/public-sector-grants:check-cost-allowability`. Use `grants-compliance-analyst` + the `uniform-guidance-compliance` skill.

## Steps
1. **Allowable?** Is it permitted by the 2 CFR 200 cost principles AND the award terms — not a prohibited/excluded item? If no, stop: unallowable, name why, suggest an alternate funding source.
2. **Allocable?** Does it benefit the award in proportion to the amount charged? If only partly, allocate the benefiting share.
3. **Reasonable?** Would a prudent person incur it, consistent with market/policy? If excessive, reduce to the reasonable amount.
4. **Period & documentation:** Is it within the period of performance and contemporaneously documented? Flag any pre-award/post-period authority needed.
5. Note the indirect-rate and match/cost-share implications if relevant; classify any sub-recipient relationship and the monitoring it triggers.
6. Cite the relevant 2 CFR section, verify any threshold/deadline against current 2 CFR + the award terms, mark the determination **advisory** (the authorized official/auditor decides), and emit the Structured Output block (with `Funder requirement traced:` and `Compliance posture:`).
