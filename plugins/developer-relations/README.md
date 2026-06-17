# developer-relations

> A **Developer Relations** team for Claude Code — the people who get developers from "never heard of it" to "it works and I'd recommend it," and prove it. Strategy (operating model, funnel, measurement) plus production (the golden-path tutorial, runnable sample apps, talks, community).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "What should DevRel focus on for <goal>?" | The motion (advocacy / education / community / product-feedback) the goal needs, via a decision tree, + the one metric that proves it |
| "Where does our developer funnel leak?" | An instrumented AAARRP funnel — a metric per stage (TTFHW, activation, retention) + the suspected leak + the experiment to test the fix |
| "Our DevRel KPIs are followers and stars — fix them" | A vanity-vs-actionable audit + an activation/retention-anchored scorecard + the qualitative feedback loop wired to PM/eng |
| "Write a quickstart for <product>" | A copy-paste-runnable quickstart — every block language-tagged, a "you should see …" success check, a measured TTFHW |
| "Build a sample app / a talk / run a community" | A golden-path sample that runs unmodified, a talk with a recorded fallback, or a community plan that captures DX feedback |

**Two rules it never breaks:** *sample apps must run unmodified*, and *measure with developer success (TTFHW / activation / retention), never vanity reach.*

## What's inside

- **2 agents** — `devrel-strategist` (operating model, funnel, measurement) and `developer-advocate` (golden-path content, sample apps, talks, community, DX feedback).
- **3 skills** — `design-developer-funnel`, `author-quickstart-and-sample-app`, `measure-devrel-impact`.
- **2 knowledge files** — a Mermaid goal→motion→metric decision tree, and a developer-metrics reference (the AAARRP funnel, TTFHW, activation/retention, the qualitative loop, and vanity-metric traps).
- **2 templates** — a golden-path quickstart tutorial and a one-page DevRel content plan.
- **3 best-practice rules** — optimize TTFHW, sample apps must run unmodified, close the product-feedback loop.
- **1 advisory hook** — `flag-devrel-smells.sh` (bare-fence quickstart code blocks, vanity-only goal statements, quickstarts with no success criterion).

## The motions it works in

```
advocacy          →  awareness: talks, demos, launch content
education         →  activation: the golden-path quickstart + sample app  (TTFHW is the lever)
community         →  retention: forums/Discord, contributor + ambassador programs
product-feedback  →  route developer friction back to PM/eng (the motion teams skip)
```

## How it seams with adjacent plugins

```
developer-relations   →  the golden-path tutorial, sample apps, advocacy, community, DX feedback
technical-writing-docs →  the docs SITE & reference manual
api-engineering       →  the API / SDK design ITSELF
product-management    →  market positioning, messaging, pricing
customer-success-analytics →  community for a NON-developer audience
```

The advocate *finds* API friction and routes it to `api-engineering`; the reference manual and docs site belong to `technical-writing-docs`.

## Install

```shell
/plugin marketplace add /workspaces/RavenClaude
/plugin install developer-relations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
