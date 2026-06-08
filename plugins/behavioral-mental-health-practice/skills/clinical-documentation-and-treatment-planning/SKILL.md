---
name: clinical-documentation-and-treatment-planning
description: "Structure treatment plans, progress notes, and measurement-based care workflows for an outpatient behavioral health practice so they satisfy payer medical-necessity requirements, survive utilization review, and support clinician quality tracking. Public practice framing only — not clinical advice."
---

# Clinical Documentation and Treatment Planning

**Purpose:** give the practice a documentation framework — treatment plan components, progress-note
structure, MBC cadence — that is organized for the clinician, defensible for the payer auditor, and
sustainable as an EHR workflow.

---

## Treatment plan components (required for medical necessity)

A behavioral health treatment plan must contain at minimum the following components to satisfy most
commercial and Medicaid payer requirements:

| Component | What goes here | Why it matters |
| --- | --- | --- |
| **Presenting problem** | Chief complaint and symptoms in functional terms | The starting point for medical-necessity justification |
| **Diagnosis** | DSM/ICD-10 code(s) with specifier; linked to functional impairment | Links clinical picture to billable diagnosis |
| **Functional impairment** | How the diagnosis impairs daily functioning (occupational, social, self-care) | The "medical necessity" anchor — treatment is necessary because function is impaired |
| **Measurable goals** | SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound) | Auditors look for measurable and time-bound; "patient will improve" fails |
| **Interventions** | Evidence-based modality(ies) to be used, listed by name; NOT a clinical endorsement | Describes the treatment method linked to each goal |
| **Frequency and duration** | Sessions per week/month; estimated treatment duration | Justifies ongoing authorization and continued medical necessity |
| **Clinician signature and date** | Credentialed clinician name, credential, date signed | Payer audit requirement |
| **Update date** | Date of last review; reviewer signature | Plans must be updated at auth renewal or every 90 days |

---

## Medical-necessity statement pattern

Every progress note and treatment plan should contain a medical-necessity statement that follows
this pattern:

> *"[Patient] presents with [diagnosis] causing [specific functional impairment]. Continued
> [service type] is medically necessary to [specific treatment goal] and to prevent [deterioration /
> hospitalization / functional decline]."*

**Examples of insufficient vs. sufficient statements:**

| Insufficient | Sufficient |
| --- | --- |
| "Patient has depression." | "Patient presents with MDD, severe, causing inability to maintain employment and significant social isolation. Weekly individual therapy is medically necessary to reduce depressive symptoms and restore occupational functioning." |
| "Patient continues to benefit from therapy." | "Patient's PHQ-9 score declined from 18 to 12 over 8 sessions, indicating partial response. Continued weekly therapy is medically necessary to achieve remission (PHQ-9 < 5) and prevent relapse." |

---

## Progress note structure

A minimal clinically and compliance-appropriate outpatient progress note contains:

1. **Date, time, session duration** — exact time matters for CPT time-based codes.
2. **Service type** — individual therapy, family therapy, group therapy, crisis, etc.
3. **Session summary** — brief clinical narrative (not a transcript); what was addressed.
4. **Patient response** — engagement, response to interventions, any safety concerns.
5. **MBC score** — if an instrument was administered this session, record the score and trend.
6. **Medical-necessity statement** — explicit statement of why the service continues to be necessary.
7. **Plan** — next appointment, any referrals, any changes to treatment plan.
8. **Clinician signature, credential, date/time**.

---

## Measurement-based care (MBC) workflow

MBC means using validated, publicly available instruments at defined intervals to track patient
progress and inform clinical and administrative decisions (including authorization renewal).

**Commonly used instruments in outpatient BH (public framing — not clinical endorsement):**

| Instrument | Targets | Public cadence guidance |
| --- | --- | --- |
| PHQ-9 | Depression (adult) | Every session or every 2–4 weeks |
| GAD-7 | Generalized anxiety (adult) | Every session or every 2–4 weeks |
| PCL-5 | PTSD/trauma | Every 2–4 weeks |
| BASIS-24 | General BH symptom severity | Monthly |
| CAMS (Collaborative Assessment and Management of Suicidality) | Suicide risk | Each session for elevated-risk patients |
| CGAS / CPSS | Child/adolescent | Monthly |

**EHR workflow to build:**

1. Configure the instrument as a standardized intake form in the EHR.
2. Assign the cadence as a recurring task on the patient's chart.
3. Score automatically (if EHR supports) or enter manually; store score in the clinical timeline.
4. Display the trend in the provider's chart view.
5. Flag scores above clinical concern thresholds (e.g., PHQ-9 ≥ 15) for provider review.
6. Include the score and trend in progress notes and treatment-plan updates.

---

## Treatment plan update cadence

| Trigger | Action |
| --- | --- |
| Authorization renewal (most payers require) | Update treatment plan, reassess functional impairment and goals |
| 90 days from last update | Review and update regardless of auth cycle |
| Significant clinical change | Update goals and interventions to reflect new clinical picture |
| Diagnosis change | New treatment plan with new diagnostic linkage |

---

## Anti-patterns

- Goals written as "patient will improve" or "patient will feel better" — not measurable.
- Treatment plans not updated in over 90 days.
- Progress notes with no medical-necessity statement.
- MBC scores captured at intake but not trended at subsequent sessions.
- Group notes with no individual clinical documentation.

---

## Output

A treatment plan template (see `templates/treatment-plan.md`), a progress-note structure guide, and
an MBC instrument cadence table configured for the practice's EHR workflow. Every output is framed
as practice operational guidance; clinical decisions remain with the licensed clinician.
