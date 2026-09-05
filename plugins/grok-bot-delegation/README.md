# grok-bot-delegation

> **Standing operating procedure for Chief of Staff:** on every Matthew ask, match or create expert Grok Bots, port/upstream RavenClaude skills, delegate with a tight brief, and coordinate — Matthew only for decisions, auth, or irreversible actions.

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`. Pairs with `grok-bot-creation`.

## What it does

| You ask | It returns |
|---|---|
| "Who should own this?" | Match existing expert bots or create missing ones |
| "How do I hand this off?" | A SendToAgent brief: goal, constraints, success criteria, skills |
| "Should CoS do the deep work?" | No — specialists own deep work; CoS coordinates |
| "How do I cut fleet token spend?" | Condensed returns, effort ladder before spawn, routine hygiene, connectors over browser, CPCT measurement |

## What's inside

- **skills** — `delegate-via-expert-bots`, `grok-bot-token-spend`

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install grok-bot-delegation@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`. Prefer also installing `grok-bot-creation@ravenclaude`.
