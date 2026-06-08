---
description: "Read LTV:CAC and CAC-payback to gate acquisition spend on unit economics, not lead count. Reach for this on a CAC or sustainability question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read CAC and LTV

You are running `/marketing-operations:read-cac-ltv` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Compute fully-loaded CAC — All acquisition cost ÷ customers acquired.
2. Compute LTV — Gross-margin lifetime value per customer.
3. Ratio and payback — LTV:CAC and CAC ÷ monthly margin contribution via `marketingops_calc.py cac-ltv` (§3 #3).
4. Gate the spend — Compare to a dated health frame; mark benchmarks unverified (§3 #8).

## Output
An LTV:CAC and payback read gating spend, with benchmarks dated. Traverse Tree 2 in the decision-trees file. See [`../skills/read-cac-ltv/SKILL.md`](../skills/read-cac-ltv/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/lead PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
