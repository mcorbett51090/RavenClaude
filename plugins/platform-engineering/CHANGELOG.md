# Changelog — platform-engineering

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The internal-developer-platform (IDP) / platform-as-product layer above the existing
software-delivery cluster.

- **3 agents** — `platform-architect` (thinnest viable platform, Team Topologies, the platform API, build-vs-buy),
  `developer-portal-engineer` (software catalog + ownership, scaffolder templates, TechDocs, scorecards — Backstage-leaning,
  portal-neutral), `golden-paths-and-adoption-engineer` (self-service provisioning, guardrails-as-defaults + policy-as-code,
  DORA + DevEx + paved-road coverage + platform SLO). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `internal-developer-platform-design`, `software-catalog-and-portal`, `golden-path-and-self-service`.
- **Knowledge bank** — `platform-engineering-decision-trees.md`: Mermaid trees (build-a-platform-at-all, build-vs-buy the portal/provisioning, paved-road-vs-guardrail-vs-gate, the platform-API surface) + a dated 2026 capability map (`[verify-at-build]`).
- **10 best-practices**, **3 commands** (`design-platform`, `scaffold-service-catalog`, `pave-golden-path`),
  **2 templates** (thinnest-viable-platform brief, golden-path spec), **1 advisory hook**
  (`check-platform-engineering-anti-patterns.sh`; `PLATFORM_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: pipelines → `devops-cicd`; clusters → `cloud-native-kubernetes`; modules → `terraform-iac`; SLOs → `observability-sre`;
  secure defaults → `security-engineering` / `data-governance-privacy`. Requires `ravenclaude-core@>=0.7.0`.
