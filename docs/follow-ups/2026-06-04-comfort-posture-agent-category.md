# Follow-up — comfort-posture has no `subagent_dispatch` category

**Date:** 2026-06-04
**Severity:** medium (UX papercut, not a security issue)
**Surfaced by:** Matt during `/code-review` xhigh — every one of 9 parallel finder agents prompted for permission

## What happened

I ran `/code-review` at xhigh effort across the 28-commit batch that landed in `main`. The skill fans out via 9 parallel subagent dispatches (the `Agent` tool, internally a `Task` tool call in Claude Code's permission grammar). **Every single dispatch prompted Matt for approval.**

Root cause:

| Layer | Allow rules | Has `Agent`? |
|---|---|---|
| `.claude/settings.json` (project, committed) | 0 (deny-only by design) | n/a |
| `.claude/settings.local.json` (personal) | 117 (Bash×105, Read/Edit/Write×7, Web×2) | **no** |
| `~/.claude/settings.json` (user-level) | 117 | **no** |

The comfort-posture YAML has 12 categories:

```
file_edit_global, file_edit_project, file_read_global, file_read_project,
mcp_tools, network_read, network_write,
shell_code_exec, shell_local_mutate, shell_package_install,
shell_readonly, shell_remote_mutate
```

**None of them map to subagent dispatch.** Matt set every category to `allow` for user + local layers, but `apply-comfort-posture.py` had no source category to translate into an `Agent` rule. The hole is structural: a maxed-out posture still leaves subagent dispatch prompting.

## Immediate workaround (already applied)

Added `"Agent"` (bare, matches all subagents per [the permissions docs](https://code.claude.com/docs/en/permissions.md#agent-subagents)) to `.claude/settings.local.json`'s allow array. Subagent dispatches now auto-approve.

**Caveat:** `apply-comfort-posture.py`'s docstring says it OVERWRITES `permissions.{allow,ask,deny}` in the layer it targets. If a future `/set-posture` run rewrites `settings.local.json`, the hand-added `Agent` rule may be clobbered. Verify before assuming the patch is durable.

## Proposed fix

Two parts:

### Part 1 — Add a category to the comfort-posture YAML schema

Add a 13th category in [`plugins/ravenclaude-core/skills/set-posture/SKILL.md`](../../plugins/ravenclaude-core/skills/set-posture/SKILL.md):

```yaml
categories:
  subagent_dispatch:
    user: allow      # one of: allow | ask | deny | inherit
    local: allow
    project: inherit
```

Semantics: `allow` → emit `"Agent"` (bare) into the target layer's allow array; `ask` → emit nothing and rely on Claude Code's default-prompt behavior; `deny` → emit `"Agent"` into the deny array (this disables ALL subagents — note that a more granular shape uses `Agent(SubagentName)` per the docs).

### Part 2 — Extend `apply-comfort-posture.py`'s emission table

Add `subagent_dispatch` to the category → rule translation table around `plugins/ravenclaude-core/scripts/apply-comfort-posture.py:78` (the patterns/levels structure). The emission for `allow` is the single string `"Agent"`; `deny` is also `"Agent"`. No path globs needed because the tool doesn't take a path-style specifier.

### Optional Part 3 — Per-subagent overrides

If Matt ever wants to deny ONE subagent (say, an experimental one) without blocking the rest, use the per-permission override mechanism the schema already has:

```yaml
categories:
  subagent_dispatch:
    user: allow
    overrides:
      "Agent(experimental-agent)":
        user: deny
```

This composes cleanly with the existing per-permission override path in `category_overrides_map()` / `pattern_layer_value()`.

## Test plan

A new gate in `scripts/audit-gates.sh`:

- **must-pass**: posture YAML with `subagent_dispatch.local: allow` → `apply-comfort-posture.py` emits `"Agent"` into `.claude/settings.local.json` allow array.
- **must-fail**: posture YAML with NO `subagent_dispatch` key → script either (a) errors with a clear "missing category" message, or (b) defaults to `ask` and emits nothing. Pick one explicitly.

## Why this is medium-severity not high

- Security envelope is intact — the `security_deny` floor still blocks the worst Bash patterns regardless of subagent-dispatch posture.
- Workaround is one line in a gitignored file.
- The pain is wall-clock and frustration, not data loss.

## Why this is worth fixing soon

- `/code-review`, `/ultraplan`, and most multi-agent skills fan out 5-15 subagents. Every one of them currently prompts unless the user has hand-added `"Agent"`.
- The dashboard's "Save & apply" workflow is supposed to be the canonical way to relax posture. As long as the YAML schema lacks this category, the dashboard literally cannot fix the issue — it's not a knob in the UI yet.
- The fix is small: one category, one emission, one gate.

## Linked artifacts

- Permissions docs (load-bearing for the exact syntax): https://code.claude.com/docs/en/permissions.md#agent-subagents
- `plugins/ravenclaude-core/skills/set-posture/SKILL.md`
- `plugins/ravenclaude-core/scripts/apply-comfort-posture.py:78` (emission table)
- `.claude/settings.local.json` (where the workaround currently lives)
