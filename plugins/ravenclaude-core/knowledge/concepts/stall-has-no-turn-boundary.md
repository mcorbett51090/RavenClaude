---
id: stall-has-no-turn-boundary
title: "A stall has no turn boundary"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 913
summary: "Every registered hook fires on a turn or tool boundary. A stall is the absence of one, so no in-session hook can observe it — including the guard built for it."
last_verified: 2026-08-25
covers:
  - plugins/ravenclaude-core/scripts/stall_watch.py
  - plugins/ravenclaude-core/scripts/stall_reach.py
  - plugins/ravenclaude-core/scripts/install_stall_watch.py
covers_digest: "sha256:89cbda9bbd9cc2b1093c3c55050e0afa7a8090b1646f7e8851a55106825d8d90"
nuance: "The observable must be the last *assistant* record, not the last record of any type: a human typing into a suspected stall, and a product-generated `system/away_summary`, both reset a last-any clock without any progress having occurred."
nuance_evidence:
  measured: 2026-08-25
  control: "the same enumeration returned 39 hooks across 6 event types, so an empty in-turn set is the event map and not a failed read; and on the recorded stall the last-assistant and last-any clocks disagreed by 44.3 min while the exited-session fixtures showed a 0.0 min delta"
  falsifier: "a registered hook event that fires without a turn or tool boundary, or a stalled session whose last-any clock tracks its last-assistant clock"
  probe: plugins/ravenclaude-core/hooks/tests/test-stall-watch.py
nuance_source: "plugins/ravenclaude-core/scripts/stall_watch.py:96-118"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/hooks/tests/test-stall-watch.py"
  teeth_exit: 1
sources:
  - label: measured in the FORGE stall-watchdog run
    url: https://github.com/mcorbett51090/RavenClaude/tree/forge/stall-watchdog
---

## What it does

The three covered scripts detect a wedged Claude Code session from **outside** the
session, because nothing inside one can. They read the session registry for
liveness, the transcript for progress, and reach the owner through a receipted
webhook.

control: the same enumeration of `hooks.json` returned 39 hooks across 6 event
types, so an empty in-turn set is the event map itself and not a failed read
Measured 2026-08-25: every registered hook fires on a turn or tool boundary
(`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`,
`SubagentStart`, `Stop`), so a stall — which is *defined* by the absence of a
turn boundary — is unobservable from any of them.

The guard built for exactly this case is the sharpest instance rather than an
exception. `handoff-nudge.sh` exists to nudge a context-hot session toward a
handoff, and it is registered on `Stop`. If the turn never stops it never runs,
so the one hook authored for a hot window is structurally silent during the
failure it was written for. Detection therefore has to live in a separate
process on a timer, which is what the LaunchAgent is.

The second mechanism is which clock the detector reads, and the two available
clocks disagree in the direction that matters.

control: on the exited-session fixtures the two clocks agree to 0.0 min, so the
divergence below is the live stall and not a parsing artifact
Measured 2026-08-25: on the recorded 174-minute stall the last-assistant clock
read 141.0 min while the last-any-record clock read 96.6 min — a 44.3 minute
mask, produced by the owner's own queued prompts and by a product-generated
`system/away_summary` record, neither of which is progress.

A detector keyed on the wrong clock therefore fails toward "looks alive", which
is the dangerous direction: typing into a session suspected of being stuck
silences the detector for a further window, so the act of investigating hides
the thing being investigated.
