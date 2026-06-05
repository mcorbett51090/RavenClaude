> Denial root-cause analysis worksheet — categorizes denied claims by payer, denial reason, and origin point so the RCM team can assign ownership and implement front-end fixes rather than managing denials as a permanent back-end appeals queue.

# Denial Root-Cause Analysis — [Practice / Organization Name]

**Practice / Organization:** [Name]
**Segment:** [Physician-group | Hospital | Specialty | RCM-vendor | FQHC]
**Analysis Period:** [YYYY-MM-DD] to [YYYY-MM-DD]
**Analyst:** [Name, Title]
**Date Prepared:** [YYYY-MM-DD]

---

## 1. Denial Volume Summary

| Metric | This Period | Prior Period | Change | Benchmark |
|---|---|---|---|---|
| Total claims submitted | [#] | [#] | [+/-X%] | — |
| Total claims denied | [#] | [#] | [+/-X%] | — |
| Initial denial rate | [X]% | [X]% | [+/-X pp] | < 5% (best-in-class < 3%) |
| Dollar value denied | $[Amount] | $[Amount] | | |
| Dollar value appealed | $[Amount] | | | |
| Appeal success rate | [X]% | | | |
| Net denial write-off rate | [X]% | | | |

---

## 2. Denial Breakdown by Root-Cause Category

| Category | # Claims | $ Value | % of Total Denials | Owner | Fix Type |
|---|---|---|---|---|---|
| **Front-end** | | | | | |
| Eligibility / coverage inactive | [#] | $[Amount] | [X]% | Front desk | Pre-visit verification |
| Authorization missing / expired | [#] | $[Amount] | [X]% | Scheduling / Auth team | Pre-service auth workflow |
| Patient demographic error (name, DOB, ID) | [#] | $[Amount] | [X]% | Registration | Intake validation |
| **Coding / Documentation** | | | | | |
| CPT not covered / non-covered service | [#] | $[Amount] | [X]% | Coding / Provider | LCD/NCD review; documentation |
| ICD-10 not supported by CPT (medical necessity) | [#] | $[Amount] | [X]% | Coding / Provider | Documentation improvement |
| Modifier missing or incorrect | [#] | $[Amount] | [X]% | Coding | Coding education |
| Duplicate claim | [#] | $[Amount] | [X]% | Billing | Claims edit rules |
| **Payer / Contract** | | | | | |
| Timely filing exceeded | [#] | $[Amount] | [X]% | Billing | Filing deadline monitoring |
| Coordination of benefits (COB) | [#] | $[Amount] | [X]% | Billing | COB workflow at intake |
| Bundling / unbundling | [#] | $[Amount] | [X]% | Coding | NCCI edit compliance |
| **Provider** | | | | | |
| Provider not credentialed with payer | [#] | $[Amount] | [X]% | Credentialing | 90-day advance credentialing |
| Referring provider info missing / incorrect | [#] | $[Amount] | [X]% | Billing | Referral capture at scheduling |
| **Other / Unclassified** | [#] | $[Amount] | [X]% | RCM Lead | Triage and categorize |
| **TOTAL** | [#] | $[Amount] | 100% | | |

---

## 3. Denial Breakdown by Top 5 Payers

| Payer | # Denials | $ Value | Denial Rate | Primary Denial Category | Action |
|---|---|---|---|---|---|
| [Payer 1] | [#] | $[Amount] | [X]% | [Category] | [Action item] |
| [Payer 2] | | | | | |
| [Payer 3] | | | | | |
| [Payer 4] | | | | | |
| [Payer 5] | | | | | |

---

## 4. Front-End vs. Back-End Origin

| Origin | # Denials | $ Denied | % Preventable |
|---|---|---|---|
| Front-end (eligibility, auth, registration) | [#] | $[Amount] | ~100% |
| Coding / documentation | [#] | $[Amount] | ~80% |
| Billing / timely filing | [#] | $[Amount] | ~100% |
| Payer error / contract dispute | [#] | $[Amount] | ~0% (appeal-only) |
| **Preventable total** | | $[Amount] | [X]% of all denials |

> Goal: > 80% of dollar-weighted denials are preventable. If preventable denials exceed that threshold, the investment is in front-end workflow, not the appeals team.

---

## 5. Root-Cause Action Plan

| Root Cause | # of Denials | $ at Risk | Action | Owner | Target Completion | Expected $ Recovery |
|---|---|---|---|---|---|---|
| [e.g., Missing auth — payer X] | [#] | $[Amount] | Implement same-day auth check at scheduling for payer X services | [Auth supervisor] | [YYYY-MM-DD] | $[Amount/mo] |
| | | | | | | |

---

## 6. Appeals Worklist Priority

| Payer | Denial Reason | # Claims | $ Value | Appeal Deadline | Assigned To | Status |
|---|---|---|---|---|---|---|
| [Payer] | [Reason] | [#] | $[Amount] | [YYYY-MM-DD] | [Name] | Pending / In progress / Filed |

> Sort by appeal deadline ascending — a missed deadline is unrecoverable.

---

_Template version: 1.0 — medical-revenue-cycle plugin_
