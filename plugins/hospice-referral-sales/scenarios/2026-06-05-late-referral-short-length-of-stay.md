---
scenario_id: 2026-06-05-late-referral-short-length-of-stay
contributed_at: 2026-06-05
plugin: hospice-referral-sales
product: eligibility-education
product_version: "n/a"
scope: likely-general
tags: [late-referral, length-of-stay, education, timing, snf, conversion]
confidence: medium
reviewed: false
---

## Problem

A hospice program's referrals from a cluster of skilled-nursing facilities looked healthy on the dashboard — volume was up year over year — but the median length of stay from those buildings was a handful of days, and a meaningful share of referred patients died before or within a day of admission. The sales manager read the short stays as an intake/responsiveness problem and pushed the team to admit faster. Admitting faster did not help: the patients were arriving at hospice in their final days because they were being *recognized* in their final days.

## Context

- Segment: a set of SNFs referring to a single hospice program; manual referral tracking, no length-of-stay read by source.
- Constraint: a very short length of stay is the documented signature of **late referrals**, not slow intake — the patient and family lose most of the benefit (symptom management, support, planning, bereavement) when hospice starts in the last days. National hospice data consistently shows a large share of stays are very short. [unverified — confirm against current NHPCO / MedPAC public hospice data, retrieved 2026-06-05]
- The manager had conflated "more referrals" and "faster admits" with better access, missing that the leverage was *earlier recognition* upstream in the SNF.

## Attempts

- Tried: re-read the funnel by source with length of stay added (via the funnel/census calculator), which made the short-stay pattern and the "died before admission" declines visible per building rather than hidden in the aggregate. Outcome: the problem reframed from intake to upstream recognition.
- Tried: built a recurring SNF in-service on the **non-disease-specific decline guidelines** — teaching the DON and floor nurses to recognize the declining, multi-morbidity resident (falling PPS, weight loss, recurrent infections, repeat hospitalizations) and to prompt a physician conversation earlier. Clinical content owned by the eligibility educator, framed strictly as recognition, ending every time at "the physician certifies." Outcome: referrals began arriving with more decline runway.
- Tried: used each "died before admission" decline as a (de-identified) teaching case with the building, not as a complaint. Outcome: the conversation became collaborative, about patients, not about referral volume.

## Resolution

The short length of stay was a **late-referral / education** failure, not an intake one. Reading length of stay by source exposed it; a recurring in-service on earlier recognition (the non-disease-specific decline picture), reinforced with de-identified teaching cases, moved the average referral earlier — which served patients better and, as a result, grew genuine access. The lesson the manager had inverted: *recognize earlier* beats *admit faster*.

**Action for the next consultant hitting this pattern:** when length of stay is short, look **upstream at recognition**, not at intake speed. Read length of stay by source, treat a short median and "died before admission" declines as an education signal, and invest in a recurring in-service on the non-disease-specific decline guidelines. Never certify eligibility in the process — teach recognition and route to the physician (CLAUDE.md §3 #1, #4). Keep every teaching case de-identified (§3 #7).

**Sources (retrieved 2026-06-05):** the hospice short-length-of-stay / late-referral problem is well documented in public hospice policy literature (e.g., NHPCO Facts & Figures; MedPAC hospice chapters; CMS hospice data). Specific national percentages and median-stay figures are `[unverified]` here — confirm against the current public source and calibrate to your own program's data (§3 #8).
