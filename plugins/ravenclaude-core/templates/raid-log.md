# RAID Log — *<Project Name>*

> **Single living document tracking Risks, Assumptions, Issues, and Decisions for this engagement.** The most important PM artifact. Update weekly minimum; log critical items immediately. **Each item has exactly one owner — no "TBD," no "the team."**

**Last reviewed:** YYYY-MM-DD
**Owner of this log:** *<name>*

---

## Risks (R-#)

Things that *could* go wrong. Open items need a mitigation and a single owner.

| ID | Description | Owner | Probability | Impact | Mitigation | Status | Opened | Closed |
|----|-------------|-------|-------------|--------|------------|--------|--------|--------|
| R-1 | *Example: Client SME unavailable for 2 weeks during data validation phase.* | Matt | High | High | *Schedule data validation calls in advance; identify backup SME by 2026-05-15.* | Open | 2026-05-07 | — |

---

## Assumptions (A-#)

Conditions we're assuming will hold. Each one needs to be **validated**; if it fails, it becomes a Risk or Issue.

| ID | Assumption | Owner | Status | Validated? | Notes | Opened | Closed |
|----|------------|-------|--------|------------|-------|--------|--------|
| A-1 | *Example: Client will provide production Dataverse environment by week 2.* | *Client PM* | Open | No (target 2026-05-21) | *Prerequisite for milestone 2.* | 2026-05-07 | — |

---

## Issues (I-#)

Things that have *actually* gone wrong and need active management. Severity drives urgency.

| ID | Issue | Owner | Severity | Resolution plan | Status | Opened | Closed |
|----|-------|-------|----------|-----------------|--------|--------|--------|
| I-1 | *Example: Power Automate flow failing on rows with embedded commas.* | Matt | Medium | *Replace CSV import with Dataverse direct insert.* | Open | 2026-05-07 | — |

---

## Decisions (D-#)

Key decisions made and their rationale. **Append-only** — once a decision is logged, it's history. New decisions on the same topic get new IDs.

| ID | Decision | Decided by | Date | Rationale | Affected items |
|----|----------|------------|------|-----------|----------------|
| D-1 | *Example: Use existing client SharePoint as document store rather than spinning up new Dataverse table.* | *Matt + Client sponsor* | 2026-05-07 | *Reduces solution complexity; client already trusts the SP location.* | *Removed Dataverse setup task from scope.* |

---

## Status legend

- **Risk status:** Open, Mitigating, Closed (no longer applicable), Realized (became an Issue)
- **Issue status:** Open, In progress, Resolved, Escalated
- **Assumption status:** Open, Validated, Invalidated (became a Risk / Issue)
- **Severity / Probability / Impact:** Low, Medium, High

## Cadence

- **Weekly review** — walk every Open item, update status, retire Closed ones older than 30 days.
- **Immediate entry** — for any critical Risk or new Issue, log within the same day. Don't wait for the weekly review.
