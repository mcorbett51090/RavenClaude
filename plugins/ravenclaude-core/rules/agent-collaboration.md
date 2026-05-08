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
