# Changelog — event-management

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-22

Initial release.

### Added

- **3 agents** — `event-strategist` (goals/KPIs, format, audience, budget/break-even, sponsorship strategy, go/no-go), `event-operations-lead` (run-of-show, venue/vendor/AV logistics, registration ops, contingency, day-of), `event-marketing-revenue` (promotion, registration funnel, sponsorship sales + fulfillment, attendee acquisition, post-event ROI).
- **5 skills** — `design-event-plan-and-budget`, `build-run-of-show`, `sponsorship-and-revenue`, `registration-and-attendee-ops`, `post-event-measurement`.
- **Knowledge bank** — `event-management-decision-trees.md` (4 Mermaid trees: format in-person/virtual/hybrid, budget/break-even, sponsorship tiering, go/no-go gate) and `event-management-reference-2026.md` (dated tooling/benchmark map; re-verify before quoting).
- **8 best-practices** — budget carries a contingency line, run-of-show is minute-by-minute, registration funnel not a headcount, sponsorship is a fulfilled promise not a logo, name the go/no-go criteria early, have a plan B for every single point of failure, measure against the goal you set, post-event debrief while it's fresh.
- **3 templates** — event-plan-and-budget, run-of-show, post-event-report.
- **3 commands** — `/plan-event`, `/build-run-of-show`, `/event-debrief`.
- **1 advisory hook** — `check-event-anti-patterns.sh` (3 checks on `.md`; `EVENT_STRICT=1` to block).

### Verify-at-use

- All platform names and benchmark numbers in `event-management-reference-2026.md` (registration/ticketing, virtual/hybrid platforms, no-show and conversion rules of thumb) — volatile; re-confirm against the vendor and your own historical actuals before quoting.
