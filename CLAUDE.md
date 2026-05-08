# RavenClaude — Marketplace Constitution

> This file describes how to work **on** the RavenClaude plugin marketplace itself. If you're looking for the team rules that ship inside the `ravenclaude-core` plugin (architect, coders, reviewers, etc.), see [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md).

---

## 1. What this repo is

**Name:** RavenClaude
**Purpose:** A private Claude Code **plugin marketplace** that hosts opinionated, reusable agent + skill bundles. Starts with the domain-neutral `ravenclaude-core` plugin (Team Lead + 13 specialists, dispatch playbooks, gates, templates) and grows to include domain plugins (Power Platform, finance, EdTech, Salesforce) over time.
**Status:** Marketplace meta-repo. The "product" of this repo is the contents of `plugins/`, distributed via Claude Code's built-in plugin marketplace mechanism.

### Repo layout

```
RavenClaude/
├── .claude-plugin/
│   └── marketplace.json           ← marketplace catalog (lists available plugins)
├── plugins/
│   └── ravenclaude-core/          ← the domain-neutral plugin
│       ├── .claude-plugin/
│       │   └── plugin.json        ← plugin manifest
│       ├── CLAUDE.md              ← team constitution that ships with the plugin
│       ├── agents/                ← 13 agent definitions
│       ├── skills/                ← dispatch playbook, worktree helpers, etc.
│       ├── hooks/                 ← format-on-write, guard-destructive, remind-tests
│       ├── rules/                 ← coding-standards, security, git-workflow, agent-collab
│       └── templates/             ← memos, runbooks, design specs, RAID logs, partner-success
├── .claude/                       ← project-level config FOR working on this repo itself
│   ├── settings.json              ← permissions + hooks for marketplace dev
│   └── settings.local.json        ← gitignored, per-developer overrides
├── docs/                          ← meta-repo docs (architecture, lessons-learned, decisions)
├── README.md                      ← marketplace install instructions for end users
└── CLAUDE.md                      ← this file (working ON the marketplace)
```

Future domain plugins land alongside `ravenclaude-core/` under `plugins/` and are added to `marketplace.json`.

---

## 2. How to work on this repo

### Adding a new plugin
1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json` with `name`, `description`, `version`.
2. Add `agents/`, `skills/`, `hooks/`, `rules/`, `templates/` subdirectories as needed.
3. Append the new plugin to `plugins[]` in `.claude-plugin/marketplace.json`.
4. Bump version on every release (or rely on git commits as implicit versioning if `version` is omitted).
5. Test locally with `/plugin marketplace add ./` from a separate test project, then `/plugin install <plugin-name>@ravenclaude`.

### Modifying an existing plugin
1. Edit files inside `plugins/<plugin-name>/`.
2. Bump the plugin's `version` in `plugins/<plugin-name>/.claude-plugin/plugin.json`.
3. Update consumers via `/plugin marketplace update ravenclaude` followed by `/reload-plugins`.

### Internal references
- Plugin agent files reference the plugin's own `CLAUDE.md`, `rules/`, `templates/` via plugin-relative paths (`../CLAUDE.md`, `../rules/X.md`, `../templates/X.md`).
- Plugin agent files do **not** reference the meta-repo's root `CLAUDE.md` — that's a different document with a different purpose.

---

## 3. Quality gates for marketplace dev work

| Gate | Command | When |
|------|---------|------|
| JSON validity | `python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && python3 -m json.tool plugins/*/​.claude-plugin/plugin.json > /dev/null` | After any manifest edit |
| Shell syntax | `bash -n plugins/*/hooks/*.sh` | After any hook edit |
| Hook executability | `find plugins/*/hooks -name '*.sh' -exec test -x {} \;` | After any hook edit |
| Markdown link sanity | `grep -rEn '\]\([^)]+\)' plugins/ CLAUDE.md` then spot-check that referenced paths exist | After any agent/skill/rule edit |
| Local install test | `/plugin marketplace add ./` from a separate test project, then verify agents appear in `/plugin` UI | Before tagging a release |

---

## 4. Git workflow for the marketplace

- **`main`** — always green, always installable. Every commit on `main` is a candidate version of every plugin (unless plugin manifests pin explicit versions).
- **`feat/<plugin-name>-<slug>`** — new features in a specific plugin.
- **`fix/<plugin-name>-<slug>`** — bug fixes in a specific plugin.
- **`chore/<slug>`** — marketplace tooling, docs, devcontainer, etc.

Versioning: plugin manifests use semver. Bump on every user-visible change. Marketplace consumers can pin to a specific commit `sha` for reproducibility.

---

## 5. House rules

1. The `ravenclaude-core` plugin stays **domain-neutral**. Power Platform / finance / EdTech / Salesforce specifics go in their own plugins, not in `ravenclaude-core`.
2. Plugin agents reference *plugin-internal* files only (rules, templates inside the same plugin). They never reference paths in the consumer project's repo unless those paths are conventional (e.g. `docs/pm/raid-log.md` is the convention; the agent doesn't link to it as an absolute path).
3. CLAUDE.md is **two distinct files**: this one (meta-repo dev guide) and `plugins/ravenclaude-core/CLAUDE.md` (team constitution). They have different audiences and shouldn't drift toward each other.
4. The marketplace is **private** by default. Don't push to a public-readable remote without removing the `email` field from `marketplace.json` and `plugin.json` (or accept that the email is now public).
5. Before merging a plugin change, mentally simulate "what happens when a consumer runs `/plugin marketplace update`?" — if the answer is "their existing project breaks," the change needs a migration note in the plugin's release notes.

---

## 6. Installing the marketplace (for end users)

```shell
# In any Claude Code project where you want the agents:
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude

# Or, for local development against your own checkout:
/plugin marketplace add /path/to/RavenClaude
/plugin install ravenclaude-core@ravenclaude
```

After install, run `/reload-plugins` to activate.

For users on locked-down enterprise plans where marketplace installs are restricted, the fallback is a plain `git clone` of this repo and copying `plugins/ravenclaude-core/` into `~/.claude/` (user scope) or the consumer project's `.claude/` (project scope). Loses auto-update; everything else works.
