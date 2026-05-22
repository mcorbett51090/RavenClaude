---
name: risk-register-build
description: Build / refresh an enterprise risk register that survives audit committee scrutiny — three lines of defense assignment, inherent + residual rating math, KRI design, risk-appetite mapping, control coverage, and the half-yearly refresh cadence. Reach for this skill when standing up a new ORM/ERM framework, refreshing the register, or remediating an "outdated register" finding. Used by `risk-and-controls-specialist` (primary) and `policy-and-procedure-writer`.
---

# Skill: risk-register-build

**Purpose:** Build a risk register that an audit committee, a regulator, and a second-line ORM/ERM function can all use. A register that satisfies one but not the other two is not a risk register — it's a spreadsheet. Used by `risk-and-controls-specialist` (primary) and `policy-and-procedure-writer`.

## When to use

- Standing up an ORM / ERM framework for the first time
- Refreshing an existing register (half-yearly is the cadence floor; annually is the *very* slow end)
- Remediating an "outdated risk register" exam finding
- Acquired-entity integration (taxonomy mapping)
- New-product risk assessment (a register row before launch; not after)
- Pre-board / pre-audit-committee paper preparation

## Reference frameworks (cite the one you're using)

- **COSO ERM 2017** — *Enterprise Risk Management — Integrating with Strategy and Performance*. The most-cited ERM framework; supports the appetite-statement-first discipline.
- **ISO 31000:2018** — *Risk management — Guidelines*. Process-oriented; useful where COSO feels US-centric.
- **Basel III / Pillar 2** — for banks. ICAAP and ILAAP risk identification feed the register.
- **Solvency II (Pillar 2 — ORSA)** — for EU/UK insurers. The ORSA process and the risk register feed each other.
- **BMA — Insurance Code of Conduct + Group Supervision Rules** — for Bermuda insurers; the Code-mandated risk-management framework is the register's regulatory anchor.

House opinion #1: name the framework, cite the section. "Per the firm's ERM policy" is not enough on the cover page of a board-bound register.

## Risk taxonomy — the top-level categories

Most firms use 7–9 top-level categories. A standard taxonomy:

| Category | What's in it | Example |
|---|---|---|
| **Strategic** | Business model, market position, M&A, capital allocation | Loss of access to a key reinsurance market |
| **Operational** | Process, people, systems failures; execution | A claims-handling error rate above tolerance |
| **Financial** | Liquidity, credit, market, capital, FX, interest-rate | A counterparty default in the investment portfolio |
| **Compliance** | Regulatory rule breach; AML / sanctions / market-conduct | An SAR not filed within the statutory window |
| **IT / Cyber** | Confidentiality / integrity / availability; cyber attack; vendor IT failure | A ransomware event affecting policy admin |
| **Conduct** | Customer outcomes; mis-selling; treating-customers-fairly | A product sold outside its suitability envelope |
| **Reputational** | Brand / stakeholder perception; ESG-adjacent | Adverse media tied to a sanctions-tier customer |
| **Legal** | Litigation, contract enforceability, IP, employment | A class action arising from a coverage dispute |

Sub-categories live one level down; don't go more than 3 levels deep on the taxonomy — registers stop being usable.

## The risk-statement format

A risk *row* is sloppy. A risk *statement* is structured. Use the cause–event–consequence pattern:

> **In** \[activity / process / function\], **we are exposed to** \[event\] **caused by** \[driver(s)\], **leading to** \[consequence — quantified where possible\].

Examples:

- *In* policy underwriting, *we are exposed to* writing business outside the appetite *caused by* underwriter discretion exceeding documented authorities, *leading to* unmodeled loss exposure (>$X) and capital-adequacy variance.
- *In* customer onboarding, *we are exposed to* onboarding a sanctioned UBO *caused by* incomplete beneficial-ownership screening on legal-entity customers, *leading to* OFAC blocking action, regulatory enforcement, and reputational loss.

Statements that don't follow this shape are vague ("operational risk") or impossible to score ("things could go wrong with claims"). The shape forces the analyst to identify driver and consequence — without which, controls can't be designed.

## Inherent rating — 5x5 likelihood × impact

**Inherent risk** is the risk *before* any controls. Many firms cheat and start with residual ("we have controls so it's low"). The exam finding writes itself: "the firm cannot demonstrate the gross exposure being managed."

Likelihood:

| Score | Label | Heuristic |
|---|---|---|
| 1 | Rare | Less than once in 10 years |
| 2 | Unlikely | Once in 5–10 years |
| 3 | Possible | Once every 2–5 years |
| 4 | Likely | Once a year or more |
| 5 | Almost certain | Multiple times a year |

Impact (calibrate to the firm — example for a mid-sized insurer):

| Score | Financial | Regulatory | Customer / conduct | Reputational |
|---|---|---|---|---|
| 1 | <$100k | Minor; correctable | <10 customers | Limited internal awareness |
| 2 | $100k–$500k | Letter; written remediation | <100 customers | Local trade media |
| 3 | $500k–$5M | MRA / management letter | <1,000 customers | Industry trade media |
| 4 | $5M–$25M | MRIA / enforcement | <10,000 customers | National media |
| 5 | >$25M | Public action / licence at risk | >10,000 customers | International media |

The firm's actual rubric should be in the ERM policy and cited on every register row.

**Inherent rating = max(impact dimensions) × likelihood**, or a weighted approach if the firm's policy specifies. **Document which.**

## Control inventory — design + operating effectiveness

For each risk, list the controls that mitigate it. For each control:

| Field | What's in it |
|---|---|
| **Control ID** | Stable identifier across refreshes |
| **Description** | What the control does, plainly stated |
| **Type** | Preventive / Detective / Corrective |
| **Automation** | Manual / Semi-automated / Automated |
| **Frequency** | Continuous / Per-transaction / Daily / Weekly / Monthly / Quarterly / Annual / Event-driven |
| **Owner** | Named owner (a role; back-up named) |
| **Design assessment** | Adequate / Partially adequate / Inadequate, with rationale |
| **Operating effectiveness** | Effective / Partially effective / Ineffective, with last-test date + sample size + result |
| **Line of defense** | 1st / 2nd / 3rd |

The design vs operating-effectiveness distinction matters. A well-designed control that doesn't operate is the same risk as no control. A control that operates but isn't well-designed catches only the events it was sized for.

## Residual rating math

**Residual rating = inherent rating reduced by control effectiveness.** The firm's policy should specify the math (matrix lookup, multiplicative, additive — any of these is acceptable if documented). The most common, defensible approach:

| Combined control effectiveness | Reduction from inherent |
|---|---|
| Strong (design adequate + operating effective) | -2 risk levels |
| Adequate (one or both partial) | -1 risk level |
| Weak (any inadequate / ineffective) | 0 (residual = inherent) |
| Materially failed | +0 to +1 (residual *worse* than inherent under specific conditions, e.g., over-reliance creates blind spots) |

Residual is never lower than the firm's risk appetite would tolerate without action. If residual exceeds appetite, the row triggers a remediation plan with date + owner (house opinion #5).

## Risk-appetite statement — the front of the register

The register is meaningless without a stated appetite. The appetite statement names the categories the firm will / won't take, and the tolerance per category. Format:

> The firm has a **\[low / moderate / high\]** appetite for **\[category\]**. The firm tolerates **\[quantified threshold\]** in this category. The firm has zero tolerance for **\[carve-outs — e.g., breaches of sanctions, market manipulation, customer-data exposure beyond regulatory threshold\]**.

Examples:

- The firm has a **low** appetite for **compliance risk** and **zero tolerance** for **AML / sanctions breaches**. The firm tolerates up to **$X** in compliance-cost (fines, remediation) in any rolling 12 months before the appetite is breached.
- The firm has a **moderate** appetite for **credit risk** in the investment portfolio. Tolerance: max **Y%** below-investment-grade exposure; max **Z%** single-counterparty.

Each register row maps to one or more appetite statements. A row with residual exceeding appetite is an appetite breach — escalate.

## KRI design — leading and lagging

A KRI (Key Risk Indicator) is a quantitative signal that a risk is trending toward / away from the appetite threshold.

| Type | What it tells you | Examples |
|---|---|---|
| **Leading** | The risk is changing *before* the consequence materializes | AML alerts per 1,000 customers; KYC files past refresh date; sanctions-list age since last vendor update |
| **Lagging** | The consequence has materialized | SARs filed; sanctions blocking actions; MRA / MRIA count; customer complaints upheld |

A good register has 2–4 KRIs per material risk, mixing leading and lagging. KRI design includes:

- **Definition** (calculation in plain English)
- **Source data** (system, report, query)
- **Threshold** (green / amber / red — usually 3-tier)
- **Frequency of measurement**
- **Owner** (who runs the KRI)
- **Escalation path** when amber / red trips

KRIs without thresholds are metrics, not indicators. KRIs without owners are decorations.

## Three lines of defense — ownership column

Every register row maps to all three lines:

| Line | Function | On the register |
|---|---|---|
| **1st** | Business / operations — owns the risk | "Risk owner" — the business head accountable |
| **2nd** | Risk + compliance — oversees and challenges | "Risk-oversight owner" — typically CRO, CCO, AML Officer |
| **3rd** | Internal audit — provides independent assurance | "Assurance owner" — internal audit (or co-sourced auditor) |

House opinion #3: these are different functions. A register that lists the same person under 1st and 2nd line is a finding. The CRO is 2nd line; they don't own the underwriting risk (the chief underwriter does).

## Refresh cadence

| Trigger | Action |
|---|---|
| Half-yearly (minimum) | Full refresh: inherent / control / residual / KRI / appetite mapping |
| Annual | Top-to-bottom refresh + appetite-statement re-approval at board |
| Trigger event | Material new product, M&A, regulatory change, large incident, exam finding |
| Quarterly | Light-touch: KRI report; new/closed rows; appetite-breach review |

A register last refreshed >12 months ago is a regulator-finding by default in most regimes.

## Link to control testing

Operating-effectiveness ratings on the register must trace to actual test evidence. The 2nd-line control-testing program (see `control-testing` skill) produces the evidence. A register cell that says "operating effectiveness: Effective" with no last-test date or testing-program reference is wishful thinking.

## Common findings

- Risks stated as one-word labels ("Cyber") rather than cause–event–consequence statements
- No inherent rating; only residual — can't demonstrate the gross exposure
- Control effectiveness recorded without test evidence
- Same person listed as 1st and 2nd line on the same row
- Appetite statement absent or undated
- KRIs without thresholds, or thresholds never re-calibrated
- Risk-rating rubric different per row (analyst preference, not firm standard)
- Risks closed without documented rationale
- New products launched with no register row added

## Anti-patterns

- A register treated as an audit deliverable, not a management tool — refreshed only when the auditor asks
- "Heatmap" produced with no underlying register
- Risk appetite written in qualitative platitudes ("we have a prudent appetite for risk") with no quantitative anchor
- Residual lower than inherent with no documented control effectiveness
- KRIs that nobody reports on
- Risks duplicated across business units because the taxonomy isn't enforced centrally

## See also

- Skill: [`./control-testing.md`](./control-testing.md)
- Skill: [`./regulatory-mapping.md`](./regulatory-mapping.md)
- Skill: [`./examination-readiness.md`](./examination-readiness.md)
- Template: [`../templates/risk-register.md`](../templates/risk-register.md)
- Template: [`../templates/control-narrative.md`](../templates/control-narrative.md)
- Agent: [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md)
- Agent: [`../agents/policy-and-procedure-writer.md`](../agents/policy-and-procedure-writer.md)
