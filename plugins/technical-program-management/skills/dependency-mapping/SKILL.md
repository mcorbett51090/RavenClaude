---
name: dependency-mapping
description: "Build the cross-team dependency graph and derive the critical path — every handoff gets a producer, consumer, due date, and interface contract; cycles and single points of failure get flagged. Use when a program spans multiple teams and you need to know what actually decides the date."
---

# Skill: Dependency mapping

Make the invisible cross-team handoffs visible, then compute what actually drives
the program date. A program is its dependencies, not its tasks.

## When to use

- A program spans ≥2 teams and the date feels unknowable.
- Two teams are building toward an integration with no agreed contract.
- You need to know which slips matter (critical path) and which don't (slack).

## Procedure

1. **Enumerate cross-team deliverables.** For each, record: producer team,
   consumer team, due date, and the **interface contract** (schema / API / event /
   doc) at the seam. A handoff with no named interface is the highest-risk kind.
2. **Build the graph.** Nodes are deliverables; edges are "X must finish before Y
   can start." Use the [`dependency-map`](../../templates/dependency-map.md) template.
3. **Derive the critical path.** Find the longest chain of gated handoffs — that
   chain *is* the date. Compute **slack** on every other chain.
4. **Flag cycles** (A waits on B waits on A): break with a stub/mock or a phased
   contract. **Flag single points of failure**: one under-resourced team on the
   critical path is a key-person risk.
5. **Make every seam contract-first.** Where two teams meet, agree the interface
   *before* either builds. Route unowned seams to the TPM to assign an owner.

## Output

A dependency map, the critical path, the slack on non-critical chains, and a list
of flagged cycles/SPOFs feeding the RAID log.

## Anti-patterns

- A "dependency list" that's really a task list (no producer→consumer edges).
- A date asserted with no critical path to defend it.
- An interface seam with no owner and no contract.
