---
id: subagent-ttl-advisor-in-window-gaps
title: "The TTL advisor counts only gaps the 1-hour cache changes"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 946
summary: "Which re-dispatches count toward a 1-hour subagent cache, and why most agents should keep the default."
last_verified: 2026-10-18
covers:
  - plugins/ravenclaude-core/scripts/subagent-ttl-advisor.py
covers_digest: "sha256:d7b37eeb8435f8e1098610702438e45eeaa7d60db6a1293f341cd859da253680"
nuance: "Only a same-session re-dispatch 5 to 60 minutes after the previous one counts. A recommendation needs at least 5 dispatches and 0.65 such gaps per 1-hour write; with no ledgers the advisor prints a notice and exits 0."
nuance_evidence:
  measured: 2026-10-18
  control: "subagent-ttl-advisor.py --self-test passes 18 checks, including an agent re-dispatched every 2 minutes that scores zero in-window gaps and one re-dispatched every 2 hours that is not recommended, and --must-fail catches a mutant that recommends 1h for every agent with enough data"
  falsifier: "a gap under 5 minutes or over 60 minutes counted as in-window, or an agent below the 0.65 ratio recommended"
  probe: "plugins/ravenclaude-core/scripts/subagent-ttl-advisor.py"
nuance_source: "plugins/ravenclaude-core/scripts/subagent-ttl-advisor.py"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/subagent-ttl-advisor.py"
  teeth_exit: 1
sources:
  - label: "2026-10-14 prompt-caching build plan — Phase 4, subagent TTL from data"
    url: https://github.com/mcorbett51090/RavenClaude/blob/main/docs/plans/2026-10-14-prompt-caching/BUILD-PLAN.md
---

## What a reader would have assumed instead

That any agent dispatched more than once in a session would save money on a 1-hour cache, so the advisor should recommend it for every busy agent.

## The discriminator

control: `subagent-ttl-advisor.py --self-test` scores an agent re-dispatched every 2 minutes at zero in-window gaps, and does not recommend one re-dispatched every 2 hours.

Measured 2026-10-18: a gap under 5 minutes already reads the 5-minute cache, and a gap over 60 minutes misses either way, so only the 5-60 minute band changes the bill.
