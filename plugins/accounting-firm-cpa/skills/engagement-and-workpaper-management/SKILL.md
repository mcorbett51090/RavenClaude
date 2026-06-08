---
description: "Plan and manage attest engagements end-to-end: independence analysis, engagement planning, risk assessment, PBC list design and tracking, workpaper standards, and report issuance under AICPA professional standards."
---

# Engagement and Workpaper Management

**Purpose:** run a US public-accounting attest engagement (audit, review, compilation, AUP) from
acceptance through report issuance — with independence confirmed, risk assessed, PBC items tracked,
and every workpaper number supported by a documented source.

---

## Entry point

Spawn when asked to plan an attest engagement, perform an independence analysis, draft a PBC
list, or review workpapers for completeness. Primary agent: `audit-engagement-lead`. Supporting:
`firm-practice-lead` (engagement economics), `cas-engagement-lead` (if CAS services create an
independence conflict).

---

## Phase 1: Engagement acceptance and independence

1. **Identify existing firm services to the client.** List all current engagements: tax,
   CAS, advisory, other attest. Each creates a potential independence threat.
2. **Independence threat analysis** (AICPA ET §1.200):
   - Self-review threat: firm prepared records or financial statements the firm will now audit
   - Self-interest threat: firm has a financial interest in the client
   - Advocacy threat: firm acts as advocate in a legal or regulatory proceeding for the client
   - Familiarity threat: long association; close personal relationship with client management
   - Intimidation threat: client management uses position to influence firm judgment
   - Management participation threat: firm performs management functions (makes decisions,
     signs checks, controls assets, supervises employees)
3. **Traverse independence tree.** Use the decision tree in
   [`../../knowledge/cpa-firm-decision-trees.md`](../../knowledge/cpa-firm-decision-trees.md).
   If a non-attest service impairs independence and cannot be restructured, decline the attest
   engagement or terminate the non-attest service.
4. **Document independence conclusion.** Independence documentation must include: threats
   identified, safeguards applied (or not available), and the conclusion. Must be in the file
   before the engagement letter is signed.
5. **Engagement letter.** Scope, standard applicable (SAS/SSARS/SSAE/PCAOB), fee, client
   responsibilities, report form, and timing. Use
   [`../../templates/engagement-letter.md`](../../templates/engagement-letter.md).

---

## Phase 2: Engagement planning

1. **Materiality determination** (audits):
   - Overall materiality: select benchmark and percentage. Common benchmarks and ranges:
     - Revenue: 0.5–1% for high-volume / low-margin; 1–3% for typical `[verify-at-use]`
     - Pre-tax income: 5–10% for stable profitable entities `[verify-at-use]`
     - Total assets: 0.5–1% for balance-sheet-heavy entities `[verify-at-use]`
   - Performance materiality: typically 50–75% of overall materiality `[verify-at-use]`
   - Trivial amount: below which misstatements are not aggregated (typically 3–5% of overall
     materiality `[verify-at-use]`)
   - Document the quantitative threshold AND qualitative factors that could lower it.
2. **Risk assessment:**
   - Understand the entity: business model, industry, regulatory environment, related parties,
     IT environment.
   - Identify significant accounts and disclosures.
   - Assess inherent risk (nature of the balance) and control risk (reliance on internal controls).
   - Fraud risk: revenue recognition presumption (AU-C 240); management-override risk is always
     significant — document regardless of control environment.
3. **Audit response design:**
   - For each significant account × assertion, design a procedure (substantive test, analytical
     procedure, or test of controls) responsive to the assessed risk.
   - Higher assessed risk → more rigorous procedures (larger sample, more items, end-of-period
     timing vs. interim).
4. **Staffing and timeline.** Assign staff levels to each area. Set fieldwork start/end dates,
   manager review date, partner review date, and report issuance date.

---

## Phase 3: PBC list design and tracking

1. **Organize by audit area.** Standard areas: revenue/AR, inventory, fixed assets, AP/accruals,
   debt, equity, payroll, income taxes, cash, related parties, other. Use
   [`../../templates/pbc-request-list.md`](../../templates/pbc-request-list.md).
2. **For each item, specify:**
   - Description: what exactly is needed (be specific — "accounts receivable aging as of 12/31"
     not "AR schedule")
   - Format: Excel, PDF, system export, confirmation
   - Audit area and assertion it supports
   - Responsible contact at the client
   - Due date
3. **Issue PBC list early.** Issue the PBC list at least 2–4 weeks before fieldwork start. Clients
   that receive it the day before fieldwork will not be ready.
4. **Track receipt status.** Log date received for each item. Items outstanding at fieldwork
   start are a scope risk — escalate to the engagement partner.
5. **Follow-up protocol:**
   - First follow-up: 1 week before fieldwork if item is outstanding
   - Second follow-up: at fieldwork start if item is still outstanding
   - Escalation: item outstanding more than 1 week into fieldwork → partner communicates to
     client management

---

## Phase 4: Workpaper standards

Every workpaper must have:
- **Header:** client name, period, workpaper reference (e.g., C-1), preparer, date prepared,
  reviewer, date reviewed.
- **Purpose statement:** what question this workpaper answers and what assertion(s) it addresses.
- **Procedures performed:** describe what was done (not just the result).
- **Source documentation:** every number has a tick mark that maps to a legend and to a source
  document (client schedule, third-party statement, confirmation, prior-year workpaper).
- **Conclusion:** does the workpaper support the audit objective or not? State it explicitly.
- **Open items:** list and clear before sign-off.

Workpaper review checklist:
- [ ] Header complete (client, period, reference, preparer, reviewer, dates)
- [ ] All numbers have tick marks with defined legend
- [ ] Source documents cross-referenced and included or indexed
- [ ] Procedures performed described (not just the result)
- [ ] Assertions addressed for each significant amount
- [ ] Conclusion stated explicitly
- [ ] No open items outstanding at sign-off

---

## Phase 5: Report issuance

1. **Clearance of all open items** before the report is drafted.
2. **Financial statement tie-out.** Every number in the financial statements ties to a workpaper.
3. **Representation letter** (audits/reviews): obtain a signed management representation letter
   before the report is issued. Do not issue the report without it.
4. **Report drafting.** Select the appropriate report form based on outcome:
   - Unmodified opinion: financial statements present fairly in all material respects.
   - Qualified opinion: material misstatement in a specific area, or scope limitation that is
     not pervasive.
   - Adverse opinion: pervasive material misstatements.
   - Disclaimer of opinion: scope limitation so pervasive that no assurance can be expressed.
5. **Engagement quality review (if required by firm policy or standards).** Quality reviewer
   signs off before report issuance for high-risk or public-interest engagements.
6. **Archive.** Archive the complete file within 60 days of report issuance (AICPA standard;
   PCAOB requires 7-year retention `[verify-at-use]`).

---

## Anti-patterns

- Independence analysis performed after the engagement letter is signed.
- PBC list issued at fieldwork start — not enough lead time for client preparation.
- Workpapers with numbers but no tick marks or source cross-references.
- Risk assessment that marks all accounts as "low risk" without documentation.
- Audit procedures carried forward from prior year without updating for current-year risk.
- Report issued without a signed management representation letter.

---

## Output

An engagement plan (independence conclusion, materiality, risk assessment, audit program), a
PBC request list organized by audit area, a workpaper review with a clearing list, and report
selection with documentation. Use [`../../templates/pbc-request-list.md`](../../templates/pbc-request-list.md).
