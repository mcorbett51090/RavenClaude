---
id: plugin-cache-is-version-keyed
title: "Merged is not live"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 903
summary: "Why a merged fix does not reach an installed session until the version field moves."
last_verified: 2026-08-25
covers:
  - plugins/ravenclaude-core/.claude-plugin/plugin.json
  - scripts/sync-plugin-versions.py
  - scripts/generate-copilot-plugin.py
covers_digest: "sha256:4f7a67d4a972ff47a3f3be49363e3b3aeb2a0986b3b5caa8784ab48b39f99121"
nuance: "The cache key is the `version` string, never a content hash, so `sync-plugin-versions.py` can report clean while every installed session keeps running the old `hooks/` code."
nuance_evidence:
  measured: 2026-08-19
  control: "a bumped version propagated on the next update while an unbumped one did not"
  falsifier: "an installed cache picking up an unbumped change"
  probe: "unprobed: requires a real consumer install cycle, which no CI job performs"
nuance_source: "plugins/ravenclaude-core/.claude-plugin/plugin.json:1-10"
verify:
  tier: "reachability"
  strength: "static"
  class: "static-resolution"
  probe: "scripts/sync-plugin-versions.py"
  teeth_exit: 2
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

a bumped version propagated on the next update while an unbumped one did not

## The discriminator

control: a bumped version propagated on the next update while an unbumped one did not
Measured 2026-08-19: The cache key is the `version` string, never a content hash, so `sync-plugin-versions.py` can report clean while every installed session keeps running the old `hooks/` code.

## Why it matters

Falsifier: an installed cache picking up an unbumped change

Probe: `unprobed: requires a real consumer install cycle, which no CI job performs`
