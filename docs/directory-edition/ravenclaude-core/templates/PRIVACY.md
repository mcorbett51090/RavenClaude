# Privacy and data handling

RavenClaude Core {{VERSION}}, directory edition. This page says what the plugin does with your data, and how each statement is checked. A claim that is only read from the code, and not measured, is marked as such.

## Summary

- **It collects nothing.** No telemetry, analytics, crash reports or accounts. The author runs no server that this plugin talks to.
- **Its hooks are off until you opt in.** Every hook except one setup line is invoked through `hooks/posture-gate.sh`, which exits immediately unless the project has a `.ravenclaude/comfort-posture.yaml` **and** `~/.ravenclaude/edition-trusted-projects` lists the project's real path with a SHA-256 fingerprint of the three files the hooks read from it (the posture, `.repo-layout.json`, `.ravenclaude/task-scope.json`). A repository you clone can ship those files; it cannot write the trust file, and changing any of them switches the hooks off again until you trust the project again. Skills and agents are different: they act on what you ask, and the files of a repository you point them at (for example for `/repo-review`) are untrusted input to them.
- **With the hooks on, they write only under `.ravenclaude/` in your project** (plus a temporary file they remove when they exit), start only a short allow-list of programs, and never contact a network.
- **The posture file is treated as untrusted input.** Hooks read settings from it; they never run a value from it, never rewrite a tool call or its output, never pre-approve a permission, and run their Python in isolated mode so that a file in your project cannot replace a standard-library module.
- **No command or skill pre-approves a tool.** The `allowed-tools` field is removed from every shipped command and skill, so each `Bash`, `Write` or `Edit` call goes through your own permission settings.

## How the hook claims are checked (measured)

`scripts/directory-edition-hook-audit.py` in the [source repository](https://github.com/mcorbett51090/RavenClaude) runs every shipped hook, built from the exact `hooks/hooks.json` in this plugin, in a scratch project with a minimal environment and a payload for every event and tool the hook is registered for, including payloads shaped like the thing each guard looks for (a destructive command, a write to `.env`, a new source file, a shrinking memory file). Every scratch project also holds decoy Python modules named like standard-library modules, a vendored git repository whose `.git/config` runs a command on `git status`, and a `.ravenclaude/` nested inside it with its own posture. It runs each hook three ways and fails the build if any of these happen.

| Lane | What the hook must do |
|---|---|
| **No posture file** | Exit 0, print nothing (stdout is the only channel a hook can use to rewrite a tool call or its output), create or change no file in the project, `HOME`, `TMPDIR` or the plugin directory, make no network call, start no `claude`, import no decoy module. The single exception is the setup prompt, which may print its one fixed line and nothing else. |
| **Posture file, project not trusted** (or trusted, then changed) | Exactly the same as the lane above, even though the posture file asks for every knob to be on and plants commands to run. This is the lane that proves a cloned repository's own posture file cannot switch a hook on. |
| **Hostile posture file, project trusted** | A posture that turns every knob on and tries to make hooks run a shell command, spawn `claude`, open a socket, widen permissions or rewrite output. The hook must not run the command (a canary file proves it), must not start `claude` or touch the network, must not emit `permissionDecision: allow`, `updatedInput` or `updatedToolOutput`, must not edit `.claude/settings.json`, must not write outside `.ravenclaude/`, must not import a decoy module, and must not fail with a missing file inside the plugin. Making a hook stricter (a deny, a block, a warning) is allowed. |

Network use is observed with `strace` on `connect`/`sendto`/`sendmsg` and with tripwires for `curl`, `wget`, `nc`, `ssh`, `gh` and `claude`; programs started are observed with `strace` on `execve`. Every check is itself tested against hooks built to misbehave in each way (including one that imports a decoy module and one that ignores the trust test), so a check that cannot fail would fail the build. The build also refuses any shipped script that runs `python3 -c`, `-m` or `-` (which import from the project directory) without `-I`, any shipped script that starts the `claude` CLI, any hook command that is not a plain `"${CLAUDE_PLUGIN_ROOT}/…"` path, and any shipped file that falls back to a project path when the plugin root is unset.

Programs the hooks are **allowed** to start (the build fails if one starts anything else): {{EXEC_LIST}}.

**Limits.** The payloads are a corpus, not a proof over all inputs. `hooks/posture-gate.sh` is what makes the "off until you opt in" case true by construction; the hostile lane is a measurement of the opted-in case, and a reviewer should read the eight hook scripts rather than trust the harness alone. Python's isolated mode also ignores the `PYTHONPATH`-based socket tripwire the harness uses, so network use by a Python snippet is checked by `strace` (required for the release check) and by a scan of the shipped scripts, not by that tripwire. In a project you trust, a posture file or a file Claude just wrote can still put short quoted text into what the hooks tell Claude. The fingerprint covers only the three files named above: other files in a project (source, documents, anything `/repo-review` reads) are never trusted by it and are read as untrusted input.

## What leaves your machine

| Component | What | Where to | When |
|---|---|---|---|
| Claude Code's own tools | Several agents and skills tell Claude to use `WebSearch` or `WebFetch` (for example `deep-researcher` and `architect`) | whatever you ask Claude to look up | under your Claude Code permission settings; this plugin adds no endpoint of its own |
| `create-pr`, `init-agent-ready` | Tell Claude to use `git`, `gh` or GitHub tools to open a pull request, or scaffold CI files in your repository. `init-agent-ready` can write workflow files and a branch-protection helper that **prints** what it would do by default | your own GitHub account | only when you run them; Claude runs that helper (dry-run) only if it is identical to the plugin's template |
| Hosted posture editor (optional) | A static page on GitHub Pages. It runs in your browser; what you choose in it is not sent anywhere. Opening its **Guardrails → Perimeter alerts** card makes one `GET` to `api.github.com/repos/mcorbett51090/RavenClaude/actions/runs` for a CI status card | GitHub | only if you open the page; GitHub sees ordinary request metadata under its own privacy statement |

The hosted editor's behaviour was observed in headless Chromium on 2026-10-13 across ten of its routes: every request went to its own origin except that one `api.github.com` call, and pressing **Copy** made no request. That is a sample of the page, not an audit of every route.

`/repo-review` and the `repo-review` skill read the files of the repository you point them at and run `git` against it, through Claude's `Bash` tool under your own permissions and in the skill's helper scripts. Git runs the filter and diff programs that repository's own `.git/config` names, and no flag turns those off, so review only a repository you would be willing to run `git status` in; they dispatch Claude subagents inside your own Claude Code session, which is Claude's own mechanism and sends nothing to anyone else. They do not contact a network themselves.

## What is written to your machine

| Where | What | When |
|---|---|---|
| `.ravenclaude/comfort-posture.yaml` | Your posture | when you save it (through Claude's `Write` tool, so your normal permission prompt applies) |
| `~/.ravenclaude/edition-trusted-projects` | One line per project you trust: its real path and a SHA-256 fingerprint of the three files the hooks read | when you say yes to trusting a project; `scripts/edition-trust.sh` writes it after you approve Claude's `Bash` call, and writes nothing else |
| `.ravenclaude/runs/<session>/…` | Small per-session files: a call counter and its lock, a "reminder shown" marker, and event lines in `hook-events.jsonl` when a guard denies or warns about something | only with a posture file present **and** the project trusted |
| `$TMPDIR` | One short-lived file that holds a hook's message while it is built; removed when the hook exits | only while a hook runs |
| `.claude/worktrees/` | Git worktrees | when you use the `new-worktree` skill |
| Files you ask Claude to create | Reports, scaffolds, CI files, documents | only when you ask; each write goes through your own `Write`/`Edit` permissions |

Deleting `.ravenclaude/` removes everything the hooks create in a project. To forget a trusted project, remove its line from `~/.ravenclaude/edition-trusted-projects` or ask Claude (`/dashboard`) to stop trusting it. The agents' `memory:` setting is removed in this edition, so no `.claude/agent-memory/` file is ever loaded into an agent's prompt or written by one. **This edition never edits `.claude/settings.json` or `~/.claude/settings.json`.**

## Things this plugin does not do

It does not start a separate `claude -p` model call (the build scans every shipped script and fails if one starts the `claude` CLI), run a local server, open a browser, change your shell startup files, install anything, read other sessions' transcripts, change your permission rules, or send your files, prompts or environment anywhere.

## Retention and deletion

The author keeps no data. Everything the plugin creates is in your project, or the single trust file in your home directory, as listed above, and is yours to delete. (Skills never write into the installed plugin: the one that used to cache a project's test commands in its own file does not, in this edition.) `claude plugin uninstall ravenclaude-core` removes the plugin.

## Contact

Open an issue at {{SUPPORT}}. Do not include secrets or private code in it.
