---
id: probing-a-script-runs-it
title: "Asking a script a question runs it"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 912
summary: "Asking a script a question is not free: one that ignores arguments simply runs."
last_verified: 2026-08-20
covers:
  - scripts/inventory-sweep.py
  - scripts/audit-prose-rendering-path.py
covers_digest: "sha256:ce946fc704195d1519164d4d58837add70d2e069a42b5c43c4173f4c15131e0c"
nuance: "A script that never calls `argparse` simply runs, so asking 183 of them for `--must-fail-convention` wrote `forge-route.py` to a stray file rather than answering."
nuance_evidence:
  measured: 2026-08-19
  control: "the same sweep after grepping first left the tree clean and finished in 33 seconds"
  falsifier: "an argument-probing sweep leaving no artefact behind"
  probe: "scripts/inventory-sweep.py"
nuance_source: "scripts/inventory-sweep.py:1-60"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "scripts/inventory-sweep.py"
  teeth_exit: 1
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

the same sweep after grepping first left the tree clean and finished in 33 seconds

## The discriminator

control: the same sweep after grepping first left the tree clean and finished in 33 seconds
Measured 2026-08-19: A script that never calls `argparse` simply runs, so asking 183 of them for `--must-fail-convention` wrote `forge-route.py` to a stray file rather than answering.

## Why it matters

Falsifier: an argument-probing sweep leaving no artefact behind

Probe: `scripts/inventory-sweep.py`
