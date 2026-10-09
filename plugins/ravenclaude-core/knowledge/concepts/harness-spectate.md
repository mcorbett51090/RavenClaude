---
id: harness-spectate
title: "Harness Spectate — observe-only agent loop livestream"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 910
summary: "Spectate reduces scrubbed JSONL into a loop graph; empty streams stay idle with cause-not-established, and unknown capability cells never upgrade to unavailable-harness."
last_verified: 2026-10-09
covers:
  - plugins/ravenclaude-core/scripts/spectate_store.py
  - plugins/ravenclaude-core/scripts/spectate_demo.py
  - plugins/ravenclaude-core/commands/spectate.md
  - scripts/check-spectate.py
  - plugins/ravenclaude-core/hooks/spectate-emit.sh
  - plugins/ravenclaude-core/hooks/spectate-steer.sh
covers_digest: "sha256:8e27f0183fee75cd46baa3fedde4062fea9c7b304a0924dd23e51b2626532476"
nuance: "An empty Spectate stream reduces every node to idle with cause-not-established; a capability cell whose state is unknown never reduces to unavailable-harness."
nuance_evidence:
  measured: 2026-10-09
  control: "grok-bot and grok-build gallery fixtures keep unknown cells while a seeded empty stream yields idle + cause-not-established"
  falsifier: "an unknown cell rendered as unavailable-harness, or an empty stream upgrading idle without the cause phrase"
  probe: "scripts/check-spectate.py"
nuance_source: "scripts/check-spectate.py"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "scripts/check-spectate.py --must-fail"
  teeth_exit: 3
sources:
  - label: "Harness Spectate BUILD-PLAN"
    url: "docs/plans/2026-10-09-harness-spectate/BUILD-PLAN.md"
---

## What a reader would have assumed instead

That a missing stream meant the harness lacked the step (`unavailable-harness`), or that idle without a cause phrase was enough.

## The discriminator

control: grok-bot and grok-build gallery fixtures keep unknown cells while a seeded empty stream yields idle + cause-not-established
Measured 2026-10-09: An empty Spectate stream reduces every node to idle with cause-not-established; a capability cell whose state is unknown never reduces to unavailable-harness.

## Why it matters

Spectate is observe-only honesty infrastructure. Collapsing unknown into unavailable-harness would invent evidence; dropping the cause phrase on idle would hide that the absence was never explained.
