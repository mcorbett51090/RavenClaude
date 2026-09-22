# grok-bot-creation

> Design **token-efficient, mostly autonomous Grok Bot personas** — CreateAgent / UpdateAgent checklists, a gold description template, safe token hygiene (never cut verification that changes outcomes), and the recipe for upstreaming net-new skills into RavenClaude via GitHub Sage.

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Create a Grok Bot for X" | A scoped persona (name + description) following the gold template, with clear ownership and stop conditions |
| "Is this too token-heavy?" | Safe cuts only — fluff out; verification and outcome-changing context stay |
| "How do I upstream a new Grok skill?" | The `plugins/<slug>/` layout + marketplace registration + handoff to GitHub Sage for the PR |

## What's inside

- **skills** — `create-grok-bot`

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install grok-bot-creation@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
