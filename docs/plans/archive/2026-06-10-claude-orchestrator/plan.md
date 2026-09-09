# FORGE plan — Claude orchestrator for non-Claude CLIs (ravenclaude-core)

> Synthesized from the FORGE run (scope + G1 grounding + two cross-model panels + gap-delta). Owner scope locked: 3-way knob `orchestrator: off | decide | full`, knob-only, default `off`, dashboard-explained, fail-safe to host. Builds in **this** repo (ravenclaude-core).

## Context
Under a non-Claude CLI (GitHub Copilot routing GPT/Grok — "Copilot CLI is horrendous"), let the user route the **Team-Lead orchestration** to Claude via `claude -p`, accepting the higher token cost. Precedent + plumbing already exist: the tribunal seats shell `claude -p` from inside a Copilot session (`scripts/thing-seat.sh`), and `THING_HOST=copilot` is exported by `hooks/copilot-hook-adapter.sh`.

## Mechanism (behavioral knob — no new hook)
`orchestrator: off | decide | full` is the **fourth behavioral commitment** in `.ravenclaude/comfort-posture.yaml` (after `design_checkins`, `decision_review`, `parallelism`) — read **directly** from the YAML by `spawn-team` at dispatch time. **No `apply-comfort-posture.py` change, no `settings.json` rule, no SessionStart hook** (those knobs are behavioral, not permission rules — verified this session). Absent = `off` = zero cost. No-op under Claude Code (host already IS Claude).

`spawn-team` adds a routing step: `THING_HOST==claude-code` OR knob `off`/absent → host orchestrates as today; `decide` → `claude -p` returns a structured dispatch plan the **host executes**; `full` → `claude -p` runs the orchestration and returns artifact content the host writes.

- **`decide`** — `claude -p --tools ""` is handed the task + the agent roster and returns a **named JSON dispatch plan** (specialists, briefs, order — the SOP-JSON the Team Lead already consumes). The host CLI runs the agents. Brain (Claude) / hands (host) split. Lower cost.
- **`full`** — **ONE large `claude -p` call** (NOT a nested Claude Code session — Panel B's load-bearing correction: a nested session has unbounded token cost, plugin-resolution complexity, and a fragile recursive-entry surface). It reasons through the whole task and returns the artifact content; the host writes the files. Highest cost, bounded.

## The `claude -p` invocation — reuse `thing-seat.sh`
A thin wrapper **`scripts/claude-orchestrate.sh`** (a script, not inline — so it is gate-testable and carries the recursion guard as code), copying `thing-seat.sh`'s exact pattern: **plain `claude -p` (never `--bare`)**, `mktemp -d` scratch dir (so the consumer's project CLAUDE.md isn't loaded), sources `hooks/_scrub.sh` for the egress secret backstop, defangs `${CLAUDE_PROJECT_DIR}`, wraps the task in the canonical `<untrusted>` envelope.

## Security (load-bearing — security-reviewer sign-off REQUIRED before the version bump)
1. **Recursion guard — three layers** (a `claude -p` orchestration must never spawn another → infinite spawn/cost):
   - export `RAVENCLAUDE_ORCH_ACTIVE=1` into the nested run; the wrapper refuses at entry (exit 7) if already set;
   - inherit/respect `THING_SEAT_ACTIVE=1` (kept semantically distinct from the orchestrator flag);
   - **`--tools ""` is the non-negotiable structural layer** — for `decide`, the nested session has zero tools, so it cannot call spawn-team / read files / invoke hooks regardless of any prompt injection. This holds even if both env vars are cleared.
2. **Secret scrub** on the task brief before it egresses to `claude -p` (reuse `_scrub.sh`; on a match, refuse locally and fall back to host).
3. **Fail-safe:** ANY non-zero exit / claude-unavailable / unauthenticated → fall back to host orchestration (the `off` path). Never hard-block. A deterministic preflight (`command -v claude` + a cheap auth probe) decides availability.
4. **Cost transparency:** a one-line cost note printed when the knob fires (mode + "this routed to Claude — extra tokens"), and the dashboard control carries a per-mode cost callout.

## Dashboard explanation (owner requirement)
A "Claude orchestrator" control in the Pipeline/Configure tab (`generate-dashboards.py`) — a **three-radio** (`off`/`decide`/`full`) control, each mode with its **cost trade-off line**, a `[host-only — inert under Claude Code]` badge, and a short explainer of what each does + where it fires. Round-trips through the existing `state` / `emitYaml` / `/__save` path (no new server endpoint → no Gate 32 impact). The other behavioral knobs (`design_checkins`, `parallelism`) are the rendering template.

## Deterministic gate (with teeth)
New `audit-gates.sh` gate (mock-`claude` driven): knob absent/`off` OR claude-unavailable → host path (no `claude -p`); `decide`/`full` + claude available → routes to the wrapper; the recursion guard refuses a re-entrant call; the secret-scrub refuses a brief with a secret. **Must-fail half:** strip the recursion guard (re-entrant call must then be caught) / strip the scrub (secret must then leak) — proving teeth. Plus the dashboard round-trip assertion (Gate 35) for the new knob.

## Dependency DAG
```
scope → wrapper(claude-orchestrate.sh)+recursion-guard → security-reviewer ┐
                                                          gate(audit-gates) ┤→ version-bump+regen → DoD
spawn-team routing prose ──────────────────────────────────────────────────┤
dashboard control (generate-dashboards.py) → Gate 35 assertion ─────────────┘
```
Critical path = wrapper + security-reviewer (the security sign-off gates the bump).

## Alternatives considered
- **Behavioral knob (chosen)** vs a PreToolUse hook that intercepts dispatch — the hook fires every session even when spawn-team is never called (cost/complexity); the knob is read only at dispatch.
- **`full` = one `claude -p` call (chosen)** vs a nested Claude Code session — the nested session is unbounded-cost + plugin-resolution-fragile.
- **Wrapper script (chosen)** vs inline in the SKILL — the script is gate-testable and carries the guard as code.

## DoD
- Version bump core `plugin.json` + `copilot/plugin.json` + `marketplace.json` (lockstep), regen dashboards + copilot package, CHANGELOG + a CLAUDE.md milestone.
- `audit-gates.sh` green (incl. the new gate + must-fail half), `check-frontmatter`, `check-md-links`, prettier, json valid.
- **security-reviewer sign-off on the `claude -p` exec path** is a hard predecessor of the bump.
- A PR for Matt's review (not auto-merge).

## Risk to keep in view
A non-Claude host may not faithfully **act on** the `decide` plan (no hook enforces plan compliance → "Claude's cost, host's judgment"). Mitigation: make the dispatch plan maximally prescriptive (the SOP-JSON the Team Lead already consumes) and owner-verify one real Copilot run; if the host ignores it, **`full` is the mode that delivers the locked intent** — frame `decide` as the cheaper best-effort and `full` as the guarantee.
