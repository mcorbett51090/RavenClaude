# ITSM — Decision Trees

_Decision trees for routing an issue and classifying a change. Traverse the relevant tree top-to-bottom before acting. Principle-stable (ITIL 4 structure); last reviewed: 2026-06-19._

## Decision Tree: Incident, problem, request, or change?

```mermaid
graph TD
  A[An issue or ask arrives] --> B{Is a service degraded or down?}
  B -- No --> C{Is it a standard, pre-approved ask access/equipment/how-to?}
  C -- Yes --> D[SERVICE REQUEST - fulfill from the catalog]
  C -- No, it's a desired alteration to a service/CI --> E[CHANGE - route to change enablement]
  B -- Yes --> F{Broad impact / critical service / high urgency?}
  F -- Yes --> G[MAJOR INCIDENT - declare command: commander + comms]
  F -- No --> H[INCIDENT - restore service fast, workaround counts]
  H --> I{Has this recurred or is the cause unknown and worth removing?}
  I -- Yes --> J[Also open a PROBLEM - RCA + known error, drive permanent fix]
  I -- No --> K[Close on restoration]
  J --> L{Permanent fix alters a service/CI?}
  L -- Yes --> E
```

_The key split (§2 #1): restoring service now = incident; removing the cause = problem. They run in parallel for a recurring issue._

## Decision Tree: Which change type?

```mermaid
graph TD
  A[A change is needed] --> B{Urgent - fixing/preventing a major incident now?}
  B -- Yes --> C[EMERGENCY change - expedited path/ECAB + retrospective review]
  B -- No --> D{Low-risk, repeatable, well-understood?}
  D -- Yes --> E[STANDARD change - pre-authorized model, NO CAB]
  D -- No --> F{Assess: impact x likelihood x reversibility}
  F -- Higher risk / novel --> G[NORMAL change - assess + CAB authorization]
  F -- Lower risk --> H[NORMAL change - assess + delegated authorization, no full CAB]
```

_The lever for de-bottlenecking (§2 #2, #3): move repeatable changes into standard models so the CAB only sees genuine, novel risk._

## Decision Tree: Is this ITSM's or observability-sre's?

```mermaid
graph TD
  A[A production reliability event] --> B{Need ITIL records, comms, CAB, SLA accounting, CMDB?}
  B -- Yes --> C[ITSM owns the operating-model layer: the incident/problem/change records + comms + SLA]
  A --> D{Need engineering reliability: SLOs/error budgets, telemetry, blameless eng postmortem, fault analysis?}
  D -- Yes --> E[observability-sre owns the engineering practice]
  C --> F[Most prod outages are BOTH -> coordinate, do not duplicate]
  E --> F
```

_This team owns the ITIL/ITSM operating model; `observability-sre` owns the engineering reliability practice. A real outage is usually both at once._
