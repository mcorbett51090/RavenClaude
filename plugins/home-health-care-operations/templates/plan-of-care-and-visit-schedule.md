# Plan of care & visit schedule — <patient / episode>

> The one-page artifact captured when taking a patient through intake and scheduling. Pairs with
> [`agency-compliance-and-survey-checklist.md`](agency-compliance-and-survey-checklist.md) (the compliance/survey side of the same operation).
> **Not medical, legal, or reimbursement advice.** Volatile CMS/PDGM/OASIS/EVV/state-Medicaid specifics carry a retrieval date — verify at use.

**Owner:** <clinical manager> · **Date:** <YYYY-MM-DD> · **Service line:** skilled home health / non-medical home care · **Payer:** <Medicare / Medicaid waiver / private pay / LTC> · **Status:** draft / active · **Review cadence:** <recert cycle / weekly schedule>

## 1. Intake & eligibility (the gate — cleared before the first visit)
| Check | Result | Evidence / date |
|---|---|---|
| Service line classified (skilled vs non-medical) | <skilled / non-medical> | |
| **Medicare:** homebound status | <yes / n/a> | |
| **Medicare:** skilled need (SN / PT / OT / SLP) | <which> | |
| **Medicare:** intermittent + certified agency | <yes / n/a> | |
| **Order gate:** signed physician order | <yes — date> | |
| **Order gate:** face-to-face encounter (in window, tied to HH reason) | <yes — date> | |
| **Order gate:** certification of eligibility | <yes — date> | |
| **Waiver:** authorization (units / service / dates) | <n/a / details> | |
| **Private pay / LTC:** signed agreement + rate/hours | <n/a / details> | |
| Benefits verified (coverage, prior auth, no open episode) | <yes> | |
| **START-OF-CARE date (gated on the signed order):** | **<YYYY-MM-DD>** | |

## 2. Plan of care (physician-ordered)
- **Primary diagnosis / reason for home health:** <dx>
- **Relevant comorbidities:** <list — drive PDGM comorbidity adjustment>
- **Disciplines & orders:**
| Discipline | Frequency / duration | Goals | Interventions |
|---|---|---|---|
| Skilled nursing | <e.g. 3x wk1-2, 2x wk3-4> | <goal> | <med teaching / assessment / wound> |
| PT / OT / SLP | <e.g. PT 2x/wk × 4> | <goal> | <gait / ADL / strengthening> |
| Home-health aide | <e.g. 2x/wk> | <goal> | <personal care — under supervision> |
- **OASIS assessment:** <SOC completed — date · functional level → PDGM case mix>
- **Physician / allowed practitioner:** <name · order signed date>

## 3. Visit schedule (matched to the plan of care & authorization)
```
Wk:        1     2     3     4     ...
SN         .     .     .     .           (RN/LPN — continuity: <primary caregiver>)
Therapy    .     .     .     .           (PT/OT/SLP — continuity: <primary>)
Aide       .     .     .     .           (continuity: <primary aide> · backup: <name>)
Authorized units used vs cap:  <n / cap>
```
- **Continuity assignment:** <primary caregiver(s) · backup · warm-handoff plan on turnover>
- **Over/under-visit check:** <matches POC & authorization · not over a capped auth · above LUPA threshold?>

## 4. EVV setup (verify every visit — Cures-Act mandate)
- **State EVV model:** <open (agency vendor) / closed (state aggregator)> · _(retrieved <date>)_
- **Capture method:** <mobile GPS / telephony / fixed device> · fallback: <telephony for no-signal>
- **Six elements captured:** service type · recipient · caregiver · date · location · check-in/out
- **Data flow confirmed:** capture → <vendor/aggregator> → claim, matched to authorization

## 5. EVV exception handling (worked same-day)
| Visit | Exception | Reason | Correction | Billable? |
|---|---|---|---|---|
| <date/patient> | <missed / no check-out / GPS mismatch / late> | <reason> | <corrected / documented / rescheduled> | <yes / lost> |

## 6. Delay / deny & continuity conditions
- <e.g. face-to-face outside window → re-obtain before certifying>
- <e.g. waiver authorized units < ordered frequency → reconcile before scheduling>
- <e.g. primary caregiver resigns → warm-handoff re-assignment, not a cold swap>

## Seams (not this team)
- **Strategy / payer-mix / staffing model / CoP posture:** home-health-agency-lead
- **Hospital / physician-group RCM:** medical-revenue-cycle
- **End-of-life / hospice referral:** hospice-referral-sales
- **Facility-based senior living:** senior-care-operations
- **Caregiver hiring & retention:** people-operations-hr
- **Deep survey remediation:** regulatory-compliance

## Open questions / risks
- <list>

**Sign-off:** <clinical manager / DON> · <date> · *Not medical/legal/reimbursement advice — volatile CMS/PDGM/OASIS/EVV specifics verified at use (<retrieval date>).*
