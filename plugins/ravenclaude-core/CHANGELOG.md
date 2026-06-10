# Changelog — ravenclaude-core

All notable changes to the `ravenclaude-core` plugin. Versioning is semver; the `version` field in `.claude-plugin/plugin.json` (mirrored in the marketplace catalog) is the authoritative source of truth, and this file tracks the user-visible arc. Larger architectural narratives live in [`CLAUDE.md`](CLAUDE.md) milestones; this file is the scannable per-version log.

## 0.147.0 — 2026-06-10

### Changed

- **`scout` now persists every run to disk — the full detail no longer dies in the chat transcript.** The skill's Step 5 (and Output Contract) gained an explicit two-tier storage step: (1) write the **full run report** — ranked shortlist with per-find reasoning, the *dropped-and-why* + ToS-flagged items, the per-lane/per-source detail, and the load-bearing finding(s) — to `docs/research/<YYYY-MM-DD>-scout-<slug>/report.md` (the same committed research-persistence home `rc-deep-research` uses; `docs/` commits straight to `main`, no PR); (2) append the **distilled keepers** as rows to `docs/idea-board.md`, the run-section header linking to the report. Both committed. Prior behavior only wrote the distilled idea-board rows, so the richer per-lane detail was lost to the transcript. Added a matching anti-pattern ("letting the run die in the chat transcript").

### Notes

- **Migration:** none — a skill-content change; the next `/scout` run writes the report + idea-board rows. Nothing in an installed plugin's wiring changes on `/plugin marketplace update`.
- Version note: 0.146.0 (the `monitors.json` path fix, PR #385) merged immediately before this; this change took 0.147.0 to avoid a version collision while both PRs were open.

## 0.146.0 — 2026-06-09

### Fixed

- **`monitors.json` load failure (`/doctor` ENOENT).** `plugin.json`'s `experimental.monitors` field pointed at `./monitors.json`, but the file ships at `./monitors/monitors.json` (inside the `monitors/` directory, beside `watch-run-state.sh`). Claude Code resolved the manifest path to a non-existent file and reported `monitors load failed … ENOENT` on every session start. Corrected the manifest path; aligned the `CLAUDE.md` milestone and [`knowledge/run-state-monitor.md`](knowledge/run-state-monitor.md), which both documented the same wrong path. No file move — the `monitors/` directory is the file's correct home.

### Notes

- **Migration:** none — a manifest path correction; the reactive run-state monitor now loads as intended on `/plugin marketplace update`. Consumers on a prior version simply stop seeing the `/doctor` load-failure line.

## 0.140.0 — 2026-06-09

### Added

- **Eval-harness wiring — the `rc-deep-research` workflow now honors the eval contract end-to-end.** Completes the deliberate follow-up the Agent-dispatch-evaluator Phase 2 milestone (0.121.0) carved out ("the eval-harness args-shape/runId/stats wiring … different regions"). Two halves land together: (1) the **harness side** — [`scripts/eval-adaptive-classifier.py`](../../scripts/eval-adaptive-classifier.py) gains the transcript-token acquisition path (`collect_metrics` reads per-agent `usage` from `~/.claude` transcripts post-hoc and buckets it into per-phase wall-clock windows, since a workflow script structurally cannot see per-agent token usage), the mismatch-1 `{question, runId}` invocation form, the mismatch-4 baseline knobs, and a second self-test sub-test that proves the transcript bucketing (verify_default cache-hit-rate = 0.75); (2) the **workflow side** — both `rc-deep-research.js` copies ([`.claude/workflows/`](../../.claude/workflows/rc-deep-research.js) + the bundled `skills/rc-deep-research/` mirror) accept a `{question, runId}` object as well as a plain string, fall back to `BASELINE_KNOBS` for the two vote knobs the run-config schema excludes, persist per-phase wall-clock windows + the grader's `stats` contract (`subagent_tokens`/`agent_count`/`duration_ms`/`confirmed_claim_count`/`run_window`/`per_phase`), and — when a `runId` is set — persist `structured-output.json` + `synthesis.md` under `.ravenclaude/runs/<runId>/` via the `rc-audit-emit` agent()-write pattern (with `_predispatch:"skip"` so the dispatch-evaluator leaves the infra writes alone).
- **Unblocks adaptive-run-classifier Phase 6.** The Phase-6 pre-build gate was "Phase 5 eval gate green," which was unrunnable because the harness↔workflow contract had never been wired (5 documented mismatches). With this wiring the eval can run; the `enabled:true` flip stays deferred pending a live eval run + the tier-framing re-confirm.

### Notes

- **Invariant preserved:** a plain-string `/rc-deep-research` call (legacy / interactive) is byte-identical to before — `runId` gates all eval-only behavior. Gate 52 (dispatch-evaluator disabled-floor, byte-identical) stays green; the copied wrapper block is untouched.
- **Migration:** none — the workflow lives in the marketplace repo's own `.claude/workflows/`; the bundled skills mirror changed but the string-arg path is unchanged, so nothing in a consumer's installed plugin behaves differently on `/plugin marketplace update`.

## 0.139.0 — 2026-06-09

### Added

- **New consumer-facing best-practice: [`best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md`](best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md)** (16th rule). Encodes the two most-repeated, independently-validated Claude Code community lessons — _"hooks are deterministic, `CLAUDE.md` is advisory; encode must-happen rules as hooks/CI, not prose"_ and _"an over-long `CLAUDE.md` gets half-ignored — prune it"_ — as a named rule the core agents surface to consumer-repo users (the `/init-agent-ready` audience). The repo already practiced this on its _authoring_ side (`AGENTS.md` house-rule #4, the hook+CI layout enforcement) but shipped no consumer-facing version. Sourced from a 2026-06-09 Claude-subreddit scan cross-checked against Anthropic's Claude Code best-practices docs; research + panel record in [`docs/research/2026-06-09-claude-subreddit-scan/README.md`](../../docs/research/2026-06-09-claude-subreddit-scan/README.md). Index count 15 → 16.

### Notes

- **Migration:** none — additive best-practice markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

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
