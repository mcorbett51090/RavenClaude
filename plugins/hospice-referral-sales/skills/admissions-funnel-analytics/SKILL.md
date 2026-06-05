---
name: admissions-funnel-analytics
description: "Veteran playbook for reading the hospice referral-to-admission funnel — the stage definitions tied to observable events, conversion rate, time-to-admission and same-day admits, the declined-referral root-cause taxonomy with an owner for each, average daily census and length-of-stay reads, and the activity-to-census model. Consulted by admissions-conversion-coach. A referral is not census until it converts."
---

# Admissions Funnel Analytics Skill

**Purpose:** help `admissions-conversion-coach` read the funnel honestly, find the leak, give every decline a root cause and an owner, and connect activity to census. A referral count is never census; a converted, admitted patient is.

## When to use

- Reading the funnel for a leak.
- Diagnosing a conversion drop.
- Setting up honest tracking.
- Connecting activity to a census target.

## 1. The funnel stages (tie each to an observable event)

| Stage | The observable event | Watch |
| --- | --- | --- |
| Referral | A source sends a patient for consideration | Volume, source mix |
| Eligibility screen | A clinical review of appropriateness | Ineligible rate (an upstream education signal) |
| Information visit | The informational/election conversation with patient/family | Family-declined rate (a goals-of-care signal) |
| Election / consent | The patient elects the benefit | Time at this stage |
| Admission | The patient is admitted to service | Time-to-admission, same-day rate |

Conversion is measured stage-to-stage and overall (referral → admission). Stages move on **events**, not optimism.

## 2. Conversion analysis

- **Overall conversion** = admissions ÷ referrals. **Stage conversion** isolates the leak.
- Compare against a benchmark _band_ — but treat any external number as `[example — calibrate to your program]`; published hospice conversion benchmarks vary widely by market and source mix.
- The leaking stage points to the owner (see the root-cause taxonomy). Run `scripts/hospice_calc.py funnel` for the arithmetic.

## 3. Declined-referral root-cause taxonomy (every decline gets a cause and an owner)

| Root cause | Likely owner / fix |
| --- | --- |
| Ineligible (not yet hospice-appropriate) | Upstream education — `hospice-eligibility-educator`; also a possible late/early-timing signal |
| Family / patient declined | The goals-of-care conversation — `goals-of-care-conversation-coach` |
| Lost to another agency | Responsiveness / relationship — `referral-account-manager`, time-to-admit |
| Response too slow | Intake / staffing / after-hours capability |
| Patient died before admission | The **late-referral** problem — the highest-value upstream education target |
| Facility re-routed (relationship) | The account relationship — `referral-account-manager` |

"We lost some" is not a diagnosis. Every decline carries a cause and an owner, and the **mix** tells you where to invest.

## 4. Time-to-admission & same-day admits

Time-to-admission is a **conversion lever**, not a logistics footnote: a slow response loses referrals to faster agencies and, worse, can mean the patient dies before admission. Track the elapsed referral-to-admission time, the same-day-admit rate, and after-hours/weekend admit capability.

## 5. Census & length of stay

- **Average daily census (ADC)** is the running result of admissions − discharges over time — the program's true size. Run `scripts/hospice_calc.py census`.
- **Length of stay (LOS):** average and median. A **short LOS** (and a high share of very-short stays) is the signature of **late referrals** — read it as an upstream education gap, not an intake problem. Median LOS is more honest than mean (a few long stays skew the average).

## 6. Activity-to-census model

Work backward from a census target: a target ADC, sustained at an average LOS, requires a steady admission rate, which (at your conversion rate and time-to-admit) requires a referral rate, which sets the activity target. This grounds activity goals in arithmetic instead of habit. The model and the math live in `scripts/hospice_calc.py` (`census` + `funnel`).

## Hand-offs

- Top-of-funnel volume too low → `referral-territory-development` skill / `referral-development-strategist`.
- A specific partner driving declines → `referral-account-planning` skill / `referral-account-manager`.
- Eligibility-driven declines → `hospice-eligibility-criteria` skill / `hospice-eligibility-educator`.
- Family-declined declines → `goals-of-care-conversations` skill / `goals-of-care-conversation-coach`.
- Building the reporting dashboard → `data-platform` plugin (a reporting build, not a referral-conversion question).
