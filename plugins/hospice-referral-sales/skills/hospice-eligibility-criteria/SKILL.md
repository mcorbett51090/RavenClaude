---
name: hospice-eligibility-criteria
description: "Veteran playbook for EDUCATING referral sources on hospice eligibility — the Medicare Hospice Benefit structure, the non-disease-specific decline guidelines, the diagnosis-specific LCD criteria, and the PPS/FAST/NYHA scales. Teaches recognition, never certification. Consulted by hospice-eligibility-educator. Every output ends with 'the attending physician and medical director certify eligibility.'"
---

# Hospice Eligibility Criteria Skill

**Purpose:** help `hospice-eligibility-educator` teach a referral source to _recognize_ a potentially hospice-eligible patient. This skill is **education**, not a certification or determination tool.

## The hard line (applies to everything below)

**The representative educates; the physician certifies.** Hospice eligibility — a prognosis of six months or less if the disease runs its normal course — is certified by the **attending physician and the hospice medical director** on clinical judgment. Nothing in this skill, and nothing the agent produces from it, tells anyone that a specific patient "qualifies," "is eligible," or "is covered." Every deliverable ends with the physician-certifies line. (`../CLAUDE.md` §3 #1, §5.)

## When to use

- Preparing eligibility education for a diagnosis or a mixed population.
- Doing a de-identified, educational read of whether a profile warrants a physician conversation.
- Correcting a referral source's eligibility misconception.

## 1. The Medicare Hospice Benefit (structure, not a coverage promise)

- For a patient with a **terminal prognosis of six months or less** if the disease runs its normal course, who **elects** the benefit and forgoes curative treatment for the terminal illness.
- **Benefit periods:** two 90-day periods, then unlimited 60-day periods, each requiring **recertification**; a **face-to-face encounter** is required before the third and each subsequent period. (Confirm the current CMS rule — `[example — verify]`.)
- The benefit is **revocable** — a patient can leave hospice and resume curative care at any time. This fact matters enormously in the goals-of-care conversation.

## 2. The non-disease-specific decline guidelines (teach this first)

The most useful teaching tool, because it catches the multi-morbidity and failure-to-thrive patients that single-diagnosis LCDs miss. The decline picture:

- **Functional decline** — falling Palliative Performance Scale (PPS), increasing dependence in activities of daily living, mostly bed/chair-bound.
- **Nutritional decline** — unintentional weight loss, falling BMI, declining albumin, decreasing intake.
- **Recurrent acute events** — repeated infections (aspiration pneumonia, UTIs, sepsis), repeated hospitalizations / ED visits.
- **Progressive symptoms** — dyspnea, pain, or other symptoms worsening despite optimal treatment.

Teach the clinician to see the _trajectory_, not a single number.

## 3. The scales

| Scale | Measures | Hospice-relevant signal |
| --- | --- | --- |
| **PPS** (Palliative Performance Scale) | Functional status 0–100% | Lower PPS (often ≤ 40–50%) supports a decline picture — `[example — confirm against the LCD]` |
| **FAST** (Functional Assessment Staging) | Dementia progression | FAST stage 7 (plus a recent complication) is the dementia LCD anchor |
| **NYHA** (New York Heart Association) | Heart-failure functional class | Class IV (symptoms at rest), optimally treated, anchors the cardiac LCD |

## 4. Diagnosis-specific LCD criteria (as education)

The detailed per-diagnosis decline indicators live in `resources/lcd-quick-reference.md` and [`../../knowledge/hospice-eligibility-lcd-reference.md`](../../knowledge/hospice-eligibility-lcd-reference.md). Covered: heart disease, pulmonary, dementia, renal, liver, stroke/coma, ALS/neuromuscular, cancer, HIV, and adult failure-to-thrive. Each is **dated and sourced** to the published LCD, and each is teaching content — the recognition picture, not a checklist that certifies.

## 5. Correcting the common myths

| Myth | The accurate framing |
| --- | --- |
| "You need a DNR for hospice." | False — a DNR is not required to elect hospice. |
| "Hospice is cancer-only." | False — the majority of hospice patients have non-cancer diagnoses (cardiac, dementia, pulmonary, etc.). |
| "You have to stop all treatment." | The patient forgoes curative treatment _for the terminal illness_; comfort and symptom treatment continue, and unrelated conditions are still treated. |
| "Hospice is the last 48 hours." | Hospice is for a six-month-or-less prognosis — earlier election gives the full benefit. |

## 6. The educational screen (never a certification)

When reading a de-identified profile, list which decline indicators are **present**, what is **missing to know**, and recommend **routing to the attending physician** for the clinical conversation. The output is "these published indicators are present; this warrants a physician discussion," never "this patient is eligible." The `eligibility-indicators` subcommand of `scripts/hospice_calc.py` tallies indicators with the same discipline.

## Hand-offs

- The conversation framing once a patient is identified → `goals-of-care-conversations` skill / `goals-of-care-conversation-coach`.
- Turning the education into a territory in-service → `referral-territory-development` skill / `referral-development-strategist`.
- The current text of a revised LCD → `ravenclaude-core` `deep-researcher`.
- The actual certification → the **attending physician / medical director** (always).
