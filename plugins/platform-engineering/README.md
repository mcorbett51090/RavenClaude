# Platform Engineering

The **platform-engineering** plugin — the internal-developer-platform (IDP) craft: the paved-road, platform-as-product layer *above* CI/CD, Kubernetes, IaC, and observability that ties them into self-service golden paths a developer portal makes discoverable — distinct from the pipeline, the cluster, and the module themselves.

## Agents

- **`platform-architect`** — Platform shape and operating model: the thinnest viable platform, Team Topologies (stream-aligned / platform / enabling teams), the platform's API (the self-service capabilities it exposes), build-vs-buy per layer, roadmap sequencing, and explicit non-goals. Designs the platform as a product, not a tools-team backlog.
- **`developer-portal-engineer`** — The developer portal and software catalog: catalog modeling (components/systems/APIs/resources + team ownership + lifecycle + tier), auto-discovery/ingestion, scaffolder/software templates that generate paved-road repos, TechDocs (docs-as-code), and scorecards. Backstage-leaning, portal-neutral (Port / Cortex / OpsLevel / Roadie).
- **`golden-paths-and-adoption-engineer`** — Paved roads as real self-service and proving the platform is a product: self-service provisioning (Terraform modules / Crossplane / Score / Kratix), guardrails-as-defaults + policy-as-code, and adoption/outcomes measurement (paved-road coverage, DORA, DevEx/SPACE, a platform SLO).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install platform-engineering@ravenclaude
```

## Seams

- **The actual pipeline (build/test/deploy stages, the CI tool)** → `devops-cicd`; this team specifies the paved-road CI shape, they build the pipeline.
- **The cluster, Helm charts, operators, runtime ops** → `cloud-native-kubernetes`; we pave the "deploy a service" path, they own the cluster.
- **The Terraform module / Crossplane composition the path provisions, and cloud primitives** → `terraform-iac` + `aws-cloud` / `azure-cloud` / `gcp-cloud`; we design the self-service path + guardrails, they author the module.
- **The platform SLO and error budget** → `observability-sre`; we say the self-service surface needs an SLO, they set and protect it.
- **What "secure/compliant default" means inside a guardrail** → `security-engineering` + `data-governance-privacy`; we encode their policy into the paved road as a default.
- **TechDocs content quality and information architecture** → `technical-writing-docs`; we wire docs-as-code into the portal.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `devops-cicd`, `cloud-native-kubernetes`, `terraform-iac`, and `observability-sre`.
