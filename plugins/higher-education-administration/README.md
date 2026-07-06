# higher-education-administration

A RavenClaude plugin: a **higher-education administration operations** specialist team for the three engines of a college or university's administrative operation — institutional strategy, enrollment management, and student success.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Advisory domain operations knowledge — not legal, financial-aid-compliance, or academic-policy advice.** Funnel benchmarks, discount-rate norms, and retention/persistence metric definitions are volatile and institution-/system-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed against your own institutional-research definitions, aid-office rules, and accreditor before it drives a target, a budget, or an intervention. **FERPA-aware — the agents store no student PII;** they work in cohorts, funnels, and policy, never individual student records.

## What it's for

Running the administrative side of an institution well: an enrollment funnel modeled stage-by-stage rather than guessed at a headcount, a discount rate deployed as deliberate strategy instead of drifting upward by accident, a yield defended before it melts, and a retention operation that catches at-risk students on an early alert instead of at the withdrawal desk.

## Agents

| Agent | Use for |
|---|---|
| **higher-ed-administration-lead** | Enrollment strategy, budget / net-tuition-revenue model, retention/completion, cross-functional coordination (admissions/registrar/aid/student-success), accreditation |
| **enrollment-management-strategist** | The inquiry->apply->admit->yield->melt funnel, yield & discount-rate modeling, financial-aid leveraging, recruitment |
| **student-success-advisor** | Retention/persistence, early-alert, advising, at-risk intervention, completion, DFW-course analysis |

## What's inside

- **4 skills** — enrollment-funnel-and-yield, financial-aid-and-discount-rate, retention-and-student-success, registrar-and-academic-operations.
- **Knowledge bank** — [`higher-ed-decision-trees.md`](knowledge/higher-ed-decision-trees.md) (4 Mermaid trees: yield/melt intervention, discount-rate / aid-leverage decision, at-risk student triage, enrollment-vs-retention lever choice) + [`higher-ed-reference-2026.md`](knowledge/higher-ed-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — enrollment funnel model, retention intervention plan.
- **2 commands** — `/model-enrollment-funnel`, `/build-retention-plan`.

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install higher-education-administration@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the advisory scope, routing rules, house opinions, and the output contract.
