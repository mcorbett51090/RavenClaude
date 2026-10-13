# Privacy and data handling

RavenClaude Core {{VERSION}}, directory edition. This page says what the plugin does with your data, and how each statement is checked. A claim that is only read from the code, and not measured, is marked as such.

## Summary

- **It collects nothing.** No telemetry, analytics, crash reports or accounts. The author runs no server that this plugin talks to.
- **Its hooks are off until you opt in.** Every hook except one setup line is invoked through `hooks/posture-gate.sh`, which exits immediately unless `.ravenclaude/comfort-posture.yaml` exists in your project.
- **With the posture file present, hooks write only under `.ravenclaude/` in your project**, start only a short list of programs, and never contact a network.
- **The posture file is treated as untrusted input.** Hooks read settings from it; they never run a value from it, never rewrite a tool call or its output, and never pre-approve a permission.

## How the hook claims are checked (measured)

`scripts/directory-edition-hook-audit.py` in the [source repository](https://github.com/mcorbett51090/RavenClaude) runs every shipped hook, built from the exact `hooks/hooks.json` in this plugin, in a scratch project with a minimal environment and a payload for every event and tool the hook is registered for, including payloads shaped like the thing each guard looks for (a destructive command, a write to `.env`, a new source file, a shrinking memory file). It runs each one twice and fails the build if any of these happen.

| Lane | What the hook must do |
|---|---|
| **No posture file** | Exit 0, print nothing (stdout is the only channel a hook can use to rewrite a tool call or its output), create or change no file in the project, `HOME`, `TMPDIR` or the plugin directory, make no network call, start no `claude`. The single exception is the setup prompt, which may print its one fixed line and nothing else. |
| **Hostile posture file** | A posture that turns every knob on and tries to make hooks run a shell command, spawn `claude`, open a socket, widen permissions or rewrite output. The hook must not run the command (a canary file proves it), must not start `claude` or touch the network, must not emit `permissionDecision: allow`, `updatedInput` or `updatedToolOutput`, must not edit `.claude/settings.json`, must not write outside `.ravenclaude/`, and must not fail with a missing file inside the plugin. Making a hook stricter (a deny, a block, a warning) is allowed. |

Network use is observed with `strace` on `connect`/`sendto`/`sendmsg` and with tripwires for `curl`, `wget`, `nc`, `ssh`, `gh` and `claude`; programs started are observed with `strace` on `execve`. Every check is itself tested against hooks built to misbehave in each way, so a check that cannot fail would fail the build.

Programs the hooks started in that run: {{EXEC_LIST}}.

**Limits.** The payloads are a corpus, not a proof over all inputs. `hooks/posture-gate.sh` is what makes the no-posture case true by construction; the hostile lane is a measurement of the posture-present case, and a reviewer should read the nine hook scripts rather than trust the harness alone.

## What leaves your machine

| Component | What | Where to | When |
|---|---|---|---|
| `/forge` (`scripts/forge-worktree.sh`) | `git fetch --quiet origin`, bounded to 10 seconds, so a new worktree starts from up-to-date `origin/main` | your own git remote | only when you run `/forge` inside a git repository |
| Claude Code's own tools | Several agents and skills tell Claude to use `WebSearch` or `WebFetch` (for example `deep-researcher` and `architect`) | whatever you ask Claude to look up | under your Claude Code permission settings; this plugin adds no endpoint of its own |
| `create-pr`, `init-agent-ready` | Tell Claude to use `git`, `gh` or GitHub tools to open a pull request, or scaffold CI files in your repository. `init-agent-ready` can write workflow files and a branch-protection helper that **prints** what it would do by default | your own GitHub account | only when you run them; nothing written is executed by the plugin |
| Hosted posture editor (optional) | A static page on GitHub Pages. It runs in your browser; what you choose in it is not sent anywhere. Opening its **Guardrails → Perimeter alerts** card makes one `GET` to `api.github.com/repos/mcorbett51090/RavenClaude/actions/runs` for a CI status card | GitHub | only if you open the page; GitHub sees ordinary request metadata under its own privacy statement |

The hosted editor's behaviour was observed in headless Chromium on 2026-10-13 across ten of its routes: every request went to its own origin except that one `api.github.com` call, and pressing **Copy** made no request. That is a sample of the page, not an audit of every route.

## What is written to your machine

| Where | What | When |
|---|---|---|
| `.ravenclaude/comfort-posture.yaml` | Your posture | when you save it (through Claude's `Write` tool, so your normal permission prompt applies) |
| `.ravenclaude/runs/<session>/…` | Small per-session files: a call counter and its lock, a "reminder shown" marker, and event lines in `hook-events.jsonl` when a guard denies something | only with a posture file present |
| `.claude/settings.json` (and `~/.claude/settings.json` if your posture defines a user layer) | Permission rules translated from your posture | only when you run `/set-posture` |
| `.claude/worktrees/` | Git worktrees | when you run `/forge` or the `new-worktree` skill |

Deleting `.ravenclaude/` removes everything the hooks create. `.claude/settings.json` is yours; `/set-posture` replaces its `permissions.allow`, `ask` and `deny` lists with the translation of your posture and prints a per-list summary of what changed.

## Things this plugin does not do

It does not start a separate `claude -p` model call, run a local server, open a browser, change your shell startup files, install anything, read other sessions' transcripts, or send your files, prompts or environment anywhere. (`scripts/apply-comfort-posture.py` contains an optional `claude auth status --json` probe behind a flag, `--nested-dispatch-auth`, that no shipped command, skill or hook passes.)

## Retention and deletion

The author keeps no data. Everything the plugin creates is in your project as listed above and is yours to delete. `claude plugin uninstall ravenclaude-core` removes the plugin.

## Contact

Open an issue at {{SUPPORT}}. Do not include secrets or private code in it.
