# Harness Spectate (v0.1)

Observe-only livestream of atlas harness agent loops: see / understand / direct (direct is out of scope for v0.1).

## Open it

```bash
bash plugins/ravenclaude-core/bin/rc spectate
bash plugins/ravenclaude-core/bin/rc spectate --demo
```

Or, with a dashboard server already running on loopback: open `/spectate`.

## Honesty (v0.1)

- **No emit hooks yet.** Streams come from demo writers or future `spectate-emit.sh` (v0.2).
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
