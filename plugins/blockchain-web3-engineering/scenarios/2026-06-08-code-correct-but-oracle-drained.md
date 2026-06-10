---
scenario_id: 2026-06-08-code-correct-but-oracle-drained
contributed_at: 2026-06-08
plugin: blockchain-web3-engineering
product: economics
product_version: "n/a"
scope: likely-general
tags: [oracle-manipulation, flash-loan, mev, economic-attack]
confidence: medium
reviewed: false
---

## Problem

A lending protocol passed a code audit but priced collateral from a spot DEX pool, and an attacker flash-loaned the pool to skew that price and borrow against inflated collateral. The risk: a contract can be code-correct and still be economically drained when its oracle or incentive design is part of an un-modeled attack surface (§3 #7).

## Context

- Stack: EVM DeFi lending, collateral priced from an on-chain DEX spot price.
- Constraint: spot DEX prices are manipulable within a single block, and flash loans supply the capital to do it — economic surface is part of the threat model (§3 #7).
- The team reasoned that a passing code audit meant the protocol was safe.

## Attempts

- Tried: **mapped the economic attack surface** beyond the code, not just the reentrancy/access checks. Outcome: the spot-price oracle was the single point of manipulation (§3 #7).
- Tried: **simulated a flash-loan-amplified price skew.** Outcome: a one-block manipulation moved the collateral valuation enough to over-borrow and drain — code-correct, economically broken (§3 #7).
- Tried: **moved pricing to a TWAP / multiple independent sources** and bounded the amplified path. Outcome: the single-block manipulation no longer moved the reference price enough to exploit (§3 #7).

## Resolution

The fix was to **replace the spot-price oracle with a TWAP / multi-source feed and stress the design under flash loans** — treating economic surface as part of the threat model, not assuming a code audit covered it. The output was the economic-attack map, the oracle redesign, and a not-financial-advice marking on the economics. Classification/investment questions routed to counsel (§2).

**Action for the next consultant hitting this pattern:** **a code-correct contract can still be drained — model the economic surface.** Never price from a spot DEX feed (use TWAP/multi-source), stress for flash-loan amplification and MEV, and keep economics outputs illustrative — routing investment/securities/tax to a licensed authority. See Tree 3 and §3 #7 #8.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
