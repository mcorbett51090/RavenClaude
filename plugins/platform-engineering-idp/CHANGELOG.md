# Changelog — platform-engineering-idp

All notable changes to this plugin are documented here. Versions follow semver and are kept in sync
with `.claude-plugin/plugin.json` and the marketplace catalog.

## 0.1.0 — 2026-06-08

Initial release. Created as candidate **#1** of the 2026-06-08 twenty-candidate-plugins research
(`docs/research/2026-06-08-twenty-candidate-plugins/`), prioritized first on demand (Gartner: 80% of
large software-engineering orgs to have platform teams by 2026; Backstage ≈89% IDP-portal share),
feasibility, and fit (sits directly above the existing devops-cicd + cloud-native-kubernetes +
observability-sre + technical-writing-docs cluster).

- 4 agents: `platform-product-lead`, `idp-portal-engineer`, `golden-path-engineer`,
  `devex-metrics-engineer` — each with the scenario-authoring frontmatter schema.
- 5 skills: platform-as-product operating model, golden-path design, IDP/portal setup, self-service
  infrastructure, DevEx measurement.
- 4 commands: assess-platform-maturity, design-golden-path, scaffold-software-catalog, measure-devex.
- 4 templates: golden-path spec, Backstage `catalog-info.yaml`, paved-road RFC, platform maturity
  scorecard.
- Knowledge bank: `platform-engineering-decision-trees.md` (5 Mermaid decision trees + a dated 2026
  capability map of the IDP/portal landscape).
- 12 best-practices, a 4-note scenarios bank, and 1 advisory PreToolUse hook.
