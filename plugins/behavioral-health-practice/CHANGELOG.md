# Changelog — behavioral-health-practice

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The operations + documentation layer for an outpatient behavioral / mental-health practice —
operational and documentation support only, **never clinical, medical, or legal advice**, PHI-aware throughout
(HIPAA + 42 CFR Part 2).

- **3 agents** — `practice-operations-lead` (intake & scheduling, no-show management, telehealth ops, caseload/panel
  management, referral flow), `clinical-documentation-specialist` (treatment plans, DAP/SOAP/BIRP progress notes,
  medical necessity, release of information — structure only, never clinical content),
  `billing-and-authorization-lead` (eligibility, prior authorization, behavioral CPT codes, claims basics, 42 CFR
  Part 2 + HIPAA in billing — never upcoding). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `intake-and-scheduling`, `clinical-documentation`, `prior-auth-and-claims`.
- **Knowledge bank** — `behavioral-health-practice-decision-trees.md`: Mermaid trees (is-a-prior-auth-required-and-confirmed,
  is-this-record-Part-2-covered-and-disclosable) + a dated 2026 reference map (intake→treatment-plan→note→claim
  medical-necessity thread, DAP/SOAP/BIRP, behavioral CPT codes, 42 CFR Part 2 vs HIPAA basics) — `[verify-at-build]` rows.
- **8 best-practices**, **3 commands** (`design-intake-flow`, `draft-progress-note-template`, `prep-prior-auth`),
  **2 templates** (progress-note template, prior-auth request checklist), **1 advisory hook**
  (`check-behavioral-health-practice-anti-patterns.sh`; flags plaintext PHI, disclosure-without-consent, Part 2-without-consent,
  ticket-queue "self-service"; `BH_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: revenue-cycle depth → `medical-revenue-cycle`; senior care → `senior-care-operations`; HIPAA security controls
  → `cybersecurity-grc`; every clinical decision → a licensed clinician. Requires `ravenclaude-core@>=0.7.0`.
