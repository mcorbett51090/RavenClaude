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

## Launching

Load the agents as Copilot custom agents by pointing Copilot at this
directory:

```shell
copilot --plugin-dir plugins/ravenclaude-core/copilot
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
