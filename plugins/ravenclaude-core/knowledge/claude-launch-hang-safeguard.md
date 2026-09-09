# Claude launch-hang safeguard (anthropics/claude-code#92932)

## The bug

Starting a new Claude Code session with `cwd` outside any git repository (most commonly bare
`$HOME`) can hang the session indefinitely, with zero CPU usage and no error surfaced. Root cause,
confirmed via `--debug` log analysis: Claude Code runs an unscoped `rg` (ripgrep) file-index scan
across the whole home directory when it has no git repo to establish a project boundary. That scan
walks into dozens of macOS TCC-protected paths (`.Trash`, `Library/Mail`,
`Pictures/Photos Library.photoslibrary`, `Library/Messages`, etc.), each erroring
`Operation not permitted (os error 1)` — and whatever consumes that error shape afterward hangs
rather than continuing or surfacing an error.

`--safe-mode` and `--bare` sessions are unaffected. Filed upstream:
[anthropics/claude-code#92932](https://github.com/anthropics/claude-code/issues/92932) — measured
against Claude Code **2.1.263**, **2026-09-08**.

⛔ **This is Claude Code's own binary. It cannot be patched by RavenClaude.** Everything below is a
local, defense-in-depth safeguard against reaching the condition, or detecting it fast when the
safeguard is bypassed — not a fix for the underlying bug.

## Two layers

### Layer 1 — prevention (`plugins/ravenclaude-core/bin/claude-launch-guard` + the installer)

A shell **function** (never `alias` — an alias can't branch on argv and doesn't reach
non-interactive shells) named `claude`, installed into the user's `.zshrc`/`.bashrc`/fish config by
`plugins/ravenclaude-core/scripts/install_launch_guard.py`. Before letting `claude` launch, it runs
`claude-launch-guard check -- "$@"`, which checks (bounded, ~2s timeout) whether `cwd` is inside a
git work tree.

- **Exempt flags** (from the confirmed root cause): `--safe-mode`, `--bare`, `--help`/`-h`,
  `--version`/`-v`, `-p`, `--print`, `--resume`, `-c`/`--continue`, `mcp`, `plugin`, `config`,
  `install`, `doctor`.
- **Default posture: warn, never a silent hard block.** Most `$HOME` launches are benign — this
  guard's own build found two other live sessions with cwd=`$HOME` that started and ran fine. A
  hard block on a legitimate ad-hoc question is exactly the kind of guard this repo has already
  recorded getting switched off (`srm.force-push`, `sce.curl-pipe-shell`).
- **Four-option prompt** on the "not safe" path (Just once / This session / Always allow / Deny),
  matching this repo's existing `guard-web-access.sh` pattern. A non-interactive/no-TTY hit
  defaults to allow-with-a-printed-warning, never a blocking prompt with nothing to answer it.
- **FAIL-OPEN, always.** Missing helper, unreadable config, `git` absent, the timeout firing, the
  kill switch — every path ends in `command claude "$@"`. A safeguard that can make `claude`
  unlaunchable is worse than the hang it prevents.

**Known limit: interactive shells only.** A `claude` launched from a VS Code task, a launchd job, a
script, or any non-interactive shell does not see the function. A PATH-shim executable was
considered and deliberately **not** shipped in v1 — this machine's own `PATH` had `~/.grok/bin` and
two VS Code helper directories already ahead of `~/.local/bin`, and a stale shim surviving an
uninstall would silently hijack every future `claude` invocation forever, a worse standing failure
than the coverage gap it closes. Layer 2 is the compensating control for this gap.

### Layer 2 — detection (`evaluate_launch_hangs()` in `stall_watch.py`)

An **additive** function inside the existing out-of-session stall watchdog
(`plugins/ravenclaude-core/scripts/stall_watch.py`, live since v0.300.0) — `evaluate()` itself, the
general stall-scoring path, is untouched.

`evaluate()` structurally cannot see this failure: it skips any session with `status == "idle"`
before it would ever check for a missing transcript, and its resolution set would auto-close any
episode that got through anyway. `evaluate_launch_hangs()` uses a separate episode namespace
(`state["launch_episodes"]`) and its own resolution rule.

**Discriminator (all six conjuncts must hold, cheapest first — the git check runs last since it's
the only one that shells out):**

1. `alive` (pid check).
2. `status == "idle"` (registry).
3. `statusUpdatedAt <= startedAt + epsilon` — never once updated since launch. The sharpest signal;
   a healthy idle session bumps on a ~17-minute cadence.
4. No transcript exists for the session.
5. `now - startedAt > LAUNCH_HANG_MIN` (3.0 minutes) — bounds a normal cold start.
6. `cwd` is not inside a git work tree (bounded probe; any failure — git absent, timeout, an
   unexpected error — is treated as **not hung**, never as a false alarm).

**Optional enrichment (P4, never a conjunct):** if a `~/.claude/debug/<sessionId>.txt` happens to
exist (only true when the session was launched with `--debug`, which is not the default), it's
checked for the `rg ... Operation not permitted` signature and, if found, the finding gains
`signature: "rg-tcc"` plus a match count — never a raw matched line or path.

## Kill switches (three, deliberately layered)

1. `RAVENCLAUDE_LAUNCH_GUARD=off` — read as the helper's very first statement. Works even in an
   already-broken shell.
2. `command claude …` — the shell's own escape, printed in every warn message.
3. `bash plugins/ravenclaude-core/scripts/install_launch_guard.py --uninstall` (or
   `scripts/ravenclaude launch-guard uninstall`) — removes the installed fence and restores the rc
   file's pre-install backup.

## Empirical basis and its expiry

The five/six-conjunct discriminator is derived from **one observed instance** of the real hang
(pid captured live during this build, cwd=`$HOME`, ~12 minutes elapsed, `statusUpdatedAt ==
startedAt`, no transcript). If a future Claude Code release changes what it writes to the session
registry at launch, or starts writing a transcript before the hang, conjunct 3 or 4 can silently
stop matching — the detector would go quiet without erroring. Re-verify against the version this
was measured on (Claude Code **2.1.263**, 2026-09-08) before trusting it on a materially different
release.

**Nothing here fixes #92932.** If upstream fixes it, Layer 1 becomes a small per-launch tax and
Layer 2 becomes dead code. Both should be reviewed when the issue closes.

## Install

```shell
python3 plugins/ravenclaude-core/scripts/install_launch_guard.py install
# or, from the CLI wrapper:
bash scripts/ravenclaude launch-guard install
```

`--check` reports without writing; `--uninstall` reverses it; `--shell zsh|bash|fish` overrides
detection.
