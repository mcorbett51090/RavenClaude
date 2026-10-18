# Headless Claude calls in ravenclaude-core

**Last reviewed:** 2026-10-17. Applies to this plugin's `claude -p` sites. The consumer API playbook is [`plugins/claude-app-engineering/knowledge/prompt-caching-playbook.md`](../../claude-app-engineering/knowledge/prompt-caching-playbook.md). Measured call shapes are in [`docs/plans/2026-10-14-prompt-caching/analysis.md`](../../../docs/plans/2026-10-14-prompt-caching/analysis.md).

Claude Code caches `claude -p` itself. Do not add `cache_control` on these sites.

## Pins

Catalog `current` (Gate 134): Opus 5.5 `claude-opus-5-5`, Sonnet 5.5 `claude-sonnet-5-5`, Haiku 5.5 `claude-haiku-5-5`, Fable 5.1 `claude-fable-5-1`.

| Rule | Why |
|---|---|
| Set effort explicitly | Opus 5.5 and Haiku 5.5 default to `medium`. An unset Opus seat is under-powered. Agent frontmatter `effort:` is the Claude Code surface. |
| Fable 5.1 only after Opus at `xhigh` demonstrably fails | Same sticker price as Opus is not the point: Fable is the hardest tail, not the default. |
| Do not pin legacy `claude-fable-5` | Same sticker price, 4× cache-read price, no per-message effort. Fall back to Opus 5.5, not to Fable 5. |
| The model-fallback ladder may still list Fable | That ladder is an outage retry, not the quality-escalation rule. |

Haiku 5.5 is $0.10 / $0.50 per million tokens at or under 100k prompt tokens, and 5× above that. Keep a triage prompt under that cliff. A lean seat prefix can also sit under the cache minimum, so Mímir may stay uncached and still be the cheap seat.

## Call shape

`--tools ""` removes built-in tools. It does not keep MCP tool definitions out of the prefix. The measured stable lean flag for a JSON-only site that already passes `--tools ""` and cannot call MCP is `--strict-mcp-config`, placed before `--tools`.

| Flag | This plugin |
|---|---|
| `--strict-mcp-config` | Added on JSON-only sites that already passed `--tools ""` and do not need MCP: `thing-seat.sh`, `claude-orchestrate.sh`, `prompt-optimizer-gate.sh`, `prompt-optimizer-rewrite.sh`, `prompt-optimizer-dispatch.sh`, `prompt-optimizer-judge-soak.py`, `judge.sh`. Since 0.356.0 also `thing-decide.py` (both calls, with `--tools ""`) and the repo-root `scripts/inventory-nuance-judge.py`. Gate 306 (`scripts/check-headless-call-shape.py`) requires it on every `claude -p` site unless the file is exempt with a reason in `tests/fixtures/headless-call-shape-exemptions.json`. |
| `--bare` | Already the lean flag on `agent-dispatch-evaluator.sh`. Not combined with `--strict-mcp-config` here; that pair was not measured. `--bare` also stays opt-in on seats (`THING_SEAT_BARE` / `ANTHROPIC_API_KEY`). This change does not flip that. |
| `--safe-mode` | Not used. It skips hooks, and whether it beats `--strict-mcp-config` once hooks are counted was not measured on the owner's machine. |

`--tools` is variadic. A positional prompt must not sit immediately after `--tools ""`. Sites that pass the prompt next use `--tools=""`.

## Left unchanged, and why

| Site | Why it was left |
|---|---|
| `thing-decide.py` `_run_seat` and the evaluator shadow | **Changed in 0.356.0** (pending security review): both calls now pass `--strict-mcp-config --tools ""`. The seats only ever return a verdict JSON, so they need no tools, and a seat that can call tools while reading untrusted decision text was a wider injection surface than needed. Live probe of the seat shape: ~4,825 input tokens. Usage is recorded. |
| `agent-dispatch-evaluator.sh` | Already `--bare`. Combining with `--strict-mcp-config` is unmeasured. Usage is recorded. The model pin moved. |
| `scripts/inventory-nuance-judge.py` | **Changed in 0.356.0:** `--strict-mcp-config --tools=` and a temp cwd, so the repo's `CLAUDE.md`, project hooks and project MCP config stay out of the judge's prompt. The model is still the CLI default. |
| Both `rc-deep-research.js` copies | Already `--bare`. `opts.cache_control` / `opts.thinking` are still set but are not documented `agent()` options, so they are probably ignored (not re-probed). Since 0.355.11 the comments say so instead of claiming a 1-hour verify cache. Gate 126 keeps the two copies identical. Claude pins moved. |
| Nonce in the seat system prompt | Moving it into the volatile tail (Phase 5 / D5) changes the security boundary. Not done. |
| Secret handling | `THING_SEAT_BARE` and whether `ANTHROPIC_API_KEY` is set were not touched. |

## Cached prefix and volatile tail

Lay the stable brief, rubric, and tool list above the breakpoint. Put the per-request question, nonce, and peer verdicts in the tail. A top-level effort change busts the cache. Per-message effort (beta `mid-conversation-output-config-2026-07-01`) preserves it on 5.1 / 5.5 models, not on legacy Fable 5. Delta re-reviews should append a turn to the cached prefix, not rebuild the prompt.

Do not stagger tribunal seats to share a cache. They are different models. Do not adopt `--exclude-dynamic-system-prompt-sections`; it was not the measured win.

## Usage

`scripts/headless-usage.py record` appends a derived row to `.ravenclaude/runs/headless-usage.jsonl` (gitignored; override with `HEADLESS_USAGE_LOG`). Absent fields are omitted. A present `0` is kept. Prompt text and `result` text are not logged. Record mode is fail-open and does not change the caller's exit code.

`rc cache-report` prints the sum, then one line per call site with its own hit rate (since 0.357.0), so a site that never reads the cache stands out. Hit rate is `cache_read / (cache_read + cache_creation + input_tokens)`; a site with no denominator prints `n/a`. `total_cost_usd` is the client-side estimate on the envelope. Subscription accounting is unverified. Since 0.357.0 the repo-root `scripts/inventory-nuance-judge.py` records too (site `inventory-nuance-judge`, JSON envelope), and Gate 307 runs the recorder's self-test plus a `--must-fail` mutant that stores result text and must be caught.

## Effort, max tokens, verdicts, batches

- Effort must be set explicitly. On Claude Code that is agent frontmatter `effort:` / the session `effortLevel`. These `claude -p` sites do not pass an API `max_tokens`; inventing a CLI flag for it would be a guess. A direct Messages API call at `high` / `xhigh` needs headroom (start near 64k at `xhigh`) because thinking counts against `max_tokens`. Alert when `stop_reason` is `max_tokens`.
- Structured verdicts stay prompt-forced JSON plus the existing salvage. API `output_config.format` does not apply to these `claude -p` sites. Do not invent a CLI schema flag.
- Message Batches are 50% off and are the right shape for a latency-insensitive judge. The one direct SDK Batch site is `scripts/eval-adaptive-classifier.py`. Do not move the soak or the tribunal onto Batch; those are interactive. Batch cache hits are best-effort.

## Console checklist

Operator checklist, not a claim that a workspace already exists:

1. Put lab keys and `--bare` / Batch spend in a separate Console workspace with a spend cap. A spend-cap `429` is not a rate-limit `429`.
2. Key expiry is immutable. Rotate by creating a new key.
3. Subscription `claude -p` cache writes in the main session are 1 hour; an API key is 5 minutes. Subagents stay at 5 minutes unless a TTL knob overrides it (`CLAUDE_CODE_PROMPT_CACHE_TTL`, `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`, `FORCE_PROMPT_CACHING_5M`).
4. Confirm the key's workspace before treating `total_cost_usd` as the bill.

## Not done here

Owner-machine Phase 0 baseline, nonce relocation, and shrinking the plugin `CLAUDE.md`. Those stay follow-ups. (The call-shape gate shipped as Gate 306 in 0.356.0, with a live probe of the two new shapes.)
