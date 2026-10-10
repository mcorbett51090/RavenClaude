# Harness Spectate (v0.11)

Observe-only livestream of atlas harness agent loops: see / understand / direct (direct is out of scope for v0.1).

## Open it

```bash
bash plugins/ravenclaude-core/bin/rc spectate
bash plugins/ravenclaude-core/bin/rc spectate --demo
```

Or, with a dashboard server already running on loopback: open `/spectate`.

On Claude Code, the `spectate` skill opens the UI and arms the push mirror (`monitors/watch-spectate.sh`) for the rest of the session. <!-- delegation-nudge-ok: documents the skill surface, not a hand-back -->

## Honesty (v0.11)

- **v0.11 Codex lifecycle observe.** `generate-codex-hooks.py` wires `spectate-emit.sh` on Codex `UserPromptSubmit` / `SubagentStart` / `PreCompact` / `PermissionRequest` (native Claude contract; docs-verified event set `[docs-verified 2026-07-28 — learn.chatgpt.com/docs/hooks]`). Steer stays unwired. Codex `tool_use_id` capability is `supported` (docs PreToolUse field list + native payload forward).
- **v0.10 Cursor preToolUse/postToolUse observe.** `spectate-emit.sh` wires Cursor `preToolUse` / `postToolUse` (adapter `tool-pre` / `tool-post`) — all tools + docs-verified `tool_use_id` `[docs-verified 2026-10-10 — cursor.com/docs/agent/hooks]`. `tool-pre` always emits `{"permission":"allow"}`; never forwards `tool_output` / `agent_message`. Bash enforcement stays on `beforeShellExecution`; formatters stay on `afterFileEdit`. Cursor `tool_use_id` capability is `supported` (docs + Gate 159 forward; same bar as copilot-cli).
- **v0.9 Codex tool/stop emit + Cursor PreCompact/SubagentStart.** Codex fixed lists wire `spectate-emit.sh` on PreToolUse / PostToolUse / Stop (SessionStart already derived). Cursor `preCompact` / `subagentStart` observe; SubagentStart always returns `{"permission":"allow"}`, never forwards `task`, maps `tool_call_id` → `tool_use_id`. PermissionRequest stays skipped on Cursor/Gemini.
- **v0.8 Cursor afterFileEdit + tool_use_id forward.** `file-posttool` builds Claude-shaped stdin (`Edit` + `file_path` only — never `edits[]`). Adapters forward host `tool_use_id` / `toolUseId` when present; never mint from `generation_id`.
- **v0.7 Cursor/Gemini partial emit.** Per-event skip wires SessionStart / UserPromptSubmit / Stop / Bash-PreToolUse (Cursor) and SessionStart / PreToolUse / PostToolUse (Gemini).
- **v0.7 launcher hygiene.** `scripts/open-dashboard.sh` `WALK=10` mirrors `_bind_server` span=10 (8000–8010).
- **v0.6 Claude monitor push mirror.** Skill `spectate` starts `spectate-push-mirror` (`on-skill-invoke:spectate`). Derived labels only (kind / status / tool name / steer action) for permission.*, steer.applied, tool.fail, session.*, subagent.*, *.truncated — never paths, prompts, or note text. Claude Code only; other hosts keep the pull `/spectate` UI.
- **v0.5 true interrupt.** With `spectate_steer: on`, browser Interrupt arms `interrupt_pending`; the next PreToolUse/PostToolUse/UserPromptSubmit/PermissionRequest emits top-level `continue: false` + `stopReason` (docs-verified agentic-loop stop). Pause-as-deny and Approve/Deny remain.
- **v0.4 approve/deny.** Browser Approve/Deny arm PermissionRequest wait ≤45s.
- **v0.3 SSE + steer.** EventSource stream + opt-in pause/note.
- **v0.2 emit hooks.** `hooks/spectate-emit.sh` appends scrubbed `rc.spectate.v1` lines on SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop / SubagentStart / PreCompact / PermissionRequest. Observe-only (always exit 0). Deny join uses `corr_id` from `tool_use_id` on both spectate-events and hook-events.
- **Observe-only.** The UI never POSTs; the server never accepts Spectate writes except CLI demo.
- **Capability cells stay `unknown` until measured.** Empty / missing streams reduce to `idle` with cause-not-established — never to `unavailable-harness`. v0.2: grok-build `deny_*` is `partial` from a measured harness-detect probe + atlas F06.output-blocking; event-catalog cells and grok-bot stay `unknown`.
- **Fonts.** IBM Plex Sans/Mono are vendored OFL woff2 under `dashboard-assets/spectate/fonts/` (no CDN).
- **localStorage is per-origin.** Changing the bind port loses prefs.
- A visible Spectate tab keeps `--max-idle` from firing via the 2s poll activity.

## Surfaces

| Path | Role |
|---|---|
| `/spectate` | UI shell (assets under `dashboard-assets/spectate/`) |
| `/__spectate/capabilities` | Static capability matrix |
| `/__spectate/sessions` | Discoverable sessions |
| `/__spectate/nodes` | Reduced graph for one session |
| `/__spectate/events` | Scrubbed event page |

Loopback / Codespace-Host peer check + existing Origin/Host CSRF floor. No CORS.
