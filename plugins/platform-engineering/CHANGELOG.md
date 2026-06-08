# Changelog — platform-engineering

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth build-out to the v0.2.0 standard. No agent/skill/command surface changes — this round deepens
the knowledge, scenario, rules, and runnable-tooling layers.

- **Best-practices → 12** — the rule set reached the full 12 atomic rules
  (`platform-as-product-not-a-tools-backlog` … `the-build-belongs-to-the-layer-below`); the
  `best-practices/README.md` index lists all 12.
- **Knowledge bank → 5 decision trees** (6 present) — Mermaid trees for build-a-platform-at-all,
  build-vs-buy the portal/provisioning, paved-road-vs-guardrail-vs-gate, the platform-API surface,
  the Team Topologies interaction mode, and golden-path deprecation/migration — plus the dated 2026
  capability map (`[verify-at-build]` rows: Backstage / Port / Cortex / OpsLevel / Crossplane / Score /
  Kratix / OPA-Kyverno / DORA-DevEx).
- **Scenarios → 5 field notes** — added `self-hosted-backstage-no-owner` (build-vs-buy / TCO),
  `boiling-the-ocean-platform` (thinnest-viable-platform / cognitive load), and
  `platform-as-tax-mandated-adoption` (platform-as-product / paved-road / DevEx) to the existing two
  (catalog drift, self-service-that-was-a-ticket-queue). Each follows the 9-field schema; index updated.
- **Runnable calculator** — `scripts/platform_calc.py` (stdlib-only, Python 3.8+, ruff-clean): `dora`
  (four-key Elite/High/Medium/Low banding), `paved-road` (coverage % + gap-to-target + units-to-move),
  `error-budget` (platform SLO → allowed downtime / bad-event budget + spend-to-date verdict). A
  calculator, not a data source — the user supplies every input.
- Version bumped `0.1.0 → 0.2.0`; description's best-practices count updated to 12 (agents/skills counts
  unchanged).

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
