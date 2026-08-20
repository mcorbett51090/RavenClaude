---
id: must-fail-conventions-diverge
title: "must-fail conventions diverge"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 904
summary: "Every self-testing tool declares its own teeth-bit exit, because no single number fits all."
last_verified: 2026-08-20
covers:
  - scripts/audit-gates.sh
  - scripts/check-covers-completeness.py
  - scripts/check-inventory-evidence.py
  - scripts/check-artifact-budgets.py
  - scripts/check-nuance-floor.py
  - scripts/inventory-census.py
  - scripts/inventory-sweep.py
  - scripts/check-inception-coverage.py
  - scripts/check-ratchet-freshness.py
  - scripts/spike-selfheal-contract.sh
  - scripts/audit-prose-rendering-path.py
  - scripts/check-changed-concept-renders.py
  - scripts/inventory-coverage.py
  - scripts/inventory-nuance-judge.py
covers_digest: "sha256:332903c6e5ab2c780888e8bfa7cfa1d53ef35647abb29a54c7c4014f6c0ff86d"
nuance: "`premise-gate.py` treats `exit 0` as its teeth bit while `sync-plugin-versions.py` uses `exit 2`, so an auditor that hard-codes one number can never be right for both."
nuance_evidence:
  measured: 2026-08-19
  control: "each tool `--must-fail-convention` is read first and compared against its observed exit"
  falsifier: "both tools returning the same teeth exit"
  probe: "scripts/audit-gates.sh"
nuance_source: "scripts/audit-gates.sh:1-40"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "scripts/audit-gates.sh"
  teeth_exit: 1
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

each tool `--must-fail-convention` is read first and compared against its observed exit

## The discriminator

control: each tool `--must-fail-convention` is read first and compared against its observed exit
Measured 2026-08-19: `premise-gate.py` treats `exit 0` as its teeth bit while `sync-plugin-versions.py` uses `exit 2`, so an auditor that hard-codes one number can never be right for both.

## Why it matters

Falsifier: both tools returning the same teeth exit

Probe: `scripts/audit-gates.sh`
