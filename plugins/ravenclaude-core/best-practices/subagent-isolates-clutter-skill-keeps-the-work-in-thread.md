# Choose a subagent to isolate clutter, a skill to keep the work in the thread

**Status:** Pattern
**Domain:** Agent design / Plugin authoring

**Applies to:** `ravenclaude-core`

---

## Why this exists

A plugin author packaging a capability faces a recurring fork: should this be a
**skill** or a **subagent**? The reflex answer — "a subagent, because it can run in
parallel" — is the wrong first cut. Parallelism is a *reason to reach for a
subagent* ([`./delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md),
[`./route-before-spawning.md`](./route-before-spawning.md) own that story), but it is
not the axis that decides skill-vs-subagent for a *single* capability. The axis that
does is **where the work's intermediate results should live**:

- **A subagent runs in its own context window** and hands back only its final,
  distilled result. The steps it took — the greps, the log lines it read, the
  approaches it tried — never enter the main thread. That is exactly right when
  those intermediate results are **clutter you will not reference again**: a deep
  search, a log-analysis pass, a dependency audit, a "go find out X and tell me the
  answer." Isolation is the feature — the main conversation stays clean and the lead
  agent keeps reasoning at full context.

- **A skill plays out inside the main thread.** Its steps, its tool calls, and its
  partial results are all visible to the lead agent as they happen. That is right
  when you want to **see and steer each step** — a procedure where the next move
  depends on the last one's output, where the human (or the lead) may want to
  intervene mid-way, or where the intermediate state *is* the value, not just the
  final answer.

Get this backwards and both failure modes are real: a **skill** for a noisy audit
floods the main window with intermediate output it will then have to compact away
(the context-cost this repo's budget rules fight —
[`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md),
[`./compact-proactively-and-persist-state-before-compaction.md`](./compact-proactively-and-persist-state-before-compaction.md)); a
**subagent** for a steer-as-you-go procedure hides the very steps you needed to watch
and returns a black-box result you can't course-correct.

## How to apply

**Ask "do I need to watch this happen, or just get the answer?"** — that one
question resolves most cases:

- **Just the answer, and the middle is noise → subagent.** "Search the codebase for
  every call site of X," "analyze these logs and summarize the failure," "audit the
  dependency tree." The lead agent gets a clean result; the mess stays isolated.
- **Watch and steer, or the middle is the point → skill.** A staged procedure the
  lead drives step-by-step, a playbook where step 3 depends on step 2's output, a
  capability the human may want to interrupt. It runs in-thread, visible.

**This is the skill-vs-subagent question, not the parallelism question.** If the real
driver is "run N of these *at once*" (fan out reads, touch independent files in
parallel), that's the delegation/fan-out rules' territory —
[`./delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md)
and [`./isolate-parallel-claude-instances-in-git-worktrees.md`](./isolate-parallel-claude-instances-in-git-worktrees.md).
Decide *isolate-vs-steer* first; reach for parallelism as a separate, additive
reason.

**Author for the choice you made.** A subagent's contract is its handoff — give it a
sharp brief and the Structured Output Protocol so the one thing it returns is
clean and parseable ([`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md),
[`./structured-output-protocol-for-all-agent-handoffs.md`](./structured-output-protocol-for-all-agent-handoffs.md)).
A skill's contract is its lean, in-thread spine — keep the body tight so its visible
steps read cleanly and the detail loads on demand
([`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md)).

## Edge cases / when the rule does NOT apply

- **A whole specialist role is neither of these — it's an agent.** This rule sorts a
  *single capability* into skill-vs-subagent. Whether a plugin should ship a new
  standalone specialist agent at all is a different, upstream question governed by
  [`./domain-plugins-extend-via-skills-not-parallel-agents.md`](./domain-plugins-extend-via-skills-not-parallel-agents.md)
  (extend core via skills/knowledge; fork a core role only when the domain's rubric
  is genuinely incompatible).
- **A capability can be both.** Some work is legitimately a skill the lead runs
  in-thread *and*, when it needs to run many times over independent inputs, is
  dispatched as parallel subagents. Author the in-thread skill; let the Team Lead
  decide per-run whether to fan it out — the two aren't mutually exclusive.
- **Deterministic must-happen-every-time work is a hook, not either.** If the point
  is enforcement (runs regardless of the model's choice), that's a hook —
  [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md).
  Skills and subagents are both model-invoked; neither guarantees it fires.
- **Non-Claude hosts differ.** The *principle* — isolate clutter, keep steerable work
  visible — ports, but the mechanics don't: GitHub Copilot CLI reads `.claude/skills`
  but its subagent/context-isolation model is its own; verify the host's behavior
  before assuming this maps 1:1.

## See also

- [`./route-before-spawning.md`](./route-before-spawning.md) — *which* specialist to spawn once you've decided a subagent is the shape; this rule is the prior question of skill-vs-subagent.
- [`./delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md) — the parallelism/fan-out axis, deliberately separate from this isolate-vs-steer axis.
- [`./domain-plugins-extend-via-skills-not-parallel-agents.md`](./domain-plugins-extend-via-skills-not-parallel-agents.md) — the upstream "should this be a new agent at all?" question this rule sits beneath.
- [`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) — how to author the skill half once you've chosen it.
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) · [`./structured-output-protocol-for-all-agent-handoffs.md`](./structured-output-protocol-for-all-agent-handoffs.md) — how to author the subagent half (sharp brief + clean handoff).

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-08 subreddit scan](../../../docs/research/2026-07-08-claude-subreddit-scan/README.md)).
The decision criterion is grounded in the Anthropic primary source
[Steering Claude Code: skills, hooks, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
("Use a subagent when a side task … would clutter your main conversation with
intermediate results you won't reference again. Use a skill when you want the
procedure to play out inside the main thread so you can see and steer each step."),
cross-checked against this repo's existing delegation/routing rules — which own the
*parallelism* axis but state no *isolate-vs-steer* criterion for a single capability.
The three-to-five-concurrent-subagents "sweet spot" and the dynamic-workflows
ceiling are `[verify-at-use]` — practitioner/feature guidance that evolves.

---

_Last reviewed: 2026-07-08 by `claude`_
