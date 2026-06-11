---
name: pt-billing-units-and-denials
description: "Code PT visits correctly and prevent denials — apply the 8-minute rule to timed minutes for billable units, code forward from documented medical necessity, cluster denials by reason code to their origin, and fix the cause at its source."
---

# PT Billing, Units & Denials

**Purpose:** protect reimbursement by coding from documented medical necessity, applying the
8-minute rule correctly, and preventing denials at the point they originate rather than reworking
claims at the back end.

> **Compliance note:** the 8-minute rule, therapy threshold/KX modifier, CPT codes, and payer
> policies change and vary. Treat all specifics below as `[verify against current CMS/payer policy
> and a certified coder]`.

---

## Steps

### 1. Code forward from documentation, never backward from a target

The documented, medically necessary, delivered care determines the code. Working backward from a
desired reimbursement to a code is fraud risk. If the documentation doesn't support the code, the fix
is the documentation (or the care), not the code.

### 2. Apply the 8-minute rule to timed minutes

Billable units for timed CPT codes follow total timed treatment minutes. Use
[`../../scripts/pt_calc.py`](../../scripts/pt_calc.py) `eight_minute_rule_units`:

| Total timed minutes | Billable units (Medicare 8-minute rule) |
|---|---|
| 8–22 | 1 |
| 23–37 | 2 |
| 38–52 | 3 |
| 53–67 | 4 |

A unit claimed without the documented minute basis is a denial and an audit exposure. (Some
commercial payers use rule-of-eights/AMA variants — verify per payer.)

### 3. Cluster denials by reason code to their origin

| Denial cluster | Usual origin | Fix at the source |
|---|---|---|
| Medical necessity | Documentation | Necessity/skilled-service note (documentation skill) |
| Units / 8-minute rule | Timed-minute recording | Record minutes at point of care |
| Authorization | Front desk | Auth verification before the visit |
| Modifier (KX / threshold) | Coding/documentation | Threshold tracking + attestation documentation |

### 4. Apply threshold/KX correctly

When cumulative therapy passes the threshold, the KX modifier attests continued medical necessity —
and requires the documentation to back it. Track cumulative amounts so it's applied on time.

### 5. Analyze payer performance

Net collection per visit by payer, underpayment vs. contract, and denial patterns — to target
contract and workflow levers.

---

## Output

A denial analysis with root-cause fixes, a units review, and a payer reimbursement analysis. Use the
[`../../templates/denial-prevention-checklist.md`](../../templates/denial-prevention-checklist.md).
