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
covers_digest: "sha256:aab5c1c185347e87698163f4dbf693b9a632ca889a5a9b3c2187caca5b34dd6e"
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
