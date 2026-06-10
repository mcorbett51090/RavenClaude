# Changelog — ravenclaude-core

All notable changes to the `ravenclaude-core` plugin. Versioning is semver; the `version` field in `.claude-plugin/plugin.json` (mirrored in the marketplace catalog) is the authoritative source of truth, and this file tracks the user-visible arc. Larger architectural narratives live in [`CLAUDE.md`](CLAUDE.md) milestones; this file is the scannable per-version log.

## 0.127.0 — 2026-06-10

### Added

- **`orchestrator: off | decide | full` behavioral knob** — the fourth behavioral commitment in `.ravenclaude/comfort-posture.yaml`. Routes team-lead orchestration to Claude when the host CLI is not Claude Code (e.g. GitHub Copilot routing GPT/Grok). Read directly by `spawn-team` at dispatch time; no new hook, no `apply-comfort-posture.py` change. Inert under Claude Code (host already IS Claude). Default: `off` (zero extra cost). Seeded as `orchestrator: off` in `templates/comfort-posture-balanced.yaml`.
- **`scripts/claude-orchestrate.sh`** — thin wrapper copying `thing-seat.sh`'s `claude -p` plumbing: plain `claude -p` (OAuth-compatible, never `--bare`), `mktemp` scratch dir, `_scrub.sh` sourced for egress backstop, `CLAUDE_PROJECT_DIR` defanged. **Three-layer recursion guard:** (1) `RAVENCLAUDE_ORCH_ACTIVE=1` env-var check at entry; (2) `THING_SEAT_ACTIVE=1` check; (3) `--tools ""` structural layer for both modes (the nested session has zero tools regardless of injection). Secret scrub on brief + roster before egress. **Fail-safe:** any non-zero exit → caller falls back to host orchestration; never hard-blocks. `decide` mode returns a JSON dispatch plan; `full` mode returns artifact content.
- **spawn-team Step 4.5** — orchestrator routing step in `skills/spawn-team/SKILL.md`: check `THING_HOST` + the knob, route to `claude-orchestrate.sh`, fall back to host on any failure.
- **Dashboard: Claude orchestrator control** (Pipeline/Configure tab) — three-radio `off`/`decide`/`full` select with per-mode cost callout and a `[host-only — inert under Claude Code]` badge. Round-trips via the existing `state`/`emitYaml`/`/__save` path (no new server endpoint).
- **Gate 102** (`audit-gates.sh`) — mock-claude-driven gate: recursion guard fires, seat guard fires, scrub fires on secret brief, fallback on absent claude, happy path passes. Must-fail halves prove both guards are real code: stripped guard lets re-entry through; stripped scrub lets secret through.

### Security

⚠️ **NEEDS `ravenclaude-core/security-reviewer` sign-off before merge.** This version introduces a `claude -p` exec path in `scripts/claude-orchestrate.sh`. The three-layer recursion guard + scrub + fail-safe are load-bearing security controls that have NOT yet had a formal security review. The PR is open for review; the version bump is deliberately committed but the PR must not be merged until the security-reviewer pass is complete. See `docs/plans/2026-06-10-claude-orchestrator/plan.md` §Security.

### Notes

- **Migration:** none — `orchestrator` defaults to `off` (absent = `off` = inert). Nothing changes on `/plugin marketplace update` unless a consumer adds the key.
- No existing hook, agent, rule, or other script was modified except `spawn-team/SKILL.md` (new routing step added) and `audit-gates.sh` (new gate appended).

## 0.126.0 — 2026-06-05

### Added

- **`scenarios/` bank (net-new).** The plugin shipped the `scenario-retrieval` skill but had no bank of its own. Added a domain-neutral **orchestration** scenarios bank — four dated, scope-tagged, unverified narratives that teach the plugin's own protocols, plus a [`scenarios/README.md`](scenarios/README.md) index:
  - `2026-06-05-keyword-routed-to-wrong-specialist` — route-before-spawning (traverse the routing tree, don't keyword-match; earliest-blocking gate wins).
  - `2026-06-05-subagent-tried-to-spawn-subagents` — orchestrator-worker hierarchy + recursion guard (escalate a handoff, don't dispatch peers).
  - `2026-06-05-blocked-report-skipped-alternate-methods` — Capability Grounding (read the error, enumerate alternatives, load the deferred/MCP route before reporting "can't").
  - `2026-06-05-decision-routed-to-tribunal-not-human` — decision-review envelope (route every yes/no, but high-blast + genuine-preference always `defer` to the human).
- **`CLAUDE.md` §"Value-add completeness (build-out 2026-06-05)"** — disposition table for every value-add menu item (scenarios BUILT; the runtime-tier items N-A or already-present for a foundation plugin that already ships hooks/scripts/a dashboard).

### Notes

- No existing hook, script, skill, rule, or agent was modified. The only changes are additive files (`scenarios/`, this CHANGELOG) plus a `CLAUDE.md` append and the version bump. `plugins/*/scenarios/**` was already an allowed glob in `.repo-layout.json`, so no layout-manifest change was needed.
- **Migration:** none — additive content; nothing in a consumer's installed plugin changes on `/plugin marketplace update`.
