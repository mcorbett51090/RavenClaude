# Higher-Education Administration — Decision Trees

> Reference decision trees for the `higher-education-administration` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Advisory operations knowledge, not legal, financial-aid-compliance, or academic-policy advice.** Anything touching a funnel benchmark, discount-rate norm, aid rule, or retention/persistence metric definition is `[verify-at-use]` — confirm against the institution's own IR definitions, the aid office, and the accreditor before acting. FERPA-aware: cohorts and policy only, no student PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated benchmarks and metric definitions live in [`higher-ed-reference-2026.md`](higher-ed-reference-2026.md)._

---

## Decision Tree: yield / melt intervention

```mermaid
flowchart TD
    A[Class softer than target] --> B{Where in the funnel?}
    B -- "admits enrolling below plan<br/>(yield gap)" --> C{Aid competitive vs<br/>peer offers? [verify-at-use]}
    C -- no --> D[Aid-leverage move on the<br/>responsive admit segment]
    C -- yes --> E{Yield gap by segment<br/>or across the board?}
    E -- "segment" --> F[Targeted recruitment / touch<br/>on the leaking segment]
    E -- "across the board" --> G[Fit / timing / competitiveness<br/>review of the whole offer]
    B -- "deposits melting before<br/>census (melt gap)" --> H{Melt-season touch<br/>in place?}
    H -- no --> I[Fund a melt-season<br/>communication + support plan]
    H -- yes --> J[Segment melt by cause<br/>aid, transfer, fit, logistics]
```

**Rule:** defend the yield you've earned before buying more top-of-funnel. A melt-season intervention is almost always cheaper per net student than replacing the loss with new inquiries — yield is cheaper to defend than to replace. Aid moves target the segment whose decision actually changes (`[verify-at-use]`).

---

## Decision Tree: discount-rate / aid-leverage decision

```mermaid
flowchart TD
    A[Considering an aid / discount move] --> B{Modeled net tuition revenue,<br/>not gross headcount?}
    B -- no --> C[Build the net-revenue model FIRST<br/>gross - institutional aid]
    B -- yes --> D{Does the dollar change<br/>an enrollment decision<br/>at the margin?}
    D -- "no — student enrolls anyway" --> E[Do not spend it there<br/>it is discount, not leverage]
    D -- "yes — responsive segment" --> F{Net revenue still positive<br/>at the new discount rate?}
    F -- no --> G[Bigger class, less revenue<br/>hold or re-target the aid]
    F -- yes --> H[Deploy as leverage;<br/>state the break-even yield]
```

**Rule:** the discount rate is a strategy, not an accident. Model net tuition revenue at each scenario, spend aid only where it does yield work at the margin, and never let the rate drift upward package-by-package. State the break-even yield before committing (`[verify-at-use]`).

---

## Decision Tree: at-risk student triage

```mermaid
flowchart TD
    A[Cohort with at-risk signals] --> B{Group by risk signal<br/>— no PII, cohort-level}
    B -- "early-alert flag +<br/>gateway-course failing" --> C{On the edge<br/>this term?}
    C -- yes --> D[Highest-leverage first touch NOW<br/>advising + course support]
    C -- no --> E[Structured outreach<br/>this term]
    B -- "aid gap / financial hold" --> F[Route to aid + registrar;<br/>clear the friction]
    B -- "flag without cause /<br/>false positive" --> G[Monitor, do not spend<br/>the intervention]
    D --> H[Fix the PROCESS the cluster<br/>points to, not one student]
    E --> H
    F --> H
```

**Rule:** retention is an early-alert problem — triage the cohort by *leverage*, not by alarm, and put the first touch where it changes an outcome. A recurring at-risk cluster is a process signal (a gateway course, an aid gap, an onboarding gap), not a series of individual bad-luck cases. Metric definitions are `[verify-at-use]`; no student PII.

---

## Decision Tree: enrollment-vs-retention lever choice

```mermaid
flowchart TD
    A[Where to invest next year?] --> B{Marginal cost per<br/>net student added}
    B --> C[Cost to YIELD one more<br/>new student -> enrollment lever]
    B --> D[Cost to RETAIN one more<br/>current student -> retention lever]
    C --> E{Which is cheaper per<br/>net-revenue dollar?}
    D --> E
    E -- "retention cheaper" --> F[Invest in early-alert +<br/>gateway-course support]
    E -- "enrollment cheaper" --> G[Invest in funnel /<br/>aid leverage]
    E -- "both constrained" --> H{Is the retention loss an<br/>enrollment-quality signal?}
    H -- yes --> I[Fix upstream: yield the<br/>right-fit class]
    H -- no --> J[Split by net-revenue<br/>marginal return]
```

**Rule:** enrollment and retention are two levers on the *same* net-tuition-revenue outcome — compare the marginal cost of a yielded student against a retained one before allocating. A retained student usually costs less than replacing them, but a retention loss that traces to a mis-yielded class is an enrollment-quality problem to fix upstream (`[verify-at-use]`).

---

## See also

- [`higher-ed-reference-2026.md`](higher-ed-reference-2026.md) — dated benchmarks + metric definitions (verify-at-use).
- Skills: [`../skills/enrollment-funnel-and-yield/SKILL.md`](../skills/enrollment-funnel-and-yield/SKILL.md), [`../skills/financial-aid-and-discount-rate/SKILL.md`](../skills/financial-aid-and-discount-rate/SKILL.md), [`../skills/retention-and-student-success/SKILL.md`](../skills/retention-and-student-success/SKILL.md), [`../skills/registrar-and-academic-operations/SKILL.md`](../skills/registrar-and-academic-operations/SKILL.md).
