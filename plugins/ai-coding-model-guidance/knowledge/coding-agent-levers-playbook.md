# Coding-agent levers playbook

**Plugin:** `ai-coding-model-guidance`  
**Role:** Authoritative deep layer under the quota HARD GATE (`ai-coding-quota-exhaustion-decision-tree.md`). Use this when you need *how* to stretch quality under quota or right-size spend — not when you only need the hard-gate order.  
**Retrieval date:** 2026-09-04 (America/New_York). Volatile params/prices/limits: **`[verify-at-use]`**.  
**Sources:** lever-research angles 00–05 (live CloudAgent `models` catalog + vendor docs + cited studies). Do not invent SKUs or params beyond the catalog snapshot and cited sources.

---

## 1. Purpose / when

Use this playbook to:

1. **Stretch quality under quota** — keep shipping on a soft-capped surface by dialing effort/reasoning/fast/scope/context before hopping vendor.
2. **Right-size spend before SKU prestige** — raise or lower dials, tighten scope, and decompose *before* paying for a frontier SKU.

Do **not** use this file as a substitute for the HARD GATE. The quota tree remains the mandatory classify → record → lever → failover sequence. This playbook is the encyclopedia + interaction rules those lever steps expand into.

**Bot rule of thumb:** if the surface is still usable, exhaust same-surface levers here first; if the surface is hard-capped, jump to missing-lever failover / surface hop (sections 5–6) without inventing params.

---

## 2. Apply order (default)

```
1. Classify limit
   context overflow | short rate limit | soft quota | hard weekly/monthly/spend
2. Record headroom
   surface, model, error, reset time, task state, remaining headroom
3. Levers on same surface (usable headroom)
   a. Scope / success criteria / file envelope
   b. Decompose (cheap triage → mid/frontier implement)
   c. Stretch dials if soft quota: lower effort/thinking/reasoning + fast=true; avoid 1m context
   d. Quality gap only: raise reasoning/effort on SAME model (not SKU hop)
   e. Shrink/curate context; compact/drop history; strip attachments
   f. Cap turns/budget/tools; prefer 1 agent + dial over N-agent fan-out
4. Surface hop (same vendor, different meter)
5. Vendor / tier hop (closed-world lineup only; same tier first, then lower tier that fits leaf)
6. Wait for reset (if deadline allows)
7. Escalate CoS → Matthew for plan upgrade only
```

Never silent-fail. Never identical-retry an exhausted surface with dials unchanged. Never invent params — re-fetch CloudAgent `models` / surface docs `[verify-at-use]`.

---

## 3. Lever encyclopedia

Param vocabulary observed in live Cursor CloudAgent catalog (2026-09-04) `[verify-at-use]`:

| Param id | Typical values | Families |
|---|---|---|
| `effort` | low, medium, high, xhigh, max (subset varies) | Claude Opus/Sonnet/Fable (newer), Grok 4.5/4.6, Gemini 3.7 Flash |
| `thinking` | false, true | Most Claude |
| `reasoning` | none/low/medium/high/xhigh/max or extra-high | GPT-5.x, Codex 5.3, Kimi K3, GLM 5.2 |
| `reasoning_effort` | low, medium, high | Gemini 3.8 Flash |
| `context` | 200k, 272k, 300k, 1m | Claude; GPT |
| `fast` | false, true | Grok, Composer, many Claude Opus, many GPT |

Hard catalog restrictions `[verify-at-use]`:

- Claude Opus 5: `thinking=false` **cannot** combine with `effort=xhigh` or `effort=max`.
- GPT 5.x Sol/Terra/Luna/5.5/5.4: `fast=true` **cannot** combine with `context=1m`.
- Older Claude (Opus 4.5, Haiku 4.5, Sonnet 4/4.5): often **thinking only**.
- Gemini 3.1 Pro / some Flash: **no params**.
- Composer 2.5: **fast only**.
- Codex 5.3: **reasoning + fast** (no thinking/effort/context).

---

### 3.1 Effort / thinking / fast

**Best use**

- Stretch soft quota: `effort=low`, `thinking=false` (when allowed), `fast=true`.
- Quality bump without SKU hop: `thinking=true` + raise `effort` on same Claude model after scope OK.
- Latency path: `fast=true` + lower effort; treat fast as orthogonal to depth where both exist.
- Claude Code: `/effort`, `--effort`, `effortLevel`, env `CLAUDE_CODE_EFFORT_LEVEL` (env overrides CLI/`/effort`).

**Token effect**

- Higher effort/thinking inflates hidden reasoning/thinking tokens, generally billed like **output** (OpenAI explicit; Anthropic thinking toward `max_tokens`; xAI billed in consumption; Copilot AI credits rise).
- Anthropic: effort is a **behavioral signal, not a hard token budget**; lower effort → fewer/tersier tool calls; changing **top-level** effort between turns can **invalidate prompt-cache** prefixes.
- Cursor secondary blogs claim ~2.5× credit for ~1.5× speed on fast — treat as `[verify-at-use]`.

**Quality effect**

- Higher → deeper planning, better tool use, better ambiguity recovery (vendor-stated).
- Diminishing returns: OpenAI/Anthropic warn against always-max; Anthropic notes `max` can **hurt** some structured tasks via overthinking.
- Adaptive thinking already spends less on easy asks inside a level — "always max" buys less than expected.

**Per-model / surface deltas `[verify-at-use]`**

| Surface / family | Dial | Notes |
|---|---|---|
| Claude newer (Opus/Sonnet/Fable) | `thinking` + `effort` (+ often `fast`, `context`) | Default effort often `high`; Haiku 4.5: effort **not supported** (extended thinking / budget only) |
| Claude Opus 5 | thinking gates xhigh/max | `thinking=false` + xhigh/max = **invalid** |
| Claude Code Pro/Max | product effort | Effort is a documented usage driver; lowering stretches session/weekly bars |
| Cursor Cloud Agents | `model.params` from catalog | Discover via `GET /v1/models` / CloudAgent `models`; do not hardcode enums |
| Grok 4.5/4.6 | `effort` + `fast` | Reasoning **cannot be disabled**; default **high**; pin low/medium on trivial leaves |
| Composer 2.5 | `fast` only | No effort/thinking |

**Missing-lever failover**

- No effort on current model → pick same-surface model that exposes effort/reasoning; else same-vendor other surface; else other vendor same tier (section 5).
- Need "thinking off" on Grok → impossible; use `effort=low` + shorter loops.

**Anti-patterns**

- Submit Opus 5 `thinking=false` × `effort=xhigh|max`.
- Default `thinking=true` + `effort=xhigh|max` + frontier SKU + wide scope (spend explosion E1).
- Thrash top-level effort mid-session (cache bust on Claude).
- Invent effort enums not in live catalog.

---

### 3.2 Reasoning dial

**Best use**

- Quality gap on GPT/Codex/Kimi/GLM: raise `reasoning` (or Codex `model_reasoning_effort` / `--reasoning`) on **same model** before bigger SKU.
- Soft quota stretch: `reasoning=low|none` + `fast=true` when available.
- OpenAI guidance (paraphrased): `none` latency-critical; `low` tool/execution coding; `medium` default-ish agentic; `high` hard debug/planning; `xhigh`/`max` only with eval evidence.
- Copilot: Thinking Effort / reasoning level UI; raise only for harder tasks; credits scale with thinking tokens.

**Token effect**

- Reasoning tokens bill as **output** (OpenAI); occupy context; reserve ≥~25k headroom for reasoning+output when experimenting `[verify-at-use]`.
- Hitting `max_output_tokens` mid-reasoning → incomplete with cost spent and little visible text.
- GPT-5.6 `reasoning.mode` `pro` is orthogonal to effort and adds latency/tokens/cost `[verify-at-use]`.

**Quality effect**

- Same label ≠ equal quality across nano vs Astra / Haiku vs Opus — bind per catalog entry.
- GPT-6 Astra **rejects** `reasoning.effort=none` (HTTP 400).

**Per-model / surface deltas `[verify-at-use]`**

| Surface | Param | Notes |
|---|---|---|
| GPT-5.x / Astra | `reasoning` / `reasoning.effort` | Model-specific subset; Astra no `none` |
| Codex 5.3 / Codex CLI | `reasoning` + `fast`; CLI `model_reasoning_effort` minimal…xhigh | No thinking/effort/context in CloudAgent snapshot |
| Copilot agent | Thinking Effort Low–Max | Post-2026-06-01: AI Credits; **no** silent cheaper-model fallback |
| Gemini 3.8 Flash | `reasoning_effort` | Name differs from GPT |
| Claude | use `effort` + thinking — not GPT `reasoning` | Do not equate labels 1:1 |

**Missing-lever failover**

- No reasoning dial → Claude `effort`/`thinking`, or Grok `effort`, or switch model that exposes reasoning (section 5 recipe R1/R4).

**Anti-patterns**

- Jump frontier SKU before raising reasoning on current model.
- Leave max reasoning on forever for easy tasks (right-size).
- Equate `thinking=true` ≡ `reasoning=high` ≡ `effort=high` across vendors.

---

### 3.3 Scope / decompose

**Best use**

- Always before dial/SKU change: goal + allowed/forbidden paths + acceptance tests + **executable stop rule**.
- Decompose pattern: (1) cheap/low-effort triage → scoped ticket; (2) mid/raised-effort implement on those files; (3) frontier + high/xhigh only if mid fails **same** ticket; (4) optional mid-tier review with fixed checklist (no certainty loops).
- Prefer bounded-efficiency prompts ("failing test + likely files; inspect more only when evidence requires; smallest change; stop when criteria pass").

**Token effect**

- Span (observational, May–Jul 2026): +1 prompt-clarity point ↔ ~**27.2%** lower cost/merged AI line; example 50-line trajectory $6.90→$4.45 `[verify-at-use]`.
- PointFive (preregistered): "compare several approaches" → **2.4–7.4×** reasoning, **no** success gain; verbose restatement ≈ **1.0×**; max certainty/re-verify → ~**18×** cost, ~2.5× tool calls, flat success `[verify-at-use]`.
- EvoRoute-style per-step routing: up to ~**80%** cost / ~**70%** latency cuts on agentic benches `[verify-at-use]`; early cheap mistakes compound (BAAR).

**Quality effect**

- Ambiguous scope: success drop (~83% in PointFive) + reasoning ↑ (~1.44×).
- Scoped ticket makes effort/reasoning dials *work*; unscoped high effort → expensive bad answers.

**Per-model / surface deltas `[verify-at-use]`**

- Universal work-design lever — applies on every surface.
- Claude Agent SDK: subagents start fresh; only summary returns to parent; use `effort=low` for file-list/grep subagents; cap `max_turns` / `max_budget_usd`.
- Heavy harnesses amplify prompt waste (PointFive: Claude Code vs lighter harness **5–30×** cost/success on same tasks `[verify-at-use]`).

**Missing-lever failover**

- Scope is never "missing" — if UI has no scope fields, encode envelope in the prompt / CLAUDE.md / ticket.

**Anti-patterns**

- "Be absolutely certain / re-verify everything" without stop rule.
- "Compare N approaches" on ordinary patches.
- Escalate to frontier **without** tightening the failed ticket.
- Max effort on every decompose shard (E6).

---

### 3.4 Context / window

**Best use**

- Default productive band: curated ≤~200k for most agent coding.
- Prefer reshape/summarize/RAG/edge-placed critical instructions over filling 1m.
- OpenAI: stay under **272k** surcharge boundary when evals allow `[verify-at-use]`.
- Use 1m only for whole-artifact synthesis / long-horizon state / cache-anchored static corpora — never "just in case" under quota pressure.
- Compaction: Anthropic server compaction default trigger ~150k (min 50k); pin durable DoD in CLAUDE.md / custom compaction `instructions`; subagent isolation to avoid parent bloat.

**Token effect**

- Bigger window bills every token processed each turn even when $/MTok flat (Anthropic 1M at standard rates still costly if filled) `[verify-at-use]`.
- OpenAI inputs **>272k** may trigger **2×** input/cache and **1.5×** output for the **full** request `[verify-at-use]`.
- GPT: `fast=true` incompatible with `context=1m` on listed 5.x SKUs.

**Quality effect**

- Lost-in-the-middle U-curve (Liu et al.); production 1M probes show sharp mid-window recall drops `[verify-at-use]`.
- Plausible misdirection hurts more than irrelevant noise (PointFive: wrong architectural hint **2.61×** reasoning).

**Per-model / surface deltas `[verify-at-use]`**

| Family | Context dial | Notes |
|---|---|---|
| Claude (catalog) | 200k / 300k / 1m | Richest window set |
| GPT 5.x | 272k / 1m | No fast+1m on Sol/Terra/Luna/5.5/5.4 |
| Grok / Composer / Codex 5.3 / many Gemini | **N/A** in snapshot | Reshape first; hop to Claude/GPT for window dial |
| Cursor Cloud Agents | selectable context | Larger window ↑ API $ |

**Missing-lever failover**

- No context dial → summarize/drop history/sparse paths first; then same-surface model with `context`; on GPT need 1m → `fast=false`.

**Anti-patterns**

- `context=1m` under soft quota "just in case" (E2).
- `fast=true` + `context=1m` on forbidden GPT SKUs.
- Blind whole-monorepo dump into any window.

---

### 3.5 Sampling (temperature / top_p / penalties)

**Best use**

- Legacy **non-reasoning** chat: low temperature (~0–0.2) for deterministic coding; alter temperature **or** top_p, not both.
- Frontier reasoning / newest Claude: **do not** use sampling — steer with effort/reasoning + prompts.

**Token effect**

- Sampling does not change input tokens directly; high temp → more invalid JSON/tool-arg retries → indirect spend.
- Sending non-default sampling on Claude 4.7+ / Sonnet 5 / Opus 5 → HTTP **400** (wasted call).

**Quality effect**

- Low temp: stable code; high temp: exploration + flake. Penalties are weak coding levers vs clear specs.

**Per-model / surface deltas `[verify-at-use]`**

| Surface | Available? |
|---|---|
| OpenAI non-reasoning Chat Completions | Yes |
| OpenAI reasoning / latest-model guidance | **Remove** sampling |
| Anthropic ≤4.6 | Yes (prefer omit both temp & top_p) |
| Anthropic 4.7+ / Sonnet 5 / Opus 5 | **Rejected if non-default** |
| Cursor CloudAgent catalog | Not free-form temperature — effort/reasoning/fast only |
| Claude Code | Effort levels, not classic temperature |

**Missing-lever failover**

- N/A sampling → dial effort/reasoning/thinking/fast; tighten prompt; only hop to a non-reasoning SKU with temperature if exploration is the goal (rare for production coding).

**Anti-patterns**

- Sending temperature on Claude 4.7+/Opus 5 / OpenAI reasoning SKUs.
- Treating sampling as a quota dial on frontier coding agents.

---

### 3.6 max_tokens / max output

**Best use**

- Cap just above expected answer **plus** thinking headroom.
- Claude adaptive thinking: if truncated at high effort → raise `max_tokens` **or** lower effort.
- OpenAI: oversized `max_tokens`/`max_output_tokens` can inflate TPM reservation — keep close to expected size.
- Truncation policy: prose may continue; **tool_use / JSON → full retry** with higher cap (never stitch).

**Token effect**

- Unused cap usually not billed, but truncation→retry doubles spend.
- Claude: thinking counts toward `max_tokens`; at xhigh/max start ~64k and tune `[verify-at-use]`.
- Claude Code: raising `CLAUDE_CODE_MAX_OUTPUT_TOKENS` **shrinks** room before auto-compact.

**Quality effect**

- Too low: half-answers, broken tool_use. Too high: little quality gain; may encourage verbosity at high effort.

**Per-model / surface deltas `[verify-at-use]`**

| Surface | Param |
|---|---|
| Anthropic Messages | `max_tokens` (required; includes thinking) |
| OpenAI Chat | `max_completion_tokens` / legacy `max_tokens` |
| OpenAI Responses | `max_output_tokens` |
| Claude Sonnet 5 | up to ~128k max output `[verify-at-use]` |
| Cursor Cloud Agents | no free-form max_tokens in launch params — bound via spend + prompt |

**Missing-lever failover**

- N/A explicit max_output → `max_turns` / spend limits / stepwise deliverables / strip attachments.

**Anti-patterns**

- Stitching incomplete tool_use JSON.
- Experimenting on reasoning models without ≥~25k output headroom.

---

### 3.7 Tools / concurrency

**Best use**

- Parallel tools for **independent** reads; disable for side-effecting writes/deploys.
- Keep tool schema lists small and stable (cache-friendly); allowlist tools.
- Cap local concurrency when fan-out overwhelms I/O (`max_function_tool_concurrency`, Claude Code `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` default 10).

**Token effect**

- Each parallel tool_result re-enters next-turn context → input growth ~N×.
- Tool schemas billed as input (OpenAI).
- OpenAI: `parallel_tool_calls: false`; Anthropic: `tool_choice.disable_parallel_tool_use: true`.

**Quality effect**

- Parallel independent reads: better + faster. Parallel dependent writes: races / confused state.

**Per-model / surface deltas `[verify-at-use]`**

| Surface | Control |
|---|---|
| OpenAI | `parallel_tool_calls` + `tool_choice` |
| Anthropic | `disable_parallel_tool_use` inside `tool_choice` |
| Claude Code | read-only concurrent; mutating sequential; env concurrency caps |
| Cursor Cloud Agents | MCP supported; no documented parallel_tool_calls dial → prompt + MCP design |

**Missing-lever failover**

- N/A parallel dial → prompt "one tool at a time"; reduce MCP surface; sequential subagents.

**Anti-patterns**

- Parallel tool spam under soft quota.
- Huge always-on tool lists that bust cache and bloat every turn.

---

### 3.8 Parallel agents

**Best use**

- Fan-out N agents only for **independent** workstreams (disjoint files/PRs).
- Prefer **1 agent + dial** when work is serial, quota is soft, or the gap is "needs more reasoning" not "needs more workers".
- Cursor Cloud Agents: parallel allowed; billed at API rates; spend limit binds.
- Claude SDK: subagent spend counts toward `max_budget_usd`.

**Token effect**

- ~Linear N× token burn (prefix may cache; each agent still generates).
- Ensemble "best of N" = N× cost — last resort under quota.

**Quality effect**

- Independent: wall-clock win. Dependent: merge conflicts + wasted tokens.

**Per-model / surface deltas `[verify-at-use]`**

| Surface | Bound |
|---|---|
| Cursor Cloud Agents | Spend limit; plan concurrency (forum ~8 on Pro — `[verify-at-use]`) |
| Claude Agent SDK | `max_budget_usd`, `max_turns`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (default 20) |
| OpenAI Agents SDK | handoffs + `max_turns` |

**Missing-lever failover**

- N/A multi-agent → sequential milestones; raise effort; read-only explore subagent then implementer; Batch API for offline fan-out.

**Anti-patterns**

- N clones of a failing job.
- Max reasoning on every shard after decompose.

---

### 3.9 Caching

**Best use**

- Front-load stable system/tools/repo maps; append-only history; byte-stable tool schemas.
- Keep model + effort/reasoning + tools **sticky** across turns; steer with per-message text (Claude) / `configuration_update` that preserves cache (OpenAI where supported).
- OpenAI: `prompt_cache_key`, GPT-5.6+ breakpoints; Claude: `cache_control` ephemeral.

**Token effect**

- OpenAI GPT-5.6+: cache read up to **0.1×**, writes ~**1.25×**; break-even after ~2 full reuses `[verify-at-use]`.
- Claude: reads ~**0.1×**; top-level effort change → cache miss (`cache_read_input_tokens: 0`).
- Cached tokens still count toward rate limits (OpenAI).

**Quality effect**

- Neutral if prefix identical; regressions come from accidental cache-bust (timestamps in system prompt, reordered tools, effort thrash).

**Per-model / surface deltas `[verify-at-use]`**

| Surface | Caching |
|---|---|
| OpenAI | Automatic + explicit breakpoints |
| Anthropic | Explicit/automatic `cache_control` |
| Claude Code | Automatic for stable system/tools/CLAUDE.md |
| Cursor Cloud Agents | Opaque provider-side — keep prompts stable |

**Missing-lever failover**

- N/A explicit cache_control → still structure cache-friendly prefixes; avoid mid-session model/effort/tool-schema thrash.

**Anti-patterns**

- Flipping effort every turn "to save tokens" (often costs more via cache miss).
- Reordering tool defs each request.

---

### 3.10 Attachments (multimodal)

**Best use**

- Attach only when pixels/layout matter (UI bugs, diagrams). Prefer text diffs/logs for code.
- Downsample; use Files API `file_id` (Claude) to avoid resending base64 every turn.
- Strip attachments before SKU hop / cheaper model once a text summary exists.

**Token effect**

- Claude visual tokens ≈ `⌈w/28⌉ × ⌈h/28⌉`; high-res up to ~**3×** vs standard `[verify-at-use]`.
- Large PDFs can be ~125k-token class `[verify-at-use]`.
- Gemini `media_resolution` sets fixed per-media budgets.

**Quality effect**

- Necessary for visual bugs; otherwise context crowding hurts coding focus.

**Per-model / surface deltas `[verify-at-use]`**

- Claude/OpenAI/Gemini vision paths differ; Cursor Cloud Agents via artifacts/screenshots/computer-use.
- Text-only cheap SKUs may still tokenize or reject large images — do not assume free ignore.

**Missing-lever failover**

- N/A vision → OCR/summarize locally; paste text; strip image before hop.

**Anti-patterns**

- Carrying multi-MB screenshots into every turn and every SKU hop.
- "Attach the whole PDF just in case" under soft quota.

---

### 3.11 Stop / step caps

**Best use**

- Always set `max_turns` and budget where available on production agents.
- Pair with executable success criteria so the model stops early.
- Caps are **circuit breakers**; prefer tight scope + stop rule first, then resume narrower if capped.

**Token effect**

- Prevents unbounded tool/verification loops (dominant agent spend mode).
- Hitting cap early + resume < runaway loop.

**Quality effect**

- Too low: `error_max_turns` before fix. Too high: waffle / repeated test cycles.

**Per-model / surface deltas `[verify-at-use]`**

| Surface | Levers |
|---|---|
| Claude Agent SDK / Claude Code | `max_turns`, `max_budget_usd`, output/bash/file-read caps, web-search session cap |
| OpenAI Agents SDK | `max_turns` → `MaxTurnsExceeded` |
| Anthropic raw Messages | `max_tokens`, `stop_sequences`; loop app-owned |
| Cursor Cloud Agents | Spend limit; cancel/archive; no public max_turns in launch API — bound via prompt + spend |

**Missing-lever failover**

- N/A max_turns → wall-clock cancel; spend limit; "stop after N tool rounds"; phased prompts.

**Anti-patterns**

- Unlimited turns + high effort + noisy 1m context (spend explosion).
- Blind identical retry after `error_max_turns` without narrowing scope.

---

### 3.12 Batch / async

**Best use**

- Evals, nightly summarization, embedding corpora, offline codegen where ≤24h latency OK.
- Move load off sync RPM/TPM pools.

**Token / meter effect**

| Provider | Discount | Notes |
|---|---|---|
| OpenAI Batch | **50%** vs sync `[verify-at-use]` | Separate rate-limit pool; ≤50k req / 200 MB; 24h window |
| Anthropic Message Batches | **50%** input+output `[verify-at-use]` | Often <1h; stacks with caching per pricing notes |
| Cursor Cloud Agents / Claude Code interactive | **No** batch 50% | Full API / session rates |

**Quality effect**

- Same model quality; unsuitable for interactive coding loops.

**Per-model / surface deltas `[verify-at-use]`**

- Interactive IDE/cloud-agent products: schedule offline work to vendor Batch APIs, or overnight Cloud Agent with spend limit (still full rates).

**Missing-lever failover**

- N/A Batch on Cursor/Claude Code → vendor Batch via API for offline; or overnight agent with hard spend cap.

**Anti-patterns**

- Expecting 50% batch pricing on interactive Cloud Agent runs.
- Putting an active debugging loop on a 24h batch window.

---

### 3.13 Bonus: repo / worktree scope & smart retry

Not separate Architect subsections, but high-ROI secondary levers from angle 05:

- **Repo scope:** start in package subdirectory; deny Read on `dist/`/`build/`/vendor; `worktree.sparsePaths`; `.cursorignore`; LSP over Grep thrash; explore in read-only subagent.
- **Smart retry:** honor `Retry-After` + exponential backoff+jitter on 429; **never** blind-retry billing/quota; unsuccessful retries still count toward RPM; truncation → branch by prose continue vs structured full retry.

---

## 4. Interaction matrix

Legend: help = prefer; hurt = avoid as default.

### Pairs that help

| Pair | Why | Bot action |
|---|---|---|
| Tight scope × raise effort/reasoning | Dial works only on bounded asks | Scope first, then raise |
| Decompose × cheap triage tier | Stretch quota; right-size | Frontier only on failing leaf |
| `thinking=true` × `effort=low` | Cheap quality bump | Easy tasks needing some deliberation |
| `fast=true` × non-1m context | Speed + stretch | Soft quota / latency path |
| `reasoning=low\|none` × `fast=true` | GPT/Codex stretch | Soft quota |
| Compaction × CLAUDE.md-pinned DoD | Retain stop rules after summarize | Long agentic loops |
| Sticky effort × prompt cache | Preserve 0.1× reads | Steer with message text, not effort thrash |
| 1 agent × raise dial | Beats N-fan-out under soft quota | When gap is depth not parallelism |
| Same-vendor surface hop × remapped dial | Different meter, keep intent | Claude Code ↔ Cursor cloud Claude |

### Pairs that hurt (spend-explosion / invalid)

| # | Combo | Why | Catalog note |
|---|---|---|---|
| E1 | `thinking=true` + `effort=xhigh\|max` + frontier Claude + wide scope | Max dials × prestige × sprawl | Opus 5: max effort implies thinking on |
| E2 | `context=1m` just-in-case under quota | Window cost without proven need | Prefer 300k/272k; reshape first |
| E3 | `fast=false` + `context=1m` + high reasoning/effort + undecomposed job | Large window × deep reasoning × monolith | Split; shrink window |
| E4 | Bigger SKU while dials default + prompt unscoped | Pays SKU premium for prompt bug | Scope → dial → SKU |
| E5 | Identical retries on exhausted surface | Wastes headroom / fails closed | Record limit; lever or failover |
| E6 | Max reasoning on every decompose shard | Decomposition without right-sizing | Low dial for triage shards |
| X1 | Opus 5 `thinking=false` × `effort=xhigh\|max` | **Invalid** | Enable thinking or drop effort ≤ high |
| X2 | GPT 5.x `fast=true` × `context=1m` | **Invalid** | Drop fast or drop 1m |
| H1 | High effort × huge noisy context × uncapped turns | Multiplicative spend explosion | Cap turns; curate context; lower dial |
| H2 | High dial × "compare approaches" × "be certain" | Token-borne + tool-borne waste stacked | Executable stop rule |
| H3 | Effort thrash × prompt cache | Cache invalidation | Keep sticky |

### Stretch-quota combos (prefer when quality bar still met)

| # | Combo | When |
|---|---|---|
| S1 | `effort=low` + `thinking=false` (+ `fast=true`) | Soft quota; Claude new / routine |
| S2 | `reasoning=low\|none` + `fast=true` | Soft quota GPT/Codex |
| S3 | `effort=low` + `fast=true` | Grok stretch |
| S4 | Non-1m context + summarize / drop history | Context pressure |
| S5 | Tighten scope + same dial | Sprawl burn |
| S6 | Decompose: cheap triage → dial/SKU only on hard leaf | Large agentic work |
| S7 | Composer: `fast=true` only | Sole dial |
| S8 | Same vendor other surface before other vendor | Hard cap on one meter |

---

## 5. Missing-lever failover table

**Rule:** do not invent params. Intent → same-surface substitute → escalate A→F.

### Intent → substitute (CloudAgent vocabulary)

| Intent | If current has dial | If missing — same-surface substitute | If still missing |
|---|---|---|---|
| More deliberation | Claude: `thinking=true` + raise `effort`; GPT/Codex: raise `reasoning`; Grok: raise `effort`; Gemini 3.8: `reasoning_effort`; Gemini 3.7: `effort` | Other model on same surface that exposes dial (leave Composer/bare Gemini) | Escalate A→F |
| Stretch quota | `effort=low`, `thinking=false`, `reasoning=low\|none`, `fast=true`, non-1m context | Use whatever subset exists (Composer: `fast` only; older Claude: `thinking=false`; bare Gemini: change model) | Escalate |
| Bigger working set | Claude/GPT `context=1m` (GPT: not with fast) | Switch to catalog model listing `context` | Reshape first; then escalate |
| Speed over depth | `fast=true` + lower effort/reasoning | Composer `fast=true`; else lower dial or faster SKU | Escalate |
| Quality bump without SKU hop | Raise reasoning/effort same model after scope | If no dial: scope/decompose, then same-tier model with dial | Escalate |

### Escalate path (stop at first usable)

```
A. Same surface, other model that has the dial (prefer same tier)
B. Same vendor, other surface (different meter / CLI flag)
C. Other vendor, same tier (closed-world lineup only)
D. Lower-cost tier that still fits the task leaf
E. Wait for reset (record time; no silent retry)
F. Escalate CoS → Matthew for plan upgrade only
```

### Cross-surface remap cheat-sheet

| If missing… | Do this instead |
|---|---|
| Claude `thinking` / `budget_tokens` on newest models | Adaptive thinking + `output_config.effort` |
| Cursor `thinking` param | Thinking-capable model ID from catalog + effort if present |
| Codex Claude-style effort | `model_reasoning_effort` minimal\|low\|medium\|high\|xhigh |
| Grok "turn thinking off" | Impossible on 4.5/4.6 — `effort=low` + shorter loops |
| Copilot PRU fallback | Removed under AI Credits (2026-06-01) — cheaper model / lower thinking **before** hard stop, or budget/wait |
| Context dial on Grok/Codex/Composer | Reshape; hop to Claude/GPT with context; GPT 1m ⇒ `fast=false` |
| Sampling on frontier | Effort/reasoning + prompts |
| Batch 50% on Cursor/Claude Code | Vendor Batch API offline, or overnight agent at full rates |
| max_turns on Cursor Cloud launch | Spend limit + phased prompts + cancel |

### Family cheat-sheet (snapshot `[verify-at-use]`)

| Family | Exposed | Missing vs full vocab |
|---|---|---|
| Claude newer Opus/Sonnet/Fable | thinking, effort, often context, often fast | — richest |
| Older Claude 4.5-class | often thinking only | effort, fast, context |
| GPT 5.x listed | reasoning, context, fast | thinking, effort (use reasoning) |
| Codex 5.3 | reasoning + fast | thinking, effort, context |
| Grok 4.5/4.6 | effort, fast | thinking, reasoning, context |
| Gemini 3.8 Flash | reasoning_effort | others |
| Gemini 3.7 Flash | effort | — |
| Gemini 3.1 Pro / some Flash | **none** | all |
| Composer 2.5 | fast only | all others |

---

## 6. Worked examples

### 6.1 Claude Code weekly soft (Pro/Max session+weekly still has headroom)

**Situation:** Usage bar yellow; large refactor still needed; quality bar must hold.

1. Classify: soft weekly/session (not hard zero).
2. Record: `/usage` or Settings → Usage; note Opus-only vs all-models bars; reset time.
3. Same-surface levers:
   - Tighten file envelope + stop rule (tests once).
   - Decompose: Haiku/Sonnet/low-effort triage → scoped ticket; implement on Sonnet/`effort=medium|high` not Opus/`max`.
   - Stretch: `effort=low` / thinking off on scout subagents; avoid 1m; keep effort sticky for cache.
   - Cap `max_turns` / `max_budget_usd`.
4. If weekly still critical: **B** hop → Cursor cloud Claude (API $ + spend limit) or Codex if that pool has headroom — remap dials (Cursor `model.params` / Codex reasoning).
5. Wait only if delivery > reset; else escalate plan (Max 5x→20x) via CoS/Matthew after 2–3 tuned cycles.

**Cite:** Anthropic Max plan + usage-limit best practices; effort affects usage; angle 03 hop notes.

### 6.2 Cursor spend (Cloud Agent / Other Models on-demand)

**Situation:** Approaching spend limit mid-PR; cloud Claude/GPT run.

1. Classify: hard/soft spend cap.
2. Record: spend limit, model, context size, remaining headroom (~$2 start-headroom folklore is forum-only — confirm dashboard `[verify-at-use]`).
3. Levers before raising limit:
   - Drop `context=1m` → 300k/272k; reshape.
   - `fast=true` + lower effort/reasoning if quality OK (respect GPT fast×1m ban).
   - Prefer Composer/Grok **Cursor Models** pool for routine shards; Other Models only for hard leaf.
   - 1 agent + dial > N parallel agents.
   - Strip screenshots; pin cache-stable prefix.
4. Failover: raise spend limit only if leaf must finish; else same-vendor Claude Code if Max weekly remains; else wait cycle.
5. Never spawn parallel clones of a spend-aborted job.

**Cite:** Cursor Cloud Agents + Models & Pricing docs; angles 00/03/05.

### 6.3 Codex quality-fail (output wrong, pool not exhausted)

**Situation:** Default Codex model at default reasoning fails multi-file debug; budget OK.

1. Classify: quality gap (not quota).
2. Scope check first — if sprawl, tighten; do not raise dial on unscoped ask.
3. Raise `model_reasoning_effort` / CloudAgent `reasoning` one rung (e.g. medium→high); keep `fast=false` for depth.
4. Re-test same scoped ticket. Accept if tests pass.
5. Only if dial at max (xhigh where supported) and still failing: document steps → bigger SKU or other vendor same tier (Claude/Grok) via closed-world tree.
6. If context overflows: Codex 5.3 has no context dial in snapshot → reshape or hop to GPT/Claude with context.

**Cite:** OpenAI reasoning guide; best-practice reasoning-before-upgrade; missing-lever R4.

### 6.4 Forge under one path capped (fact-check / dual-path)

**Situation:** One forge path (e.g. Claude Code weekly hard-zero) blocked; other path (Cursor/Codex/Grok) available.

1. Classify: hard cap on path A.
2. **Do not** silent-skip the whole forge — run path B; note the gap in the deliverable.
3. Remap intent on B (effort↔reasoning↔fast); smoke-eval one representative task before mid-flight hop.
4. On B: right-size (Grok pin `effort=low|medium` — default high always-on); avoid E1–E6.
5. Record: what A would have used, what B used, reset time for A, residual risk from single-path coverage.
6. Escalate plan upgrade only if both paths miss quality bar under deadline.

**Cite:** SKILL Matthew house defaults; angle 03 closed-world pitfalls; HARD GATE anti-patterns.

---

## 7. Dated volatility box

| Field | Value |
|---|---|
| **Retrieval date** | 2026-09-04 (America/New_York / EDT) |
| **Live catalog source** | Cursor CloudAgent action `models` → `00-live-cloud-agent-params.md` |
| **Research angles** | 01 effort/thinking · 02 scope/context · 03 surface/vendor · 04 interaction + missing-lever · 05 secondary levers |
| **Confidence** | Catalog hard restrictions **5/5**; methodology ladders **5/5**; absolute $ multipliers & cross-vendor quality equivalence **3–4/5** (directional; re-measure on your telemetry) |
| **Must re-verify before quoting** | Param enums per model; prices $/MTok; 272k surcharge; batch 50% rows; Claude/Codex weekly bucket internals; Copilot credit tables; Cursor concurrent-agent plan caps; Max Mode legacy vs usage-based context select |

**`[verify-at-use]` rider:** Re-fetch CloudAgent `models` / vendor pricing & quota docs before naming a param set, price, reset clock, or plan limit to a user. Catalog and meters churn. Prefer in-product meters (`/usage`, Settings → Usage, spend dashboards) over guessed token counts inside weekly buckets.

**Hard gate reminder:** This playbook deepens levers; it does not replace `ai-coding-quota-exhaustion-decision-tree.md`. Classify → record → levers → failover → wait → CoS/Matthew remains mandatory.

---

## Bot checklist (copy/paste)

```
[ ] Limit classified + headroom recorded
[ ] Scope tightened or task decomposed
[ ] Live catalog checked for this model [verify-at-use]
[ ] Compatible combo only (no X1/X2; no E-list defaults)
[ ] Stretch (S*) or raise-dial applied before SKU hop
[ ] If dial missing → substitute table → A→B→C→D→E→F
[ ] Cache sticky; attachments stripped if hopping
[ ] Deliverable: levers tried + failover + reset time + what NOT to retry
```
