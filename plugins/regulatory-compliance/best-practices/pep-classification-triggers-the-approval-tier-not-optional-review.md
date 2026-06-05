# PEP Classification Triggers the Approval Tier, Not Optional Review

**Status:** Absolute rule
**Domain:** AML / KYC
**Applies to:** `regulatory-compliance`

---

## Why this exists

Politically Exposed Person (PEP) classification is frequently treated in practice as a flag that prompts a more thorough KYC review, when the regulatory requirement is stronger: a PEP classification triggers a mandatory higher-approval tier and, in most FATF-implementing regimes, prohibits onboarding without senior management approval. The distinction matters because "enhanced review" is a judgment call by the analyst; "senior management approval" is a governance gate. When an analyst reviews a PEP file and concludes "looks fine — proceeding," they have short-circuited the governance structure the AML regime is designed to require. Examiners check that the approval tier was invoked, not just that the file looks thorough.

## How to apply

Treat PEP classification as a governance gate, not a risk-rating modifier.

```
PEP Classification Workflow
──────────────────────────────────────────────────────
Step 1 — CLASSIFY (before any file-building begins)
  Screen the customer and their beneficial owners against PEP databases.
  PEP categories: Foreign PEPs (highest risk) | Domestic PEPs | IO/IO officials |
  Family members / close associates of the above.
  Note: classification does not require current office-holding — most regimes
  apply PEP status for 12–24 months after leaving office; check jurisdiction.

Step 2 — ROUTE BASED ON CLASSIFICATION
  PEP identified → mandatory EDD → mandatory senior management approval BEFORE
  establishing the relationship (or before continuing an existing relationship
  for a customer whose PEP status was identified after onboarding).
  "Senior management" is defined in the firm's AML policy — must be at least
  one tier above the relationship manager.
  No exception: a PEP cannot be onboarded without the approval gate, regardless
  of relationship size, expected transaction volume, or existing relationship.

Step 3 — DOCUMENT THE APPROVAL
  Record: name and title of approver, date, summary of EDD review outcome,
  explicit statement that the relationship was approved with PEP status known.
  Retain in the KYC file.

Step 4 — APPLY ENHANCED ONGOING MONITORING
  Flag the account for enhanced transaction monitoring.
  Set periodic review cadence to annual (regardless of standard risk-tier schedule).
```

**Do:**
- Build the PEP-approval gate into the onboarding workflow as a system control, not a checklist item the analyst can skip.
- Re-check PEP status on every periodic review — a customer can become a PEP between reviews.
- For family members and close associates of a PEP, apply the same approval tier; the FATF framework extends the classification.

**Don't:**
- Accept "the PEP left office two years ago" as a reason to waive the approval gate without checking the jurisdiction's de-PEP timeline.
- Use a relationship manager's opinion ("I know this person — they're clean") as a substitute for the senior management approval.
- Treat a foreign PEP and a domestic PEP as equivalent risk; foreign PEPs are typically higher risk under most FATF-aligned regimes; the approval tier should reflect that.

## Edge cases / when the rule does NOT apply

- **Public-sector banking mandated by law** (e.g., a central bank or government-mandated financial institution obligated to serve government officials) — the relationship may exist by legal requirement; document the mandate and still apply EDD and monitoring.
- **Lower-risk PEP products** — some jurisdictions permit a simplified PEP procedure for certain product types (e.g., pension products); verify the specific jurisdiction's rule and document the basis before applying any simplification.

## See also

- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — owns the PEP classification and EDD workflow.
- [`./edd-is-depth-not-document-count.md`](./edd-is-depth-not-document-count.md) — the EDD triggered by PEP classification must meet the depth standard described in this rule.

## Provenance

Codifies the AML/KYC-analyst's PEP governance discipline from the `kyc-edd-review` skill and CLAUDE.md §4 anti-pattern ("KYC EDD packages relying on a single source"). The senior-management approval requirement reflects FATF Recommendation 12 and its implementations in BMA AMLR 2008, CIMA AML guidance, and FinCEN/BSA regulations.

---

_Last reviewed: 2026-06-05 by `claude`_
