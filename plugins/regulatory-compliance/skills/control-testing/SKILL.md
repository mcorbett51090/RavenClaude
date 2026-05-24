---
name: control-testing
description: Compliance / second-line control testing rubric — design adequacy + operating effectiveness for compliance controls (KYC quality, monitoring rule tuning, training coverage, regulatory-mapping freshness). Distinct from SOC1/SOC2 financial-control testing — second-line compliance testing has different scoping, sampling, and reporting. Reach for this skill when scoping a periodic compliance-monitoring program, training MI/QC analysts, or responding to an exam request for "evidence your controls work." Used by `risk-and-controls-specialist` (primary) and `aml-kyc-analyst`.
---

# Skill: control-testing

**Purpose:** A second-line compliance-control testing program — different from SOC1 / SOC2 / ICFR testing in scope, sampling, and reporting. This skill is the rubric for that program. Used by `risk-and-controls-specialist` (primary) and `aml-kyc-analyst`.

## When to use

- Standing up a periodic compliance-monitoring program for the first time
- Refreshing the testing program (annually at minimum)
- Training MI / QC analysts on what a finding looks like (vs an observation)
- Pre-exam — examiners ask "show me the evidence your controls work"; this skill produces that evidence
- Responding to an MRA on monitoring-program adequacy
- Quarterly committee reporting on control effectiveness

## How this differs from SOC / ICFR testing

| | SOC1 / SOC2 / ICFR | Second-line compliance testing |
|---|---|---|
| **Framework** | AICPA / PCAOB / COSO ICIF | FFIEC examination manual, FATF Rec. 18, local-regulator monitoring expectations |
| **Audience** | Auditors, investors, customers via SOC report | Regulator, audit committee, AML/CCO chain |
| **Risk universe** | Financial-statement assertions | Compliance / conduct / AML / sanctions / market-conduct risks |
| **Sampling rigor** | Highly prescribed (AICPA AS 2315; PCAOB AS 2315 + AS 1105) | Risk-based; the regulator's expectation is "reasonable", not auditor-grade |
| **Reporting** | Annual / semi-annual SOC report | Continuous / quarterly committee reports + ad-hoc to AML/CCO |
| **Independence** | External CPA firm (SOC1/SOC2) or internal audit (ICFR) | Second-line (compliance / risk) — distinct from 1st-line business |
| **Conclusion** | Opinion (qualified / unqualified) | Findings + severity + remediation tracker |

Conflating the two produces either (a) over-engineered compliance testing that takes auditor-grade evidence on every sample (impractical), or (b) under-rigorous SOC work that fails AICPA standards. Different jobs.

**Cross-reference:** the finance plugin's `soc-control-walkthrough.md` covers SOC-style walkthroughs in detail. Reach for it when the engagement is SOC1 / SOC2 / ICFR; reach for *this* skill when the engagement is second-line compliance monitoring.

## Monitoring vs assurance — what 2nd line does and doesn't

| | Monitoring (2nd line) | Assurance (3rd line) |
|---|---|---|
| **Who** | Compliance / risk function | Internal audit |
| **Independence** | Independent of 1st line but not of management | Independent of 1st and 2nd lines; reports to audit committee |
| **Coverage** | Continuous / risk-based / thematic | Periodic / based on internal-audit plan |
| **Reporting** | To management + 2nd line head + risk committees | To audit committee + board |
| **Action** | Direct remediation pressure on 1st line | Recommendations to management; track to closure |

House opinion #3: don't conflate the lines. A 2nd-line monitoring report and a 3rd-line audit report are different artifacts with different audiences and different consequences.

## What 2nd-line compliance testing covers (typical population)

The testing program scopes risk-based across these populations. Calibrate the depth per the firm's risk profile.

| Control area | Population | Typical sample basis |
|---|---|---|
| **KYC file quality** | Onboarded customers in the period; risk-tier weighted | Stratified by tier (every High; sample of Medium; smaller sample of Low) |
| **Sanctions hit disposition** | Cleared dispositions in the period | Stratified by match-quality tier; oversample Strong/Exact |
| **Transaction-monitoring alert dispositions** | Closed alerts in the period | Stratified by typology / by analyst / by aging |
| **SAR / STR filing timeliness + quality** | SARs filed in the period; SARs *not* filed where escalation occurred | All in period, given typically low count + high importance |
| **Periodic refresh execution** | Refreshes due in the period | Verify refreshes happened, not just that the system flag was cleared |
| **Training coverage + currency** | Personnel in roles requiring AML / sanctions / conduct training | All; not a sample — completion is binary |
| **Policy / procedure currency** | All policies | All — every policy past review-due is a finding |
| **Regulatory-mapping freshness** | All in-scope regulations | All — every reg without an updated mapping after a known change is a finding |
| **Vendor screening / list-update receipt** | Vendor list-update reports for the period | All scheduled updates verified received + applied |
| **PEP screening** | Customer + family + close associates | Same stratification as KYC files |
| **Beneficial-ownership verification** | Higher-risk corporate customers | Stratified; full for High-tier |
| **Reportable-relationship escalation** | Wire / counterparty / introducer thresholds | Per the firm's escalation rules |

## Design adequacy vs operating effectiveness

For every control tested, both:

**Design adequacy** — would this control, *as designed*, prevent or detect the risk?

Test:
- Read the procedure / control narrative
- Map to the underlying risk + risk appetite
- Evaluate against regulator expectation (cite the rule)
- Assess: Adequate / Partially Adequate / Inadequate, with rationale

If the design is Inadequate, operating-effectiveness testing is wasted effort — fix design first.

**Operating effectiveness** — is the control, *as operated*, actually catching what it's supposed to catch?

Test:
- Pull the sample
- Re-perform / inspect / observe per the control's nature
- Compare actual operation to the documented control
- Evaluate: Effective / Partially Effective / Ineffective, with rationale + sample size + exception rate

## Sampling for compliance-monitoring populations

Second-line testing is **risk-based**, not auditor-statistically-precise. Documented in the program:

| Population size | Suggested sample (per risk-based tier) |
|---|---|
| <30 in period | All |
| 30–100 | 25 minimum + 100% of High-tier |
| 100–500 | 40 + 100% of High-tier |
| 500–2,500 | 60 + 100% of High-tier |
| >2,500 | 80 + 100% of High-tier + judgemental over-sample on outlier analysts / typologies |

Within sample: stratify by risk tier (KYC), match-quality tier (sanctions), typology (TM), analyst (workload distribution), and aging.

For exam-defensibility, document the sampling rationale up front, not after-the-fact.

## What makes a finding (vs an observation)

| | Observation | Finding |
|---|---|---|
| **What** | An improvement opportunity; not a control failure | A control failure or design inadequacy |
| **Tied to risk** | May reduce a residual risk | The residual risk is currently outside appetite |
| **Tied to regulator citation** | Indirectly | Directly — name the rule it breaches |
| **Remediation required** | Recommended, not mandatory | Required, with date + owner |
| **Reporting** | Operating-meeting level | Risk committee + audit committee; sometimes regulator-notified |

The distinction matters because findings drive remediation tracking + regulator-notification thresholds. An observation that should have been a finding is a missed escalation; a finding downgraded to "observation" is a governance failure.

## Severity rating

| | Definition | Examples | Escalation |
|---|---|---|---|
| **P0** | Regulatory rule breach already occurred *or* control failure presents imminent breach risk | Sanctioned-party onboarded; SAR not filed within statutory window; UBO not verified on a high-risk customer | Notify CCO + AML Officer same day; possible regulator notification; immediate remediation |
| **P1** | Material control weakness; residual risk outside appetite; pattern of misses | KYC files past refresh date with no follow-up; sanctions hits cleared with no rationale on multiple files | Risk committee; remediation within current quarter |
| **P2** | Minor weakness; residual within appetite but improvable | Periodic refresh evidence stored inconsistently; training records present but format inconsistent | Operating meeting; remediation in routine cadence |

A finding without a severity is incomplete. Severity drives reporting cadence.

## Reporting cadence

| Audience | Frequency | Content |
|---|---|---|
| 1st-line ops | Continuous / per-finding | Specific findings on their controls; root cause; remediation expectation |
| 2nd-line head (CCO / CRO) | Monthly | All open findings; severity distribution; remediation aging |
| Risk committee / management committee | Quarterly | Themes, trends, P0/P1 findings, remediation status |
| Audit committee | Half-yearly minimum | Program coverage; effectiveness trends; P0/P1 history; comparison to risk appetite |
| Board | Annually | Program summary; appetite-vs-residual; major themes |
| Regulator | On-finding (P0); on-request | Specific to the matter; cleared through legal + CCO |

## MRA / management-letter response patterns

When the testing program produces a finding that escalates to an MRA-equivalent (or the firm receives one from a regulator), the response pattern:

1. **Acknowledge** in writing, within the regulator's stated window (often 30 days).
2. **Root-cause** before remediation design. Symptoms get remediated to come back next year; causes get remediated and stay fixed.
3. **Remediation plan** — date + owner + measurable success criterion + independent verification step. House opinion #5.
4. **Interim controls** — what stops the risk *now*, before remediation lands.
5. **Status updates** to the regulator at the cadence they specified (or quarterly if not specified).
6. **Independent verification** before closure — usually 3rd line (internal audit) or external.
7. **Closure submission** to the regulator with verification evidence attached.

A response that lists the remediation step but no root-cause analysis is incomplete. A closure submitted without independent verification is fragile.

## Link to remediation tracking

Every finding has a remediation row in the tracker:

| # | Finding | Severity | Root cause | Remediation | Owner | Target date | Status | Verification | Closure date |
|---|---|---|---|---|---|---|---|---|---|

Tracker reviewed monthly by 2nd line; quarterly by committee. Findings overdue trigger re-rating (a P1 overdue by >90 days re-rates toward P0).

## Common findings on the testing program itself (meta)

- No documented sampling rationale
- Same population sampled every period (no rotation; no thematic coverage)
- Findings without root cause
- Severity assigned by feel, not by rubric
- Remediation tracker disconnected from the testing program (findings closed in one place, never updated in another)
- Tester independence not documented (a 2nd-line tester reporting through the 1st-line head is not independent)
- "Effective" rating on a control with a 30% sample exception rate

## Anti-patterns

- Testing program scoped only to controls where the firm is confident — defeats the purpose
- Sample sizes that round-trip the same files every period
- "Observation" used when the finding criteria are met, to keep severity profile low
- Remediation closed on a target date without verification evidence
- 2nd-line testing branded as "audit" — confuses regulator on the line of defense
- Same person designs the control + tests it
- Reporting that rolls up only the count of findings, not the residual risk after them

## See also

- Skill: [`../risk-register-build/SKILL.md`](../risk-register-build/SKILL.md)
- Skill: [`../aml-program-review/SKILL.md`](../aml-program-review/SKILL.md)
- Skill: [`../kyc-edd-review/SKILL.md`](../kyc-edd-review/SKILL.md)
- Skill: [`../sanctions-hit-disposition/SKILL.md`](../sanctions-hit-disposition/SKILL.md)
- Skill: [`../examination-readiness/SKILL.md`](../examination-readiness/SKILL.md)
- Cross-plugin: `finance` plugin `skills/soc-control-walkthrough.md` (for SOC1 / SOC2 / ICFR-style work)
- Template: [`../../templates/control-narrative.md`](../../templates/control-narrative.md)
- Template: [`../../templates/examination-response-tracker.md`](../../templates/examination-response-tracker.md)
- Agent: [`../../agents/risk-and-controls-specialist.md`](../../agents/risk-and-controls-specialist.md)
- Agent: [`../../agents/aml-kyc-analyst.md`](../../agents/aml-kyc-analyst.md)
