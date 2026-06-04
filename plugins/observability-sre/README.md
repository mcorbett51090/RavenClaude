# Observability & SRE

The **observability-sre** plugin — making a system observable and reliable — SLOs and error budgets, the three pillars (metrics, logs, traces) on OpenTelemetry, alerting that pages on symptoms, and incident response that learns.

## Agents

- **`observability-engineer`** — Instrumentation and the telemetry pipeline: OpenTelemetry traces/metrics/logs, semantic conventions, sampling strategy, cardinality control, correlation across the three pillars, dashboards that answer questions
- **`sre-reliability-engineer`** — SLI/SLO/error-budget design, symptom-based alerting (multi-window multi-burn-rate), reliability targets and the budget policy, capacity and toil reduction
- **`incident-commander`** — Incident response: severity classification, the IC/comms/ops role split, status communication, the timeline, blameless postmortems, and action-item follow-through

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install observability-sre@ravenclaude
```

## Seams

- **The deploy health-gate that promotes or aborts a canary** → `devops-cicd/release-engineer` consumes the SLO/burn-rate signal this team defines.
- **Cluster/pod/node telemetry and the metrics pipeline in-cluster** → `cloud-native-kubernetes` runs it; this team designs what to measure and the SLOs.
- **API-level SLIs (availability, latency of an endpoint)** → defined here, but the API contract & RateLimit semantics are `api-engineering`'s.
- **Managed monitoring backends (CloudWatch, Azure Monitor, Cloud Monitoring)** → the relevant cloud plugin; OTel-vendor-neutral instrumentation is portable across them.
- **A reliability incident that is actually a security incident** → `security-engineering` / `ravenclaude-core/security-reviewer`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
