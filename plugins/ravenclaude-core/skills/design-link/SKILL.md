---
name: design-link
description: Bind THIS repo to one of your claude.ai/design design-system projects in one step — lists your projects, lets you pick, and writes .ravenclaude/design-project.json so every session's capability banner surfaces the link and the agent can read/edit the project. Use when starting design work in a repo that has no .ravenclaude/design-project.json yet (or to re-point it). Pairs with the built-in /design-sync skill (which does the actual component sync) and the DesignSync tool.
allowed-tools: DesignSync, AskUserQuestion, Write, Read, Bash
---

# /design-link — bind this repo to a claude.ai/design project

Records which of your claude.ai/design design-system projects belongs to **this repo**, so the
agent stops having to ask each session. This is the *binding* step only — the actual reading
(context) and editing (sync) happen through the **`DesignSync`** tool and the built-in
**`/design-sync`** skill once the binding exists.

> **Access note (read first).** Reading/writing claude.ai/design projects needs design scopes on
> your claude.ai login. The first `DesignSync` call in a session **auto-grants** them
> (`user:design:read` + `user:design:write`); if a session genuinely has no claude.ai login, run
> `/design-login` once. A "this environment can't see design projects" message is almost always the
> un-granted scope, **not** a missing repo file — adapt accordingly (Capability Grounding: a missing-
> looking capability is one route, not proof it's absent).

## Steps

1. **List the user's projects.** Call `DesignSync` with `method: list_projects`. (This also grants the
   design scopes on first use.) It returns writable design-system projects: `{projectId, name, ownerDisplayName, updatedAt}`.
   - **Zero projects** → tell the user to create one at claude.ai/design (or offer `DesignSync create_project`), then re-run.
   - **One project** → propose it as the binding (confirm it's the right one for this repo).
   - **Several** → present them via `AskUserQuestion` (one option per project, newest `updatedAt` first) and let the user pick the one that belongs to THIS repo. Do **not** guess by name-similarity alone — a repo and its design project can be named differently.
2. **Confirm the target repo.** The binding is written into the **current** repo's `.ravenclaude/`. If
   the user is in a different repo than the project is "for," stop and confirm — don't drop a project's
   binding into the wrong repo (the exact mistake the consult-your-access-inventory clause guards: act on the right target).
3. **Write the binding.** Write `.ravenclaude/design-project.json` from the template
   ([`../../templates/design-project.json`](../../templates/design-project.json)):
   ```json
   {
     "project_id": "<the chosen projectId>",
     "name": "<the project name>",
     "mirror_dir": "",
     "notes": "<one line — what this design system covers>"
   }
   ```
   - `project_id` is a **non-secret UUID** — safe to commit. `mirror_dir` is the optional local dir
     `/design-sync` mirrors components into; leave `""` if you only read the project remotely.
   - If the file already exists, show the current binding and confirm before overwriting (re-point).
4. **Confirm.** Report the link and that the next SessionStart banner will surface it
   (`LINKED DESIGN PROJECT: <name>`). From now on, "read/sync the design project" needs no project
   id from the user — the agent reads it from the file.

## What this does NOT do
- It does **not** sync components — that's the built-in **`/design-sync`** skill (incremental, one
  component at a time, plan-gated writes). `/design-link` just records *which* project.
- It does **not** store credentials — the binding is a pointer (a project id + name), never a token.

## Cross-references
- The binding is surfaced by [`../../scripts/capability-orientation.py`](../../scripts/capability-orientation.py) (SessionStart banner) — leak-safe (name + mirror dir; the id stays in the file).
- Canon: [`../../knowledge/design-project-binding.md`](../../knowledge/design-project-binding.md).
