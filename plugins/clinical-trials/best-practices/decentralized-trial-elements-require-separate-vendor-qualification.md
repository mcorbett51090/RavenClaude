# Decentralized Trial Elements Require Separate Vendor Qualification

**Status:** Pattern
**Domain:** Decentralized clinical trials / vendor management
**Applies to:** `clinical-trials`

---

## Why this exists

Decentralized clinical trial (DCT) elements — home nursing visits, direct-to-patient drug shipment, telemedicine visits, wearable/ePRO data collection — introduce vendors who are not traditional clinical CROs but who are nonetheless collecting GCP-regulated data or performing protocol procedures. If these vendors are not qualified under a formal audit/qualification process, the data they generate may be challenged by regulators on inspection. DCT vendor gaps were flagged in FDA's 2023 DCT Guidance and subsequent inspection observations as a common compliance weakness.

## How to apply

Apply the same vendor qualification framework to DCT service providers that you apply to central labs and CROs.

```
DCT vendor qualification steps:
1. Classify the vendor's function:
   - Critical (performs protocol procedures or generates primary endpoint data) → full audit
   - Non-critical (e.g., package delivery, patient travel logistics) → QA questionnaire only

2. Qualification audit for critical DCT vendors:
   [ ] QMS (Quality Management System) documentation reviewed
   [ ] SOPs for the specific service reviewed (e.g., home visit SOP, wearable data transfer SOP)
   [ ] Data security and PHI handling compliance confirmed (HIPAA/GDPR as applicable)
   [ ] GCP training records for personnel performing protocol procedures
   [ ] Chain of custody for investigational product in direct-to-patient shipments

3. Contractual requirements:
   [ ] Quality Agreement executed before any subject enrolled
   [ ] Data transfer agreement with format and frequency specified
   [ ] Audit rights clause included

4. Ongoing oversight:
   [ ] Performance metrics tracked (visit completion rate, data transmission latency)
   [ ] Issue escalation pathway documented
```

**Do:**
- Include DCT vendors in the Trial Master File vendor list and track their qualification status.
- Confirm the telemedicine platform and home-nursing agency have GCP training programs before contracts are signed.
- Map each DCT data stream to the protocol-specified source data definition so auditors can trace source-to-database.

**Don't:**
- Treat patient-facing technology vendors (ePRO app providers, wearable vendors) as commercial software vendors exempt from qualification.
- Allow home-nursing visits to begin before the nurse agency's staff have been trained on the protocol procedures they will perform.
- Assume that a vendor's ISO certification substitutes for GCP qualification.

## Edge cases / when the rule does NOT apply

Fully on-site, traditional-site trials with no decentralized elements are outside scope. Observational registry studies using consumer wearables as exploratory data may use a lighter qualification standard if the data is not a regulatory endpoint.

## See also

- [`../agents/clinical-operations-manager.md`](../agents/clinical-operations-manager.md) — owns vendor management and site/DCT activation.
- [`./risk-based-monitoring-requires-a-written-plan-not-a-vague-policy.md`](./risk-based-monitoring-requires-a-written-plan-not-a-vague-policy.md) — DCT vendor risks belong in the monitoring plan's risk assessment.

## Provenance

Grounded in FDA Guidance for Industry: Decentralized Clinical Trials for Drugs, Biological Products, and Devices (2023); ICH E6(R3) §5.2 (sponsor responsibilities for vendors); standard CRO DCT operational practice emerging since 2021.

---

_Last reviewed: 2026-06-05 by `claude`_
