---
id: hook-emitter-collision
title: "Two emitters on one event"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 902
summary: "Two hooks registered on one event both emit. What the host does with the second payload."
last_verified: 2026-08-25
covers:
  - plugins/ravenclaude-core/hooks/hooks.json
covers_digest: "sha256:a519704d9af89156b83eafe3a8e8cd1817300254ef7d181519f69d106e3fcc96"
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
