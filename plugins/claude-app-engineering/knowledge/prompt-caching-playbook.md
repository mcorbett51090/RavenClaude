# Prompt-caching playbook (the #1 cost + latency lever)

**Last reviewed:** 2026-10-17 · **Confidence:** high for the 2026-09-23 fetch ([prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [pricing](https://platform.claude.com/docs/en/about-claude/pricing), both fetched directly 2026-09-23). The 2026-10-17 corrections below follow the Claude API playbook and [`docs/plans/2026-10-14-prompt-caching/analysis.md`](../../../docs/plans/2026-10-14-prompt-caching/analysis.md) F10. This session did not re-fetch platform.claude.com. Numeric figures are dated — re-verify on the Researcher sweep.
**Owner:** `prompt-and-context-engineer`.

## The model
Caching reuses a prompt **prefix** across requests. Content up to a `cache_control` breakpoint is cached; subsequent requests with the identical prefix **read** from cache at a fraction of the base input price — **the fraction is per-model, not a flat 0.1× anymore** (see below).

Two ways to set breakpoints:
- **Automatic** (good for conversations): `cache_control` at the request top level — the system places the breakpoint on the last cacheable block and moves it forward as the conversation grows.
- **Explicit** (fine control): `cache_control` on individual blocks, **up to 4 breakpoints total**. On read, the system does a lookback to find the longest matching cached prefix.

## TTL & pricing multipliers (relative to base input; dated 2026-09-23)
| Operation | Multiplier | Applies to |
|---|---|---|
| Base input | 1× | all models |
| 5-min cache **write** | 1.25× | all models |
| 1-hour cache **write** | 2× | all models |
| Cache **read** | **0.025×** | Fable 5.1, Mythos 5.1 |
| Cache **read** | **0.05×** | Opus 5.5, Sonnet 5.5 |
| Cache **read** | **0.1×** | every other model (Haiku 5.5, Haiku 4.5, Sonnet 5, Fable 5, Mythos 5, Opus 5, Opus 4.8/4.7/4.6/4.5, Sonnet 4.6/4.5) |

**Cache read is no longer a flat 0.1× everywhere** — Fable 5.1/Mythos 5.1 are 0.025×, and Opus 5.5 and Sonnet 5.5 are 0.05×. Haiku 5.5 stays on the 0.1× row. `[docs-verified 2026-09-23 for the September launches; Sonnet 5.5 0.05× and Haiku 5.5 0.1× added 2026-10-17 from the API playbook, not re-fetched this session]` The old per-$/MTok worked example (Opus 4.7, $5/MTok base: write 5-min $6.25, write 1-hour $10, read $0.50) still applies exactly as before — substitute the model's own base price and read multiplier from the table above.

5-min default: `{"cache_control":{"type":"ephemeral"}}`; 1-hour: add `"ttl":"1h"` (use for async/agentic gaps).

## Minimum cacheable tokens (dated 2026-09-23 — verify)
| Models | Minimum |
|---|---|
| Fable 5.1, Mythos 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5, Opus 5, Fable 5, Mythos 5 | **512** |
| Opus 4.8, Sonnet 5, Sonnet 4.6, Sonnet 4.5 | **1,024** |
| Opus 4.7 | **2,048** |
| Opus 4.6, Opus 4.5, Haiku 4.5 | **4,096** |
| Haiku 3.5 | 2,048 |

The prior "Opus 4.x / Haiku 4.5 = 4,096" line was too coarse — Opus 4.7 sits at 2,048 and Opus 4.8 at 1,024, not 4,096; only Opus 4.6/4.5 (and Haiku 4.5) are at 4,096. Sonnet 5.5 and Haiku 5.5 sit on the 512-token row with the other current 5.x models. Below the minimum, the request runs **without** caching. Check `usage.cache_creation_input_tokens` / `usage.cache_read_input_tokens` to confirm. `[docs-verified 2026-09-23; Sonnet 5.5 and Haiku 5.5 minimums added 2026-10-17 from the API playbook, not re-fetched this session]`

## Cache-miss diagnostics (dated — verify)
The Claude API has a native **cache-diagnostics** beta that names *where* the prefix diverged from the previous request, so you don't have to diff payloads by hand. Pass `diagnostics.previous_message_id` on the request and read `cache_miss_reason` (e.g. `system_changed`, `tools_changed`) off the response. Beta header (2026-06-20): **`cache-diagnosis-2026-04-07`** `[verify-at-use]` ([cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics), retrieved 2026-06-20). **Claude API only** — not Bedrock/Vertex. Diagnostic fingerprints expire quickly and need closely-spaced same-org requests, so the manual payload-diff (see the [`prompt-caching-audit`](../skills/prompt-caching-audit/SKILL.md) skill) remains the durable fallback.

## The invalidation hierarchy — and the #1 real-world failure mode
Caching follows **tools → system → messages**; a change at one level busts that level **and everything downstream**:
- change a **tool definition** → invalidates *all* caches
- toggle web-search / citations / fast-mode → invalidates system + messages
- change `tool_choice` / add-remove images → invalidates messages
- thinking and effort: the tools/system effect is model-specific. A top-level `output_config.effort` change busts the cached prefix. Per-message effort (beta `mid-conversation-output-config-2026-07-01`) preserves it on Fable 5.1, Opus 5.5, Sonnet 5.5, and Haiku 5.5, not on legacy Fable 5. `[playbook 2026-10-17, not re-fetched this session]`

> **House opinion #1 — stable content above the breakpoint, volatile below; never mutate tool defs per request.** The dominant cause of a low hit rate in production is putting per-request content (timestamps, the incoming message, freshly-appended tool results) *above* the breakpoint, or reordering/regenerating tool definitions each call. Lay out: **tools (stable) → system (stable) → long static context (stable) → [BREAKPOINT] → conversation / per-request content (volatile).**

> **Changing instructions mid-session without busting the cache — mid-conversation system messages (2026-05-28, PRIMARY-VERIFIED 2026-06-30; scope corrected 2026-09-23).** The classic cache-killer is mutating the top-level `system` prompt mid-session to change instructions — it invalidates the whole cached prefix. **This is not Opus-4.8-only** — the prompt-caching invalidation table lists it as supported on **Fable 5.1, Mythos 5.1, Fable 5, Mythos 5, Opus 5.5, Sonnet 5.5, Opus 5 and Opus 4.8** `[docs-verified 2026-09-23 for the original list; Sonnet 5.5 added 2026-10-17 from the API playbook, not re-fetched this session]`. On any of those models you can instead send `role:"system"` messages *after a user turn* (subject to [placement rules](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)) inside the `messages` array: instructions change while the cached `tools`+`system` prefix stays intact, **preserving prompt-cache hits**. No beta header. A new beta as of 2026-09 lets a `tool_addition` block in a mid-conversation system message carry a full tool definition (`inline-tools-2026-09-15`), so a tool can be added/changed mid-session without editing `tools` or losing the cache. ([release notes](https://platform.claude.com/docs/en/release-notes/overview))

## What can / can't be cached
✅ tool definitions, system blocks, text/image/document blocks in messages, tool_use + tool_result blocks, prior-turn thinking blocks (counted as input on read).
❌ blocks below the minimum, empty text blocks, citations sub-blocks.

## Measure it
On every response check `usage`: `cache_read_input_tokens` (a hit — paid at that model's cache-read multiplier, not a flat 0.1×), `cache_creation_input_tokens` (a write happened), `input_tokens` (uncached, after the last breakpoint). **Cache hit rate = cache_read / (cache_read + input)** is the metric to dashboard.

## Pre-warming
Eliminate first-request latency: pre-warm with `max_tokens: 0` and explicit `cache_control` on the static prefix before users arrive, instead of a tiny completion. Refresh every ~5 min (5-min TTL) or hourly (1-hour TTL). `[F10, 2026-10-17 playbook; not re-fetched this session]`

## Thinking + caching
On Opus 4.5+/Sonnet 4.6+, prior-turn thinking blocks are preserved by default when non-tool-result content follows, keeping the cache valid. On older models/Haiku, a non-tool-result user turn strips cached thinking and invalidates. Keep thinking config consistent across turns to protect the cache.


## Turn-scoped reminders

Context editing can bust the cache at the clear point. The 2026-10-17 playbook names `clear_at_least` so a clear is large enough to be worth the bust (context-management beta). The 2026-10-14 analysis (F10) names `clear_at` for turn-scoped reminders. Re-check the field name on the caching page before relying on either spelling. `[not re-fetched this session]`

## Caching inside Claude Code

Claude Code caches `claude -p` automatically. Do not add `cache_control` on a headless call and expect the API breakpoint semantics.

- **TTL.** A subscription main session writes a 1-hour cache; an API key writes 5 minutes. Subagents and workflows stay at 5 minutes unless overridden. Knobs: `CLAUDE_CODE_PROMPT_CACHE_TTL`, `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`, `FORCE_PROMPT_CACHING_5M`, settings `promptCacheTtl` / `subagentPromptCacheTtl`, and agent frontmatter `experimental.cacheTtl: 1h` (Claude Code 2.1.248+). Source: the 2026-10-14 prompt-caching analysis (F8/F10).
- **Seeing it.** The statusline exposes a `prompt_cache` object, and `/usage` has a cache line. RavenClaude's own headless sites record the JSON envelope's `usage` via `plugins/ravenclaude-core/scripts/headless-usage.py` (`rc cache-report`).
- **Workflow siblings.** Stagger identical siblings so the second reads the first's write. Do not stagger tribunal seats: they are different models, so they do not share a prefix.
- **`--tools ""` is not a lean prefix.** It removes built-in tools and can inflate MCP tool definitions into the cached prefix. A JSON-only site that does not need MCP uses `--strict-mcp-config` before `--tools`. `--safe-mode` was smaller in one measurement and skips hooks; it is not the default. Detail: [`plugins/ravenclaude-core/knowledge/headless-claude-calls.md`](../../ravenclaude-core/knowledge/headless-claude-calls.md).

> See also [`tool-use-and-structured-output.md`](tool-use-and-structured-output.md) (tool-def stability) and [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md) (dated minimums/multipliers).
