---
description: "Plan an attest engagement and produce a PBC (provided-by-client) request list: independence analysis, materiality, risk assessment, and a structured PBC organized by audit area with responsible contacts and due dates."
argument-hint: "[context, e.g. 'calendar-year manufacturer, ~$8M revenue, third year of audit, firm also does tax; fieldwork starts 2026-02-15']"
---

You are running `/accounting-firm-cpa:prep-audit-pbc`. Use the `audit-engagement-lead`
discipline and the `engagement-and-workpaper-management` skill.

## Steps

1. **Independence analysis.** Identify all existing firm services to this client (tax,
   CAS, advisory, prior attest). For each non-attest service, evaluate the independence
   threat using the engagement-type / independence tree in
   `knowledge/cpa-firm-decision-trees.md`. Document the threats, any available safeguards,
   and the conclusion (proceed / restructure / decline).

2. **Engagement planning.**
   - Select the applicable standard (SAS for GAAP-basis audit, SSARS for review/compilation,
     PCAOB for issuer).
   - Determine overall materiality (select benchmark and percentage; document rationale).
   - Determine performance materiality and trivial amount.
   - Identify qualitative factors that could lower quantitative thresholds.

3. **Risk assessment.**
   - Identify significant accounts and disclosures.
   - For each significant area, assess inherent risk (nature of the balance) and note
     fraud risk considerations (revenue recognition presumption always applies for audits —
     AU-C 240).
   - Note any prior-year audit adjustments, management estimates, or related-party transactions
     that elevate risk.

4. **PBC request list.** Produce a complete PBC request list using
   `templates/pbc-request-list.md` as the structure. Organize by audit area:
   - Revenue and accounts receivable
   - Inventory (if applicable)
   - Fixed assets and depreciation
   - Accounts payable and accrued liabilities
   - Debt and financing
   - Equity and capital structure
   - Payroll and compensation
   - Income taxes
   - Cash and bank reconciliations
   - Related-party transactions
   - Other significant accounts / disclosures

   For each item: description (be specific), format, audit area and assertion, responsible
   contact at the client, and due date. Issue date of the PBC list should be at least 2–3
   weeks before fieldwork start.

5. **Fieldwork timeline.** Produce a high-level engagement schedule: PBC list issued →
   PBC items due → fieldwork start → fieldwork end → manager review → partner review →
   draft report to client → management representation letter → report issuance.

6. **Staffing matrix.** Assign staff levels to each audit area based on complexity and
   risk level.

7. **Output.** Emit the Structured Output block. Handoffs: `firm-practice-lead` for
   engagement economics; `cas-engagement-lead` if CAS restructuring is needed for
   independence; `regulatory-compliance` for standard interpretation questions.
