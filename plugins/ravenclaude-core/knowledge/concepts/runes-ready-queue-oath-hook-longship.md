---
id: runes-ready-queue-oath-hook-longship
title: "Runes ready-queue, Oath-hook, and Longship land-request never merge"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 937
summary: "rc runes ready|claim|hanging plus SessionStart Oath-hook surface hanging work; Longship land-request records Sage intent only and never merges."
last_verified: 2026-09-15
covers:
  - plugins/ravenclaude-core/hooks/oath-hook.sh
  - plugins/ravenclaude-core/scripts/oath_hook.py
  - plugins/ravenclaude-core/scripts/runes.py
covers_digest: "sha256:f5239745556340975cd8e33ac86c57c5b4e98d759103eadeb5aca72b305edbbe"
nuance: "Longship `land-request` writes intent with auto_merge=false and never calls gh/git merge; Oath-hook SessionStart surfaces hanging Runes for the current hook_owner; human_gate=matthew|appsec|sage|cos refuses claim."
nuance_evidence:
  measured: 2026-09-15
  control: "runes.py --self-test: longship land-request returns land_requested true and auto_merge false; human_gate=matthew claim prints REFUSED and does not set hook_owner; oath_hook hanging payload must_run true when a claimed rune is open"
  falsifier: "land-request invoking gh pr merge, or a matthew-gated rune accepting claim, or Oath-hook staying silent while hanging Runes exist for the owner"
  probe: "plugins/ravenclaude-core/scripts/runes.py"
nuance_source: "plugins/ravenclaude-core/scripts/runes.py (cmd_longship_land_request / claim human_gate wall); plugins/ravenclaude-core/scripts/oath_hook.py"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/runes.py"
  teeth_exit: 1
sources:
  - label: "PE DIGEST ship Norse Runes ready-queue (Longship amend), 2026-09-15"
    url: https://github.com/mcorbett51090/RavenClaude/blob/feat/runes-ready-queue/docs/runes-ready-queue.md
  - label: docs/runes-ready-queue.md
    url: https://github.com/mcorbett51090/RavenClaude/blob/feat/runes-ready-queue/docs/runes-ready-queue.md
---

## What a reader would have assumed instead

A delivery-batch CLI that can open a PR and merge it, or a SessionStart hook that is
advisory only — hanging claimed work stays invisible until someone remembers to ask.

## The discriminator

control: `python3 plugins/ravenclaude-core/scripts/runes.py --self-test` exercises
ready/claim/sling, Oath-hook hanging assembly, the human_gate refuse path, strand apply,
and Longship open/add/land-request. Measured 2026-09-15: `land-request` returns
`auto_merge: false` with a Sage-facing message and performs no merge; a Rune with
`human_gate=matthew` prints REFUSED and never sets `hook_owner`.

## Why it matters

Ready-queue UX without an Oath-hook leaves claimed work optional. A Longship that could
merge would bypass Sage sole-SCM. The three surfaces share one ledger projection and keep
product names free of Hird/Beads/Gas Town.

Falsifier: `land-request` invoking `gh pr merge`, a matthew-gated claim succeeding, or
Oath-hook silent while hanging Runes exist for the owner.

Probe: `plugins/ravenclaude-core/scripts/runes.py --self-test` (and
`hooks/tests/test-runes-ready-queue.sh`).
