# developer-relations

A RavenClaude plugin: a **Developer Relations** specialist team for running a DevRel
program — developer advocacy, developer experience (quickstarts + samples), community
operations, and outcome-based metrics.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install developer-relations@ravenclaude
```

Requires `ravenclaude-core@>=0.5.0` (inherits its Grounding + Structured Output protocols).

## Agents

| Agent | Use it for |
|-------|-----------|
| `devrel-lead` | Program strategy, the developer funnel, OKRs/metrics, investment decisions, cross-team seams |
| `developer-advocate` | Talks, blog/video content, conference + community engagement, the product feedback loop |
| `docs-and-samples-engineer` | Quickstarts, sample apps, SDK ergonomics, the getting-started path, time-to-first-success |
| `community-manager` | Forums/Discord/Discussions, moderation, the contributor ladder, ambassador program |

## Skills

- `devrel-strategy` — design the program: pick the developer funnel, set north-star + guardrail metrics, decide where to invest.
- `quickstart-authoring` — write a quickstart that minimizes time-to-first-success and is CI-tested against the real SDK.
- `developer-content-pipeline` — a sustainable editorial calendar with repurposing (one talk → blog → video → docs).
- `community-health` — response-time SLAs, code-of-conduct enforcement, the contributor ladder, anti-burnout rotation.
- `devrel-metrics` — the funnel, leading vs lagging indicators, honest attribution, and the vanity-metric ban.

## What ships

- A developer-funnel **decision-tree** knowledge doc (where to invest given your funnel's weakest stage).
- 7 best-practices (one claim each), 3 templates (quickstart, talk abstract, community-health dashboard).
- 2 slash commands (`/devrel-quickstart-audit`, `/devrel-funnel-review`).
- 1 advisory hook flagging DevRel anti-patterns (vanity metrics as goals, a quickstart with no time-to-first-success target, megaphone-only advocacy).

## House rules

DevRel here is a **feedback loop, not a megaphone**; the **quickstart is a product**
measured by time-to-first-success; **vanity metrics are never success criteria**; and
**attribution is honest or absent**. See [`CLAUDE.md`](CLAUDE.md) for the full constitution
and the seams to `technical-writing-docs`, `product-management`, and `marketing-operations`.
