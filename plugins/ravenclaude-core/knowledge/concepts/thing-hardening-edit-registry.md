---
id: thing-hardening-edit-registry
title: "Thing hardening EDIT default ON; OFF remains shape-sensitive"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 938
summary: "A signed transform registry can rewrite Bash via empty-cited EDIT, gated by hardening_edit."
last_verified: 2026-09-18
covers:
  - plugins/ravenclaude-core/scripts/thing-harden.py
  - plugins/ravenclaude-core/hooks/thing-orchestrator.sh
covers_digest: "sha256:9bf8c4e11d36b0e8165ff291b1e83be7ca671fe918a08c4f0d7b39acc8c33100"
nuance: "AppSec enable GO flipped seed/default hardening_edit ON (2026-09-16); with explicit false, empty-cited EDIT outside the orchestrator discriminator is DENY rather than ask, while a cited EDIT still allows byte-identical — OFF remains shape-sensitive, not a uniform no-op."
nuance_evidence:
  measured: 2026-09-16
  control: "test-thing-hardening-edit.sh flag-off: empty-cited EDIT → DENY; cited EDIT → allow+updated; registered harden never fires while flag unset"
  falsifier: "flag OFF collapsing empty-cited EDIT to ask, or applying a registry transform while hardening_edit is false"
  probe: "plugins/ravenclaude-core/hooks/tests/test-thing-hardening-edit.sh"
nuance_source: "plugins/ravenclaude-core/scripts/thing-harden.py; plugins/ravenclaude-core/hooks/thing-orchestrator.sh"
verify:
  tier: "effect"
  strength: "executed"
  class: "hook-selftest"
  probe: "plugins/ravenclaude-core/hooks/tests/test-thing-hardening-edit.sh"
  teeth_exit: 1
sources:
  - label: "PE DIGEST ship Thing hardening EDIT (0.323.5), 2026-09-15"
    url: https://github.com/mcorbett51090/RavenClaude/blob/feat/thing-hardening-edit/plugins/ravenclaude-core/knowledge/thing-harden-transforms.yaml
  - label: knowledge/thing-harden-transforms.yaml
    url: https://github.com/mcorbett51090/RavenClaude/blob/feat/thing-hardening-edit/plugins/ravenclaude-core/knowledge/thing-harden-transforms.yaml
---

## What a reader would have assumed instead

That turning the feature flag off would make every EDIT path behave the same — either all
ask, or all no-op — and that an empty-cited safer rewrite would be treated like any other
seat EDIT while the registry sits dark.

## The discriminator

control: `bash plugins/ravenclaude-core/hooks/tests/test-thing-hardening-edit.sh` with the
flag unset/false: empty-cited EDIT → DENY; cited EDIT → allow+updated; registered harden
never fires. Measured 2026-09-15: OFF is shape-sensitive, not a blanket mute.

## Why it matters

AppSec enable GO flipped seed/default `hardening_edit` **ON** (2026-09-16; Gate 14/21/22
green + AppSec SHIP). Explicit `hardening_edit: false` keeps OFF (House Rule 3). Operators
who assume "flag off = no tribunal EDIT policy" would miss the hard DENY on empty-cited
rewrites outside the discriminator — a silent allow would be the dangerous opposite
failure. OFF remains shape-sensitive.

Falsifier: flag OFF collapsing empty-cited EDIT to ask, or applying a registry transform
while `hardening_edit` is false.

Probe: `plugins/ravenclaude-core/hooks/tests/test-thing-hardening-edit.sh`.
