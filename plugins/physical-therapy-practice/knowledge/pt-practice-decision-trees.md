# PT practice decision trees + capability map

Decision support for the `physical-therapy-practice` specialists. Traverse top-to-bottom; pick the
smallest-scope leaf that fits. Resolve every decision to plan-of-care adherence and defensible,
medically-necessary, documented care.

> **Compliance note:** all Medicare/CPT/payer specifics below are `[verify against current CMS/payer
> policy and a certified coder/compliance professional]`.

---

## 1. 8-minute rule — "how many units do these timed minutes bill?"

```
Total timed treatment minutes (Medicare 8-minute rule):
├─ < 8    → 0 units
├─ 8–22   → 1 unit
├─ 23–37  → 2 units
├─ 38–52  → 3 units
├─ 53–67  → 4 units
└─ +15 per additional unit thereafter
Untimed (service-based) codes bill 1 unit per service regardless of time.
Commercial payers may use rule-of-eights / AMA variant → verify per payer.
```

Rule: no unit without the documented minute basis behind it.

## 2. Denial root cause — "where did this denial originate?"

```
What is the denial reason code?
├─ Medical necessity        → documentation gap → necessity/skilled-service note
├─ Units / time             → timed minutes not recorded → record at point of care
├─ Authorization            → front-desk gap → verify auth before the visit
├─ Modifier (KX/threshold)  → threshold not tracked / attestation missing → track + document
└─ Coding (wrong CPT)       → coded from target not documentation → code forward from the note
```

## 3. Cancellation driver — "why did this visit get missed?"

```
Segment the cancellation:
├─ "Forgot"                 → reminder cadence + confirmation
├─ Scheduling friction      → easier rebooking, standing appointments
├─ "Felt better" mid-episode→ clinical-engagement gap → frame remaining visits to the functional goal
├─ Access (transport/cost)  → telehealth where appropriate, financial counseling
└─ Clinician-specific cluster→ relationship/engagement → coaching, reassignment
```

Rule: a missed visit is a broken episode of care first; the revenue loss is downstream.

## 4. Medical necessity — "is this defensibly necessary skilled care?"

```
Can the note establish all of:
├─ Skilled service (needed a licensed therapist, not an aide/HEP)?
├─ Medical necessity (needed for this condition now)?
├─ Progress toward measurable POC goals?
└─ The timed-minute basis for the units?
If any "no" → the gap is the fix BEFORE billing; do not code around a documentation gap.
```

## 5. P&L lever — "where does clinic margin actually move?"

```
Pull in this order (highest leverage first):
├─ Plan-of-care adherence (complete episodes = the multi-visit revenue + clinical result)
├─ Cancellation/no-show rate (recovered delivered visits)
├─ Net collection per visit (denials, coding accuracy, payer mix)
├─ Units per visit (only within medically-necessary, documented bounds — never push past)
└─ Labor cost / clinician productivity (without over-utilization audit risk)
```

---

## 2026 capability map (verify before quoting specifics)

- **Medicare 8-minute rule & therapy threshold/KX** — stable in structure but threshold dollar
  amounts and policy update annually; `[unverified — confirm current-year CMS amounts]`.
- **MIPS / quality reporting** — applicability and measures change yearly; verify current
  participation requirements. `[unverified — training knowledge]`
- **Telehealth PT coverage** — payer and Medicare coverage of remote therapeutic services has
  shifted; verify current coverage before designing telehealth into the flow. `[unverified]`
- **EMR/scheduling platforms** — the flow, adherence, and units logic here is platform-independent;
  treat any platform-feature claim as `[unverified]` until checked.

> Per the core Claim-Grounding protocol, date and verify any Medicare-, CPT-, or payer-specific
> claim before it gates a decision. This is decision-support, not coding/compliance/clinical advice.
