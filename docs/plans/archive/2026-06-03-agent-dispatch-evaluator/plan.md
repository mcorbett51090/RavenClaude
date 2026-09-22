# Plan — Agent-Dispatch Pre-Evaluator (universal model right-sizing)

**Slug:** `agent-dispatch-evaluator` · **Depth:** quick · **Date:** 2026-06-03 · **Route:** stays local (pending G7)
**Synthesized from:** `plan-A.md` (Opus, system-architect), `plan-B.md` (Sonnet, Claude-app-substrate), `gap-delta.md`. Resolutions applied per gap-delta column 5.

---

## Why we're doing this

The prior /forge (`adaptive-run-classifier`) tiered models per phase **inside the deep-research workflow**. This /forge extends the principle **everywhere an agent is dispatched** — Workflow `agent()` calls, top-level Agent tool dispatches from conversation, tribunal seats in `thing-decide.py`. A small Haiku classifier evaluates `{subagent_type, description, prompt-head}` and binds (downgrades AND upgrades) the model selection, with a hybrid carve-out (allowlist for trivial types + per-call skip marker), a quality-regression sampler, and a single-flag rollback.

**Aggressive choices the user made** (per G0 AskUserQuestion): widest scope (Agent + workflows + tribunal seats), full binding both directions. This plan absorbs the blast radius with strong protective design.

---

## Phase 0 — Verification gate (≤1 day)

**Pre-build gate:** none (entry).

**Three load-bearing verifications:**

1. **Hook event for top-level Agent intercept** (gap-delta C1, BLOCK-tier from claims-table #2).
   **VERIFIED THIS SESSION** via WebFetch + Read: `updatedInput` IS supported in `PreToolUse` `hookSpecificOutput`, BUT the existing `hooks.json` matcher set (read in-session: `Bash|Read|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*|AskUserQuestion`) contains **no `Agent` or `Task` matcher**. The documented Agent-lifecycle hook event is `SubagentStart` (post-spawn, DENY-only — cannot mutate `model` in-flight).
   **Architectural consequence:** binding-mutation paths are:
   - **Workflow `agent()` wrapper** — in-process JS, always binding.
   - **`thing-decide.py` seat-dispatch** — in-process Python dict, always binding (but tribunal seats stay shadow-only per Phase 4).
   - **`SubagentStart` hook** — DENY+suggested-redispatch advisory at the top-level Agent surface.

2. **Runaway-brake exemption for evaluator's own classifier call** (claim #5, gap-delta C10).
   **Verify in this phase:** Read `plugins/ravenclaude-core/hooks/runaway-brake.sh` to confirm that a `claude -p --bare` subprocess invocation does NOT enter the agent's tool-call stream (and thus doesn't count against `max_total` or trip `max_consecutive`). Panel A's mechanism (subprocess) is sound; Phase 0 confirms it empirically.

3. **Evaluator caching is impossible at MVP scale** (gap-delta C2).
   **Verified this session** via re-read of `plugins/claude-app-engineering/knowledge/prompt-caching-playbook.md`: Haiku 4.5 min cacheable = 4,096 tokens; Sonnet 4.6 min = 1,024. Evaluator prompt is ~600-900 stable + ~200 volatile per call → **below both minimums**. **Design must NOT set `cache_control`** on evaluator calls (write penalty with no possible read). Evaluator runs uncached; per-call cost (~$0.001) is the lever, NOT caching.

**Acceptance:** all three flipped in `claims-table.md` with this-session source citations. Architecture pivot from Panel A's PreToolUse(Agent) design to Panel B's wrapper-primary design captured here.

**Time-box:** 0.5-1 day. Owner: this session + maintainer.

---

## Phase 1 — Skill contract, classifier prompt, schema (1-2 days)

**Pre-build gate:** Phase 0 complete.

**Work:**
- `plugins/ravenclaude-core/skills/agent-dispatch-evaluator/SKILL.md` — the artifact. Defines:
  - **Classifier input schema:** `{subagent_type, description, prompt_head[:500 tokens], requested_model, caller_context (workflow|toplevel|tribunal_seat)}`.
  - **Classifier output schema:** `{verdict: "keep"|"upgrade"|"downgrade", suggested_tier: "fast"|"balanced"|"top", confidence: "low"|"medium"|"high", rationale: string, signals: string[]}`. Forced `tool_choice:{type:"tool", name:"classify_dispatch"}` to suppress retries.
  - **Tier table REUSED from `plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md`** — single source of truth across both classifiers. `[verify-at-use — 2026-05-31]` marker on SKUs.
  - **NO `cache_control`** anywhere — explicit non-caching design with the minimum-token rationale (gap-delta C2).
  - **Carve-out allowlist** (built-in): `Explore`, `statusline-setup`, the implicit `claude` catch-all. Plus per-call `{_predispatch: 'skip'}` opt-out marker for workflows running their own classifier.
  - **Precedence rules:**
    - For tribunal seats (`caller_context: 'tribunal_seat'`): evaluator runs in **shadow mode forever for MVP** (gap-delta C3) — verdict logged to Sága, NEVER mutates `cfg["panel"][seat]["model"]`. Re-evaluate after 4-6 weeks of data.
    - For Workflow `agent()` calls already inside a `run_config` context: evaluator downgrade is binding (subject to nothing); evaluator upgrade above `run_config.tiers[phase]` is **advisory only** (gap-delta C2 alternative A3 from Panel B — explicit configuration should not be overridden by per-dispatch heuristic).
    - For top-level Agent dispatches (no `run_config`): full binding both directions, BUT executed via DENY+redispatch (SubagentStart can't mutate).
  - **Fail-open contract:** evaluator timeout (2s default) → pass-through with audit-log entry `{verdict:"passthrough", reason:"timeout"}`. NEVER blocks a dispatch.
  - **Worked examples** for 5 dispatch classes (research-heavy, code-review, statusline-setup carve-out, tribunal-seat shadow, allowlist hit).

- `plugins/ravenclaude-core/skills/agent-dispatch-evaluator/templates/dispatch-config.json` — defaults:
  ```json
  {
    "schema_version": "1",
    "enabled": false,
    "mode": "shadow",
    "subagent_type_allowlist": ["Explore", "statusline-setup", "claude"],
    "downgrade_blocked_types": [],
    "quality_sampler": { "rate": 0.20, "judge_model": "claude-haiku-4-5", "use_batch_api": true },
    "latency_circuit_breaker": { "median_ms_threshold": 1500, "window_size": 20 },
    "tribunal_seat_mode": "shadow",
    "async_mode": false,
    "rationale": "default baseline — disabled"
  }
  ```

- `.repo-layout.json` `allowed_globs` updated for `plugins/ravenclaude-core/skills/agent-dispatch-evaluator/**`, `.ravenclaude/dispatch-config.json`, `.ravenclaude/runs/dispatch-eval/**`.

**Acceptance:** SKILL.md scored ≥4/6 by `agent-quality-rubric`; JSON-schema validates `templates/dispatch-config.json`; prettier exit 0; audit-gates unchanged.

**Agents:** `prompt-and-context-engineer` (primary, owns SKILL.md + classifier prompt), `architect` (intercept-shape contract), `security-reviewer` (mandatory — this is in the critical path of EVERY dispatch).

---

## Phase 2 — Workflow `agent()` wrapper (PRIMARY binding path) (2 days)

**Pre-build gate:** Phase 1 merged. Re-confirm `agent()` opts signature in workflow scripts.

**Work:** wrap the existing Workflow `agent(prompt, opts)` helper. Live integration with the deep-research workflow + any other multi-agent workflow.
- `loadDispatchConfig()` — reads `.ravenclaude/dispatch-config.json`. `enabled:false` → pass-through (regression floor). `mode:'shadow'` → call classifier, log verdict, but DO NOT mutate `opts.model`. `mode:'binding'` → apply verdict per precedence rules.
- `evaluateDispatch({subagent_type, description, prompt_head, requested_model, caller_context})` — fires `claude -p --bare --output-format json --model haiku-4-5` subprocess (NOT an Agent dispatch — structurally exempt from `runaway-brake.sh` per Phase 0). 2s timeout (`timeout 2` wrapper). Fail-open. Returns `{verdict, suggested_tier, confidence, rationale}`.
- `agent(prompt, opts)` wrapper logic:
  1. If `opts._predispatch === 'skip'` → pass-through (no classifier call).
  2. If `opts.subagent_type` in allowlist → pass-through.
  3. Call `evaluateDispatch`. On timeout / fail → pass-through.
  4. Apply verdict per precedence rule (binding for non-tribunal; advisory for tribunal; advisory upward for in-run_config calls).
  5. Log full verdict to `.ravenclaude/runs/dispatch-eval/<session-id>.jsonl` (one line per call).
- **Latency circuit-breaker:** rolling-20-call median latency tracker (in-memory per session); if median > 1500ms, flip the rest of the session to pass-through mode and write a Heimdall amber event (gap-delta C6 — Panel A's mitigation, now standard).
- **Async mode** (`async_mode: true`, default OFF): verdict applies to the NEXT dispatch of same `subagent_type` within the session. Phase 5 latency measurement decides whether `async_mode` becomes the default in Phase 6 (gap-delta C5).

**Acceptance:**
- `enabled:false` path produces **byte-identical** `opts.model` to today (new **Gate 52** — regression floor in `scripts/audit-gates.sh`).
- `mode:'shadow'` logs verdicts without mutation.
- `mode:'binding'` downgrades a known-Opus dispatch to Sonnet on a shallow task; upgrades a known-Haiku dispatch to Sonnet on a deep task.
- Timeout → pass-through; rolling latency >1500ms → session-pass-through + Heimdall event.
- Allowlist + `_predispatch:'skip'` carve-outs work unconditionally.

**Agents:** `prompt-and-context-engineer`, `architect`, `code-reviewer`, `tester-qa`.

---

## Phase 3 — `SubagentStart` hook (top-level Agent advisory) (1 day, parallel with Phase 4)

**Pre-build gate:** Phase 1 merged.

**CRITICAL caveat from Panel B R1:** `SubagentStart` fires **AFTER** subagent process initiation, not before tool-call commit. A DENY may be a late-stage cancel, not a pre-dispatch intercept. **Phase 3 acceptance MUST verify deny actually prevents the original dispatch from completing** (no work done, no tokens spent). If deny is post-commit:
- Demote `SubagentStart` to **audit-only** (logs verdict to dashboard, no DENY emitted).
- Workflow wrapper (Phase 2) becomes the SOLE binding path for top-level dispatches.
- Document the limitation prominently in SKILL.md.

**Work:** `plugins/ravenclaude-core/hooks/agent-dispatch-evaluator.sh` — `SubagentStart` matcher:
- Off-by-default short-circuit (single grep on `dispatch-config.json` for `enabled:`).
- Carve-outs (allowlist match → exit 0 zero-cost; `_predispatch:'skip'` in input → exit 0).
- **Tribunal-seat detection:** `THING_SEAT_ACTIVE=1` in env → shadow-mode (log verdict, exit 0).
- Otherwise: invoke `evaluateDispatch` via the same `claude -p --bare` subprocess.
- On downgrade verdict: emit `{permissionDecision:"deny", permissionDecisionReason:"[evaluator] this dispatch was right-sized to <tier>; re-issue with model=<suggested_model>. Pass _predispatch:'skip' to bypass."}` — caller redispatches. (Same DENY+redispatch shape `route-decision-review.sh` uses.)
- On upgrade verdict: emit `{permissionDecision:"allow", hookSpecificOutput:{additionalContext:"[evaluator] this dispatch may warrant <suggested_tier> — current run continues at requested model"}}` — advisory only (cannot mutate at this surface).
- Fail-open envelope: missing `jq` / timeout / unparseable → exit 0 (allow).
- `_emit_hook_event` for every verdict.
- **MANDATORY shadow-soak coverage for Copilot host** (gap-delta C7 — Panel A R3): Phase 5 fixtures MUST include `THING_HOST=copilot` dispatches to verify the DENY+redispatch pattern doesn't silently suppress capability on Copilot CLI.
- Register in `plugins/ravenclaude-core/hooks/hooks.json` + `.claude/settings.json` dev-mirror.

**Acceptance:**
- Hook fires on `SubagentStart`; evaluator times out → exit 0.
- Downgrade → DENY with structured reason; **deny actually prevents the original dispatch** (load-bearing — if not, hook demoted to audit-only).
- Upgrade → ALLOW + advisory additionalContext.
- `enabled:false` → exit 0 with single stat check.
- Copilot-host fixture: DENY+redispatch doesn't silently fail (R3 mitigation).

**Agents:** `architect`, `code-reviewer`, `security-reviewer` (critical path — mandatory).

---

## Phase 4 — `thing-decide.py` tribunal-seat integration (1 day, parallel with Phase 3)

**Pre-build gate:** Phase 1 merged.

**Per gap-delta C3 — Panel A's more conservative position adopted:** tribunal seats run in **shadow mode forever for MVP**. Re-evaluate after 4-6 weeks of data shows safe-to-mutate cases.

**Work:** in `plugins/ravenclaude-core/scripts/thing-decide.py`, before each `_run_seat()` call:
- Call `evaluateDispatch(caller_context='tribunal_seat', subagent_type=role, description=panel.label, ...)`.
- Verdict logged to the seat's Sága entry under `.ravenclaude/runs/thing/decisions/<id>/seats/<seat>.json` as `evaluator_shadow: {verdict, suggested_tier, would_have_changed_model_to:..., confidence, rationale}`.
- **Never mutates** `cfg["panel"][role]["model"]` — preserves the v0.32.0 ≥2-distinct-backbones invariant (Panel A R1).
- Provides the data substrate to decide if seat-evaluator should ever go binding.

**Acceptance:**
- Tribunal decision-review run produces seat records with `evaluator_shadow` field populated.
- Model actually used at each seat is unchanged from pre-evaluator behavior.
- Backbone-diversity invariant unaffected.

**Agents:** `architect`, `code-reviewer`.

---

## Phase 5 — Quality-regression sampler + dashboard tab + auto-revert (2 days, after Phase 2)

**Pre-build gate:** Phase 2 merged.

**Work:** `scripts/eval-dispatch-quality.py` — sampled post-hoc judge over downgraded dispatches.
- **Sample rate:** 20% during MVP shadow soak (more signal); drops to 5% post-flip (gap-delta C4 best-of-both).
- **Sampling mechanism:** on sample-trigger, the dispatch's transcript is captured to `.ravenclaude/runs/dispatch-eval/samples/<verdict-id>/transcript.json` (reuses existing transcript-capture infra).
- **Judge:** Haiku 4.5 via Anthropic Batch API (50% off, `[verify-at-use — anthropic.com/pricing]`). Batch is right for non-latency-critical post-hoc scoring.
- **Rubric (3-axis, each 0-3):** task completion / output fidelity / format correctness. Pass threshold ≥7/9. **Threshold calibrated** from baseline (Sonnet-tier) median score on the fixture set — NOT a fixed constant.
- **Position-bias control:** judge prompt randomizes order of sampled output vs same-prompt Sonnet baseline (A/B comparison).
- **Auto-revert circuit-breaker:** if a single `subagent_type` accumulates ≥3 consecutive failed samples in the rolling-50-sample window for that type, the script appends `subagent_type` to `dispatch-config.json` `downgrade_blocked_types`; next session's evaluator skips downgrade for those types. Logs `REVERT` event to Víðarr.
- **Dashboard tab** (`/__evaluator` endpoint + read-only "Dispatch evaluator" tab, mirroring Heimdall/Víðarr pattern): downgrade/upgrade counts per `subagent_type`, judge-flagged regressions, current effective-model per type, latency p50/p95, single-button kill-switch.
- **Eval fixture:** 30+ past Agent dispatches from this session's transcripts + recent sessions, labeled by human judge with expected tier. Measures:
  - Evaluator precision/recall vs human labels (≥85% downgrade precision, ≥70% upgrade recall).
  - Median wall-clock latency added per dispatch (decides Phase-6 sync vs async default).
  - **Copilot-host coverage** in fixtures (gap-delta C7 mandate).

**Acceptance — new Gate 70 (auto-revert circuit):**
- Fixture-driven: a stubbed judge flagging 3 consecutive regressions on type `foo` writes `foo` into `downgrade_blocked_types`; next hook fire no-ops `foo`.
- Must-fail half: stubbed judge passing all samples leaves `downgrade_blocked_types` unchanged.

**Acceptance — Phase 5 gate:**
- Precision ≥85% downgrade; recall ≥70% upgrade.
- Median latency reported (decides Phase 6 default mode).
- Copilot-host fixtures pass.
- Dashboard tab renders.

**Agents:** `eval-engineer` (primary), `tester-qa`, `data-engineer`, `architect` (gate definition).

---

## Phase 6 — Shadow→binding flip + release (1 day after 2-week shadow soak)

**Pre-build gate:** Phase 5 eval green; 2-week dev-repo shadow-mode data accumulated; verify-at-use on Batch pricing + tier SKUs the day before merge.

**Work:**
- Review the shadow data: ≥30% Opus dispatches identified as downgradable with zero quality regressions in the sampler; ≤5 false-upgrade events; median latency at or below 1500ms (or async confirmed as the default).
- Flip `templates/dispatch-config.json`:
  - `enabled: true`
  - `mode: 'binding'` (or `'shadow'` permanently if eval fails — defer the flip rather than ship broken)
  - `async_mode` set per Phase 5 latency measurement
- Tribunal `tribunal_seat_mode` stays `'shadow'` regardless.
- Bump `plugins/ravenclaude-core/.claude-plugin/plugin.json` minor + `marketplace.json` lockstep.
- Milestones entry in `plugins/ravenclaude-core/CLAUDE.md`.
- Dashboard pointer card under Settings → "Dispatch evaluator — enabled/disabled in `.ravenclaude/dispatch-config.json`".
- **Migration note in PR:** "rollback = flip `enabled: false` in `dispatch-config.json`; per-type disable via `downgrade_blocked_types: [<subagent_type>]`."

**Acceptance:** plugin-release-checklist passes; audit-gates clean; prettier exit 0; migration note in PR body.

**Agents:** maintainer, `project-manager`.

---

## Dependency DAG

```
Phase 0 (verify gate, ≤1d)
   │
   ▼
Phase 1 (skill + schema + templates, 1-2d)
   │
   ├──────────────────────────┬──────────────────────────┐
   ▼                          ▼                          ▼
Phase 2                    Phase 3                    Phase 4
(workflow wrapper, 2d)     (SubagentStart hook, 1d)   (tribunal shadow, 1d)
   │                          │                          │
   ▼                          └──────────────────────────┘
Phase 5 (sampler + dashboard + auto-revert, 2d)
   │
   ▼ (2-week dev-repo shadow soak)
Phase 6 (binding flip + release)
```

**Critical path:** 0 → 1 → 2 → 5 → 6 ≈ **7d build + 14d shadow soak**.
**Parallel branches:** Phase 3 + Phase 4 from Phase 1; Phase 5 depends on Phase 2 only.

---

## Alternatives (load-bearing choices kept on the record)

| # | Decision | Chosen | Alternatives | Trade-off |
|---|---|---|---|---|
| A1 | Skill home | `plugins/ravenclaude-core/skills/agent-dispatch-evaluator/SKILL.md` | claude-app-engineering | Reuses tier table from the prior /forge's skill (same plugin); single-source-of-truth |
| A2 | Evaluator substrate | Haiku 4.5 forced-tool call | Deterministic rule LUT / hybrid | Haiku-only MVP; deterministic fast-path is a Phase-7 optimization once dashboard shows one-way `subagent_type` patterns |
| A3 | Cache strategy | **No `cache_control`** anywhere | Pad prompt to ≥4,096 to enable Haiku cache | Padding degrades evaluator focus for minimal cost benefit at Haiku prices |
| A4 | Top-level binding mechanism | Workflow wrapper (primary) + SubagentStart DENY+redispatch (advisory) | `PreToolUse(Agent)` mutation | Empirical: no Agent matcher in hooks.json (verified in-session by Read) |
| A5 | Tribunal-seat enforcement | **Shadow forever for MVP** | Advisory + binding-when-below-gate_floor | Protects ≥2-distinct-backbones invariant; shadow data informs whether to ever go binding |
| A6 | Upgrade binding interaction with `run_config.tiers` | Downgrade binding; **upgrade advisory** | Both binding | Explicit per-phase configuration set at workflow start shouldn't be overridden by per-dispatch heuristic |
| A7 | Sync vs async dispatch evaluator default | OFF (sync), decided by Phase 5 latency measurement | Async-on-by-default | Measurement-driven default; staleness risk in async mode (in-memory cache keyed by subagent_type) |
| A8 | Sample rate | 20% during MVP soak; 5% post-flip | Fixed 5% / fixed 20% | More signal during soak when calibration matters; less overhead steady-state |
| A9 | Judge model | Haiku 4.5 via Batch (50% off) | Sonnet 4.6 nightly | Batch-able post-hoc scoring; A/B comparison controls position bias |

---

## Risk matrix (Panel A R1-R3 + Panel B R1-R3, merged + scored)

| # | Risk | P × I | Mitigation | Owner |
|---|---|---|---|---|
| RM1 | **SubagentStart fires post-spawn — DENY may be late-stage cancel, not pre-commit intercept** (Panel B R1) | High × High | Phase 3 acceptance MUST verify deny actually prevents original dispatch from completing. If post-commit, **demote SubagentStart to audit-only** and rely on workflow wrapper as sole binding path for top-level dispatches. | `architect` |
| RM2 | **Tribunal seat mutation risks ≥2-distinct-backbones invariant** (Panel A R1) | High × High | Phase 4 = shadow-only forever for MVP. Data accumulates for 4-6 weeks; only then re-evaluate. | `architect` |
| RM3 | **Latency degradation invisible to runaway-brake** (Panel A R2) | Medium × High | Built-in rolling-20-call median latency circuit-breaker: if >1500ms, flip rest of session to pass-through + Heimdall amber event. Phase 5 measures real latency on the fixture. | `prompt-and-context-engineer` |
| RM4 | **DENY+redispatch may silently fail on Copilot CLI host** (Panel A R3) | Medium × High | Phase 5 shadow-soak fixtures MUST include `THING_HOST=copilot` dispatches. Deny-reason text includes the literal redispatch JSON ("tee up the human-only residue" rule). | `architect` + `security-reviewer` |
| RM5 | **Async-mode cache staleness can downgrade a genuinely-hard dispatch** (Panel B R3) | Medium × Medium | Default async mode OFF. When enabled, cache key includes complexity-bucket hash (description length + prompt_head length), not just `subagent_type`. Phase-7 refinement. | `prompt-and-context-engineer` |
| RM6 | **Silent downgrade quality regression** (Panel A's core motivation for the sampler) | Medium × High | Quality-regression sampler with 20% rate during soak; 3-consecutive-failure auto-revert per `subagent_type`; A/B-comparison rubric controls position bias. | `eval-engineer` |
| RM7 | **Evaluator subprocess counts against runaway-brake** (Panel B R2) | Medium × Medium | Phase 0 confirms `claude -p --bare` subprocess does NOT enter agent's tool-call stream (Panel A mechanism). If wrong: add explicit brake-exemption via `RC_EVALUATOR_CLASSIFIER=1` env signal the brake reads. | `architect` (Phase 0) |
| RM8 | **Schema drift across the two classifiers** (prior /forge + this one) | Low × Medium | Tier table imported from the prior /forge's SKILL.md, not re-authored. `schema_version: "1"` on both `run_config` and `dispatch-config`. Single docs page documents both. | `prompt-engineer` |

---

## Definition of Done

- [ ] Phase 0 verifications captured in `claims-table.md` with this-session sources (claim #2 flipped to `CONFIRMED — SubagentStart-only for top-level + workflow wrapper for binding`).
- [ ] **Version bumps lockstep** — `plugins/ravenclaude-core/.claude-plugin/plugin.json` + `marketplace.json`. Minor on Phase 1; patches on 2-5; minor on Phase 6.
- [ ] **Layout allow-list** updated for `plugins/ravenclaude-core/skills/agent-dispatch-evaluator/**`, `.ravenclaude/dispatch-config.json`, `.ravenclaude/runs/dispatch-eval/**`, `scripts/eval-dispatch-quality.py`, `plugins/ravenclaude-core/hooks/agent-dispatch-evaluator.sh`, `plugins/ravenclaude-core/hooks/tests/test-agent-dispatch-evaluator.sh`.
- [ ] **Prettier** `--write` then `--check` exit 0 every phase.
- [ ] **Hook executable bit** set; registered in `plugins/ravenclaude-core/hooks/hooks.json` + `.claude/settings.json` dev-mirror.
- [ ] **Audit-gates: new Gate 52** (workflow-wrapper regression floor — `enabled:false` byte-identical opts). **New Gate 70** (auto-revert circuit). **New Gate 71** (hook fail-open invariants — all 6 fail paths emit allow). Each must-fail half registered.
- [ ] **`_emit_hook_event`** wired for every verdict emission (allow, deny, advisory, error) — required for dashboard.
- [ ] **2-week shadow-mode soak completed** with dev-repo data before Phase 6 flip.
- [ ] **Eval gate (Phase 5):** precision ≥85% downgrade, recall ≥70% upgrade, latency reported, Copilot-host fixtures pass, sampler+auto-revert demonstrated.
- [ ] **Quality-regression sampler** running on schedule; dashboard tab renders.
- [ ] **Migration note in PR body:** rollback = flip `enabled: false`; per-type disable via `downgrade_blocked_types`.
- [ ] **Tribunal-seat mode permanently `shadow` for MVP.** Re-evaluation issue filed for 4-6 weeks out.
- [ ] **Claims #6, #7, #8, #9 re-verified** day before merge against vendor docs.
- [ ] **Security review sign-off** on the hook (critical path of every dispatch).

---

## Settling steps for the unverified claims

| Claim | Settling step | Where in plan |
|---|---|---|
| #2 — PreToolUse Agent mutation | **Resolved Phase 0:** no `Agent` matcher exists; `SubagentStart` DENY-only + workflow wrapper binding. | Phase 0 + Phase 1 SKILL.md. |
| #5 — Runaway-brake counting evaluator calls | Read `runaway-brake.sh`; confirm `claude -p --bare` subprocess exemption mechanism. | Phase 0. |
| #6 — Evaluator caching feasibility | Re-read `prompt-caching-playbook.md`; confirm below-minimum design rationale. | Phase 0 + Phase 1 SKILL.md. |
| #7 — Forced tool_choice | Re-read `tool-use-and-structured-output.md`. | Phase 1. |
| #8 — Added latency estimate | Phase 5 eval measures real latency on fixture. | Phase 5. |
| #9 — Classifier extracts enough signal from prompt_head | Phase 5 precision/recall against human-labeled fixture. | Phase 5. |
| Batch pricing + tier SKUs | `[verify-at-use]` markers; day-before-merge check. | Phase 0 + Phase 6. |

---

## Open questions parked

- **Per-`subagent_type` deterministic fast-path** — Phase 7 optimization once dashboard shows one-way patterns.
- **Cross-session learning** — evaluator stateless per-dispatch in MVP; aggregation a follow-up.
- **Tribunal seats going binding** — re-evaluate at 4-6 weeks from shadow data.
- **Codex / Copilot equivalent ports** — contract is substrate-neutral, port deferred.
- **Async-mode cache key with complexity-bucket hash** — Phase 7 once async is the default.
