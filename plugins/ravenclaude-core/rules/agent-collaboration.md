# Rule: Agent Collaboration Protocol

Expands on §5 of CLAUDE.md. This file is the contract between the Team Lead and sub-agents.

## Roles in one line
- **Team Lead** — top-level Claude. Owns the user relationship, decomposes work, dispatches agents, integrates results, opens PRs. Loads the [`spawn-team`](../skills/spawn-team/SKILL.md) skill when dispatching multiple agents — that's the routing playbook.
- **Sub-agents** — specialists (architect, coders, tester, reviewers, designer, documentarian, deep-researcher, project-manager, partner-success-manager, prompt-engineer, scout). Each runs in isolation, sees only the brief it was given, returns a structured report. Each runs on the **model tier its frontmatter pins** (`model:` is gated on every agent file) — frontier for the gates and the architect, mid for the coders, fast for the scout. The tier is part of the contract, not an implementation detail; see [`knowledge/model-tier-delegation.md`](../knowledge/model-tier-delegation.md).

## The dispatch tree
The dependency graph is a **tree**, never a graph with cycles or peer calls.

```
              Team Lead
             /    |    \
       architect  coder  tester
                   |
            (single-orchestrator by house policy)
```

- Sub-agents do not spawn other sub-agents — single-orchestrator is the binding default; they surface needs to the Team Lead. **(This is a deliberate house policy, not a platform limit.** Claude Code *permits* nested sub-agent spawning, but the platform default has since tightened — the earlier "5 levels deep (v2.1.172)" note is **superseded**: **v2.1.217 (2026-07-21)** changed subagents to *not* nest by default, then **v2.1.219 (2026-07-24)** set the default nesting depth to **3** (env `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `=1` disables nesting). RavenClaude retains the single-orchestrator pattern on purpose — for observability, debuggability, loop-avoidance, and because every nested hop pays the handoff tax at the *caller's* tier where the Team Lead cannot see it. **The layer that binds is the `tools:` allow-list, not this sentence:** a sub-agent whose `tools:` omits `Agent` cannot dispatch, and `Agent(type)` scoping is *ignored* in a sub-agent definition, so `Agent` in any form is an unscoped grant `[docs-verified 2026-09-14, sub-agents § "Restrict which subagents can be spawned"]`. **Gate 289** (`scripts/check-nested-dispatch.py`) fails any shipped agent whose `tools:` grants `Agent` / `Task` / `"*"` without a reasoned, by-name exemption in `tests/fixtures/nested-dispatch-exemptions.json` — the one sanctionable shape is a frontier-tier parent fanning out to fast-tier read-only leaves; see [`docs/decisions/2026-09-14-nested-dispatch-determination.md`](../../../docs/decisions/2026-09-14-nested-dispatch-determination.md). `guard-recursive-spawn.sh` stays as the **soft** prose-level nudge (warns, does not block). The gate cannot reach the built-in `general-purpose` / `claude` types, a fork, or a consumer's project-local agent, all of which can nest; `handoff-tax-meter` records those as `nested_dispatch` and the consumer's off-switch is `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`. `[platform facts re-verified 2026-09-14 against the sub-agents and hooks references]`)
- Sub-agents must not directly read each other's reports unless the Team Lead pastes the relevant excerpt into the brief.

## Briefing checklist (Team Lead → Agent)
Every brief must include:
1. **Goal** — one sentence the agent could repeat back.
2. **Context** — links and excerpts. The agent has no prior conversation memory.
3. **What's been tried / ruled out** — saves wasted work.
4. **Success criteria** — concrete, testable.
5. **Boundaries** — what's out of scope.
6. **Reporting cap** — word/line limit on the report ("under 300 words").
7. **Worker contract** — the model tier and one clause why it fits (`haiku` for read-a-lot-return-a-little, `sonnet` for a bounded edit against a plan, `opus` for design / adjudication / a gate), the **exact inputs** as paths or excerpts, the tools the worker needs, and the deterministic **success check** the Team Lead will run. Template: [`spawn-team`](../skills/spawn-team/SKILL.md) Step 4; tier table: Step 4.25.
8. **Artifact pointer** — a `Max output: <N> words` line plus the rule for overflow: anything longer is written to `.ravenclaude/runs/<run-id>/<phase>.{md,json}` and the report carries the **path**, never the content.

A bad brief is the most common cause of bad agent output. Spending two extra minutes on the brief saves twenty on rework.

**Never paste the conversation into `Context`.** The worker has no prior memory *by design* — that is what makes its context cheap. Paths and excerpts, not the transcript. A brief that has to forward the transcript to make sense was not decomposed; it was forwarded, and the handoff cost more than doing the work in-session. The [`handoff-tax-meter`](../hooks/handoff-tax-meter.sh) flags this shape (`brief_over_cap`, default 600 words) when the posture enables it.

## Reporting checklist (Agent → Team Lead)
Every report must include:
1. **Status** — ✅ / ⚠️ / ❌. No fourth option.
2. **Files changed** — paths and rough line counts.
3. **Gates run** — which passed, which failed, which were skipped and why.
4. **Open questions** — anything the agent could not decide alone.
5. **Out of scope but noticed** — surface, don't fix.
6. **Artifact, not narrative** — the report stays under the brief's `Max output`; the deliverable is the small thing the Team Lead asked for (paths, a diff manifest, extracted fields, pass/fail) plus the Structured Output Protocol block. Anything longer lives at a `.ravenclaude/runs/<run-id>/…` path named in `deliverables`. **The one-line test: if the report is longer than what the Team Lead would have pasted into its own context, the handoff failed** — the Team Lead re-reads every word at frontier input rates.

If a report omits a section, the Team Lead asks for it before integrating. If a report *exceeds* its cap, the Team Lead reads the structured block and the artifact path, not the prose — and tightens the cap in the next brief to that worker.

## The handoff is overhead — keep both ends short

Delegation saves **money** only when the volume of tokens moves to a cheaper tier; it never saves **tokens**, because every dispatch is a brief written at premium output rates, a fresh worker context that shares none of the parent's cache, a report, and a re-read of that report at premium input rates. Both halves of this contract exist to keep that tax small:

| Half | What keeps it small | Measured by |
|---|---|---|
| Brief (Team Lead → worker) | paths + excerpts, not the transcript; a tier that fits; `Max output` stated | `brief_over_cap` |
| Report (worker → Team Lead) | the artifact shape the brief asked for; overflow to a run-dir path | `report_over_cap` |
| Tier (who pays) | read-only / mechanical work on `haiku`; gates never de-escalated | `frontier_readonly` |

The three flags are the advisory [`handoff-tax-meter`](../hooks/handoff-tax-meter.sh) (`PostToolUse` on `Agent`), which also appends one counts-only line per dispatch to `.ravenclaude/runs/<session>/dispatch-ledger.jsonl` so cost-per-completed-task is auditable after the run. Opt-in by comfort posture; never blocks. Doctrine and the token sinks it watches for: [`knowledge/model-tier-delegation.md`](../knowledge/model-tier-delegation.md).

## Trust but verify
The Team Lead **always** reads the diff before relaying success to the user. Self-reports describe intent, not always reality. A passing test report can sit alongside a broken file the agent didn't realize it left in a half-edited state.

## Conflict resolution
- Coder says ✅, tester says ❌ → tester wins until the coder reproduces and fixes.
- Reviewer says blocker, coder disagrees → Team Lead reads the diff, decides, documents the call.
- Two specialists disagree on design → escalate to architect for adjudication, or Team Lead decides if the architect already weighed in.
- **Specialist A asserts another specialist's prior artifact is factually wrong** → apply **Cited-Adjudicator Escalation** below; don't trust a single empirical test from the Team Lead.
- **A worker returns `partial` / `blocked`, or its result is falsified by the success check** → escalate **one tier up** (haiku → sonnet → opus) with the same brief tightened, never the same tier with more words. A cheap model asked to "figure it out" is the classic case where saving tokens costs more than one frontier pass. After a failure *at* opus the problem is the brief or the plan, not the dispatch — go back to the architect or the user.

## Cited-Adjudicator Escalation

When Agent A confidently calls out Agent B's claim or artifact as wrong, the Team Lead must triage instead of immediately trusting A *or* running a single test to refute A. A one-shot orchestrator test can confirm-wrong-for-wrong-reasons; the resolution often needs a *cited* third opinion.

**Pattern** — *Cited-Adjudicator Escalation*. Synthesis of Anthropic's [Evaluator-Optimizer](https://www.anthropic.com/research/building-effective-agents), [AutoGen's Critic agent](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_groupchat_research/), and LLM-as-Judge selection heuristics. The third specialist's contract is **citation-backed adjudication**, not a re-vote or a re-test.

**Decision rule (Team Lead applies on receiving a "B is wrong" claim from A):**

1. **Trust A immediately** when A's claim is in A's domain of authority AND doesn't contradict an existing artifact.
2. **Test it yourself** when the claim is *deterministically verifiable by software* — schema, exit code, file presence, regex match. Never spawn a judge for what `python3 -m json.tool` or a single regex can settle.
3. **Spawn `deep-researcher` in citation-only mode** when *any two* of the following hold:
   - A's claim contradicts B's prior artifact AND A's `confidence` ≥ 0.7 in the Structured Output Protocol block.
   - The domain is correctness-critical (security, concurrency, shell/regex/glob semantics, crypto, data loss, layout enforcement).
   - Your one-shot test could plausibly confirm-wrong-for-wrong-reasons (e.g., the matcher worked in your test but A specified a *different input class*).
   - Resolution requires citing a *spec* (POSIX, RFC, bash manual, vendor docs), not running code.
4. **Escalate to the user** when the third specialist still cannot resolve. Never spawn a fourth agent — that's debate without termination.

**How to brief the third specialist (cap at 200 words):**

- Paste both prior claims verbatim with their `confidence` labels. Do **not** paraphrase. Do **not** signal whom you believe.
- Name the exact authority class required ("bash reference manual section on Pattern Matching", "RFC 7231 §4.3.1").
- Forbid running new code as the *primary* evidence; require a citation. Repro is corroborating evidence only.
- Required output: binary verdict + cited line. JSON shape: `{ "A_correct": bool, "B_correct": bool, "citation": "<url+quote>", "confidence": <0..1> }`.

**Why this exists:** this pattern was added to the constitution after the failure mode it prevents played out during the marketplace's own self-review. An architect agent confidently claimed a hook was buggy; the Team Lead's one-shot test seemed to refute it; the deep-researcher confirmed (with bash manual citations) that the architect was *partially* correct on mechanics but wrong on the conclusion. A single empirical test would have settled it the wrong way.

## Parallel vs. sequential
| Pattern | When |
|---------|------|
| Parallel | Independent work in separate worktrees (e.g. backend + frontend on a stable contract; code-reviewer + security-reviewer on the same diff) |
| Sequential | When B's input depends on A's output (architect → coder → tester → reviewer) |

When in doubt, sequential. The cost of a wasted round-trip is lower than the cost of two agents stomping each other.

## Worktree discipline
- One agent per worktree. One worktree per agent task.
- The Team Lead creates the worktree before dispatch and tears it down after integration.
- An agent that finds itself wanting to leave the worktree (touch shared config, etc.) stops and asks.

## Silence is failure
Agents that go quiet without a report are failures, not "in progress." If an agent has been running > 5 minutes with no output, the Team Lead checks in or aborts.
