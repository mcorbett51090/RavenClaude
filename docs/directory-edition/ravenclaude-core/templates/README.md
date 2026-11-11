# RavenClaude Core

A Team Lead plus {{N_AGENTS}} specialist agents, {{N_SKILLS}} skills, {{N_COMMANDS}} slash commands and {{N_HOOKS}} hooks for Claude Code. This is the **directory edition**: a smaller, reviewable build of [`ravenclaude-core`](https://github.com/mcorbett51090/RavenClaude). Version {{VERSION}}, {{N_FILES}} files.

> **Every hook except one setup line is switched off until you have done two things for a project: it has a `.ravenclaude/comfort-posture.yaml`, and you have trusted the project.** A repository you clone can ship its own posture file, so the file alone switches nothing on. Remove either one, or change the posture, `.repo-layout.json` or `.ravenclaude/task-scope.json` after you trusted the project, and the hooks are off again until you trust it again. Nothing here contacts a server run by the author, and nothing here makes a model call outside your own Claude Code session.

## What you get

**Specialist agents** (dispatched by the Team Lead via the `spawn-team` skill):

{{AGENT_LIST}}

**Slash commands:**

{{COMMAND_LIST}}

**Skills** (Claude loads these when a task matches):

{{SKILL_LIST}}

## What the hooks do

Hooks run on Claude Code events. They are the part of a plugin that acts without being asked, so each one is listed here, with the events it fires on.

{{HOOK_TABLE}}

**How the switch works.** Every hook above except `dashboard-prompt.sh` is registered as `bash "${CLAUDE_PLUGIN_ROOT}/hooks/posture-gate.sh" <the hook>`. `hooks/posture-gate.sh` is the whole on/off script, and the wrapped hook starts only when all of these hold: the project has `.ravenclaude/comfort-posture.yaml` as a regular file; nothing under `.ravenclaude/` is a symbolic link at any depth, or a directory the check cannot read (the runaway counter is `.ravenclaude/runs/thing/runaway/<session_id>`, four levels under `.ravenclaude/`, which `find` counts as depth 0, so a three-level bound would miss the file the hook opens); the project's real path contains no newline or tab; and `~/.ravenclaude/edition-trusted-projects` holds a line `<real path><TAB><sha256>` whose digest still matches the posture, `.repo-layout.json` and `.ravenclaude/task-scope.json` (the three project files the hooks read, each at most 1 MiB; a missing one counts as missing). Otherwise it exits 0 at once: no output, no files, no network, and the hook never starts. `scripts/edition-trust.sh` (run by `/dashboard` after you agree) writes that line, and gets the digest from the gate itself. Read both files before you rely on this.

**What the hooks cannot do.** No hook in this edition starts a program outside a short allow-list ({{EXEC_LIST}}), contacts a network, rewrites a tool call or its output, pre-approves a permission, or edits `.claude/settings.json`. These are checked, not just claimed: a test harness runs every shipped hook under a minimal environment in three situations (no posture file; a posture file in a project you have not trusted; a hostile posture file in a trusted project) and fails the build if any hook does any of those things. Every test project also contains decoy Python modules (`json.py`, `shlex.py`, `re.py` and others) that write a marker if a hook imports them from the project directory; the hooks run Python in isolated mode (`python3 -I`), so they are never imported. The only files hooks write are under `.ravenclaude/` in your project, plus a short-lived temporary file that is removed when the hook exits. See [PRIVACY.md](PRIVACY.md).

**What they can do once you have opted in.** They print short advisory messages. Some of that text reaches the model as well as you, and a few messages quote a line from a file you or Claude just wrote, so a project you trust can influence what Claude is told. A hook can also deny a tool call (for example the runaway brake after too many identical calls); a posture file in a project you trust can set those limits, so read the posture, `.repo-layout.json` and `.ravenclaude/task-scope.json` before you trust a project. The trust is tied to their exact content and lapses when they change. No hook in this edition runs `git`: the one that did (the test reminder) is not shipped, because git runs the programs a repository's own `.git/config` names and no flag turns the filter drivers off. `enforce-git-protocol.sh` only reads the command Claude is about to run.

## Turn the guardrails on

With no posture file you will see one line at session start. To opt in:

1. Run `/dashboard`. It prints the link to the hosted posture editor ({{PORTAL}}).
2. Choose your settings. Open **Alternative ways to save** at the bottom of the YAML panel and press **Copy** (or **Download**).
3. Paste the block back into Claude and say `save my posture`, or run `/dashboard` with the block pasted after it. Claude writes it to `.ravenclaude/comfort-posture.yaml` after you approve the write.
4. Say yes when Claude offers to trust the project. It then runs `scripts/edition-trust.sh add`, after you approve, which adds this project's real path to `~/.ravenclaude/edition-trusted-projects`. You can also add that line yourself (`pwd -P` prints the path).

You can also write the posture by hand. A minimal one that turns on the commit-message and runaway checks:

```yaml
design_checkins: true
git_protocol: warn
runaway:
  max_consecutive: 8
  max_total: 1200
```

If you cloned a project that already has a posture file, read it (and `.repo-layout.json` / `.ravenclaude/task-scope.json` if present), then decide: the setup line at session start tells you the project is not trusted, and nothing runs until you trust it. After a `git pull` that changes any of those files it says the project changed since you trusted it, and the hooks stay off until you review the change and trust it again.

## What is not in this edition

The full plugin, installed from the [RavenClaude marketplace](https://github.com/mcorbett51090/RavenClaude), adds things this edition deliberately leaves out because they start background processes, spawn other Claude sessions, rewrite tool input or output, change your permission settings, or are specific to other tools: the command-review tribunal, the local dashboard server, the `bin/` launchers, always-on guards, `/forge`, `/set-posture`, the prompt optimizer, session handoff and the Copilot/Codex/Gemini bridges. Some skills and agents mention those features; in this edition the mention is just text. If you install both, the marketplace copy takes precedence over the directory copy.

Two limits worth knowing. Skills such as `spawn-team` read a few behavioural settings (`parallelism`, `orchestrator`) from the posture file whether or not the project is trusted; those only change how Claude plans its work, and they are the reason to read a posture file you did not write. And `.ravenclaude/runs/` holds small per-session files; add it to your `.gitignore` so it is not committed by accident.

The agents' `memory:` setting is removed in this edition: with it, a repository could ship `.claude/agent-memory/<agent>/MEMORY.md` and have it loaded into an agent's prompt. `architect` and `prompt-engineer` therefore keep no memory here.

Shipped commands and skills do not pre-approve any tool (the `allowed-tools` field is removed in this edition), so each `Bash`, `Write` or `Edit` call goes through your own Claude Code permission settings.

## Install

From the Claude Code directory: `/plugin directory`, then choose **RavenClaude Core**.

From GitHub:

```shell
claude plugin marketplace add mcorbett51090/ravenclaude-core
claude plugin install ravenclaude-core@ravenclaude-core
```

To remove it: `claude plugin uninstall ravenclaude-core`. To switch the hooks off without uninstalling, delete `.ravenclaude/comfort-posture.yaml`, or stop trusting the project: run `/dashboard` and ask Claude to stop trusting it, or delete the project's line from `~/.ravenclaude/edition-trusted-projects`.

## Support, source and licence

Report problems at {{SUPPORT}}. This repository is generated from the source plugin by `scripts/build-directory-edition.py` in [mcorbett51090/RavenClaude](https://github.com/mcorbett51090/RavenClaude); the manifest that decides what ships, with a reason for every entry, is `docs/directory-edition/ravenclaude-core/manifest.json` there. Changes belong in the source repository. MIT licence.
