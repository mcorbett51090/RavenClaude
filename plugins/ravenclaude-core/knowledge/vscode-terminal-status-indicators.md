# VS Code terminal status indicators — bell + chime + idle-watcher (the "why")

> Ships as the skill [`skills/terminal-status-indicators/`](../skills/terminal-status-indicators/).
> This doc is the design rationale + bug history: read it before changing `terminal-watcher.py`.
> Mechanics verified locally on Linux 6.8 (Codespace), 2026-07-09; VS Code settings verified against
> code.visualstudio.com docs the same day.

## Problem

Running multiple background agent sessions across many VS Code terminals, there's no native way to
see which terminal needs your attention without clicking through each one. A terminal **waiting for
input** looks identical to one **actively processing**.

## Solution — three layers

| Layer | Rings when | Where |
|---|---|---|
| VS Code settings | a BEL (`\a`) reaches the tab → 🔔 + chime; ⟳ from shell integration | `.vscode/settings.json` |
| Shell prompt bell | any shell command finishes (agent/script done) | `~/.bashrc` `preexec`/`precmd` |
| Background watcher | an agent **process** goes idle after responding (mid-session, before the prompt) | `terminal-watcher.py` |

### The VS Code settings that matter

- `terminal.integrated.enableBell: true` — shows the 🔔 on a tab that receives a BEL. **Visual only.**
- `accessibility.signals.terminalBell: { "sound": "on" }` — plays the audio cue (VS Code ≥ 1.87).
  **It takes an object `{ "sound": … }`, not a bare string** — a string is the pre-1.87 `audioCues`
  shape and silently won't apply.
- `audioCues.terminalBell: "on"` — the pre-1.87 name, auto-migrated and deprecated; harmless to keep
  for back-compat on old VS Code.
- `terminal.integrated.shellIntegration.enabled: true` — the ⟳ running indicator + command decorations.

### The `~/.bashrc` gotcha (the original dead layer)

The first implementation guarded the prompt hook with `if [[ "$TERM" == "xterm" ]]` — a **literal**
match. GitHub Codespaces sets `TERM=xterm-256color`, so the block **never ran**. Always glob:
`[[ "$TERM" == xterm* ]]`. The shipped block additionally requires an **interactive** shell
(`[[ $- == *i* ]]`) so a non-interactive shell that sources `~/.bashrc` (via `BASH_ENV` or a script)
never installs the `DEBUG` trap or rings a spurious bell.

### How the watcher's bell reaches VS Code

Writing `\a` to the PTY **slave** (`/dev/pts/N`) is what VS Code (the PTY master) sees:

```
agent writes to /dev/pts/N  →  VS Code reads it  →  🔔 on tab + chime
```

The watcher resolves a process's PTY from `/proc/<pid>/fd/{0,1,2}` (they symlink to `/dev/pts/N` for
an interactive process) and detects "actively responding then quiet" by polling the `wchar:` field of
`/proc/<pid>/io` (cumulative bytes written). Both were verified locally: a 1000-byte write moved
`wchar` 504 → 1504, and `/proc/<tty-pid>/fd/1` resolved to `/dev/pts/0`.

## Bugs found & fixed (review loop, 2026-07-09)

All are real failure modes, each confirmed with proof-of-failure before fixing.

### B1 (P0) — `was_active` never set for streaming responses
A `MIN_ACTIVE_BYTES = 500` threshold checked against a **single** 0.5s tick's delta. Streaming
responses arrive as many small chunks (20–100 bytes/tick); no single tick cleared 500, so
`was_active` was never set and **the bell never rang at all.**

```python
MIN_ACTIVE_BYTES = 500
deltas = [30] * 20            # streaming: 30 B/tick × 20 = 600 total
any(d >= MIN_ACTIVE_BYTES for d in deltas)   # → False  ← core feature dead
```

**Fix:** accumulate the delta across ticks (`active_bytes_total += delta`), compare the *running total*
to the threshold, and reset to 0 only after a bell fires. Verified: 20×30 B → `was_active=True`.

### B2 (P0) — double bell from one terminal
The shell wrapper **and** the real binary share one `/dev/pts/N`; tracking both rings the bell twice.
**Confirmed live:** every `claude` session showed `bash`+`claude` on the same PTS (`/dev/pts/1`,
`/dev/pts/2`). **Fix (two lines of defense):** dedup by PTY at intake, **and** — the decisive one —
make the ring decision **once per PTY in the main loop**, so even the intake race (two PIDs added
before either's PTY resolved) can't double-ring. All states on a rung PTY are reset together.

### B3 (P1) — `$!` literal in a single-quoted alias
`alias watch-terminals='… & echo "started (pid=$!)"'` — in bash, `$!` inside **single** quotes is not
expanded; it prints the literal `$!`. **Fix:** make it a shell **function** — expansion works normally
in a function body.

### B4 (P1) — no guard against double-starting the watcher
Running `watch-terminals` twice started two watchers; both ring every bell. **Fix:** an `is_running()`
check (pidfile + `os.kill(pid, 0)` existence probe) in the script, plus a shell-side guard
(`terminal-watcher.py --is-running`) before spawning. Stale pidfiles are auto-cleaned.

### B5 (P2) — PTY not re-detected after `None` at init
`get_pty()` ran once in `__init__`; if the PTY wasn't available yet (race, or the process hadn't
opened its terminal), it stayed `None` forever and that process could never ring. **Fix:** re-resolve
`get_pty()` every tick until it's non-`None`.

### Baseline (avoided) — no spurious startup bell
The **first** observation of a PID only establishes the `wchar` baseline (no delta), so a process's
historical byte count isn't counted as one giant burst that would instantly ring on startup.

## Propagation

- The `.vscode/settings.json` block is safe in any workspace.
- The `~/.bashrc` block belongs in the Codespace user profile — install via `postCreateCommand`
  calling `setup-terminal-indicators.sh` (idempotent).
- `terminal-watcher.py` is copied to `~/.local/share/ravenclaude/` (version-agnostic path).
- Customize the watched processes per project via `TERMINAL_WATCHER_COMMANDS` — the watcher is generic.
