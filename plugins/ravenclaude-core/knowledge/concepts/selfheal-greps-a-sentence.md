---
id: selfheal-greps-a-sentence
title: "The self-heal grep contract"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 908
summary: "How a failing registry check decides whether the post-merge self-heal survives."
last_verified: 2026-08-19
covers:
  - .github/workflows/regenerate-artifacts.yml
  - scripts/concepts.py
  - scripts/spike-selfheal-contract.sh
covers_digest: "sha256:9ad4384f2133790dcc2e17903364c32b25cf6232b30230bd889afb90a632f4fd"
nuance: "`regenerate-artifacts.yml` greps the sentence `staleness gate FAILED`, never a status, so an unrecognised class runs `exit \"$_crc\"` and every later self-heal step is skipped."
nuance_evidence:
  measured: 2026-08-19
  control: "the human-reverify marker replays as survivable while an unmarked line replays as fatal"
  falsifier: "an unmarked failure class continuing the self-heal"
  probe: "scripts/spike-selfheal-contract.sh"
nuance_source: ".github/workflows/regenerate-artifacts.yml:193-206"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "scripts/spike-selfheal-contract.sh"
  teeth_exit: 0
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

the human-reverify marker replays as survivable while an unmarked line replays as fatal

## The discriminator

control: the human-reverify marker replays as survivable while an unmarked line replays as fatal
Measured 2026-08-19: `regenerate-artifacts.yml` greps the sentence `staleness gate FAILED`, never a status, so an unrecognised class runs `exit "$_crc"` and every later self-heal step is skipped.

## Why it matters

Falsifier: an unmarked failure class continuing the self-heal

Probe: `scripts/spike-selfheal-contract.sh`
