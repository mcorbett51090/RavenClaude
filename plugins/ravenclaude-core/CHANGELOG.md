# Changelog — ravenclaude-core

All notable changes to the `ravenclaude-core` plugin. Versioning is semver; the `version` field in `.claude-plugin/plugin.json` (mirrored in the marketplace catalog) is the authoritative source of truth, and this file tracks the user-visible arc. Larger architectural narratives live in [`CLAUDE.md`](CLAUDE.md) milestones; this file is the scannable per-version log.

## 0.159.0 — 2026-06-22

### Added

- **Visual-feedback-loop `parity` gate — diff a visual against a known-good exemplar** ([`skills/visual-feedback-loop/driver.py`](skills/visual-feedback-loop/driver.py), v0.2.0). Closes the gap the layout linter structurally can't see: a visual that is *perfectly placed* yet renders **blank** because its render skeleton is wrong for its type. The new `parity` config (`{"candidate": "...visual.json", "reference": "...visual.json"}`) extracts a PBIR render skeleton from each and **fails** (`next_action: match-reference-exemplar`) only on render-blocking divergence — a wrong query role (`Values`/`Data`/`Indicator`), a candidate-only object key (e.g. `calloutValue` on a legacy `card`), or a missing `$id`. A different `visualType` is `not_captured` (not a false fail), and it echoes only allowlist-sanitized schema tokens (never raw `visual.json` content). The technique is documented generically for all declarative-viz (Vega-Lite, Tableau) in [`knowledge/visual-feedback-loop.md`](knowledge/visual-feedback-loop.md); the runnable differ is PBIR-first. Proven by **Gate 100** (match→ship, wrong-role/unknown-key/missing-`$id`→fail, non-comparable→not_captured, + a parity-specific teeth mutant). Origin: a Fabric/PBIR field session that burned four deploy-and-eyeball cycles before diffing against the confirmed-working exemplar cracked it.

### Notes

- **Migration:** none — additive `parity` gate (off unless a config supplies it); the driver envelope shape is unchanged. Nothing changes on `/plugin marketplace update`.

## 0.158.0 — 2026-06-22

### Added

- **`rc` launcher — host-agnostic dashboard front door** ([`bin/rc`](bin/rc), new `plugins/*/bin/**` layout glob). The `rc dashboard` "one-verb front door" the docs referenced was a phantom (no `rc` on disk); it now exists for real as a thin bash dispatcher (one verb today: `rc dashboard [--port N] [--no-open]`). It **never `cd`s** — `serve-dashboards.py` resolves the project root from `Path.cwd()`, so the launcher `exec`s the server with the caller's cwd preserved (`.ravenclaude/` lands in the consumer's repo) and works identically under Claude Code, GitHub Copilot CLI, or a bare terminal.
- **Copilot dashboard discoverability** — [`scripts/generate-copilot-plugin.py`](../../scripts/generate-copilot-plugin.py) appends an always-applicable **"Launch the comfort-posture dashboard"** block to the generated [`copilot/AGENTS.md`](copilot/AGENTS.md) (parallel to the opt-in Relay-mode block). Copilot reads `AGENTS.md` natively, so "open the dashboard" now Just Works in a Copilot repo — closing the gap where there's no `/dashboard` slash command (Claude-Code-only) and Copilot had to reverse-engineer the launch each time.

### Fixed

- **Phantom `rc dashboard` references made real.** [`commands/dashboard.md`](commands/dashboard.md) now documents where `rc` lives, the PATH one-liner, and the Copilot "just ask" path; the N-A `bin/` disposition in the CLAUDE.md Value-add table is updated to BUILT.

## 0.155.0 — 2026-06-11

### Added

- **New best-practice — "Permissions are a three-tier posture (`deny`/`ask`/`allow`), not an on-off switch"** ([`best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md`](best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md), 18 rules total). Distills the Claude Code permission model: eval order is `deny` → `ask` → `allow` (first match wins; specificity doesn't reorder — a `deny` always beats an `allow`), sort operations by reversibility (idempotent reads → `allow`, intent-changing → `ask`, irreversible/secret → `deny`), `allow` is a convenience layer while `deny` is the boundary, `--dangerously-skip-permissions` skips the `deny` backstop too (isolated envs only), and `settings.json` is reviewed-in-a-PR like code. The repo's own 20-entry `.claude/settings.json` deny list is the worked example. Generalizes the existing WebFetch-specific `web-access-allow-deny-list-before-first-fetch.md` (which it declares itself the parent of). Sourced from the [2026-06-11 Claude subreddit scan](../../docs/research/2026-06-11-claude-subreddit-scan/README.md) (1 of 4 findings approved; the other three deferred/denied as covered or out-of-core-scope).

### Notes

- **Migration:** none — additive markdown; nothing in a consumer's installed plugin changes on `/plugin marketplace update`.

## 0.152.0 — 2026-06-10

### Added

- **`orchestrator: off | decide | full` behavioral knob** — the fourth behavioral commitment in `.ravenclaude/comfort-posture.yaml`. Routes team-lead orchestration to Claude when the host CLI is not Claude Code (e.g. GitHub Copilot routing GPT/Grok). Read directly by `spawn-team` at dispatch time; no new hook, no `apply-comfort-posture.py` change. Inert under Claude Code (host already IS Claude). Default: `full` (owner choice — route orchestration to Claude by default under a non-Claude host). Seeded as `orchestrator: full` in `templates/comfort-posture-balanced.yaml`.
- **`scripts/claude-orchestrate.sh`** — thin wrapper copying `thing-seat.sh`'s `claude -p` plumbing: plain `claude -p` (OAuth-compatible, never `--bare`), `mktemp` scratch dir, `_scrub.sh` sourced for egress backstop, `CLAUDE_PROJECT_DIR` defanged. **Three-layer recursion guard:** (1) `RAVENCLAUDE_ORCH_ACTIVE=1` env-var check at entry; (2) `THING_SEAT_ACTIVE=1` check; (3) `--tools ""` structural layer for both modes (the nested session has zero tools regardless of injection). Secret scrub on brief + roster before egress. **Fail-safe:** any non-zero exit → caller falls back to host orchestration; never hard-blocks. `decide` mode returns a JSON dispatch plan; `full` mode returns artifact content.
- **spawn-team Step 4.5** — orchestrator routing step in `skills/spawn-team/SKILL.md`: check `THING_HOST` + the knob, route to `claude-orchestrate.sh`, fall back to host on any failure.
- **Dashboard: Claude orchestrator control** (Pipeline/Configure tab) — three-radio `off`/`decide`/`full` select with per-mode cost callout and a `[host-only — inert under Claude Code]` badge. Round-trips via the existing `state`/`emitYaml`/`/__save` path (no new server endpoint).
- **Gate 102** (`audit-gates.sh`) — mock-claude-driven gate: recursion guard fires, seat guard fires, scrub fires on secret brief, fallback on absent claude, happy path passes. Must-fail halves prove both guards are real code: stripped guard lets re-entry through; stripped scrub lets secret through.

### Security

✅ **`ravenclaude-core/security-reviewer` sign-off COMPLETE (2026-06-10) — CLEAR-TO-MERGE.** The `claude -p` exec path was reviewed: all controls verified by execution + teeth-stripping (3-layer recursion guard incl. `--tools ""` for both `decide` and `full`, pre-egress secret scrub, nonce-wrapped injection envelope, scratch-dir isolation, total fail-safe-to-host). No blocking findings.

### Notes

- **Migration:** `orchestrator` defaults to `full` — a consumer on a NON-Claude CLI who hasn't set the key routes orchestration through `claude -p` by default on `/plugin marketplace update` (inert under Claude Code; set `orchestrator: off` to opt out).
- No existing hook, agent, rule, or other script was modified except `spawn-team/SKILL.md` (new routing step added) and `audit-gates.sh` (new gate appended).

## 0.151.0 — 2026-06-10

### Fixed

- **Gate 101 SVG linter hardened — `<foreignObject>` and remote/`javascript:` href now enforced** ([`skills/declarative-visualization/lint.py`](skills/declarative-visualization/lint.py)). `lint.py`'s `_check_svg()` previously only caught `<script>` elements and `on*` event attributes. Two additional SVG injection vectors are now flagged at exit 1:
  - `<foreignObject>` elements (XSS-escalation vector — embedded HTML can carry arbitrary scripts).
  - `href` or `xlink:href` whose value begins with `http://`, `https://`, or `javascript:` (network call + potential JS execution). **Safe local fragment refs like `href="#id"` are explicitly allowed** — the pattern matches only remote/script schemes, not intra-document references.
- **Gate 101 test extended** ([`hooks/tests/test-gate101-declarative-viz-linter.sh`]). Three new must-fail fixtures (`bad-svg-foreign-object.svg`, `bad-svg-remote-href.svg`, `bad-svg-javascript-href.svg`) and one new must-pass fixture (`good-svg-local-ref.svg` — safe local `href="#id"` + `xlink:href="#id"`). Mutant (always-pass) half extended to cover the two new bad SVG fixtures, proving the new checks are logic, not luck.
- **`knowledge/declarative-visualization.md` §4b reconciled**: the `<foreignObject>` and `xlink:href` rows' "Caught by" column updated from `security-reviewer (NOT yet linter-enforced)` to `lint.py (Gate 101)`. The "Honest scope" note updated to reflect that all four SVG vector classes are now linter-caught; Vega `signals`/`expr` remain security-reviewer-gated. The tracked follow-up note removed (it was this change).

### Notes

- **Migration:** none — the new checks only add rejections (stricter); no valid committed SVG that passed before should contain `<foreignObject>` or remote/`javascript:` hrefs, and the safe local-fragment carve-out preserves the `xlink:href="#id"` pattern used in `<use>` elements.

## 0.150.0 — 2026-06-10

### Added

- **New skill: `declarative-visualization`** ([`skills/declarative-visualization/`](skills/declarative-visualization/SKILL.md)). Cross-surface Vega-Lite/Deneb/SVG spec-authoring for any visual agent. Ships: a 6-step authoring method (pick grammar → bind data → encode → wire interactivity → test null/empty → verify via render loop); a surface-agnostic `spec-patterns/` library of 6 starter templates (diverging bar, dumbbell, small-multiples facet, heatmap, sparkline strip, annotated line); a runnable stdlib-only `lint.py` security linter (no `data.url`, no remote `transform.lookup`, no custom `loader`, no remote `$schema`, no SVG `<script>`/`on*` — exit-coded for CI); and Gate 101 (bidirectional: clean fixtures pass, 6 security-vector fixtures fail, path traversal rejected, always-pass mutant lets a bad spec through = logic has teeth). Any PR adding/modifying a `spec-patterns/` template routes through `ravenclaude-core/security-reviewer` (load-bearing invariant).
- **New knowledge file: `knowledge/declarative-visualization.md`** — cross-surface canon: when to use Vega-Lite vs Vega vs Deneb vs SVG, grammar essentials, surface→delivery map (web/Power BI/Tableau/SVG-in-DAX), the full security model (Vega network-access vectors + SVG script-injection vectors), visual-feedback-loop integration, null/empty data handling, and a pre-publish checklist. Claim grounding markers on unverified Vega/Deneb specifics.
- **Cross-surface priors on 6 viz agents** — a `## Declarative visualization (Deneb / Vega-Lite / SVG)` section added to: `power-platform/power-bi-engineer` (Deneb + SVG-in-DAX), `data-platform/dashboard-builder` (vega-embed/react-vega/Evidence), `ravenclaude-core/frontend-coder` (vega-embed/react-vega + inline SVG), `tableau/tableau-viz-engineer` (extension iframe + SVG export), `web-design/frontend-implementer` (vega-embed/Evidence), `frontend-engineering/react-implementation-engineer` (react-vega). Each prior points to the neutral skill, states the Gate 101 security rule, and degrades gracefully (guidance even without a render tool).
- **Skill count** bumped `40 → 41` in `plugin.json` description and marketplace catalog.
- **Version** `0.149.4 → 0.150.0` in `.claude-plugin/plugin.json`, the `copilot/plugin.json` mirror, and the `marketplace.json` catalog entry (lockstep).

### Notes

- **Security is load-bearing:** Gate 101 must-fail half (a mutant template with `data.url` must exit 1) is the teeth assertion that makes the linter a real gate. Any PR adding a `spec-patterns/` template routes through `security-reviewer` — this is declared in the SKILL.md as an invariant, not a suggestion.
- **Migration:** none — additive skill, knowledge file, and agent priors; nothing in a consumer's installed plugin wiring changes on `/plugin marketplace update`.
- **Coordination caveat:** the queued `data-viz-designer` phases 2–7 (currently unrealized) will inherit this skill when they land. The plan specifies that `data-viz-designer` invokes `declarative-visualization` rather than re-implementing spec authoring.

## 0.149.4 — 2026-06-11

### Added

- **New always-on agent discipline: "Verify the load-bearing assumption before a high-impact activity"** ([`CLAUDE.md`](CLAUDE.md) § Capability Grounding Protocol). Before an activity whose impact is large or hard to reverse (delete / recreate / drop / migrate / force-overwrite / mass-edit / publish / prod change), the agent must name the single assumption the activity rests on and verify it — cheapest means first (authoritative doc, inspect the real artifact, or a reversible probe) — and prefer the smaller-blast-radius path that tests the premise before reaching for the irreversible one. Closes the costliest shape of the confident-reasoning error: a wrong premise driving an irreversible activity that "succeeds" mechanically while solving the wrong problem, where the cleanup dwarfs the task. Composes with "Read the error before you re-route" (verify a failure's *cause*) and "Check why a constraint exists" (verify a *constraint*); this verifies the *premise*. Distinct from `design_checkins` (which pauses for the human's judgment) — this is the agent checking its *own* belief. Grounded in a real 2026-06-11 case (a managed-solution import: 19 Dataverse entities deleted + recreated *twice* to "move them out of the Active layer," a non-goal the docs flag; the real fix was an in-place behavior flag, no delete). Adds a matching anti-pattern bullet.
- Version **0.149.3 → 0.149.4** in `.claude-plugin/plugin.json`, the `copilot/plugin.json` mirror, **and** the `marketplace.json` catalog entry (lockstep).

### Notes

- **Migration:** none — an additive behavioral discipline in the constitution (inherited by every agent + ported to Copilot CLI via the auto-loaded `CLAUDE.md`/`AGENTS.md`); nothing in a consumer's installed plugin wiring changes on `/plugin marketplace update`.

## 0.149.3 — 2026-06-10

### Added

- **New consumer-facing best-practice: "Checkpoints / `/rewind` are the recovery layer — they undo Claude's edits, not the world's side-effects"** ([`best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md)). The repo shipped a thorough _prevention_ stack (runaway brake / dod-gate / task-scope / `guard-destructive` / tribunal / containment posture) and git-based recovery (`branch-archive`), but no rule on Claude Code's native _recovery layer_ — checkpoints + `/rewind` (Esc-Esc). The rule pairs the feature with its load-bearing boundary: a checkpoint reverts Claude's file edits + the conversation, but **not** `Bash` side-effects, network/external state, or DB writes — so it complements git commits + the destructive-action guards, never replaces them. Index bumped 16 → 17 rules. Surfaced by the 2026-06-10 Claude-subreddit scan ([`docs/research/2026-06-10-claude-subreddit-scan/README.md`](../../docs/research/2026-06-10-claude-subreddit-scan/README.md)); 1 of 4 findings approved, the rest denied/deferred as already-covered or out-of-core-scope.
- **Official-API data-access tooling** — `scripts/reddit-scan.py` (Reddit OAuth Data API) + `scripts/content-scan.py` (Brave Search discovery, open-web body fetch with a ToS-respecting `NEVER_FETCH` boundary + an http/https SSRF guard). Both stdlib-only, credentials via env vars.

### Notes

- **Migration:** none — additive markdown (a new best-practice + the index row) + repo-level scripts; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.
- **Version note:** re-versioned `0.149.0 → 0.149.3` on merge so it lands above the `0.149.2` lint-fix that took the catalog first.

## 0.149.2 — 2026-06-10

### Fixed

- **`skills/pbir-layout-engine/lint.py` couldn't find its PBIR reference when installed as a symlink into a consumer repo** (the `ravenclaude setup` default for GitHub Copilot CLI). `_repo_root()` locates the sibling-plugin reference `plugins/power-platform/knowledge/pbir-enhanced-reference.md` via `os.path.abspath(__file__)` four-dirs-up — but `abspath` does **not** follow symlinks, so under a symlinked install (`<consumer>/.claude/skills/pbir-layout-engine/` → the marketplace clone) it resolved to the consumer's parent dir (e.g. `/workspaces`) and `parse_visual_type_enum()` raised `EnumParseError` (exit 3), breaking `check-7` (PBIR `visualType` validation) for every Copilot-CLI consumer. **Fix:** a new `_reference_file_root()` resolves the reference via `os.path.realpath(__file__)` (follows the symlink back to the marketplace), with a `$RAVENCLAUDE_DIR` override for forks / the non-symlink `cp -r` install path, falling back to `_repo_root()` for the run-from-checkout (dev) case. **The `_resolve_safe()` input-path sandbox boundary is untouched** — it stays anchored to `_repo_root()` (the consumer's working tree), so no security boundary changes. Replaces the brittle per-repo `/workspaces/plugins → ~/RavenClaude/plugins` symlink workaround with a root-cause fix every consumer inherits. Verified end-to-end (resolves from both the checkout and a simulated symlink install); Gate 92 stays green.
- Version **0.149.1 → 0.149.2** in `.claude-plugin/plugin.json`, the `copilot/plugin.json` mirror, **and** the `marketplace.json` catalog entry (lockstep).

## 0.148.1 — 2026-06-10

### Added

- **`skills/webfetch-hardening/SKILL.md`** — a new "**When the fetch itself is blocked — the 403 / refusal route ladder**" section. Complements the existing return-envelope sanitizer (which hardens a body you *received*) with what to do when `WebFetch` returns `403 Forbidden` / "unable to fetch". Grounded in a live 2026-06-10 route-test: a 403 is **target-side bot-blocking, per-target, not a blanket egress block** (`raw.githubusercontent.com` fetched while `anthropic.com`/`github.blog`/`example.com` 403'd); `archive.org` is refused at the tool layer and `WebFetch` exposes no UA/header controls, so Wayback + UA-spoofing are unavailable. The ladder: **`WebSearch` (reads bot-blocked content) → domain MCP (Microsoft-Learn / GitHub) → a non-blocked host → secondaries last.** Surfaced by, and consumed by, the freshness-anchor docs in `claude-app-engineering` + `ai-coding-model-guidance`.
- Version **0.148.0 → 0.148.1** in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry (lockstep).

## 0.148.0 — 2026-06-10

### Fixed

- **`rc-deep-research` workflow crashed at startup under the current workflow runtime (`Date.now()` / `new Date()` forbidden).** The v0.140.0 eval-stats wiring added per-phase wall-clock timing (`_runStartedMs`, `_phaseWindows`, `duration_ms`, `run_window`, plus a per-op `latency` and an ISO `ts`) that calls `Date.now()` / `new Date()` **unconditionally** (top-level + per-`phase()`, not gated by `runId`). The workflow runtime forbids those APIs (they break in-session resume) and throws, so **every** `rc-deep-research` invocation failed at startup — surfaced when deepening the power-platform scout finds. Replaced the 10 call sites with a deterministic, resume-safe monotonic time source (`_now()` / `_isoNow()`) in **both** byte-identical copies (`.claude/workflows/rc-deep-research.js` + the bundled `skills/rc-deep-research/rc-deep-research.js` mirror). Gate 52 (dispatch-evaluator disabled-floor) stays green — the copied wrapper block is untouched.

### Notes

- **Known limitation (documented inline):** the eval-stats timing fields are now monotonic ORDINALS, not wall-clock ms. The adaptive-run-classifier **Phase 6** eval grader buckets real transcript `usage` by these per-phase windows, which now needs a separate runtime-legal time source (an agent-returned timestamp, or a base time passed via `args`). Phase 6 was already deferred; this is tracked as its follow-up. The **research output itself does not depend on timing**, so interactive runs are fully restored.
- **Migration:** none — the workflow lives in the marketplace repo's own `.claude/workflows/` (the bundled mirror changed but its behavior is a bug-fix-to-runnable); nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

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
