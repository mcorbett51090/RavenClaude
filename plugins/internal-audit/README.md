# internal-audit

> The **independent, objective assurance & advisory layer over ALL risk** for Claude Code — the team that answers *"what should internal audit look at, how do we test it, how bad is what we find — and how do we stay independent, conformant, and useful to the board?"* Two agents: the **internal-audit-lead** (the CAE-level function — the risk-based audit universe & annual plan, IIA-Standards conformance, independence & objectivity, the audit-committee reporting line, and the QAIP) and the **audit-engagement-specialist** (the engagement — planning memo & scope, risk & control matrix, testing, workpapers, 5-C findings, ratings, and follow-up).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "How do we rank our audit universe and build this year's plan?" | A residual-risk-ranked universe + a resource-balanced annual plan (assurance/advisory mix, cycle coverage) with the audit-committee residual-risk narrative and the conditions that would flip it |
| "Are we conformant with the 2024 IIA Standards, and where do we sit in the Three Lines Model?" | A conformance read across the 5 domains / 15 principles, the independence & audit-committee reporting-line setup, and a Three-Lines placement that keeps IA out of control ownership |
| "Stand up our QAIP — when's the external quality assessment due?" | A QAIP covering internal (ongoing + periodic) and external assessments, with the every-5-years EQA cadence and the conformance-statement basis |
| "Draft the planning memo and the risk & control matrix for this engagement." | A planning memo (objectives/scope/criteria/timing) + an RCM mapping each key risk → control → type → the tests of design and operating effectiveness |
| "How do we test this control, and what sample size?" | A test-of-design + test-of-operating-effectiveness plan and an attribute-sampling approach with a defensible sample size (population × frequency × tolerable deviation) |
| "The control failed on 3 of 25 — write it up." | A finding on the 5 C's (Criteria/Condition/Cause/Consequence/Corrective action), an impact×likelihood rating (high/med/low), and an agreed management action plan with owner + date |
| "Are our workpapers review-ready, and did the fix close?" | A workpaper set that meets the sufficiency/relevance/reliability bar, plus a follow-up plan that re-tests the remediated control before closing the issue |

**One rule it never breaks:** *internal audit assures and advises; it never owns the control it assures.* The moment IA owns a control, runs a process, or makes a management decision, its independence — and its assurance — is worthless. Advisory work is welcome; owning the remediation is not.

## What's inside

- **2 agents** — `internal-audit-lead` (the risk-based audit universe & annual plan, IIA-Standards conformance, independence & objectivity, the audit-committee reporting line, and the QAIP) and `audit-engagement-specialist` (the planning memo, risk & control matrix, tests of design & operating effectiveness, sampling, workpapers, 5-C findings, ratings, and follow-up).
- **3 skills** — `build-risk-based-audit-plan`, `plan-and-execute-audit-engagement`, `rate-and-report-audit-findings`.
- **2 knowledge files** — a Mermaid internal-audit decision tree (assurance-vs-advisory, risk-ranking the universe, sampling approach, issue-rating matrix + trade-off tables) and a 2026 internal-audit-patterns reference (IIA Global Internal Audit Standards / 5 domains / 15 principles, COSO Internal Control / 5 components, COSO ERM, the Three Lines Model, the engagement lifecycle, common audit programs, KPIs, and the QAIP / external-quality-assessment cadence).
- **2 templates** — an audit-engagement planning memo and an audit-finding & issue log.

## Where it sits in the assurance stack

```
internal-audit (HERE)          →  INDEPENDENT assurance & advisory over ALL risk  ("what to audit, how to test, how bad, report to the board")
cybersecurity-grc              →  deep security-control assurance                 ("ISO 27001 / NIST / SOC 2 control testing")
regulatory-compliance          →  AML / financial-regulatory obligations          ("the regulated-conduct rules")
esg-sustainability-reporting   →  ESG / sustainability assurance                  ("the ESG disclosures")
process-improvement            →  redesigning the audited process                 ("fix the process, don't just assure it")
```

This plugin is the **independent assurance function**: it decides what to audit, tests whether controls over the in-scope risks are designed and operating effectively, rates and reports what it finds to the audit committee, and validates remediation — while staying clear of the *deep security-control* work (`cybersecurity-grc`), the *AML/financial-regulatory* obligations (`regulatory-compliance`), the *ESG assurance* (`esg-sustainability-reporting`), and *owning the control* it assures.

## Domain stance

Standards-first (the **IIA Global Internal Audit Standards** 2024 / 5 domains / 15 principles, **COSO Internal Control** 5 components + **COSO ERM**, the **Three Lines Model** 2020), and method-disciplined across the engagement lifecycle — risk-based universe → annual plan → planning memo/criteria → risk & control matrix → walkthrough → test of design + operating effectiveness → attribute sampling → workpapers → 5-C findings → impact×likelihood rating → audit-committee report → management action plans → follow-up re-test → QAIP + external quality assessment (every 5 years). **Independence is the through-line: IA assures and advises, never owns the control.** Standard versions, effective dates, the EQA cadence, and any sample-size numbers carry retrieval dates — re-verify before pinning in a board or client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install internal-audit@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
