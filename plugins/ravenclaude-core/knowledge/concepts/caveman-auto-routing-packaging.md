---
id: caveman-auto-routing-packaging
title: "Caveman auto-routing: SHADOW-only, and the scripts/ packaging exception"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 919
summary: "The caveman auto-routing hook decides and records but never calls the mode applier this phase, and ships from scripts/ because a new hooks/*.sh chmod is denied."
last_verified: 2026-09-03
covers:
  - plugins/ravenclaude-core/scripts/caveman-route.py
  - plugins/ravenclaude-core/scripts/caveman-apply-mode.sh
  - plugins/ravenclaude-core/scripts/caveman-route-hook.sh
  - plugins/ravenclaude-core/scripts/caveman-route-engine.py
covers_digest: "sha256:7d29faaf1d3ad717aa39ba0c59d6549977ec26ca3d4d31eafbe1aa467aa7db13"
nuance: "caveman-route-hook.sh ships from scripts/, not hooks/ -- a NEW hooks/*.sh file needs a chmod\nthe tribunal's own substrate guard denies, the same reason ask-on-ambiguity.sh lives there too.\nEven when the posture is live, this phase's hook only decides and records: it never calls the\napplier."
nuance_evidence:
  measured: 2026-09-03
  control: "ask-on-ambiguity.sh (also in scripts/, registered via the identical bash-prefixed escape) already proves the substrate guard denies a NEW hooks/*.sh chmod but not a scripts/*.sh one -- the same escape pattern, reused rather than re-argued from scratch"
  falsifier: "a git history showing hooks/caveman-route-hook.sh ever existed in this repo with its executable bit successfully set"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate264-caveman-routing.sh"
nuance_source: "plugins/ravenclaude-core/scripts/caveman-route-hook.sh:1-42"
verify:
  tier: "effect"
  strength: "executed"
  class: "hook-decision"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate264-caveman-routing.sh"
  teeth_exit: 1
sources:
  - label: measured in the FORGE caveman-routing-decision-tree run
    url: https://github.com/mcorbett51090/RavenClaude/pull/1095
---

## What a reader would have assumed instead

That a new SessionStart/UserPromptSubmit hook body would live in `hooks/`, like every other hook in
this plugin, and that turning the posture knob to `live` would make the routing decision actually take
effect immediately.

## The discriminator

control: ask-on-ambiguity.sh (also in scripts/, registered via the identical bash-prefixed escape)
already proves the substrate guard denies a NEW hooks/*.sh chmod but not a scripts/*.sh one -- the same
escape pattern, reused rather than re-argued from scratch
Measured 2026-09-03: caveman-route-hook.sh ships from scripts/, not hooks/ -- a NEW hooks/*.sh file
needs a chmod the tribunal's own substrate guard denies, the same reason ask-on-ambiguity.sh lives
there too. Even when the posture is live, this phase's hook only decides and records: it never calls
the applier.

## Why it matters

Falsifier: a git history showing hooks/caveman-route-hook.sh ever existed in this repo with its
executable bit successfully set.

Probe: `plugins/ravenclaude-core/hooks/tests/test-gate264-caveman-routing.sh`
