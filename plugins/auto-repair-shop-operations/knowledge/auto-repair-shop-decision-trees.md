# Auto-Repair Shop — Decision Trees

> Reference decision trees for the `auto-repair-shop-operations` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Operations and financial decision-support — not legal, tax, or OEM-warranty advice.** Anything touching a labor rate, a labor-guide time, a parts-margin figure, a productivity benchmark, or a state estimate-authorization rule is `[verify-at-use]` — confirm against the shop's own numbers, the current labor guide, or the local statute before acting. No customer PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated benchmarks and figures live in [`auto-repair-shop-reference-2026.md`](auto-repair-shop-reference-2026.md)._

---

## Decision Tree: price a job (labor + parts matrix)

```mermaid
flowchart TD
    A[Job to price] --> B{Complaint verified<br/>and diagnostic authorized?}
    B -- no --> C[Verify complaint + authorize diagnostic FIRST<br/>state disclosure rule verify-at-use]
    B -- yes --> D[Labor: labor-guide hours x shop rate]
    D --> E{Warranty / fleet / discount<br/>applies to this job?}
    E -- yes --> F[Apply the correct rate;<br/>protect the effective labor rate]
    E -- no --> G[Full posted labor]
    F --> H[Parts: cost x matrix tier]
    G --> H
    H --> I{DVI evidence attached<br/>to each recommended line?}
    I -- no --> J[Add photo/measurement<br/>before presenting]
    I -- yes --> K[Present sell-now vs sell-later,<br/>ranked by safety/failure risk]
```

**Rule:** never price before the complaint is verified and the diagnostic authorized. Labor = labor-guide hours x the shop rate (`[verify-at-use]` on both), parts = cost x the matrix tier — not an off-the-cuff markup or discount. Present with DVI evidence, triaged sell-now vs sell-later.

---

## Decision Tree: comeback root-cause triage

```mermaid
flowchart TD
    A[Vehicle returned — comeback] --> B{Same concern as the original RO?}
    B -- "no, unrelated / new" --> C[No-fault: new RO;<br/>check write-up clarity]
    B -- "yes, same concern" --> D{Root cause?}
    D -- "wrong diagnosis" --> E[Fix diagnostic process,<br/>tooling, info access]
    D -- "poor workmanship" --> F[Skill/dispatch match + QC step;<br/>tech owns the rework, billed at zero]
    D -- "part failed" --> G[Supplier / matrix-tier decision;<br/>warranty the part]
    D -- "repair incomplete" --> H[Multi-point verification<br/>before closeout]
    E --> I[Log cause; fix the PROCESS,<br/>not just this car]
    F --> I
    G --> I
    H --> I
```

**Rule:** a comeback is triaged by **root cause**, and the fix is the process that produced it — not just re-doing the car. Rework is billed at zero and taxes the effective labor rate, so the tech who caused a workmanship comeback owns the rework. Group comebacks by cause; don't chase them one at a time.

---

## Decision Tree: declined-work follow-up

```mermaid
flowchart TD
    A[Recommended work declined] --> B{Urgency of the declined item}
    B -- "safety / failure imminent" --> C[Re-present now:<br/>explain the risk, offer to schedule]
    B -- "wear item, life remaining" --> D[Log as dated deferred service<br/>with estimated part life]
    B -- "customer deferred on price" --> E[Log; offer financing / phased plan<br/>at next contact]
    C --> F[Deferred-service list = warmest lead]
    D --> F
    E --> F
    F --> G{Next contact due?}
    G -- yes --> H[Recontact on cadence;<br/>re-present at next visit]
    G -- no --> I[Hold on the recall list<br/>until due]
```

**Rule:** a decline is logged, never forgotten. Rank by urgency and part life, set a recontact cadence, and re-present at the next visit — the deferred-service list is the shop's warmest source of future car count. Honest triage (safety now, wear later) is the ethical form of upsell.

---

## Decision Tree: tech pay — flat-rate vs hourly

```mermaid
flowchart TD
    A[Choosing / reviewing the pay plan] --> B{What behavior does the shop need?}
    B -- "high-volume, guide-timed work;<br/>reward speed" --> C{Steady car count to<br/>keep techs flagging hours?}
    C -- yes --> D[Flat-rate / flag-time can work;<br/>monitor comeback + quality]
    C -- no --> E[Flat-rate starves techs on slow days<br/>-> turnover risk; consider hourly+bonus]
    B -- "diagnostic-heavy, low-volume,<br/>or trust/quality priority" --> F[Hourly or hourly + efficiency bonus;<br/>protects against corner-cutting]
    D --> G{Comeback rate rising<br/>under flat-rate?}
    G -- yes --> H[Add QC gate + comeback ownership;<br/>rework billed at zero]
    G -- no --> I[Keep plan; track efficiency + proficiency]
    E --> I
    F --> I
```

**Rule:** the pay plan is chosen for the **behavior the shop needs** and the **car count it can guarantee** — flat-rate rewards speed but needs volume and a quality gate (it can incentivize comebacks); hourly protects quality and diagnostic work but must still be measured on efficiency. Effective-labor-rate and pay-plan strategy are the shop lead's call; benchmarks `[verify-at-use]`.

---

## See also

- [`auto-repair-shop-reference-2026.md`](auto-repair-shop-reference-2026.md) — dated labor-rate norms, productivity benchmarks, and the parts-GP matrix (verify-at-use).
- Skills: [`../skills/effective-labor-rate-and-gross-profit/SKILL.md`](../skills/effective-labor-rate-and-gross-profit/SKILL.md), [`../skills/estimate-and-dvi-workflow/SKILL.md`](../skills/estimate-and-dvi-workflow/SKILL.md), [`../skills/technician-productivity-and-efficiency/SKILL.md`](../skills/technician-productivity-and-efficiency/SKILL.md), [`../skills/ro-lifecycle-and-comeback-control/SKILL.md`](../skills/ro-lifecycle-and-comeback-control/SKILL.md).
