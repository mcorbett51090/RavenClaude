---
name: audit-before-deploy
description: "Gate deploy on a security audit and invariant tests across the top vuln classes — deploy is irreversible. Reach for this before any mainnet go-live."
---

# Skill: Audit before deploy

A non-upgradeable contract has no hotfix; shipping unaudited is shipping an exploit (§3 #1).

## Step 1 — Check the top three
Reentrancy (checks-effects-interactions + guard), access control (modifiers/init), arithmetic (overflow/rounding) first (§3 #2).

## Step 2 — Model the threat surface
Add oracle manipulation, flash loans, and MEV to the code review (§3 #7).

## Step 3 — Specify and fuzz invariants
Value-conservation and access invariants property/fuzz-tested, not just happy-path units (§3 #5).

## Step 4 — Gate the deploy
No go-live until the findings clear and the testnet exercise passes (§3 #1).

## Output
A severity-ranked findings set gating deploy, with invariant/fuzz coverage and the threat surface named. Traverse Tree 1 in the decision-trees file.
