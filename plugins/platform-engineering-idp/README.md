# platform-engineering-idp

The **platform-as-a-product** layer that sits above CI/CD and the cluster. This plugin's team helps
you decide whether to build a platform team, stand up an **internal developer platform (IDP)** and
developer portal, author **golden paths / paved roads** with **self-service infrastructure**, and
**measure developer experience** so the platform earns adoption instead of mandating it.

> **The one-line philosophy:** the platform is a product, developers are its customers, and the
> platform team's KPI is _someone else's_ velocity. Pave the 80% path, keep an escape hatch, make it
> self-service, and measure the friction you removed — not the features you shipped.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Should we build a platform team / an IDP? What first?" | **platform-engineering-idp** (`platform-product-lead`) |
| "Set up Backstage / model our software catalog / add a software template" | **platform-engineering-idp** (`idp-portal-engineer`) |
| "Make spinning up a new service / new infra self-service" | **platform-engineering-idp** (`golden-path-engineer`) |
| "Measure & improve developer experience / platform adoption" | **platform-engineering-idp** (`devex-metrics-engineer`) |
| "Design the CI pipeline / rollout the golden path _runs_" | `devops-cicd` |
| "Run the workload on Kubernetes / Argo / Helm" | `cloud-native-kubernetes` |
| "Author the Terraform module behind the self-service button" | `terraform-iac` |
| "Instrument the SLO / deploy-health signal" | `observability-sre` |
| "Make the TechDocs content actually good" | `technical-writing-docs` |

## What's inside

- **4 agents** — `platform-product-lead`, `idp-portal-engineer`, `golden-path-engineer`,
  `devex-metrics-engineer`.
- **5 skills** — platform-as-product operating model, golden-path design, IDP/portal setup,
  self-service infrastructure, DevEx measurement.
- **4 commands** — `/platform-engineering-idp:assess-platform-maturity`,
  `:design-golden-path`, `:scaffold-software-catalog`, `:measure-devex`.
- **4 templates** — golden-path spec, Backstage `catalog-info.yaml`, paved-road RFC, platform
  maturity scorecard.
- **Knowledge bank** — `knowledge/platform-engineering-decision-trees.md`: Mermaid trees for
  buy-vs-build IDP, golden-path scoping, the self-service boundary, platform-team topology, and
  maturity staging, plus a dated 2026 capability map.
- **12 best-practices**, a **scenarios** bank (4 field notes), and **1 advisory hook**
  (flags mandate-language, ticket-driven "self-service", vanity metrics, no escape hatch).

## House opinions (the short list)

1. The platform is a product; adoption is earned, not mandated.
2. Pave the 80% path; keep an escape hatch for the 20%.
3. Self-service or it isn't a platform.
4. Reduce cognitive load — that's the whole job.
5. Measure outcomes (adoption, time-to-prod, friction), not output.
6. Start with the thinnest viable platform; buy/adopt before you build.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
