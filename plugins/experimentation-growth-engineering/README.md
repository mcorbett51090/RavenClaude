# Experimentation & Growth Engineering

The **experimentation-growth-engineering** plugin — the apparatus for learning fast and safely in production — feature flags and safe rollouts, A/B test plumbing, and trustworthy product-analytics event instrumentation — with statistical validity deferred to applied-statistics.

## Agents

- **`experimentation-architect`** — The experimentation system: assignment/randomization, exposure logging, the experiment lifecycle, SRM and trustworthiness checks, guardrail metrics, and the build-vs-buy of an experimentation platform — partnering with applied-statistics on design
- **`feature-flag-engineer`** — Feature flags and safe rollout: flag types (release/experiment/ops/permission), targeting and segmentation, kill switches, progressive rollout, the flag lifecycle and debt management, and SDK integration
- **`product-analytics-instrumentation-engineer`** — Trustworthy event instrumentation: the tracking plan, a consistent event/property schema (naming + types), identity stitching (anonymous -> known), a CDP (Segment-style), data quality of events, and funnel/retention instrumentation

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install experimentation-growth-engineering@ravenclaude
```

## Seams

- **Statistical validity: power/MDE, significance, sequential methods, 'is the difference real'** → `applied-statistics` (load-bearing). This team produces clean assignment + exposure + metric data; that team judges it.
- **The hypothesis, the outcome metric, and what to test** → `product-management` (discovery + metrics); we run the apparatus, they frame the question.
- **Progressive-delivery rollout orchestration and the deploy pipeline** → `devops-cicd/release-engineer` (flags are the shared surface).
- **The data pipeline/warehouse the events land in and the analysis runs on** → `data-platform` / `analytics-engineering`.
- **Frontend/mobile SDK integration of flags + tracking** → `frontend-engineering` / `mobile-engineering`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
