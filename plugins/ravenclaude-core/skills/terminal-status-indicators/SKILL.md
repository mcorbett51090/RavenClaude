---
name: terminal-status-indicators
description: "Make VS Code terminal tabs show 🔔 + chime the moment an agent session needs you, across many parallel Copilot/Claude terminals. Installs three layers: workspace settings (tab bell icon + audio cue), a shell prompt hook (bell on command completion), and a background /proc-io watcher that rings a terminal's PTY bell when its agent process goes idle after responding. Use in a Codespace / VS Code setup where you run multiple background agent sessions and can't tell which one is waiting for input without clicking through each tab."
---

# Terminal status indicators — bell + chime + idle-watcher

When you run several background agent sessions across many VS Code terminals, a terminal **waiting
for your input** looks identical to one **actively working**. This skill makes the waiting ones
announce themselves: the tab shows a 🔔 and plays a chime the moment the agent goes quiet.

## The three layers

| Layer | What it does | Mechanism |
|---|---|---|
| **VS Code settings** | 🔔 icon on the tab + audio chime when a BEL is received; ⟳ running indicator via shell integration | `.vscode/settings.json` keys ([`settings-snippet.json`](settings-snippet.json)) |
| **Shell prompt bell** | Rings the bell when *any* shell command finishes (agent done, script complete) | `preexec`/`precmd` in `~/.bashrc` (interactive shells only) |
| **Background watcher** | Rings a terminal's bell when its **agent process** goes idle after responding — even mid-session, before the shell prompt returns | [`terminal-watcher.py`](terminal-watcher.py) reads `/proc/<pid>/io` `wchar` and writes `\a` to the PTY |

Net effect: actively-working terminals show ⟳; terminals that need you show 🔔 + chime — visible in the
tab strip without expanding each terminal.

## Install

One command wires all three layers (idempotent — safe on every Codespace rebuild):

```bash
bash setup-terminal-indicators.sh [--project DIR] [--commands "copilot,claude"]
```

- `--project DIR` — the repo whose `.vscode/settings.json` to configure (default: `$PWD`). The merge is
  **non-destructive**: it only adds keys you don't already have.
- `--commands LIST` — comma-separated process names the watcher rings for (default `copilot,claude`;
  it's generic — any agent CLI works).

The installer copies the watcher to `~/.local/share/ravenclaude/terminal-watcher.py` (a stable path,
independent of the plugin-cache version dir) and adds a marker-bounded block to `~/.bashrc`.

### Codespace auto-setup

Call the installer from your devcontainer's `postCreateCommand` so a new Codespace self-configures —
see [`../../../../.devcontainer/post-create.sh`](../../../../.devcontainer/post-create.sh) (this repo
dogfoods it) and the consumer template
[`../../templates/codespace-copilot/ravenclaude-post-create.sh`](../../templates/codespace-copilot/ravenclaude-post-create.sh).

## Use (after `source ~/.bashrc` or a new terminal)

```bash
watch-terminals    # start the idle-watcher in the background (guarded: won't double-start)
watcher-log        # follow its log (/tmp/terminal-watcher.log)
stop-watching      # stop it
```

## How the bell reaches VS Code

```
agent process writes \a to its PTY slave (/dev/pts/N)
        ↓
VS Code (the PTY master) reads it
        ↓
VS Code shows 🔔 on the tab + plays the audio cue
```

The watcher writes a single `\a` byte to the PTY slave (`O_WRONLY | O_NOCTTY`). It must run as the
same OS user as the terminal owner (in a Codespace, `codespace` → `codespace`, so this holds).

## Design & bug history

The watcher's non-obvious correctness decisions — accumulate-across-ticks (streaming responses never
clear a per-tick byte threshold), ring-once-per-PTY (a shell wrapper + the real binary share one PTS),
retry-PTY-resolution, single-instance pidfile guard, no-startup-bell baseline — are documented with
proof-of-failure in
[`../../knowledge/vscode-terminal-status-indicators.md`](../../knowledge/vscode-terminal-status-indicators.md).
Read that before changing `terminal-watcher.py`.

## Known limitations

- **`wchar` counts all writes, not just terminal output.** A process that writes heavily to log files
  between responses may not settle. CLI agents are quiet between responses in practice; if you see
  false idles, raise `TERMINAL_WATCHER_IDLE` or `TERMINAL_WATCHER_MIN_BYTES`.
- **The idle heuristic can't perfectly tell "response done" from "mid-response pause."** A single
  response with an internal pause longer than `TERMINAL_WATCHER_IDLE` (a tool call, a network wait)
  can ring twice; conversely the tool errs toward *ringing* (a missed bell defeats the purpose more
  than a rare extra one). `TERMINAL_WATCHER_RESET` (default 30s) is the window after which a
  *sub-threshold* burst is forgotten — long enough that a real chunked response still accumulates,
  short enough that genuinely-stale partial activity doesn't linger. Tune all three to your agents'
  cadence.
- **Non-interactively-launched agents may have no PTY** (`pty=None`) and can't be rung; the watcher
  keeps retrying resolution but can't invent a terminal.
- **The prompt bell fires on every prompt return** (including fresh terminal opens) — slightly noisy
  but it correctly signals "process done, your turn."
- **The `DEBUG` trap is global** — it overwrites any existing `DEBUG` trap (e.g. another prompt
  framework). If you use starship/oh-my-bash, install this after them or merge by hand.
- **Terminals collapsed into one panel icon** don't show per-tab indicators. Move agent terminals to
  the editor area (right-click tab → *Move Terminal into Editor Area*) for persistent visibility.

## Tuning (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `TERMINAL_WATCHER_COMMANDS` | `copilot,claude` | process names (matched on `/proc/<pid>/comm`) to watch |
| `TERMINAL_WATCHER_POLL` | `0.5` | seconds between polls |
| `TERMINAL_WATCHER_IDLE` | `3.0` | seconds of quiet after activity before ringing |
| `TERMINAL_WATCHER_MIN_BYTES` | `500` | cumulative bytes that count as "a real response" |
| `TERMINAL_WATCHER_RESET` | `30.0` | seconds of quiet before a *sub-threshold* burst is forgotten (kept well above `IDLE` so a real response with a mid-stream pause still accumulates) |
| `TERMINAL_WATCHER_PIDFILE` | `/tmp/terminal-watcher.pid` | single-instance lock path |
