---
name: orchestrator-relay-scope
description: Design decision (2026-06-11) for the relay-all vs team-only orchestrator scope toggle — new orthogonal knob, generated AGENTS.md directive, NOT a hand-edited copilot-instructions.md
metadata:
  type: project
---

Matt wants a toggle between two relay scopes for the nested-Claude orchestrator (the `orchestrator: off|decide|full` knob, v0.152.0): **team-only** (today's behavior — fires only on spawn-team dispatch, Step 4.5) vs **relay-all** (every Copilot prompt forwarded to nested Claude).

**Architect recommendation (3-seat panel seat, 2026-06-11):**
- **Schema = NEW orthogonal knob `orchestrator_scope: team | all`** (default `team`), composing with the existing `orchestrator` HOW knob. NOT folded into the HOW enum (would create a 6-value matrix-minus-dead-cells smell).
- **Illegal cell `off` + `all` resolved by precedence, not a 4th enum value:** `off` masks `scope` (scope inert + dashboard greyed out). Same masking pattern as `command_review.enabled`+`gate_floor` and `parallelism`-absent.
- **Relay-all enforcement surface = a GENERATED, host-gated "Relay mode" directive in `copilot/AGENTS.md`** via `scripts/generate-copilot-plugin.py` — the same always-on instruction surface the bridge already uses. A `userPromptSubmitted` hook was rejected (a hook can only gate, not make a model relay-and-execute). It's a **behavioral commitment, not a hook-enforced gate** (Copilot has no event that forces a model to relay) — same honesty class as `design_checkins`/`parallelism`.
- **No-op under Claude Code** via the existing `THING_HOST == claude-code` skip (spawn-team SKILL.md:150,164) — host already IS Claude.

**Why:** keeps the existing knob + its emitYaml "emit only when ≠ default" round-trip untouched; two independent dashboard controls beat one six-value dropdown; no new mental model.

**The trap to avoid (the original Copilot prompt's bug):** it had the agent **hand-append a "Relay Mode" block to `.github/copilot-instructions.md`** (ABSENT, no generator) in the CONSUMER's clone (~/RavenClaude + Contoso). That file gets **clobbered on `git pull`/regenerate**. Correct split: schema + dashboard + directic text live in the marketplace plugin (generated, versioned); the only per-consumer thing is the one-line `orchestrator_scope:` in their git-ignored `.ravenclaude/comfort-posture.yaml` (git pull never touches it). **Zero hand-edited tracked files.**

**Build prerequisite:** security-reviewer re-check — relay-all widens the `claude -p` input surface from team-briefs to EVERY prompt; v0.152.0 sign-off covered team-brief volume only. Re-confirm the 3-layer recursion guard + scrub + `--tools ""` hold on the arbitrary-prompt path.

Single PR, near-zero migration (defaults to today's behavior). Relates to [[project-2026-06-10-forge-code-apps-skill]] (Copilot bridge work).
