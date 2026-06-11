# Early-Alert Playbook — <institution>

> A FERPA-aware early-alert design. Fill the signals, the score, the ladder, and the data-flow
> access map. Frame the target population by entering cohort.

## 1. Target & framing

- Entering cohort(s): `<term/year>`
- Primary target: the **year-1 → year-2 cliff** (highest-attrition transition)
- Highest-attrition segment (if known): `<segment>`

## 2. Leading risk signals

| Signal | Source | Why it leads | Weight |
|---|---|---|---|
| Attendance / early no-shows | `<SIS/LMS>` | disengagement precedes withdrawal | `<w>` |
| LMS engagement drop | `<LMS>` | behavioral early warning | `<w>` |
| Midterm / gateway grade | `<SIS>` | academic struggle, recoverable | `<w>` |
| Financial hold / aid gap | `<SIS/aid>` | solvable barrier if caught early | `<w>` |

## 3. Risk score → tier

| Tier | Trigger | Owner | Intervention |
|---|---|---|---|
| Watch | 1 signal | advisor (visibility) | automated nudge |
| Elevated | 2 signals | advisor | proactive outreach |
| High | 3+ / financial hold | case manager | wraparound support |

## 4. FERPA data-flow access map

| Field | Education record? | Who has legitimate educational interest | Access scope |
|---|---|---|---|
| `<signal/field>` | yes/no | `<role>` | `<scope>` |

> Compliance points (FERPA, state law) flagged for verification with institutional counsel.

## 5. Loop closure

- Recurring academic-struggle signals → route to gateway-course support and the registrar's
  scheduling/section capacity review.
- Measure intervention effect by cohort persistence, not by contact count.
