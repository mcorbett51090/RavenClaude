---
scenario_id: 2026-06-08-reentrancy-shipped-no-hotfix
contributed_at: 2026-06-08
plugin: blockchain-web3-engineering
product: security
product_version: "n/a"
scope: likely-general
tags: [reentrancy, checks-effects-interactions, audit-before-deploy, immutability]
confidence: medium
reviewed: false
---

## Problem

A team deployed a non-upgradeable vault whose withdraw sent ETH before zeroing the user's balance, then discovered the ordering after launch. The risk: a deployed contract's bytecode is permanent, so a reentrancy bug ships at the speed of a block and is drained at the speed of a bot — with no hotfix available (§3 #1 #2).

## Context

- Stack: EVM L1, non-upgradeable by design.
- Constraint: checks-effects-interactions requires updating state before any external call, and immutability means the audit is the gate, not a post-launch fix (§3 #1 #2).
- The team reasoned the happy-path unit tests passing meant it was safe.

## Attempts

- Tried: **traced the external-call ordering** before assuming the unit tests sufficed. Outcome: the `call{value:}` ran before the balance was zeroed — a classic reentrancy path (§3 #2).
- Tried: **specified value-conservation invariants and fuzzed them** instead of happy-path-only. Outcome: the fuzzer found a re-entered withdraw that created value from nothing — exactly the off-path state units missed (§3 #5).
- Tried: **applied checks-effects-interactions + a reentrancy guard** and re-ran the fuzz. Outcome: the invariant held; the fix had to land before deploy because there was no hotfix path (§3 #1).

## Resolution

The fix was to **reorder to checks-effects-interactions, add a reentrancy guard, fuzz the value-conservation invariant, and gate deploy on it clearing** — not to patch post-launch, which was impossible. The output was the findings set, the invariant tests, and a held deploy gate.

**Action for the next consultant hitting this pattern:** **audit and fuzz before deploy — there is no hotfix.** Update state before external calls (checks-effects-interactions), add a guard, and fuzz value-conservation invariants because the exploit lives in the state your happy-path tests never reach. See Tree 1 and §3 #1 #2 #5.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
