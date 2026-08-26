---
id: hook-message-channels
title: "Hook message channels"
category: "Inventory \u2014 measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 901
summary: "A hook can write to the terminal or to the model, and only one of those reaches the model."
last_verified: 2026-08-25
covers:
  - plugins/ravenclaude-core/hooks/_advise.sh
  - plugins/ravenclaude-core/hooks/_emit-event.sh
  - plugins/ravenclaude-core/hooks/_host-canary.sh
  - plugins/ravenclaude-core/hooks/_model-fallback.sh
  - plugins/ravenclaude-core/hooks/_portable.sh
  - plugins/ravenclaude-core/hooks/_rearm-notice.sh
  - plugins/ravenclaude-core/hooks/_scrub.sh
  - plugins/ravenclaude-core/hooks/agent-dispatch-evaluator.sh
  - plugins/ravenclaude-core/hooks/capability-orientation.sh
  - plugins/ravenclaude-core/hooks/claim-grounding-lint.sh
  - plugins/ravenclaude-core/hooks/codex-hook-env.sh
  - plugins/ravenclaude-core/hooks/compact-anchor.sh
  - plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh
  - plugins/ravenclaude-core/hooks/cursor-hook-adapter.sh
  - plugins/ravenclaude-core/hooks/dashboard-autostart.sh
  - plugins/ravenclaude-core/hooks/delegation-nudge.sh
  - plugins/ravenclaude-core/hooks/dod-gate.sh
  - plugins/ravenclaude-core/hooks/enforce-git-protocol.sh
  - plugins/ravenclaude-core/hooks/enforce-layout.sh
  - plugins/ravenclaude-core/hooks/enforce-portability.sh
  - plugins/ravenclaude-core/hooks/ensure-default-mode.sh
  - plugins/ravenclaude-core/hooks/format-on-write.sh
  - plugins/ravenclaude-core/hooks/gemini-hook-adapter.sh
  - plugins/ravenclaude-core/hooks/guard-destructive.sh
  - plugins/ravenclaude-core/hooks/guard-foreground-suite.sh
  - plugins/ravenclaude-core/hooks/guard-memory-compaction.sh
  - plugins/ravenclaude-core/hooks/guard-premise.sh
  - plugins/ravenclaude-core/hooks/guard-probe-validity.sh
  - plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh
  - plugins/ravenclaude-core/hooks/guard-web-access.sh
  - plugins/ravenclaude-core/hooks/handoff-nudge.sh
  - plugins/ravenclaude-core/hooks/handoff-successor-ack.sh
  - plugins/ravenclaude-core/hooks/keep-awake.sh
  - plugins/ravenclaude-core/hooks/log-probe.sh
  - plugins/ravenclaude-core/hooks/mark-web-domain-seen.sh
  - plugins/ravenclaude-core/hooks/reapply-posture.sh
  - plugins/ravenclaude-core/hooks/regen-on-manifest-change.sh
  - plugins/ravenclaude-core/hooks/remind-tests.sh
  - plugins/ravenclaude-core/hooks/route-decision-review.sh
  - plugins/ravenclaude-core/hooks/runaway-brake.sh
  - plugins/ravenclaude-core/hooks/sanitize-webfetch-output.sh
  - plugins/ravenclaude-core/hooks/storage-placement-nudge.sh
  - plugins/ravenclaude-core/hooks/stream-prompt-attribute.sh
  - plugins/ravenclaude-core/hooks/stream-session-close.sh
  - plugins/ravenclaude-core/hooks/thing-denial-kb-recall.sh
  - plugins/ravenclaude-core/hooks/thing-denial-kb-sync.sh
  - plugins/ravenclaude-core/hooks/thing-orchestrator.sh
  - plugins/ravenclaude-core/hooks/triage-outcome.sh
  - plugins/ravenclaude-core/hooks/worktree-guard.sh
<<<<<<< HEAD
covers_digest: "sha256:5fa0239aac3118f4f5ded2dbc1b21c547676e97a7011bda89857b70caadc6940"
=======
covers_digest: "sha256:dc1db96172f360f4c815dca14d3738346787eb2b2e1041e93c3595f287d64311"
>>>>>>> origin/main
nuance: "A hook writing to stderr at `exit 0` reaches the model on no event; only `hookSpecificOutput.additionalContext` and `updatedToolOutput` are delivered, so `_advise.sh` advised the terminal for its entire service life."
nuance_evidence:
  measured: 2026-08-19
  control: "a SessionStart additionalContext sentinel came back in every trial while the stderr token never did"
  falsifier: "any recorded transcript containing the stderr token"
  probe: "unprobed: the delivery fact is a host-platform property; it is modelled as its own platform-fact concept under the 90-day gate"
nuance_source: "plugins/ravenclaude-core/hooks/_advise.sh:1-40"
verify:
  tier: "effect"
  strength: "executed"
  class: "hook-advisory"
  probe: "plugins/ravenclaude-core/hooks/tests/lib/assert-delivered-channel.sh"
  teeth_exit: 1
sources:
  - label: measured in the FORGE product-inventory run
    url: https://github.com/mcorbett51090/RavenClaude/pull/997
---

## What a reader would have assumed instead

a SessionStart additionalContext sentinel came back in every trial while the stderr token never did

## The discriminator

control: a SessionStart additionalContext sentinel came back in every trial while the stderr token never did
Measured 2026-08-19: A hook writing to stderr at `exit 0` reaches the model on no event; only `hookSpecificOutput.additionalContext` and `updatedToolOutput` are delivered, so `_advise.sh` advised the terminal for its entire service life.

## Why it matters

Falsifier: any recorded transcript containing the stderr token

Probe: `unprobed: the delivery fact is a host-platform property; it is modelled as its own platform-fact concept under the 90-day gate`
