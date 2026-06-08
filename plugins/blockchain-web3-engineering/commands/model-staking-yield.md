---
description: "Model an illustrative net staking APR and annual reward — clearly NOT financial advice. Reach for this on a yield or reward question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Model staking yield

You are running `/blockchain-web3-engineering:model-staking-yield` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Take the inputs — Staked amount, gross annual reward rate, validator commission.
2. Compute net APR — Net APR = gross rate × (1 − commission) via `blockchain_web3_calc.py staking-yield`.
3. Mark it illustrative — Label the output not-financial-advice and date the volatile price/rate inputs (§3 #8).
4. Stress the sustainability — Is the reward funded or diluting — incentive soundness, not a return promise (§3 #7).

## Output
An illustrative net APR + annual reward, marked not-financial-advice, with volatile inputs dated and routing noted. See [`../skills/model-staking-yield/SKILL.md`](../skills/model-staking-yield/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No private keys / wallet data in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
