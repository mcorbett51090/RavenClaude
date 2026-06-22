# Changelog — observability-sre

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.4.1] — 2026-06-13

Research-sweep **correction** (Tier-A weekly news sweep) — the capability map said OpenTelemetry **logs** were still "maturing"; they have **reached Stable**. Verified against the primary [OpenTelemetry spec status](https://opentelemetry.io/docs/specs/status/) (Logs Data Model + Logs API = Stable). Routed through two expert panels (usefulness → USEFUL; detailed review → APPROVE-WITH-FIX, the per-language-SDK rider applied); panels concurred, no tiebreak. (Patch on top of **0.4.0**, which folded in chaos engineering via #452 and shipped without its own CHANGELOG entry.)

### Fixed

- **`knowledge/observability-sre-decision-trees.md`** — capability-map OpenTelemetry row updated from "traces+metrics | GA | Logs maturing" to "**traces+metrics+logs | GA — all 3 core signals Stable**", with a `[verify-at-build — per-language SDK logs maturity still varies]` rider, a note that **Profiles** is the 4th signal (public **Alpha**, ~2026-03, `[verify-at-build]`), and a spec-status citation. An SRE deciding whether to route logs through OTel was being told logs were not production-ready when the data model + API are GA.
- Version **0.4.0 → 0.4.1** in `.claude-plugin/plugin.json` **and** `marketplace.json` (lockstep).

## [0.3.0] — 2026-06-05

Value-add build-out — running the repeatable plugin-enrichment recipe against the full value-add menu. Every menu item was dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `alert-fatigue-slo-redesign` (delete cause-based pages, alert on SLO burn — but define the SLO first), `high-cardinality-metrics-cost-blowout` (count series before you scale; the unbounded label wanted to be a trace attribute), `missing-instrumentation-trace-gap` (a trace gap is a context-propagation hole, not a verdict on the dark service), `error-budget-burn-freeze-policy` (write and pre-sign the budget policy before the SLO binds). Uses the 9-field scenario schema + a `scenarios/README.md` index.
- **Decision-tree knowledge (2 new files, complementing the consolidated tree).** `knowledge/sli-slo-design-decision-tree.md` — which SLI shape for a journey + which window/how-many (the design step before the existing "set the target" / "tighten-loosen-hold" trees). `knowledge/alerting-threshold-strategy-decision-tree.md` — which threshold mechanism (static vs. burn-rate vs. multi-window vs. anomaly) + how to tune a multi-window multi-burn-rate alert (the *how-to-fire* step after the existing "should this page?" / "page-ticket-dashboard?" trees). Both grounded in the Google SRE Workbook with sources + dates.
- **Runnable calculator.** `scripts/slo_calc.py` (stdlib only, Python 3.9+) — `error-budget` (SLO + window → allowed downtime / bad-event budget), `burn-rate` (events over a slice → burn rate, budget consumed, time-to-exhaustion + a verdict), `alert-windows` (SLO → the multi-window multi-burn-rate alert thresholds, reproducing the Workbook's 14.4x / 6x factors). A calculator, not a data source — the user supplies every input; outputs are decision-support. Ruff-clean.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (technical-runtime tier disposition: MCP + LSP), the runnable-tooling note, and the value-add completeness disposition table; §1/§3/§4 unchanged.

### Decisions (recorded, not built)

- **No bundled MCP server.** Every published observability MCP server is per-instance + credentialed: the official **Grafana MCP** (`grafana/mcp-grafana`, Apache-2.0) needs a Grafana URL + service-account token and is write-capable (`--disable-write` for read-only); the **Prometheus MCP** servers (`pab1it0/prometheus-mcp-server`, `giantswarm/mcp-prometheus`, AWS's AMP server) all need a per-instance Prometheus/Mimir URL + auth. None clears the doctrine's zero-config + read-only bar, so all are **recommend-not-bundle** with documented `claude mcp add …` paths + a `security-reviewer` gate. No invented servers.
- **No bundled LSP `.lsp.json`.** A real PromQL LSP exists (`prometheus-community/promql-langserver`, Go) but PromQL has no standard file extension in a consumer repo (it lives embedded in YAML rule files), and the server's label completion needs a live Prometheus — so a generic `.lsp.json` mapping wouldn't fire usefully. Referenced honestly instead of shipped. (Contrast: `backend-engineering` ships an `.lsp.json` because its example languages — Python/TS/Go — have real source files in the repo.)
- **No `bin/`, output-styles, monitors, settings defaults, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — 7 skills, 4 commands, 4 templates, 1 advisory hook already cover instrumentation, SLO/error-budget design, alerting-rule design, incident response, and postmortem facilitation; no gap warranted a new component this round.

### Verify-at-use

- Grafana MCP license/auth/write-capability and install paths (`uvx mcp-grafana` / `docker pull grafana/mcp-grafana` / `go install …@latest`); the Prometheus-MCP package names and the AWS AMP MCP server; the PromQL-langserver maturity. All version-volatile — re-confirm against the vendor before quoting. SLO/burn-rate conventions (windows, burn factors) are SRE-Workbook examples — recompute for the target at hand.

## [0.2.x] — earlier

3-agent observability & SRE team (observability-engineer, sre-reliability-engineer, incident-commander): 7 skills, a consolidated decision-tree knowledge bank (alert-design + SLO-target + pillar-choice + on-call-routing + cardinality + log-level + postmortem trees + a dated 2026 capability map), 12 best-practices, 4 templates, 4 commands, 1 advisory hook. Seams to devops-cicd, cloud-native-kubernetes, api-engineering, the cloud plugins, and security-engineering.
