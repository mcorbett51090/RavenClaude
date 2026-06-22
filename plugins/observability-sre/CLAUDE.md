# Observability & SRE Plugin — Team Constitution

> Team constitution for the `observability-sre` Claude Code plugin — **3** specialist agents for making a system observable and reliable — SLOs and error budgets, the three pillars (metrics, logs, traces) on OpenTelemetry, alerting that pages on symptoms, and incident response that learns. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`observability-engineer`](agents/observability-engineer.md) | Instrumentation and the telemetry pipeline: OpenTelemetry traces/metrics/logs, semantic conventions, sampling strategy, cardinality control, correlation across the three pillars, dashboards that answer questions | "instrument this service", "set up tracing", "our metrics bill is exploding", "we can't tell where the latency is" |
| [`sre-reliability-engineer`](agents/sre-reliability-engineer.md) | SLI/SLO/error-budget design, symptom-based alerting (multi-window multi-burn-rate), reliability targets and the budget policy, capacity and toil reduction | "define our SLOs", "our alerts are too noisy", "set up burn-rate alerting", "how reliable should this be?" |
| [`incident-commander`](agents/incident-commander.md) | Incident response: severity classification, the IC/comms/ops role split, status communication, the timeline, blameless postmortems, and action-item follow-through | "we have an incident", "run the incident", "write the postmortem", "set up our incident process" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Alert on symptoms, not causes.** Page on user-visible pain (latency, error rate, the SLO burning), not on a high CPU that may be harmless. A page must be actionable and urgent.
2. **An SLO without an error budget is a vanity number.** The budget is what lets you say yes to risk — spend it on velocity when there's slack, freeze when it's gone.
3. **Three pillars, one trace context.** Metrics tell you *that* something's wrong, traces tell you *where*, logs tell you *why*. Correlate them with a shared trace/span id or you're guessing.
4. **Cardinality is a cost and a foot-gun.** A label with unbounded values (user-id, request-id as a metric label) explodes your TSDB. Put high-cardinality on traces/logs, not metrics.
5. **Every page must be actionable.** If the runbook says 'just acknowledge it', the alert is noise — delete it or fix it. Alert fatigue kills real incidents.
6. **Postmortems are blameless and they ship action items.** The output of an incident is a list of owned, dated fixes — not a person to blame. An incident you didn't learn from will recur.

## 3. Seams (the bridges to neighbouring plugins)

- **The deploy health-gate that promotes or aborts a canary** → `devops-cicd/release-engineer` consumes the SLO/burn-rate signal this team defines.
- **Cluster/pod/node telemetry and the metrics pipeline in-cluster** → `cloud-native-kubernetes` runs it; this team designs what to measure and the SLOs.
- **API-level SLIs (availability, latency of an endpoint)** → defined here, but the API contract & RateLimit semantics are `api-engineering`'s.
- **Managed monitoring backends (CloudWatch, Azure Monitor, Cloud Monitoring)** → the relevant cloud plugin; OTel-vendor-neutral instrumentation is portable across them.
- **A reliability incident that is actually a security incident** → `security-engineering` / `ravenclaude-core/security-reviewer`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/observability-sre-decision-trees.md`](knowledge/observability-sre-decision-trees.md) (the consolidated bank — alert yes/no, page-ticket-dashboard, pillar choice, cardinality, SLO target, SLO tighten-loosen-hold, log level, postmortem action item + a dated capability map), plus two **topic-specific** trees that complement it: [`knowledge/sli-slo-design-decision-tree.md`](knowledge/sli-slo-design-decision-tree.md) (which SLI *shape* + which window/how-many — the design step *before* setting the target) and [`knowledge/alerting-threshold-strategy-decision-tree.md`](knowledge/alerting-threshold-strategy-decision-tree.md) (which threshold *mechanism* + how to tune a multi-window multi-burn-rate alert — the *how-to-fire* step *after* deciding it's pageable). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (alert-fatigue → SLO-burn redesign, high-cardinality metrics cost blowout, missing-instrumentation trace gap, error-budget freeze policy). Secondary source; never replaces the knowledge bank. The three specialists should glob the bank when a situation matches.

**Runnable calculator** — [`scripts/slo_calc.py`](scripts/slo_calc.py) (stdlib only, Python 3.9+) removes arithmetic error from three recurring reliability decisions: `error-budget` (SLO target + window → allowed downtime / bad-event budget), `burn-rate` (good/bad events over a slice → burn rate, budget consumed, time-to-exhaustion + a plain verdict), and `alert-windows` (SLO → the multi-window multi-burn-rate alert thresholds, reproducing the Workbook's 14.4x / 6x burn factors). It is a **calculator, not a data source** — the user supplies every input; outputs are decision-support, not a reliability guarantee. Owned primarily by `sre-reliability-engineer`; `incident-commander` uses `burn-rate` during an incident readout.

## 6. Technical-runtime tier — MCP & LSP (dispositioned, nothing bundled)

Observability/SRE is a **code/infra** domain, so the runtime tier was evaluated honestly — but **nothing is bundled this round**, because every candidate fails the bar in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) (a bundled MCP server must be **zero-config and read-only by default**).

**Recommended (not bundled) MCP servers — live telemetry context.** Each is **per-instance + credentialed** → recommend-not-bundle; the secret stays a **reference** (env-var name / vault URI), never a literal, and a write-capable server is gated through `ravenclaude-core/security-reviewer` before any consumer adopts it.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Grafana MCP** ([`grafana/mcp-grafana`](https://github.com/grafana/mcp-grafana), Apache-2.0, first-party) | Needs a **per-instance Grafana URL + service-account token** (a secret), and is **write-capable** (dashboards/alerts/incidents) — both disqualify bundling. Read-only mode exists via `--disable-write`. | `claude mcp add grafana -- uvx mcp-grafana` with `GRAFANA_URL` + `GRAFANA_SERVICE_ACCOUNT_TOKEN` as env-var **references**; prefer `--disable-write`; `security-reviewer` sign-off before write is enabled. |
| **Prometheus MCP** ([`pab1it0/prometheus-mcp-server`](https://github.com/pab1it0/prometheus-mcp-server) / [`giantswarm/mcp-prometheus`](https://github.com/giantswarm/mcp-prometheus) / AWS AMP) | Needs a **per-instance Prometheus/Mimir URL + auth** (per-tenant, credentialed). Read-oriented (PromQL query/metadata), but still per-consumer-configured → recommend-not-bundle. | `claude mcp add prometheus -- uvx prometheus-mcp-server` (or the Go/AWS variant) with `PROMETHEUS_URL` + auth as references. Vet license/activity at adoption. |

**LSP — dispositioned N-A (not bundled).** A real PromQL language server exists ([`prometheus-community/promql-langserver`](https://github.com/prometheus-community/promql-langserver), Go) — but unlike `backend-engineering` (whose example languages Python/TS/Go have real source files in the consumer repo), **PromQL has no standard file extension** in a repo; it lives embedded inside YAML rule/recording files, and the server's label completion needs a live Prometheus to attach to. A generic `.lsp.json` extension→language mapping therefore wouldn't fire usefully. Referenced honestly here rather than shipped. Revisit if a maintained PromQL/YAML-embedded LSP with a real file-extension surface appears.

> Verified 2026-06-05: Grafana MCP license (Apache-2.0), auth (URL + service-account token), write-capability + `--disable-write`, and install paths (`uvx`/`docker pull`/`go install`) per [github.com/grafana/mcp-grafana](https://github.com/grafana/mcp-grafana); the Prometheus-MCP package set per their GitHub/PyPI listings; the PromQL-langserver per [prometheus-community/promql-langserver](https://github.com/prometheus-community/promql-langserver). Package names, versions, and capabilities are volatile — re-confirm at use.

## 7. Value-add completeness (build-out 2026-06-05)

PR #315 added the consolidated `knowledge/*-decision-trees.md`, `best-practices/`, and `templates/`. This build-out fills the net-new gaps (scenarios bank + runtime tier) and adds two complementary topic-specific decision trees. Disposition of every value-add menu item:

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (alert-fatigue/SLO redesign, high-cardinality cost blowout, missing-instrumentation trace gap, error-budget freeze policy) + a `scenarios/README.md` index on the 9-field schema. |
| 2 | **Decision-tree knowledge** | **BUILT** — 2 NEW topic-specific Mermaid trees complementing #315's consolidated file: `sli-slo-design-decision-tree.md` (SLI shape + window — the *before-target* design step) and `alerting-threshold-strategy-decision-tree.md` (threshold mechanism + multi-window tuning — the *how-to-fire* step). Grounded + cited + dated. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §6. Grafana MCP (per-instance + token + write-capable) and the Prometheus MCP servers (per-instance + auth) all fail the zero-config + read-only bar. Documented the `claude mcp add` paths + `security-reviewer` gate instead. No invented servers. |
| 4 | **LSP server** | **N-A** — §6. A real PromQL LSP exists but has no standard file-extension surface in a consumer repo (PromQL lives inside YAML) and needs a live Prometheus for completion; a generic `.lsp.json` wouldn't fire. Referenced honestly, not shipped. |
| 5 | **Runnable script under `scripts/`** | **BUILT** — `slo_calc.py` (error-budget / burn-rate / alert-windows). Genuine value: removes arithmetic error from the recurring reliability decisions; reproduces the SRE-Workbook burn factors. Stdlib-only, ruff-clean. |
| 6 | **bin/ · monitors · output-styles · settings · themes** | **N-A** — no groundable, broadly-valuable instance. A monitor/background job has nothing to watch (advisory plugin, no runtime). An output-style would overlap the agents' Output Contract. The single stdlib script covers the runnable surface. |
| 7 | **skills / hooks / commands / templates** | **Coverage sufficient** — 7 skills, 4 commands, 4 templates, 1 advisory hook already cover instrumentation, SLO/error-budget design, alerting-rule design, incident response, and postmortem facilitation. No clear gap warranted a new component this round. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.3.0` entry. No `NOTICE.md` (nothing third-party is bundled — the script is original/stdlib-only and all MCP/LSP servers are *referenced*, not vendored). |

## 8. Milestones

- **v0.2.x** — initial release: 3 agents, 7 skills, 4 templates, 4 commands, 1 advisory hook, the consolidated decision-tree knowledge bank, 12 best-practices.
- **v0.3.0** — value-add build-out: scenarios bank (4 scenarios), 2 complementary topic-specific Mermaid decision-tree files, `scripts/slo_calc.py` (3 modes), CHANGELOG. Runtime tier (MCP + LSP) dispositioned recommend-not-bundle / N-A with reasons (§6).
- **v0.4.0** — **chaos engineering** folded in as the proactive complement to the reactive incident/SLO practices: a [`chaos-engineering`](skills/chaos-engineering/SKILL.md) skill (steady-state hypothesis → blast-radius-limited fault injection → game day) and a [`chaos-engineering-reference.md`](knowledge/chaos-engineering-reference.md) knowledge doc (the Principles of Chaos, the experiment loop, a fault catalog, the staging→prod maturity ramp, verify-at-use tooling). Same currency as the SRE practices already here (SLIs/SLOs, error budgets) and the same feedback sink (the reliability action-item backlog). Resilience patterns being verified are `backend-engineering`'s; fault-injection automation routes to `devops-cicd` / `cloud-native-kubernetes`.
