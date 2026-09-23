---
id: caveman-auto-routing-packaging
title: "Caveman auto-routing: scripts/ packaging exception, live-apply since P7"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 919
summary: "The caveman auto-routing hook ships from scripts/ because a new hooks/*.sh chmod is denied. Since P7, live posture calls the mode applier (on→lite, off→off); shadow still never applies."
last_verified: 2026-09-10
covers:
  - plugins/ravenclaude-core/scripts/caveman-route.py
  - plugins/ravenclaude-core/scripts/caveman-apply-mode.sh
  - plugins/ravenclaude-core/scripts/caveman-route-hook.sh
  - plugins/ravenclaude-core/scripts/caveman-route-engine.py
covers_digest: "sha256:e747cee327d3497794420abc9c1ce997eefd78df5ab43f66f216840bf368eb98"
nuance: "caveman-route-hook.sh ships from scripts/, not hooks/ -- a NEW hooks/*.sh chmod is denied,\nsame reason ask-on-ambiguity.sh lives there. P7 live calls the applier (on→lite, off→off);\nshadow still records only. Absent/off is the default and writes nothing."
nuance_evidence:
  measured: 2026-09-10
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
this plugin, and (before P7) that turning the posture knob to `live` would still only decide and
record.

## The discriminator

control: ask-on-ambiguity.sh (also in scripts/, registered via the identical bash-prefixed escape)
already proves the substrate guard denies a NEW hooks/*.sh chmod but not a scripts/*.sh one -- the same
escape pattern, reused rather than re-argued from scratch
Measured 2026-09-10: caveman-route-hook.sh still ships from scripts/, not hooks/. P7 wires
live-apply in caveman-route-engine.py: classifier on→lite, off→off, hold never applies,
shadow never calls the applier. Default remains absent/off. Owner overrode the uncleared
P5 soak gates; this is not a claim that soak passed.

## Why it matters

Falsifier: a git history showing hooks/caveman-route-hook.sh ever existed in this repo with its
executable bit successfully set.

Probe: `plugins/ravenclaude-core/hooks/tests/test-gate264-caveman-routing.sh`
