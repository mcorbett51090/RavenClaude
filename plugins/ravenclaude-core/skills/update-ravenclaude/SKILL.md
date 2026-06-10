---
name: update-ravenclaude
description: "Bring a RavenClaude install up to date when it's stale, when new skills/agents aren't showing, or after upstream changes ship. Covers both hosts: under GitHub Copilot CLI the update is `git pull` in the marketplace clone then re-running `ravenclaude setup` (idempotent); under Claude Code it's `/plugin marketplace update ravenclaude` then `/reload-plugins`. Read this skill on triggers like 'update ravenclaude', 'ravenclaude is stale', 'refresh skills', or 'new skills not showing'."
---

# Skill: update-ravenclaude

This skill is the canonical reference for **how to refresh a RavenClaude install** so that newly shipped skills, agents, hooks, and posture changes take effect. The mechanics differ by host (GitHub Copilot CLI vs. Claude Code), so the skill covers both.

## When to use it

Reach for this skill on any of these signals:

- "update ravenclaude" / "bring ravenclaude up to date"
- "ravenclaude is stale" / "my version is behind"
- "refresh skills" / "reload skills"
- "new skills aren't showing" / "I don't see the agent/skill that was just added"
- after you know upstream shipped a change (a new plugin version, a new skill, a hook fix) and you want it locally

## Path B — GitHub Copilot CLI (the `git pull` + re-wire flow)

The Copilot bridge loads everything **live from your marketplace clone** — skills (`.claude/skills`), hooks (`.github/hooks`), MCP config, and the `rc` alias are all read live from disk. So an update is two steps:

```shell
# 1. Pull latest upstream changes into the marketplace clone
cd ~/RavenClaude && git pull

# 2. Re-wire skills, hooks, and posture into the current project
bash ~/RavenClaude/scripts/ravenclaude setup --project . [--with-plugin <name>]
```

Notes:

- **`--with-plugin <name>`** (e.g. `--with-plugin power-platform`) should be included **only if that plugin was part of your original setup**. A base, core-only update omits it.
- **`ravenclaude setup` is idempotent** — safe to re-run at any time. It re-wires the live surfaces and never clobbers an existing `.ravenclaude/comfort-posture.yaml`.
- `ravenclaude update` (a bare `git pull` + regenerate, no project re-wire) is the lighter form when you only need fresh marketplace content and don't need the current project re-wired.

## Path A — Claude Code (the marketplace-update flow)

Claude Code caches installed plugins, so the refresh is a marketplace update followed by a reload:

```text
/plugin marketplace update ravenclaude
/reload-plugins
```

- Run `/reload-skills` as well if a **skill** specifically isn't showing after the reload.
- If the cache is genuinely broken (tool lockout, "decision helper missing"), escalate to `/reset-plugin-cache` (alias `/ragnarok`) — read its command doc first; it's high-blast-radius and dry-run by default.

## Why the two hosts differ

| Host | Loads plugin content… | Update is… |
|---|---|---|
| GitHub Copilot CLI | **live from the clone on disk** | `git pull` + `ravenclaude setup` (idempotent) |
| Claude Code | from a **cached copy** | `/plugin marketplace update` + `/reload-plugins` |

This is why a Copilot update is "just `git pull`" (the design pillar of the bridge — no re-install ever) while a Claude Code update has to invalidate and reload the cache.

## See also

- `GETTING_STARTED.md` § "Updating RavenClaude (Copilot CLI)" — the consumer-facing copy of the Copilot flow.
- `scripts/ravenclaude` — the `setup` / `install` / `update` / `status` subcommands.
- `commands/reset-plugin-cache.md` — the disaster-recovery reset for a broken Claude Code cache.
