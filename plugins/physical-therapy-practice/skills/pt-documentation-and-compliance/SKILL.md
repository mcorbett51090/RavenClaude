---
name: pt-documentation-and-compliance
description: "Build defensible PT documentation and a compliant plan of care — establish medical necessity and skilled service in every note, record the timed-minute basis for units, get certification/recert timing right, and assess audit readiness."
---

# PT Documentation & Compliance

**Purpose:** make every note and plan of care defensible evidence of medically necessary, skilled
care — so delivered services survive audit and convert to reimbursement instead of denial.

> **Compliance note:** Medicare/CPT/payer rules change and vary. Treat the specifics below as
> `[verify against current CMS/payer policy and a certified coder/compliance professional]`.

---

## Steps

### 1. Establish the four elements in every note

Each treatment note should make these defensible:

| Element | What it proves |
|---|---|
| Skilled service | Why a licensed therapist (not an aide or HEP) was required |
| Medical necessity | Why the care was needed for this condition now |
| Progress toward goals | Movement against the measurable POC goals |
| Timed-minute basis | The total timed minutes that justify the billed units |

A note missing any of these turns a delivered service into a denial.

### 2. Write a defensible plan of care

The POC carries: measurable, functional goals; justified frequency and duration; the diagnosis and
necessity linkage; and correct certification/recertification timing. A vague POC ("continue
therapy") is an indefensible episode.

### 3. Record the timed-minute basis up front

For timed codes, the documented total timed minutes are what justify units under the 8-minute rule.
Record minutes as care happens; reconstructing them later is an audit red flag. Compute the unit
basis with [`../../scripts/pt_calc.py`](../../scripts/pt_calc.py) `eight_minute_rule_units`.

### 4. Get certification/recert timing right

Initial certification and recertification have timing requirements; a lapsed certification can
invalidate otherwise-good care. Track the dates as a compliance control.

### 5. Assess audit readiness

Sample notes against the four elements, the unit basis, and certification timing. Prioritize the
highest-risk gaps (units without minutes, necessity not established, lapsed certs).

---

## Output

A documentation standard, a plan-of-care review, and an audit-readiness assessment. Use the
[`../../templates/plan-of-care-template.md`](../../templates/plan-of-care-template.md). Route the
unit-to-claim mapping to the billing skill.
