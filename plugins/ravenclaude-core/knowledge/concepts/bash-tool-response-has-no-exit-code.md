---
id: bash-tool-response-has-no-exit-code
title: "A failing Bash tool_response"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 905
summary: "What a post-failure hook can and cannot read after a Bash call fails."
last_verified: 2026-08-25
covers:
  - plugins/ravenclaude-core/hooks/triage-outcome.sh
covers_digest: "sha256:9a2df20ae75bb49090262342007b0a89fee94d0c4f62e7a9099fc5ce09dc9ed2"
nuance: "A failing Bash `tool_response` carries no exit-code field at all, so a hook that branches on `.tool_response.exit_code` never fires; `triage-outcome.sh` reads stream shape instead."
nuance_evidence:
  measured: 2026-08-19
  control: "the same payload shape with a synthetic exit field present did branch"
  falsifier: "a real failing Bash payload carrying an exit code"
  probe: "unprobed: the payload shape is host-supplied and cannot be synthesised faithfully offline"
nuance_source: "plugins/ravenclaude-core/hooks/triage-outcome.sh:1-40"
verify:
  tier: "none"
  rationale: "The payload shape is supplied by the host and cannot be synthesised faithfully offline; a synthetic fixture would assert the shape this entry says is absent."
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

the same payload shape with a synthetic exit field present did branch

## The discriminator

control: the same payload shape with a synthetic exit field present did branch
Measured 2026-08-19: A failing Bash `tool_response` carries no exit-code field at all, so a hook that branches on `.tool_response.exit_code` never fires; `triage-outcome.sh` reads stream shape instead.

## Why it matters

Falsifier: a real failing Bash payload carrying an exit code

Probe: `unprobed: the payload shape is host-supplied and cannot be synthesised faithfully offline`
