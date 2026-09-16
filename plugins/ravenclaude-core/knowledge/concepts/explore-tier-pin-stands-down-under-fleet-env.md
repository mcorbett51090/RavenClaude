---
id: explore-tier-pin-stands-down-under-fleet-env
title: "explore-tier-pin rewrites an un-pinned Explore to haiku — but stands down entirely when CLAUDE_CODE_SUBAGENT_MODEL is set"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 936
summary: "The pin fires only on an un-pinned `explore`; a set CLAUDE_CODE_SUBAGENT_MODEL makes it stand down even then — a per-invocation pin would OVERRIDE the fleet-wide env choice, not add to it."
last_verified: 2026-09-14
covers:
  - plugins/ravenclaude-core/hooks/explore-tier-pin.sh
  - plugins/ravenclaude-core/scripts/explore-tier-pin.py
  - plugins/ravenclaude-core/hooks/tests/test-gate286-explore-tier-pin.sh
covers_digest: "sha256:522a05cec00c8233175ed6079a42bba7b48d2e55f4aad7ca63e1e5d2fb4dec94"
nuance: "Same un-pinned `Explore` payload, same `haiku` knob: env `{}` yields an `updatedInput.model: haiku` envelope; env `{CLAUDE_CODE_SUBAGENT_MODEL: haiku}` yields `None`. Per-invocation `model` outranks the env var in Claude Code's resolution order, so a pin would have silently replaced the consumer's fleet-wide routing — the hook yields instead."
nuance_evidence:
  measured: 2026-09-14
  control: "same payload (`Explore`, no `model`), same knob (`haiku`): env `{}` -> envelope with `updatedInput.model == haiku` and NO `permissionDecision`; env `{CLAUDE_CODE_SUBAGENT_MODEL: haiku}` -> `None`. The env var was the only input that changed between the rewrite and the stand-down."
  falsifier: "an envelope emitted while CLAUDE_CODE_SUBAGENT_MODEL is set, or a `permissionDecision` key appearing in any envelope (the hook would then be gating, not rewriting)"
  probe: "plugins/ravenclaude-core/scripts/explore-tier-pin.py"
nuance_source: plugins/ravenclaude-core/scripts/explore-tier-pin.py:113-130
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/explore-tier-pin.py"
  teeth_exit: 1
sources:
  - label: knowledge/model-tier-delegation.md — "The one place a hook does bind"
    url: https://github.com/mcorbett51090/RavenClaude/blob/main/plugins/ravenclaude-core/knowledge/model-tier-delegation.md
  - label: Claude Code sub-agents — model resolution order (per-call `model` > frontmatter > CLAUDE_CODE_SUBAGENT_MODEL)
    url: https://code.claude.com/docs/en/sub-agents
  - label: Claude Code hooks — PreToolUse `updatedInput` (rewrite without a permissionDecision)
    url: https://code.claude.com/docs/en/hooks
---

## What a reader would have assumed instead

The pin is a cost guardrail, so it always applies: any `Explore` dispatched without a `model`
gets `haiku`, full stop — and a consumer who has already set `CLAUDE_CODE_SUBAGENT_MODEL` to route
every sub-agent gets the pin *on top of* that, belt and braces.

## The discriminator

control: `decide(_payload(), "haiku", {})` returned an envelope whose `updatedInput.model` was
`haiku`, whose original `subagent_type` / `prompt` fields were preserved, and which carried **no**
`permissionDecision`; `decide(_payload(), "haiku", {"CLAUDE_CODE_SUBAGENT_MODEL": "haiku"})`
returned `None`. Same payload, same knob — the environment variable was the only input that
changed. Measured 2026-09-14 via the script's `--self-test` (the checks are named
`envelope: updatedInput.model == haiku`, `envelope: NO permissionDecision (gate untouched)` and
`stand down: CLAUDE_CODE_SUBAGENT_MODEL set`).

## Why it matters

Claude Code resolves a sub-agent's model **per invocation first**: the Team Lead's `model`
parameter beats the agent's frontmatter, which beats `CLAUDE_CODE_SUBAGENT_MODEL`. A hook that
injects `model: haiku` into `tool_input` is therefore writing at the *highest*-precedence slot —
so on a host where the consumer already routes the whole fleet by env var (say, to `sonnet` for a
compliance reason), an always-on pin would not be belt-and-braces; it would silently **override**
the consumer's decision with this plugin's. Standing down is what keeps the pin a default rather
than a policy. The same logic is why an explicit `model` — including an explicit `inherit` — is
honoured untouched, and why the envelope never carries a `permissionDecision`: this hook changes
the model of a dispatch that was already allowed; it never becomes a gate.

Falsifier: an envelope emitted while `CLAUDE_CODE_SUBAGENT_MODEL` is set, or a
`permissionDecision` key appearing in any emitted envelope.

Probe: `plugins/ravenclaude-core/scripts/explore-tier-pin.py --self-test` (exit 1 on any failed
check; 25 checks covering the envelope shape, the eight stand-down conditions and the knob parse).
