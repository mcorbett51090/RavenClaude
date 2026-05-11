# Authoring PreToolUse / PostToolUse / Stop hooks

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Plugin authoring, hook design, agent guardrails.

**Applies to:** Anyone adding a hook to a plugin's `hooks/` directory (currently `plugins/ravenclaude-core/hooks/`; same patterns apply to future plugins).

---

## Why this exists

Hooks are how the marketplace enforces behavior the model can't enforce itself — auto-formatting after writes, blocking destructive commands the deny list missed, end-of-session reminders. The `ravenclaude-core` plugin ships three working hooks today, and future plugins will need more. But hooks have non-obvious failure modes: silent no-ops, payload-parsing bugs, watcher caveats, double-blocks with the settings deny list. This doc captures the patterns the existing three hooks demonstrate so the next hook author starts from a known-good shape.

## How to apply

### Pick the right event

| Event | When it fires | Can block? | Use for |
|---|---|---|---|
| `PreToolUse` | Before a tool runs | **Yes** — exit 1 blocks the call | Guards (destructive command refusal, secret-leak prevention) |
| `PostToolUse` | After a tool succeeds | No — exit code is logged only | Cleanup (auto-format, lint, regen artifacts) |
| `Stop` | When Claude finishes a turn | Can re-wake the model with exit 2 + `asyncRewake` | Reminders (run full test suite, commit-message hygiene) |

There are other events (`PostToolUseFailure`, `Notification`, `PreCompact`, `UserPromptSubmit`, `SessionStart`) — see the full list in the settings schema. The three above cover ~90% of plugin needs.

### Read the stdin payload

Every hook receives a JSON payload on stdin. The shape depends on the event:

```bash
# PreToolUse / PostToolUse for Bash
{ "tool_name": "Bash", "tool_input": { "command": "ls" } }

# PreToolUse / PostToolUse for Edit | Write | MultiEdit
{ "tool_name": "Edit", "tool_input": { "file_path": "/abs/path/to/file.ts" }, "tool_response": {...} }
#                                                                              ^^ PostToolUse only

# Stop
{ "session_id": "abc123" }
```

**This repo's existing hooks take their input as positional args**, not from stdin, because `.claude/settings.json` invokes them with shell variables (`$CLAUDE_TOOL_FILE_PATH`, `$CLAUDE_TOOL_INPUT`). That's a working pattern; you can also `jq -r` from stdin if you prefer.

### Reference the three working examples

The fastest way to start a new hook is to copy the closest-shaped existing one:

| Existing hook | Event + matcher | Shape worth copying |
|---|---|---|
| [`format-on-write.sh`](../../plugins/ravenclaude-core/hooks/format-on-write.sh) | `PostToolUse` on `Edit\|Write\|MultiEdit` | Extension-dispatch via `case`, `command -v` fallback chain, silent on no-match, never blocks |
| [`guard-destructive.sh`](../../plugins/ravenclaude-core/hooks/guard-destructive.sh) | `PreToolUse` on `Bash` | Bash-regex deny-pattern array, exit 1 + stderr explanation on match, narrowly scoped |
| [`remind-tests.sh`](../../plugins/ravenclaude-core/hooks/remind-tests.sh) | `Stop` (no matcher) | Git-aware reachability check, code-extension filter, stderr-only heredoc reminder |

### Wire it into settings

`.claude/settings.json` (project-wide) or `.claude/settings.local.json` (personal override):

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "plugins/<plugin>/hooks/my-hook.sh \"$CLAUDE_TOOL_FILE_PATH\""
      }]
    }]
  }
}
```

Project-wide rules live in `settings.json` (committed, applies to every collaborator). Personal preferences live in `settings.local.json` (gitignored). Pick the right scope before you commit.

### Test before you commit

A hook that silently does nothing is worse than no hook. Run a **pipe-test** before relying on it:

```bash
# Synthesize the payload the hook will receive, pipe it directly
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/example.ts"}}' \
  | plugins/<plugin>/hooks/my-hook.sh /tmp/example.ts

# Then verify the side effect (file formatted, sentinel written, reminder printed)
```

If pipe-test passes but the hook doesn't fire in a live session: the file watcher only watches directories that had a settings file when the session started. Open `/hooks` once (reloads config) or restart the session.

**Do:**
- `set -euo pipefail` at the top of every shell hook — fail loudly on the rare bugs, not silently.
- Guard against missing args: `file="${1:-}"; [[ -z "$file" ]] && exit 0`.
- Use `command -v <tool> >/dev/null 2>&1` before invoking external tools so a missing dependency doesn't crash the agent's flow.
- Keep hooks **idempotent** — running twice on the same input should be a no-op (format-on-write, for example, re-formats an already-formatted file with no effect).
- Print user-facing messages to **stderr** (the UI surfaces it as a system notice) and keep stdout silent unless you have a structured JSON response.

**Don't:**
- Don't block PostToolUse or Stop with exit 1 hoping it'll prevent something — only `PreToolUse` (and `Stop` via `asyncRewake`) can re-route control. Other exit codes are logged only.
- Don't shell-parse JSON with `grep`/`sed`. Use `jq -r '.tool_input.file_path'` and quote the result.
- Don't put `set -x` or chatty `echo` lines in committed hooks — every session pays the noise tax. Use a temporary sentinel file (`/tmp/hook-fired.txt`) for development, then strip before commit.
- Don't ship a hook whose deny list duplicates the `settings.json` deny list verbatim. If both layers block the same thing, you've created a double-block trap where lifting the rule in one place still leaves it blocked from the other (see the rebase-orphan lesson for the lived example).

## Edge cases / when the rule does NOT apply

- **Hook depends on a binary not in PATH** — prefix with an absolute path or use `command -v <tool> || { echo "tool missing"; exit 0; }` to no-op gracefully rather than crash.
- **PreToolUse on Edit fires *before* the edit** — the file is still in its pre-edit state when the hook reads it. If you need post-edit content, use `PostToolUse`.
- **Hook for an MCP tool** — matchers use the full MCP tool name (`mcp__server__tool`). Wildcards are not supported across server prefixes; match exact names.
- **Pure prose docs hook** — if the hook's only job is to nudge the model, prefer the `prompt` hook type (LLM-evaluated) over a shell script. Cheaper to author, no shell-injection surface.
- **Hook that needs network access** — be explicit about the timeout in `.claude/settings.json` (`"timeout": 30`). The default kills slow hooks at 60 seconds; long-running network calls should run async (`"async": true`) or be replaced with a background job.

## See also

- [`format-on-write.sh`](../../plugins/ravenclaude-core/hooks/format-on-write.sh) — canonical `PostToolUse` example.
- [`guard-destructive.sh`](../../plugins/ravenclaude-core/hooks/guard-destructive.sh) — canonical `PreToolUse` example.
- [`remind-tests.sh`](../../plugins/ravenclaude-core/hooks/remind-tests.sh) — canonical `Stop` example.
- [`.claude/settings.json` `hooks` block](../../.claude/settings.json) — how the three are wired up today.
- [Rebase orphans lesson](../memory-bank/lessons-learned.md) — the double-block trap that motivated the *don't duplicate the deny list* rule above.
- [Plugin versioning rule](./plugin-versioning.md) — bump PATCH after every hook edit; bump MINOR when adding a new hook file.
- The official Claude Code hooks reference (run `/help` in any session and search for *hooks*) for the full event list and JSON output schema.

## Provenance

Codified 2026-05-11 after modifying [`guard-destructive.sh`](../../plugins/ravenclaude-core/hooks/guard-destructive.sh) (commit `f0d58d1`) to remove an overly-aggressive `git branch -D` pattern. Tracing the block to both `settings.json` deny **and** the hook deny-patterns surfaced the *two-layer cooperation* model — and the *double-block* trap when the layers duplicate each other. The three existing hooks in `plugins/ravenclaude-core/hooks/` have been working examples since the plugin was scaffolded (commit `1596a26`); this doc names the patterns they already follow so the next author doesn't re-derive them.

---

_Last reviewed: 2026-05-11 by `mcorbett51090`_
