# Gemini CLI — the customization surface, and why the lane is cheap

> **Worktree bound.** `GEMINI.md` is loaded from `~/.gemini/`, then workspace directories and parents, then **just-in-time** when a tool accesses a path. A Read of a sibling worktree can pull that tree's `GEMINI.md` into context. FOREIGN-TREE does **not** deny Read by default. Do **not** turn on `experimental.worktrees`.

**Status:** `[docs-verified 2026-07-29]` against <https://geminicli.com/docs/hooks/>,
<https://geminicli.com/docs/hooks/reference/> and <https://geminicli.com/docs/cli/gemini-md/>.
Every platform claim carries its provenance; repo claims are `[verified]`.

Created as the prerequisite artifact for the Gemini lane (multi-host audit MH-30), following the
rule the Codex lane established the hard way: build a host lane only after reading *that host's*
own docs (MH-15).

---

## The headline: Gemini's hook contract is nearly Claude's

The audit recorded Gemini as *"name-checked 17 times, supported zero times"* and framed it as an
open question — support it, or formally unsupport it. The answer (now in
[`host-support.json`](host-support.json), `hooks.gemini.supported`) turns out to be cheap, because
Gemini CLI ships a **real hooks API** whose contract is closer to Claude Code's than Copilot's is.

| Surface | Claude Code | **Gemini CLI** | Copilot CLI |
|---|---|---|---|
| stdin fields | `session_id`, `cwd`, `tool_name`, `tool_input`, `transcript_path` | **identical names** | `toolName`, `toolArgs` (JSON *string*) |
| Block mechanism | `exit 2` + stderr as reason | **identical** — exit 2 is a "System block"; stderr becomes the reason | JSON `permissionDecision` |
| Per-tool matcher | yes | **yes**, and regex (`"read_.*"`) | none in the native format |
| Tool-name VALUES | `Bash`, `Read`, `Write` | **snake_case** — `run_shell_command`, `read_file`, `write_file` | lowercase `bash`, `edit` |

**So the lane needs a thin shim, not a full adapter:** `exit 2` passes straight through, stdin
field names already match, and the genuine translations are (1) the **tool-name vocabulary** —
exactly the defect that made the tribunal a silent no-op under Copilot (MH-01) — and (2) Claude
JSON `permissionDecision=deny` at exit 0 → Gemini exit 2 (SH-F1; the tribunal and several guards
emit that shape). Getting either wrong leaves a guardrail inert on a third host.

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

Gemini merges settings from **four** documented layers (precedence for single-value keys is in the
[settings reference](https://geminicli.com/docs/cli/settings/) — do not restate a closed three-file
list here; vendor FAQ text sometimes says "two files"). Typical paths include **project**
`<project>/.gemini/settings.json`**, **user** `~/.gemini/settings.json`, **system**
`/etc/gemini-cli/settings.json`, and **extension**-contributed settings — hooks in any layer merge
with what `ravenclaude install --host gemini` writes into the project file, so read every layer
before declaring a guardrail unwired. Shape:

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
3. **Pass `exit 2` through; ALSO honor Claude JSON deny.** Guards that already block with
   `exit 2` need no translation. Guards that emit `hookSpecificOutput.permissionDecision=deny`
   at exit 0 (tribunal) must become Gemini exit 2 — SH-F1. Do not invent a Gemini JSON deny
   path for exit-2 guards.
4. **`GEMINI.md` imports `AGENTS.md`** — do not generate a copy.
5. **Claude's `Stop` and `UserPromptSubmit` are NOT wired on Gemini.** The documented
   **`AfterAgent`** hook is the post-turn counterpart for retry/stop semantics: vendor exit code
   **`2` = system block / retry** (same blocking contract as `BeforeTool` exit 2). **`BeforeAgent`**
   and **`SessionEnd`** remain unwired until their payload shapes are verified on a live CLI — do
   not map lifecycle events by name alone. (**Hold wiring — ENH-039:** do not attach `dod-gate.sh` or other Stop-lane guardrails to `AfterAgent` until the AfterAgent stdin payload is read from the hooks reference and a self-limit for exit-2 retry loops is designed. UserPromptSubmit stays unwired.)

## Gemini CLI 0.60 — host-security alignment (DOC adapt 2026-09-20 — UNVERIFIED)
[verify-at-use · angle release-gemini-cli-0.60.0 · KEEP sandbox/path gates]

These controls ship **in Gemini CLI**. RavenClaude's `hooks/gemini-hook-adapter.sh`
stays a thin shim (tool-name normalize + `THING_HOST` + exit-2 passthrough + JSON-deny
→ exit 2). Do **not** weaken RC FOREIGN-TREE / Seatbelt-aligned guidance when documenting them.

| 0.60 theme | Operator / adapter expectation | RC posture |
|------------|--------------------------------|------------|
| **MCP OAuth RFC 9207 issuer strictness** | Issuer identification in MCP OAuth must match strictly; mis-issuer → fail closed | Document only; no adapter bypass. Multi-harness: Grok bots \| Cursor \| Claude \| SuperGrok — applies when host is Gemini |
| **Extension consent + env sanitize** | Explicit consent before extension-driven env changes; sanitize runtime-altering env vars | Do not inject unsanitized env in installer/settings generators |
| **Path / symlink / SFN (NTFS 8.3) boundary hardening** | Workspace boundary validation, symlink resolution, short-name mitigation across command safety + discovery | KEEP — aligns with existing worktree-bound / FOREIGN-TREE note at top of this file; do not recommend `experimental.worktrees` |
| **Envelope metadata provenance (untrusted tool outputs)** | Treat tool-result envelope metadata as **untrusted provenance**; do not promote it to trusted policy input | Adapter must not strip provenance fields if/when present; guards that consume outputs should assume hostile metadata |
| **Sandbox / settings / temp isolation + macOS Seatbelt path isolation** | Settings/temp dirs isolated in sandbox containers | KEEP gate/host safety — compare DIGEST KEEP bullet; adapt docs only |
| **System-wide config ownership checks + extension loader path resolution** | Strict permission/ownership on system config paths; hardened extension loader boundaries | Installers must not chmod/chown their way around checks |

### Hook-adapter non-goals (do not "helpfully" encode in the shim)
- Re-implementing Gemini's OAuth issuer checks inside bash.
- Softening exit-2 deny into JSON-allow on parse failure (Cursor fail-open class — Gemini is exit-2 safe).
- Treating envelope metadata as authenticated identity.

---

## Comfort posture projection (2026-10-09)

`scripts/emit-gemini-config.py` (called from `ravenclaude install --host gemini` when `.ravenclaude/comfort-posture.yaml` exists) merges **tighten-only** values into `<project>/.gemini/settings.json`:

- `general.defaultApprovalMode` — `default`, `auto_edit`, or `plan` (never `yolo`; CLI-only per vendor docs).
- `tools.sandboxNetworkAccess` — boolean; tightening to `false` is allowed; loosening is refused.

Gemini's OS sandbox remains **opt-in** (`--sandbox` defaults off); this projection does not enable the sandbox by itself.

## Extension manifest (2026-10-09)

`plugins/ravenclaude-core/gemini-extension.json` + `GEMINI.md` (`@AGENTS.md`) support `gemini extensions install <path>` packaging. Skills/agents via extension are **not** marked supported in `host-support.json` until a live install probe confirms they load.

