# developer-relations

> **Developer-relations (DevRel) team** for Claude Code — grow and serve a developer audience
> without lying to it. Two doing-agents, a funnel-and-metrics knowledge bank, skills, templates,
> commands, and an advisory anti-pattern hook. Inherits the `ravenclaude-core` protocols.

## What this plugin is for

DevRel sits in a seam the marketplace didn't cover: it's not the docs *system*
(`technical-writing-docs`), not the API *contract* (`api-engineering`), not *what to build*
(`product-management`), and not the *buyer* funnel (`marketing-operations`). It's the craft of
turning a developer who's never heard of you into one who ships with you and tells their friends —
and **measuring that honestly** (activation and time-to-first-success, not GitHub stars).

## Agents

| Agent | Spawn it for |
|---|---|
| `devrel-strategist` | DevRel strategy & program design, the developer funnel, the metrics that track it, community-program design, honest measurement |
| `developer-advocate` | Sample apps & demos that run as shipped, tutorials & content, CFP abstracts & talks, the content calendar, community engagement |

## The house opinions (what makes this opinionated)

1. **Measure activation, not applause** — time-to-first-success and activation rate over stars/followers.
2. **Teach, don't market at developers** — the unit of DevRel helps them do their job today.
3. **Sample code runs as shipped** — placeholder secrets and `TODO`s in a getting-started are defects.
4. **Time-to-first-success is the product** — count the steps; every one loses people.
5. **A CFP abstract leads with the attendee takeaway**, not the speaker or the product.
6. **Community health is response time + resolution**, not member count.

## Skills

- `devrel-strategy-and-metrics` — program + funnel + the metric set
- `developer-onboarding-funnel` — time-to-first-success audit
- `sample-app-and-demo-design` — a demo that runs as shipped and teaches one thing
- `conference-talk-and-cfp` — CFP abstract + talk design
- `developer-community-program` — community design + health metrics

## Commands

- `/developer-relations:design-devrel-program`
- `/developer-relations:audit-developer-onboarding`
- `/developer-relations:draft-cfp-abstract`
- `/developer-relations:plan-sample-app`

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude   # or a local path
/plugin install developer-relations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Seams (where it hands off)

| Need | Goes to |
|---|---|
| The docs artifact / docs site | `technical-writing-docs` |
| The API contract itself | `api-engineering` |
| What to build / product strategy | `product-management` |
| The non-developer marketing funnel | `marketing-operations` |
| A security verdict on a sample app | `ravenclaude-core/security-reviewer` |

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution, routing rules, and the Output Contract.
