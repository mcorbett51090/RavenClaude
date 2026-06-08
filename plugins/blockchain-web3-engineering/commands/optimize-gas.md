---
description: "Profile gas and cut the dominant costs — storage writes and loops — then estimate the user-facing cost. Reach for this on a cost or UX-cost question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Optimize gas

You are running `/blockchain-web3-engineering:optimize-gas` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Profile the function — Find where gas goes; SSTORE and loops dominate (§3 #3).
2. Pack and cache — Pack storage slots, cache storage reads in memory, prefer events over storage for off-chain-needed data (§3 #3).
3. Bound the loops — Replace loops over unbounded arrays with pull patterns / pagination (§3 #3).
4. Estimate user cost — Tx cost in token + USD via `blockchain_web3_calc.py gas-cost`, with dated price inputs (§3 #8).

## Output
A gas profile with the dominant cost named, the fixes ranked by savings, and a dated user-facing cost estimate. See [`../skills/optimize-gas/SKILL.md`](../skills/optimize-gas/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No private keys / wallet data in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
