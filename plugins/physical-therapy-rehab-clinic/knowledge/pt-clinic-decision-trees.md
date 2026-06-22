# Outpatient PT / Rehab Clinic — Decision Trees

> Reference decision trees for the `physical-therapy-rehab-clinic` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Advisory only — not medical, legal, or billing advice.** Every regulatory / payor specific (the 8-minute-rule variant, the therapy threshold, certification windows, denial codes) is **`[verify-at-use]`** against the current payor/CMS source. Dated figures live in [`pt-clinic-reference-2026.md`](pt-clinic-reference-2026.md). No patient PII.
>
> _Last reviewed: 2026-06-22 by `claude`. Principles are durable; specific dollar figures and payor rules are volatile — re-verify before quoting._

---

## Decision Tree: 8-minute-rule unit calculation

```mermaid
flowchart TD
    A[Service delivered] --> B{Timed or untimed code?}
    B -- "untimed / service-based" --> C[1 unit per session<br/>regardless of minutes]
    B -- "timed / time-based" --> D[Sum ALL timed minutes]
    D --> E{Single timed service<br/>≥ 8 minutes?}
    E -- no --> F[0 units for that service<br/>too few minutes]
    E -- yes --> G[Map cumulative minutes to units<br/>8–22=1, 23–37=2, 38–52=3, 53–67=4, +15=+1]
    G --> H{Multiple timed codes?}
    H -- no --> I[Assign units to the one code]
    H -- yes --> J[Total units, then allocate<br/>by largest remaining minutes]
    J --> K{Payor uses CMS cumulative<br/>or per-service rule of eights?}
    K -- "CMS / Medicare" --> L[Cumulative total — VERIFY-AT-USE]
    K -- "some commercial" --> M[Per-service eights — VERIFY-AT-USE]
```

**Rule:** untimed = 1 unit/session; timed = 15-minute units under the 8-minute rule (≥8 min for the first unit, cumulative-minute brackets thereafter). Mixed timed codes are totaled then allocated. **The payor's variant (CMS cumulative vs per-service) decides edge cases — `[verify-at-use]`.** Brackets are the standard CMS pattern; confirm the current bracket and variant against the payor.

---

## Decision Tree: documentation defensibility / medical necessity

```mermaid
flowchart TD
    A[Daily note / encounter] --> B{Does it state WHY skilled<br/>therapy was needed TODAY?}
    B -- no --> C[Not defensible<br/>add medical-necessity reasoning]
    B -- yes --> D{Does it read as SKILLED?<br/>decision-making, progression, cueing}
    D -- "no — boilerplate<br/>'tolerated well'" --> E[Not defensible<br/>name the skilled clinical work]
    D -- yes --> F{Does it trace to a<br/>plan-of-care goal?}
    F -- no --> G[Orphan note<br/>tie to a POC goal]
    F -- yes --> H{Objective + functional<br/>change recorded?}
    H -- no --> I[Add measurable functional outcome]
    H -- yes --> J{Signed + dated per<br/>signature rule? VERIFY-AT-USE}
    J -- no --> K[Obtain signature<br/>check requirement]
    J -- yes --> L[Defensible — proceed]
```

**Rule:** a defensible note establishes medical necessity *this visit*, reads as skilled (not boilerplate), traces to a POC goal, records objective functional change, and is signed per the applicable rule. **Signature/content rules are `[verify-at-use]`.** Defensible notes beat appeals.

---

## Decision Tree: plan certification vs recertification timing

```mermaid
flowchart TD
    A[Plan of care status] --> B{New episode or<br/>existing plan?}
    B -- "new" --> C{Initial certification<br/>obtained within the window?}
    C -- no --> D[Risk: visits under an<br/>uncertified plan — certify now]
    C -- yes --> E[Plan active<br/>start the recert clock]
    B -- "existing" --> F{Certification period<br/>nearing its end OR plan<br/>materially changed?}
    F -- no --> G[Continue under current cert]
    F -- "nearing end" --> H[Recertify BEFORE it lapses<br/>book the visit + signature]
    F -- "plan changed" --> I[Revise + recertify the plan]
    H --> J{Recert obtained in time?}
    J -- no --> K[Lapse risk — visits may deny<br/>VERIFY-AT-USE timing]
    J -- yes --> E
```

**Rule:** certify the new plan within its required window; track the recertification clock and recertify *before* it lapses or when the plan changes materially. **Certification windows and recert timing are `[verify-at-use]`** (payor / CMS, change annually). Operations owns the re-book; compliance owns the deadline.

---

## Decision Tree: denial triage

```mermaid
flowchart TD
    A[Claim denied] --> B{What does the<br/>denial reason say?}
    B -- "units / frequency / cap" --> C{Recount under 8-min rule<br/>+ check payor variant}
    C -- "miscount" --> D[Re-bill corrected units]
    C -- "cap / auth" --> E[Verify auth + visit cap<br/>VERIFY-AT-USE]
    B -- "modifier / NCCI edit" --> F[Match GP/KX/59 to<br/>discipline / threshold / distinct service]
    B -- "medical necessity" --> G{Does the note justify<br/>skilled care?}
    G -- no --> H[Documentation fix<br/>not appeal language]
    G -- yes --> I[Appeal WITH the note<br/>as evidence]
    B -- "eligibility / auth" --> J[Front-end miss<br/>verify, then re-submit]
```

**Rule:** map the denial reason to its root cause — units (8-minute-rule variant / cap), modifier/NCCI, medical necessity (a documentation fix, not appeal prose), or eligibility/auth (a front-end miss). **Denial codes and appeal windows are `[verify-at-use]` per payor.** Prevent at the front end; appeal with the documentation that already exists.

---

## See also

- [`pt-clinic-reference-2026.md`](pt-clinic-reference-2026.md) — dated reference (timed-vs-untimed CPT, KX/threshold concept, common payor rules); every figure carries a source placeholder + retrieval date + verify-at-use.
- Skills: [`../skills/therapy-billing-and-units/SKILL.md`](../skills/therapy-billing-and-units/SKILL.md), [`../skills/defensible-documentation/SKILL.md`](../skills/defensible-documentation/SKILL.md), [`../skills/plan-of-care-management/SKILL.md`](../skills/plan-of-care-management/SKILL.md), [`../skills/denial-prevention-and-appeals/SKILL.md`](../skills/denial-prevention-and-appeals/SKILL.md), [`../skills/schedule-and-capacity-planning/SKILL.md`](../skills/schedule-and-capacity-planning/SKILL.md).
