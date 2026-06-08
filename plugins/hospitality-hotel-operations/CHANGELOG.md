# Changelog — hospitality-hotel-operations

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth pass — deepening the lodging / rooms layer to the v0.2.0 standard. No agent/skill/command
roster change; this release thickens the priors, the decision logic, the field evidence, and adds a
runnable calculator.

- **Best-practices 8 → 12.** Added `the-guest-journey-is-one-system` (own booking → stay → post-stay
  end-to-end; the seams are first-class defects), `channel-mix-is-a-margin-decision` (the right OTA/direct
  mix on net-ADR contribution, never zero-OTA), `the-pms-is-the-system-of-record` (no side spreadsheets),
  and `specify-the-seam-hand-off-the-build` (do the rooms-side slice, hand the F&B / stat / BI build to the
  neighbour). README index updated.
- **Knowledge — 5 Mermaid decision trees** (was 4): added "Cut labor for this shift?" (schedule to the
  occupancy curve, never below the service floor), alongside the rate-move, overbook, channel-mix, and
  review-triage trees. The dated 2026 PMS / RMS / OTA / reputation system-and-channel map is retained
  (`[verify-at-build]`).
- **Scenarios 2 → 5** (9-field schema, `reviewed: false`): added `overbook-walk-with-no-protocol`,
  `pms-side-spreadsheet-drift`, and `labor-cut-below-service-floor`. README index updated.
- **Runnable calculator** — `scripts/hotel_calc.py` (stdlib only, argparse): `revpar` (RevPAR from ADR×Occ
  and from room-revenue ÷ available-rooms, reconciled), `goppar` (GOP per available room, the profit check),
  and `channel-mix` (net ADR after OTA commission + give-back, blended across channels). ruff-clean
  (F,E9,B,C4,I,UP). Decision-support, not financial advice.
- No migration: additive only — `/plugin marketplace update` is safe.

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
