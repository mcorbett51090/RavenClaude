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

**A malformed hook response SILENTLY ALLOWS the command.**
`[docs-verified via Cursor's own bug tracker — forum.cursor.com/t/…/152669, "malformed JSON response
silently allows command instead of blocking"]`

Read that against this repo's entire premise and the consequence is stark: **on Cursor, a guardrail
that emits slightly-wrong JSON does not fail loudly — it disappears.** Every other host in this
marketplace fails *closed* on a broken hook (Claude Code and Codex treat a non-zero exit as a block;
Copilot's `preToolUse` "fails closed — an error/crash/timeout denies the tool"). Cursor is the
exception, and it is the reason the adapter is written the way it is:

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
