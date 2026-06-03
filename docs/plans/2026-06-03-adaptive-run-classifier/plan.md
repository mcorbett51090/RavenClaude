# Plan — Adaptive Pre-Execution Classifier for Research/Agentic Workflows

**Slug:** `adaptive-run-classifier`
**Depth:** quick · **Date:** 2026-06-03 · **Route:** stays local (pending G7 confirmation)
**Synthesized from:** `plan-A.md` (Opus, system-architect), `plan-B.md` (Sonnet, Claude-app-substrate), `gap-delta.md`. Conflict resolutions applied per gap-delta column 5.

---

## Why we're doing this

Just-finished research run cost **4.9M tokens / 103 agents / 36 min**. Estimated **~40-50% waste** (~2M tokens) because the workflow hardcodes every cardinality knob and uses one model tier for every phase. 22 of 25 verify votes were unanimous 3-0 (third voter was pure cost); 16 of 21 fetches were `learn.microsoft.com` URLs that should have routed through the Microsoft Docs MCP. Target post-port: **≤2.4M tokens** on the same question with no degradation in confirmed-claim count.

---

## Phases

### Phase 0 — Pre-build verification gate (≤0.5d)

**Pre-build gate:** none (this IS the entry).
**Work:** confirm the four outside-repo claims from `claims-table.md` with this-session reads:
- **#7** cache TTL/min-cacheable per `plugins/claude-app-engineering/knowledge/prompt-caching-playbook.md` (5-min default, 1-h opt-in via `"ttl":"1h"` with 2× write, Haiku 4.5 min ~4,096 tokens, Sonnet 4.6 min ~1,024).
- **#8** Batch API ~50% off → mark `[verify-at-use — anthropic.com/pricing]` in skill; do NOT quote ratio in CHANGELOG until measured.
- **#9** substrate tier SKUs per `plugins/ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md` (dated 2026-05-31).
- **#6** `copilot-hook-adapter.sh` SessionStart path lines 137-146 dual-emits `additionalContext` AND plain stdout — already confirmed by Panel A via Read.

**Acceptance:** all four claim rows in `claims-table.md` flipped to `CONFIRMED — <this-session-source>` or carry a `[verify-at-use]` marker with named verifier.
**Agents:** none required (manual confirm during Phase 1 authoring).

### Phase 1 — Substrate contracts & feature flag (1-2d)

**Pre-build gate:** Phase 0 complete.
**Work:**
- `plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md` — the **artifact**. Defines:
  - The `run_config` JSON schema with new `schema_version: "1"` field (gap-delta C5).
  - The classifier system prompt (cache-friendly: stable instructions above breakpoint, question below).
  - The substrate tier table (fast/balanced/top → SKU per Claude/Codex/Copilot) dated 2026-05-31, with `[verify-at-use]` marker. **Does NOT hardcode model IDs into the script** — the table is the single source of truth.
  - Worked examples per task_class (`research_loop_vendor_docs`, `research_loop_contested`, `research_loop_general`).
  - The **Copilot informational-only** clarification (gap-delta C7 + Panel-A R3): Copilot adapter surfaces the rationale; per-call Copilot model routing is parked.
- `plugins/ravenclaude-core/skills/adaptive-run-classifier/templates/run-config.json` — default config (`enabled: false`, `schema_version: "1"`, `batch_verify: false` per gap-delta C2, `rationale: "default baseline"`).
- `plugins/ravenclaude-core/skills/adaptive-run-classifier/templates/run-config.schema.json` — JSON-schema for validation.
- Update `.repo-layout.json` `allowed_globs` to cover `plugins/ravenclaude-core/skills/adaptive-run-classifier/**` and `.ravenclaude/run-config.json`.

**Acceptance:**
- `python3 -m jsonschema -i templates/run-config.json templates/run-config.schema.json` exits 0.
- SKILL.md renders in the dashboard skill-list.
- `scripts/audit-gates.sh` passes unchanged (no new gate yet).
- Prettier exit 0.

**Agents:** `prompt-engineer` (SKILL.md authoring per `agent-quality-rubric`), `architect` (contract review), `code-reviewer`.

### Phase 2 — Claude in-script substrate adapter (2d)

**Pre-build gate:** Phase 1 merged. Re-read `prompt-caching-playbook.md`. Reconfirm `agent()` opts signature in the deep-research script (line 96, etc.).

**Work:** in the workflow script (or a sibling helper file consumed by it):
- `loadRunConfig()` — reads `.ravenclaude/run-config.json`. If absent or `enabled:false`, returns hardcoded baseline matching today's constants (regression floor). If `enabled:true` and `task_class` missing, calls the classifier (one Haiku Messages API call with forced `tool_choice:{type:"tool",name:"classify_run"}` per gap-delta C8). **Flag is read ONCE into a closure variable and snapshotted into the audit log — frozen for the rest of the run** (Panel-A R1, gap-delta C9).
- `adapter.opts(phase, tierLabel, reasoningLabel)` — returns `{model, thinking?, cache_control?}`:
  - `tierLabel→model` via the SKILL.md tier table (one mapping table, not spread across the script).
  - `reasoningLabel→thinking:{type:"adaptive"}` ONLY when `model` is Sonnet/Opus (gap-delta C3 — Haiku 4.5 has no extended thinking; passing the param API-errors). Unit test asserts `adapter.opts("fast","low")` returns no `thinking` key.
  - `cache_control:{type:"ephemeral", ttl:"1h"}` on the verify system block when the workflow's expected duration exceeds ~3 minutes (gap-delta C1 — baseline 36 min vastly exceeds 5-min default TTL; eat the 2× write penalty on call #1 to keep cache warm). Default to 5-min for shorter phases.
  - Layout: tools (stable schemas) → system [BREAKPOINT] → user (volatile claim text + vote index).
- Log every classifier verdict to `.ravenclaude/runs/run-classifier/<timestamp>.json` (audit substrate parallel to `.ravenclaude/runs/thing/decisions/`).

**Acceptance:**
- Baseline run with `enabled:false` produces **byte-identical** `agent()` opts across all 5 phases (snapshot test — this is the regression floor; **new Gate 51** in `scripts/audit-gates.sh`).
- `enabled:true` with a hand-crafted run_config flips Scope→Sonnet/adaptive-thinking, Verify-default→Haiku/no-thinking, Synthesize→Sonnet/adaptive-thinking.
- Unit test confirms `adapter.opts("fast", *)` never emits `thinking`.
- Classifier verdict logged with full rationale.

**Agents:** `prompt-and-context-engineer` (cache_control placement, classifier prompt), `architect` (adapter shape), `code-reviewer`, `tester-qa`.

### Phase 3 — Workflow port to consume run_config (1d)

**Pre-build gate:** Phase 2 merged + Gate 51 (regression snapshot) green.
**Work:** in `deep-research-wf_*.js`:
- Replace the 4 hardcoded constants (lines 12-15) with reads off `runCfg.knobs`.
- SCOPE_SCHEMA `maxItems` becomes `runCfg.knobs.angle_count`.
- Thread `adapter.opts(phase, runCfg.tiers[phase], runCfg.reasoning[phase])` into every `agent()` call site.
- **Per-claim verify-vote dispatch:** primary policy is the upfront lookup `runCfg.verify_policy[claim.sourceQuality]` (B's deterministic path). **Optional escalation** (A's logic): if `confidence:low` returned by any vote, fire an additional vote at the `verify_judgment` tier. **Audit log** `claim_tier_audit.jsonl` (one line per claim: `{claim_idx, initial_tier, votes_fired, escalated_to?, final_verdict}`) — gap-delta C4.
- `use_specialized_mcp && primary_source_host=="learn.microsoft.com"` → prepend a "prefer the Microsoft Docs MCP (`microsoft_docs_search` + `microsoft_docs_fetch`)" instruction in FETCH_PROMPT. **Prompt-string change only** — no new tool wiring.
- Emit `run_config.rationale` + the audit log path in the workflow `stats` block for transparency.
- **`batch_verify` stays in the schema but defaults `false`** (gap-delta C2). Phase 3 wires the threshold gate (`batch_verify && verifier_count>=10`) but the default config does NOT enable batch — Phase-5+ follow-up after sync-path savings are measured.

**Acceptance:**
- `enabled:false` path remains byte-identical (Gate 51 floor holds).
- `enabled:true` smoke run on a fixture question completes; `stats` contains `run_config` summary.
- `verify_policy` routing produces expected vote counts (unit-style assertion in the fixture harness).
- `claim_tier_audit.jsonl` written for the fixture run with at least one row per claim.

**Agents:** `prompt-and-context-engineer` (primary), `architect` (per-claim escalation logic), `tester-qa`.

### Phase 4 — Copilot SessionStart wiring (1d, parallel with Phase 5)

**Pre-build gate:** Phase 1 merged. Claim #6 already CONFIRMED.
**Work:** edit `plugins/ravenclaude-core/hooks/capability-orientation.sh` (NOT a new hook file per gap-delta C7) to append a compact one-liner to the existing `additionalContext` text WHEN `.ravenclaude/run-config.json` exists AND `enabled:true`:
> `"adaptive-run-classifier: enabled · task_class=<x> · tiers={scope:<t>,verify:<t>,synthesize:<t>} · rationale=<truncated to ≤512 chars, scrubbed via _scrub_reason>"`
No new hook event needed. No-op when `enabled:false` or file absent or malformed. Fail-safes for missing `jq` / file / JSON.

**Acceptance:**
- Under Claude Code, the banner appears in SessionStart context (hook fixture).
- Under the Copilot adapter (`copilot-hook-adapter.sh` sessionstart path), the existing dual-emit (lines 137-146) carries the appended text — covered by the adapter, no adapter change.
- Hook fail-safes silently no-op on all error paths.

**Agents:** `architect`, `code-reviewer`, `security-reviewer` (the rationale is potentially user-controlled text → `_scrub_reason` must be applied).

### Phase 5 — Measurement gate / eval harness (1-2d, parallel with Phase 4)

**Pre-build gate:** Phase 3 merged.
**Work:** `scripts/eval-adaptive-classifier.py` — fixture-based harness:
- **N=3 fixtures**, each a distinct task_class:
  1. **`research_loop_vendor_docs`** — the just-completed PP-description question (baseline known: 4.9M tokens / 103 agents).
  2. **`research_loop_contested`** — a comparison question (e.g. "Cube vs Metabase for a 5-tenant SaaS").
  3. **`research_loop_general`** — an open-web question (e.g. "What are the failure modes of the 2026 EU AI Act for downstream OSS deployers?").
- For each fixture: run **baseline** (`enabled:false`) + **adaptive** (`enabled:true`), capture `{subagent_tokens, agent_count, duration_ms, confirmed_claim_count, cache_read_input_tokens, cache_creation_input_tokens}` from the workflow result.
- **Graders** (Panel-B Phase 5):
  - Programmatic: `subagent_tokens ≤ 2.4M` on the PP fixture; `confirmed_claim_count` delta ≤ 1 vs baseline.
  - **Cache-hit-rate** per phase: `cache_read / (cache_read + input)`. Verify-phase target ≥ 0.5 (Panel B's R1: if Haiku-verify system block is <4096 tokens, this metric will surface the silent-no-cache failure).
  - LLM-as-judge on synthesis quality: Haiku 4.5 via Batch API (50% off, `[verify-at-use]`).
  - `classifier_output.rationale` human-readability: inspection.
- **Settles claim #11** (MCP vs WebFetch token ratio) via the PP-docs `use_specialized_mcp` comparison.
- Report under `.ravenclaude/runs/eval/adaptive-classifier-<YYYY-MM-DD>.md`.

**Acceptance:**
- Harness runs end-to-end against all 3 fixtures.
- Report shows ≥2× total token reduction across the 3 fixtures with `confirmed_claim_count` delta ≤ 1 each.
- Report includes the verified MCP/WebFetch ratio with retrieval timestamp.
- Cache-hit-rate ≥ 0.5 on verify phase (or a documented warning if not — escalate verify model to Sonnet 4.6 in the run_config defaults).

**Agents:** `tester-qa` (primary), `data-engineer` (metric capture), `eval-engineer` (judge design + Batch wiring), `architect` (gate definition).

### Phase 6 — Flag flip + docs + release

**Pre-build gate:** Phase 5 eval gate green. Verify-at-use on claims #8 (Batch pricing) and #9 (tier SKUs) the day before merge.
**Work:**
- Flip `templates/run-config.json` default to `enabled:true`.
- Bump `plugins/ravenclaude-core/.claude-plugin/plugin.json` AND `marketplace.json` versions (minor — user-visible behavior change). Lockstep per CI.
- Milestones entry in `plugins/ravenclaude-core/CLAUDE.md`.
- 5-line dashboard pointer card under Settings → "Adaptive run classifier — enabled/disabled per `.ravenclaude/run-config.json`".
- **Migration note in PR body:** "rollback = flip `enabled:true → false` in `.ravenclaude/run-config.json`."

**Acceptance:** plugin-release-checklist passes; audit-gates clean; prettier exit 0; migration note in PR body.

**Agents:** maintainer, `project-manager`.

---

## Dependency DAG

```
Phase 0 (verify gate, ≤0.5d)
   │
   ▼
Phase 1 (skill + schema + defaults, 1-2d)
   │
   ├──────────────────────────────────────────┐
   ▼                                          ▼
Phase 2 (Claude adapter, 2d)            Phase 4 (Copilot wiring, 1d, parallel)
   │                                          │
   ▼                                          │
Phase 3 (workflow port, 1d) ──────────────────┤
   │                                          │
   ▼                                          │
Phase 5 (eval harness, 1-2d) ─────────────────┘
   │
   ▼
Phase 6 (flag flip + release)
```

**Critical path:** 0 → 1 → 2 → 3 → 5 → 6 (≈ 7-9 days elapsed if serialized; ≈ 6-8 with Phase 4 parallel).
**Parallelizable:** Phase 4 starts after Phase 1 (only needs the schema); runs alongside Phases 2-5.

---

## Alternatives (load-bearing choices kept on the record)

| # | Decision | Chosen | Alternative(s) considered | One-line trade-off |
|---|---|---|---|---|
| A1 | Classifier artifact home | Skill (`SKILL.md`) | 14th specialist agent | Skill avoids routing-ambiguity; revisit if non-deep-research callers need it. |
| A2 | Config storage | `.ravenclaude/run-config.json` | env var `RC_RUN_CONFIG` | JSON is audit-loggable, dashboard-readable, restart-surviving; env var is lighter but invisible to Sága. |
| A3 | Classifier invocation | Per-run forced-tool Messages API call (Haiku 4.5) | Agent SDK `agent()` call inside workflow / pre-computed task-class→config map | Forced-tool single call is cheapest and yields the auditable `rationale`; Agent-SDK over-engineers a one-shot; pre-computed map loses the rationale. |
| A4 | Per-claim verify cardinality | Upfront `verify_policy[sourceQuality]` lookup + optional escalation on `confidence:low` | Uniform `verify_default` for all claims | Upfront lookup is deterministic; escalation captures the few genuinely-contested claims without paying the 3-vote tax on the 22/25 unanimous case. |
| A5 | Batch API on verify | **Schema field present, default `false` in MVP** | Default `true` from MVP / not in schema at all | Defer until synthesize-coupling design lands; ship savings from sync path first, then layer Batch as a follow-up. |
| A6 | Cache TTL on verify system block | `"1h"` (workflows ≥ ~3 min); `5m` for shorter | Always `5m` default | Baseline ran 36 min — 5m TTL expires mid-run, every post-expiry call pays write cost again; eat the 2× write penalty once. |
| A7 | Copilot wiring shape | Edit existing `capability-orientation.sh` (string-append) | New hook `inject-run-config-context.sh` | Less surface, fewer registrations, leverages adapter's existing dual-emit. |

---

## Risk matrix (Panel A R1-R3 + Panel B R1-R3, merged + scored)

| # | Risk | Prob × Impact | Mitigation | Owner |
|---|---|---|---|---|
| RM1 | **Cache minimum mismatch — Haiku 4.5 verify system block <4,096 tokens** silently runs uncached, blowing the ≤2.4M target. | High × High | Phase 5 eval reports cache-hit-rate per phase as an **explicit metric** (not "check later"). If below 0.5, escalate verify-default tier to Sonnet 4.6 in the default run_config (Sonnet min = 1,024). | `prompt-and-context-engineer` |
| RM2 | **Batch API latency coupling to synthesize** — workflow's synthesize consumes verify output synchronously; no async-continuation mechanism. | High × Medium (when batch is enabled) | Default `batch_verify:false` in MVP. Batch becomes a Phase-7+ follow-up requiring a workflow split or polling loop. **Not load-bearing on the headline savings.** | `architect` (design) |
| RM3 | **Mid-run feature-flag toggle inconsistency** — if `loadRunConfig()` re-reads on retry mid-run, baseline + adaptive opts get mixed. | Medium × High | Phase 2 reads flag exactly **ONCE** into a closure variable + snapshots into the audit log. State explicitly in SKILL.md and unit-test. | `architect` |
| RM4 | **Per-claim escalation observability blind spot** — without per-claim audit, aggregate token counts conflate fast-everywhere vs fast-then-escalated. | Medium × Medium | Phase 3 emits `claim_tier_audit.jsonl` (per-claim row: `{claim_idx, initial_tier, votes_fired, escalated_to?, final_verdict}`). Acceptance criterion. | `tester-qa` |
| RM5 | **Schema drift as the workflow evolves** — new phases adding knobs would silently fall back to defaults on old classifier output. | Medium × Low (now), High (over 6+ months) | `run_config.schema_version: "1"`; adapter logs warning on mismatch; classifier emits current version. Cheap insurance. | `prompt-engineer` |
| RM6 | **Thinking-param on Haiku 4.5** — passing `thinking:{type:"adaptive"}` to Haiku API-errors. | High × High (silent regression bug class) | Adapter conditionally emits `thinking` ONLY for Sonnet/Opus tiers. Unit test asserts `adapter.opts("fast", *)` never emits `thinking`. | `prompt-and-context-engineer` |
| RM7 | **Scope conflation on Copilot wiring** — "informational-only" must not drift into per-call Copilot model routing. | Low × Medium | SKILL.md explicitly marks Copilot wiring as informational-only-in-MVP, links to scope.md §Out-of-scope. PR template includes the check. | `prompt-engineer` |

---

## Definition of Done

- [ ] **Version bumps in lockstep** — `plugins/ravenclaude-core/.claude-plugin/plugin.json` minor on Phase 1, patch on Phases 2-5, minor on Phase 6. Matching `marketplace.json`. CI fails on drift.
- [ ] **Layout allow-list** — `.repo-layout.json` updated to cover `plugins/ravenclaude-core/skills/adaptive-run-classifier/**`, `.ravenclaude/run-config.json`, `scripts/eval-adaptive-classifier.py`. Layout-verification snippet from AGENTS.md run before each push.
- [ ] **Prettier** — `npx prettier --write . && npx prettier --check .` exit 0 before pushing every phase.
- [ ] **Audit-gates** — **new Gate 51** (baseline-regression floor, byte-identical opts when `enabled:false`) added to `scripts/audit-gates.sh` with must-fail half (a synthetic adapter returning differing opts when disabled). **No new Gate 52 — JSON-schema validation is a one-shot Phase-1 acceptance, not a steady-state CI gate.**
- [ ] **Eval gate** — Phase 5 report shows ≥2× total token reduction across 3 fixtures, no confirmed-claim regression, cache-hit-rate ≥ 0.5 on verify (or escalation documented).
- [ ] **Migration note** — PR body documents "rollback = flip `enabled` in `.ravenclaude/run-config.json`." Required because Phase 6 changes runtime behavior of an existing workflow.
- [ ] **Plugin-release-checklist** — full pass before Phase 6 merges (the skill carries it).
- [ ] **Claims #8 and #9 re-verified** day before merge against vendor docs; markers updated.

---

## Settling steps for the unverified claims

| Claim | Settling step | Where in plan |
|---|---|---|
| #6 — `copilot-hook-adapter.sh` SessionStart `additionalContext` shape | Already CONFIRMED by Panel A via Read; flip claims-table row. | Phase 0. |
| #7 — Cache TTL / min-cacheable | Re-read `prompt-caching-playbook.md` during Phase 1 SKILL.md authoring. | Phase 0 + Phase 1. |
| #8 — Batch API 50% off | `[verify-at-use — anthropic.com/pricing]` in SKILL.md and eval report. Re-check day before Phase 6 merge. | Phase 0 + Phase 6. |
| #9 — Substrate tier SKUs (2026-05-31) | `[verify-at-use]` marker in SKILL.md tier table. Re-check day before Phase 6 merge. | Phase 0 + Phase 6. |
| #11 — MCP vs WebFetch token ratio | Phase 5 eval fixture measures actual ratio on the PP question. | Phase 5. |
| Best-practice literature (FrugalGPT / RouteLLM / Self-Consistency) | Optional re-run of the deep-researcher probe after spend cap clears. If returned, add as corroborating citation in SKILL.md; if not, omit rather than overstate. | Optional post-Phase 6. |

---

## Substrate-tier mapping (the contract)

| Tier | Claude (verified 2026-05-31, `[verify-at-use]`) | Codex (verified 2026-05-31) | Copilot (verified 2026-05-31, picker-per-chat) |
|---|---|---|---|
| `fast` | Haiku 4.5 — `claude-haiku-4-5-20251001` | GPT-5.5 reasoning=low | Haiku 4.5 (cloud agent fast tier) |
| `balanced` | Sonnet 4.6 — `claude-sonnet-4-6` (adaptive thinking) | GPT-5.5 reasoning=medium/high | `Auto` or Sonnet 4.6 |
| `top` | Opus 4.7/4.8 — `claude-opus-4-7` (escalate sparingly) | GPT-5.5-Pro | Opus 4.6 |

Per-phase defaults (in `templates/run-config.json`):

| Phase | Tier | Reasoning |
|---|---|---|
| scope | balanced | medium |
| search | fast | low |
| fetch | fast | low |
| verify_default | fast | low |
| verify_judgment | balanced | high |
| synthesize | balanced | high |
| synthesize_contested | top | high |

---

## Open questions parked

- **Codex sub-session orchestrator port.** No current Codex consumer urgency. The contract is already substrate-neutral; a Codex orchestrator can consume `run_config` later without contract change.
- **MCP-based per-call model routing on Copilot.** Verified-unsupported today (gap-delta C7).
- **Org-rule documentation for Business/Enterprise Copilot customers.** Consultant-deliverable, not infra.
- **Re-running deep-researcher general-best-practice probe.** Spend cap; nice-to-have, not gating.
- **Application of this pattern to the FORGE pipeline itself.** Deep-research is the first pilot. FORGE adoption is a future PR after the contract settles.
