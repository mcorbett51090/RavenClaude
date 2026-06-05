> Use this template to capture business requirements, audience, and success criteria for a new Tableau dashboard before building begins.

# Dashboard Requirements: [Dashboard Name]

## Metadata

| Field | Value |
|---|---|
| Requester | [Name / Team] |
| Owner (post-publish) | [Name / Team] |
| Target publish date | [YYYY-MM-DD] |
| Tableau Server/Cloud site | [Site URL / project path] |
| Audience | [e.g., Finance directors, field sales reps, all employees] |

---

## Business context

**What decision or action does this dashboard support?**

[Describe the decision this dashboard enables. E.g., "Weekly review of regional sales performance to identify which territories need manager intervention."]

**What is the current workflow without this dashboard?**

[E.g., "Analysts export to Excel each Monday; directors review in a meeting with no shared view."]

---

## Primary questions (one per sheet)

| # | Business question | Answer format | Priority |
|---|---|---|---|
| 1 | [e.g., Which regions are below target YTD?] | [Bar chart / KPI / map] | P0 |
| 2 | [e.g., What is the trend for the top 5 regions?] | [Line chart] | P0 |
| 3 | [e.g., Which reps are at risk of missing quota?] | [Table with conditional formatting] | P1 |
| 4 | | | |

---

## Data sources

| Source | Type | Refresh frequency | Owner |
|---|---|---|---|
| [e.g., Salesforce Opportunity] | [Published DS / live / extract] | [Daily / real-time] | [Team] |
| [e.g., Quota targets] | [Excel upload / direct DB] | [Monthly] | [Team] |

**Freshness requirement:** [e.g., Data must be no more than 24 hours old. Live connection required / extract acceptable.]

---

## Filters and interactivity

| Filter | Type | Default value | Scope |
|---|---|---|---|
| Date range | [Quick filter / parameter] | [Last 90 days] | [All sheets] |
| Region | [Quick filter / action] | [All] | [Sheets 1, 2] |
| Sales rep | [Action filter on click] | [None] | [Sheet 3 only] |

---

## Row-level security requirements

- [ ] No RLS required (data is not sensitive to this audience).
- [ ] RLS required. Dimension: [e.g., Region]. Mechanism: [entitlement table / data policy / user filter]. Reviewer: [Name].

---

## Acceptance criteria

| Criterion | Pass condition |
|---|---|
| Load time | Dashboard loads in < [5] seconds on production hardware |
| Data accuracy | Key metric matches source system within [0.1%] |
| RLS | Test user [name] sees only [their region's] data |
| Mobile | Usable on Tableau Mobile at 375 px width |
| Accessibility | Passes colour-blind check (no colour-only encoding) |

---

## Out of scope

[List anything explicitly not included in this dashboard to avoid scope creep.]

---

## Sign-off

| Role | Name | Date |
|---|---|---|
| Business owner | | |
| Data owner | | |
| Tableau admin | | |
