---
id: cross-plugin-invocation
title: "Cross-plugin names resolve exactly"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 904
summary: "A call into another plugin is an exact catalog name plus a real directory, or a refusal. No prefix match and no nearest-name fallback."
see_also: [plugin-lifecycle]
last_verified: 2026-11-16
refresh_when: "Name rules, depth cap, tool refusal, or the resolver's refusal reasons change."
covers:
  - plugins/ravenclaude-core/scripts/cross-plugin-invoke.py
covers_digest: "sha256:8a06b63046ed788e36be1d10cfff1f14398a5d3fc83cfdad18bee2f53bc56ec5"
nuance: "resolve refuses traversal, absolute paths, symlinks, prefix names, the wrong kind, over-privileged tools, cycles, and depth above 3. It does not start a shell. check fails when a written plugin/target does not exist."
nuance_evidence:
  measured: 2026-11-16
  control: "python3 plugins/ravenclaude-core/scripts/cross-plugin-invoke.py --self-test"
  falsifier: "a prefix name, a traversal, or an unknown target returning a plan"
  probe: "plugins/ravenclaude-core/scripts/cross-plugin-invoke.py"
nuance_source: "plugins/ravenclaude-core/scripts/cross-plugin-invoke.py"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/cross-plugin-invoke.py"
  teeth_exit: 1
sources:
  - label: "scripts/cross-plugin-invoke.py"
    url: "plugins/ravenclaude-core/scripts/cross-plugin-invoke.py"
---

## What a reader would have assumed instead

A near name is close enough, and a missing target falls through to a similar agent.

## The discriminator

control: `python3 plugins/ravenclaude-core/scripts/cross-plugin-invoke.py --self-test` (pass on 2026-11-16).
A prefix of a real plugin name, a `../` path, a symlink out of `plugins/`, and an unknown target each exit 2 with a reason and no suggestion list.

## Why it matters

The Team Lead is the only caller, and the plan it gets is the tool list it may pass on.

Falsifier: a prefix name, a traversal, or an unknown target returning a plan.

Probe: `plugins/ravenclaude-core/scripts/cross-plugin-invoke.py`.
