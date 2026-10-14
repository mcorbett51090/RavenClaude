# Prompt Caching Build Plan

> **For agentic workers:** steps use checkbox (`- [ ]`) syntax. Read [`analysis.md`](./analysis.md) first. Every number here cites one of its findings (F1–F10) or measured runs (E1–E10).

**Goal:** Cut what RavenClaude's own model calls cost and how much weekly usage they burn, mainly the command-review tribunal. Make every headless `claude -p` call cache-friendly and lean. Record cache behavior so a regression cannot go unnoticed. Correct the repo's false claims about caching.

**Architecture:** No `cache_control` and no new API client. Claude Code already caches automatically. RavenClaude controls the **shape** of the requests it sends:
1. Flags that keep MCP and context bloat out of the prefix.
2. Varying content kept small and last.
3. `usage` read back from the JSON envelope the call sites already request.
4. TTL chosen from measured re-dispatch gaps.

**Tech stack:** bash (3.2-safe), Python 3 stdlib, existing `audit-gates.sh` harness, the existing Sága, dispatch-ledger, and `bin/rc` substrate.

**Expected outcome (measured in this environment, E8):** a tribunal seat call drops from **213,164 → 4,909** input tokens. Each warm call's rewrite drops from **5,806 → 1,416**. That is about **$0.26 → $0.027** per warm panel decision and **$3.41 → $0.074** per cold one (analysis §4). The owner's machine will differ, and Phase 0 measures it.

---

## Global constraints (apply to every phase)

- **Substrate route.** `plugins/ravenclaude-core/scripts/` and `hooks/` are the tribunal's own substrate, and the self-tamper floor denies ordinary edits there. Edit them through one of the sanctioned routes:
  - the maintainer-substrate exemption (`command_review.dev_repo_exempt: true` plus the REST owner check from #1238), or
  - an API content write followed by a branch-only CI dispatch, as in the v0.324.0 milestone.

  **Never work around the guard.**
- **Every PR** must:
  - bump `ravenclaude-core`'s `plugin.json` version;
  - run `python3 scripts/sync-plugin-versions.py` and `python3 scripts/generate-copilot-plugin.py`;
  - add a CHANGELOG top entry and a CLAUDE.md milestone;
  - **supersede any stale claim in the same PR** (v0.196.0 rule).
- **New gates:**
  - Take the next free number **re-censused at land time**, after `git fetch origin main` and a merge. There is a collision history: 261→263, 269→280, 264→266.
  - Register each one in the `--check` dispatcher, the main sequence, the `Supported:` string, and a suite.
  - Then **grep the full suite output for the gate by name** (Gate 184 lesson).
- **Telemetry is derived values only.** Store integers, model ids, and fixed tokens. Never store prompt text or command text (Gate 19/110 discipline).
- **Live API probes are owner-run only.** Never in CI: they cost money and flake on MCP connection timing.
- Run the pre-PR checks in AGENTS.md § Testing instructions: `ci-preflight.py`, prettier, ruff, `audit-gates.sh`.

## Owner decisions needed (ask once, before the phase that needs it)

| # | Decision | Needed by | Default if no answer |
|---|---|---|---|
| D1 | Is a ~$0.30 per run budget acceptable for running the probe on your Mac? | Phase 0 | Run it on Haiku only |
| D2 | `--strict-mcp-config` alone, or `--safe-mode`, for seats? | Phase 1 | Decided by Phase 0 data: use `--safe-mode` only if hooks measurably inflate seats |
| D3 | Pin `inventory-nuance-judge.py` to a model, or keep inheriting the default? | Phase 1 | Keep inheriting (no quality change); add the lean flags only |
| D4 | Add a dashboard card for cache telemetry? This needs a Gate 132 DOM-ratchet raise. | Phase 2 | No card; CLI report only |
| D5 | Move the seat nonce into the user turn (security trade-off)? | Phase 5 | No; record the decision |
| D6 | Restructure the 587 KB `plugins/ravenclaude-core/CLAUDE.md`? | Phase 6 | No; out of scope until decided |

---

## Phase 0: Baseline on the owner's machine (no shipped behavior change)

**Why:** every figure in the analysis comes from this cloud environment, which has hundreds of connector MCP tools. The 208K MCP-driven figure (F1) depends on how each machine is configured. Build the instrument first, then measure.

- [ ] **0.1** Add `scripts/headless-cache-probe.py`. It is a marketplace-root dev tool and is **not shipped in a plugin**.
  - Named shapes: `seat-current`, `seat-lean-strict`, `seat-lean-safe`, `decide`, `judge`, `inventory-judge`, `orchestrate`.
  - Each shape mirrors its real call site's flags and its prompt template, with a canned command.
  - Runs `--runs N` sequentially, plus a `--parallel K` variant.
  - Prints only derived values: total, read, write (1h / 5m), uncached, `duration_api_ms`, `total_cost_usd`.
  - **Refuses to run without `--yes`** because it spends money. Defaults to `--model haiku`.
  - `--self-test` uses a stub `claude` on `PATH` that returns canned JSON, so CI can exercise it for free. Register its self-test in Gate 258's style, as part of an existing bundle or a new gate.
  - The working prototype is `seatprobe.py` from this analysis session. Its logic is reproduced in the appendix.
- [ ] **0.2** Run it on the owner's Mac with ravenclaude-core installed and the real MCP config. Write `docs/plans/2026-10-14-prompt-caching/baseline.md` with the table and the Claude Code version.
- [ ] **0.3** Answer D2 from that data:

  | Condition | Choose |
  |---|---|
  | `seat-lean-safe` rewrites at least ~1K fewer tokens per call than `seat-lean-strict` (plugin `SessionStart` hooks injecting into seats) | `--safe-mode` |
  | Otherwise | `--strict-mcp-config` (narrower, documented as stable) |

- [ ] **0.4** Measure Opus seat latency, `seat-current` against the chosen lean shape (3 warm calls each, `--model opus`). Record it. **Do not claim a latency win without this.**

**Exit criterion:** `baseline.md` committed (docs go straight to `main` per AGENTS.md), and D2 answered.

---

## Phase 1: Lean headless invocations (the main saving)

**Why:** F1 and F2. This removes about 98% of each seat call's input in this environment.

**Files** (all but the last two are substrate; see Global constraints):

| File | Change |
|---|---|
| `scripts/thing-seat.sh` (both the `_seat_run` and the no-fallback paths) | add the lean flag |
| `scripts/thing-decide.py` | add the lean flag **and `--tools ""`** — it currently gets the full default tool set; security-reviewer to confirm a decision seat needs no tools |
| `scripts/claude-orchestrate.sh` | add the lean flag |
| `scripts/prompt-optimizer-gate.sh`, `-rewrite.sh`, `-dispatch.sh` | add the lean flag |
| `scripts/prompt-optimizer-judge-soak.py` | add the lean flag |
| `skills/refine-to-rubric/scripts/judge.sh` | add the lean flag |
| `hooks/agent-dispatch-evaluator.sh` | its `--bare` path is already lean; check any non-bare fallback |
| `skills/agent-dispatch-evaluator/reference/evaluate-dispatch.js` | same |
| `scripts/inventory-nuance-judge.py` (repo root) | add `--tools "" --strict-mcp-config --output-format json`, and run from a temp dir so it stops loading the repo's ~17.6K tokens of CLAUDE.md + AGENTS.md and can no longer trigger the 587 KB nested CLAUDE.md through a file read (F7). D3 decides model pinning. |
| `.claude/workflows/rc-deep-research.js` + skill copy (optional `claude -p --bare` wrapper) | already `--bare` |

**Steps:**

- [ ] **1.1** Add the chosen lean flag (D2) **inline** at each site. Use a named constant in Python and a single quoted flag in bash. No new sourced helper: these are security-critical scripts, and a flag written at the call site is easier to audit than an indirection.
- [ ] **1.2** Keep `--tools ""` followed by another flag, **never by the positional prompt**. `--tools` is variadic, and in this session `--tools "" "$prompt"` swallowed the prompt as a tool name: *"Input must be provided either through stdin or as a prompt argument"*. Every existing site already orders it safely. Phase 1's gate pins that.
- [ ] **1.3** Correct the `thing-seat.sh:363` comment. `--tools ""` removes **built-in** tools only; the lean flag is what keeps MCP content out (F1).
- [ ] **1.4** **New gate** `scripts/check-headless-call-shape.py`. Every `claude -p` / `claude --print` invocation in shipped code must:

  | Check | Rule |
  |---|---|
  | (a) lean flag | carries `--strict-mcp-config`, `--safe-mode`, or `--bare` |
  | (b) `--tools` ordering | `--tools ""` is followed by another flag |
  | (c) exemptions | otherwise it is listed **with a reason** in `tests/fixtures/headless-call-shape-exemptions.json`; a stale or reasonless exemption fails |

  The gate also needs:
  - a **must-fail mutant** that strips the flag from a copy of `thing-seat.sh` and must turn the gate red;
  - a **positive control** that the scanner finds at least N invocations, so it refuses to pass on a scan that found nothing.
- [ ] **1.5** Regression: Gates 14, 15, 20, 22, 24, 33 (the tribunal golden eval, verdicts must not change), 50, 60 and 102 stay green.
- [ ] **1.6** `security-reviewer` signs off on the change to the tribunal seat invocation, with the diff and the Phase 0 numbers.
- [ ] **1.7** Re-run the Phase 0 probe after the change and append before/after to `baseline.md`.

**Acceptance:**
- On the owner's machine, the seat's warm per-call rewrite is at most about 2K tokens.
- Total input per seat call is within 2× of `seat-lean-*` from Phase 0.
- Golden-eval verdicts are unchanged.

**Migration (consumer-visible):** seats, judges, and the orchestrator no longer load the consumer's MCP servers. They were never meant to use them, and a seat asked to call one answered `CANNOT` (E10). No verdict change is expected. A consumer whose own MCP server somehow fed a seat would see it disappear, which is the intended isolation.

---

## Phase 2: Cache telemetry (stop flying blind)

**Why:** F6. The docs say the costliest caching failure is the silent regression.

- [ ] **2.1** At every site that already requests `--output-format json`, parse:
  - `usage`: `input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, and `cache_creation.ephemeral_{5m,1h}_input_tokens`;
  - `total_cost_usd`;
  - the model id.

  Append them as **derived integers** to the log each site already writes:

  | Site | Log |
  |---|---|
  | tribunal seats | Sága entry |
  | decision review | its decisions log |
  | soak | soak results |
  | judge loop | its run artifacts |
  | orchestrator | its run dir |

  Absent fields mean "not reported". **Never `0`.**
- [ ] **2.2** Add an `rc cache-report [--days N]` verb to `bin/rc`. It rolls up hit rate per call site and model, with `hit_rate = read / (read + write + uncached)`, plus write tokens per call and estimated cost. It must print its own limit: `total_cost_usd` is a client-side estimate, and subscription accounting is unverified.
- [ ] **2.3** Resolve the false claim in `agent-dispatch-evaluator/SKILL.md:147`. Either the evaluator now records `cache_creation_input_tokens` through 2.1, or delete the sentence.
- [ ] **2.4** Gate: extend Phase 1's gate, or add one, so that:
  - a fixture JSON envelope produces the exact derived row;
  - a payload with planted prompt text produces a row without it (derived-values-only);
  - a must-fail mutant that writes a raw field turns it red.
- [ ] **2.5** (D4) Optionally, a Heimdall-adjacent dashboard card. Only with an owner-approved Gate 132 raise.

**Acceptance:** a real tribunal decision writes a Sága row with cache fields, and `rc cache-report` shows the seat hit rate.

---

## Phase 3: Knowledge and doc corrections

**Why:** F9 and F10. Some of these are docs-only and can go straight to `main`; plugin files go through a PR.

- [ ] **3.1** New core knowledge file `plugins/ravenclaude-core/knowledge/headless-claude-calls.md`, with dated sources. It holds the rules for any `claude -p` the marketplace ships:
  - the lean flag;
  - keep the varying content small and last;
  - record `usage`;
  - never stagger a multi-model panel;
  - the variadic `--tools` footgun;
  - the TTL facts: 1h main and `-p` on a subscription, 5m on an API key and for subagents and workflows;
  - `--exclude-dynamic-system-prompt-sections` is cross-user only and measured no effect here.

  Cross-link it from `knowledge/model-tier-delegation.md` and the tribunal skill.
- [ ] **3.2** Refresh `plugins/claude-app-engineering/knowledge/prompt-caching-playbook.md` with every F10 item:
  - the 512-token minimum for Sonnet 5.5 / Haiku 5.5;
  - Sonnet 5.5's 0.05× cache reads;
  - `max_tokens: 0` pre-warm;
  - the model-specific tools/system effect of thinking and effort changes;
  - mid-conversation system messages on Sonnet 5.5, and `clear_at`.

  Add a new section, **"Caching inside Claude Code"**, covering:
  - `CLAUDE_CODE_PROMPT_CACHE_TTL` / `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` / `FORCE_PROMPT_CACHING_5M`;
  - the statusline `prompt_cache` object;
  - the `/usage` cache line;
  - workflow sibling stagger;
  - the `--tools ""` MCP gotcha.

  Re-date it and bump `claude-app-engineering`'s version.
- [ ] **3.3** `rc-deep-research.js` (both copies, kept byte-identical for Gate 126): remove or qualify the `opts.cache_control` / `opts.thinking` lines and their comments at `:61-65, 108-128`. Keep them only if a probe shows `agent()` honors them. Today they are undocumented options and the "1h verify cache" claim is unbacked.
- [ ] **3.4** Append a dated correction box to `docs/research/2026-06-04-claude-features-gap-analysis/gap-analysis.md` §B3. Append; do not rewrite history. State that the 2026-06-04 withdrawal was unmeasured, and link `analysis.md`.

---

## Phase 4: Subagent TTL from data

**Why:** F8. Subagents get a 5-minute TTL even on a subscription. `experimental.cacheTtl: 1h` in agent frontmatter (2.1.248+) helps only agents that are re-dispatched 5–60 minutes apart.

- [ ] **4.1** Add `scripts/subagent-ttl-advisor.py` (read-only). It reads `.ravenclaude/runs/*/dispatch-ledger.jsonl` and computes each agent's same-session re-dispatch gaps.

  **Break-even:** a 1-hour write costs 0.75× more than a 5-minute write (2.0 against 1.25). Each re-dispatch 5–60 minutes later then reads at 0.1× instead of rewriting at 1.25×, which saves 1.15×. So the 1-hour TTL pays off when an agent averages **at least ~0.65 in-window re-dispatches per write**. Recommend it only above that.
- [ ] **4.2** Run it on the owner's real ledgers and record the result. **Zero qualifying agents is a valid outcome.**
- [ ] **4.3** If any qualify, add `experimental: { cacheTtl: 1h }` to those agents only. First confirm that `check-frontmatter.py` accepts the key, and that the Copilot and Codex projections (`generate-copilot-plugin.py`, the Codex lane) drop it rather than emit an unknown field.

---

## Phase 5 (optional, security-gated): byte-stable seat system prompts

**Why:** F5. The saving is small: about 0.8–1.1K rewritten tokens per seat call.

- [ ] **5.1** Proceed only if Phase 2 telemetry shows the Opus seats' per-call write is still material **and** D5 is yes.
- [ ] **5.2** In `thing-seat.sh` and `judge.sh`, move the category and the nonce out of `--append-system-prompt` into the trusted preamble at the top of the user turn. The system prompt then says the delimiter nonce is declared on the user turn's first line. Defang rules stay unchanged.
- [ ] **5.3** Gate 15 (injection fixtures, including forged-delimiter cases) and Gate 33 (golden eval) stay green. Add one fixture where the untrusted payload declares its own nonce line, and assert a deny.
- [ ] **5.4** `security-reviewer` signs off. If declined, record the decision in the plan and close the phase.

---

## Phase 6 (owner decision D6): shrink the dev repo's largest cache write

**Why:** F7. `plugins/ravenclaude-core/CLAUDE.md` (587,591 bytes) is injected whole into any dev session or subagent that reads under that directory, at about 150–230K tokens and a 1-hour write price.

- [ ] **6.1** Measure first:
  - the exact injected token count, with `count_tokens` or a session counter;
  - whether consumer sessions ever load it from the plugin cache (expected: no);
  - every gate or script that greps this file.
- [ ] **6.2** If D6 is yes, run it as its own `/forge`. The candidate shape: keep the normative constitution sections and move the dated milestone narratives to a history file, with one-line pointers. This has a big blast radius, and the design check-in applies.

---

## Sequencing

| Phase | Depends on | Size | Ships in plugin? |
|---|---|---|---|
| 0 Baseline | D1 | S | No (dev tool + doc) |
| 1 Lean invocations | 0 | M | Yes (core) |
| 2 Telemetry | 1 | M | Yes (core) |
| 3 Knowledge/docs | none (3.2/3.3 after 0) | S | Yes (core + claude-app-engineering) |
| 4 Subagent TTL | 2 (ledger data) | S | Maybe (frontmatter only) |
| 5 Byte-stable seats | 2, D5 | S | Yes (core) |
| 6 CLAUDE.md shrink | D6 | L | Dev-repo only |

Phases 1 and 3 can run in parallel worktrees: their files do not overlap except the CLAUDE.md milestone, so merge order resolves it.

## Explicitly out of scope

These are covered with reasons in `analysis.md` §5:
- `cache_control` anywhere;
- staggering seats;
- `--exclude-dynamic-system-prompt-sections`;
- a global 5-minute TTL;
- pre-warming;
- live cache assertions in CI.

---

## Appendix: reproducing E8 (the seat measurement)

```bash
# From any NON-repo directory, so no project CLAUDE.md loads. Haiku keeps the cost to cents.
# seat_system.tmpl = the SEAT_SYSTEM heredoc body extracted from thing-seat.sh:
awk '/^read -r -d .. SEAT_SYSTEM <<SYS/{f=1;next} /^SYS$/{f=0} f' \
  "$RC/plugins/ravenclaude-core/scripts/thing-seat.sh" > seat_system.tmpl

# Current shape: fresh mktemp dir per call, nonce + category substituted into the system text
claude -p --output-format json --model haiku --tools "" \
  --append-system-prompt "$SYSTEM_WITH_NONCE" "$USER_PROMPT_WITH_NONCE"

# Lean shape: same template, nonce and category moved to the user turn
claude -p --output-format json --model haiku --strict-mcp-config --tools "" \
  --append-system-prompt "$SYSTEM_WITHOUT_NONCE" "$USER_PROMPT_DECLARING_NONCE"

# Read: .usage.{input_tokens,cache_read_input_tokens,cache_creation_input_tokens}
#       .usage.cache_creation.{ephemeral_5m_input_tokens,ephemeral_1h_input_tokens}
#       .total_cost_usd  .duration_api_ms
```

Run each shape three times **sequentially**. Call 1 is the cold write; calls 2 and 3 show the warm rewrite. Phase 0.1 turns this into `scripts/headless-cache-probe.py`.
