# Tag at birth or you cannot allocate

**Status:** Absolute rule
**Domain:** Cloud cost allocation
**Applies to:** `finops-cloud-cost`

---

## Why this exists

Retroactive tagging projects consistently fail to reach full coverage. A resource created without
required tags enters the billing stream immediately — it accrues cost that cannot be attributed to
a team, project, or cost centre. By the time a quarterly cleanup happens, months of spend are
permanently unattributable. Worse, teams have no incentive to tag resources they did not create
and do not own.

The only reliable tagging model is **enforcement at resource creation time**: if a resource cannot
be created without the required tags, there is no cleanup problem downstream. Showback, chargeback,
unit economics, and every other allocation artifact depend on tagging coverage. Get it to >95%
before building any downstream cost model.

## How to apply

- Author the tagging policy as a named, versioned document (use `templates/tagging-policy.md`).
- Enforce via cloud-native mechanisms at creation time:
  - AWS: Tag Policies (allowed values) + SCP `deny` on create without required tags.
  - Azure: Azure Policy `deny` effect for missing required tags at the subscription or MG level.
  - GCP: Org policy label constraints via Resource Manager.
- Ship the enforcement with the IaC. The tagging policy is a module in Terraform/Pulumi, not a
  wiki page. Every resource provisioned via IaC inherits the required tags from the module.
- Set a coverage KPI: untagged spend <5% of total monthly cloud spend within 90 days of rollout.
  Alert weekly on teams above the threshold.

**Do:**

- Enforce tags at the cloud API level (SCP/Policy/Org policy) so Console, CLI, and IaC all comply.
- Define allowed values per tag — free-form tags are unqueryable at scale.
- Track untagged spend as a first-class metric in the FinOps dashboard.
- Set a documented fallback rule for the untagged spend that exists before enforcement reached 100%.

**Don't:**

- Rely on a quarterly tagging cleanup sprint — it never reaches 100% and recurs endlessly.
- Apply tags only to IaC resources while console-provisioned resources go untagged.
- Accept "we'll add tags later" as a delivery condition — later means never in billing data.
- Add tags to already-running resources as the primary strategy (use this only as a catch-up for
  legacy resources while enforcement prevents new untags).

## Edge cases / when the rule does NOT apply

Some managed cloud services (e.g., certain AWS service-linked roles, auto-created support
resources, some GCP system projects) do not support customer-managed labels. These are genuine
exceptions. Document each exception explicitly in the tagging policy, assign them to a
"platform/system" cost bucket, and do not let the exceptions justify a broad tagging gap.

## See also

- [`./every-cost-has-an-owner-showback-changes-behavior.md`](./every-cost-has-an-owner-showback-changes-behavior.md)
- [`../templates/tagging-policy.md`](../templates/tagging-policy.md)
- [`../skills/cost-allocation-and-tagging/SKILL.md`](../skills/cost-allocation-and-tagging/SKILL.md)

## Provenance

Reflects the FinOps Foundation's inform-phase discipline and the practical experience across
large-scale cloud tagging programs that retroactive tagging consistently under-delivers relative
to enforce-at-birth approaches.

---

_Last reviewed: 2026-06-08 by `claude`._
