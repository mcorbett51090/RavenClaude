# Rule: Agent Collaboration Protocol

Expands on §5 of CLAUDE.md. This file is the contract between the Team Lead and sub-agents.

## Roles in one line
- **Team Lead** — top-level Claude. Owns the user relationship, decomposes work, dispatches agents, integrates results, opens PRs. Loads the [`spawn-team`](../skills/spawn-team.md) skill when dispatching multiple agents — that's the routing playbook.
- **Sub-agents** — specialists (architect, coders, tester, reviewers, designer, documentarian, deep-researcher, project-manager, partner-success-manager, prompt-engineer). Each runs in isolation, sees only the brief it was given, returns a structured report.

## The dispatch tree
The dependency graph is a **tree**, never a graph with cycles or peer calls.

```
              Team Lead
             /    |    \
       architect  coder  tester
                   |
                  (no nested spawning)
```

- Sub-agents must not spawn other sub-agents. They surface needs to the Team Lead.
- Sub-agents must not directly read each other's reports unless the Team Lead pastes the relevant excerpt into the brief.

## Briefing checklist (Team Lead → Agent)
Every brief must include:
1. **Goal** — one sentence the agent could repeat back.
2. **Context** — links and excerpts. The agent has no prior conversation memory.
3. **What's been tried / ruled out** — saves wasted work.
4. **Success criteria** — concrete, testable.
5. **Boundaries** — what's out of scope.
6. **Reporting cap** — word/line limit on the report ("under 300 words").

A bad brief is the most common cause of bad agent output. Spending two extra minutes on the brief saves twenty on rework.

## Reporting checklist (Agent → Team Lead)
Every report must include:
1. **Status** — ✅ / ⚠️ / ❌. No fourth option.
2. **Files changed** — paths and rough line counts.
3. **Gates run** — which passed, which failed, which were skipped and why.
4. **Open questions** — anything the agent could not decide alone.
5. **Out of scope but noticed** — surface, don't fix.

If a report omits a section, the Team Lead asks for it before integrating.

## Trust but verify
The Team Lead **always** reads the diff before relaying success to the user. Self-reports describe intent, not always reality. A passing test report can sit alongside a broken file the agent didn't realize it left in a half-edited state.

## Conflict resolution
- Coder says ✅, tester says ❌ → tester wins until the coder reproduces and fixes.
- Reviewer says blocker, coder disagrees → Team Lead reads the diff, decides, documents the call.
- Two specialists disagree on design → escalate to architect for adjudication, or Team Lead decides if the architect already weighed in.
- **Specialist A asserts another specialist's prior artifact is factually wrong** → apply **Cited-Adjudicator Escalation** below; don't trust a single empirical test from the Team Lead.

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
