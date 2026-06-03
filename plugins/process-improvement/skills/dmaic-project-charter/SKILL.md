---
name: dmaic-project-charter
description: "Scope an improvement opportunity as a DMAIC project: problem statement, quantified goal, CTQ/VOC, SIPOC boundaries, baseline metric, team, and timeline. Produces a populated charter using the dmaic-project-charter template."
---

# Skill: dmaic-project-charter

> **Invoked by:** `process-improvement/black-belt` (primary). Also used by any agent framing a new improvement initiative before committing to a root-cause analysis or solution design.
>
> **When to invoke:** when a performance problem (cost, quality, speed, capacity) is named but not yet scoped; when a sponsor asks "can we fix this?" and no one has written down *what* success looks like; when a team is about to start solving before defining the problem.
>
> **Output:** a populated `dmaic-project-charter.md` with every section completed — blank fields are a scope failure, not a placeholder.

## Why the charter matters

An unchartered project is a conversation, not a project. The charter does four things no Slack thread can:

1. **Forces quantification** — "faster billing" becomes "reduce billing-cycle time from 9.2 to ≤ 5 days."
2. **Locks the boundary** — in-scope and out-of-scope are written down so the team doesn't scope-creep into a six-month undertaking.
3. **Names the metric before the improvement** — you cannot claim a win if you didn't declare the baseline first (see best-practice: `measure-the-baseline-before-you-change-anything.md`).
4. **Creates the sponsor contract** — the charter is signed by the sponsor. A signed charter is a license to act; an unsigned one is a suggestion.

## Step-by-step

### Step 1 — Identify the problem and the process

Confirm the following before writing anything:

| Question | Answer required |
|---|---|
| What is broken or underperforming? | One sentence, user-observable impact |
| Which process does it live in? | Named process, start step → end step |
| Who is the customer of that process? | Internal (team) or external (end user / client) |
| Is there data showing the problem exists? | At least one number or a documented complaint |

If the answer to any row is "unknown," that is the first task — go find out. Don't draft a charter on a hypothesis.

### Step 2 — Write the problem statement (5W1H format)

The problem statement is **not** the solution, the cause, or the goal. It is a factual description of the current undesirable condition.

| Element | Prompt |
|---|---|
| **What** is wrong? | The defect or failure mode in plain language |
| **Where** does it occur? | Process step, system, location, team |
| **When** does it occur? | Frequency, pattern, seasonality |
| **Who** is affected? | Customer, team, downstream process |
| **How much** / how often? | Magnitude, volume, rate — the number that proves the problem is real |
| **So what** — impact? | Business consequence: cost, delay, customer experience, risk |

Poor: "Billing is slow." Better: "Customer invoices are issued an average of 9.2 days after service delivery (target: ≤ 5 days), resulting in delayed cash collection and 12 escalations/month from the AR team."

### Step 3 — Define the goal statement (SMART)

| Property | Requirement |
|---|---|
| **Specific** | Names the metric and the direction (reduce, increase, eliminate) |
| **Measurable** | States a number and the unit |
| **Achievable** | Grounded in data, not wishful thinking |
| **Relevant** | Ties to a business outcome the sponsor cares about |
| **Time-bound** | States the deadline (end of DMAIC project) |

Example: "Reduce billing-cycle time from 9.2 days (current) to ≤ 5 days (target) by [date]."

### Step 4 — Identify CTQs from the Voice of the Customer

The **Voice of the Customer (VOC)** is the raw complaint, request, or observation. The **Critical-to-Quality (CTQ)** is the measurable specification that satisfies it.

| VOC (raw) | CTQ (measurable spec) |
|---|---|
| "Invoices arrive too late" | Billing-cycle time ≤ 5 days |
| "I can never reach support" | First-response time ≤ 4 hours, 95th percentile |
| "Onboarding drags on forever" | Time-to-activate ≤ 3 business days |

Capture 2–5 CTQs. More than five usually means the scope is too broad.

### Step 5 — Build the SIPOC (high level)

Use the `sipoc.md` template. The SIPOC defines the outer boundary — what is in scope. Confirm the start step and end step explicitly; write them into the charter.

### Step 6 — Establish the baseline metric

The baseline is the **current-state** value of the primary CTQ, measured before any changes are made. This is non-negotiable — see best-practice `measure-the-baseline-before-you-change-anything.md`.

- State the metric name and operational definition (exactly how it is measured).
- State the current value (with sample size and time period).
- State the target value.
- State how the metric will be collected in the Measure phase.

If a baseline does not exist, schedule a measurement study as the first Measure-phase task. Do not skip the baseline and plan to "measure after we fix it."

### Step 7 — Define the team

| Role | Responsibility |
|---|---|
| **Sponsor / Champion** | Owns the business case; removes organizational obstacles; signs the charter |
| **Project Lead / Black Belt** | Drives DMAIC execution; accountable for the result |
| **Process Owner** | Owns the process day-to-day; must accept the improved process at project close |
| **Team members** | Subject-matter experts, data owners, front-line workers who know the process |
| **Finance representative** | Validates savings claim (required if financial benefit is part of the goal) |

A project without a named Process Owner cannot sustain its improvements. Surface this gap at charter time.

### Step 8 — Build the timeline

| Phase | Typical duration | Milestone |
|---|---|---|
| Define | 1–2 weeks | Charter signed; SIPOC complete; baseline measurement plan in place |
| Measure | 2–4 weeks | Baseline established; process map complete; measurement system validated |
| Analyze | 2–4 weeks | Root cause(s) proven with data |
| Improve | 4–8 weeks | Solution piloted; improvement quantified against baseline |
| Control | 2–4 weeks | Control plan in place; process handed off to Process Owner |

Timelines compress for urgent problems and expand for complex ones. The critical gate: **do not begin Improve before root cause is proven** (see best-practice `prove-root-cause-with-data-before-improving.md`).

### Step 9 — Identify risks and constraints

Write at least two: one that could slow data collection, one that could block the solution. A charter with no risks listed is a sign the team hasn't thought it through.

### Step 10 — Get the sponsor's signature

A charter without a sponsor signature is a wish list. The sponsor signature signals:
- Resources (people's time, data access) are available.
- The scope is agreed.
- The sponsor will remove obstacles.

## Charter-quality checklist

Before handing to the sponsor:

- [ ] Problem statement contains a number that proves the problem is real
- [ ] Goal statement is SMART: specific metric, quantified target, deadline
- [ ] At least one CTQ with a measurable spec is named
- [ ] SIPOC boundaries: start step and end step explicitly written
- [ ] Baseline metric: value, unit, sample size, measurement method
- [ ] Team table: sponsor, project lead, process owner all named
- [ ] Timeline: all 5 DMAIC phases have a target date
- [ ] Risks: at least two identified
- [ ] In-scope / out-of-scope written down
- [ ] Sponsor has reviewed and signed (or a sign-off date is scheduled)

## Anti-patterns this skill flags

- **Problem statement that is really a solution** — "We need a new ticketing system" is a solution; "ticket-resolution time is 8 days vs. a 3-day SLA" is a problem.
- **Goal without a baseline** — you cannot claim improvement without before/after.
- **Scope that covers the whole company** — a DMAIC charter scopes one process. If the answer to "what process?" is "everything," break it down.
- **No Process Owner** — improvements without an owner regress. If no one owns the process, name that as a risk.
- **Team without a finance representative when savings are claimed** — unvalidated savings numbers get challenged at the close gate.
- **Starting the Measure phase without a signed charter** — the sponsor has not committed, and you'll be doing rework when they redirect you.

## See also

- Template: [`../../templates/dmaic-project-charter.md`](../../templates/dmaic-project-charter.md) — the artifact this skill populates
- Template: [`../../templates/sipoc.md`](../../templates/sipoc.md) — Step 5 above
- Skill: [`../process-mapping/SKILL.md`](../process-mapping/SKILL.md) — Measure-phase process mapping; follows the charter
- Skill: [`../root-cause-analysis/SKILL.md`](../root-cause-analysis/SKILL.md) — Analyze phase; requires a charter-defined CTQ as input
- Best-practice: [`../../best-practices/measure-the-baseline-before-you-change-anything.md`](../../best-practices/measure-the-baseline-before-you-change-anything.md)
- Best-practice: [`../../best-practices/prove-root-cause-with-data-before-improving.md`](../../best-practices/prove-root-cause-with-data-before-improving.md)
