# RavenClaude Core

A Team Lead plus {{N_AGENTS}} specialist agents, {{N_SKILLS}} skills, {{N_COMMANDS}} slash commands and {{N_HOOKS}} hooks for Claude Code. This is the **directory edition**: a smaller, reviewable build of [`ravenclaude-core`](https://github.com/mcorbett51090/RavenClaude). Version {{VERSION}}, {{N_FILES}} files.

> **Every hook except one setup line is switched off until you create `.ravenclaude/comfort-posture.yaml` in your project.** Delete that file and they are off again. Nothing here contacts a server run by the author, and nothing here makes a model call outside your own Claude Code session.

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

**How the switch works.** Every hook above except `dashboard-prompt.sh` is registered as `bash "${CLAUDE_PLUGIN_ROOT}/hooks/posture-gate.sh" <the hook>`. `hooks/posture-gate.sh` is three lines of code: if `.ravenclaude/comfort-posture.yaml` is missing it exits 0 immediately, so the wrapped hook never starts and produces no output, no files and no network traffic. Read it before you rely on this.

**What the hooks cannot do.** No hook in this edition starts a program outside a short list ({{EXEC_LIST}}), contacts a network, rewrites a tool call or its output, pre-approves a permission, or edits `.claude/settings.json`. These are checked, not just claimed: a test harness runs every shipped hook under a minimal environment, once with no posture file and once with a hostile one (a posture file that tries to make hooks run a command, call `claude`, open a socket or approve a call), and fails the build if any hook does any of those things. The only files hooks write are under `.ravenclaude/` in your project. See [PRIVACY.md](PRIVACY.md).

## Turn the guardrails on

With no posture file you will see one line at session start. To opt in:

1. Run `/dashboard`. It prints the link to the hosted posture editor ({{PORTAL}}).
2. Choose your settings. Open **Alternative ways to save** at the bottom of the YAML panel and press **Copy** (or **Download**).
3. Paste the block back into Claude and say `save my posture`, or run `/dashboard` with the block pasted after it. Claude writes it to `.ravenclaude/comfort-posture.yaml`.
4. Optionally run `/set-posture` to translate the posture into permission rules in `.claude/settings.json`. That is the only thing here that edits that file, and only when you run it.

You can also write the file by hand. A minimal one that turns on the commit-message and runaway checks:

```yaml
design_checkins: true
git_protocol: warn
runaway:
  max_consecutive: 8
  max_total: 1200
```

## What is not in this edition

The full plugin, installed from the [RavenClaude marketplace](https://github.com/mcorbett51090/RavenClaude), adds things this edition deliberately leaves out because they start background processes, spawn other Claude sessions, rewrite tool input or output, or are specific to other tools: the command-review tribunal, the local dashboard server, the `bin/` launchers, always-on guards, the prompt optimizer, session handoff and the Copilot/Codex/Gemini bridges. Some skills and agents mention those features; in this edition the mention is just text. If you install both, the marketplace copy takes precedence over the directory copy.

## Install

From the Claude Code directory: `/plugin directory`, then choose **RavenClaude Core**.

From GitHub:

```shell
claude plugin marketplace add mcorbett51090/ravenclaude-core
claude plugin install ravenclaude-core@ravenclaude-core
```

To remove it: `claude plugin uninstall ravenclaude-core`. To switch the hooks off without uninstalling, delete `.ravenclaude/comfort-posture.yaml`.

## Support, source and licence

Report problems at {{SUPPORT}}. This repository is generated from the source plugin by `scripts/build-directory-edition.py` in [mcorbett51090/RavenClaude](https://github.com/mcorbett51090/RavenClaude); the manifest that decides what ships, with a reason for every entry, is `docs/directory-edition/ravenclaude-core/manifest.json` there. Changes belong in the source repository. MIT licence.
