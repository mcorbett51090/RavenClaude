---
id: islanded-panel-costs-two
title: "An islanded panel costs two"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 911
summary: "What the DOM budget measures, and the far larger number it does not."
last_verified: 2026-08-25
covers:
  - scripts/check-dom-budget.py
  - scripts/check-artifact-budgets.py
  - scripts/generate-dashboards.py
  - scripts/generate-index-dashboard.py
covers_digest: "sha256:47a239fc9a5869dc4cfb85114bdd79e525e96e31ecc6d2b5932c72bfe8e0ab6f"
nuance: "`ISLANDED_PANEL_COST` is a flat 2 because the parser reads the payload as CDATA, so `check-dom-budget.py` cannot fire on `learn-payload` no matter how far past 23,861 elements it grows."
nuance_evidence:
  measured: 2026-08-19
  control: "the payload counter reports 23,861 for learn-payload while the live gate reports it as two"
  falsifier: "the live-element gate ever failing on payload growth alone"
  probe: "scripts/check-artifact-budgets.py"
nuance_source: "scripts/check-dom-budget.py:95-135"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "scripts/check-artifact-budgets.py"
  teeth_exit: 1
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

the payload counter reports 23,861 for learn-payload while the live gate reports it as two

## The discriminator

control: the payload counter reports 23,861 for learn-payload while the live gate reports it as two
Measured 2026-08-19: `ISLANDED_PANEL_COST` is a flat 2 because the parser reads the payload as CDATA, so `check-dom-budget.py` cannot fire on `learn-payload` no matter how far past 23,861 elements it grows.

## Why it matters

Falsifier: the live-element gate ever failing on payload growth alone

Probe: `scripts/check-artifact-budgets.py`
