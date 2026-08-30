---
id: must-fail-conventions-diverge
title: "must-fail conventions diverge"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 904
summary: "Every self-testing tool declares its own teeth-bit exit, because no single number fits all."
last_verified: 2026-08-25
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
  - scripts/_base_ref.py
  - scripts/spike-selfheal-contract.sh
  - scripts/audit-prose-rendering-path.py
  - scripts/check-changed-concept-renders.py
  - scripts/inventory-coverage.py
  - scripts/inventory-nuance-judge.py
covers_digest: "sha256:69e548655966b677e3c182b4ead62081a01fdc0ceb94eea41a289e357aadb4a3"
nuance: "The teeth bit is the exit a tool own CHECK returns on a planted defect, never the exit `--must-fail` itself returns: `premise-gate.py` denies at `exit 0` while `sync-plugin-versions.py` reddens at `exit 2`, so an auditor that hard-codes one number can never be right for both."
nuance_evidence:
  measured: 2026-08-19
  control: "ran --must-fail on both: each exits 0 on success, so the 0-vs-2 divergence is in the CHECK exit each teeth run observes, not in the teeth exit itself"
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

ran --must-fail on both: each exits 0 on success, so the 0-vs-2 divergence is in the CHECK exit each teeth run observes, not in the teeth exit itself

## The discriminator

control: ran --must-fail on both: each exits 0 on success, so the 0-vs-2 divergence is in the CHECK exit each teeth run observes, not in the teeth exit itself
Measured 2026-08-19: The teeth bit is the exit a tool own CHECK returns on a planted defect, never the exit `--must-fail` itself returns: `premise-gate.py` denies at `exit 0` while `sync-plugin-versions.py` reddens at `exit 2`, so an auditor that hard-codes one number can never be right for both.

## Why it matters

Falsifier: both tools returning the same teeth exit

Probe: `scripts/audit-gates.sh`
