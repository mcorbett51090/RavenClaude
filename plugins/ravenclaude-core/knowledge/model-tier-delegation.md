# Model-tier delegation — push the expensive tokens down, not just the tasks

> **Last reviewed:** 2026-09-14 against [sub-agents](https://code.claude.com/docs/en/sub-agents) and [hooks](https://code.claude.com/docs/en/hooks) (retrieved 2026-09-14). **Refresh when:** Anthropic changes the subagent `model` resolution order, the `Explore` model cap, the Agent tool's per-invocation `model` parameter, or the `PostToolUse(Agent)` `tool_response` telemetry fields. Companion to [`agent-routing.md`](agent-routing.md) (which specialist), [`subagent-isolation-and-tooling.md`](subagent-isolation-and-tooling.md) (what a subagent can do), and the [`spawn-team`](../skills/spawn-team/SKILL.md) playbook (how to brief).

This file is written for **the Team Lead** — the top-level session, which in this marketplace normally runs on the strongest model available. It answers one question the rest of the dispatch discipline had left implicit: **which model tier does each dispatched worker run on, and why does that decide whether delegation saves money or costs it.**

## The claim, stated precisely

Delegation saves **money** when the volume of tokens moves to a cheaper price tier. It does **not** save **tokens** — it usually spends more, because every handoff is overhead:

1. the orchestrator writes a brief (premium output tokens),
2. the worker loads its own system prompt and context (a fresh cache — nothing from the parent's prompt cache carries over),
3. the worker returns a report (worker output tokens),
4. the orchestrator reads that report (premium input tokens).

If the brief and the report are long, the round trip is paid before any useful work happens. Isolated subagents and agent teams have been measured at several multiples of a single continuous session's token count. **More models ≠ fewer tokens. More models = cheaper tokens, only if the workers do the volume and send back short artifacts.**

So the discipline has two halves, and the marketplace ships both:

| Half | What it controls | Where it lives |
|---|---|---|
| **Price mix** — which tier does the volume | `model:` frontmatter on every agent (gated), the [`scout`](../agents/scout.md) haiku-tier worker, the per-invocation `model` parameter | this file § "What runs on which tier" |
| **Handoff tax** — how many tokens cross the boundary each way | the worker contract in every brief (inputs / tools / success check / max output), artifact-pointer returns, the [`handoff-tax-meter`](../hooks/handoff-tax-meter.sh) hook | this file § "The worker contract", § "Hidden token sinks" |

## What runs on which tier

| Role in the run | Tier | `model:` alias | Why |
|---|---|---|---|
| Decompose the goal, choose the strategy, judge results, adjudicate disagreements | **frontier** | `opus` (or the session's model — the Team Lead itself) | Planning quality is the floor of the whole system. A cheap plan makes every downstream worker's output cheap in the bad sense. |
| Search, grep, classify, extract fields, format, lint, inventory, "find every X" | **fast** | `haiku` | High volume, low judgment. The worker reads a lot and returns a little. This is where the savings live. |
| Bounded code edits against a plan, known API calls, tests for a stated contract, first-draft prose from supplied inputs | **mid** | `sonnet` | Needs competence, not invention. The design decision has already been made upstream. |
| Gates that hold merge (security verdict, final code review), cited adjudication, research whose conclusion the run depends on | **frontier** | `opus` | The cost of a wrong verdict is the whole run, not the dispatch. |
| **Recovery when a worker botches it** | **escalate up one tier** | — | Do not let the cheap model "figure it out" on a second attempt with a longer brief. See § "The escalation ladder". |

The roster encodes this: every `agents/*.md` in every plugin declares a `model:` line (gated by `scripts/check-frontmatter.py`), the review gates and the architect pin `opus`, the coders / tester / documentarian / project-manager pin `sonnet`, and `scout` is the shipped **haiku** worker for the read-heavy, judgment-light row. Across the domain plugins the same split holds by **role shape**: the architect / lead / strategist half of a pair pins `opus`, the `*-implementation-engineer` / `*-developer` half that builds what the architect chose pins `sonnet`. That was true of the early app-craft plugins (backend / frontend / api / database / kubernetes) from the start and was made true of the later batches on 2026-09-14 in two passes: 24 implementers named or described as such (frontier share 77.7% → 73.8%), then 26 more that the name did not give away — the build half of an architect/engineer pair written in lower-case prose (73.8% → 69.7%) — see § "The role-fit gate".

**Sibling-plugin parity.** The same role shape gets the same tier wherever it appears. The second pass was found by that rule, not by a regex: every `aws-cloud` and `gcp-cloud` engineer (compute, IAM, network, ops) sat on `sonnet` beside its `opus` architect, while every `azure-cloud` engineer of the identical shape sat on `opus` — one role, three prices, decided by which month the plugin was written in. When you tier an agent, the tie-breaker is its analog in the nearest sibling plugin, and a difference between them needs a reason that names the *role*, not the batch.

**The tribunal is the shipped worked example of the price mix, and it is not a roster of agents.** [`templates/thing.yaml`](../templates/thing.yaml) seats the command-review panel by stakes: `low` convenes **no panel at all** (the deterministic concern screen clears it — zero model calls); `medium` convenes two `haiku` seats (Mímir / correctness, Heimdall / injection watch); `high` and `extreme` add Forseti (security) on `opus`, and Thor (tie-break, `opus`) is convened only on a split or low-confidence panel. Read against the table above: the volume seats that run on *every* reviewed command sit on the fast tier, the seat whose wrong verdict costs the most sits on the frontier, and the most expensive seat exists only for the recovery case. The per-seat models are the `panel.<seat>.model` knobs, so a consumer can re-price a seat without touching code — but the `≥2 distinct backbones` invariant that keeps the panel from collapsing onto one model is why the seat-level right-sizer in [`thing-decide.py`](../scripts/thing-decide.py) records what it *would* have chosen and never changes a seat's model (`evaluator_shadow` in the Sága entry). That is a recorded design decision, not a gap: re-tiering a seat is a panel-composition change, and it goes through the posture, not through a hook.

### The three ways a dispatch picks its model (verified 2026-09-14)

Claude Code resolves a subagent's model in this order — `[docs-verified 2026-09-14, sub-agents § "Choose a model"]`:

1. **The per-invocation `model` parameter on the Agent tool call** (`model: "haiku"`, `"sonnet"`, `"opus"`, or a full model id). The Team Lead can set this on any dispatch, including the built-in `Explore` / `general-purpose` types.
2. **The subagent definition's `model:` frontmatter** (`inherit` selects the main conversation's model).
3. **`CLAUDE_CODE_SUBAGENT_MODEL`** (env var), when nothing above set one. With `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+) the env var overrides everything, including plugin frontmatter — a fleet-wide "every worker on haiku" switch, at the cost of also flattening the opus gates. Do not set FORCE in a project that runs the review gates through subagents.

Before v2.1.251 the env var came **first**; that order is stale.

⛔ **`Explore` is no longer free.** Since v2.1.198 the built-in `Explore` subagent **inherits the main conversation's model** (capped at Opus on the Claude API) instead of always running on Haiku `[docs-verified 2026-09-14]`. On an Opus session, an un-pinned `Explore` dispatch is an Opus dispatch. Either pass `model: "haiku"` per invocation, dispatch [`scout`](../agents/scout.md) instead (it pins `haiku` and also receives the project's `CLAUDE.md`, which `Explore` deliberately skips), or define a project-level agent named `Explore` with `model: haiku` to override the built-in.

## The four preconditions — push work down only when all hold

1. **The subtask is well-specified after the strong model has already done the thinking.** The brief names the files, the criteria, and the shape of the answer. A cheap model given an open question does not save money; it produces a confident wrong answer that the orchestrator then pays to unwind.
2. **The worker does not need the conversation history** — just the brief plus the files it must touch. If you find yourself pasting the transcript, the task was not decomposed; it was forwarded.
3. **The worker returns a small artifact** — paths, a diff manifest, extracted fields, pass/fail plus the Structured Output Protocol block — not a narrative. Anything long goes to `.ravenclaude/runs/<run-id>/` and comes back as a pointer.
4. **Failures are cheap to retry on the cheap model** and rare enough that the orchestrator is not re-planning every time. If the same brief has bounced twice, the problem is the tier or the brief, not the worker's effort.

**The one-line test:** *if the worker's output is longer than what you would have pasted into the main model yourself, the handoff failed.*

## The worker contract (what every brief carries)

The [`spawn-team`](../skills/spawn-team/SKILL.md) Step 4 template already carries goal / context / success criteria / boundaries / reporting cap. The tier discipline adds four lines, and they are the ones that decide the cost:

```
## Worker contract
- Model tier: <haiku | sonnet | opus> — <one clause why this tier>
- Inputs: <exact paths / excerpts; NOT the conversation>
- Tools you need: <subset — read-only for scouts>
- Success check: <the deterministic thing the Team Lead will run to verify>
- Max output: <N words> + the Structured Output Protocol JSON. Long material -> write to <path>, return the path.
```

`Max output` is not a courtesy. The orchestrator re-reads every worker report at premium input rates; a 2,000-word report from a haiku scout costs more to *read* than the scout cost to *run*.

## Hidden token sinks (named so they can be checked)

| Sink | What it looks like | The fix |
|---|---|---|
| **Re-feeding the parent transcript** | A brief that opens with "here is what we discussed…" and runs to hundreds of lines | Decompose, then brief. Context is file paths and excerpts, never the conversation. The `handoff-tax-meter` flags a brief over its cap. |
| **Parallel scouts all loading the same corpus** | N `Explore`/`scout` dispatches that each `grep -r` the same tree | One scout builds the index artifact first (`.ravenclaude/runs/<run-id>/00-index.json`); the fan-out reads the index, not the repo. Fan out on *disjoint* slices. |
| **Verbose worker reports** | A "summary" that restates the brief, narrates every step, then gives the answer | Cap it in the contract; require artifact-pointer returns; the meter flags reports over the cap so the pattern is visible, not felt. |
| **Retries after a cheap model misunderstood an underspecified brief** | Same task dispatched twice to the same tier with a longer prompt | Escalate the tier once (§ below). Two haiku attempts plus the re-plan cost more than one sonnet pass would have. |
| **Un-pinned `Explore` on an Opus session** | A read-only search running on the most expensive model | `model: "haiku"` per invocation, or `scout`. |
| **Gates on the cheap tier** | A `security-reviewer` or `code-reviewer` dispatched with a per-invocation `model: "haiku"` "to save money" | Never. Gates hold merge; a missed finding costs the run. The savings live in the volume work, not the verdicts. |

## The escalation ladder (recovery goes UP, never sideways)

When a worker returns `status: blocked` / `partial`, a `confidence` below 0.5, or output the Team Lead's success check falsifies:

1. **Check the brief first.** If the brief was ambiguous, fix the brief — but re-dispatch **one tier up**, not the same tier with more words. (Re-dispatching a haiku worker with a longer brief is the classic case where "saving tokens" costs more than one strong pass.)
2. **haiku → sonnet → opus.** One rung per failure. Say the rung in the summary.
3. **After a failure at `opus`, the task is not a dispatch problem.** Route by problem type per spawn-team Step 6 (architect re-plan, ask the user, cited adjudication) — do not spawn a fourth attempt.
4. **Never de-escalate a gate.** A blocked `security-reviewer` is a finding, not a cost to route around.

## Orchestrator → workers vs. a router on the raw prompt

These look alike and behave differently:

- **Orchestrator → workers** (this marketplace's pattern): one strong brain decomposes; workers read a lot and return little. Saves money reliably when the preconditions above hold. This is [`spawn-team`](../skills/spawn-team/SKILL.md).
- **Router on the raw user prompt**: send "easy" prompts to a cheap model, "hard" ones to the frontier. Mixed evidence. A bad router sends everything to the expensive model *after* a failed cheap attempt, so it pays twice. RavenClaude's [`cheap-lane-delegation`](../skills/cheap-lane-delegation/SKILL.md) is a router of this second kind — deliberately **off by default**, deterministic (no model call to decide), and with **escalation dominating** every ambiguous match precisely because of the pay-twice failure. Do not "balance" that asymmetry.

## When NOT to build the hierarchy

A short, sequential task — one file, one function, one question — is cheaper on one mid/strong model with a tight context than on any orchestrator-plus-workers shape. The handoff tax has no volume to amortise against. [`spawn-team`](../skills/spawn-team/SKILL.md) Step 1.5's "do it yourself" row is the tier discipline's floor, not an exception to it.

The hierarchy earns its overhead when the work is **long, parallelisable, and full of mechanical reading** — the shape where a fast-tier worker can read ten files and return ten lines.

## Measuring it — cost per completed task, not tokens per call

Tokens-per-call is the wrong denominator; it rewards a quiet agent that did nothing. The unit is **cost per completed task**, and the marketplace gives the Team Lead four instruments for it — three that observe, one that binds:

| Instrument | What it records | Where |
|---|---|---|
| [`handoff-tax-meter.sh`](../hooks/handoff-tax-meter.sh) (`PostToolUse` on `Agent`) | per dispatch: `subagent_type`, requested vs `resolvedModel`, tier, brief words, report words, `totalTokens`, `totalToolUseCount`, duration, over-cap flags | `.ravenclaude/runs/<session>/dispatch-ledger.jsonl` (+ an advisory to the Team Lead on an over-cap report or brief, or an un-pinned frontier dispatch of a read-only type) |
| `bash plugins/ravenclaude-core/bin/rc dispatch-summary` (= `handoff-tax-meter.py --summary`) | the ledger rolled up: dispatches by tier, frontier share, `frontier_readonly` count, over-cap briefs/reports, median brief/report words, the token lower bound | stdout, for `/wrap` and the retrospective — the "cost per completed task" line comes from here, not from a feeling |
| [`parallelism-detector.py`](../scripts/parallelism-detector.py) (`SubagentStart`) | whether independent work ran one-at-a-time | `.ravenclaude/runs/<session>/parallelism-observations.json` |
| [`context-usage-meter.py`](../scripts/context-usage-meter.py) | how full the orchestrator's own window is — the "context pressure" trigger of the conserve-tokens exception | read by the SessionStart banner and `conserve-tokens.py` |

Honest limits, stated so the numbers are not over-trusted: `totalTokens` / `usage` on the Agent `tool_response` cover the subagent's **final** API request only, not the whole run `[docs-verified 2026-09-14]`; the ledger's word counts are exact, its token figures are a lower bound. A background (`async_launched`) dispatch carries no usage fields at all, so the ledger records the brief side and marks the report side unknown. The meter is **observation, never a gate** — the same "a hook cannot compel a shorter report" limit that governs the parallelism detector.

### The one place a hook does bind: `explore-tier-pin`

The meter flags `frontier_readonly` **after** the Explore has already run on Opus — an advisory on a bill already paid. [`explore-tier-pin.sh`](../hooks/explore-tier-pin.sh) (`PreToolUse` on `Agent|Task`) closes that gap on the one dispatch shape where a hook *can* act: when the `subagent_type` basename is `explore` and the call carries no `model`, it returns a `hookSpecificOutput.updatedInput` envelope that adds `model: haiku` (or the `pin_explore` knob's value) `[docs-verified 2026-09-14 — updatedInput is the one PreToolUse field that rewrites the Agent call]`. It never overrides an explicit `model`, stands down when `CLAUDE_CODE_SUBAGENT_MODEL` already sets a fleet default, and does nothing for any other `subagent_type` — `scout` and every roster agent already carry their tier in frontmatter. Self-test: `python3 plugins/ravenclaude-core/scripts/explore-tier-pin.py --self-test`.

### The roster-level ratchet — the frontier share may not creep

Per-dispatch pins are worthless if the roster quietly re-pins its agents to `opus` one PR at a time. [`scripts/check-model-tier-ratchet.py`](../../../scripts/check-model-tier-ratchet.py) (Gate 287 in `scripts/audit-gates.sh`) counts every `agents/*.md` across every plugin by tier and binds two invariants to [`tests/fixtures/model-tier-ratchet.json`](../../../tests/fixtures/model-tier-ratchet.json): the **frontier share** (`opus` / `fable` / `inherit` over total) may not rise, and the **haiku count** may not fall. A PR that adds an opus agent must add enough non-frontier agents to hold the share, or re-stamp the baseline with `--stamp --allow-loosen` and say why in the PR — the loosening is allowed, the *silent* loosening is not. The fixture is bound to the merge base by `check-ratchet-freshness.py`, the same way the other ratchets are.

### The role-fit gate — the tier must fit the role the agent declares

A ratchet freezes a roster; it cannot tell whether the roster it froze was right. The day the ratchet shipped, 24 agents named `*-implementation-engineer` or described "Use to BUILD …" sat on `opus` and both existing gates passed — the per-file gate saw a valid alias, the ratchet saw an unchanged share. [`scripts/check-model-tier-fit.py`](../../../scripts/check-model-tier-fit.py) (Gate 288) **reads the role**, deliberately narrowly, from `name:` + the *opening* of `description:`:

| Shape | How it is recognised | Tier it must have | Why |
|---|---|---|---|
| **merge gate** | the three the doctrine names: core `security-reviewer`, `code-reviewer`, `architect` | frontier (`opus`) | the verdict is the whole run; never de-escalated to save money |
| **implementer** | name ends `-implementation-engineer` / `-implementer` / `-coder` / `-developer`, **or** the description opens with the build verb (`Use to BUILD …`, `Use for BUILDING …`, `IMPLEMENT …`, `Build an …`, `Use for X implementation`, `hands-on`) | `sonnet` (or `haiku`) — **not** `opus` / `fable` / `inherit` | the design was made upstream by the sibling architect; this is the "bounded edits against a plan" row |
| **named fast-tier worker** | core `scout` — the agent every "dispatch `scout`" line in [`spawn-team`](../skills/spawn-team/SKILL.md), the constitution and the orchestration skills resolves to | `haiku` — a **floor** | re-tiering it up silently re-prices every one of those dispatches; symmetric to the merge-gate floor, and the fast row would otherwise have no member |
| **scout** (any other) | name is `scout` / ends `-scout`, **or** the description opens `Haiku-tier` / `Read-only` | `haiku` — **advisory only** | "read-only" is an adjective many judgment roles also use, so this leg reports and never fails. The first cut matched only `Read-only` and classified zero roster agents — the shipped `scout` opens "Haiku-tier worker" — so the leg had synthetic teeth and no positive control; a class no roster member can hit is a claim, not a measurement |

Everything else — leads, architects, strategists, analysts, specialists — is a judgment the gate does not make; Gate 287 bounds the aggregate. The verb match is anchored at the start of the description on purpose: "designs X; NOT for building it" is not the build verb. A genuine mis-read (a renewable-energy "project developer" is not a code implementer) is exempted **by name, with the reason in the diff**, in [`tests/fixtures/model-tier-fit-exemptions.json`](../../../tests/fixtures/model-tier-fit-exemptions.json) — and an exemption naming an agent that no longer exists fails the gate, because stale rows are how allow-lists rot. Report without failing: `python3 scripts/check-model-tier-fit.py --report`.

**The pair-review queue (report only).** `--report` also lists what the classifier deliberately does not rule on: every frontier-tier `*-engineer` that is unshaped, sits in a plugin that also ships an `*-architect` / `*-lead` / `*-strategist`, and whose description does not *open* by deciding (`Use to design or repair …` is the design half whatever its suffix says). That is the shape the second pass found — "Use this agent to build the Fabric Lakehouse …", "GraphQL resolvers & server: …" — and it cannot become a rule: a lower-case `build` also opens "build a defensible GHG inventory", which is an analyst. So the gate *lists* the candidates and a human tiers them, one agent at a time, with the sibling-plugin analog as the tie-breaker and the reason in the plugin's CHANGELOG. `--check` never reads the queue. An agent that stays on the queue is not wrong; it is undecided — the judgment roles that remain there (`profiling-and-capacity-engineer` finds *where* a system breaks; `database-operations-engineer` carries a production blast radius; `api-security-engineer` holds a security posture) are exactly the ones the frontier row was written for.

## Cross-host honesty — where the tier travels

The pin and the meter are Claude Code hooks; the *discipline* is not. Per host (`[docs-verified 2026-09-14]`, projected by the `generate-*-hooks.py` generators, each of which prints its skip reasons):

| Host | `model:` on the agent file | `explore-tier-pin` | `handoff-tax-meter` | So the tier lives in… |
|---|---|---|---|---|
| **Claude Code** | yes (`model:` frontmatter, gated) | wired (`PreToolUse` `Agent\|Task`) | wired (`PostToolUse` `Agent\|Task`) | the agent file, the dispatch call, and the pin as backstop |
| **Copilot CLI** | the host honours a `model:` property, but it takes a **plan-specific picker id**, so the projector states the canonical tier in the generated header and does **not** emit the field — the agent inherits the session default until you pin it | **skipped** — Copilot's hook output has no verified input-rewrite field, so a rewrite would be silently ignored | wired — Copilot ≥ 1.0.62 honours Claude matcher semantics | your pin, in the projected `.agent.md`, on your lineup's Haiku-class id |
| **Codex CLI** | the `.codex/agents/*.toml` contract has a `model` key, but it takes a **Codex model id**; same treatment — tier stated as a TOML comment, field not emitted | skipped (lane-scope: the Codex hook lanes are SessionStart-only today) | skipped (same) | your pin, in the projected TOML, or the session's `/model` |
| **Cursor** | not projected | skipped — Cursor's pre-tool lane carries a shell command, not a dispatch | skipped — no verified after-subagent event | the dispatch call (`model` on the Task call) |
| **Gemini CLI** | not projected | skipped — `Agent\|Task` has no Gemini tool equivalent in the verified vocabulary | skipped (same) | the session's model |

Read the row for your host before quoting a "we pin Explore" claim in a PR description — on four of the five it is a claim about Claude Code, not about you. The two projections that *could* carry a model (Copilot, Codex) deliberately do not invent an alias→id map: one tenant's picker lineup hard-coded into every consumer is a worse default than an honest "inherits until pinned" comment they can act on.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| `handoff_tax.report_cap_words` | `.ravenclaude/comfort-posture.yaml` | `400` | Report length above which the meter advises the Team Lead. |
| `handoff_tax.brief_cap_words` | same | `600` | Brief length above which the meter advises (the transcript-forwarding tell). |
| `handoff_tax.pin_explore` | same | `haiku` | The tier [`explore-tier-pin.sh`](../hooks/explore-tier-pin.sh) writes onto an un-pinned `Explore` dispatch (`haiku` \| `sonnet` \| `off`). `off` keeps the meter and disables only the pin. |
| `handoff_tax: off` | same | (absent = on when a posture file exists) | Disables the advisory **and** the pin; the ledger line is still written. |
| `CLAUDE_CODE_SUBAGENT_MODEL` (+ `_FORCE`) | settings `env` | unset | Fleet-wide default (or forced) worker model — see § "The three ways". |

The meter is **opt-in by posture**, exactly like every other advisory hook in this plugin: no `.ravenclaude/comfort-posture.yaml`, no advisory, no ledger.
