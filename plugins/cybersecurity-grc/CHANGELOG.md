# Changelog — cybersecurity-grc

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth build-out to the v0.2.0 standard — knowledge, scenarios, a runnable calculator, and reconciled counts. No agent/skill/command surface change (still 3 agents / 3 skills / 3 commands); nothing breaks on `/plugin marketplace update`.

- **Best-practices → 12** — reconciled the count references (plugin.json description and the CLAUDE.md milestone previously said "8"; the directory and `best-practices/README.md` index already carried 12: `compliance-is-a-byproduct-of-real-security`, `scope-is-the-highest-leverage-decision`, `map-once-attest-many`, `a-control-has-three-states`, `evidence-is-a-system-not-a-fire-drill`, `risk-drives-controls-not-the-reverse`, `the-soa-exclusion-needs-a-justification`, `third-party-risk-is-your-risk`, `the-framework-is-a-means-the-risk-is-the-end`, `attest-only-what-you-can-evidence`, `read-the-cuecs-not-just-the-opinion`, `gap-assessment-before-fieldwork-not-during`).
- **Knowledge → 5 Mermaid trees** — added 3 trees to `cybersecurity-grc-decision-trees.md` (vendor-assessment-depth, audit-boundary scoping, risk-treatment selection) alongside the existing which-framework-first and Type I vs Type II. Extended the dated 2026 framework/capability map (`[verify-at-build]`) with vendor-tiering, residual-risk, and Type II observation-period rows, plus a pointer to the runnable calculator. Last reviewed 2026-06-08.
- **Scenarios → 5 field notes** — added 3 (scope-creep blew the SOC 2 budget; parallel control sets doubled the work; no gap assessment meant fieldwork surprises) to the existing 2, corroborating `scope-is-the-highest-leverage-decision`, `map-once-attest-many`, and `gap-assessment-before-fieldwork-not-during`. 9-field schema, `reviewed: false`, no real PII/secrets; README index updated.
- **Runnable calculator** — `scripts/grc_calc.py` (stdlib-only, argparse, ruff-clean): `risk-score` (likelihood × impact → inherent + residual band after control effectiveness), `control-coverage` (% of applicable controls with evidence), `audit-readiness` (Type II observation-period evidence coverage). Decision-support, not a verdict; mirrors the decision trees and the house doctrine.

## 0.1.0 — 2026-06-08

Initial release. The security governance, risk & compliance (GRC) program layer above the technical-control plugins.

- **3 agents** — `grc-architect` (framework selection + scoping across SOC 2 TSC / ISO 27001 + Annex A / NIST CSF 2.0 / 800-53,
  the ISMS, control crosswalk, the Statement of Applicability), `control-and-evidence-engineer` (control implementation + operating
  effectiveness, policy/procedure authoring, evidence collection + continuous control monitoring, Type I vs Type II readiness),
  `audit-and-third-party-risk-lead` (gap assessments, auditor liaison + the PBC list, vendor/third-party risk — tiering, SIG/CAIQ,
  shared-responsibility, ongoing monitoring). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `framework-selection-and-control-mapping`, `risk-register-and-assessment`, `evidence-and-audit-readiness`.
- **Knowledge bank** — `cybersecurity-grc-decision-trees.md`: Mermaid trees (which-framework-first, Type I vs Type II, vendor-tiering + assessment depth, audit-boundary scoping) + a dated 2026 framework/reference map (SOC 2 TSC / ISO 27001 Annex A / NIST CSF 2.0 / 800-53 / SIG / CAIQ) — `[verify-at-build]`.
- **8 best-practices**, **3 commands** (`scope-compliance-program`, `build-risk-register`, `audit-readiness-review`),
  **2 templates** (Statement of Applicability, risk register), **1 advisory hook**
  (`check-cybersecurity-grc-anti-patterns.sh`; `GRC_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: AppSec/secure-coding → `security-engineering`; financial-regulator compliance → `regulatory-compliance`;
  data-subject/privacy mechanics → `data-governance-privacy`; cloud config controls → `aws-cloud` / `azure-cloud` / `gcp-cloud`.
  Requires `ravenclaude-core@>=0.7.0`.
