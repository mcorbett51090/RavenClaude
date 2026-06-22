---
description: Map the cross-team dependencies for a program and derive the critical path — every handoff gets a producer, consumer, due date, and interface contract; cycles and single points of failure get flagged.
argument-hint: "[the program + teams, e.g. 'billing platform across payments, ledger, and platform teams']"
---

# Map dependencies

You are running `/technical-program-management:map-dependencies`. Build the
dependency graph and critical path for `$ARGUMENTS` using the
`cross-team-dependency-manager` discipline: a program is its dependencies, not its
tasks.

## Steps

1. **Enumerate cross-team deliverables** — producer, consumer, due date, and the
   **interface contract** (schema/API/event/doc) at each seam.
2. **Build the graph** in the [`dependency-map`](../templates/dependency-map.md)
   template (Mermaid `flowchart`).
3. **Derive the critical path** — the longest chain of gated handoffs. Compute
   **slack** on every other chain and the date its slack runs out.
4. **Flag cycles** (break with a stub/phased contract) and **single points of
   failure** (one under-resourced team on the critical path).
5. **Mark unowned interface seams** and route them to the TPM to assign an owner.

## Guardrails

- Don't assert a date without a critical path to defend it.
- A "dependency list" with no producer→consumer edges is a task list — redo it.
