---
name: Bug report
about: Report something broken in a RavenClaude plugin, hook, or workflow.
title: "[bug] "
labels: bug
assignees: mcorbett51090
---

## What plugin is affected?

- [ ] `ravenclaude-core`
- [ ] `power-platform`
- [ ] Marketplace / catalog (`.claude-plugin/marketplace.json`)
- [ ] CI workflows (`.github/workflows/`)
- [ ] Docs / meta
- [ ] Other (describe):

Plugin version (from `plugins/<plugin>/.claude-plugin/plugin.json`):

## What were you doing?

Describe the action that triggered the bug. Be concrete — what command did you run, what agent did you spawn, what file were you editing?

```
# example: /plugin install power-platform@ravenclaude
# example: dispatched flow-engineer via spawn-team with brief "..."
```

## What did you expect?

## What happened instead?

Paste the actual output, error message, or screenshot. If the bug is "the wrong agent got dispatched" or "the output contract was violated," paste the agent's report.

## Environment

- OS:
- Claude Code version (`claude --version`):
- Marketplace install method: `/plugin marketplace add mcorbett51090/RavenClaude` / local checkout / clone-fallback
- Are you running other plugins alongside? List them:

## Repro

Minimum steps to reproduce on a clean install:

1.
2.
3.

## Anything else?

Logs, screenshots, related issues, hypotheses about the root cause.
