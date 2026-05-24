---
name: aml-program-review
description: Structured review of an AML program against FATF / FFIEC expectations — the 5 pillars, common findings, regulatory citations with primary sources. Used by `aml-kyc-analyst` (primary).
---

# Skill: aml-program-review

**Purpose:** Structured review of an AML program against FATF / FFIEC expectations. Used by `aml-kyc-analyst` (primary).

## When to use

- Pre-exam AML program review
- Annual independent review (mandated under most regimes)
- Post-incident program assessment
- New-licence applicant readiness check
- Acquired-entity integration

## The 5 pillars (US BSA / FFIEC framework; equivalent concepts in most regimes)

Most regulators expect an AML program with these components:

1. **Designated AML Officer** with appropriate authority, resources, board access
2. **Internal policies, procedures, and controls** for CDD, EDD, transaction monitoring, sanctions, reporting
3. **Ongoing training** for relevant employees, with records
4. **Independent testing** at appropriate frequency, with documented findings + remediation
5. **CDD / beneficial-ownership** identification + ongoing risk-based monitoring

(Bermuda's AMLR 2008 captures equivalent concepts with different structure; map them on review.)

## Review structure

For each pillar, assess:

- **Design** — does the documented program meet the regulator's expectations?
- **Implementation** — does what's done in practice match what's documented?
- **Effectiveness** — does the implementation actually catch what it's supposed to catch?

A program can be well-designed but poorly implemented, or implemented as designed but ineffective at catching what it should. Differentiate.

## Common findings (in order of frequency in mid-market firms)

### Design findings

- BOI verification weak (relies on customer's own statement for higher-risk corporate customers)
- EDD triggers documented but actual EDD content is the same as CDD with more pages
- Sanctions screening covers customers but not connected parties / counterparties
- Negative-news screening has no documented procedure
- Transaction monitoring rule set never validated; thresholds at vendor defaults
- AML training is generic; doesn't reflect the firm's actual product / customer base

### Implementation findings

- KYC files have gaps (missing BOI, expired ID, no risk rating recorded)
- Sanctions hits cleared with no documented rationale
- Alert backlogs (TM alerts unworked beyond regulator-expected SLAs)
- SAR / STR filings sparse; no continuing-activity reports
- Periodic refresh skipped on higher-risk customers
- AML Officer not actually independent (also runs operations)

### Effectiveness findings

- Independent-testing reports never trigger material remediation
- Training records exist but knowledge doesn't (interviews fail)
- Board / committee minutes show no substantive AML discussion
- Risk assessment static for years; new products / customers / geographies not reflected

## Report structure

For each pillar, produce:

| Pillar | Design (✅ / ⚠️ / 🔴) | Implementation (✅ / ⚠️ / 🔴) | Effectiveness (✅ / ⚠️ / 🔴) | Findings | Severity (P0 / P1 / P2) |
|---|---|---|---|---|---|

Plus:
- **Top 3 remediations** prioritized
- **Regulator-exposure score** (e.g., "BMA exam unlikely to clear without addressing finding #1")
- **Recommendation** (e.g., refresh program, targeted remediation, comprehensive rebuild)

## Severity guide

- **P0** — program fails a regulator's published expectation; remediate before next exam window.
- **P1** — program meets expectations on paper, fails in practice; remediate before next refresh.
- **P2** — improvable; not a current gap.

## Anti-patterns the review catches

- Program designed by the vendor template, customized only by find-and-replace
- "Independent" testing done by the team being tested
- AML Officer with no actual authority to escalate to the board
- Training records that don't tie to the people actually doing AML work
- "We follow industry best practice" used as substantive policy text

## See also

- Skill: [`../sar-narrative-drafting/SKILL.md`](../sar-narrative-drafting/SKILL.md)
- Template: [`../../templates/aml-program-outline.md`](../../templates/aml-program-outline.md)
- Template: [`../../templates/kyc-edd-workpaper.md`](../../templates/kyc-edd-workpaper.md)
- Agent: [`../../agents/aml-kyc-analyst.md`](../../agents/aml-kyc-analyst.md)
