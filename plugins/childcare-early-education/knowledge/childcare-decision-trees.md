# Childcare / Early-Education — Decision Trees

> Reference decision trees for the `childcare-early-education` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Advisory operations knowledge, not legal, licensing, or financial advice.** Anything touching a ratio, group-size cap, staff qualification, subsidy rule, or licensing requirement is **state-specific and `[verify-at-use]`** — confirm against your current state licensing regulation and the funding agency before acting. No child or family PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated norms and program concepts live in [`childcare-reference-2026.md`](childcare-reference-2026.md)._

---

## Decision Tree: staff a room to ratio

```mermaid
flowchart TD
    A[Room needs staffing] --> B{Age group of the room}
    B --> C[Look up required child:staff ratio<br/>for that age — verify-at-use, state-specific]
    B --> D[Look up group-size cap<br/>for that age — verify-at-use, state-specific]
    C --> E{Enrolled children <= ratio x<br/>ratio-countable teachers?}
    D --> F{Enrolled children <=<br/>group-size cap?}
    E -- no --> G[Add a qualified teacher<br/>OR cap enrollment in this room]
    F -- no --> H[Split the group / open another room<br/>ratio alone will not fix group size]
    E -- yes --> I{Coverage holds at open,<br/>close, breaks, nap?}
    F -- yes --> I
    I -- no --> J[Schedule float / openers-closers<br/>to hold ratio all day]
    I -- yes --> K[Room is compliant —<br/>read cost vs revenue for this room]
```

**Rule:** ratio and group size are **two separate limits** — a room must satisfy both, by age, every moment of the day. Only **ratio-countable** (qualified, verified) staff count. Adding the child that crosses a ratio boundary adds a **whole teacher** — model the step, don't average it. All specific numbers are `[verify-at-use, state-specific]`.

---

## Decision Tree: enrollment / waitlist decision

```mermaid
flowchart TD
    A[Open or soon-open seat] --> B{Is there a waitlist<br/>for this age band?}
    B -- yes --> C[Convert the waitlist FIRST<br/>by desired start date]
    B -- no --> D{Where does the funnel leak?}
    D -- "few inquiries" --> E[Lead-gen / referral / visibility]
    D -- "inquiries not touring" --> F[Fix intake responsiveness<br/>+ tour scheduling friction]
    D -- "tours not enrolling" --> G{Is there a tour<br/>follow-up cadence?}
    G -- no --> H[Build the follow-up sequence:<br/>same-day -> decision-window -> ask]
    G -- yes --> I{Price objection<br/>vs fit/timing objection?}
    I -- "timing/fit" --> J[Waitlist for the right start;<br/>do not discount]
    I -- "price" --> K[Confirm no waitlist exists<br/>before discounting — else convert it]
    C --> L[Route the committed seat<br/>to its billing rail]
    H --> L
```

**Rule:** **work the waitlist and diagnose the funnel leak by stage before you discount tuition.** A discount on a seat someone was waiting for is margin given away. The tour leaks most often at **follow-up**, not at the tour itself.

---

## Decision Tree: tuition vs subsidy billing route

```mermaid
flowchart TD
    A[Committed family — how do we bill?] --> B{Family has a childcare<br/>subsidy authorization?}
    B -- no --> C[Private-pay tuition<br/>on the standard schedule]
    B -- yes --> D{Authorization covers<br/>full tuition?}
    D -- yes --> E{Program requires a<br/>parent fee / co-pay?}
    E -- yes --> F[Blended: bill subsidy on its driver<br/>+ collect the parent fee]
    E -- no --> G[Full subsidy: bill on the<br/>attendance/reporting driver]
    D -- "partial" --> H[Blended: subsidy portion<br/>+ private-pay balance + any co-pay]
    F --> I[Track authorization dates<br/>+ reconcile subsidy as A/R]
    G --> I
    H --> I
    C --> J[Standard receivables cadence]
```

**Rule:** decide the rail — **private / subsidy / blended** — deliberately, then **collect the parent fee/co-pay as seriously as private tuition**, **track the authorization** (it expires), and **bill on the program's payment driver** (often attendance). Subsidy is **accounts-receivable to reconcile**, not money that arrives. Every subsidy rule `[verify-at-use, state-specific]`.

---

## Decision Tree: licensing-readiness triage

```mermaid
flowchart TD
    A[Licensing visit ahead or self-audit] --> B{Walk the domains}
    B -- "ratios & group size" --> C{In ratio AND under group-size<br/>cap every moment, all rooms?}
    B -- "staff qualifications & files" --> D{Every ratio-countable adult<br/>qualified, background-checked, trained?}
    B -- "health & safety" --> E{Med/allergy, sanitation, emergency<br/>drills, environment current?}
    B -- "records & documentation" --> F{Immunization, enrollment,<br/>incident logs complete & current?}
    C -- no --> G[HIGHEST RISK — fix ratio/group first]
    D -- no --> H[Void ratio-countable headcount risk<br/>— close the file gaps]
    E -- no --> I[Remediate the specific hazard/record]
    F -- no --> J[Bring records current + set a daily cadence]
    C -- yes --> K[Domain clean]
    D -- yes --> K
    E -- yes --> K
    F -- yes --> K
    K --> L[Compliance is the resting state —<br/>maintain daily, not pre-visit]
```

**Rule:** triage the **licensing domains** by risk — **ratio/group-size gaps first** (they are the fastest citations and can be immediate), then staff-file gaps (which can void ratio-countable headcount), then health-safety and records. Compliance is **continuous**, not an inspection-day project. Every requirement `[verify-at-use, state-specific]`.

---

## See also

- [`childcare-reference-2026.md`](childcare-reference-2026.md) — dated ratio/group-size norms by age, CCDF/subsidy basics, licensing domains (verify-at-use, state-specific).
- Skills: [`../skills/staffing-to-ratio-scheduling/SKILL.md`](../skills/staffing-to-ratio-scheduling/SKILL.md), [`../skills/enrollment-and-waitlist-management/SKILL.md`](../skills/enrollment-and-waitlist-management/SKILL.md), [`../skills/tuition-and-subsidy-billing/SKILL.md`](../skills/tuition-and-subsidy-billing/SKILL.md), [`../skills/ratios-and-licensing-compliance/SKILL.md`](../skills/ratios-and-licensing-compliance/SKILL.md).
