# developer-relations

A **Developer Relations (DevRel)** team for Claude Code — the seat that owns the
**developer experience** of a product with an API/SDK: getting a developer from
"heard about it" to "built something that works," fast, then keeping them.

> **Not a tech writer, not a marketer, not a PM.** Reference docs →
> `technical-writing-docs`. Demand gen → `marketing-operations`. What to build →
> `product-management`. The API/SDK itself → `api-engineering`.

## Agents

| Agent | Use it for |
|---|---|
| **developer-advocate** | Audit the developer experience, measure the activation funnel, plan content/talks, run the product-feedback loop. |
| **devrel-content-engineer** | Design a getting-started path, a sample app, or an SDK quickstart as runnable, production-grade code. |
| **developer-community-manager** | Review community health, design forum/Discord ops, contributor and ambassador programs. |

## Skills

- `getting-started-audit` — measure and shorten time-to-first-success.
- `sample-app-design` — spec a sample app that demonstrates the real value path.
- `devrel-content-strategy` — pick formats and a calendar for an activation goal.
- `community-health-review` — diagnose a developer community by answered-question rate and returning contributors.

## Commands

- `/developer-relations:audit-getting-started`
- `/developer-relations:design-sample-app`
- `/developer-relations:plan-devrel-content`
- `/developer-relations:review-community-health`

## Knowledge

- **Decision trees** (`knowledge/devrel-engagement-decision-trees.md`) — advocate-vs-docs-vs-community, fix-the-product-or-document-it, content-format choice.
- **Developer-experience playbook** (`knowledge/developer-experience-playbook.md`) — the activation funnel, TTFS, content, community, the feedback loop.

## House opinions

- Time-to-first-success is the metric.
- Fix the product before writing around it.
- Sample code is production code — it runs, handles errors, and teaches secure patterns.
- DevRel is not demand gen; measure activation, not MQLs.

## Requires

`ravenclaude-core@>=0.7.0`. Advisory only — it produces audits, specs, plans, and
feedback briefs; it does not run your forum, CMS, or SDK.
