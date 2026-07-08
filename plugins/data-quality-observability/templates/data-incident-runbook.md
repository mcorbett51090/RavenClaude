# Data-incident runbook — <dataset / pipeline>

> The response plan for a bad-data incident. Reached from an alert on
> [`data-quality-check-spec.md`](data-quality-check-spec.md). The order matters:
> **detect → triage → contain → root-cause → correct → prevent.** Do not skip to
> "re-run it and see" — that is symptom-chasing, not root-causing.

**Incident ID:** <YYYY-MM-DD-nn> · **Dataset:** <name> · **Reported by:** <monitor / person> · **Responder / on-call:** <name>

## 1. Detect
- **What fired:** <which check/monitor · freshness / volume / schema-drift / distribution / test failure>
- **First signal at:** <timestamp> · **How found:** <monitor alert / stakeholder report — note if a human beat the monitor, that's a coverage gap>
- **Symptom in plain terms:** <e.g. "revenue dashboard shows yesterday's number, mart is 6h stale">

## 2. Triage & severity
- **Severity:** <Sev-1 trusted business-facing number wrong/stale · Sev-2 non-critical or at-risk · Sev-3 warn-level / caught-at-gate>
- **Blast radius (lineage):** <downstream dashboards / models / exports that consume this and are now suspect>
- **Who to notify now:** <owner · consumers · comms channel — set expectations before they find it themselves>

## 3. Contain (stop the bleeding before you fix)
- **Containment action:** <circuit-break the downstream refresh · quarantine the bad partition · freeze the dashboard / publish a "data delayed" banner>
- **Pattern used:** <block / quarantine / warn-and-watch — chosen by downstream harm vs stall cost>
- **Confirmed contained at:** <timestamp>

## 4. Root-cause — to the CHANGE, not the symptom
Work the four usual suspects; name which one:
- [ ] **Schema change** — an upstream column renamed/dropped/retyped? <check the schema-drift monitor / diff the source>
- [ ] **Upstream source change** — the source's own data changed (new category, a backfill, a definition shift)? <compare to source>
- [ ] **Transform-logic change** — a dbt/SQL change altered the numbers? <git-blame the model between last-good and first-bad run>
- [ ] **Late-arriving / out-of-order data** — incomplete when the run fired? <check freshness/volume at run time>
- **Root cause (the change):** <the specific change, with the evidence — commit SHA / source diff / run timestamps>
- **Last-good vs first-bad:** <the run/partition boundary where it went wrong>

## 5. Correct (idempotent, partition-scoped)
- **Fix the cause:** <revert/patch the logic · adapt to the new schema · re-pull the source · wait for late data>
- **Backfill the bad slice:** <the exact partitions to reprocess — overwrite by partition (MERGE / INSERT OVERWRITE), never blind-append a "fix">
- **Backfill executed via:** <data-orchestration — with concurrency cap + monitoring; see its backfill runbook>
- **Verify corrected:** <re-run the failing checks green · consumer confirms the number is right>

## 6. Prevent (close the loop)
- **New check that would have caught it earlier:** <the test/monitor to add — e.g. a schema-drift monitor at the seam, a tighter freshness SLA>
- **Coverage gap found:** <if a human beat the monitor, what monitor was missing>
- **Owner + severity for the new check:** <who owns it · block/warn>
- **Follow-up ticket:** <link>

## 7. Retrospective (Sev-1 / Sev-2)
- **Timeline:** <detect → contain → root-cause → correct, with timestamps>
- **What worked / what was slow:** <so the next incident is faster>
- **Escalate for a program-level pattern?** <ravenclaude-core/project-manager if this is a recurring class>

**Closed at:** <timestamp> · **Signed off:** <name>
