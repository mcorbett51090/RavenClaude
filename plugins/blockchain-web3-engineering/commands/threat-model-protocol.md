---
description: "Build the threat model beyond code — oracle, flash-loan, and MEV economic surface. Reach for this on a 'can we be drained?' question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Threat-model the protocol

You are running `/blockchain-web3-engineering:threat-model-protocol` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map the code threats — Reentrancy/access/arithmetic from the security analysis (§3 #2).
2. Add the oracle surface — Price feeds — use TWAP/multiple sources, never a spot DEX price (§3 #7).
3. Add flash-loan + MEV — Flash-loan-amplified economic attacks, front-running, sandwiching (§3 #7).
4. Own the upgrade risk — If a proxy is used, treat the admin key and storage layout as top-tier threats (§3 #6).

## Output
A threat model covering code, oracle, flash-loan, MEV, and upgrade surface, with mitigations named. Traverse Tree 3 in the decision-trees file. See [`../skills/threat-model-protocol/SKILL.md`](../skills/threat-model-protocol/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No private keys / wallet data in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
