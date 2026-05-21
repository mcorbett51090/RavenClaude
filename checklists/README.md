# Checklists

Pre-flight / post-flight checklists for common operations.

Each checklist is a markdown file with concrete tickable items, ordered by when they should fire (before, during, after the operation). Use these instead of loose prose when a procedure has gone wrong enough times that a fixed order pays off.

## Available

- [`release-checklist.md`](release-checklist.md) — bump a plugin version, update `marketplace.json`, run local validation, open the PR, tag, draft a GitHub Release, verify consumers pick it up.
- [`new-plugin-checklist.md`](new-plugin-checklist.md) — scaffold a brand-new domain plugin (folders, manifest, CLAUDE.md, agents, hooks, smoke test, PR).

## Planned

- `incident-postmortem-checklist.md` — what to capture after an issue (write this the first time we actually have an incident — premature templates rot).
