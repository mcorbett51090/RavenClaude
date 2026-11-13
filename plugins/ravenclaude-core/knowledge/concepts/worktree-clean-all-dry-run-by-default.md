---
id: worktree-clean-all-dry-run-by-default
title: "A bulk cleanup that previews before it touches anything"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 947
summary: "Why a bulk worktree sweep is safe to run blind: --all alone never removes anything."
last_verified: 2026-11-10
covers:
  - plugins/ravenclaude-core/scripts/worktree-clean.sh
  - plugins/ravenclaude-core/scripts/worktree-cleanup-report.sh
covers_digest: "sha256:54c3e56ca08066bcdeabec0115a64e8ef1e9ae32626b08fd852650c4a5bd793d"
nuance: "Unlike a typical bulk-cleanup command, `--all` alone never removes anything — it only PREVIEWS what `--execute` would do, worktree by worktree; the SessionEnd report hook reuses that same preview mode, so it can run on every session close without ever mutating a worktree."
nuance_evidence:
  measured: 2026-11-10
  control: "a plain --all run left a genuinely clean, removable worktree on disk untouched, and the output was labeled DRY RUN"
  falsifier: "a plain --all run (no --execute) deleting any worktree"
  probe: "plugins/ravenclaude-core/hooks/tests/test-worktree-clean-lifecycle.sh"
nuance_source: "plugins/ravenclaude-core/scripts/worktree-clean.sh:27-38"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/hooks/tests/test-worktree-clean-lifecycle.sh"
  teeth_exit: 1
sources:
  - label: "worktree-clean.sh usage doc + P12/T2 of its own lifecycle test"
    url: "plugins/ravenclaude-core/hooks/tests/test-worktree-clean-lifecycle.sh"
---

## What a reader would have assumed instead

A `--all` bulk-cleanup flag mutates immediately, the way most bulk-delete commands do.

## The discriminator

control: a plain `--all` run left a genuinely clean, removable worktree on disk untouched, and the output was labeled DRY RUN
Measured 2026-11-10: `--all` alone only previews — framed as what `--execute` would do to each worktree — and never passes `--force` even once `--execute` is given. The SessionEnd report hook (`worktree-cleanup-report.sh`) runs the same `--status`/preview path on every session close, which is exactly what makes an always-on hook safe: there is no mutating code path for it to accidentally reach.

## Why it matters

Falsifier: a plain `--all` run (no `--execute`) deleting any worktree.

Probe: `plugins/ravenclaude-core/hooks/tests/test-worktree-clean-lifecycle.sh` (P12a/P12b/T2 exercise exactly this contract, including a teeth check that neuters the `--execute` gate and confirms a plain `--all` then mutates).
