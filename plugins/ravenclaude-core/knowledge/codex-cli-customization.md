# Codex CLI — the customization surface, and why it is NOT another Copilot

**Status:** `[docs-verified 2026-07-28]` against <https://learn.chatgpt.com/docs/hooks>
(reached via a 308 from `developers.openai.com/codex/hooks`). Every platform claim below carries
its provenance. Repo claims are `[verified]` with `file:line`.

Created as the prerequisite artifact for the Codex lane (multi-host audit MH-15). Before this file
existed, every Codex work item in the repo cited **Copilot's** mechanics doc — which is the wrong
model, and the reason the whole lane was mis-scoped.

---

## The headline: Codex speaks the Claude Code hook contract

This is the single most important fact about the Codex lane, and it inverts the assumption the repo
was built on (`{Claude Code} ∪ {everything else = Copilot}`).

| Surface | Claude Code | **Codex** | Copilot CLI |
|---|---|---|---|
| Event names | `PreToolUse`, `SessionStart`, … | **identical, PascalCase** | `preToolUse`, `sessionStart` (camelCase) |
| stdin fields | `tool_name`, `tool_input`, `cwd`, `session_id` | **identical** | `toolName`, `toolArgs` (JSON *string*) |
| Tool-name values | `Bash`, `Read`, … | **identical PascalCase** (`"Bash"`) | lowercase `bash`, `edit`, `view` |
| Block mechanism | `exit 2` + stderr | **identical** (also JSON `permissionDecision`) | JSON `permissionDecision` |
| Output envelope | `hookSpecificOutput` | **identical** | top-level `permissionDecision` |
| Plugin hooks | reads `hooks/hooks.json` | **reads `hooks/hooks.json` directly** | plugin hooks **do not fire** (#2540) |

**Consequence: Codex needs NO envelope adapter.** Copilot required a 456-line generator plus
~300 lines of `copilot-hook-adapter.sh` translation. Codex requires neither — it reads the plugin's
`hooks/hooks.json` and speaks the same protocol end to end.

> Codex's full event set is **`SessionStart`, `SessionEnd`, `PreToolUse`, `PostToolUse`,
> `PermissionRequest`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStart`,
> `SubagentStop`, `Stop`** — a superset of the six RavenClaude registers.

### PreToolUse stdin (verbatim field list)

`session_id` · `turn_id` · `cwd` · `hook_event_name` · `tool_name` · `tool_use_id` · `tool_input` ·
`permission_mode` · `model` · `transcript_path`

### Blocking

Three accepted shapes: `exit 2` + stderr; a JSON `hookSpecificOutput.permissionDecision: "deny"`
(with optional `permissionDecisionReason`, `updatedInput`, `additionalContext`); and a legacy
`{"decision": "block"}`.

---

## Where hooks are configured

- `~/.codex/hooks.json`, or a `[hooks]` table in `~/.codex/config.toml`
- `<repo>/.codex/hooks.json`, or `<repo>/.codex/config.toml`
- **Plugin bundles: Codex looks for `hooks/hooks.json` in the plugin root** (or a path named in the
  plugin manifest)

---

## Environment variables — and a CORRECTION to this repo's own shim

Codex exposes to a hook:

| Variable | Note |
|---|---|
| `PLUGIN_ROOT` | installed plugin root |
| `PLUGIN_DATA` | plugin's writable data directory |
| **`CLAUDE_PLUGIN_ROOT`** | **provided as a legacy-compatibility name** |
| **`CLAUDE_PLUGIN_DATA`** | **provided as a legacy-compatibility name** |

> Session values such as `cwd` arrive **via stdin JSON, not the environment.**

**This corrects a claim made in `hooks/_portable.sh` and in the audit ledger.** Both stated that all
18 hooks "fail open on variable names alone" because Codex supplies `PLUGIN_ROOT` where the hooks
read `CLAUDE_PLUGIN_ROOT`. That is **wrong for `CLAUDE_PLUGIN_ROOT`** — Codex supplies it directly as
a compatibility alias, so hooks resolving their helper path work unaided.

What **does** still break, and why the shim is still correct to keep:

- **`CLAUDE_PROJECT_DIR` is NOT in the compatibility set.** 25 hook files read it. `_emit-event.sh`
  no-ops when it is unset, so **no hook event is ever written** and the Guardrails dashboard
  (Heimdall / Víðarr) stays dark — which is exactly the "unwatched, not clean" state now surfaced
  honestly by `d9185f4e`.
- **`CLAUDE_SESSION_ID` is NOT in the compatibility set.** 14 hook files read it; events would land
  under `runs/unknown/` even if the project dir were resolved.

`_rc_host_env` fills blanks only and never overwrites, so where Codex already supplies
`CLAUDE_PLUGIN_ROOT` the alias is a harmless no-op — the shim is right, one sentence of its
justification was not. Corrected here rather than quietly left standing.

---

## What this means for the Codex lane (supersedes the Copilot-shaped plan)

1. **No adapter.** Do not build a `codex-hook-adapter.sh`. The contract already matches.
2. **No tool-name map.** Codex sends `"Bash"`, PascalCase — the same value
   `thing-orchestrator.sh:113-116` already dispatches on. The Copilot normalisation (`f55039ec`) is
   **Copilot-specific** and must not be generalised to Codex.
3. **The real gap is the installer.** `scripts/ravenclaude` has **zero** Codex references
   `[verified 2026-07-28]`, so `ravenclaude setup` completes and wires nothing. Codex reads skills
   from `.agents/skills` and config from `.codex/config.toml` — neither is written today.
4. **The second real gap is `CLAUDE_PROJECT_DIR` / `CLAUDE_SESSION_ID`**, per above. Either export
   them from a Codex-aware install path, or derive them from the stdin payload (`cwd`, `session_id`),
   which the hooks already receive.
5. **Containment differs.** Codex ships its own OS sandbox with `approval_policy` × `sandbox_mode`.
   The plugin `CLAUDE.md` guidance that "the OS sandbox is Claude-only, use a container" was
   generalised from Copilot and is **wrong for Codex** `[inferred — the sandbox model was reported by
   the audit but is not re-verified in this file; check config docs before acting on it]`.

---

## Provenance discipline

Any row above marked `[inferred]` must be verified before it is built on. The rest were read from
the linked source on 2026-07-28. If Codex changes its hook contract, this file — not a Copilot doc —
is the thing to update.
