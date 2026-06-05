# hospice-referral-sales

A Claude Code plugin for a **hospice sales / community-education representative** — the person who grows a hospice program's admissions by building relationships with the clinicians and facilities that refer patients (the role titled, depending on the agency, _community liaison_, _patient care coordinator_, _hospice care consultant_, _community education representative_, or _account executive_).

It packages the recurring, judgment-heavy work of that job into a team of specialist agents, reusable skills, slash commands, and a runnable calculator — so territory planning, eligibility education, referral-partner reviews, funnel analysis, the goals-of-care conversation, and (above all) staying on the right side of healthcare's referral-marketing rules take minutes instead of hours and come out consistent.

> **Employer-neutral and compliance-first by design.** Nothing here is internal or confidential to any agency (VITAS, Kindred/Gentiva, Amedisys, AccentCare, Compassus, a regional non-profit, etc.). It encodes **public, industry-standard** hospice-sales practice and **published CMS rules** (the Medicare Hospice Benefit, the hospice Local Coverage Determinations, the Anti-Kickback Statute, HIPAA). It does **not** give medical, legal, or regulatory advice: **the representative educates referral sources on eligibility; the attending physician and hospice medical director certify it.**

## Who it's for

- Field hospice sales reps / community liaisons developing a referral territory
- Account executives managing key referral partners (hospital systems, SNF/ALF chains, physician groups, ACOs)
- Sales managers who coach a liaison team and own a referral-to-admission funnel and census target

## What's inside

### Agents (6)

| Agent | Owns |
| --- | --- |
| `referral-development-strategist` | Territory & prospecting: referral-source segmentation (hospitals, SNF/ALF, physician practices, ACOs/value-based), targeting, trigger events, in-service education programs, multi-touch outreach to clinicians |
| `hospice-eligibility-educator` | The clinical-education layer: the Medicare Hospice Benefit, the LCD decline criteria by diagnosis (cardiac, pulmonary, dementia/FAST, renal, liver, stroke, ALS, cancer, failure-to-thrive), PPS/FAST/NYHA scales — **educating** referral sources to recognize eligible patients, never certifying |
| `referral-account-manager` | Key referral-partner retention & growth: business reviews led by patient/family outcomes, account plans, whitespace (units/floors/service lines not yet referring), relationship recovery after a poor admission experience |
| `admissions-conversion-coach` | The referral-to-admission funnel: referral volume, conversion rate, time-to-admission, same-day admits, declined-referral root cause, CRM hygiene, average daily census growth |
| `goals-of-care-conversation-coach` | The hard human conversations: coaching clinicians and families through the hospice-vs-palliative distinction, the "giving up" myth, timing, and the common objections — without scripting false promises |
| `hospice-sales-compliance-advisor` | The dominant constraint: Anti-Kickback Statute & Stark, beneficiary-inducement CMP, gift/meal nominal limits, HIPAA/PHI handling, truthful non-misleading marketing, **no eligibility or coverage guarantees** — every other agent routes through it |

### Skills (6)

`referral-territory-development`, `hospice-eligibility-criteria`, `referral-account-planning`, `admissions-funnel-analytics`, `goals-of-care-conversations`, `hospice-sales-compliance` — veteran-level playbooks each agent consults on demand.

### Slash commands (6)

`/hospice-referral-sales:plan-referral-territory`, `:screen-hospice-eligibility`, `:prep-referral-review`, `:analyze-admissions-funnel`, `:coach-hospice-conversation`, `:compliance-check-outreach`.

### Knowledge bank (4)

- `hospice-sales-decision-trees.md` — 6 Mermaid decision trees: **referral-source prioritization**, **is-this-patient-ready-for-a-hospice-conversation** (educational eligibility screen), **hospice vs palliative vs continue-curative**, **level-of-care selection** (RHC/CHC/GIP/IRC), **gift/meal/arrangement anti-kickback gate**, **declined-referral root-cause**.
- `hospice-sales-glossary.md` — the working vocabulary (MHB, benefit periods, recertification, F2F, election/revocation, levels of care, PPS/FAST/NYHA, ADC/ALOS, AKS/Stark).
- `hospice-eligibility-lcd-reference.md` — the published LCD decline criteria summarized by diagnosis, **as education, not certification**, dated and sourced.
- `hospice-sales-compliance-reference.md` — AKS, Stark, beneficiary-inducement CMP, OIG hospice risk areas, gift/meal rules, HIPAA — dated and sourced.

### Runnable tool

`scripts/hospice_calc.py` — a zero-dependency Python CLI:

```bash
# Referral-to-admission funnel: 80 referrals, 65% admit rate, 1.8 day avg time-to-admit
python3 scripts/hospice_calc.py funnel --referrals 80 --admit-rate 65% --time-to-admit 1.8 --cost-per-admission 1200

# Census flow: ADC from start census + admits - discharges, ALOS, revenue at a per-diem
python3 scripts/hospice_calc.py census --start 120 --admits 22 --discharges 18 --days 30 --per-diem 225

# Benefit-period & recertification schedule from an election date
python3 scripts/hospice_calc.py benefit-periods --election 2026-01-15

# Eligibility-indicator tally (EDUCATIONAL — defers to physician certification)
python3 scripts/hospice_calc.py eligibility-indicators --pps 40 --weight-loss 12% --hospitalizations 3 --fast 7a
```

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project, or use the repo URL
/plugin install hospice-referral-sales@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0` (inherited Team Lead, protocols, and structured-output contract).

## House stance

- **The rep educates eligibility; the physician certifies it.** A liaison never tells a referral source or family that a patient "qualifies" or "is covered" — they teach the published criteria and route the determination to the attending physician and medical director.
- **Every touch clears the Anti-Kickback Statute first.** Gifts, meals, free services, staffing, and space arrangements all carry a fraud-and-abuse line. When a play is ambiguous, it goes to the compliance advisor before it goes to the customer.
- **Lead with the patient and family outcome, not the census number.** The census follows from earlier, better-timed hospice access — not from selling.
- **Earlier is better.** The biggest failure in hospice is the too-late referral: a short length of stay that denies the patient and family the benefit. Education that drives earlier referrals is the job.
- **Protect PHI at every step.** A liaison handles real patient data; HIPAA governs every message, list, and CRM field.

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and routing rules.
