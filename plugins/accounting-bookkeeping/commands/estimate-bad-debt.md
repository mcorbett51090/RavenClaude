---
description: "Estimate bad-debt from AR aging buckets weighted by loss rate. Reach for this on a receivables-risk question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Estimate bad debt

You are running `/accounting-bookkeeping:estimate-bad-debt` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Bucket the AR — Current / 30 / 60 / 90+ aging buckets (§3 #3).
2. Apply loss rates — Per-bucket expected loss; older = higher.
3. Weight the estimate — Σ(bucket × loss rate) via `acctgops_calc.py aging` (§3 #3).
4. Route the write-off — Tax treatment of write-offs → a licensed CPA (§2 #8).

## Output
A weighted bad-debt estimate from the aging. See [`../skills/estimate-bad-debt/SKILL.md`](../skills/estimate-bad-debt/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
