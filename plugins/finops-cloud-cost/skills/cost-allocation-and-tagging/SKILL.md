---
description: "Design and enforce a cloud tagging strategy, build a showback or chargeback model, define unit economics (cost per customer/request/feature), and allocate shared and untagged costs using documented, auditable methods."
---

# Cost Allocation & Tagging

**Purpose:** make cloud costs visible, attributed, and owned at the team, product, and feature level
so the inform phase of FinOps produces signal that drives optimization action.

## The operating loop

1. **Define the tagging taxonomy.** Mandatory tags (environment, team/owner, project/cost-centre,
   application, managed-by) and recommended tags (region override, data-classification, backup-
   policy). Document the allowed values for each mandatory tag — free-form tags are unqueryable.
2. **Enforce at resource creation time.** Tag policies (AWS Tag Policies, Azure Policy deny-on-
   missing-tag, GCP Resource Manager org policy) enforced in IaC. Retroactive tagging projects
   fail at scale. Use the `tagging-policy.md` template.
3. **Handle untagged cost.** Apply a documented fallback rule: proportional (split by the same ratio
   as tagged spend), direct (assign to a "shared" cost centre), or flag as a compliance violation
   and alert. Never silently absorb untagged cost into a single team's allocation.
4. **Design shared cost allocation.** Shared Kubernetes clusters, networking, security tooling,
   support contracts. Choose the method: proportional (by resource consumption metric), direct
   (explicit mapping), or even (equal split among n teams). Document the method version and the
   denominator so it is auditable.
5. **Build showback first.** Tag dimension → billing data join → team-level spend summary →
   dashboard or weekly digest to engineers. Use the `showback-chargeback-model.md` template. Run
   for 2-3 months before introducing chargeback.
6. **Advance to chargeback only after behavior has changed.** Chargeback = showback +
   GL journal-entry mapping + Finance sign-off. Requires an agreed allocation key per shared service
   and a monthly reconciliation process. Hand off to `finance` plugin for the GL entries.
7. **Define unit economics.** Numerator: attributed cloud cost for the product/feature.
   Denominator: agreed business metric (active customers, API requests, transactions). Get
   Finance/Engineering/Product to sign off on the denominator definition before publishing the
   metric. Track the trend; a rising unit cost is a signal.

## Anti-patterns

- A tagging strategy that lives in a wiki instead of an enforced IaC policy.
- Chargeback before showback — teams receiving a charge they cannot verify.
- A "shared cost" allocation that silently grows over time with no denominator review.
- Unit-economics definitions that change mid-quarter without a documented version.
- FOCUS column mappings assumed to be stable — they evolve; re-verify at use.

## Output

A tagging taxonomy doc (use `templates/tagging-policy.md`), a showback or chargeback design (use
`templates/showback-chargeback-model.md`), and a unit-economics definition with the agreed
denominator and a trend tracking plan.
