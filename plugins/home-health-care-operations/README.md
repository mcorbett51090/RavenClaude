# home-health-care-operations

> The **in-home-care-delivery layer** for Claude Code — the team that answers *"who's eligible, who visits them, and did we prove it well enough to be paid and pass survey?"* and executes the answer. Two agents: the **home-health-agency-lead** (sets the service-line & payer-mix strategy, the PDGM/OASIS posture, the staffing & capacity model, the referral-development plan, the conditions-of-participation & survey-readiness posture, and the quality/VBP strategy) and the **home-care-operations-specialist** (runs intake & eligibility, the physician-order gate, scheduling & EVV, plan-of-care & visit documentation, and billing/RCM & the survey-readiness trail).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

> **Not medical, legal, or reimbursement advice.** Volatile CMS/PDGM/OASIS/EVV/state-Medicaid and conditions-of-participation specifics carry a retrieval date — verify at use, and confirm with a qualified professional before a billing, survey, or board commitment.

## What it does

| You ask | It returns |
|---|---|
| "Should we run skilled home health, private-duty home care, or both — and what payer mix?" | A service-line & payer-mix recommendation (Medicare/PDGM, Medicaid waiver, private pay) with the OASIS/PDGM posture, the margin/compliance implications, and the conditions that would change it |
| "Get this referral through intake and eligibility." | An intake packet: eligibility & benefit verification, the physician-order / face-to-face / certification gate cleared, and the initial plan of care — with the start-of-care date gated on the signed order |
| "Schedule this patient's visits and make sure EVV holds up." | A visit schedule matched to the plan of care & authorization, staffed for caregiver continuity, with EVV capture set up (the six Cures-Act elements) and a same-day exception-handling procedure |
| "Bill this 30-day period and tell me why claims are being denied." | A documentation-to-claim run: OASIS/plan-of-care/visit-note completeness check, PDGM period billing (NOA, LUPA watch, comorbidity), the waiver/private-pay path, and a denial root-cause analysis with the fix |
| "How do we staff clinicians and caregivers without blowing continuity?" | A staffing & capacity model (clinician/caregiver mix, W2 vs contract, ratios, continuity/retention targets) tied to referral volume and acuity, with the triggers that resize it |
| "Are we survey-ready — what would a surveyor cite?" | A conditions-of-participation & survey-readiness posture: the CoP-mapped gaps (QAPI, order/POC compliance, OASIS accuracy, EVV, competency/supervision), the likely citations, and a daily-habit readiness plan |
| "How do we move our Star rating and win under value-based purchasing?" | A quality strategy (OASIS outcomes, HHCAHPS, Star, HHVBP) with the 2-3 highest-leverage measures and the operational change each requires |

**Two rules it never breaks:** *eligibility and the physician order gate the start of care* (verify homebound, skilled need, face-to-face, and the signed order/certification before the first visit — the start-of-care date is gated on the order, not the referral), and *EVV is not optional* (capture the six Cures-Act elements on every Medicaid visit and work exceptions same-day — an unverified visit is an unbillable visit and a survey finding).

## What's inside

- **2 agents** — `home-health-agency-lead` (sets the service-line & payer-mix strategy, the PDGM/OASIS posture, the staffing & capacity model, the referral-development plan, the conditions-of-participation & survey-readiness posture, and the quality/VBP/Star strategy) and `home-care-operations-specialist` (runs intake & eligibility / benefit verification, the physician-order / face-to-face / certification gate, scheduling matched to the plan of care & authorization with caregiver continuity, EVV capture & exception handling, plan-of-care & visit documentation, and billing/RCM — PDGM period billing, Medicaid-waiver/private-pay, denials — with the survey-readiness audit trail).
- **3 skills** — `plan-intake-and-eligibility`, `build-scheduling-and-evv-workflow`, `run-billing-and-survey-readiness`.
- **2 knowledge files** — a Mermaid home-health decision tree (intake & the order gate, scheduling & EVV, PDGM/waiver billing & denials, CoP survey readiness + trade-off tables) and a 2026 home-health-patterns reference (the service-line split, intake & eligibility, OASIS & the plan of care, scheduling & continuity, EVV, PDGM/waiver/private-pay billing, the Conditions of Participation, quality/VBP, and a dated regulatory/tooling map).
- **2 templates** — a plan of care & visit schedule and an agency compliance & survey-readiness checklist.

## Where it sits in the care-continuum stack

```
home-health-care-operations (HERE)  →  care delivered IN THE HOME + the agency        ("who's eligible, who visits, did we prove it?")
hospice-referral-sales              →  end-of-life referral development                ("the terminal-care referral relationship")
senior-care-operations              →  facility-based senior living / assisted living  ("care delivered in a facility")
medical-revenue-cycle               →  hospital / physician-group RCM                   ("the institutional/professional claim")
people-operations-hr                →  caregiver / clinician hiring & retention         ("the workforce")
regulatory-compliance               →  licensure / accreditation / survey program       ("the compliance program")
```

This plugin is the **in-home-care-delivery layer**: it takes patients through intake, schedules and verifies the visits, documents the care, and bills it so it's paid and survives survey — and stays clear of the *end-of-life referral* (`hospice-referral-sales`), the *facility* (`senior-care-operations`), and the *hospital claim* (`medical-revenue-cycle`).

## Domain stance

Concept-first (eligibility + the physician order as the start-of-care gate, the skilled-vs-non-medical service-line split, OASIS driving the PDGM case mix and the quality outcomes, the plan of care as the contract, documentation-is-the-claim, scheduling to the plan of care & authorization, continuity-of-caregiver as the felt quality metric, EVV as the Cures-Act mandate, and survey-readiness as a daily habit against the Conditions of Participation), fluent across **Medicare skilled home health** (homebound + skilled need + face-to-face + certification), **PDGM** (30-day period, clinical/functional/admission-source/timing grouping, NOA, LUPA, comorbidity), **Medicaid waiver & private-pay** home care, **EVV** (six elements, open vs closed state models, GPS/telephony/device), the **Conditions of Participation** (QAPI, order/POC compliance, OASIS accuracy, competency/supervision), and **quality/VBP** (HHCAHPS, Star ratings, HHVBP). PDGM rates & weights, OASIS versions, EVV state models, CoP interpretive guidance, and VBP methodology carry retrieval dates — re-verify (and confirm with a qualified professional) before pinning in a client deliverable. **Not medical, legal, or reimbursement advice.**

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install home-health-care-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
