---
id: handoff-tax-flags-on-role-not-frontmatter
title: "The handoff-tax meter keys frontier_readonly on worker role × resolved model, not on the agent's model: line"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 935
summary: "frontier_readonly is computed from the payload's resolvedModel × subagent_type, never the agent's model: line — a scout overridden to opus is caught; an architect on opus is not."
last_verified: 2026-09-14
covers:
  - plugins/ravenclaude-core/agents/scout.md
  - plugins/ravenclaude-core/hooks/handoff-tax-meter.sh
  - plugins/ravenclaude-core/scripts/handoff-tax-meter.py
  - plugins/ravenclaude-core/hooks/tests/test-gate285-handoff-tax-meter.sh
covers_digest: "sha256:dddd6d630b5af212c800a4ee739cc899fd2fb89d12f14f9f69acd11a456d283e"
nuance: "`frontier_readonly` fires on `tool_response.resolvedModel` × the basename of `tool_input.subagent_type` (`explore` / `scout`), never on the agent file's `model:` — so `scout` dispatched with a per-call `model: opus` override is flagged while `scout.md` still reads `haiku`, and `architect` on opus is not."
nuance_evidence:
  measured: 2026-09-14
  control: "same resolvedModel (claude-opus-4-8), three subagent_types: `Explore` -> SIGNAL frontier_readonly, `ravenclaude-core:scout` -> SIGNAL frontier_readonly, `architect` -> OK; the only input that changed between the flagged and unflagged runs was the role"
  falsifier: "an `architect` dispatch on an opus id emitting frontier_readonly, or a `scout` dispatch on an opus id staying silent"
  probe: "plugins/ravenclaude-core/scripts/handoff-tax-meter.py"
nuance_source: plugins/ravenclaude-core/scripts/handoff-tax-meter.py:196-223
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/handoff-tax-meter.py"
  teeth_exit: 1
sources:
  - label: knowledge/model-tier-delegation.md — the doctrine this meter measures
    url: https://github.com/mcorbett51090/RavenClaude/blob/main/plugins/ravenclaude-core/knowledge/model-tier-delegation.md
  - label: Claude Code sub-agents — "Choose a model" (Explore inherits the main model since v2.1.198)
    url: https://code.claude.com/docs/en/sub-agents
---

## What a reader would have assumed instead

The meter reads the dispatched agent's `model:` frontmatter, so a `scout` (pinned `haiku`) can
never trip `frontier_readonly` — the frontmatter is the tier, and the gate on `model:` in
`check-frontmatter.py` is what makes the flag unnecessary for shipped agents.

## The discriminator

control: with `resolvedModel` held at `claude-opus-4-8` across three self-test payloads, `Explore`
and `ravenclaude-core:scout` both returned `SIGNAL frontier_readonly` while `architect` returned
`OK` — the role was the only input that changed between the flagged and the unflagged runs.
Measured 2026-09-14: the flag is computed from the `PostToolUse(Agent)` payload alone —
`tool_response.resolvedModel` classified to a tier, crossed with the basename of
`tool_input.subagent_type` against `READ_ONLY_TYPES = {explore, scout}` — and the agent file is
never opened, so a per-invocation `model` override that puts a scout on opus is caught while a
judgment role on opus is deliberately not.

## Why it matters

The `model:` frontmatter gate closes one door (a shipped agent cannot silently inherit the
session's model), but Claude Code resolves the model **per invocation first** — the Team Lead's
`model` parameter, then the frontmatter, then `CLAUDE_CODE_SUBAGENT_MODEL`. A meter that trusted
the frontmatter would report every scout as haiku forever. Reading `resolvedModel` is what lets
the ledger's `tier` column be the tier the worker actually billed at, and what lets the built-in
`Explore` (which has no frontmatter and since v2.1.198 inherits the main model) be flagged at all.

Falsifier: an `architect` dispatch on an opus id emitting `frontier_readonly`, or a `scout`
dispatch on an opus id staying silent.

Probe: `plugins/ravenclaude-core/scripts/handoff-tax-meter.py --self-test` (exit 1 on any failed
check; the three role-crossed payloads are named `Explore on opus`, `plugin-scoped scout on opus`,
`architect on opus`).

```mermaid
graph TD
  A["PostToolUse(Agent) payload"] --> B["tool_response.resolvedModel -> tier"]
  A --> C["basename(tool_input.subagent_type)"]
  B --> D{"tier == frontier AND role in {explore, scout}?"}
  C --> D
  D -->|yes| E["flag frontier_readonly -> advisory + ledger"]
  D -->|no| F["ledger line only"]
  G["agents/scout.md model: haiku"] -. never read by the meter .-> D
```
