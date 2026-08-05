# Gemini CLI — the customization surface, and why the lane is cheap

**Status:** `[docs-verified 2026-07-29]` against <https://geminicli.com/docs/hooks/>,
<https://geminicli.com/docs/hooks/reference/> and <https://geminicli.com/docs/cli/gemini-md/>.
Every platform claim carries its provenance; repo claims are `[verified]`.

Created as the prerequisite artifact for the Gemini lane (multi-host audit MH-30), following the
rule the Codex lane established the hard way: build a host lane only after reading *that host's*
own docs (MH-15).

---

## The headline: Gemini's hook contract is nearly Claude's

The audit recorded Gemini as *"name-checked 17 times, supported zero times"* and framed it as an
open question — support it, or formally unsupport it. The answer turns out to be cheap, because
Gemini CLI ships a **real hooks API** whose contract is closer to Claude Code's than Copilot's is.

| Surface | Claude Code | **Gemini CLI** | Copilot CLI |
|---|---|---|---|
| stdin fields | `session_id`, `cwd`, `tool_name`, `tool_input`, `transcript_path` | **identical names** | `toolName`, `toolArgs` (JSON *string*) |
| Block mechanism | `exit 2` + stderr as reason | **identical** — exit 2 is a "System block"; stderr becomes the reason | JSON `permissionDecision` |
| Per-tool matcher | yes | **yes**, and regex (`"read_.*"`) | none in the native format |
| Tool-name VALUES | `Bash`, `Read`, `Write` | **snake_case** — `run_shell_command`, `read_file`, `write_file` | lowercase `bash`, `edit` |

**So the lane needs a thin shim, not an adapter:** `exit 2` passes straight through, and the stdin
field names already match. The only genuine translation is the **tool-name vocabulary** — which is
exactly the defect that made the tribunal a silent no-op under Copilot (MH-01). Getting that wrong
here would reproduce it on a third host.

### Events

`SessionStart` · `SessionEnd` · `BeforeAgent` · `AfterAgent` · `BeforeModel` · `AfterModel` ·
`BeforeToolSelection` · **`BeforeTool`** · **`AfterTool`** · `PreCompress` · `Notification`

### `BeforeTool` I/O

stdin: `session_id` · `transcript_path` · `cwd` · `hook_event_name` · `timestamp` · `tool_name` ·
`tool_input` · `mcp_context` · `original_request_name`

stdout (optional): `decision: "allow"|"deny"|"block"` · `reason` · `continue` · `stopReason` ·
`systemMessage` · `suppressOutput` · `hookSpecificOutput.tool_input` (argument rewrite)

Exit codes: **0** = success, stdout parsed as JSON · **2** = system block, tool prevented, stderr is
the reason, turn continues · **anything else** = non-fatal warning, CLI continues.

> **The exit-2 path is why this lane is safe to build.** Every RavenClaude guardrail already blocks
> by `exit 2` + stderr. Under Gemini that needs **no translation at all** — unlike Cursor, where a
> malformed JSON response silently ALLOWS, so the deny had to be a fixed literal. Gemini's blocking
> path does not depend on us emitting well-formed JSON.

### Where hooks are configured

`.gemini/settings.json` (project) · `~/.gemini/settings.json` (user) ·
`/etc/gemini-cli/settings.json` (system). Shape:

```json
{ "hooks": { "BeforeTool": [ { "matcher": "write_file|replace",
    "hooks": [ { "name": "…", "type": "command", "command": "…", "timeout": 5000 } ] } ] } }
```

Extensions may also carry `hooks/hooks.json`, but the settings route is what a consumer repo can
wire without publishing an extension.

---

## `GEMINI.md` — and why this lane needs no projection

`[docs-verified]` Gemini loads `~/.gemini/GEMINI.md` (global), then workspace directories and their
parents, then just-in-time as tools touch files. It is loaded **automatically**, the filename is
configurable via `context.fileName`, and — the load-bearing part —

> **it supports `@file.md` imports, relative or absolute.**

So the instruction lane is a **one-line `GEMINI.md` that imports `AGENTS.md`**, exactly as
`CLAUDE.md` `@`-imports it. No projection, no generated copy, nothing to drift. Compare Aider,
which needed a real projection because `CONVENTIONS.md` has no import mechanism, and Copilot, which
needed a pointer file. **Gemini is the only non-Claude host that can simply include the canonical
file.**

---

## What this means for the lane

1. **Wire `BeforeTool` / `AfterTool` / `SessionStart`.** Their schemas are published.
2. **Normalise tool names** — `run_shell_command` → `Bash`, `read_file` → `Read`,
   `write_file` → `Write`, `replace` → `Edit`. This is the MH-01 lesson; a guardrail that dispatches
   on `Bash` sees `run_shell_command` and falls through to "no decision, proceed".
3. **Do NOT translate blocking.** `exit 2` is already the contract. Leave it alone.
4. **`GEMINI.md` imports `AGENTS.md`** — do not generate a copy.
5. **Claude's `Stop` and `UserPromptSubmit` are NOT wired.** `AfterAgent` / `BeforeAgent` /
   `SessionEnd` are plausible counterparts, but their payload schemas were not published on the
   pages verified, and mapping a lifecycle event by name-similarity is how a lane ends up asserting
   coverage it does not have. Wire them when their schemas are read, not before.
