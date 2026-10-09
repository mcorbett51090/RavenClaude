# Cursor — the customization surface, and the one place it fails OPEN

**Status:** `[docs-verified 2026-07-28]` against <https://cursor.com/docs/agent/hooks> and
<https://cursor.com/docs> (rules). Every platform claim carries its provenance; repo claims are
`[verified]`.

Created as the prerequisite artifact for the Cursor lane (multi-host audit MH-13 / MH-25). The Codex
lane taught this the hard way: building a host lane without first reading *that host's* own docs is
how a lane gets scoped against the wrong model (MH-15).

---

## The headline: Cursor has a real in-loop hooks API, and it is a SUPERSET of what the audit claimed

The audit entry (MH-13) listed the event set as `beforeSubmitPrompt` / `beforeShellExecution` /
`beforeMCPExecution` / `afterFileEdit` / `stop`, sourced from third-party write-ups. **The primary
docs list far more, including Claude-named events**:

| Category | Events |
|---|---|
| **Claude-shaped** | `sessionStart`, `sessionEnd`, `preToolUse`, `postToolUse`, `postToolUseFailure`, `subagentStart`, `subagentStop`, `preCompact`, `stop` |
| **Cursor-specific** | `beforeShellExecution`, `afterShellExecution`, `beforeMCPExecution`, `afterMCPExecution`, `beforeReadFile`, `afterFileEdit`, `beforeSubmitPrompt`, `afterAgentResponse`, `afterAgentThought` |
| **Tab / lifecycle** | `beforeTabFileRead`, `afterTabFileEdit`, `workspaceOpen` |

Config lives at `<project>/.cursor/hooks.json`, `~/.cursor/hooks.json`, or an enterprise path
(`/Library/Application Support/Cursor/hooks.json`, `/etc/cursor/hooks.json`, or the Windows
`ProgramData` equivalent). **`matcher` is supported** — the docs' own example scopes a hook with
`"matcher": "curl|wget|nc"`.

---

## ⚠️ THE SAFETY FACT THAT GOVERNS EVERY DESIGN DECISION HERE

Cursor hook failures split into **two classes** — do not conflate them.

| Class | What happened | Default behavior | `[docs-verified 2026-10-09]` |
|---|---|---|---|
| **Permission / schema mismatch** | Invalid JSON, wrong shape, or missing required fields on a **permission hook** (`beforeShellExecution`, `preToolUse`, `beforeReadFile`, `beforeMCPExecution`, …) | **BLOCKS** the action (same intent as other hosts) | Cursor docs: the hook must return a valid permission object; a bad response does not grant the action. |
| **Hook crash / timeout / other non-zero exit** | Script error, timeout, exit `1`, etc. (exit **`2`** is the deliberate deny path) | **Fail-open** — the action proceeds — **unless** the hook entry sets `"failClosed": true` | Documented fail-open default; `failClosed` opts into fail-closed. |

**Historical forum report (unreproduced here):** a 2026 community thread claimed malformed JSON
*silently allowed* shell execution (forum.cursor.com/t/…/152669). Treat that as **history**, not the
current docs contract — the permission-hook row above is what the published hooks reference describes
today. If Cursor regresses, re-open with a live repro.

Every other host in this marketplace still fails *closed* on many broken-hook shapes (Claude Code and
Codex treat a non-zero exit as a block; Copilot's `preToolUse` fails closed on error/crash/timeout).
Cursor's **crash/timeout** path is the outlier (fail-open unless `failClosed`), which is why the
adapter is written the way it is:

1. **The deny payload is emitted from a fixed, literal JSON string** where possible — no
   interpolation, nothing that a hostile command or a `jq` absence can make malformed.
2. **Both field spellings are emitted.** The docs specify `user_message` / `agent_message`; multiple
   community reports show `userMessage` / `agentMessage`. Unknown keys are ignored by a JSON consumer,
   so emitting both is strictly safer than betting on one. **`permission` itself is not in dispute** —
   every source agrees on it, and it is the only field that actually binds.
3. **Silence means allow, so silence is only ever emitted on a genuine allow.**

**Also reported:** `allow` and `ask` may be ignored when a command is already allow-listed, so only
`deny` reliably binds `[community-reported, not docs-confirmed]`. The adapter therefore treats deny as
the only verdict worth translating and lets everything else fall through to Cursor's own permissions.

---

## Input / output schema — `beforeShellExecution`

This is the **only** enforcement event whose full input *and* output schema the docs publish, which is
why the lane is built on it rather than on `preToolUse`.

Every hook receives a common envelope on stdin:

```
conversation_id · generation_id · model · model_id · model_params ·
hook_event_name · cursor_version · workspace_roots[] · user_email · transcript_path
```

`beforeShellExecution` adds `command`, `cwd`, `sandbox`, and returns:

```json
{ "permission": "allow" | "deny" | "ask",
  "user_message": "shown in the client",
  "agent_message": "sent to the agent" }
```

> **`preToolUse` / `postToolUse` exist but are NOT wired.** Their per-event payload fields were not
> published on the page fetched, and guessing a payload shape on a host that fails open is exactly the
> trade this repo does not make. Wire them when their schema is verified — the event names are already
> known, so it is a small change, not a redesign.

---

## Input schema — `sessionStart`, and why it never carries a `matcher`

`[docs-verified 2026-09-02 — cursor.com/docs/agent/hooks]`, checked while investigating a live
`worktree-guard.sh` self-lease-denial incident (see [`kb-tribunal-seats-abstaining.md`]'s sibling
research, `.ravenclaude/runs/forge/sessionstart-hook-safeguards/`). `sessionStart` adds to the common
envelope above:

```
session_id · is_background_agent · composer_mode ("agent" | "ask" | "edit")
```

**`sessionStart` carries no `source`-shaped field, and the matcher-config section of the docs does not
list `sessionStart` among the events matcher applies to at all** — unlike Claude Code's own
`SessionStart`, which matches `startup` / `resume` / `clear` / `compact` / `fork`. So
[`scripts/generate-cursor-hooks.py`](../../../scripts/generate-cursor-hooks.py) never emitting a
matcher for `SessionStart` is **not** an unverified-schema gap to fix later — it is the platform's own
documented ceiling: there is nothing to filter by. Every `SessionStart`-registered hook fires on every
Cursor session start, always, by design of the host, not this generator.

**What IS useful here:** `transcript_path` is present in the common envelope, same field name as
Claude Code's own hook payload — a candidate stable-across-resume identity anchor for anything (like a
worktree/session lease) that needs to recognize "this is the same logical conversation continuing"
across a process boundary, portable across at least these two hosts. Not yet verified: whether Cursor's
`transcript_path` value is stable across whatever Cursor's own equivalent of a context-compaction /
session-resume event is — that would need its own host-specific probe before a design leans on it.

---

## Rules — `.cursor/rules/*.mdc` (MH-25)

`[docs-verified — cursor.com/docs]` Cursor's primary rules mechanism is `.cursor/rules/*.mdc`, with
`description` / `globs` / `alwaysApply` frontmatter and a precedence of
**Team Rules → Project Rules → User Rules**. Cursor's docs frame `AGENTS.md` as *"a simple markdown
file … as an alternative to `.cursor/rules`"* — **the simpler, unscoped sibling, not a superset.**

The consequence for this repo is specific: a Cursor user reading only `AGENTS.md` gets flat,
always-on text. `.mdc` `globs` can express a rule that fires **only on the paths it governs** — which
is exactly the shape of this repo's most distinctive mechanism, the layout allow-list.

---

## What this means for the Cursor lane

1. **Build on `beforeShellExecution`**, not on `preToolUse`, until the latter's payload is verified.
2. **Never let the deny path depend on `jq`, string interpolation, or the shell's error handling.**
   On this host those are not robustness concerns, they are the difference between a guardrail and a
   no-op.
3. **Emit both message spellings.** Cheap, harmless, and removes a coin-flip from the safety path.
4. **The rules half is risk-free and should ship alongside** — it is fully docs-verified and needs no
   adapter.
5. **This lane is untested against a running Cursor** in this repo `[verified — no Cursor binary
   here]`. It is docs-verified, gated on its translation, and honestly labelled as such. Do not
   upgrade that claim without an actual session.

---

## Installer extras (2026-10-09)

| Artifact | Behavior |
|---|---|
| `.cursorignore` | Marker block `# BEGIN RAVENCLAUDE` / `# END RAVENCLAUDE` with secret-path globs; upsert only. |
| `.cursor/skills/` | Symlinks (or copy) from `plugins/ravenclaude-core/skills`. |
| `.cursor/agents/` | Generated by `scripts/generate-cursor-agents.py`; `readonly: true` on the five review-only agents (Codex read-only set). |
| `.cursor/BUGBOT.md` | Marker-delimited layout/discipline pointer; never replaces an existing file without the marker. |

**ENH-028:** `scripts/generate-cursor-hooks.py` sets `"failClosed": true` on every `beforeShellExecution` entry. `cursor-hook-adapter.sh` calls `_rc_adapter_internal_fail` (exit **2**) when stdin translation fails; set `RAVENCLAUDE_CURSOR_ADAPTER_LENIENT=1` to keep the old fail-open behavior on adapter errors only.

