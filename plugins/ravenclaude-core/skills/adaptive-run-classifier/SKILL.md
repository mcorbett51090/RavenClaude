---
name: adaptive-run-classifier
description: "Substrate-neutral pre-execution classifier contract. A single Haiku call emits a `run_config` JSON envelope that right-sizes cardinality knobs + per-phase model tier + reasoning level for multi-phase agentic workflows (the deep-research loop is the first consumer). Workflows read the envelope; substrate adapters (Claude / Codex / Copilot) map tier labels to SKUs. Carved out behind `.ravenclaude/run-config.json` `enabled: false` so adoption is opt-in and rollback is one line."
last_reviewed: 2026-06-03
confidence: high
---

# Skill: adaptive-run-classifier

## What this is

The **wire contract** between an agentic workflow and the cheap classifier call that tells it how big and how careful to be. The classifier emits one JSON `run_config` per workflow run; the workflow reads it; substrate adapters map the tier labels to SKUs. **Invoke it before any multi-phase loop with cardinality knobs** (deep-research is the first port; FORGE is the obvious second). One forced-tool Haiku call. No agent loop. No retries to parse.

Plan reference: [`docs/plans/2026-06-03-adaptive-run-classifier/plan.md`](../../../../docs/plans/2026-06-03-adaptive-run-classifier/plan.md) §"Substrate-neutral run_config" + Phase 1 + Risk matrix. The skill is the **artifact** that contract; the workflow's adapter is the **consumer**.

## The `run_config` JSON schema

Every field below ships in every run_config. The schema is versioned (RM5 — workflow evolution silently falls back to defaults without this) and substrate-neutral (tier *labels*, not SKUs).

```json
{
  "schema_version": "1",
  "enabled": true,
  "task_class": "research_loop_vendor_docs",
  "knobs": {
    "angle_count": 3,
    "max_fetch": 10,
    "max_verify_claims": 18,
    "verify_policy": {
      "primary_recent": 1,
      "primary_old": 2,
      "secondary": 3,
      "judgment": 3
    }
  },
  "tiers": {
    "scope": "balanced",
    "search": "fast",
    "fetch": "fast",
    "verify_default": "fast",
    "verify_judgment": "balanced",
    "synthesize": "balanced",
    "synthesize_contested": "top"
  },
  "reasoning": {
    "scope": "medium",
    "search": "low",
    "fetch": "low",
    "verify_default": "low",
    "verify_judgment": "high",
    "synthesize": "high",
    "synthesize_contested": "high"
  },
  "batch_verify": false,
  "use_specialized_mcp": true,
  "primary_source_host": "learn.microsoft.com",
  "rationale": "Vendor-docs lookup: most claims will be unanimous primary-recent → 1 vote; reserve 3-vote escalation for the few judgment claims. Prefer Microsoft Docs MCP over open-web fetch."
}
```

See the full schema definition in [`templates/run-config.schema.json`](templates/run-config.schema.json). Field semantics and the substrate tier table follow.

**Field semantics (one-liners):**

- `schema_version` — string; `"1"` today. Adapter logs a warning on mismatch and falls back to defaults (RM5).
- `enabled` — wire-level mirror of the feature flag. The workflow's `loadRunConfig()` snapshots this once per run.
- `task_class` — one of `research_loop_vendor_docs` / `research_loop_contested` / `research_loop_general` (extensible; the classifier picks).
- `knobs` — the four cardinalities that used to be hardcoded. `verify_policy[sourceQuality]` is the upfront per-claim vote count (B's deterministic lookup is the default path; A's escalation-on-`confidence:low` runs on top).
- `tiers.<phase>` — `fast` / `balanced` / `top`. The substrate adapter maps the label to a SKU.
- `reasoning.<phase>` — `low` / `medium` / `high`. Conditionally emitted by the adapter ONLY for `balanced`/`top` tiers (RM6 — see §Constraints).
- `batch_verify` — boolean. **Defaults `false` in MVP**. The schema field exists today; the workflow gate (`batch_verify && verifier_count>=10`) ships in Phase 3 but the default config does not flip it. Phase-7+ follow-up.
- `use_specialized_mcp` + `primary_source_host` — when both set, the workflow's fetch prompt prefers the matching MCP server (e.g. `microsoft_docs_fetch` for `learn.microsoft.com`). Prompt-string change only.
- `rationale` — load-bearing. A human-readable one-sentence justification. This is the auditable trace the rest of the pipeline points back at; the field is **mandatory** and the classifier prompt enforces it.

## Substrate tier table

The single source of truth for `tier label → SKU` mapping. **Mark every SKU `[verify-at-use — 2026-05-31]`** — the underlying lineup re-dates monthly (Claude) / weekly (Codex, Copilot, Grok). Source: [`plugins/ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md`](../../../ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md) (Tier-4 freshness anchor) + [`plugins/claude-app-engineering/knowledge/model-selection-and-2026-capability-map.md`](../../../claude-app-engineering/knowledge/model-selection-and-2026-capability-map.md).

| Tier       | Claude `[verify-at-use — 2026-05-31]`                | Codex `[verify-at-use — 2026-05-31]`        | Copilot `[verify-at-use — 2026-05-31]`         |
| ---------- | ---------------------------------------------------- | ------------------------------------------- | ---------------------------------------------- |
| `fast`     | Haiku 4.5 (`claude-haiku-4-5-20251001`)              | GPT-5.5 reasoning=low                       | Haiku 4.5 (cloud-agent fast tier) / GPT-5.4-mini |
| `balanced` | Sonnet 4.6 (`claude-sonnet-4-6`) — adaptive thinking | GPT-5.5 reasoning=medium/high               | `Auto` or Sonnet 4.6                            |
| `top`      | Opus 4.7 (`claude-opus-4-7`) — escalate sparingly    | GPT-5.5-Pro                                 | Opus 4.6                                        |

**Adapter discipline:** the adapter holds the ONE mapping table. Workflow code never names a SKU directly. SKU rotation happens here; everything downstream stays substrate-neutral.

## Per-phase defaults

Default tier + reasoning per phase. The classifier may override per `task_class`; the adapter applies these when a field is absent.

| Phase                  | Tier     | Reasoning |
| ---------------------- | -------- | --------- |
| `scope`                | balanced | medium    |
| `search`               | fast     | low       |
| `fetch`                | fast     | low       |
| `verify_default`       | fast     | low       |
| `verify_judgment`      | balanced | high      |
| `synthesize`           | balanced | high      |
| `synthesize_contested` | top      | high      |

Empirical baseline (2026-06-03 PP-description run): 22 of 25 verify votes were unanimous, and the cheap path resolved them; 3-vote tax on every claim was the waste. Hence `verify_default: fast/low` with escalation reserved for `synthesize_contested`.

## The classifier prompt

**One forced-tool Messages API call. No agent loop.** Skill = the artifact + prompt; implementation = single Messages API call.

**Layout** (per [`prompt-caching-playbook.md`](../../../claude-app-engineering/knowledge/prompt-caching-playbook.md) — stable above, volatile below):

```
tools (stable — VERDICT_SCHEMA + classify_run tool def)
  └─► system (stable — rubric + tier vocabulary; cache_control IFF block ≥ 4,096 tokens)
       └─► user (volatile — the task description + any priors)
```

**`tool_choice`:** `{"type": "tool", "name": "classify_run"}` — forces the classifier to fill the schema; suppresses retries (house opinion #5 from [`tool-use-and-structured-output.md`](../../../claude-app-engineering/knowledge/tool-use-and-structured-output.md)).

**Model:** `fast` tier (Haiku 4.5 on Claude). Routing-ladder bottom rung.

**Tool definition** — the run_config shape; the full JSON schema lives in [`templates/run-config.schema.json`](templates/run-config.schema.json) (single source of truth).

**System block** (the rubric — keep stable across runs to preserve any cache):

> You classify multi-phase workflow tasks for an agentic system. Emit one `run_config` envelope by calling the `classify_run` tool. Choose `task_class` from the enum; pick `tiers.<phase>` and `reasoning.<phase>` to **right-size**, not to be safe — the cost of `top`/`high` is paid on every call, the advantage shows up only on the hard tail. Use the per-phase defaults unless the task demands otherwise. For verify cardinality: vendor-docs / primary-recent claims usually need **1 vote**; contested / judgment claims need **3**. `batch_verify` stays `false` in MVP. The `rationale` field is mandatory — one sentence naming the load-bearing choice and why; this is the auditable trace the rest of the pipeline points back at.

**User block (volatile):** the task description + any priors (e.g. "the user just asked about Power Platform solution-export behavior; expect 80% of claims to resolve at learn.microsoft.com").

## Caching design

The classifier prompt is intentionally **small**. Per [`prompt-caching-playbook.md`](../../../claude-app-engineering/knowledge/prompt-caching-playbook.md) §"Minimum cacheable tokens":

- **Haiku 4.5 minimum: 4,096 tokens.** Sonnet 4.6 minimum: 1,024 tokens. Below the minimum, a request runs **without** caching even when `cache_control` is set.
- **Do NOT set `cache_control` on the classifier prompt today.** The tools+system block is well below 4,096 tokens (~600-800). Setting `cache_control` writes a cache the next call can't read → pure 1.25× write penalty for nothing.
- **The threshold:** if the system rubric grows past **4,096 tokens** AND a workflow re-invokes the classifier for the same task within 5 minutes (e.g. a forge-pipeline that retries scoping), then `cache_control:{type:"ephemeral"}` on the last tool def + the system block is worth it. Document the threshold in the adapter comment, not the prompt.

**The verify-system-block discipline (RM1)** — this is the *consumer* workflow's caching concern, not the classifier's, but it's the load-bearing cache decision in the pipeline so it lives in this skill's adapter contract:

- Verify-phase system block: layout `tools (VERDICT_SCHEMA) → system [BREAKPOINT] → user (claim+vote)`.
- **`ttl: "1h"`** when expected workflow duration ≥ ~3 minutes (the deep-research baseline was 36 min; 5-min TTL expires mid-run and every post-expiry call pays the 1.25× write tax again). Eat the 2× write penalty on call #1 to keep the cache warm.
- If the verify system block is below the model's minimum, the cache silently doesn't fire — RM1 in the plan. Phase-5 eval reports `cache_read / (cache_read + input)` per phase; if verify-phase hit rate < 0.5, escalate the verify-default tier from `fast` (Haiku 4.5, min 4,096) to `balanced` (Sonnet 4.6, min 1,024).

## The feature flag

**Location:** `.ravenclaude/run-config.json` at the consumer's project root.

**Default shape (rollback target):**

```json
{
  "schema_version": "1",
  "enabled": false,
  "rationale": "default baseline"
}
```

**Semantics:**

- `enabled: false` (default) — `loadRunConfig()` returns the hardcoded baseline matching pre-port behavior. **Byte-identical** to the legacy workflow (this is the regression floor; Gate 51 enforces it).
- `enabled: true` — `loadRunConfig()` invokes the classifier (one Haiku call), persists the returned envelope to `.ravenclaude/runs/run-classifier/<timestamp>.json`, and snapshots the result into the workflow run.
- A consumer can also pre-fill the JSON with a hand-crafted `run_config` (skip the classifier) for deterministic runs / debugging.

**Rollback:** edit `.ravenclaude/run-config.json` → set `enabled: false` → re-run. One line. No version bump, no migration.

## Worked examples

Three task classes, three concrete run_configs, three one-line rationales.

### Example 1 — `research_loop_vendor_docs`

**Task:** "How does Power Platform solution-export handle managed vs unmanaged for a customer-column polymorphism case?"

Use `verify_policy: {primary_recent: 1, primary_old: 2, secondary: 3, judgment: 3}`, `tiers.verify_default: fast`, `use_specialized_mcp: true`, `primary_source_host: learn.microsoft.com`. **Rationale:** "Vendor-docs question: ≥80% of claims will be unanimous primary-recent → 1 vote; prefer Microsoft Docs MCP over open-web fetch."

### Example 2 — `research_loop_contested`

**Task:** "Cube vs Metabase for a 5-tenant SaaS — cost, RLS, embed story."

Use `verify_policy: {primary_recent: 2, primary_old: 3, secondary: 3, judgment: 3}`, `tiers.verify_default: balanced`, `tiers.synthesize: top`. **Rationale:** "Contested comparison: vendor docs disagree with practitioner blogs; pay for Sonnet on verify-default and Opus on synthesis to reconcile sources."

### Example 3 — `research_loop_general`

**Task:** "What are the failure modes of the 2026 EU AI Act for downstream OSS deployers?"

Use `verify_policy: {primary_recent: 2, primary_old: 3, secondary: 3, judgment: 3}`, `tiers.verify_default: fast`, `tiers.synthesize_contested: top`. **Rationale:** "Open-web regulated topic: regulation text + a few authoritative analyses, but no specialized MCP; keep verify-default cheap, escalate contested synthesis to Opus."

## Audit substrate

Every classifier verdict is logged to `.ravenclaude/runs/run-classifier/<UTC-timestamp>.json` (parallel to `.ravenclaude/runs/thing/decisions/`). One file per verdict. `rationale` is mandatory and is the human-readable trace.

Plus a per-claim audit (Phase 3 of the workflow port, RM4): `.ravenclaude/runs/<workflow-run-id>/claim_tier_audit.jsonl`, one line per verify claim: `{claim_idx, initial_tier, votes_fired, escalated_to?, final_verdict}`.

## Constraints + invariants (the protective design)

These are the rails. Violating any of them is a regression — every one is tied to a Risk Matrix row in the plan.

1. **Flag read ONCE per workflow run, snapshotted to audit log (RM3).** `loadRunConfig()` reads `.ravenclaude/run-config.json` exactly once at workflow start, freezes the snapshot into a closure variable for the rest of the run, and writes the snapshot into the per-run audit log. A retry inside the workflow re-uses the snapshot — it does NOT re-read the file. Mid-run flag toggles never mix baseline and adaptive opts.

2. **`thinking` param conditionally emitted ONLY for Sonnet/Opus tiers — never Haiku (RM6).** Haiku 4.5 has **no extended thinking**; passing `thinking:{type:"adaptive"}` to a Haiku request API-errors silently in some paths and noisily in others — either way a regression bug class. The adapter MUST guard the param:

   ```javascript
   function adapterOpts(phase, tierLabel, reasoningLabel) {
     const model = TIER_TO_SKU[tierLabel];                          // single source of truth
     const opts = { model };
     if (tierLabel !== "fast") {                                    // Haiku is fast; no thinking
       opts.thinking = { type: "adaptive" };                        // budget_tokens deprecated on Sonnet 4.6
     }
     // cache_control set by the caller (verify-system-block has its own discipline)
     return opts;
   }
   ```

   Unit test: `adapter.opts("fast", "low")` returns `{ model }` only — **no `thinking` key**. This test ships with the adapter.

3. **Cache TTL `"1h"` on the verify system block when expected workflow duration ≥ ~3 min.** The deep-research baseline runs 36 minutes — the 5-min default TTL expires mid-run and every post-expiry call eats the 1.25× write again. Switch to `"ttl": "1h"` (2× write on call #1, then 0.1× reads for the rest of the hour). For workflows known to finish in under 3 minutes, the 5-min default is correct.

4. **`batch_verify: false` in MVP default — flag in schema but not flipped.** The field exists for forward compatibility. Phase 3 wires the threshold gate (`batch_verify && verifier_count>=10`) but the template config does NOT enable batch. Flipping it on requires either a polling loop or splitting the workflow into two invocations (synthesize consumes verify synchronously today); both are out of MVP scope and become a Phase-7+ follow-up after the synchronous path's savings are measured.

5. **Schema version field on every envelope (RM5).** `schema_version: "1"` is required. Adapter logs a warning and falls back to defaults on mismatch. Classifier emits the current version. Cheap insurance against workflow evolution silently running on stale classifier output.

## Copilot informational-only clarification

The Copilot wiring (Phase 4 of the plan) is **informational-only in MVP**. The existing `plugins/ravenclaude-core/hooks/capability-orientation.sh` SessionStart hook is edited to append a compact one-liner to its `additionalContext` payload WHEN `.ravenclaude/run-config.json` exists and `enabled: true`. The compact one-liner includes the task_class, the chosen tiers, and the scrubbed rationale (≤512 chars).

The Copilot adapter's existing dual-emit ([`copilot-hook-adapter.sh`](../../hooks/copilot-hook-adapter.sh) sessionstart path lines 137-146) carries the appended text without adapter changes. **No new hook file. No per-call Copilot model routing.** The rationale is surfaced so the user (and any Copilot session reading the banner) can see what the classifier chose; the workflow's actual per-phase SKU selection still happens in the Claude adapter. Per-call Copilot model routing is verified-unsupported today and parked.

## Output Contract

This skill emits no runtime artifact of its own — it is a *contract*, consumed by workflows. When the prompt-engineer or an architect critiques an instance of this contract (e.g. a workflow's `run_config` in a PR), the response ends with the cross-plugin Structured Output JSON block per [`structured-output/SKILL.md`](../structured-output/SKILL.md).

## References

- Plan + risk matrix: [`docs/plans/2026-06-03-adaptive-run-classifier/plan.md`](../../../../docs/plans/2026-06-03-adaptive-run-classifier/plan.md) (Phase 1 work-list, RM1/RM3/RM5/RM6, Substrate-tier mapping).
- Claude SKU lineup + capability map (the freshness anchor for Claude tier rows): [`plugins/claude-app-engineering/knowledge/model-selection-and-2026-capability-map.md`](../../../claude-app-engineering/knowledge/model-selection-and-2026-capability-map.md).
- Cross-tool SKU lineup (Codex + Copilot tier rows): [`plugins/ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md`](../../../ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md).
- Cache layout discipline (minimums, TTL, breakpoints): [`plugins/claude-app-engineering/knowledge/prompt-caching-playbook.md`](../../../claude-app-engineering/knowledge/prompt-caching-playbook.md).
- Forced-tool structured output (the `tool_choice` pattern): [`plugins/claude-app-engineering/knowledge/tool-use-and-structured-output.md`](../../../claude-app-engineering/knowledge/tool-use-and-structured-output.md).
- Agent-quality rubric (the bar this skill is scored against): [`plugins/ravenclaude-core/skills/agent-quality-rubric/SKILL.md`](../agent-quality-rubric/SKILL.md).
- Companion skill format: [`plugins/ravenclaude-core/skills/decision-review/SKILL.md`](../decision-review/SKILL.md) (parallel shape: an auditable verdict via a cheap upstream call).
- Structured Output Protocol: [`plugins/ravenclaude-core/skills/structured-output/SKILL.md`](../structured-output/SKILL.md).
