# Changelog — cybersecurity-grc

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

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
