---
description: "Triage and fix flaky tests: find the nondeterminism, fix it or quarantine with an owner."
argument-hint: "[failing test(s) / symptom]"
---

You are running `/qa-test-automation:de-flake`. Use `e2e-automation-engineer` / `test-infrastructure-engineer`.

## Steps
1. Traverse the flake-triage tree (sleeps / shared state / real time-network-RNG / order).
2. Apply the determinism fix; if not fixable now, quarantine out of the required gate + owner.
3. Log it (use `templates/flaky-test-quarantine.md`).
4. Emit + Structured Output block.
