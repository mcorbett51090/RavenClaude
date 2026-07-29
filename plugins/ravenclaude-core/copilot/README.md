# ravenclaude-core — GitHub Copilot CLI package

**This directory is auto-generated. Do not edit it by hand.** It is the
GitHub Copilot CLI projection of the canonical `ravenclaude-core` Claude
Code plugin (`plugins/ravenclaude-core/`). The canonical plugin is the
single source of truth; this package is regenerated from it.

## What's here

- `plugin.json` — the Copilot plugin manifest. It declares **only**
  `agents` (mirroring the canonical version, author, license, keywords,
  and description). It deliberately omits `skills`, `hooks`, and
  `mcpServers` (see wiring below).
- `agents/<name>.agent.md` — one per canonical `agents/<name>.md`,
  translated to Copilot's `.agent.md` form: YAML frontmatter carrying
  only `name` + `description`, followed by the full original agent body
  verbatim.

> ### Least-privilege `tools:` IS projected (MH-10, 2026-07-29)
>
> Each canonical agent carries a least-privilege `tools:` allowlist, and
> `AGENTS.md` house rule 9 is explicit that **an omitted `tools:` silently
> grants ALL tools**. This projection used to drop that field, so every
> agent ran fully privileged here — `security-reviewer` is canonically
> `Read, Grep, Glob, Bash, WebFetch` with Write/Edit **deliberately**
> withheld, and under Copilot it could write. That is now fixed: the list
> is translated into Copilot's agent-profile tool names and emitted.
>
> **Source** — the page the Copilot CLI docs designate as authoritative
> for this field, `docs.github.com/en/copilot/reference/custom-agents-
> configuration` [docs-verified 2026-07-29]: the properties apply to
> "agent profiles in GitHub.com, the Copilot CLI, and supported IDEs";
> `tools` is "List of tool names the custom agent can use... If unset,
> defaults to all tools"; and **"All unrecognized tool names are
> ignored"**.
>
> **That last line sets the failure direction, and it is why this ships.**
> A name we get wrong is DROPPED, never widened — the worst case is an
> agent missing a capability (visible: it fails at its job), never one
> that silently gains write or shell (invisible: the hole being closed).
> Because wrong names cost nothing, each Claude tool maps to every
> equal-privilege Copilot spelling rather than one guessed favourite.
>
> **The earlier note that the vocabulary was unpublished was about the
> HOOK `toolName` vocabulary** (whose doc pages did 404), which is a
> *different* list from the agent-profile `tools:` vocabulary. Reusing the
> hook map here — as the audit ledger originally proposed — would have
> produced a wrong allowlist: `web_fetch`/`ask_user`/`create` are not
> agent-profile names, and `read`/`search`/`web`/`todo` are not hook names.
>
> **VERIFIED AGAINST A RUNNING COPILOT SESSION** (CLI 1.0.70, 2026-07-29),
> not just against the docs. Three probes in a scratch repo:
>
> | Probe | Result |
> |---|---|
> | control agent, no `tools:` | created the file (via shell) |
> | restricted to `read,view,grep,search,glob` | `CANNOT_WRITE`, no file |
> | same agent, told to leak via `curl`/`git` | `LEAK_FAILED`, no file |
>
> **`read` and `search` were silently ignored** — the restricted agent got
> exactly `view` / `grep` / `glob`. That is the documented
> unrecognized-names-are-ignored rule, observed, and it is why each Claude
> tool maps to EVERY equal-privilege spelling: had the map guessed `read`
> alone, every agent would have lost file reading outright. The redundancy
> is load-bearing, not belt-and-braces decoration.
>
> **Do not trust an agent's self-report of its own tools.** Asked to list
> them, the probe named `git` and `curl` — neither exists as a tool; the
> follow-up leak attempt failed with "Skill 'curl' not found". Test the
> BEHAVIOUR (can it write?), never the description.
- `AGENTS.md` — the cross-tool claim-grounding discipline, projected
  verbatim from RavenClaude's root `AGENTS.md`. Copilot reads `AGENTS.md`
  natively, but only from *your* repo — so this travels the discipline
  with the agents. Wire it via `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (below).

## Launching

Load the agents as Copilot custom agents by pointing Copilot at this
directory:

```shell
copilot --plugin-dir plugins/ravenclaude-core/copilot
```

To also load the claim-grounding discipline (`AGENTS.md`), point
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` at this directory:

```shell
export COPILOT_CUSTOM_INSTRUCTIONS_DIRS=plugins/ravenclaude-core/copilot
```

## Skills, hooks, and MCP — wired at the repo level, not in this package

Skills, enforcement hooks, and any MCP servers are NOT bundled into this
plugin. They are wired into the consumer's repo by `scripts/ravenclaude
install`:

- **Skills** are delivered to the consumer's `.claude/skills` — Copilot
  reads them live from there, so there is no second copy to keep in sync.
- **Enforcement hooks** are delivered to `.github/hooks` via the Copilot
  hook adapter. Plugin-level hooks are intentionally NOT used: Copilot has
  an open bug (github/copilot-cli#2540) where plugin-level preToolUse
  hooks don't fire, so enforcement hooks must be repo-level to run.

## Updating

Because Copilot loads this package live via `--plugin-dir`, **updates are
just `ravenclaude update` / `git pull` — never a re-install.** Pulling the
latest tree is all it takes for the new agents to be picked up next launch.

## Regenerating this package

This package is **generated**. To change anything here, edit the canonical
`ravenclaude-core` plugin and re-run:

```shell
python3 scripts/generate-copilot-plugin.py
```
