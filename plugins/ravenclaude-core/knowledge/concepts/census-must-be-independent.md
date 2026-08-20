---
id: census-must-be-independent
title: "A sweep that counts itself"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 910
summary: "Why the coverage denominator is read from git rather than from the registry it measures."
last_verified: 2026-08-20
covers:
  - scripts/inventory-census.py
  - scripts/inventory-sweep.py
  - scripts/inventory-coverage.py
covers_digest: "sha256:47a059f945f720e676ceaea052d738f2b6548d4563c5f68b6944516ddf4e2fa8"
nuance: "`inventory-census.py` reads `git ls-files`, never a filesystem walk, so an untracked file cannot move the denominator; a `concepts.json`-derived count would shrink with the enumeration and stay green."
nuance_evidence:
  measured: 2026-08-19
  control: "planting an untracked hook left the census unchanged, which a filesystem walk would not have"
  falsifier: "an untracked artifact changing the census total"
  probe: "scripts/inventory-census.py"
nuance_source: "scripts/inventory-census.py:1-60"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "scripts/inventory-census.py"
  teeth_exit: 1
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

planting an untracked hook left the census unchanged, which a filesystem walk would not have

## The discriminator

control: planting an untracked hook left the census unchanged, which a filesystem walk would not have
Measured 2026-08-19: `inventory-census.py` reads `git ls-files`, never a filesystem walk, so an untracked file cannot move the denominator; a `concepts.json`-derived count would shrink with the enumeration and stay green.

## Why it matters

Falsifier: an untracked artifact changing the census total

Probe: `scripts/inventory-census.py`
