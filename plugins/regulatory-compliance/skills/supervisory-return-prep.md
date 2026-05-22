---
name: supervisory-return-prep
description: Period-end supervisory / regulatory return preparation playbook — data lineage, maker-checker, materiality / threshold definitions, common return families (FATCA, CRS, BMA EBS, Solvency II, supervisory returns, capital adequacy / RBC), late-filing protocols. Reach for this skill 4-6 weeks before a periodic filing or when responding to a regulator data request. Used by `regulatory-reporting-analyst` (primary).
---

# Skill: supervisory-return-prep

**Purpose:** Period-end supervisory / regulatory return preparation. The discipline that turns "we have the data somewhere" into "we filed on time, with a documented maker-checker chain, against a calibrated materiality threshold, and we can defend every line to the regulator." Used by `regulatory-reporting-analyst` (primary).

## When to use

- 4–6 weeks before any periodic filing deadline
- Responding to an ad-hoc regulator data request (treat it like a return; the discipline is the same)
- Designing or refreshing the filing-calendar control
- Recovering from a late-filing incident
- Acquired-entity integration where the new entity's filing calendar joins the firm's

## The filing-calendar discipline

The single largest source of late-filing exposure is a calendar that nobody owns. Build / maintain a filing calendar with the following columns:

| Field | Notes |
|---|---|
| **Return name** | Full regulator-side name (e.g., "BMA Economic Balance Sheet Quarterly Return"), not internal shorthand |
| **Regulator** | Named body (e.g., BMA, FinCEN, HMRC, IRS, EIOPA-via-local-supervisor) |
| **Citation** | The rule that mandates the return (e.g., BMA Insurance Returns and Solvency Regulations, regulation 4) |
| **Frequency** | Annual / Semi-annual / Quarterly / Monthly / Event-driven |
| **As-of date** | Period-end the return reports on |
| **Statutory deadline** | The regulator-published filing deadline; convert to local time / business-day calendar |
| **Internal target** | At least 5 business days before statutory — gives time for late issues |
| **Submission portal / method** | Named (e.g., BMA Connect, IRS IDES, regulator email + signed certification) |
| **Filer** | Named maker — the person who prepares and submits |
| **Checker** | Named checker — independent reviewer who signs off before submission |
| **Approver** | Named approver — typically MLRO / CCO / CFO / CRO depending on return |
| **Status** | Not started / In progress / Maker-complete / Checker-complete / Submitted / Acknowledged |

Calendar reviewed monthly with the regulator-reporting team; quarterly with the CFO / CRO; annually with the audit committee.

## Source-system to return-line mapping

For every line on every return, identify the source. This is the **data lineage**:

| Return line | Source system | Source report / table | Transformation | Tied-out to |
|---|---|---|---|---|
| e.g., Solvency II QRT S.02.01 Technical Provisions | Actuarial valuation system | Year-end valuation pack v3 | Re-grouping per QRT taxonomy + currency conversion at year-end FX | Audited annual statutory accounts |
| e.g., FATCA Form 8966 line 4a (Reportable Account Balance) | Policy admin system | Reportable accounts extract | Aggregation per Account Holder; conversion to USD at year-end FX | Bank reconciliation + policy admin trial balance |

Every line should tie out to a financial-statement / audited number where one exists, or to the source-system record-set where it doesn't. Lines that don't tie are the late-night-before-filing problem.

## Materiality / threshold definitions — per return

House opinions #7 and #12: "material" varies by regulator and by topic. Document, per return:

- The materiality threshold used (e.g., for reasonableness checks)
- The regulator's mandatory thresholds (e.g., reportable-balance thresholds for FATCA / CRS; capital-adequacy stress thresholds for RBC; ratio-of-change disclosure thresholds for Solvency II)
- How the threshold is calibrated (% of total / fixed amount / both)
- Where it differs from the firm's financial-statement materiality

A common audit finding is a single firm-wide materiality applied to all returns regardless of regulator. Don't.

## Maker-checker workflow

The maker-checker chain is the central control. House opinion #6 (default to written) demands:

1. **Maker prepares** the return per the source-to-line mapping.
2. **Maker self-reviews** against a return-specific checklist (see `templates/supervisory-return-checklist.md`).
3. **Maker hands off** to checker with: filled return, source-system extracts referenced, reconciliations attached, open items log.
4. **Checker reviews** independently — re-pulls a sample of source data, tests the transformation, evaluates open items.
5. **Checker signs off** with timestamp and a documented review note ("Reviewed lines X–Y by independent re-extract; reconciliations tied; open items resolved or escalated").
6. **Approver signs** the certification (where the return requires a CEO / CFO / MLRO certification).
7. **Filer submits** through the portal; captures submission receipt + timestamp + filer name + IP / portal-session evidence.
8. **Acknowledgment captured** from the regulator (where the portal provides one).

The whole chain is timestamped; no step is verbal.

## Reasonableness / bridging checks

Before sign-off, every return should pass at least:

- **Period-over-period bridge** — what changed from the prior period's return; explanation per material variance with documented driver
- **Tie-out to financials** — every monetized line that exists in the audited / signed statutory accounts ties, with a documented reconciliation for any cap-related differences
- **Internal consistency** — figures referenced on multiple lines / forms reconcile to themselves
- **Plausibility** — material lines compared to industry / peer / public data where available; outliers flagged

A return with no period-over-period bridge is the classic regulator finding "the filer could not explain the variance."

## Common return families and their gotchas

### FATCA (US — IRS)

- **Citation:** 26 USC §1471–1474; Treasury Regs §1.1471–§1.1474.
- **Schedule:** Forms 8966 / 1042-S due **31 March** following the reporting year (US-based filers); FFI-jurisdiction agreements may give a different schedule (e.g., Model 1 IGA jurisdictions usually 31 March to the local competent authority).
- **Gotchas:** Reportable Account vs Account Holder distinctions; controlling-person tests on passive NFFEs; sponsoring-entity structures; nil returns (some jurisdictions accept; some require submission); aggregation rules where the FI has multiple branches.
- **Common errors:** Account-balance translation at the wrong FX date; missed reporting on dormant accounts above threshold; incorrect TIN-not-available coding.

### CRS (OECD — local competent authority)

- **Citation:** OECD Standard for Automatic Exchange of Financial Account Information in Tax Matters (2014 + 2017 commentary); local implementing legislation (e.g., Bermuda's International Cooperation (Tax Information Exchange Agreements) Act + CRS Regulations).
- **Schedule:** Typically end of May / mid-July following the reporting year, to the local competent authority who then exchanges by 30 September.
- **Gotchas:** Self-certifications must be valid (signed, dated, current); the broad scope of "Investment Entity" relative to FATCA; controlling-person definitions; the wider participating-jurisdiction list.
- **Common errors:** Self-certification validity not re-tested on material change; reportable accounts undercounted because of narrower-FATCA-thinking; XML schema validation errors at submission.

### BMA EBS (Economic Balance Sheet)

- **Citation:** BMA Insurance (Prudential Standards) (Insurance Group Solvency Requirement) Rules 2011 (and equivalent for solo classes); BMA EBS Framework Guidance.
- **Schedule:** Annual EBS with the Annual Statutory Return + capital-and-solvency-return cycle; quarterly EBS reporting in addition for relevant classes.
- **Gotchas:** Best-estimate liability vs statutory liability; risk-margin calculation; recoverable from reinsurance under EBS; commercial-insurer vs captive class distinctions.
- **Common errors:** Reconciliation between EBS and statutory accounts not documented; risk-margin methodology not consistently applied period-over-period.

### Solvency II QRTs / SFCR / RSR (EU / UK insurers)

- **Citation:** Directive 2009/138/EC; Delegated Regulation 2015/35; EIOPA implementing technical standards; UK PRA's post-Brexit rulebook for UK-domiciled.
- **Schedule:** Quarterly QRTs (group + solo); annual QRTs + SFCR (public) + RSR (regulator-only); ORSA at least annually.
- **Gotchas:** Look-through on collective investment vehicles; SCR calculation under standard formula vs internal model; group-vs-solo consolidation perimeter; transitional measures.
- **Common errors:** XBRL taxonomy version mismatched to filing window; look-through skipped on a fund-of-funds; group-currency translation inconsistency.

### Capital adequacy / RBC (insurers / banks)

- **Citation:** Bermuda's BSCR (Bermuda Solvency Capital Requirement) for commercial classes; for banks, Basel III as implemented locally (BMA Banking Code; equivalent in other regimes); NAIC RBC for US insurers.
- **Schedule:** Annual with quarterly look-through where the regime requires.
- **Gotchas:** Capital-tier classification; transitional grandfathering; concentration adjustments; counterparty default add-ons.
- **Common errors:** Subordinated-debt eligibility misclassified; concentration measured at issuer level instead of group level.

### Other supervisory returns (BMA, FCA, PRA, MAS, equivalents)

- **Always:** read the regulator's most recent filing instructions and not last year's. Schemas drift.

## Late-filing protocol — *before* the deadline, not after

If the return will not be filed on time:

1. **Notify before the deadline.** Most regulators respond very differently to "we expect a 5-day delay because X, here is our plan" submitted *before* the deadline vs the same message submitted after.
2. **Document the cause** in writing: data-quality issue, system outage, scope expansion, etc.
3. **Estimate revised filing date** and commit only what you can hit.
4. **Identify the gap-bridging artifact** — what you'll submit in lieu, if anything (provisional return, attestation, partial submission).
5. **Track to a remediation owner + date** — house opinion #5. Late filing without a structural fix is a recurring finding.
6. **Reflect in the risk register** — late filing is a residual-risk-against-appetite event.

## Amendment / restatement protocol

When an already-filed return needs amendment:

1. Identify what's changing and the materiality of the change against the regulator's restatement threshold (where one exists).
2. If material: file a formal amendment + cover letter explaining the change + root cause + remediation.
3. If immaterial but disclosed for completeness: file per the regulator's accepted method (some accept correction in the next return; some require formal amendment).
4. Update the return-prep procedure and the risk register to address the root cause.

## Common findings

- No filing calendar at all, or calendar maintained by one person with no backup
- Source-to-line mapping exists in someone's head, not in writing
- Maker and checker is the same person on multiple returns
- Materiality threshold not stated, or one threshold across all regulators
- No period-over-period bridge documented
- Submission receipt not captured / not stored with the return
- Late filing recurring across multiple periods with no remediation plan
- Restated return filed with no cover-letter explanation
- Regulator data-request answered without the maker-checker discipline applied

## Anti-patterns

- "We've always filed it this way" — schemas change; re-validate
- Source data from spreadsheets without lineage to the underlying system
- Filing the same as the prior period with figures updated in the same cells, no re-mapping
- The CFO certifies without independent review of the cert content
- Treating an ad-hoc regulator data request as informal — the maker-checker discipline still applies
- Verbal handoff from maker to checker

## See also

- Skill: [`./control-testing.md`](./control-testing.md)
- Skill: [`./regulatory-mapping.md`](./regulatory-mapping.md)
- Skill: [`./examination-readiness.md`](./examination-readiness.md)
- Template: [`../templates/supervisory-return-checklist.md`](../templates/supervisory-return-checklist.md)
- Template: [`../templates/control-narrative.md`](../templates/control-narrative.md)
- Agent: [`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md)
- Agent: [`../agents/bermuda-insurance-specialist.md`](../agents/bermuda-insurance-specialist.md)
