# PT billing, units & denials — reference

Deep reference for the `billing-and-reimbursement-analyst`. Companion to
[`pt-practice-decision-trees.md`](pt-practice-decision-trees.md).

> **Compliance note:** the 8-minute rule, therapy threshold/KX, CPT codes, and payer policies change
> and vary. Treat all specifics as `[verify against current CMS/payer policy and a certified coder]`.

---

## The 8-minute rule (Medicare) — units from timed minutes

| Total timed minutes | Billable units |
|---|---|
| < 8 | 0 |
| 8–22 | 1 |
| 23–37 | 2 |
| 38–52 | 3 |
| 53–67 | 4 |
| +15 min | +1 unit |

Untimed (service-based) codes bill **1 unit per service** regardless of time, and are kept distinct
from timed codes. Some commercial payers use the rule-of-eights / AMA variant — verify per payer. Use
[`../scripts/pt_calc.py`](../scripts/pt_calc.py) `eight_minute_rule_units`.

## Timed vs. untimed — the distinction that drives errors

Mixing timed and untimed codes in the unit count is a common error. Sum the **timed** minutes for the
8-minute-rule conversion; bill untimed/service-based codes separately at one unit each.

## Denial root-cause map

| Denial reason | Usual origin | Fix at source |
|---|---|---|
| Medical necessity | documentation | skilled/necessity note |
| Units / time | minutes not recorded | record at point of care |
| Authorization | front desk / intake | verify auth before the visit |
| Modifier (KX / threshold) | threshold not tracked | track cumulative + attest |
| Coding (wrong CPT) | coded from target | code forward from the note |

The discipline: prevent at the origin, don't appeal at the end. An appealed denial is rework; a
prevented one is margin.

## Therapy threshold / KX

When cumulative therapy passes the threshold, the KX modifier attests continued medical necessity —
and requires documentation to back it. Track cumulative amounts so it's applied on time. Threshold
dollar amounts update annually; verify the current-year figure.

## Code-forward principle

Coding follows documented, medically necessary, delivered care. Working backward from a target
reimbursement is upcoding and a False Claims exposure — and the most common denial besides. If the
documentation doesn't support the code, fix the documentation (or the care), never the code.

## Payer performance

Track net collection per visit by payer, underpayment vs. contract, and denial patterns to target
contract and workflow levers.
