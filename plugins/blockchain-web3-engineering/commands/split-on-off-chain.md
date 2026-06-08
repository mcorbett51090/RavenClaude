---
description: "Decide deliberately what lives on-chain vs off-chain on cost and privacy grounds. Reach for this on any data-placement question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Split on/off-chain data

You are running `/blockchain-web3-engineering:split-on-off-chain` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Classify the data — Consensus-critical (balances, ownership, commitments) vs ancillary (metadata, media, history).
2. Price on-chain storage — Storage slots × gas-per-slot × price via `blockchain_web3_calc.py storage-cost` (§3 #4).
3. Place the rest off-chain — IPFS/Arweave/indexer with an on-chain hash/pointer for integrity (§3 #4).
4. Check the privacy implication — On-chain data is public forever — confirm nothing sensitive lands on-chain (§3 #4, §2).

## Output
An on/off-chain placement with the cost+privacy trade made explicit and a hash-pointer pattern where apt. Traverse Tree 2 in the decision-trees file. See [`../skills/split-on-off-chain/SKILL.md`](../skills/split-on-off-chain/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No private keys / wallet data in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
