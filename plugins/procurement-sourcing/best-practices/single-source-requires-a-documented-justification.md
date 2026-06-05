# Single-Source Procurement Requires a Documented Justification

**Status:** Absolute rule
**Domain:** Sourcing / governance
**Applies to:** `procurement-sourcing`

---

## Why this exists

Single-source procurement — awarding a contract to one supplier without competition — is the highest-risk procurement action from both a financial and a governance standpoint. It is also the most common vehicle for procurement fraud and conflicts of interest. Without a documented justification reviewed by an authority outside the sourcing team, single-source awards have no independent check on whether they are genuinely justified or simply convenient. Procurement functions with strong governance require documented justification, a named approver, and a periodicity limit (even single-source situations should be re-tested against the market on a defined cycle).

## How to apply

Complete a single-source justification document before award and route it to the appropriate approval authority.

```
Single-Source Justification — Required Sections
──────────────────────────────────────────────────────
1. CATEGORY AND SPEND DESCRIPTION
   Category name | Estimated annual spend | Contract term proposed

2. JUSTIFICATION BASIS (select one — document the facts, not the preference)
   □ Proprietary technology / patented product — supplier holds unique IP; no substitute.
     Document: patent number or IP evidence; why no equivalent exists.
   □ Sole provider — only one supplier in the market can meet the technical requirement.
     Document: market scan performed (date, method, result).
   □ Emergency — unforeseeable urgent need; competition not practical in the timeframe.
     Document: nature of emergency; why competition was not possible; timeline.
   □ Continuity — switching costs exceed competitive savings; prior competitive event on record.
     Document: estimated switching cost; date of last competitive event.
   □ Strategic relationship — formal partner agreement where competition would violate terms.
     Document: agreement reference; applicable clause.

3. MARKET-TEST EVIDENCE
   Evidence that the market was reviewed even if full competition was not run:
   - Internet search for alternative suppliers: date + result
   - Industry contacts consulted: name + date + finding

4. RISK STATEMENT
   Concentration risk created by this sole source:
   - Financial risk of supplier failure (credit-rating indicator / HHI)
   - Mitigation plan (dual-qualification target date if applicable)

5. APPROVAL
   Requestor: <name + title>  Date: <YYYY-MM-DD>
   Procurement Lead approval: <name>  Date:
   Business owner approval:   <name>  Date:
   [If spend > $X: CFO or CPO approval]: <name>  Date:
```

**Do:**
- Set a dollar threshold above which single-source justifications require C-suite approval.
- Include a mandatory market-re-test date in the justification; even a justified single source should be re-evaluated on a defined cycle (typically 2–3 years for large spend).
- Log all single-source justifications in the procurement governance tracker for audit access.

**Don't:**
- Accept "we've always used this supplier" as a justification basis — continuity requires a documented cost-benefit comparison, not just history.
- Allow the business owner who chose the supplier to also be the approver of the single-source justification — the approval authority must be independent of the selection.
- Apply the emergency basis retroactively to cover a purchase that was already made.

## Edge cases / when the rule does NOT apply

- **Sole-source orders below the micro-purchase threshold** — a brief memo documenting the reason is sufficient; the full single-source form is not required.
- **Option-year exercises on an existing competitively-awarded contract** — the original competition is the justification; document the exercise against the original award, but a new SSJ form is not required.

## See also

- [`../agents/sourcing-lead.md`](../agents/sourcing-lead.md) — the engagement lead is responsible for governance sign-off on single-source awards.
- [`./supplier-risk-is-a-portfolio-not-a-checkbox.md`](./supplier-risk-is-a-portfolio-not-a-checkbox.md) — single-source suppliers are the highest-concentration items in the portfolio; the risk section of the SSJ should feed the portfolio risk register.

## Provenance

Codifies the sourcing-lead's governance discipline for non-competitive awards. The justification categories reflect standard US federal acquisition (FAR 6.302) and commercial procurement governance frameworks adapted to private-sector practice. The independent-approval requirement reflects standard procurement-fraud-prevention controls.

---

_Last reviewed: 2026-06-05 by `claude`_
