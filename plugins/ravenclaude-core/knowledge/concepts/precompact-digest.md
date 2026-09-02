---
id: precompact-digest
title: "The PreCompact digest hook never waits on its own engine"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 915
summary: "precompact-digest.sh detaches its engine call so the archival hook can never turn into a synchronous ceiling on a turn."
last_verified: 2026-09-01
covers:
  - plugins/ravenclaude-core/hooks/precompact-digest.sh
  - plugins/ravenclaude-core/scripts/precompact-digest.py
covers_digest: "sha256:aeac8a553d4278ae3b506bbb99d9bfbb80af9cb6b0472c867d88d29975cd3d31"
nuance: "The hook returns near-instantly even when its digest engine takes seconds: extraction runs as a detached, disowned worker the hook never waits on, so a digest (when one appears at all) shows up seconds after the hook process has already exited."
nuance_evidence:
  measured: 2026-09-01
  control: "driven against a deliberately 3s-slow stub delegate: the hook returned in under 2000ms while the digest file appeared only afterward, proving detachment structurally rather than assuming the real path happens to be fast"
  falsifier: "the hook blocking on the digest engine before returning (LAST_MS exceeding the 2000ms bound in Gate 254's success case)"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate254-precompact-digest.sh"
nuance_source: "plugins/ravenclaude-core/hooks/precompact-digest.sh:28-46"
verify:
  tier: "effect"
  strength: "executed"
  class: "hook-selftest"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate254-precompact-digest.sh"
  teeth_exit: 1
sources:
  - label: "P2 of the precompact-critical-context FORGE plan, hardened per the P4 security review"
    url: "plugins/ravenclaude-core/hooks/precompact-digest.sh"
---

## What a reader would have assumed instead

That a `PreCompact` archival hook calling a Python digest engine would run synchronously — wait for
the engine, then return — the same shape most hooks in this repo use for a short-lived call.

## The discriminator

control: driven against a deliberately 3s-slow stub delegate — the hook returned in under 2000ms while
the digest file appeared only afterward, proving detachment structurally rather than assuming the real
path happens to be fast.

Measured 2026-09-01: `precompact-digest.sh` backgrounds its engine call (`( _pcd_worker & )` inside a
subshell that itself exits immediately) rather than waiting on it. A prior synchronous design ran the
engine under a 10s ceiling — far below the engine's own 60s/90s subprocess budgets — so on the real
path no digest was ever produced, while any egress to an external processor had already happened
before the reader was killed. The detached shape fixes both: this hook adds no ceiling of its own on
top of the engine's own internal timeouts, and it never blocks a turn regardless of how long extraction
takes.

## Why it matters

Falsifier: the hook blocking on the digest engine before returning.

Probe: `plugins/ravenclaude-core/hooks/tests/test-gate254-precompact-digest.sh`

`PreCompact` fires just before a session's context is summarized away — the same moment its own
digest engine is racing to read the untouched transcript. A hook that can block on that engine, even
briefly, risks becoming exactly the "data left, no benefit arrived" failure the P4 security review
found in the prior design: egress happens, but the digest the hook was supposed to produce never does,
because the reader was killed first. Detachment removes that race by construction rather than by
tuning a timeout.
