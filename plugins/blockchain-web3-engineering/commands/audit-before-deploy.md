---
description: "Gate deploy on a security audit and invariant tests across the top vuln classes — deploy is irreversible. Reach for this before any mainnet go-live."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Audit before deploy

You are running `/blockchain-web3-engineering:audit-before-deploy` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Check the top three — Reentrancy (checks-effects-interactions + guard), access control (modifiers/init), arithmetic (overflow/rounding) first (§3 #2).
2. Model the threat surface — Add oracle manipulation, flash loans, and MEV to the code review (§3 #7).
3. Specify and fuzz invariants — Value-conservation and access invariants property/fuzz-tested, not just happy-path units (§3 #5).
4. Gate the deploy — No go-live until the findings clear and the testnet exercise passes (§3 #1).

## Output
A severity-ranked findings set gating deploy, with invariant/fuzz coverage and the threat surface named. Traverse Tree 1 in the decision-trees file. See [`../skills/audit-before-deploy/SKILL.md`](../skills/audit-before-deploy/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No private keys / wallet data in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
