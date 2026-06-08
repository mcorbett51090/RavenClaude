---
scenario_id: 2026-06-08-on-chain-to-be-safe-cost-and-privacy
contributed_at: 2026-06-08
plugin: blockchain-web3-engineering
product: architecture
product_version: "n/a"
scope: likely-general
tags: [on-chain-off-chain, storage-cost, privacy, gas]
confidence: medium
reviewed: false
---

## Problem

A team put rich user-profile metadata directly in contract storage 'so it can't be lost,' and gas costs and a privacy review both flagged it. The risk: every byte on-chain is paid for forever and is publicly readable, so 'on-chain to be safe' is usually wrong on both cost and privacy (§3 #4).

## Context

- Stack: EVM, app storing profile data per user.
- Constraint: on-chain storage is paid-for-forever and public; only consensus-critical data needs to be on-chain (§3 #4).
- The team conflated 'durable' with 'on-chain.'

## Attempts

- Tried: **priced the on-chain storage** via `blockchain_web3_calc.py storage-cost`. Outcome: per-user SSTORE writes made onboarding prohibitively expensive at realistic gas prices (§3 #3 #4).
- Tried: **classified the data** as consensus-critical vs ancillary. Outcome: only an ownership commitment needed to be on-chain; the profile was ancillary (§3 #4).
- Tried: **moved the profile off-chain to IPFS with an on-chain content hash.** Outcome: integrity preserved, cost collapsed, and no public PII on-chain (§3 #4).

## Resolution

The fix was to **keep only a hash/pointer on-chain and store the profile off-chain on IPFS** — a deliberate cost-and-privacy decision, not 'on-chain to be safe.' The output was the storage-cost comparison, the data classification, and the hash-pointer design.

**Action for the next consultant hitting this pattern:** **decide on/off-chain on cost AND privacy — never 'on-chain to be safe.'** Put only consensus-critical data on-chain and push the rest off-chain behind an on-chain hash pointer; on-chain bytes are paid-for-forever and public. See Tree 2 and the `storage-cost` mode (§3 #3 #4).

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
