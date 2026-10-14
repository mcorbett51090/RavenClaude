# Prompt caching for RavenClaude: analysis

**Date:** 2026-10-14 · **Claude Code:** 2.1.299 · **Companion:** [`BUILD-PLAN.md`](./BUILD-PLAN.md)

**Sources:**
- The Anthropic page [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), fetched 2026-10-14.
- Claude Code docs: env-vars, prompt-caching, cli-reference, headless, statusline, workflows. A docs-research subagent read these; claims from it are tagged `[subagent-researched]`.
- `claude --help` from the installed CLI.
- About 50 measured headless `claude -p` calls in this session, all on Haiku 5.5. The client-side estimate (`total_cost_usd`) was about $0.57 in total.

This file keeps **observations** (what a tool returned) apart from **inferences** (what we concluded from them), per AGENTS.md § Accuracy discipline.

---

## Verdict

**Yes, caching can make RavenClaude much cheaper. The way to get there is not to add `cache_control`.**

Claude Code already caches every request it sends, including the `claude -p` subprocesses RavenClaude launches. RavenClaude has only one direct Anthropic SDK call site, and its prompt is below every cacheable minimum. So there is nowhere to place a breakpoint.

The savings come from **changing how RavenClaude shapes the requests that Claude Code caches for it.**

The June 2026 gap analysis withdrew this item as "nothing to do": the CLI auto-caches, and the seat briefs "are already constant." That conclusion was never measured, and it is partly wrong. Measured this session (§3), the tribunal seat's current call shape sent **213,164 input tokens per call**. A lean shape that answers the same question sent **4,909**. On a warm cache, the current shape rewrote 5,806 tokens per call; the lean shape rewrote 1,416.

---

## 1. Where caching reaches RavenClaude

| Surface | What RavenClaude controls | Caching mechanism |
|---|---|---|
| **A. RavenClaude's own headless calls**: tribunal seats, decision review, orchestrator, prompt optimizer, judges, inventory judge | Flags, working directory, and prompt layout on every `claude -p` | Claude Code automatic caching. Write TTL is 1 hour on a subscription (observed) and 5 minutes with an API key `[subagent-researched]`. |
| **B. Claude Code sessions RavenClaude shapes**: main session, subagents, workflows | CLAUDE.md size, hook-injected context, agent frontmatter, workflow prompt layout | The same automatic caching. Subagents and workflow agents get a 5-minute TTL even on a subscription `[subagent-researched]`. |
| **C. Consumer-facing knowledge** | `claude-app-engineering/knowledge/prompt-caching-playbook.md` and the `prompt-caching-audit` skill | Explicit `cache_control` in consumers' own API code |

The one direct SDK call is `scripts/eval-adaptive-classifier.py`. It uses the Batch API with a judge rubric of about 250 tokens, below every model's minimum, so caching has no effect there.

---

## 2. Findings

### F1. Removing all tools still loads every MCP server's content into each seat call

**Observation** (`--tools ""` on a non-`--bare` call, run here in the scratchpad directory): about **212K** input tokens.

| Flags | Input tokens |
|---|---:|
| `--tools ""` | 211,798 |
| `--tools "" --strict-mcp-config` | 3,470 |
| `--safe-mode --tools ""` | 3,444 |
| default tools | 46,600 |
| default tools, `--strict-mcp-config` | 39,747 |

**Inference:** the roughly 208K difference is content from configured MCP servers. Tool search normally defers MCP tool schemas, but `--tools ""` removes ToolSearch, so they load upfront. We did not inspect the bytes. The `--strict-mcp-config` A/B is the evidence.

**Consequence:**
- No call site in the repo passes `--strict-mcp-config` or `--safe-mode`. The audit found zero.
- Nearly every site passes `--tools ""` without `--bare`, which is exactly the shape that inflates.
- The size depends on each user's MCP configuration. This cloud environment has hundreds of connector tools; a machine with two MCP servers will see much less. Phase 0 measures it on the owner's machine.

**Side note, checked once:** a seat run with `--tools ""` was asked to call an MCP tool and answered `CANNOT` (1 turn, 0 permission denials). So the inflation is a cost problem. It is not shown to be a capability or security gap.

### F2. The varying question and a large context block are rewritten together on every call

**Observation:** with `--strict-mcp-config` and default tools, two calls differing only in the question each wrote **12,951** tokens and read 26,803.
- With `--disable-slash-commands`, the rewrite fell to **2,889**.
- With `--safe-mode --tools ""`, it fell to **1,280–1,416**.

**Inference:**
- Claude Code puts its context block (skills listing, CLAUDE.md, environment) into the **same final user message** as the `-p` prompt.
- Its last cache breakpoint therefore lands after content that is unique to each call. That whole block is rewritten every call and never read back, which is the documented anti-pattern of an automatic breakpoint after a unique tail.
- RavenClaude cannot move Claude Code's breakpoints. It can only shrink that block.

### F3. The tribunal's parallel seats cannot share a cache, by design

**Observation (same model, cold brief):**
- **3 seats fired in parallel:** each wrote 23,988 tokens.
- **1 seat, then 2 more:** seats 2 and 3 read 34,945 and wrote 13,498.

**Inference:** the concurrent-request rule holds: a cache entry is readable only after the first response starts. But the tribunal deliberately puts each seat on a different model (`thing-decision.py:801-808` puts at least 2 distinct backbones on the panel), and caches are per model. **Staggering seats would add latency and save nothing.** The only lever is making each seat's cold write small.

The Workflow tool already holds matching siblings for 5 seconds (`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`) so they share a cache `[subagent-researched]`. RavenClaude workflows get this for free.

### F4. `--exclude-dynamic-system-prompt-sections` had no measurable effect here

**Observation:** a call from a second directory rewrote about **12,955** tokens with or without the flag (one run per cell). In lean mode, the cached system prefix (2,110–2,162 tokens) was read from either directory. Changing git status between calls caused no extra rewrite.

**Consequence:** do not adopt the flag. It targets reuse across users and machines, and same-machine reuse already happens. Random `mktemp` working directories are not a cost driver in lean mode, so no stable scratch directory is needed.

### F5. The per-call nonce in the seat system prompt has a real but small cost, and it is a security trade-off

**Observation:**
- `thing-seat.sh:239` generates a 16-byte random nonce on every call. It goes into the system prompt passed via `--append-system-prompt` (`:254-282`), along with the category.
- `judge.sh:151,187` does the same.

**Inference:** on a warm call, the variable part of the system prompt is about 0.8–1.1K tokens of each call's rewrite. That is much smaller than F1 or F2. Moving the nonce into the user turn weakens where the delimiter is declared, which is an injection-defense decision. Low priority, and gated on security review.

### F6. No call site records usage, so a cache regression would be silent

**Observation:**
- Every site that passes `--output-format json` reads only `.result` and `.is_error`.
- No site records `usage` or `total_cost_usd`; the audit grepped every call-site file.
- `agent-dispatch-evaluator/SKILL.md:147` claims "Phase 5 monitors `cache_creation_input_tokens`". No code does.

**Consequence:** the docs say the costliest caching failure is the silent regression. RavenClaude has no instrument that could see one.

### F7. The nested `plugins/ravenclaude-core/CLAUDE.md` is the largest cache write in a dev session

**Observation:**
- The file is **587,591 bytes**.
- It was injected whole into this session the first time a file under that directory was read.
- The session's remaining-token counter fell by about 227K tokens that turn. The other content in that turn was a few thousand tokens.

**Inference:**
- Every dev session or subagent that reads under that directory pays one cold write of roughly 150–230K tokens, at the 2× one-hour write price in the main session.
- Every later turn pays reads on that context.
- Consumers are probably unaffected, because the plugin cache sits outside their project tree `[unverified]`.

### F8. TTL is already one hour where it helps; subagent TTL is a data question

**Observation:** every write in this session's probes was `ephemeral_1h`. Documented `[subagent-researched]`:
- Main and `-p` calls get 1 hour on a subscription and 5 minutes on an API key.
- Subagents and workflows get 5 minutes on both.
- Overrides: `CLAUDE_CODE_PROMPT_CACHE_TTL`, `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`, `FORCE_PROMPT_CACHING_5M`, settings `promptCacheTtl` / `subagentPromptCacheTtl`, and agent frontmatter `experimental.cacheTtl: 1h` (2.1.248+).

**Inference:** a RavenClaude agent re-dispatched at 5–60 minute gaps would benefit from a 1-hour TTL. One re-dispatched within 5 minutes would not. The dispatch ledger (`handoff-tax-meter`) already records the timestamps that settle this per agent.

### F9. Four claims in the repo are false or unbacked

| Where | Claim | Status |
|---|---|---|
| `docs/research/2026-06-04-claude-features-gap-analysis/gap-analysis.md:83` | Seat briefs are constant strings and "the code already does" keep prefixes stable | True for `thing-decide.py`. False for `thing-seat.sh` and `judge.sh` (F5), and it misses F1/F2 entirely. |
| `plugins/ravenclaude-core/scripts/thing-seat.sh:363` (comment) | `--tools ""` "disables ALL tools" and keeps the seat minimal | It removes built-in tools and inflates MCP content (F1). |
| `skills/rc-deep-research/rc-deep-research.js:61-65, 108-128` and its byte-identical mirror at `.claude/workflows/rc-deep-research.js` | 1-hour `cache_control` on the verify phase | `cache_control` and `thinking` are not documented `agent()` options. Probably ignored `[unverified]`. |
| `skills/agent-dispatch-evaluator/SKILL.md:147` | "Phase 5 monitors `cache_creation_input_tokens`" | No code does (F6). |

### F10. The consumer-facing caching playbook has drifted

`prompt-caching-playbook.md` (last reviewed 2026-09-23) against the 2026-10-14 docs:

**Outdated:**
- The Sonnet 5.5 and Haiku 5.5 minimum (512 tokens) is missing.
- Sonnet 5.5's 0.05× cache-read rate is missing.
- Pre-warming still says "fire a tiny request" instead of `max_tokens: 0`.
- Thinking and effort changes are listed as invalidating messages. The docs now say the tools and system effect is model-specific.

**Missing:**
- Mid-conversation system messages are now on Sonnet 5.5.
- `clear_at` turn-scoped reminders.
- Any section on Claude Code itself: TTL knobs, the statusline `prompt_cache` object, the `/usage` cache line, workflow stagger, and the `--tools ""` MCP gotcha.

---

## 3. Evidence: measured runs

All runs used Haiku 5.5 in this cloud environment (Claude Code 2.1.299, many connector MCP servers configured). Token totals are `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`. In every run, `input_tokens` (the uncached remainder) was 2.

| # | Shape | Total in | Read | Write |
|---|---|---:|---:|---:|
| E1 | default, identical prompt, 5 runs | 46,600–46,679 | 24,445–46,598 | 0–22,153 |
| E2 | `--strict-mcp-config`, second identical call | 39,747 | 39,745 | 0 |
| E4 | `--strict-mcp-config`, new directory, with or without `--exclude-dynamic-…` | ~39,650 | 26,693–26,794 | ~12,955 |
| E5 | 3 parallel seats, cold 8.7K brief | 48,444 each | 24,454 | 23,988 each |
| E5 | 1 seat, then 2 | 48,445 | 34,945 (2nd/3rd) | 13,498 (2nd/3rd) |
| E6 | `--strict-mcp-config`, varying question | 39,756 | 26,803 | 12,951 each |
| E6 | `+ --disable-slash-commands`, varying question | 38,045 | 35,154 | 2,889 |
| E6/E7 | `--safe-mode --tools ""`, varying question, two directories | 3,444–3,450 | 2,162 | 1,280–1,286 |
| **E8** | **real seat template, current shape** (fresh `mktemp` dir, nonce in system, `--tools ""`) | **213,164** | 0 → **207,341** | 213,162 → **5,806** |
| **E8** | **same seat, lean shape** (`--safe-mode --tools ""`, nonce in user turn) | **4,909** | 544 → **3,491** | 4,356 → **1,416** |
| E9 | `--tools ""` only, versus `+ --strict-mcp-config` | 211,798 vs 3,470 | — | — |
| E10 | `--tools ""`, asked to call a read-only MCP tool → 1 turn, answered `CANNOT`, 0 permission denials | 211,833 | 208,959 | 2,872 |

- One of five identical default calls (E1, run 2) rewrote about 20K tokens. **Inference:** MCP connection timing varies between runs. This kind of nondeterminism is what `--strict-mcp-config` removes.
- **Latency was not shown to improve** in these runs. A 212K cold write on Haiku took 4.5 s of API time, against 2–3 s for small prompts. A latency benefit for the Opus seats is a hypothesis for Phase 0, not a finding.

---

## 4. Economics: one tribunal decision, input side only

This takes E8's measured token counts and applies list prices for the default panel:
- Forseti: `claude-opus-4-8`, $5/MTok; 1-hour write $10; read $0.50.
- Heimdall: `claude-sonnet-5`, $2; $4; $0.20.
- Mímir: `claude-haiku-4-5`, $1; $2; $0.10; 4,096-token minimum.

**Inference:** the Opus 4.7/4.8 tokenizer can count up to about 1.35× more tokens than Haiku 5.5's, so real Opus figures may be higher.

| Shape | Warm (cache hit) | Cold (first decision in the TTL window) |
|---|---:|---:|
| Current: 213K prefix, 5.8K rewrite per call | Forseti $0.162 + Heimdall $0.065 + Mímir $0.032 = **≈ $0.26** | $2.13 + $0.85 + $0.43 = **≈ $3.41** |
| Lean: 4.9K total, 1.4K rewrite per call | $0.016 + $0.006 + $0.005* = **≈ $0.027** | $0.049 + $0.020 + $0.005 = **≈ $0.074** |

\* The lean prefix is below Haiku 4.5's 4,096-token minimum, so Mímir is not cached. It pays full input on about 4.9K tokens, which is still the cheapest seat.

- **Ratio:** about 10× cheaper warm and about 46× cheaper cold, in this environment. On a machine with few MCP servers the current shape is smaller (about 40K, per E1/E2), so the ratio there is smaller. Phase 0 measures the owner's real number.
- Thor joins on a split panel, which adds one more Opus call.
- **On a subscription** these are client-side estimates. The real effect is weekly-usage headroom, which the Routine token reserve exists to protect. How cache reads count against subscription limits is `[unverified]`.

---

## 5. What not to do

- **Do not add `cache_control` anywhere.** No RavenClaude call site goes to the API directly with a cacheable prefix.
- **Do not stagger tribunal seats.** They run on different models (F3).
- **Do not adopt `--exclude-dynamic-system-prompt-sections`** (F4). It moved no number here.
- **Do not force a 5-minute TTL globally.** The 1-hour main/`-p` TTL is what keeps a seat's system prefix warm across decisions minutes apart.
- **Do not pre-warm.** Seat traffic is bursty and spread across models; each pre-warm is a write per model.
- **Do not put a live cache-hit assertion in CI.** It costs money and flakes on MCP timing. Use a structural gate plus an owner-run live probe, the same split as Gate 207's Tier D.

## 6. Open / unverified

- The composition of the 208K of MCP-driven content (F1). We did not inspect it, and the inference may be wrong about deferral.
- Whether plugin `SessionStart` hooks inject context into seat calls on a machine with ravenclaude-core installed. If they do, `--safe-mode` beats `--strict-mcp-config` alone. Phase 0 measures it.
- Whether `--safe-mode` (documented as a troubleshooting mode) is stable enough to depend on.
- Whether consumers' sessions ever load a plugin's nested CLAUDE.md from the plugin cache (F7).
- Opus-seat latency difference between the current and lean shapes.
