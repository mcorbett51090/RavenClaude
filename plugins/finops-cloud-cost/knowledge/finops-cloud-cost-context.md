# FinOps & Cloud Cost Benchmarks & Context (2025–2026)

> Orientation for the team. **Every figure and regulatory statement here is `[unverified — training knowledge]`** and varies by geography, segment, and date. Confirm against a current, dated source before any deliverable, and route every professional/legal/regulatory determination to the qualified authority (CLAUDE.md §2, §3 #8).

## Where defensible benchmarks come from

Cloud pricing, discount rates, instance specs, and commitment terms **change constantly** and vary by region, account, and contract (EDP/PPA). The most defensible source is the provider's live pricing page and the org's own Cost and Usage data; published rates of thumb go stale fast. **Name the source and date, or mark the figure `[unverified — training knowledge]` and verify against the live pricing page (§3 #8).**

## The FOCUS standard (normalized cost & usage schema)

**FOCUS — the FinOps Open Cost & Usage Specification** — is the vendor-neutral open standard for normalized cloud/SaaS cost & usage billing data, and the industry-standard cost/usage data model. It gives one common schema across providers (AWS, Azure, GCP, Oracle, and others publish FOCUS-conformant exports), so allocation, unit-economics, and commitment analysis run off the same columns regardless of cloud. It is a FinOps Foundation / Linux Foundation project. **Prefer FOCUS-conformant exports over provider-proprietary billing formats** when normalizing spend across clouds.

**Current version: v1.4**, ratified by the FOCUS Steering Committee on 2026-06-04. Headline additions in v1.4 (2 datasets, 47 columns, 6 attributes, 17 glossary entries):

- **Invoice-to-usage reconciliation** — new **Invoice Detail** and **Billing Period** datasets let you tie invoiced amounts back to usage.
- **Expanded Contract Commitment dataset** — grows from 13 to 30 columns (payment models, lifecycle status, discount rates, fulfillment intervals) — richer inputs for the commitment-portfolio read (§3 #3).
- **`CommitmentProgramEligibilityDetails`** — a new column for commitment-coverage measurement.

FOCUS Validator conformance testing for **1.3 is available now**; **1.4 conformance support is expected later in Q3 2026**.

> Sources: https://www.finops.org/insights/introducing-focus-1-4/ ; https://focus.finops.org/focus-specification/ — retrieved 2026-07-09.

## Directional frames (illustrative only — `[unverified — training knowledge]`)

| Area | Directional frame | Must-verify |
|---|---|---|
| Allocation coverage target | Often framed as a high attribution threshold before optimizing | Set against the org's own tagging maturity |
| Savings-Plan / RI discount | Varies widely by term, payment, and family | Verify against the live pricing page, dated |
| Commitment coverage | Often framed as covering steady-state, not peak | Model against the rightsized baseline |
| Waste share of bill | Frequently cited as a meaningful fraction | Derive from the org's own utilization data |

## Operating rhythm

- **Allocation/showback review** monthly — coverage %, the ungoverned pile, and the team showback (§3 #1 #6).
- **Waste + rightsizing sweep** before any commitment cycle (§3 #4 #5).
- **Commitment portfolio review** before term expiry — coverage and utilization (§3 #3).
- **Forecast + anomaly review** continuously; budget against the forecast (§3 #7).

## The standing caution

Cloud-contract negotiation (EDP/PPA), tax treatment, and GAAP cost accounting are **the qualified authority's** call — the team frames the decision and routes it. Keep billing-account PII and named-customer cost attribution out of deliverables (§2).
