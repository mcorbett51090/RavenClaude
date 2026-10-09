# Harness Spectate (v0.1)

Observe-only livestream of atlas harness agent loops: see / understand / direct (direct is out of scope for v0.1).

## Open it

```bash
bash plugins/ravenclaude-core/bin/rc spectate
bash plugins/ravenclaude-core/bin/rc spectate --demo
```

Or, with a dashboard server already running on loopback: open `/spectate`.

## Honesty (v0.1)

- **v0.2 emit hooks.** `hooks/spectate-emit.sh` appends scrubbed `rc.spectate.v1` lines on SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop / SubagentStart / PreCompact. Observe-only (always exit 0). Deny join uses `corr_id` from `tool_use_id` on both spectate-events and hook-events.
- **Observe-only.** The UI never POSTs; the server never accepts Spectate writes except CLI demo.
- **Capability cells stay `unknown` until measured.** Empty / missing streams reduce to `idle` with cause-not-established — never to `unavailable-harness`.
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
