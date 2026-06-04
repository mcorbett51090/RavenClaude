# Product Management

The **product-management** plugin — the product craft of deciding what to build and why — continuous discovery, evidence-based prioritization, crisp PRDs/specs, and outcome metrics — distinct from project-management's delivery/schedule lane.

## Agents

- **`product-strategist`** — Product strategy and vision: positioning and the strategy stack (vision -> strategy -> objectives), opportunity sizing, the roadmap as a set of bets, build-vs-buy-vs-partner, and the strategic narrative
- **`product-discovery-lead`** — Continuous discovery: customer interviews and JTBD, opportunity-solution trees, assumption mapping and riskiest-assumption testing, problem validation, and writing PRDs/specs framed as problems + outcomes
- **`product-metrics-analyst`** — Product measurement and prioritization: defining a North Star + input metrics (not vanity), evidence-based prioritization (RICE / cost-of-delay / opportunity scoring), funnel/retention/activation analysis framing, and judging outcomes

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install product-management@ravenclaude
```

## Seams

- **Delivery: schedule, scope/change control, sprints, RAID, status reporting** → `project-management` (this is the how/when; we own the what/why). The litmus: 'what should we build and why' → here; 'how do we deliver it on time' → there.
- **Whether an experiment result is statistically real, power/MDE, test design** → `applied-statistics`.
- **Feature-flag infrastructure, A/B test plumbing, product analytics instrumentation** → `experimentation-growth-engineering`; we frame the hypothesis and read the outcome, they run the apparatus.
- **UX research method depth, wireframes, and interaction design** → `web-design` (UX designer); we own product discovery + the problem definition.
- **Prose polish of the PRD / strategy doc** → `ravenclaude-core/documentarian`; the product thinking is ours.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
