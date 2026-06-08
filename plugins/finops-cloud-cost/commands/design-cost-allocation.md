---
description: "Design a complete cost allocation system: tagging taxonomy with enforcement, showback or chargeback model with shared-cost allocation, unit-economics definition, and optional FOCUS spec adoption plan. Outputs filled templates and a handoff to finance for GL booking."
argument-hint: "[context, e.g. 'AWS+GCP, 8 engineering teams, Finance wants per-BU chargeback, currently no tags']"
---

You are running `/finops-cloud-cost:design-cost-allocation`. Use the `cost-allocation-engineer`
discipline, the `cost-allocation-and-tagging` skill, and the templates in `templates/`.

## Steps

1. **Tagging taxonomy.** Define mandatory tags: `environment` (prod/staging/dev), `team` or `owner`
   (the engineering team), `project` or `cost-centre` (the GL code or project ID), `application`
   (the service name), `managed-by` (terraform/pulumi/console). Define recommended tags:
   `data-classification`, `backup-policy`. Document allowed values — free-form tags are not
   filterable. Fill in `templates/tagging-policy.md`.

2. **Enforcement mechanism.** For each cloud in scope:
   - AWS: AWS Tag Policies (enforces allowed values) + SCP `deny if required tag missing on create`.
   - Azure: Azure Policy `deny` effect on missing required tags.
   - GCP: Resource Manager label constraints via org policy.
   Document the IaC snippet (Terraform) for each enforcement mechanism. Hand off the IaC authoring
   to `terraform-iac`.

3. **Untagged cost fallback.** For the spend that will not be tagged immediately: define the
   fallback allocation rule (proportional to tagged spend ratio, or park in a "shared/unattributed"
   cost centre). Set a target: untagged cost <5% of total within 90 days.

4. **Shared cost allocation design.** For each shared service (Kubernetes cluster, networking, shared
   tooling): choose the allocation method (proportional by CPU/memory/request consumption,
   direct mapping, or even split). Document the method, the denominator, and the review cadence
   (at least quarterly). Fill in `templates/showback-chargeback-model.md`.

5. **Showback vs chargeback decision.** Traverse the allocation model tree in
   `knowledge/finops-cloud-cost-decision-trees.md`. Recommend showback first unless chargeback is
   a firm requirement (Finance-mandated GL booking). If chargeback: define the allocation keys,
   GL cost-centre mapping, and the monthly reconciliation process. Handoff to `finance` plugin for
   GL entries.

6. **Unit economics definition.** Define at least one unit metric: cost per active customer, cost
   per API request, or cost per feature. Document: numerator (attributed cloud cost), denominator
   (the agreed business metric with the definition Finance/Engineering/Product have signed off on),
   the allocation method, and the target range. Use `finops_calc.py unit_cost()` for the arithmetic.

7. **FOCUS spec adoption** (if multi-cloud normalization is in scope). Provide the column mapping
   from each cloud's native billing format to the FOCUS schema. Note that FOCUS spec versions evolve
   — mark all column names `[verify-at-use]`. Recommend a tooling path (native export, third-party
   tool with FOCUS support, or custom ETL).

8. **Emit the Structured Output block** with handoffs:
   - `terraform-iac` for the IaC enforcement modules.
   - `finance` for GL chargeback booking.
   - `finops-practice-lead` if operating-model or RACI gaps are exposed.
   - `cost-optimization-engineer` if rightsizing gaps are blocking accurate baseline calculation.
