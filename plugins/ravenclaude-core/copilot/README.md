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

> ### ⚠️ KNOWN GAP — agents run UNRESTRICTED here
>
> The canonical agents each carry a least-privilege `tools:` allowlist, and
> `AGENTS.md` house rule 9 is explicit that **an omitted `tools:` silently
> grants ALL tools**. This projection drops that field. Per RavenClaude's own
> docs-verified notes (`knowledge/copilot-cli-customization.md` §2), a Copilot
> agent **has every tool by default and a `tools:` spec only *restricts*** —
> so dropping it is not neutral, it is a least-privilege regression.
>
> Concretely: `security-reviewer` is canonically `Read, Grep, Glob, Bash,
> WebFetch` — deliberately **no Write/Edit** — and under Copilot it can write.
> The same applies to every review-only agent.
>
> **Why this is not simply fixed here:** projecting the allowlist requires
> Copilot's exact tool-name vocabulary, which differs from Claude's (Copilot
> documents lowercase `bash` / `edit` / `view`). Emitting Claude's names would
> either be ignored — no gain — or restrict to unrecognised names and leave
> every agent with NO tools, which is a worse regression than the one it fixes.
> GitHub has not published the complete list at a fetchable URL as of
> 2026-07-28 (two candidate doc pages returned 404).
>
> **The probe that closes this:** run `copilot` and enumerate the real tool
> names, then add a Claude→Copilot name map to `generate-copilot-plugin.py`
> mirroring the runtime map already in `hooks/copilot-hook-adapter.sh`.
> Until then, treat every agent under Copilot as fully privileged.
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
