# Changelog — property-management-residential

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The residential property-operations layer — fair-housing-aware (it **flags** risk and routes
to counsel; it does **not** give legal advice).

- **3 agents** — `leasing-and-tenant-ops` (leasing funnel, consistent documented screening standard, lease
  lifecycle, renewals & rent increases, move-in/out, fair-housing basics), `maintenance-coordinator` (work-order
  intake & triage with safety/habitability first, preventive maintenance, vendor dispatch, unit turns, emergency
  & habitability response), `owner-and-portfolio-reporting-analyst` (rent roll, delinquency & collections, owner
  statements, NOI operating-only, occupancy/vacancy & portfolio reporting). Each carries the full
  scenario-authoring frontmatter.
- **3 skills** — `leasing-and-screening`, `work-order-triage`, `owner-reporting-and-rent-roll`.
- **Knowledge bank** — `property-management-residential-decision-trees.md`: Mermaid trees (maintenance triage
  emergency-vs-routine-vs-habitability, renew-vs-raise-vs-non-renew) + a dated 2026 reference map (fair-housing
  protected classes, screening signals, PM-software landscape, rent-roll/NOI metrics) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`screen-applicant`, `triage-work-order`, `build-rent-roll`),
  **2 templates** (tenant-screening-criteria, owner-statement-and-rent-roll), **1 advisory hook**
  (`check-property-management-residential-anti-patterns.sh`; `PM_STRICT=1` to make it blocking), and a
  **scenarios bank** (2 field notes).
- Seams: commercial leases → `commercial-real-estate`; trust/GL accounting → `finance`; trade work →
  `skilled-trades-contracting`; fair-housing/eviction/habitability legality → qualified counsel.
  Requires `ravenclaude-core@>=0.7.0`.
