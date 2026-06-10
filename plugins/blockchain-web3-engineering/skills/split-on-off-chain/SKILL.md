---
name: split-on-off-chain
description: "Decide deliberately what lives on-chain vs off-chain on cost and privacy grounds. Reach for this on any data-placement question."
---

# Skill: Split on/off-chain data

'Store it on-chain to be safe' is usually wrong on both cost and privacy — every byte is paid for forever and public (§3 #4).

## Step 1 — Classify the data
Consensus-critical (balances, ownership, commitments) vs ancillary (metadata, media, history).

## Step 2 — Price on-chain storage
Storage slots × gas-per-slot × price via `blockchain_web3_calc.py storage-cost` (§3 #4).

## Step 3 — Place the rest off-chain
IPFS/Arweave/indexer with an on-chain hash/pointer for integrity (§3 #4).

## Step 4 — Check the privacy implication
On-chain data is public forever — confirm nothing sensitive lands on-chain (§3 #4, §2).

## Output
An on/off-chain placement with the cost+privacy trade made explicit and a hash-pointer pattern where apt. Traverse Tree 2 in the decision-trees file.
