# Changelog — ravenclaude-core

All notable changes to the `ravenclaude-core` plugin. Versioning is semver; the `version` field in `.claude-plugin/plugin.json` (mirrored in the marketplace catalog) is the authoritative source of truth, and this file tracks the user-visible arc. Larger architectural narratives live in [`CLAUDE.md`](CLAUDE.md) milestones; this file is the scannable per-version log.

## 0.138.0 — 2026-06-09

### Added

- **`spawn-team` honors the parallelism posture (behavioral enforcement).** The Pipeline page's `parallelism` control (toggle + max-workers + "unlimited", shipped in 0.137.0) gains its first consumer: [`skills/spawn-team/SKILL.md`](skills/spawn-team/SKILL.md) Step 5 now reads the `parallelism:` block from `.ravenclaude/comfort-posture.yaml` and caps how wide the Team Lead fans independent agents out — `enabled: false` → sequential, `max_workers: N` → batches of ≤N, `max_workers: unlimited` → uncapped. Behavioral commitment (like `design_checkins` / `decision_review`), not a hook-enforced gate; bounds *breadth* where the runaway brake bounds *depth*.

### Notes

- **Migration:** none — the `parallelism:` block defaults absent, and an absent block preserves the Team Lead's existing parallel-fan-out behavior, so nothing changes on `/plugin marketplace update` unless a consumer sets it.

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
