# technical-program-management

A **Technical Program Management (TPM)** team for Claude Code — the seat that
delivers a *program of projects across multiple teams*: dependencies, critical
path, launch, and the executive narrative.

> **Not a project manager, not an engineering manager.** This plugin owns the
> seams *between* teams and projects. A single project plan → `project-management`.
> Team/people/headcount → `engineering-management`. What-to-build → `product-management`.

## Agents

| Agent | Use it for |
|---|---|
| **technical-program-manager** | Charter a program, build the program plan + RAID log, write decision-led status, drive delivery. |
| **cross-team-dependency-manager** | Map cross-team dependencies, find the critical path, surface integration risk and the worst-case rollup. |
| **program-launch-coordinator** | Run a launch-readiness review with written go/no-go criteria, design a staged rollout + rollback. |

## Skills

- `program-charter` — turn a fuzzy mandate into a chartered program with measurable outcomes and a sponsor.
- `dependency-mapping` — build the cross-team dependency graph and derive the critical path.
- `launch-readiness-review` — a go/no-go review with pre-agreed, owner-assigned criteria.

## Commands

- `/technical-program-management:charter-a-program`
- `/technical-program-management:map-dependencies`
- `/technical-program-management:run-launch-readiness`
- `/technical-program-management:write-program-status`

## Knowledge

- **Decision trees** (`knowledge/tpm-engagement-decision-trees.md`) — TPM-vs-PM-vs-EM, escalate-or-not, go/no-go.
- **Program-delivery playbook** (`knowledge/program-delivery-playbook.md`) — charter → dependencies → RAID → launch → comms.

## House opinions

- A program *is* its dependencies, not its tasks.
- Status leads with decisions and asks, not activity.
- A green status with a red dependency is a lie — roll up the worst, not the average.
- Go/no-go needs written, pre-agreed criteria. Escalation is a tool, not a failure.

## Requires

`ravenclaude-core@>=0.7.0`. Advisory only — it produces artifacts, it does not
operate your trackers, pipelines, or production systems.
