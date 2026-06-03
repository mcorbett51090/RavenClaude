# DMAIC project charter — {{Process / Project Name}}

> Produced by the `dmaic-project-charter` skill. Fill every section before starting the Measure phase — blank fields are a scope failure, not a placeholder. The sponsor signs this charter; an unsigned charter is a suggestion.
>
> **Last updated:** {{YYYY-MM-DD}}
> **DMAIC phase at issue:** Define

---

## 1. Problem statement

> **5W1H format.** State the current undesirable condition as fact. Do not name the cause. Do not propose the solution.

| Element | Answer |
|---|---|
| **What** is wrong? | {{The defect or failure mode in plain language}} |
| **Where** does it occur? | {{Process step, team, system, location}} |
| **When** does it occur? | {{Frequency, pattern, seasonality}} |
| **Who** is affected? | {{Customer, team, downstream process}} |
| **How much / how often?** | {{The number that proves the problem is real — current metric value}} |
| **So what — impact?** | {{Business consequence: cost, delay, customer experience, risk}} |

**One-sentence summary:**
> "{{Current metric}} is {{current value}}, against a target of {{target value}}, resulting in {{business impact}}."

---

## 2. Goal statement (SMART)

| Property | Statement |
|---|---|
| **Specific** | {{Metric name and direction: reduce / increase / eliminate}} |
| **Measurable** | {{Numerical target with units}} |
| **Achievable** | {{Brief rationale — why this target is credible}} |
| **Relevant** | {{Business outcome the sponsor cares about}} |
| **Time-bound** | {{Target date for the Control-phase close}} |

**Goal:** "Reduce/Increase {{metric}} from {{baseline value}} to {{target value}} by {{date}}."

---

## 3. Voice of the Customer (VOC) and Critical-to-Quality (CTQ) tree

| VOC — raw complaint or request | CTQ — measurable specification |
|---|---|
| {{Verbatim customer language}} | {{Metric: what, how measured, target}} |
| {{...}} | {{...}} |
| {{...}} | {{...}} |

_Capture 2–5 CTQs. More than five usually signals scope that is too broad._

**Primary CTQ (the charter metric):** {{name, operational definition, baseline value, target}}

---

## 4. SIPOC — process boundary

> High-level only (5–7 steps). Use the `sipoc.md` template for the full table. The key output here is the **start step** and **end step** that define what is in scope.

- **Process name:** {{...}}
- **Start step (in scope from):** {{Trigger event that begins the process}}
- **End step (in scope through):** {{Completion event that ends the process}}

**In scope:** {{What this project will change}}

**Out of scope:** {{What this project will NOT touch — explicitly written to prevent scope creep}}

---

## 5. Baseline metric

> The baseline is measured before any changes are made. If it does not yet exist, schedule a measurement study as the first Measure-phase task.

| Field | Value |
|---|---|
| **Metric name** | {{...}} |
| **Operational definition** | {{Exactly how this metric is measured — no ambiguity}} |
| **Current baseline value** | {{Number, unit, sample size, time period}} |
| **Data source** | {{Where the data lives}} |
| **Baseline measurement date / period** | {{YYYY-MM-DD to YYYY-MM-DD}} |
| **Target value** | {{From the goal statement}} |
| **Measurement method for Measure phase** | {{How data will be collected going forward}} |

---

## 6. Team

| Role | Name / Team | Responsibility |
|---|---|---|
| **Sponsor / Champion** | {{...}} | Owns the business case; removes organizational obstacles; signs this charter |
| **Project Lead / Black Belt** | {{...}} | Drives DMAIC execution; accountable for the result |
| **Process Owner** | {{...}} | Owns the process day-to-day; accepts the improved process at project close |
| **Team member** | {{...}} | {{Specific contribution — SME, data owner, frontline worker}} |
| **Team member** | {{...}} | {{...}} |
| **Finance representative** | {{...}} | Validates savings claim (required if financial benefit is stated in the goal) |

_A project without a named Process Owner cannot sustain its improvements. If the Process Owner is unknown, name that as Risk #1._

---

## 7. Financial benefit (if applicable)

| Metric | Value |
|---|---|
| **Estimated annual benefit** | {{$X in cost reduction / capacity freed / revenue protected — or "not financial"}} |
| **Benefit type** | Hard savings (cash out) / Soft savings (capacity) / Revenue / Risk reduction |
| **Finance validation status** | {{Preliminary estimate / Validated by {{name}} on {{date}}}} |
| **Benefit measurement plan** | {{How the benefit will be quantified and by whom at project close}} |

---

## 8. Timeline — DMAIC tollgates

| Phase | Planned start | Planned completion | Milestone / gate |
|---|---|---|---|
| **Define** | {{date}} | {{date}} | Charter signed; SIPOC complete; baseline measurement plan in place |
| **Measure** | {{date}} | {{date}} | Baseline established; process map complete; measurement system validated |
| **Analyze** | {{date}} | {{date}} | Root cause(s) proven with data; Improve-phase solution concept approved |
| **Improve** | {{date}} | {{date}} | Solution piloted; improvement quantified against baseline |
| **Control** | {{date}} | {{date}} | Control plan in place; process handed off to Process Owner; project closed |

**Critical path note:** do not begin the Improve phase until root cause is proven (Analyze tollgate gate). Skipping this gate is the most common failure mode.

---

## 9. Risks and constraints

| # | Risk / constraint | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | {{e.g., Data for the baseline metric is not currently collected}} | {{H/M/L}} | {{H/M/L}} | {{Measurement study as first Measure task; escalate to sponsor if >1 week delay}} |
| 2 | {{e.g., IT system changes require change-control approval — 4-week lead time}} | {{H/M/L}} | {{H/M/L}} | {{Submit change request in week 2 of Define, not week 1 of Improve}} |
| 3 | {{...}} | {{...}} | {{...}} | {{...}} |

---

## 10. Charter quality checklist

Before presenting to the sponsor:

- [ ] Problem statement contains a number that proves the problem is real
- [ ] Goal statement is SMART: specific metric, quantified target, deadline
- [ ] At least one CTQ with a measurable spec is named
- [ ] SIPOC: start step and end step explicitly written
- [ ] In-scope / out-of-scope written down
- [ ] Baseline metric: value, unit, sample size, measurement method
- [ ] Team table: sponsor, project lead, process owner all named
- [ ] Finance representative named if savings are claimed
- [ ] Timeline: all 5 DMAIC phases have target dates
- [ ] Risks: at least two identified
- [ ] Sponsor has reviewed and is scheduled to sign

---

## 11. Sponsor sign-off

By signing below, the Sponsor confirms:
- Resources (people's time, data access) are available for this project.
- The scope is agreed as written in §4.
- The Sponsor will remove organizational obstacles as they arise.

**Sponsor:** _____________________________________________ **Date:** _____________

**Project Lead / Black Belt:** _____________________________ **Date:** _____________

---

*This charter was produced by the `process-improvement/skills/dmaic-project-charter` skill. Re-run the skill if scope, baseline, or team changes materially.*
