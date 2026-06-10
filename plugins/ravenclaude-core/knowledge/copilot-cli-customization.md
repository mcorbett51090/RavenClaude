# GitHub Copilot CLI — the customization surface

**Last reviewed:** 2026-06-09 · **Confidence:** high (verified against the GitHub Copilot CLI customization docs — custom instructions, custom agents, agent skills, hooks, and the using-the-CLI reference; URLs in § Sources, retrieved 2026-06-09). GA Feb 2026 ([changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)).
**Owner:** the Copilot CLI bridge in [`../CLAUDE.md`](../CLAUDE.md) § "GitHub Copilot CLI bridge". This file is the **canonical, complete** reference; the bridge prose is the RavenClaude-specific wiring on top of it.

This is what GitHub Copilot CLI reads for customization, and how RavenClaude maps onto each surface. Every path/field below is from the live docs; the few RavenClaude-specific mechanics the docs don't cover are marked `[verify-at-use]`.

## 1. Custom instructions (auto-included every request)

Copilot CLI **automatically adds** these to every request at session start — *"Instructions are automatically added to requests that you submit to Copilot."* You don't invoke them; they're always-on context.

| File | Scope |
|---|---|
| `.github/copilot-instructions.md` | repository-wide |
| `.github/instructions/*.instructions.md` | path-scoped (each has an `applyTo:` glob); at repo root or under the cwd |
| `AGENTS.md` | repo root, the cwd, or any dir in `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` |
| `$HOME/.copilot/copilot-instructions.md` | personal (all repos) |
| `CLAUDE.md` / `GEMINI.md` | repo root — read as alternatives |

**Nuance `[verify-at-use]`:** the docs say the *instruction files* are auto-included; they do **not** state that a *path reference inside* one (e.g. "read `.ravenclaude/environment-context.md`") auto-loads that referenced file's content. Treat a reference as a pointer the agent reads on demand — put must-have content directly in an auto-loaded file. Convention: keep `copilot-instructions.md` short and point it at `AGENTS.md`.

## 2. Custom agents

| Location | Scope |
|---|---|
| `.github/agents/*.agent.md` | project (repository) |
| `~/.copilot/agents/*.agent.md` | personal |

- **Precedence:** a same-named agent in `~/.copilot/agents/` (home) **overrides** the repo one.
- **Format:** `<name>.agent.md` (Markdown + frontmatter). `name`; optional `tools` (by default an agent has **all** tools — a `tools` spec only *restricts*).
- **Invocation:** `/agent` (interactive picker) · explicit ("use the security-expert agent") · inference from the agent's `description` · programmatic `copilot --agent <name> --prompt "…"`.
- Agents run as temporary subagents with their **own isolated context window**.

## 3. Agent skills

| Location | Scope |
|---|---|
| `.github/skills/`, `.claude/skills/`, `.agents/skills/` | project |
| `~/.copilot/skills/`, `~/.agents/skills/` | personal |

- Each skill is its own subdirectory (lowercase, hyphenated) with a `SKILL.md`.
- **`SKILL.md` frontmatter:** `name` (required, lowercase-hyphenated) · `description` (required — what it does + *when* Copilot should use it) · optional `license` · optional **`allowed-tools`** (pre-approves tools, e.g. `shell`, without per-use confirmation).
- **Discovery/invocation:** auto-discovered; Copilot decides from the prompt + `description`, or the user forces it with `/skill-name`. When invoked, **all** files in the skill dir become available to the agent.
- **Instructions vs. skills (the docs' own guidance):** custom instructions for simple guidance relevant to *almost every* task; skills for detailed guidance Copilot should load *only when relevant*.

## 4. Hooks

External commands fired at lifecycle points (custom automation, security/policy gates).

| Location | Scope |
|---|---|
| `.github/hooks/NAME.json` | repository |
| `~/.copilot/hooks/` (or `$COPILOT_HOME/hooks/`) | personal |

- **Events:** `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `errorOccurred` (`agentStop` also appears in examples).
- **`preToolUse` is the powerful one** — it can **approve or deny** a tool call, and it **fails closed** (an error/crash/timeout *denies* the tool rather than silently allowing it). `sessionStart` output is informational (ignored by the agent).
- **Config (JSON, version 1):**
  ```json
  {
    "version": 1,
    "hooks": {
      "preToolUse": [
        { "type": "command", "bash": "…", "powershell": "…", "cwd": ".", "timeoutSec": 10, "env": {} }
      ]
    }
  }
  ```
- **⚠️ Plugin-level hooks do NOT fire** — `preToolUse` hooks defined in a *plugin's* `hooks.json` never execute (main session or subagents): [github/copilot-cli#2540](https://github.com/github/copilot-cli/issues/2540). **Ship enforcement hooks repo-level (`.github/hooks/`)**, not plugin-level, until #2540 closes.

## 5. Runtime & config

- **`settings.json`** and **`mcp-config.json`** live in **`~/.copilot/`** by default; **`COPILOT_HOME`** overrides that directory (so all of settings / MCP / hooks move with it).
- **`COPILOT_CUSTOM_INSTRUCTIONS_DIRS`** — comma-separated dirs Copilot also scans for `AGENTS.md`.
- **Permissions:** Copilot asks before a tool that modifies/executes (e.g. `touch`, `chmod`, `node`, `sed`); approve per-op / per-session / deny. `--allow-all` and `--yolo` enable everything (use with care).

## 6. How RavenClaude maps onto each surface

| Copilot CLI surface | RavenClaude wiring |
|---|---|
| **Custom instructions** | Root `AGENTS.md` carries the cross-tool discipline; `scripts/generate-copilot-plugin.py` projects it into `copilot/AGENTS.md` so it travels with the agents (wired via `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`). Consumers keep a short `.github/copilot-instructions.md` pointing at `AGENTS.md`. |
| **Custom agents** | `copilot/agents/*.agent.md` (frontmatter = `name` + `description`, body verbatim), loaded **live** via `copilot --plugin-dir copilot/` `[verify-at-use — --plugin-dir is owner-verified; not in the customization docs reviewed 2026-06-09]`. The native `.github/agents/` + `~/.copilot/agents/` dirs are an alternative path RavenClaude does not currently use. |
| **Agent skills** | `scripts/ravenclaude install` wires skills → the consumer's `.claude/skills/` (a docs-confirmed project-skills dir), read live. RavenClaude `SKILL.md` files use `name` + `description`; Copilot's `allowed-tools` is available as a future friction-reducer (not yet adopted). |
| **Hooks** | Wired **repo-level** to `.github/hooks/ravenclaude.json` via [`hooks/copilot-hook-adapter.sh`](../hooks/copilot-hook-adapter.sh), which translates Copilot's I/O envelopes (`toolName`/`toolArgs` ⇄ `tool_name`/`tool_input`; top-level `permissionDecision`; `sessionStart` `additionalContext`) so the **existing, unmodified** Claude hook scripts run. Repo-level because of #2540. |
| **MCP** | Bundled MCP → `${COPILOT_HOME:-~/.copilot}/mcp-config.json` by `scripts/ravenclaude`. |
| **Update model** | Everything is read **live from disk**, so an update is `git pull` (`ravenclaude update` / the `rc` alias) — no Copilot re-install/cache. |

## Sources

All retrieved 2026-06-09:
- [Adding custom instructions for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
- [Creating and using custom agents for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
- [Adding agent skills for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Using hooks with Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks) · [Hooks configuration reference](https://docs.github.com/en/copilot/reference/hooks-configuration)
- [Using GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli) · [#2540 — plugin hooks don't fire](https://github.com/github/copilot-cli/issues/2540)
