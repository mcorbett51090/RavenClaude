# Knowledge — Home-health-care patterns (2026)

> **Last reviewed:** 2026-07-17 · **Confidence:** High on the durable concepts (the service-line split, the eligibility & order gate, OASIS & the plan of care, the cash/quality role of documentation, EVV, caregiver continuity, the CoP structure); **Medium on the dated regulatory/payment/standard map — PDGM rates & weights, OASIS versions, EVV state models, CoP interpretive guidance, and the HHVBP/Star methodology change and carry retrieval dates below.**
> The reference the `home-care-operations-specialist` reads when running intake, scheduling and EVV, documentation, and billing — plus a 2026 regulatory/tooling snapshot. **This is not medical, legal, or reimbursement advice; volatile specifics carry a retrieval date and are verified at use.**

The team's discipline: **verify eligibility and clear the physician order before the first visit; schedule to the plan of care and the authorization, staffed for continuity; verify every visit (EVV); chart it before you bill it; bill the period deliberately (PDGM); and run survey-ready every day.**

---

## Service lines — skilled home health vs non-medical home care

| Dimension | Skilled home health | Non-medical / private-duty home care |
|---|---|---|
| **What** | Intermittent skilled nursing & therapy (PT/OT/SLP) under a physician plan of care | Personal care (ADLs), homemaking, companionship, supervision |
| **Who delivers** | RN/LPN, therapists, home-health aides (under supervision) | Home-care aides / caregivers |
| **Typical payer** | Medicare, Medicaid, managed care | Private pay, Medicaid waiver, LTC insurance |
| **Gate** | Homebound + skilled need + intermittent + certified agency + **physician order / F2F / certification** | Payer authorization (waiver) or private agreement |
| **Quality/regulatory** | OASIS, HHCAHPS, Star, HHVBP, Conditions of Participation | State licensure, EVV (for Medicaid), caregiver competency |

An agency may run one or both. The class drives the eligibility gate, the documentation set, and the payer economics — classify it first.

---

## Intake & eligibility — the gate that everything rides on

- **Medicare skilled home health — the four eligibility gates:** the patient is **homebound** (leaving home requires a considerable, taxing effort / assistance), has a **skilled need** (skilled nursing or PT/OT/SLP), needs care **intermittently**, and is served by a **Medicare-certified** agency under the care of a **physician/allowed practitioner**. All four — not one.
- **The order / face-to-face / certification gate:** a **signed physician order**, a **face-to-face encounter** within the required window and related to the primary reason for home health, and a **certification** of eligibility. The **start-of-care date is gated on the signed order** — billing ahead of it is the top denial and survey-finding source.
- **Medicaid waiver / MCO:** confirm the **waiver program** and the **service authorization** (units, service type, dates); managed-care plans add prior-auth and their own rules.
- **Private pay / LTC insurance:** a signed **agreement** (rate, hours), and any insurance **benefit / elimination period**.
- **Benefit verification:** active coverage, benefit period, prior auth, patient responsibility, and — for Medicare — no open episode with another agency (transfer rules). A benefit surprise after care starts is an uncompensated visit.

---

## OASIS & the plan of care — the clinical + payment record

- **OASIS** (Outcome and Assessment Information Set) — the standardized assessment collected at start of care, recert, resumption, transfer, and discharge for Medicare/Medicaid skilled patients. It **drives the PDGM case mix** (functional level) **and the quality outcome measures** — so OASIS accuracy is both a payment and a quality lever, and OASIS that doesn't match the visit record is an audit and case-mix risk. _(OASIS versions/items are volatile — retrieved 2026-07-17.)_
- **Plan of care** — the physician-ordered plan: diagnoses, the ordered services and **visit frequency/duration per discipline**, goals, and the interventions. It's the contract the schedule and the claim are built against; it must be **followed, updated, and signed**.
- **Visit notes** — skilled, **timely**, and matching the ordered frequency. **Documentation is the reimbursement**: if it isn't charted, it didn't happen and it won't be paid — and it's a citation.

---

## Scheduling & staffing — continuity is the felt quality metric

- **Schedule to the plan of care and the authorization** — the ordered frequency (skilled HH) or the authorized units/service type (waiver/private pay). Over-visiting a capped authorization is unpaid work; under-visiting risks **LUPA** (PDGM) and a plan-of-care-compliance finding.
- **Continuity of caregiver** — assigning the **same familiar caregiver** across the episode is the quality metric patients actually feel; it shows up in **HHCAHPS** and in retention. A revolving door of unfamiliar caregivers is the churn to design out — assign a primary and name a backup rather than floating open shifts.
- **Staffing model** — W2 (continuity, control, quality consistency) vs contract (surge/geography coverage, but weaker continuity and classification risk). Caseload ratios and travel/geography bound capacity. Caregiver **turnover** is the industry's structural problem; the retention plan is part of the staffing model — route hiring to `people-operations-hr`.

---

## EVV — Electronic Visit Verification (the Cures-Act mandate)

- **What & why:** the **21st Century Cures Act** mandates **EVV** for Medicaid-funded **personal-care services** and **home-health services** — an electronic record that a visit actually happened, to curb fraud and prove delivery.
- **The six required elements:** type of service, the individual **receiving** it, the individual **providing** it, the **date**, the **location**, and the **check-in/out times**.
- **Capture methods:** **mobile app (GPS)**, **telephony/IVR**, or **fixed device/token** — chosen by the patient's situation and the state model.
- **State models:** states run **open** (agency chooses its EVV vendor, data flows to the state) or **closed/state-mandated aggregator** models — the specific model, aggregator, and rules **vary by state** and change. _(EVV state models are volatile — retrieved 2026-07-17; verify the specific state.)_
- **The operating rule:** an **unverified visit is unbillable and a survey finding**; capture on every visit, match the verified visit to the authorization and schedule, and **work exceptions the same day** (missed/late/mismatched/manually-edited) — the exception queue is the difference between a clean claim and a denial.

---

## Billing & RCM — PDGM, waiver, private pay, and denials

- **PDGM (Patient-Driven Groupings Model)** — Medicare home health pays on a **30-day period** grouped by **clinical grouping, functional impairment level, admission source (community vs institutional), and timing (early vs late)** — **not** by visit volume. **Comorbidity adjustments** modify payment. Case mix and visit efficiency drive margin. _(PDGM rates and case-mix weights are volatile — retrieved 2026-07-17.)_
- **NOA (Notice of Admission)** — submitted at the start of the first period; **late submission reduces payment** for the period. Then the **final period claim**.
- **LUPA (Low Utilization Payment Adjustment)** — a period with **too few visits** (below the period's threshold) is paid **per visit** instead of the full period amount — a margin cliff to watch, and a signal you may be under-visiting the plan of care. _(LUPA thresholds are volatile — retrieved 2026-07-17.)_
- **Medicaid waiver / MCO** — bill the **authorized units** per service, with **EVV attached** (no verification, no payment).
- **Private pay / LTC insurance** — invoice the agreed hours/rate; watch collections and the carrier's documentation demands.
- **Denial management** — root-cause the denial (**eligibility, order/certification, documentation, EVV, timing, authorization**) and fix the **source**; a rising denial rate in one bucket is a process defect, not a billing-clerk problem.

---

## Conditions of Participation & survey readiness

The Medicare **Conditions of Participation (CoP)** are what a home-health survey tests. Run **CoP-ready every day** — the readiness checks are the billing gate, not a pre-survey cram:

- **QAPI** (Quality Assessment and Performance Improvement) — an active, data-driven program.
- **Patient rights** — notice, informed consent, complaint handling.
- **Plan-of-care & physician-order compliance** — orders followed, updated, and signed.
- **OASIS accuracy** — the assessment matches the record.
- **Competency & supervision** — aide competency evaluations and supervisory visits documented.
- **Infection control**, **emergency preparedness**, **clinical-record** completeness and timeliness.
- **EVV completeness** — no open exceptions.

Produce a **gap list** — the specific things a surveyor would cite — with remediation per item. _(CoP interpretive guidance is volatile — retrieved 2026-07-17.)_

---

## Quality & value-based purchasing

- **Outcome measures** — OASIS-derived (improvement in function/mobility, hospitalization/ED-use rates) plus claims-based and HHCAHPS measures.
- **HHCAHPS** — the patient-experience survey; continuity and communication move it.
- **Star ratings** — Care Compare quality and patient-survey stars that patients and referral sources see.
- **HHVBP (Home Health Value-Based Purchasing)** — a **payment adjustment** (up or down) tied to quality performance — quality is a revenue lever, not a plaque. Pick the 2-3 highest-leverage measures and change the operations each needs. _(HHVBP/Star methodology is volatile — retrieved 2026-07-17; verify at use.)_

---

## 2026 regulatory & tooling map (dated — volatile, re-verify before quoting)

- **Payment model:** **PDGM** — 30-day periods, clinical/functional/admission-source/timing grouping, comorbidity adjustment, **NOA** timing, **LUPA** thresholds. _(Retrieved 2026-07-17; rates/weights/thresholds volatile.)_
- **Assessment:** **OASIS** at SOC/recert/resumption/transfer/discharge — versions and items change. _(Retrieved 2026-07-17.)_
- **EVV:** **21st Century Cures Act** mandate; **open vs closed/aggregator** state models; six required elements; GPS/telephony/device capture. _(Retrieved 2026-07-17; state models volatile.)_
- **Compliance:** Medicare **Conditions of Participation** (QAPI, patient rights, POC/order, OASIS, supervision, infection control); **state licensure** overlays. _(Retrieved 2026-07-17.)_
- **Quality/VBP:** **HHCAHPS**, **Star ratings**, **HHVBP** payment adjustment. _(Retrieved 2026-07-17; methodology volatile.)_
- **Software categories:** home-health/home-care EHR & agency-management platforms (intake, OASIS/POC, scheduling, EVV, billing/RCM), EVV vendors/aggregators, and clearinghouses — the tiering, not the vendors; verify at selection. _(Retrieved 2026-07-17.)_

---

## Provenance

- Durable concepts (the skilled-vs-non-medical service-line split, the four Medicare eligibility gates + the order/F2F/certification gate, start-of-care gated on the order, OASIS driving case mix and outcomes, the plan of care as the contract, documentation-is-the-claim, scheduling to the POC/authorization, continuity-of-caregiver as the felt quality metric, EVV as the Cures-Act mandate with its six elements, PDGM period-based billing with NOA and LUPA, denial root-causing, the Conditions-of-Participation structure, and quality as a VBP revenue lever) are consensus home-health/home-care practice reviewed 2026-07-17 — **High confidence**.
- The regulatory/payment/standard map — PDGM rates & case-mix weights, NOA timing, LUPA thresholds, OASIS versions, EVV **state** models & aggregators, CoP interpretive guidance, and HHVBP/Star methodology — is a **2026-07 snapshot**; these are volatile, carry the retrieval dates above, and are **not medical/legal/reimbursement advice** — re-verify with `ravenclaude-core/deep-researcher` and a qualified professional before pinning in a deliverable. _(Reviewed 2026-07-17.)_
