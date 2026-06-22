# Program-delivery playbook

The end-to-end arc a TPM runs, from a fuzzy mandate to a landed, launched program.
Each stage names its artifact and the agent that owns it.

## Stage 1 — Charter (technical-program-manager)

Convert a mandate into a program. A program is real only when it has:

- **A measurable outcome** — the one sentence the sponsor will judge "done" by,
  with a metric and a target date. "Improve billing" is not an outcome; "cut
  invoice-generation latency p95 from 8s to <2s by Q3" is.
- **A named sponsor** — the single accountable executive who can break ties and
  fund tradeoffs.
- **Scope boundaries** — explicit in *and* out of scope. Out-of-scope is the more
  important list; it's what protects the date.
- **The teams** — who is on the hook and for what deliverable.
- **The starting RAID** — the known risks, assumptions, issues, dependencies.

Artifact: [`../templates/program-charter.md`](../templates/program-charter.md).

## Stage 2 — Dependencies & critical path (cross-team-dependency-manager)

The plan is built around the seams, not the tasks.

- Enumerate every **cross-team deliverable**: producer, consumer, due date, and the
  **interface contract** (schema/API/event/doc) at the seam.
- Derive the **critical path** — the longest chain of gated handoffs. Quantify the
  **slack** on every other chain so urgency tracks reality, not visibility.
- Flag **cycles** (break with a stub/contract) and **single points of failure**
  (one under-resourced team on the critical path).

Artifact: [`../templates/dependency-map.md`](../templates/dependency-map.md).

## Stage 3 — Run the program: RAID + decision-led status

- Keep the **RAID log** live — every item has an owner and a date; risks have
  mitigations, not hopes. Artifact: [`../templates/raid-log.md`](../templates/raid-log.md).
- Send **decision-led status** on a fixed cadence. The top of every update is the
  change in risk/critical path, the decision needed, and the ask. Roll up the
  **worst** dependency, not the average. Artifact:
  [`../templates/program-status-update.md`](../templates/program-status-update.md).
- **Escalate by the tree**, framed as a decision request to a named owner.

## Stage 4 — Launch (program-launch-coordinator)

- Define **go/no-go criteria** *before* the readiness review — measurable, owned.
- Run the **readiness review**; reach an explicit decision with an owner; record
  any **waiver** with its risk acceptance.
- Roll out in **stages**, each gated on a metric, with a **tested rollback**.

Artifact: [`../templates/launch-readiness-checklist.md`](../templates/launch-readiness-checklist.md).

## Stage 5 — Close

Declare done **against the chartered outcome's metric** — not "we shipped some
stuff." Capture what the dependency map and RAID got wrong so the next program
estimates better. A program with no measurable outcome cannot be closed honestly.

## The four house rules, condensed

1. A program is its dependencies, not its tasks.
2. Status leads with decisions and asks, not activity (worst-dependency rollup).
3. Go/no-go needs written, pre-agreed criteria.
4. Escalation is a tool, not a failure — early and framed as a decision request.

See [`../best-practices/README.md`](../best-practices/README.md) for the full
opinions and [`tpm-engagement-decision-trees.md`](tpm-engagement-decision-trees.md)
for the trees.
