# ravenclaude-core best practices

Named rules the `ravenclaude-core` agents surface to consumer-repo users. Each file is one rule — read, applied, and cited whole. These are grounded in the plugin's own constitution ([`../CLAUDE.md`](../CLAUDE.md)), knowledge files, and agent definitions; they are not generic coding advice.

For the marketplace-wide best-practice library (CI gates, hook authoring, versioning), see [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md).

---

## Index

_15 rules._

| Doc | Status | Use when |
|---|---|---|
| [`route-before-spawning.md`](./route-before-spawning.md) | Pattern | The Team Lead is about to delegate — traverse the routing tree top-to-bottom before spawning any specialist. |
| [`three-epistemic-protocols.md`](./three-epistemic-protocols.md) | Absolute rule | Any agent is about to report blocked, write a consequential claim, or hand work back — apply the CGP / Claim-Grounding / Last-Mile triad. |
| [`command-review-when-to-enable.md`](./command-review-when-to-enable.md) | Pattern | Deciding whether to turn on the command-review tribunal. |
| [`check-runtime-state.md`](./check-runtime-state.md) | Pattern | Before acting — read the event substrate (Heimdall / Víðarr / Norns tabs). |
| [`operational-console-design.md`](./operational-console-design.md) | Absolute rule | Building or reviewing any operational dashboard or "single pane of glass" surface. |
| [`delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md) | Absolute rule | Team Lead is about to fan work to sub-agents that includes any git write operation. |
| [`tee-up-human-only-residue-dont-narrate-it.md`](./tee-up-human-only-residue-dont-narrate-it.md) | Absolute rule | Any agent finishing automatable work and preparing its final output for a human. |
| [`definition-of-done-gate-makes-done-mean-done.md`](./definition-of-done-gate-makes-done-mean-done.md) | Pattern | Setting up a new project or any auto-mode session where tests must pass before the agent stops. |
| [`focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) | Pattern | Team Lead is about to delegate to a specialist — compose the task brief. |
| [`read-the-error-before-you-reroute.md`](./read-the-error-before-you-reroute.md) | Absolute rule | Any agent encountered a failure and is about to enumerate CGP alternatives. |
| [`domain-plugins-extend-via-skills-not-parallel-agents.md`](./domain-plugins-extend-via-skills-not-parallel-agents.md) | Absolute rule | Designing a new domain plugin or adding a new capability to an existing one. |
| [`structured-output-protocol-for-all-agent-handoffs.md`](./structured-output-protocol-for-all-agent-handoffs.md) | Absolute rule | Any specialist agent preparing a handoff-bearing report for the Team Lead. |
| [`web-access-allow-deny-list-before-first-fetch.md`](./web-access-allow-deny-list-before-first-fetch.md) | Pattern | Setting up a project or before any session where WebFetch will be used. |
| [`runaway-brake-prevents-the-thrash-loop.md`](./runaway-brake-prevents-the-thrash-loop.md) | Pattern | Configuring any auto-mode or unsupervised agent session. |
| [`check-constraint-scope-before-citing-it.md`](./check-constraint-scope-before-citing-it.md) | Absolute rule | Any agent is about to refuse an action or recommend against something by citing a rule. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution these rules distill
- [`../knowledge/agent-routing.md`](../knowledge/agent-routing.md) — the routing decision tree
- [`../knowledge/concerns-catalog.md`](../knowledge/concerns-catalog.md) — the tribunal's concern catalog
- [`../knowledge/orchestration-decision-trees.md`](../knowledge/orchestration-decision-trees.md) — the new orchestration decision trees
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs
