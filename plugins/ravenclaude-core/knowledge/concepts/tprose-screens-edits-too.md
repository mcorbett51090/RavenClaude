---
id: tprose-screens-edits-too
title: "T-PROSE is not CREATE-only"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 906
summary: "The premise guard prose screen is not limited to newly created files."
last_verified: 2026-08-20
covers:
  - plugins/ravenclaude-core/hooks/guard-premise.sh
  - docs/best-practices/inventory-authoring.md
covers_digest: "sha256:04c18944b458abfb396661569ad8e493875afcbd8da9fc98cca896d689d8bd2f"
nuance: "The `os.path.exists` early-exit gates T-SHAPE only, so `guard-premise.sh` screens an `Edit` too; a re-stamp escapes because `new_string` carries no defect predicate, not because edits are exempt."
nuance_evidence:
  measured: 2026-08-19
  control: "the identical body denied as a Write and as an Edit, while a benign body on the same path allowed"
  falsifier: "a stamped diagnosis passing when sent as an Edit"
  probe: "scripts/spike-tprose-canary.sh"
nuance_source: "plugins/ravenclaude-core/hooks/guard-premise.sh:320-462"
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

the identical body denied as a Write and as an Edit, while a benign body on the same path allowed

## The discriminator

control: the identical body denied as a Write and as an Edit, while a benign body on the same path allowed
Measured 2026-08-19: The `os.path.exists` early-exit gates T-SHAPE only, so `guard-premise.sh` screens an `Edit` too; a re-stamp escapes because `new_string` carries no defect predicate, not because edits are exempt.

## Why it matters

Falsifier: a stamped diagnosis passing when sent as an Edit

Probe: `scripts/spike-tprose-canary.sh`
