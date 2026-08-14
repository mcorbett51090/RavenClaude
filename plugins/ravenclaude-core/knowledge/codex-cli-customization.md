# Codex CLI — the customization surface, and why it is NOT another Copilot

> **Worktree bound.** Codex CLI `workspace-write` sandbox is the write floor (cwd + tmp; asks before editing outside the workspace). `worktree-guard.sh` FOREIGN-TREE is extra defense against a sibling worktree path. After any byte change to that hook, Codex consumers must `/hooks` (hash-trust). ChatGPT desktop **managed worktrees** are a different product and are not this marketplace's Codex CLI lane.

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

## Hook TRUST is hash-based — and it inverts this repo's update pillar (MH-17)

`[docs-verified 2026-07-28]` Codex records trust against **each hook's current hash**: *"new or
changed hooks are marked for review and skipped until trusted."* Users review via `/hooks`.
Plugin-bundled hooks use the same non-managed trust flow — **installing a plugin does not
auto-trust its hooks.**

Read that against this repo's headline update pillar — *"an update is just `git pull`. No
re-install, ever."* — and the two multiply into a **silent disarm**:

1. `git pull` changes a byte in any of the ~18 hook scripts.
2. Every changed hook's hash is now unknown, so Codex **skips it**.
3. The guardrail is off, and **nothing announces it** — because the SessionStart capability
   banner that would have told you **is itself a hook**, skipped by the same mechanism.

With near-weekly plugin bumps, the steady state for an un-warned Codex consumer is
**guardrails silently off after every update.** This is the single most dangerous property of
the Codex lane, and it is a property of the host, not a bug in the wiring.

### What ships against it

| Layer | Where | What it does |
|---|---|---|
| Install-time notice | `ravenclaude install --host codex` | names the hook count and says to run `/hooks` |
| **Update-time notice** | `ravenclaude update` | fires whenever `.codex/hooks.json` exists — the moment the disarm actually happens |
| Status | `ravenclaude status` | reports the count and that they must be **TRUSTED**, not merely wired |
| Generated file | `.codex/hooks.json` `description` | carries the warning where a reader of the artifact will find it |

### The fix we deliberately did NOT ship

**`--dangerously-bypass-hook-trust`.** Turning off the trust check to make trust convenient is
**governance theatre** — the exact anti-pattern [`skills/external-agent-onboarding/SKILL.md`](../skills/external-agent-onboarding/SKILL.md)
lists by name. It converts an honest "your guardrails are off" into a dishonest "your guardrails
are on", which is strictly worse than the problem.

**For teams, the real answer is `requirements.toml` managed hooks** `[docs-verified]` — managed
hooks are auto-trusted by policy and cannot be disabled, and are therefore *the only
configuration in which RavenClaude's guardrails survive an update unattended on this host.*

---

## What this means for the Codex lane (supersedes the Copilot-shaped plan)

1. **No adapter.** Do not build a `codex-hook-adapter.sh`. The contract already matches.
2. **No tool-name map.** Codex sends `"Bash"`, PascalCase — the same value
   `thing-orchestrator.sh:113-116` already dispatches on. The Copilot normalisation (`f55039ec`) is
   **Copilot-specific** and must not be generalised to Codex.
3. ~~**The real gap is the installer.**~~ ✅ **CLOSED 2026-07-28 (MH-07).**
   `ravenclaude install --host codex` now wires the lane: all 50 skills symlinked into
   `<project>/.agents/skills/` `[docs-verified — learn.chatgpt.com/docs/build-skills]`, and
   `<project>/.codex/hooks.json` written in the **Claude-shaped** schema. Host is auto-detected,
   but ambiguity resolves to `copilot` so no existing user's install silently changes.
   **Still not wired, and the installer says so at install time:** MCP (`.codex/config.toml`
   `[mcp]` — a bad TOML merge would clobber a hand-tuned config) and `sandbox_mode` /
   `approval_policy` (MH-16 part 2).
4. ~~**The second real gap is `CLAUDE_PROJECT_DIR` / `CLAUDE_SESSION_ID`.**~~ ✅ **CLOSED
   2026-07-28** — via the stdin route, which is the one the docs actually support.
   [`hooks/codex-hook-env.sh`](../hooks/codex-hook-env.sh) lifts `cwd` / `session_id` out of the
   payload, passes stdin through **byte-identical**, and propagates the hook's exit code
   **verbatim** (exit 2 = block). Proven by **Gate 155**, whose two must-fail halves show the
   exit-code and blanks-only invariants aren't vacuous.
   **Note the trap this avoided:** `_portable.sh`'s `_rc_host_env` falls back to
   `CODEX_PROJECT_ROOT` / `SESSION_ID` / `PROJECT_DIR` — **none of which are in Codex's documented
   environment.** Those fallbacks are harmless (fill-blanks-only) but they close nothing; the env
   alias looked like the fix and was not. Stdin is the documented, reliable source.
5. **Containment differs — and Codex holds the STRONGER boundary, by default.**
   `[docs-verified 2026-07-28 — https://learn.chatgpt.com/docs/sandboxing]` Codex ships its own OS
   sandbox using the same primitives Claude Code's optional one does — **Seatbelt** (macOS),
   **bubblewrap** (Linux/WSL2), native Windows sandbox — governed by
   `sandbox_mode` ∈ `read-only` | `workspace-write` | `danger-full-access` (**default
   `workspace-write`**, sandboxing applied automatically) × `approval_policy` ∈ `untrusted` |
   `on-request` | `never`. The docs are explicit that *"The sandbox applies to spawned commands, not
   just to built-in file operations"* — so it closes the **subprocess** gap that no tool-layer deny
   can. The plugin `CLAUDE.md` guidance that "the OS sandbox is Claude-only, use a container" was
   generalised from Copilot and is **wrong for Codex**; corrected in that file 2026-07-28 (MH-16
   part 1). *Provenance upgraded from `[inferred]` → `[docs-verified]` on 2026-07-28 by fetching the
   primary source, per the discipline below — the earlier marker was correct to withhold trust.*
   ~~**Still true and still the gap:** nothing in this repo writes `.codex/config.toml`.~~
   ✅ **CLOSED 2026-07-28 (MH-16 part 2)** — see the next section.

---

## The sandbox posture emitter — and the rule that governs it (MH-16 part 2)

`ravenclaude install --host codex` projects the comfort posture onto Codex's two real controls via
`scripts/emit-codex-config.py`. Verified schema
`[docs-verified 2026-07-28 — learn.chatgpt.com/docs/config-file/config-reference]`:

| Key | Where | Values |
|---|---|---|
| `sandbox_mode` | **top-level** | `read-only` · `workspace-write` · `danger-full-access` |
| `approval_policy` | **top-level** | `untrusted` · `on-request` · `never` · granular object |
| `network_access` | `[sandbox_workspace_write]` | boolean |

### The governing rule: NEVER SILENTLY WEAKEN (owner decision)

- absent → **write it**
- posture stricter → **tighten it**
- posture looser → **REFUSE**, printing the exact line to change by hand

The failure direction is always toward safety, and a tightening is trivially reversible. Mirroring the
posture in both directions was the rejected alternative: it would let a saved dashboard click silently
widen a sandbox somebody had deliberately locked down, with no warning to the person who locked it.

**`danger-full-access` and `approval_policy = "never"` are never emitted at any posture.** There is no
posture that means "turn the OS boundary off"; anyone who wants that can type it and own it.

### Three honesty caveats, all stated at install time

1. **It is COARSE.** Two enum keys cannot express twelve posture categories. This is a projection, not
   the parity the Claude lane has — and claiming otherwise would be the same false assurance the
   Pipeline tab used to give (MH-04).
2. **Layer aggregation takes the STRICTEST level**, not the permission engine's real layering. A
   deliberate simplification: for an OS sandbox it is the only aggregation that cannot produce a
   too-permissive boundary.
3. **A project `.codex/config.toml` loads ONLY IN TRUSTED PROJECTS** `[docs-verified]` — a second trust
   gate beside MH-17's hook hashing. **Writing the file is not the same as bounding the session**, and
   the tool must never imply it is.

### Two engineering notes worth keeping

- **No `tomllib`.** It is stdlib only on Python 3.11+; stock macOS ships **3.9.6** `[verified this
  session]`, and this repo has already paid for stock-macOS portability three times over. The reader is
  a tiny line scanner that **refuses on anything it cannot confidently parse** rather than guessing — a
  misparse here silently weakens an OS boundary.
- **Root keys must be written ABOVE the first `[table]`.** In TOML every key belongs to the most recent
  table, so appending `sandbox_mode` to the end of a file containing `[mcp_servers.github]` sets
  `mcp_servers.github.sandbox_mode` — valid TOML, wrong meaning, invisible in a diff, and Codex would
  fall back to its default while the tool reported success. Caught in testing; **Gate 156 carries a
  must-fail half for it**, and the emitted output was verified with an independent TOML parser.
- **`network_access` is a BOOLEAN, and quoting it silently breaks it.** `network_access = "false"` is
  the TOML *string* `"false"`, not the boolean Codex expects. This shipped broken first in the
  **tighten** path — i.e. the security-relevant direction produced the malformed value — and
  **Gate 156 was GREEN while it was live**, because the self-test never exercised a boolean tighten.
  A gate is only as good as the paths it reaches; the case is now asserted in both directions and
  confirmed with a real parser (`type: bool`), not by reading the file.

**Still not wired:** MCP servers (`[mcp_servers.*]`). A bad merge would clobber a hand-tuned config,
and that surface is not yet worth the risk.

---

## Provenance discipline

Any row above marked `[inferred]` must be verified before it is built on. The rest were read from
the linked source on 2026-07-28. If Codex changes its hook contract, this file — not a Copilot doc —
is the thing to update.
