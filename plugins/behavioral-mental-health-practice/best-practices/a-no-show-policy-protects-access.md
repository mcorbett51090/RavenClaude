# A no-show policy protects access

**Status:** Pattern
**Domain:** Access management and scheduling
**Applies to:** `behavioral-mental-health-practice`

---

## Why this exists

A no-show in behavioral health is not just a lost session — it is a time slot that could have gone
to a patient on the waitlist. Practices with chronic no-show problems have long waitlists and half-
full schedules simultaneously: an access paradox caused by poor policy design or inconsistent
enforcement, not genuine capacity shortage.

A clearly communicated, consistently enforced no-show policy does two things: it signals to patients
that their slot has real value (belonging to someone on the waitlist), and it protects the practice's
effective capacity — defined as `slots × providers × show-rate`. A 10-point improvement in show rate
from 75% to 85% in a 10-provider practice is the equivalent of adding a full provider's worth of
capacity without adding a single provider.

## How to apply

**Do:**

- Calculate the current no-show rate using `scripts/bh_calc.py no-show-rate` and model the revenue
  and access impact of a 5–10 point improvement.
- State the policy in the intake packet's financial agreement and get a signature at intake.
- Communicate the policy verbally at each scheduling contact.
- Send reminders at 72 hours and 24 hours before each appointment (not just one the day before).
- Enforce the policy consistently — inconsistent enforcement is worse than no policy because it
  signals that the rule is negotiable.
- Build a same-day fill protocol: when a cancellation or no-show occurs, contact the top 3–5 active
  waitlist patients who can come in on short notice.
- After 3 no-shows without notice, send a "re-engage or release slot" letter.
- Document every policy exception and the clinical rationale for the exception.

**Don't:**

- State a no-show policy in the intake paperwork but never enforce it.
- Charge a no-show fee to Medicaid patients (most Medicaid contracts prohibit this — verify per payer).
- Wait until the day of the appointment to confirm — by then it's too late to fill the slot.
- Treat no-shows as exclusively a billing problem; they are first an access problem.

## Edge cases / when the rule does NOT apply

- Patients in acute crisis or with documented clinical barriers (severe depression, anxiety, or
  other functional impairments that directly caused the no-show) may warrant a different response
  than the standard three-strike protocol — document the clinical rationale for any exception.
- Some payer contracts (particularly Medicaid) prohibit no-show fees. Always check the payer contract
  before charging fees to insured patients.
- A no-show by a new patient on their first appointment may indicate a clinical barrier to starting
  care — a follow-up call with a clinical lens is warranted, not just a fee notice.

## See also

- [`../skills/intake-and-access/SKILL.md`](../skills/intake-and-access/SKILL.md) — the no-show policy design framework
- [`../scripts/bh_calc.py`](../scripts/bh_calc.py) — no-show rate and capacity calculators
- [`./a-no-show-policy-protects-access.md`](./) — this document

## Provenance

Codifies the access management consensus from behavioral health operations literature, including
SAMHSA access standards and HRSA behavioral health workforce shortage guidance, as well as the
community mental health center operations field. No-show rate benchmarks vary by population and
setting; the 65–80% show rate range for outpatient BH is a commonly cited operational target, not a
regulatory standard.

---

_Last reviewed: 2026-06-08 by `claude`._
