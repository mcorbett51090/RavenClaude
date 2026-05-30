# azure-cloud — best-practice docs

Named, citable rules for standing up and running Azure under the Microsoft stack. Each file is **one rule**, grounded in this plugin's CAF/WAF-sourced knowledge bank ([`../knowledge/`](../knowledge/)) and enforced (where grep-able) by the `check-azure-anti-patterns.sh` hook. Read a doc whole and cite it; don't paraphrase a fragment.

These docs codify the cross-cutting **house opinions** in [`../CLAUDE.md`](../CLAUDE.md) §3 into copy-paste-grade guidance. For the underlying reference material and decision trees, go to the knowledge bank.

---

## Index

_19 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`compute-data-residency-drives-region-selection.md`](./compute-data-residency-drives-region-selection.md) | Pattern — strong default; choosing a region by latency/cost alone, before checking the residency boundary and its geo-pair, is a re-platform waiting to happen. | Region is one of the hardest things to change after the fact — resources can't be moved between regions, and data already at rest carries compliance w… |
| [`compute-zone-redundant-by-default-for-prod.md`](./compute-zone-redundant-by-default-for-prod.md) | Pattern — strong default for prod; single-zone prod needs a written reason tied to cost or a no-AZ region. | A single-zone prod deployment takes a datacenter-level outage as a full outage — and the fix is usually free or near-free. |
| [`cost-budgets-tags-and-policy-guardrails.md`](./cost-budgets-tags-and-policy-guardrails.md) | Pattern — strong default; a subscription with no budget, no enforced tags, and no SKU policy is a cost incident waiting to happen. | Cost discipline that's purely *reporting* ("the bill was high last month") is always too late. |
| [`gov-azure-policy-as-guardrails.md`](./gov-azure-policy-as-guardrails.md) | Pattern — strong default for any governed estate; assign at MG scope, roll out audit→deny safely. | Guardrails that live in people's heads (or a wiki) don't hold — the only governance that survives turnover and Cursor/Codex/portal edits is the kind t… |
| [`iac-compose-from-azure-verified-modules.md`](./iac-compose-from-azure-verified-modules.md) | Pattern — strong default; a hand-authored resource where a published AVM exists needs a written reason. | Every team that hand-authors a Storage account, a Key Vault, or a VNet from raw resource declarations re-discovers the same WAF defaults (diagnostic s… |
| [`iac-deployment-stacks-for-lifecycle-and-deletion-guard.md`](./iac-deployment-stacks-for-lifecycle-and-deletion-guard.md) | Pattern — strong default for any grouped-resource lifecycle; a plain RG deployment for shared infra needs a written reason. | Two recurring failures motivate this rule. |
| [`iac-what-if-before-every-deploy.md`](./iac-what-if-before-every-deploy.md) | Absolute rule — applying IaC to a shared environment without previewing the change set is the click-ops sin in declarative clothing. | The whole value of declarative IaC is that you can see the delta *before* it touches a running estate — yet the most common way a Bicep/Terraform chan… |
| [`identity-key-vault-references-not-app-settings-literals.md`](./identity-key-vault-references-not-app-settings-literals.md) | Absolute rule — a secret value pasted into an app setting / pipeline variable is a leak that every contributor can read. | `passwordless-by-default` says "no secret literals in code or IaC." This rule covers the unavoidable secret that *does* have to live somewhere — a thi… |
| [`identity-rbac-least-privilege-and-custom-roles.md`](./identity-rbac-least-privilege-and-custom-roles.md) | Absolute rule — `Owner`/`Contributor` at subscription/MG scope in IaC is the privilege-escalation default mistake; the hook flags it. | The path of least resistance is to assign `Contributor` (or `Owner`) at subscription scope and move on — and that is precisely how an estate ends up w… |
| [`lz-flat-management-group-hierarchy.md`](./lz-flat-management-group-hierarchy.md) | Pattern — strong default; a deeper or org-shaped hierarchy needs a written reason tied to a real policy/RBAC boundary. | The first structural mistake in a new Azure estate is modeling the **management-group (MG) hierarchy** on the company org chart — a node per business … |
| [`lz-subscription-vending-not-manual-creation.md`](./lz-subscription-vending-not-manual-creation.md) | Pattern — strong default for any multi-subscription estate; a hand-clicked subscription with bolt-on governance needs a written reason. | When subscriptions are created by hand in the portal, governance arrives *late and unevenly* — someone deploys workloads, and only afterward does anyo… |
| [`lz-tag-and-name-to-the-caf-standard.md`](./lz-tag-and-name-to-the-caf-standard.md) | Pattern — strong default; ad-hoc names and missing tags make an estate un-attributable and un-automatable. | Two facts make naming and tagging a day-one decision, not a cleanup task. |
| [`network-hub-spoke-vs-virtual-wan.md`](./network-hub-spoke-vs-virtual-wan.md) | Pattern — strong default; pick the topology from the connectivity decision, not from what the team built last. | The connectivity subscription's topology is a one-way door — re-platforming hub-to-vWAN (or back) on a live estate is expensive — so it's worth gettin… |
| [`network-segment-subnets-with-nsgs-and-forced-egress.md`](./network-segment-subnets-with-nsgs-and-forced-egress.md) | Pattern — strong default for any VNet carrying a real workload; a flat, NSG-less VNet needs a written reason. | `private-by-default-paas-data-planes` locks down the PaaS *data planes*; this rule covers the **VNet that the compute sits in**. |
| [`ops-control-log-analytics-cost.md`](./ops-control-log-analytics-cost.md) | Primary diagnostic — when an Azure bill is unexpectedly high, check Log Analytics ingestion + retention first. | The single most common "why is my Azure bill so high?" surprise is **Log Analytics ingestion + retention** — telemetry is easy to turn on (`ops-diagno… |
| [`ops-diagnostic-settings-to-log-analytics-from-day-one.md`](./ops-diagnostic-settings-to-log-analytics-from-day-one.md) | Pattern — strong default; a prod resource with no diagnostic settings is a resource you can't debug or audit after the fact. | Azure resource logs are **not collected by default** — until you create a **diagnostic setting** pointing the resource's logs/metrics at a destination… |
| [`passwordless-by-default.md`](./passwordless-by-default.md) | Absolute rule — a client secret or connection string in code or IaC is a leak, not a config choice. | Every secret literal you commit is a credential that must be rotated, scanned for, and eventually leaks. |
| [`pick-compute-from-the-decision-tree.md`](./pick-compute-from-the-decision-tree.md) | Pattern — strong default; deviate only with a written reason tied to a tree leaf. | The recurring "where should this run?" question has a habitual wrong answer — reach for AKS (or for whatever the team ran last) regardless of fit — an… |
| [`private-by-default-paas-data-planes.md`](./private-by-default-paas-data-planes.md) | Absolute rule — a public PaaS data plane is the single highest-blast-radius default mistake in an Azure estate. | Key Vault, Storage, Azure SQL, Cosmos, App Configuration, and Container Registry all ship with their data plane **reachable from the public internet**… |

---

## See also` (link this plugin's own knowledge/agents) · `## Provenance` · the `_Last reviewed:_` line.
3. Append a row to the index table above.
4. Cross-link from the relevant knowledge file and agent.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution + the house opinions these docs codify
- [`../knowledge/`](../knowledge/) — the dated, citation-grounded reference bank + decision trees
- [`../../../docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) — the marketplace-wide doc template
