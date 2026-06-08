# Changelog — hospitality-hotel-operations

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The lodging / rooms operations layer — running a hotel property as a business across
operations, revenue, and reputation. Distinct from the `restaurant-operations` F&B sibling.

- **3 agents** — `hotel-operations-lead` (front-office / PMS operations, housekeeping, the guest journey,
  SOPs, labor scheduling, maintenance/engineering coordination), `revenue-manager` (RevPAR / ADR / occupancy /
  GOPPAR, pricing and rate strategy, channel/OTA mix and cost, demand forecasting, overbooking and yield),
  `guest-experience-analyst` (reviews and online reputation, satisfaction measurement, loyalty, service recovery,
  the comment-to-action loop). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `front-office-and-housekeeping-ops`, `revenue-management-and-rate-strategy`, `guest-experience-and-reputation`.
- **Knowledge bank** — `hospitality-hotel-operations-decision-trees.md`: Mermaid trees (rate/pricing move, overbook-or-not,
  channel-mix shift, review-driven defect triage) + a dated 2026 system/channel map (PMS / RMS / OTA / reputation platforms) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`build-rate-strategy`, `audit-guest-journey`, `triage-reviews`),
  **2 templates** (rate-strategy brief, service-recovery playbook), **1 advisory hook**
  (`check-hospitality-hotel-operations-anti-patterns.sh`; `HOTEL_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: F&B outlet → `restaurant-operations`; demand statistics → `applied-statistics`; BI / reporting → `data-platform`.
  Requires `ravenclaude-core@>=0.7.0`.
