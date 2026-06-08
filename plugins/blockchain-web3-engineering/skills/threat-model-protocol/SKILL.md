---
name: threat-model-protocol
description: "Build the threat model beyond code — oracle, flash-loan, and MEV economic surface. Reach for this on a 'can we be drained?' question."
---

# Skill: Threat-model the protocol

A code-correct contract can still be economically drained — the threat model includes economic surface (§3 #7).

## Step 1 — Map the code threats
Reentrancy/access/arithmetic from the security analysis (§3 #2).

## Step 2 — Add the oracle surface
Price feeds — use TWAP/multiple sources, never a spot DEX price (§3 #7).

## Step 3 — Add flash-loan + MEV
Flash-loan-amplified economic attacks, front-running, sandwiching (§3 #7).

## Step 4 — Own the upgrade risk
If a proxy is used, treat the admin key and storage layout as top-tier threats (§3 #6).

## Output
A threat model covering code, oracle, flash-loan, MEV, and upgrade surface, with mitigations named. Traverse Tree 3 in the decision-trees file.
