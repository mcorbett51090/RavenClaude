---
name: optimize-gas
description: "Profile gas and cut the dominant costs — storage writes and loops — then estimate the user-facing cost. Reach for this on a cost or UX-cost question."
---

# Skill: Optimize gas

Micro-optimizing while an unbounded loop or redundant SSTORE dominates wastes the effort (§3 #3).

## Step 1 — Profile the function
Find where gas goes; SSTORE and loops dominate (§3 #3).

## Step 2 — Pack and cache
Pack storage slots, cache storage reads in memory, prefer events over storage for off-chain-needed data (§3 #3).

## Step 3 — Bound the loops
Replace loops over unbounded arrays with pull patterns / pagination (§3 #3).

## Step 4 — Estimate user cost
Tx cost in token + USD via `blockchain_web3_calc.py gas-cost`, with dated price inputs (§3 #8).

## Output
A gas profile with the dominant cost named, the fixes ranked by savings, and a dated user-facing cost estimate.
