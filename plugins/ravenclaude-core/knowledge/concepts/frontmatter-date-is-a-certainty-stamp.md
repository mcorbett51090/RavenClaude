---
id: frontmatter-date-is-a-certainty-stamp
title: "The date you did not think of as a stamp"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 907
summary: "Metadata you did not write as a claim can still arm the guard certainty trigger."
last_verified: 2026-08-20
covers:
  - plugins/ravenclaude-core/hooks/guard-premise.sh
  - scripts/spike-tprose-canary.sh
covers_digest: "sha256:93898f0b02b5309f27d3403a90e3dd565c66b60d4529c2340344420ad4f20e3d"
nuance: "A `last_verified` date is itself a `_STAMP` match, so `guard-premise.sh` arms on metadata rather than on anything the author wrote; only a claim seven lines below the frontmatter escapes the window."
nuance_evidence:
  measured: 2026-08-19
  control: "the same body with no date anywhere was allowed"
  falsifier: "a dated frontmatter failing to arm a nearby claim"
  probe: "scripts/spike-tprose-canary.sh"
nuance_source: "plugins/ravenclaude-core/hooks/guard-premise.sh:393-400"
verify:
  tier: "effect"
  strength: "executed"
  class: "hook-decision"
  probe: "scripts/spike-tprose-canary.sh"
  teeth_exit: 1
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

the same body with no date anywhere was allowed

## The discriminator

control: the same body with no date anywhere was allowed
Measured 2026-08-19: A `last_verified` date is itself a `_STAMP` match, so `guard-premise.sh` arms on metadata rather than on anything the author wrote; only a claim seven lines below the frontmatter escapes the window.

## Why it matters

Falsifier: a dated frontmatter failing to arm a nearby claim

Probe: `scripts/spike-tprose-canary.sh`
