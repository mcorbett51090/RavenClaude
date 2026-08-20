---
id: staleness-double-exemption
title: "The staleness double exemption"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 909
summary: "Which concepts the staleness gate actually covered, and the two ways one escaped it."
last_verified: 2026-08-20
covers:
  - scripts/concepts.py
  - scripts/check-covers-completeness.py
covers_digest: "sha256:62fcb0365fc11fd6957f7b8b4267c04d9aa488ac6d700d1ce6f5e3cca08585b1"
nuance: "`_staleness_violations` skipped on an OR, so a concept escaped for not being a `platform-fact` or merely for lacking `last_verified`; with 41 `ravenclaude-built` against 17 it gated only the minority kind."
nuance_evidence:
  measured: 2026-08-19
  control: "a fixture entry with the field absent now blocks, and one past the window warns on a PR but fails the sweep"
  falsifier: "an entry with no last_verified passing the gate"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate237-inventory-staleness.sh"
nuance_source: "scripts/concepts.py:271-330"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate237-inventory-staleness.sh"
  teeth_exit: 1
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

a fixture entry with the field absent now blocks, and one past the window warns on a PR but fails the sweep

## The discriminator

control: a fixture entry with the field absent now blocks, and one past the window warns on a PR but fails the sweep
Measured 2026-08-19: `_staleness_violations` skipped on an OR, so a concept escaped for not being a `platform-fact` or merely for lacking `last_verified`; with 41 `ravenclaude-built` against 17 it gated only the minority kind.

## Why it matters

Falsifier: an entry with no last_verified passing the gate

Probe: `plugins/ravenclaude-core/hooks/tests/test-gate237-inventory-staleness.sh`
