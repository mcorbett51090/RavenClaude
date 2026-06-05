# gcp-cloud — best-practice docs

Named, citable rules for the `gcp-cloud` plugin's specialists. Each file is **one rule**, grounded in this plugin's house opinions ([`../CLAUDE.md`](../CLAUDE.md)) and the decision trees in [`../knowledge/gcp-cloud-decision-trees.md`](../knowledge/gcp-cloud-decision-trees.md). Read a doc whole and cite it; don't paraphrase a fragment.

---

## Index

_22 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`audit-logs-on-for-all-services.md`](./audit-logs-on-for-all-services.md) | Absolute rule | Standing up any GCP project — enable Data Access audit logs org-wide |
| [`budget-alerts-per-project.md`](./budget-alerts-per-project.md) | Pattern | Creating a new GCP project — set cost alerts before deploying any resources |
| [`cloud-armor-on-public-load-balancers.md`](./cloud-armor-on-public-load-balancers.md) | Pattern | Exposing any HTTP(S) workload to the public internet via a Global LB |
| [`cloud-nat-for-private-egress.md`](./cloud-nat-for-private-egress.md) | Pattern | Provisioning VMs or GKE nodes — use Cloud NAT for outbound instead of public IPs |
| [`cloud-run-as-the-default.md`](./cloud-run-as-the-default.md) | Pattern | Choosing where to run a containerized or stateless workload on GCP |
| [`cloud-run-min-instances-for-latency.md`](./cloud-run-min-instances-for-latency.md) | Pattern | Deploying a prod Cloud Run service — set minimum instances to eliminate cold starts |
| [`cmek-where-control-is-required.md`](./cmek-where-control-is-required.md) | Pattern | Storing sensitive data — evaluate CMEK when compliance requires key control |
| [`disable-sa-key-creation-via-org-policy.md`](./disable-sa-key-creation-via-org-policy.md) | Absolute rule | Configuring org policies — enforce no SA key creation at the org level |
| [`federate-ci-no-keys-cross-boundary.md`](./federate-ci-no-keys-cross-boundary.md) | Absolute rule | Connecting CI/CD pipelines to GCP — use WIF, never export SA keys |
| [`gke-autopilot-over-standard.md`](./gke-autopilot-over-standard.md) | Pattern | Creating a new GKE cluster — prefer Autopilot unless Standard constraints apply |
| [`label-everything-for-cost.md`](./label-everything-for-cost.md) | Pattern | Provisioning any GCP resource — apply cost-allocation labels from day one |
| [`no-service-account-key-files.md`](./no-service-account-key-files.md) | Absolute rule | Granting GCP API access — attach a SA instead of exporting a key file |
| [`one-service-account-per-workload.md`](./one-service-account-per-workload.md) | Pattern | Creating service accounts — one SA per workload, minimum permissions |
| [`org-policy-guardrails.md`](./org-policy-guardrails.md) | Pattern | Setting up a GCP organization — apply preventive Org Policy constraints |
| [`predefined-roles-over-primitive.md`](./predefined-roles-over-primitive.md) | Absolute rule | Granting IAM roles — never use Owner/Editor/Viewer on a project |
| [`private-by-default-gcp.md`](./private-by-default-gcp.md) | Absolute rule | Provisioning any resource — private IPs and Private Google Access by default |
| [`pub-sub-for-event-driven-integration.md`](./pub-sub-for-event-driven-integration.md) | Pattern | Designing async event-driven integration between GCP services |
| [`regional-by-default.md`](./regional-by-default.md) | Pattern | Provisioning any GCP resource — multi-zone regional resources for prod |
| [`secret-manager-not-env-vars.md`](./secret-manager-not-env-vars.md) | Absolute rule | Passing secrets to GCP workloads — use Secret Manager, not env var literals |
| [`shared-vpc-for-multi-project-networking.md`](./shared-vpc-for-multi-project-networking.md) | Pattern | Designing multi-project networking — Shared VPC for centralized control |
| [`use-the-resource-hierarchy.md`](./use-the-resource-hierarchy.md) | Pattern | Designing the GCP estate — org/folders/projects for blast radius and policy |
| [`vpc-service-controls-as-a-perimeter.md`](./vpc-service-controls-as-a-perimeter.md) | Pattern | Protecting sensitive GCP APIs from data exfiltration — use VPC Service Controls |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution + the house opinions these docs codify.
- [`../knowledge/gcp-cloud-decision-trees.md`](../knowledge/gcp-cloud-decision-trees.md) — decision trees for compute, data store, hierarchy, networking, IAM, and billing.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
