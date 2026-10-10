# Harness Spectate (v0.7)

Observe-only livestream of atlas harness agent loops: see / understand / direct (direct is out of scope for v0.1).

## Open it

```bash
bash plugins/ravenclaude-core/bin/rc spectate
bash plugins/ravenclaude-core/bin/rc spectate --demo
```

Or, with a dashboard server already running on loopback: open `/spectate`.

On Claude Code, the `spectate` skill opens the UI and arms the push mirror (`monitors/watch-spectate.sh`) for the rest of the session.

## Honesty (v0.7)

- **v0.7 Cursor/Gemini partial emit.** Per-event skip in the Cursor/Gemini hook generators wires `spectate-emit.sh` on supported lanes (Cursor: SessionStart / UserPromptSubmit / Stop / Bash-PreToolUse; Gemini: SessionStart / PreToolUse / PostToolUse) — see `host-support.json` `hooks.cursor` / `hooks.gemini` (Gates 159/164). Adapters forward stdin + `CLAUDE_HOOK_EVENT`. `tool_use_id` → `corr_id` remains unsupported on those hosts (adapters do not mint it). PreCompact / SubagentStart / PermissionRequest (and Cursor PostToolUse) stay explicitly skipped.
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
