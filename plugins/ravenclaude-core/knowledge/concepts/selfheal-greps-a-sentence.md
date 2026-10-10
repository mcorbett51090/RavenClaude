---
id: selfheal-greps-a-sentence
title: "The self-heal grep contract"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 908
summary: "How a failing registry check decides whether the post-merge self-heal survives."
last_verified: 2026-10-10
covers:
  - .github/workflows/regenerate-artifacts.yml
  - scripts/concepts.py
  - scripts/spike-selfheal-contract.sh
covers_digest: "sha256:3e59db309dd91ecfe3e1963bb60e3eb01b3e10b010b6922d6456226cc92e216a"
nuance: "`regenerate-artifacts.yml` greps `RC-CONCEPTS-CLASS: human-reverify-required` (plus a one-release prose OR-fallback); an unmarked class runs `exit '$_crc'` and every later self-heal step is skipped."
nuance_evidence:
  measured: 2026-08-19
  control: "the human-reverify marker replays as survivable while an unmarked line replays as fatal"
  falsifier: "an unmarked failure class continuing the self-heal"
  probe: "scripts/spike-selfheal-contract.sh"
nuance_source: ".github/workflows/regenerate-artifacts.yml:198-216"
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
Measured 2026-08-19 (re-verified 2026-10-10 after CI-05 `add-paths`): the self-heal greps `RC-CONCEPTS-CLASS: human-reverify-required` (with a one-release OR-fallback on the prose `staleness gate FAILED`); an unmarked class still runs `exit "$_crc"` and every later self-heal step is skipped. `add-paths` does not touch this contract.

## Why it matters

Falsifier: an unmarked failure class continuing the self-heal

Probe: `scripts/spike-selfheal-contract.sh`
