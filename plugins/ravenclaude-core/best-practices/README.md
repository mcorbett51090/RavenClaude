# ravenclaude-core best practices

Named rules the `ravenclaude-core` agents surface to consumer-repo users. Each file is one rule — read, applied, and cited whole. These are grounded in the plugin's own constitution ([`../CLAUDE.md`](../CLAUDE.md)), knowledge files, and agent definitions; they are not generic coding advice.

For the marketplace-wide best-practice library (CI gates, hook authoring, versioning), see [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md).

---

## Index

_24 rules._

| Doc | Status | Use when |
|---|---|---|
| [`route-before-spawning.md`](./route-before-spawning.md) | Pattern | The Team Lead is about to delegate — traverse the routing tree top-to-bottom before spawning any specialist. |
| [`prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md) | Pattern | Setting up a consumer repo (or reviewing a `CLAUDE.md`) — deciding whether a rule belongs in a hook/CI gate vs. prose, and pruning the file. |
| [`three-epistemic-protocols.md`](./three-epistemic-protocols.md) | Absolute rule | Any agent is about to report blocked, write a consequential claim, or hand work back — apply the CGP / Claim-Grounding / Last-Mile triad. |
| [`command-review-when-to-enable.md`](./command-review-when-to-enable.md) | Pattern | Deciding whether to turn on the command-review tribunal. |
| [`check-runtime-state.md`](./check-runtime-state.md) | Pattern | Before acting — read the event substrate (Heimdall / Víðarr / Norns tabs). |
| [`operational-console-design.md`](./operational-console-design.md) | Absolute rule | Building or reviewing any operational dashboard or "single pane of glass" surface. |
| [`delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md) | Pattern | Team Lead is about to fan work to sub-agents that includes any git write operation — serialize writes in main, or isolate each writer in its own worktree. |
| [`tee-up-human-only-residue-dont-narrate-it.md`](./tee-up-human-only-residue-dont-narrate-it.md) | Absolute rule | Any agent finishing automatable work and preparing its final output for a human. |
| [`definition-of-done-gate-makes-done-mean-done.md`](./definition-of-done-gate-makes-done-mean-done.md) | Pattern | Setting up a new project or any auto-mode session where tests must pass before the agent stops. |
| [`focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) | Pattern | Team Lead is about to delegate to a specialist — compose the task brief. |
| [`read-the-error-before-you-reroute.md`](./read-the-error-before-you-reroute.md) | Absolute rule | Any agent encountered a failure and is about to enumerate CGP alternatives. |
| [`domain-plugins-extend-via-skills-not-parallel-agents.md`](./domain-plugins-extend-via-skills-not-parallel-agents.md) | Absolute rule | Designing a new domain plugin or adding a new capability to an existing one. |
| [`structured-output-protocol-for-all-agent-handoffs.md`](./structured-output-protocol-for-all-agent-handoffs.md) | Absolute rule | Any specialist agent preparing a handoff-bearing report for the Team Lead. |
| [`web-access-allow-deny-list-before-first-fetch.md`](./web-access-allow-deny-list-before-first-fetch.md) | Pattern | Setting up a project or before any session where WebFetch will be used. |
| [`runaway-brake-prevents-the-thrash-loop.md`](./runaway-brake-prevents-the-thrash-loop.md) | Pattern | Configuring any auto-mode or unsupervised agent session. |
| [`check-constraint-scope-before-citing-it.md`](./check-constraint-scope-before-citing-it.md) | Absolute rule | Any agent is about to refuse an action or recommend against something by citing a rule. |
| [`checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md) | Pattern | Setting up a fast-iterating or unsupervised session — when to use `/rewind` (Esc-Esc) vs. a git commit, and what checkpoints structurally can't undo. |
| [`permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md) | Pattern | Configuring a project's permission posture — sorting operations into `deny`/`ask`/`allow` (eval order, the reversibility taxonomy) instead of reaching for bypass-everything or approve-reflexively. |
| [`mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md) | Pattern | Deciding which MCP servers to enable — every enabled server preloads its full tool schemas into the context window, so right-size the set, prefer tool-search/lazy-loading, and measure with `/context`. |
| [`isolate-parallel-claude-instances-in-git-worktrees.md`](./isolate-parallel-claude-instances-in-git-worktrees.md) | Pattern | Running two or more independent Claude Code instances at once — give each its own git worktree/branch so concurrent writers don't stomp one working tree (the peer-process complement to the sub-agent fan-out rule). |
| [`keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) | Pattern | Authoring a SKILL.md — keep the body lean and push depth into `resources/` so progressive disclosure carries the detail (the body is always loaded; resources load on demand). |
| [`claude-md-imports-organize-they-dont-shrink-context.md`](./claude-md-imports-organize-they-dont-shrink-context.md) | Pattern | Structuring a `CLAUDE.md` with `@imports` — they organize content, they do NOT shrink its context cost (imported files are still loaded); prune, don't just split. |
| [`scope-the-reviewer-to-correctness-or-it-manufactures-work.md`](./scope-the-reviewer-to-correctness-or-it-manufactures-work.md) | Pattern | Briefing a code-reviewer agent — scope it to correctness/risk or it manufactures low-value churn. |
| [`expensive-test-front-loading.md`](./expensive-test-front-loading.md) | Pattern | A test costs a scarce resource (a human re-fire, a long run, a billed turn, a deploy) — exhaustively static-validate first so each expensive test exercises a fully-validated change; prefer a deterministic validator over a "remember to check" rule. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution these rules distill
- [`../knowledge/agent-routing.md`](../knowledge/agent-routing.md) — the routing decision tree
- [`../knowledge/concerns-catalog.md`](../knowledge/concerns-catalog.md) — the tribunal's concern catalog
- [`../knowledge/orchestration-decision-trees.md`](../knowledge/orchestration-decision-trees.md) — the new orchestration decision trees
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs
