# Changelog — property-management-residential

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Value-add depth build-out. The fair-housing/habitability posture is unchanged — agents still **flag** risk
and route to counsel; they do **not** give legal advice.

- **Runnable calculator** — `scripts/pm_calc.py` (stdlib-only, Python 3.8+, ruff-clean on F/E9/B/C4/I/UP):
  `rentroll` (gross potential rent, physical vs. economic occupancy, loss-to-lease separated from vacancy
  loss), `noi` (operating income − operating expense; **refuses** to net debt service / capex / depreciation
  into NOI — reports them below the line, because NOI is operating-only and is NOT cash flow), and
  `delinquency` (A/R aging buckets + delinquency rate as a % of the rent roll). A **calculator, not a data
  source** — the user supplies every input; outputs are decision-support, not the books of record.
- **best-practices** — now **12** rules (was 8): added `vacancy-is-the-most-expensive-thing`,
  `renewal-is-a-math-problem-framed-by-law`, `preventive-maintenance-is-cheaper-than-the-emergency-it-prevents`,
  `tenant-pii-is-minimized-never-pasted`. README index updated.
- **Knowledge bank** — decision-trees expanded to **5 Mermaid trees** (added delinquency-ladder,
  move-out-deduction, vacancy-&-turn) alongside the maintenance-triage and renew-vs-raise trees, plus the
  dated 2026 reference map (`[verify-at-build]`).
- **Scenarios bank** — now **5** dated field notes (added turn-clock-started-at-empty-not-notice,
  noi-reported-with-debt-service-mixed-in, drifted-rent-roll-hid-the-real-delinquency). No tenant PII;
  `reviewed: false`. README index updated.
- Plugin description updated to reflect the new counts; **no** change to the 3 agents / 3 skills surface.
  Requires `ravenclaude-core@>=0.7.0`.

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
