---
id: hook-emitter-collision
title: "Two emitters on one event"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 902
summary: "Two hooks registered on one event both emit. What the host does with the second payload."
last_verified: 2026-10-11
covers:
  - plugins/ravenclaude-core/hooks/hooks.json
  - plugins/ravenclaude-core/hooks/alias-deprecation-advisory.sh
  - plugins/ravenclaude-core/scripts/alias-deprecation-advisory.py
covers_digest: "sha256:23b5ac28feb27a664bad762a9690f10ca544155d5cef40645b2bfe7d38aeeefd"
nuance: "Two `additionalContext` emitters on one event concatenate rather than last-write-wins, but two `updatedToolOutput` emitters replace, so the second silently discards the first."
nuance_evidence:
  measured: 2026-08-19
  control: "a single-emitter run returned exactly one payload, so the doubling is the emitters and not the harness"
  falsifier: "a two-emitter run returning only one additionalContext block"
  probe: "unprobed: needs a live two-hook host session; scheduled for the T2 sampled tier"
nuance_source: "plugins/ravenclaude-core/hooks/hooks.json:1-40"
verify:
  tier: "none"
  rationale: "Two live emitters on one event cannot be staged offline; the observable needs a real host session, which places it in the T2 sampled tier gated on claim 15."
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

a single-emitter run returned exactly one payload, so the doubling is the emitters and not the harness

## The discriminator

control: a single-emitter run returned exactly one payload, so the doubling is the emitters and not the harness
Measured 2026-08-19: Two `additionalContext` emitters on one event concatenate rather than last-write-wins, but two `updatedToolOutput` emitters replace, so the second silently discards the first.

## Why it matters

Falsifier: a two-emitter run returning only one additionalContext block

Probe: `unprobed: needs a live two-hook host session; scheduled for the T2 sampled tier`
