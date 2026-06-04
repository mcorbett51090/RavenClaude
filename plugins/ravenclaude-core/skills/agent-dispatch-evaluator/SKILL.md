---
name: agent-dispatch-evaluator
description: "Universal pre-dispatch model right-sizer. A single Haiku 4.5 forced-tool call evaluates `{subagent_type, description, prompt_head}` at every Agent dispatch / Workflow `agent()` call / `thing-decide.py` seat dispatch and binds (downgrades AND upgrades) the model selection. Carved out behind `.ravenclaude/dispatch-config.json` `enabled: false` so adoption is opt-in and rollback is one line. Tribunal-seat verdicts are shadow forever for MVP (protects the v0.32.0 backbone-diversity invariant)."
last_reviewed: 2026-06-03
confidence: high
---

# Skill: agent-dispatch-evaluator

## What this is

The **wire contract** between every agent dispatch surface and the cheap Haiku call that tells it which model tier to use. Where the [`adaptive-run-classifier`](../adaptive-run-classifier/SKILL.md) right-sizes **multi-phase workflow runs**, this skill right-sizes **individual dispatches** — Workflow `agent()` calls, top-level Agent tool dispatches from conversation, and tribunal seats in [`scripts/thing-decide.py`](../../scripts/thing-decide.py). One forced-tool Haiku call per dispatch. No agent loop. No retries to parse.

Plan reference: [`docs/plans/2026-06-03-agent-dispatch-evaluator/plan.md`](../../../../docs/plans/2026-06-03-agent-dispatch-evaluator/plan.md). Phase 0 verification: `.ravenclaude/runs/forge/agent-dispatch-evaluator/phase-0-verification.md` (gitignored). Cross-panel resolutions: `.ravenclaude/runs/forge/agent-dispatch-evaluator/gap-delta.md` (gitignored).

## The `dispatch_config` JSON schema

Every field below ships in every dispatch_config. Versioned (RM8 — schema-drift insurance) and substrate-neutral (tier *labels*, not SKUs).

```json
{
  "schema_version": "1",
  "enabled": false,
  "mode": "shadow",
  "subagent_type_allowlist": ["Explore", "statusline-setup", "claude"],
  "downgrade_blocked_types": [],
  "quality_sampler": {
    "rate": 0.20,
    "judge_model": "claude-haiku-4-5",
    "use_batch_api": true
  },
  "latency_circuit_breaker": {
    "median_ms_threshold": 1500,
    "window_size": 20
  },
  "tribunal_seat_mode": "shadow",
  "async_mode": false,
  "rationale": "default baseline — disabled"
}
```

**Field semantics (one-liners):**

- `schema_version` — string; `"1"` today. Adapter logs a warning + falls back to defaults on mismatch (RM8).
- `enabled` — wire-level kill switch. `false` (default) → pass-through (regression floor, **Gate 52** enforces byte-identical `opts.model` to today).
- `mode` — `"shadow"` (verdict logged, never mutates) or `"binding"` (verdict applied per precedence rules below).
- `subagent_type_allowlist` — built-in carve-outs (see §Carve-outs). Evaluator skipped, zero cost.
- `downgrade_blocked_types` — per-`subagent_type` revert list, appended by the auto-revert circuit-breaker (§Quality sampler) on 3 consecutive failed samples.
- `quality_sampler` — Haiku-4.5-judge sampling config; Batch API for 50% off (`[verify-at-use — anthropic.com/pricing]`).
- `latency_circuit_breaker` — rolling-window median latency trip (RM3).
- `tribunal_seat_mode` — `"shadow"` forever for MVP (RM2 — protects the ≥2-distinct-backbones invariant). Do not flip without 4-6 weeks of shadow data.
- `async_mode` — fire-and-forget mode; default `false` (sync). Phase 5 latency measurement decides Phase-6 default.
- `rationale` — mandatory one-sentence human-readable justification of the config; auditable trace.

## Classifier input schema

The evaluator receives one envelope per dispatch:

```json
{
  "subagent_type": "deep-researcher",
  "description": "Research the 2026 EU AI Act failure modes for downstream OSS deployers",
  "prompt_head": "<first 500 tokens of the prompt verbatim>",
  "requested_model": "claude-opus-4-7",
  "caller_context": "workflow"
}
```

- `subagent_type` — the agent role being dispatched (`deep-researcher`, `code-reviewer`, etc.).
- `description` — the dispatch description (the same string passed to the Agent tool / `agent()` opts).
- `prompt_head` — first 500 tokens of the full prompt. Truncation is load-bearing — keeps the evaluator prompt small.
- `requested_model` — the SKU the caller asked for (the baseline the evaluator votes against).
- `caller_context` — one of `"workflow"` / `"toplevel"` / `"tribunal_seat"`. Drives precedence rules.

## Classifier output schema

Forced `tool_choice: {"type": "tool", "name": "classify_dispatch"}` (suppresses retries per [`tool-use-and-structured-output.md`](../../../claude-app-engineering/knowledge/tool-use-and-structured-output.md)):

```json
{
  "verdict": "keep",
  "suggested_tier": "balanced",
  "confidence": "high",
  "rationale": "deep-researcher with vendor-docs scope — Sonnet's adaptive thinking matches the task; Opus over-spec for non-contested synthesis",
  "signals": ["vendor_docs_scope", "non_contested", "single_pass_synthesis"]
}
```

- `verdict` — `"keep"` (requested model is right-sized), `"upgrade"`, or `"downgrade"`.
- `suggested_tier` — `"fast"` / `"balanced"` / `"top"` (the substrate tier the evaluator recommends).
- `confidence` — `"low"` / `"medium"` / `"high"`. Low-confidence verdicts log but don't mutate even in binding mode (§Precedence rules).
- `rationale` — mandatory one-sentence justification. The auditable trace.
- `signals` — short tags the evaluator extracted from the dispatch envelope. Drives dashboard aggregation.

## Substrate tier table

**Single source of truth: [`adaptive-run-classifier/SKILL.md` §"Substrate tier table"](../adaptive-run-classifier/SKILL.md#substrate-tier-table).** Do NOT re-author the table here. Both classifiers share the same tier vocabulary (`fast` / `balanced` / `top` → Claude / Codex / Copilot SKU map), with `[verify-at-use — 2026-05-31]` markers on every SKU (the underlying lineup re-dates monthly).

The adapter (workflow wrapper or SubagentStart hook) holds the ONE mapping table; the evaluator emits *labels*, never SKUs. SKU rotation happens in the tier table; this skill stays substrate-neutral.

## The three intercept points + their authority

The gap-delta C1 / RM1 architectural pivot: there is **no `Agent` matcher** in PreToolUse `hooks.json` (verified in-session — see `.ravenclaude/runs/forge/agent-dispatch-evaluator/phase-0-verification.md` (gitignored) §P0.1). Binding-mutation is therefore distributed across three surfaces, each with different authority:

| Surface | Mechanism | Authority |
|---|---|---|
| **Workflow `agent()` wrapper** | In-process JS mutation of `opts.model` | **Always binding** (primary path). |
| **`thing-decide.py` seat-dispatch** | In-process Python mutation of `cfg["panel"][seat]["model"]` | **Shadow forever for MVP** (RM2 — protects v0.32.0 ≥2-distinct-backbones invariant). |
| **`SubagentStart` hook** | Shadow-logs a right-sizing verdict at the top-level Agent surface | **Audit-only as shipped** (RM1 — see below). Emits no DENY; the workflow wrapper is the sole binding path. |

**Caveat (RM1) — RESOLVED to audit-only (Phase 3 shipped):** Panel B R1 flagged that `SubagentStart` fires **after** subagent process initiation, so a DENY may be a late-stage cancel (wasting the spawn) rather than a pre-commit intercept. Phase 3 acceptance required verifying that a DENY actually prevents the original dispatch from completing (no work done, no tokens spent). **That verification needs a live armed dispatch, which the Phase-3 build session could not run** — so per the plan's own fail-disposition the hook ships **audit-only** ([`hooks/agent-dispatch-evaluator.sh`](../../hooks/agent-dispatch-evaluator.sh)): it computes the right-sizing verdict and shadow-logs it, but **never emits a DENY**, regardless of `mode`. See the dedicated section below for the shipped behavior and the exact promotion path.

## Precedence rules

Verdict application is conditional on caller_context + existing config + verdict direction:

- **Tribunal seats (`caller_context: "tribunal_seat"`)** — `tribunal_seat_mode: "shadow"` forever for MVP. Verdict logged to the seat's Sága entry as `evaluator_shadow: {verdict, suggested_tier, would_have_changed_model_to: ..., confidence, rationale}`. **NEVER mutates** `cfg["panel"][seat]["model"]`. Re-evaluate after 4-6 weeks of shadow data (RM2).
- **Workflow `agent()` calls already inside a `run_config` context (`caller_context: "workflow"` + active run_config):**
  - Downgrade → **binding** (subject to nothing — the adaptive-run-classifier set a tier ceiling, the evaluator may right-size below it).
  - Upgrade above `run_config.tiers[phase]` → **advisory only** (explicit per-phase configuration set at workflow start should not be overridden by per-dispatch heuristic). Gap-delta C6 / A6.
- **Top-level Agent dispatches (no `run_config`, `caller_context: "toplevel"`)** — full binding both directions via DENY+redispatch (subject to SubagentStart's intercept timing — see RM1 caveat).
- **Low-confidence verdicts** — log but do not mutate, even in binding mode. Calibrated against the Phase 5 fixture set.

## Carve-outs

Two unconditional skip paths that suppress the evaluator entirely:

1. **Built-in `subagent_type` allowlist:** `Explore`, `statusline-setup`, `claude` catch-all. Pass-through with zero classifier cost (single grep on the allowlist before the subprocess fires).
2. **Per-call `{_predispatch: 'skip'}` marker** — workflows that run their own classifier (e.g. the rc-deep-research workflow consuming an `adaptive-run-classifier` `run_config`) pass `_predispatch: 'skip'` in `opts`. Pass-through, no double-evaluation.

The allowlist is extensible in `dispatch-config.json`; the `_predispatch` marker is hard-coded in the wrapper logic (not user-tunable — it's an integration contract).

## NO `cache_control` design

**Explicit non-caching invariant.** Per Phase 0 P0.3 verification + [`prompt-caching-playbook.md`](../../../claude-app-engineering/knowledge/prompt-caching-playbook.md): Haiku 4.5 minimum cacheable = 4,096 tokens; Sonnet 4.6 = 1,024.

| Component | Estimate |
|---|---|
| Stable (tools + system rubric + tier vocabulary) | ~600-900 tokens |
| Volatile (dispatch envelope) | ~200 tokens |
| **Total** | **~800-1,100 tokens** |

Both totals are **below both model minimums**. Setting `cache_control` on the evaluator prompt incurs the **1.25× write penalty** (5-min TTL) or **2× write penalty** (1-h TTL) for **ZERO possible cache read** — pure cost penalty. **The skill MUST NOT set `cache_control` on the evaluator call.**

Per-call cost at Haiku 4.5 pricing (~$0.25/MTok input, current `[verify-at-use — anthropic.com/pricing]`): ~$0.0002 per dispatch. At 100 dispatches/day = $0.02/day. **Latency is the load-bearing risk, not cost** (~300-800ms cold-start per Haiku call) — gated by the latency circuit-breaker (RM3).

**If the evaluator prompt grows organically to ≥4,096 tokens** (e.g. via worked-examples block addition), revisit. Phase 5 monitors `cache_creation_input_tokens` to detect accidental breakpoints — a NEGATIVE assertion (must be 0 if prompt stayed under min).

## The fail-open contract

The evaluator is in the critical path of EVERY dispatch. It MUST fail open.

- **2s default timeout** (`timeout 2` wrapper around `claude -p --bare`).
- **Fail-open triggers:** missing `jq` / classifier timeout / unparseable JSON / subprocess crash / network error.
- **On any fail trigger:** pass-through the original `requested_model` with an audit-log entry `{verdict: "passthrough", reason: "timeout" | "error" | "missing_jq", ...}`.
- **NEVER blocks a dispatch.** A broken evaluator must not break the agent.

## The latency circuit-breaker (RM3)

In-memory per-session rolling-20-call median latency tracker. If median >1500ms:

1. Flip the rest of the session to pass-through mode (no further classifier calls).
2. Emit a Heimdall amber event (`evaluator-latency-trip`) via `_emit_hook_event`.
3. Verdict log captures the trip so Phase 5 latency measurement sees real distribution, not the mitigated one.

The threshold is config-tunable (`latency_circuit_breaker.median_ms_threshold`); window size defaults to 20 (`latency_circuit_breaker.window_size`). The trip is **per-session, not persistent** — a new session starts fresh.

## The runaway-brake structural exemption

Per Phase 0 P0.2 verification: the evaluator runs as a `claude -p --bare` subprocess **spawned from inside the hook itself**. A subprocess spawned by a hook **never enters the agent's tool-call stream**, so it cannot trigger another PreToolUse event and cannot be hashed by [`runaway-brake.sh`](../../hooks/runaway-brake.sh)'s `{tool_name, tool_input}` cksum chain.

**The exemption is structural, not configured.** No additional brake-exemption flag needed. The design must keep this structural property:

**Caveat:** if a future refactor moves the classifier to a wrapped Bash-tool-issued call (e.g. for portability under a Copilot adapter that can't spawn subprocesses), the exemption breaks and the evaluator's calls WOULD count against `max_total` / `max_consecutive`. A Phase 2 regression check spawns 100 dispatches with `enabled: true` and asserts the runaway-brake's per-session counter file does NOT exceed 100 (one tool call per dispatch, none from the evaluator).

## The quality-regression sampler

Post-hoc judge over **downgraded** dispatches (the failure mode the sampler exists to catch). Per gap-delta C4 — best-of-both: more signal during MVP soak, less overhead steady-state.

- **Sample rate:** 20% during MVP shadow soak (calibration matters most); drops to 5% post-flip.
- **Judge model:** Haiku 4.5 via Anthropic **Batch API** (50% off `[verify-at-use — anthropic.com/pricing]`). Batch is right for non-latency-critical post-hoc scoring.
- **Rubric (3-axis, each 0-3):** task completion / output fidelity / format correctness. Pass threshold ≥7/9. **Calibrated** from baseline (Sonnet-tier) median on the fixture set — NOT a fixed constant.
- **Position-bias control:** judge prompt randomizes the order of the sampled output vs same-prompt Sonnet baseline (A/B comparison).
- **Auto-revert circuit-breaker:** if a single `subagent_type` accumulates ≥3 consecutive failed samples in the rolling-50-sample window for that type, the script appends `subagent_type` to `dispatch-config.json` `downgrade_blocked_types`; next session's evaluator skips downgrade for that type. Logs `REVERT` event to Víðarr.

The sampling mechanism captures the dispatch's transcript to `.ravenclaude/runs/dispatch-eval/samples/<verdict-id>/transcript.json` (reuses existing transcript-capture infra).

## Audit substrate

Every verdict (allow / deny / advisory / error / passthrough) emits to `hook-events.jsonl` via `_emit_hook_event` (sources [`hooks/_emit-event.sh`](../../hooks/_emit-event.sh) — the v0.110.0 substrate). The `rule` argument flows through `_scrub_reason()` from [`hooks/_scrub.sh`](../../hooks/_scrub.sh) before write (substrate-wide secret-scrub invariant preserved).

Rule names emitted by the evaluator:

| Rule | Meaning |
|---|---|
| `evaluator-keep` | Verdict was `keep` — no change to `requested_model`. |
| `evaluator-downgrade` | Verdict applied a downgrade. |
| `evaluator-upgrade` | Verdict applied an upgrade (or advisory upgrade if `run_config` precedence wins). |
| `evaluator-error` | Subprocess crashed / unparseable JSON / missing `jq`. |
| `evaluator-passthrough` | Fail-open triggered (timeout / latency-trip / allowlist / `_predispatch: 'skip'`). |
| `evaluator-latency-trip` | Rolling median >1500ms; session flipped to pass-through. |

Heimdall (perimeter alerts) and Víðarr (security log) tabs surface evaluator verdicts automatically — they already read `hook-events.jsonl`. The `dispatch-config.json` toggle joins the `comfort-posture.yaml` audit family.

Per-verdict detailed log: `.ravenclaude/runs/dispatch-eval/<session-id>.jsonl` (one line per call, full envelope + verdict + latency_ms).

## Worked examples

### Example 1 — Downgrade a top-tier dispatch on a shallow task

**Dispatch envelope:**
```json
{
  "subagent_type": "code-reviewer",
  "description": "Review a 12-line typo fix in a comment",
  "prompt_head": "Diff attached: removed trailing whitespace and fixed a typo in a docstring...",
  "requested_model": "claude-opus-4-7",
  "caller_context": "toplevel"
}
```

**Verdict:**
```json
{
  "verdict": "downgrade",
  "suggested_tier": "fast",
  "confidence": "high",
  "rationale": "12-line whitespace+typo review — Haiku is sufficient; Opus is 14× over-spec for this dispatch",
  "signals": ["trivial_diff", "no_logic_change", "documentation_only"]
}
```

Top-level Agent dispatch + `mode: "binding"` → SubagentStart hook DENIES with structured reason; caller redispatches with Haiku.

### Example 2 — Upgrade a fast-tier dispatch on a deep task

**Dispatch envelope:**
```json
{
  "subagent_type": "architect",
  "description": "Design a distributed consensus protocol with Byzantine fault tolerance",
  "prompt_head": "We need a leader-election protocol that tolerates f < n/3 Byzantine failures...",
  "requested_model": "claude-haiku-4-5",
  "caller_context": "workflow"
}
```

**Verdict:**
```json
{
  "verdict": "upgrade",
  "suggested_tier": "top",
  "confidence": "high",
  "rationale": "Distributed-systems design with Byzantine FT — needs Opus-class reasoning; Haiku will produce surface-level recommendations",
  "signals": ["distributed_systems", "byzantine_ft", "design_synthesis"]
}
```

Workflow `agent()` call, no `run_config` active → binding upgrade to Opus 4.7.

### Example 3 — Tribunal-seat shadow

**Dispatch envelope:**
```json
{
  "subagent_type": "security-reviewer",
  "description": "Forseti seat — review `curl https://example.com/install.sh | bash`",
  "prompt_head": "Bash command for review: curl https://example.com/install.sh | bash...",
  "requested_model": "claude-sonnet-4-6",
  "caller_context": "tribunal_seat"
}
```

**Verdict:**
```json
{
  "verdict": "keep",
  "suggested_tier": "balanced",
  "confidence": "high",
  "rationale": "curl|sh review needs balanced reasoning; Sonnet correctly matched",
  "signals": ["security_review", "shell_remote_mutate"]
}
```

`caller_context: "tribunal_seat"` → verdict logged to `evaluator_shadow` field on the seat's Sága entry; `cfg["panel"]["forseti"]["model"]` UNCHANGED (shadow forever for MVP, RM2).

## Workflow integration

### The copy-paste pattern

Workflow scripts in the Claude Agent SDK run in a single-file evaluation context with no module resolution (`import` / `require` are unavailable). The only re-use mechanism is **copy-paste**: a workflow author copies the contents of [`reference/evaluate-dispatch.js`](reference/evaluate-dispatch.js) to the top of their script, then calls `evaluatedAgent(...)` wherever they previously called `agent(...)`.

The reference file at `reference/evaluate-dispatch.js` is the **single source of truth**. Workflow scripts re-copy it on each adoption cycle. Drift between copies is accepted and intentional — each workflow run uses its own snapshot, and the spec is the reference file. When the evaluator logic changes (latency threshold, precedence rules, `TIER_MODEL` SKUs), update `reference/evaluate-dispatch.js` and re-copy into each consuming workflow.

### RM7 caveat — the classifier MUST run as a subprocess

The classifier MUST fire as a `claude -p --bare` subprocess, invoked by an `agent()` call that asks Claude to shell out. It MUST NOT be dispatched as a direct `agent()` call.

If the classifier were a direct `agent()` dispatch it would enter the agent's tool-call stream, count against `runaway-brake.sh`'s `max_total` / `max_consecutive` counters, and potentially trip the runaway brake on a long workflow. The structural exemption (a subprocess spawned by a hook-level shell invocation never enters the tool-call stream) is what makes the evaluator safe on the critical path of every dispatch.

See §"The runaway-brake structural exemption" above and the plan's RM7 row for the full verification record.

### Worked example — adopting the wrapper in a workflow

Below is a representative 15-line excerpt. The full three-function block is copied from [`reference/evaluate-dispatch.js`](reference/evaluate-dispatch.js) and placed before the workflow's own logic.

```js
// ── Copy from reference/evaluate-dispatch.js (top of script) ──
// const TIER_MODEL = { ... };
// const DISPATCH_EVAL_LOG_DIR = ...;
// const _latency = { window: [], tripped: false };
// async function loadDispatchConfig() { ... }
// async function evaluateDispatch(...) { ... }
// async function evaluatedAgent(prompt, opts, dispatchCfg) { ... }
// ── End copy ──

// ── Workflow start: load config ONCE ──
const dispatchCfg = await loadDispatchConfig();

// ── Replace agent() calls with evaluatedAgent() ──
const scopeResult = await evaluatedAgent(
  scopePrompt,
  { label: "scope", agentType: "ravenclaude-core:architect", schema: SCOPE_SCHEMA },
  dispatchCfg,
);

// Workflows that already use an adaptive-run-classifier run_config pass the
// _run_config_phase marker so the evaluator applies the run_config precedence
// rule (downgrade binding; upgrade advisory only):
const fetchResult = await evaluatedAgent(
  fetchPrompt,
  { label: "fetch", agentType: "ravenclaude-core:deep-researcher",
    model: TIER_MODEL[runConfig.tiers.fetch],
    _run_config_phase: "fetch" },
  dispatchCfg,
);
```

The three carve-outs (regression floor, per-call skip, allowlist) are handled inside `evaluatedAgent` — the calling code does not need to check them.

## Phase 3 — `SubagentStart` hook (audit-only)

[`hooks/agent-dispatch-evaluator.sh`](../../hooks/agent-dispatch-evaluator.sh) is the top-level-dispatch surface. It is registered on `SubagentStart` in both wiring paths (`hooks/hooks.json` via `${CLAUDE_PLUGIN_ROOT}` for consumers; `.claude/settings.json` via `${CLAUDE_PROJECT_DIR}` for marketplace dev). **It ships audit-only and never denies a dispatch** — the RM1 resolution above.

**What it does when a subagent is about to start:**

1. **Off-by-default short-circuit** — a single `grep` for `"enabled": true` on the resolved `dispatch-config.json` (project `.ravenclaude/` first, then the plugin template as a read-only fallback). `enabled:false` (the shipped default) → exit 0, zero cost.
2. **Carve-outs** — `_predispatch:"skip"` anywhere in the input, or a `subagent_type` matching the allowlist → exit 0 before any classifier call.
3. **Tribunal-seat detection** — `THING_SEAT_ACTIVE=1` in the environment marks the spawn as a tribunal seat (also handled by Phase 4 inside `thing-decide.py`); recorded with `caller_context: "tribunal_seat"` and allowed.
4. **Classifier** — fires the same `claude -p --bare --model claude-haiku-4-5-20251001` subprocess the wrapper uses (RM7 structural exemption from the runaway brake), with a 3 s `timeout`. `claude` absent on PATH / timeout / unparseable JSON → exit 0 (fail-open).
5. **Shadow-log** — the verdict is written to **two sinks**: `hook-events.jsonl` via `_emit_hook_event` (verdict `"warn"` → Heimdall's grey/advisory tier, never a security signal) and `.ravenclaude/runs/dispatch-eval/<session>.jsonl` (the JSONL the Phase-5 quality sampler reads), with `applied: "shadow"`.
6. **Always allows** — exit 0 with no `permissionDecision`, regardless of verdict (`keep`/`upgrade`/`downgrade`) or `mode`. **This is the audit-only invariant.**

**Proven by Gate 90** ([`hooks/tests/test-gate90-dispatch-evaluator-audit-only.sh`](../../hooks/tests/test-gate90-dispatch-evaluator-audit-only.sh)): disabled-by-absence → allow; a stubbed `downgrade` verdict → allow with **no deny** (the audit-only teeth); allowlist + `_predispatch:skip` carve-outs → allow; and a **must-fail half** — a mutated hook that emits a deny on `downgrade` is caught by the audit-only assertion, proving the gate has teeth.

**Promotion path (audit-only → binding), if ever warranted:** in a session that can run a live armed dispatch, verify whether a `SubagentStart` DENY actually prevents the original dispatch from completing (no work done, no tokens spent) — e.g. dispatch a subagent with the hook emitting a deny and confirm via the transcript / token accounting that the spawn did no work. **Only if deny is confirmed pre-commit:** replace the final audit-only `emit_allow` (§9 of the hook) with the DENY+redispatch envelope the plan specifies (`permissionDecision: "deny"`, `permissionDecisionReason` carrying the suggested model + the `_predispatch:'skip'` bypass note — the same shape `route-decision-review.sh` uses), gate it on `mode == "binding"` and `confidence != "low"`, and update Gate 90's audit-only assertions to the new contract. Until then, the workflow wrapper (Phase 2) is the sole binding path for top-level dispatches.

## Phase 4 — `thing-decide.py` tribunal-seat shadow (implemented, shadow forever)

[`scripts/thing-decide.py`](../../scripts/thing-decide.py) (the decision-review tribunal) computes a dispatch-evaluator **shadow** verdict for each convened seat and records it in the decision's Sága entry as a per-seat `evaluator_shadow: {verdict, suggested_tier, would_have_changed_model_to, confidence, rationale}`. Per RM2 / gap-delta C3 (Panel A's conservative position), **seats are shadow forever for MVP** — the integration **never mutates `cfg["panel"][role]["model"]`**, so the v0.32.0 ≥2-distinct-backbones invariant is untouched. The shadow data accumulates so a future call can decide whether seat right-sizing is ever safe to make binding (re-evaluate after 4–6 weeks).

Design discipline (total isolation from the verdict path): the shadow reads `dispatch-config.json` and is a **zero-cost no-op when `enabled` is not `true`** (the default everywhere — byte-identical to pre-P4); every classifier call is wrapped so any failure simply omits the shadow; and the result rides **only** in the audit entry — it is never read back into the decision logic. **Proven by Gate 91** ([`hooks/tests/test-gate91-tribunal-shadow.py`](../../hooks/tests/test-gate91-tribunal-shadow.py)): disabled → no `evaluator_shadow` (no-op); enabled → every seat shadowed; and the verdict/binding is **identical** between the enabled and disabled runs (the teeth: the shadow records a downgrade target without ever moving the verdict).

## Output Contract

This skill emits no runtime artifact of its own — it is a **contract**, consumed by the workflow wrapper (Phase 2), the SubagentStart hook (Phase 3), and `thing-decide.py` (Phase 4). When the prompt-engineer or an architect critiques an instance of this contract (e.g. a workflow's evaluator integration in a PR), the response ends with the cross-plugin Structured Output JSON block per [`structured-output/SKILL.md`](../structured-output/SKILL.md):

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "one-sentence outcome",
  "deliverables": ["..."],
  "handoff_recommendation": {"to_specialist": "<role or null>", "reason": "..."},
  "confidence": 0.0,
  "risks_or_open_questions": ["..."],
  "next_actions": ["..."]
}
---RESULT_END---
```

## References

- Plan + risk matrix: [`docs/plans/2026-06-03-agent-dispatch-evaluator/plan.md`](../../../../docs/plans/2026-06-03-agent-dispatch-evaluator/plan.md) (Phase 1 work-list, RM1-RM8, intercept-shape contract).
- **Phase 3 hook (audit-only):** [`hooks/agent-dispatch-evaluator.sh`](../../hooks/agent-dispatch-evaluator.sh) + Gate 90 [`hooks/tests/test-gate90-dispatch-evaluator-audit-only.sh`](../../hooks/tests/test-gate90-dispatch-evaluator-audit-only.sh).
- **Phase 4 tribunal-seat shadow:** [`scripts/thing-decide.py`](../../scripts/thing-decide.py) (`_load_dispatch_cfg` / `_evaluator_shadow`) + Gate 91 [`hooks/tests/test-gate91-tribunal-shadow.py`](../../hooks/tests/test-gate91-tribunal-shadow.py).
- Phase 0 verification: `.ravenclaude/runs/forge/agent-dispatch-evaluator/phase-0-verification.md` (gitignored local run-dir artifact) (the three load-bearing flips: no-Agent-matcher, subprocess-exemption, no-cache).
- Cross-panel resolutions: `.ravenclaude/runs/forge/agent-dispatch-evaluator/gap-delta.md` (gitignored local run-dir artifact) (C1-C10).
- **Tier table source of truth:** [`plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md`](../adaptive-run-classifier/SKILL.md) §"Substrate tier table".
- Cache discipline (minimum tokens, TTL, breakpoints): [`plugins/claude-app-engineering/knowledge/prompt-caching-playbook.md`](../../../claude-app-engineering/knowledge/prompt-caching-playbook.md).
- Forced-tool structured output (the `tool_choice` pattern): [`plugins/claude-app-engineering/knowledge/tool-use-and-structured-output.md`](../../../claude-app-engineering/knowledge/tool-use-and-structured-output.md).
- Hook-event substrate (v0.110.0): [`plugins/ravenclaude-core/hooks/_emit-event.sh`](../../hooks/_emit-event.sh) + [`plugins/ravenclaude-core/hooks/_scrub.sh`](../../hooks/_scrub.sh).
- Agent-quality rubric (the bar this skill is scored against): [`plugins/ravenclaude-core/skills/agent-quality-rubric/SKILL.md`](../agent-quality-rubric/SKILL.md).
- Companion skill format: [`plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md`](../adaptive-run-classifier/SKILL.md) (parallel shape: an auditable verdict via a cheap upstream call).
- Structured Output Protocol: [`plugins/ravenclaude-core/skills/structured-output/SKILL.md`](../structured-output/SKILL.md).

---

## Self-score against agent-quality-rubric (adapted for skills)

| Dimension | Score | Justification |
|---|---|---|
| Mission clarity | 5 | Stated in §"What this is" sentence 1: universal pre-dispatch model right-sizer. Three surfaces named explicitly. |
| Scope sharpness | 5 | Explicit not-this: differs from adaptive-run-classifier (per-dispatch vs per-run); shadow-only for tribunal seats; no `cache_control`; no SKU naming. |
| Capability Grounding | 4 | Cites Phase 0 verifications inline (P0.1, P0.2, P0.3) with `file:line` links; references the substrate (`_emit_hook_event`, `_scrub_reason`). Could add an explicit alternate-methods callout for the SubagentStart caveat. |
| Output-Contract completeness | 5 | Explicit Output Contract section + Structured Output JSON block per the cross-plugin standard; rule names enumerated for the audit substrate. |
| Escalation paths | 4 | Implicit through the three-intercept-point table + the RM1 demotion-to-audit-only escape hatch. Could be sharper with a named-handoff table. |
| Example scenarios | 4 | Three worked examples covering downgrade / upgrade / tribunal-shadow. Could add a fail-open example and a latency-trip example. |

**Total: 27/30 — ships as-is per the rubric's 27-30 disposition band.**
