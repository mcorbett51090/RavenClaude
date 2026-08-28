---
id: cheap-lane-agent-matrix
title: "The cheap lane is agent-agnostic, not Grok-only"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 903
summary: "route-task.py picks a lane, not a vendor; cheap-lane-delegate.sh picks the agent — and the two CLIs' real capability shapes genuinely diverge."
last_verified: 2026-08-26
covers:
  - plugins/ravenclaude-core/scripts/cheap-lane-delegate.sh
  - plugins/ravenclaude-core/scripts/copilot-delegate.sh
  - plugins/ravenclaude-core/scripts/grok-delegate.sh
  - plugins/ravenclaude-core/scripts/route-task.py
  - plugins/ravenclaude-core/skills/cheap-lane-delegation/SKILL.md
covers_digest: "sha256:40a22d94b0a8080e593d8bdc4cbc84da9ccecd825113bf6a36519fca3ee0a2fb"
nuance: "Copilot CLI's `--model auto` rejects `--effort` outright at runtime — a real error, not a doc gap — so the Copilot lane differentiates by timeout budget only unless a caller pins an effort-capable model."
nuance_evidence:
  measured: 2026-08-26
  control: "a call with --model auto and NO --effort flag completed normally, isolating the rejection to the flag pairing rather than to the CLI itself"
  falsifier: "a future Copilot CLI release accepting --effort together with --model auto"
  probe: "plugins/ravenclaude-core/scripts/copilot-delegate.sh"
nuance_source: "plugins/ravenclaude-core/scripts/copilot-delegate.sh:195-200"
verify:
  tier: "none"
  rationale: "The rejection is live Copilot CLI runtime behavior, not something offline-stageable in CI; re-verifying it means a real non-interactive Copilot CLI call — already recorded as nuance_evidence.control — not a separate staged check."
sources:
  - label: verified live against the installed grok and copilot CLIs, this session
    url: https://github.com/mcorbett51090/RavenClaude/pull/1030
---

## What a reader would have assumed instead

That `--effort` is a Copilot CLI flag like any other, so passing it alongside the default `--model auto` would just apply the effort level to whatever model `auto` resolves to.

## The discriminator

control: a call with --model auto and NO --effort flag completed normally, isolating the rejection to the flag pairing rather than to the CLI itself
Measured 2026-08-26: Copilot CLI's `--model auto` rejects `--effort` outright at runtime — `"Model \"auto\" does not support reasoning effort configuration"` — a real error hit on the first live end-to-end test through the dispatcher, not a hypothetical read from documentation. `copilot-delegate.sh` therefore emits `--effort` only when `[ "$model" != "auto" ]`.

## Why it matters

`route-task.py`'s `lane` field now reads `"cheap"`, not `"grok"` — the router decides whether work leaves Claude at all, never which CLI it lands on. `cheap-lane-delegate.sh --agent grok|copilot` is the layer that actually picks the coding agent, and the two agents' tier tables cannot share one row: Grok's model/effort/perspective come from the shared `substrate-tier-map.json`; Copilot's does not, because none of six guessed pinned model slugs validated as a real `--model` value against the installed CLI, and the only value confirmed to work (`auto`) is exactly the one that forbids `--effort`.

Falsifier: a future Copilot CLI release accepting `--effort` together with `--model auto`.
