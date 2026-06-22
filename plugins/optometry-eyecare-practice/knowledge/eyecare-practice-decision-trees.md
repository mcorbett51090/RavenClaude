# Optometry / Eye-Care Practice — Decision Trees

> Reference decision trees for the `optometry-eyecare-practice` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Advisory operations knowledge, not medical, legal, coding, or billing advice.** Anything touching a payor rule, CPT code, benefit structure, or clinical protocol is `[verify-at-use]` — confirm against the payor/clearinghouse/clinical protocol before acting. No PII/PHI.
>
> _Last reviewed: 2026-06-22 by `claude`. Principles are durable; dated benchmarks and concepts live in [`eyecare-practice-reference-2026.md`](eyecare-practice-reference-2026.md)._

---

## Decision Tree: route this visit to medical or vision-plan billing?

```mermaid
flowchart TD
    A[Eye-care visit to bill] --> B{Chief complaint /<br/>reason for visit}
    B -- "routine refraction, well-vision,<br/>'new glasses'" --> C[Vision plan<br/>routine exam + materials allowance]
    B -- "medical complaint or dx<br/>(dry eye, diabetic, glaucoma,<br/>foreign body, sudden change)" --> D{Documented medical<br/>findings + plan?}
    D -- no --> E[Document medical necessity FIRST<br/>then bill medical]
    D -- yes --> F[Medical insurance<br/>E/M or eye-exam code to the dx]
    B -- "both components present" --> G{Payor rules allow split?<br/>[verify-at-use]}
    G -- yes --> H[Split: medical for the condition,<br/>vision for refraction/materials]
    G -- no --> I[Route to the dominant<br/>reason for the visit]
```

**Rule:** route on the **chief complaint and what the visit addressed**, never on which payor is convenient. A medical claim requires documented medical necessity. Split only where the specific payor's rules allow it — `[verify-at-use]`.

---

## Decision Tree: recall / recare cadence by exam type

```mermaid
flowchart TD
    A[Patient seen — set the recall] --> B{Exam type}
    B -- "routine refraction,<br/>healthy adult" --> C[Routine recall interval<br/>per clinical protocol — verify-at-use]
    B -- "contact-lens wearer" --> D[CL recheck interval<br/>+ annual supply/eval]
    B -- "medical follow-up<br/>(diabetic, glaucoma,<br/>dry eye mgmt)" --> E[Shorter, condition-driven<br/>medical follow-up interval]
    B -- "pediatric / at-risk" --> F[Protocol-driven<br/>pediatric interval]
    C --> G[Put on recall list<br/>= the schedule-filler]
    D --> G
    E --> G
    F --> G
```

**Rule:** the recall interval is set by **exam type and clinical protocol** (treat all interval values as `[verify-at-use]`), and the recall list — not walk-ins — is the primary schedule-filler. Recall drives the schedule.

---

## Decision Tree: optical capture-rate improvement

```mermaid
flowchart TD
    A[Capture rate below target] --> B{Where does the funnel leak?}
    B -- "exams not converting<br/>to Rx-in-our-optical" --> C{Is there a warm<br/>exam-to-optician handoff?}
    C -- no --> D[Build a warm handoff<br/>into exam-exit workflow]
    C -- yes --> E{Quoting accurately vs<br/>the patient's vision plan?}
    E -- no --> F[Train formulary literacy:<br/>covered vs upgrade — verify-at-use]
    E -- yes --> G{Frame board / lens menu<br/>matching demand?}
    G -- no --> H[Re-stock to turns;<br/>cut dead segments]
    G -- yes --> I[Look at lab turnaround<br/>+ remake rate]
    B -- "Rx written but patient<br/>price-shocked" --> F
```

**Rule:** capture is won at the **handoff**, not the register. Diagnose the funnel in order — handoff, then quote accuracy against the plan, then board/menu fit, then lab. Capture rate is the optical profit lever, not frame markup.

---

## Decision Tree: claim denial triage

```mermaid
flowchart TD
    A[Wave of denied eye-exam claims] --> B{Group by cause}
    B -- "eligibility / no benefit" --> C[Fix pre-visit eligibility step<br/>check medical AND vision at scheduling]
    B -- "coding / medical necessity" --> D[Code to the encounter;<br/>document necessity — verify-at-use]
    B -- "wrong payor routed<br/>(medical vs vision)" --> E[Fix the routing decision<br/>at the front desk]
    B -- "timely filing" --> F[Submission cadence + worklist]
    C --> G[Fix the PROCESS that<br/>produced the cluster, not the claim]
    D --> G
    E --> G
    F --> G
```

**Rule:** triage denials by **cause cluster**, then fix the process that produced the group — not one claim at a time. The biggest preventable causes (eligibility, wrong-payor routing) are front-desk process defects. Specific payor denial codes are `[verify-at-use]`.

---

## See also

- [`eyecare-practice-reference-2026.md`](eyecare-practice-reference-2026.md) — dated concepts + benchmarks (verify-at-use).
- Skills: [`../skills/medical-vs-vision-billing/SKILL.md`](../skills/medical-vs-vision-billing/SKILL.md), [`../skills/eligibility-and-claims/SKILL.md`](../skills/eligibility-and-claims/SKILL.md), [`../skills/optical-capture-and-dispensary/SKILL.md`](../skills/optical-capture-and-dispensary/SKILL.md), [`../skills/schedule-and-recall-management/SKILL.md`](../skills/schedule-and-recall-management/SKILL.md).
