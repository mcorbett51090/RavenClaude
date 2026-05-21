# New plugin checklist

Use this checklist when adding a new domain plugin to the marketplace (Salesforce, finance, EdTech, or any new vertical). It's ordered.

The reference implementations to copy patterns from are `plugins/ravenclaude-core/` (neutral team shape) and `plugins/power-platform/` (domain specialist team + imported skills + bundled MCP).

---

## 1. Decide whether it actually belongs as its own plugin

- [ ] The work is **domain-specific enough** that putting it in `ravenclaude-core` would pollute it. Specifically: a Salesforce engagement, a finance engagement, and an iOS-app engagement would not all benefit from this content.
- [ ] You have **at least three specialist agents in mind** that would live in this plugin. Less than that, the boundary is too thin — consider adding the content to an existing plugin instead.
- [ ] You can name the plugin's domain in 2–4 words (`power-platform`, `salesforce-cloud`, `fpa-finance`, etc.). Slug-form, lowercase, hyphen-separated.

---

## 2. Scaffold the folder

From the repo root:

- [ ] Create `plugins/<plugin-name>/`.
- [ ] `plugins/<plugin-name>/.claude-plugin/plugin.json` — manifest. Copy structure from `plugins/power-platform/.claude-plugin/plugin.json`. Fields: `name`, `version` (start at `0.1.0`), `description`, `author`, `homepage`, `license`, `keywords`, optionally `requires` and `mcpServers`.
- [ ] `plugins/<plugin-name>/CLAUDE.md` — team constitution. Copy the section structure from `plugins/power-platform/CLAUDE.md`: roster, routing rules, house opinions, anti-patterns, output contract, hooks, skills, escalation.
- [ ] Subfolders, only the ones you actually need: `agents/`, `skills/`, `hooks/`, `rules/`, `templates/`. Don't create empty placeholder folders.
- [ ] `plugins/<plugin-name>/CHANGELOG.md` — start with `## [0.1.0] — YYYY-MM-DD` and a one-line "initial release" entry.

If you're importing third-party content (someone else's skills, a community MCP server):

- [ ] `plugins/<plugin-name>/NOTICE.md` — license attribution. Use `plugins/power-platform/NOTICE.md` as the canonical form. Include source URL, author, license, and a one-paragraph description of what was imported.

---

## 3. Wire it into the catalog

- [ ] Append the new plugin to `plugins[]` in `.claude-plugin/marketplace.json`. The catalog `version` must match the new `plugin.json` `version`.
- [ ] If the new plugin depends on `ravenclaude-core`, declare it: `"requires": { "plugins": ["ravenclaude-core@>=X.Y.Z"] }` in the new `plugin.json`. Pick the minimum core version you actually need — don't pin to the latest unless you're using something new.

---

## 4. Build the agents

For each specialist:

- [ ] One file per agent in `plugins/<plugin-name>/agents/<role>.md`. Use an existing agent file as the template (`plugins/ravenclaude-core/agents/architect.md` or any `plugins/power-platform/agents/*.md`).
- [ ] Agent file declares: role, when to spawn, output contract, escalation rules, and any domain-specific house opinions.
- [ ] Agent file references **plugin-internal paths only** (relative `../skills/X`, `../templates/X.md`). Never reference consumer-project paths or paths in `ravenclaude-core` by absolute path.
- [ ] If the specialist has a clear handoff to a `ravenclaude-core` agent (architect, security-reviewer, project-manager), document it in the agent file's escalation section.

---

## 5. Build the routing rules in CLAUDE.md

- [ ] §1 "Team roster" — table with agent name, what they own, when to spawn.
- [ ] §2 "Routing rules" — common multi-agent recipes ("Build X" → agent A → agent B → agent C).
- [ ] §3 "Cross-cutting house opinions" — the platform-wide rules every agent enforces. Keep these grep-able if you want hook coverage.
- [ ] §4 "Anti-patterns every agent flags" — things to never do.
- [ ] §5 onward — domain-specific protocols (capability grounding, skill maps, MCP boundaries, etc.).

---

## 6. Add hooks (optional but recommended)

If any §3 or §4 rule is **mechanically grep-able**, write a hook:

- [ ] `plugins/<plugin-name>/hooks/check-<thing>.sh` — bash, `#!/usr/bin/env bash`, `set -euo pipefail`.
- [ ] Hook must be `chmod +x`. CI fails if it isn't.
- [ ] Default to **advisory** (`exit 0` with warning to stderr) for the first release. Promoting to blocking (`exit 1`) is a later decision after consumers report false-positive rates.
- [ ] Scope file-type filter narrowly — don't fire on every `.md` edit if you only care about source files.
- [ ] Add a `hooks/README.md` if the hook needs setup instructions for consumer `.claude/settings.json`.

See `plugins/power-platform/hooks/check-house-opinions.sh` for the canonical pattern.

---

## 7. Pre-flight validation

Same checks the release checklist requires, applied to the new plugin:

- [ ] `python3 -m json.tool plugins/<plugin-name>/.claude-plugin/plugin.json` — manifest parses.
- [ ] `python3 -m json.tool .claude-plugin/marketplace.json` — catalog still parses with the new entry.
- [ ] `bash -n plugins/<plugin-name>/hooks/*.sh` — hooks (if any) are syntactically valid.
- [ ] All hook scripts are executable.
- [ ] No cross-plugin path leaks: `grep -rEn 'plugins/ravenclaude-core/' plugins/<plugin-name>/` should be empty (or only reference docs, not load paths).

---

## 8. Local smoke test (mandatory before opening PR)

- [ ] In a scratch directory (not this repo): `/plugin marketplace add /path/to/RavenClaude`.
- [ ] `/plugin install <plugin-name>@ravenclaude`.
- [ ] `/reload-plugins`.
- [ ] Open `/plugin` UI — the new plugin appears and shows the right number of agents.
- [ ] Ask the top-level Claude session to use `spawn-team` to dispatch one of your new specialists. Verify the dispatch lands cleanly and the agent's output contract is followed.
- [ ] If the plugin declares an MCP server: verify the MCP starts (or that the failure mode is a clear "consumer needs to install X" message, not a silent hang).

---

## 9. Open the PR

- [ ] PR title: `feat: add <plugin-name> plugin (initial release v0.1.0)`.
- [ ] Use the **Marketplace / meta change** section of the PR template.
- [ ] PR body lists: number of agents, number of skills, hooks, any bundled MCP, any consumer prerequisites (e.g., `pip install <pkg>`), and the routing rules summary.
- [ ] If imported third-party content: link to the upstream repo, its license, and your `NOTICE.md`.

---

## 10. Post-merge

Follow the [release checklist](release-checklist.md) from step 6 to tag and publish the `0.1.0` release.

- [ ] Tag: `<plugin-name>-v0.1.0`. Push the tag.
- [ ] GitHub Release drafted by `release.yml` workflow — sanity-check the auto-extracted changelog section, then publish.
- [ ] Update `docs/architecture.md` Status table with the new plugin.
- [ ] Update `README.md` "What's in each plugin" section with a new sub-section for the new plugin.
- [ ] Announce in the team channel — what the plugin is for, who should install it, any prerequisites.

---

## Common pitfalls

| Pitfall | Fix |
|---|---|
| Forgetting to bump the catalog `version` when bumping `plugin.json` `version` | Run the version-drift check locally before pushing. |
| Hook isn't `chmod +x` after copying from another plugin | `find plugins/<plugin-name>/hooks -name '*.sh' -exec chmod +x {} \;` |
| Agent files reference `ravenclaude-core` paths absolutely instead of via `[[../../ravenclaude-core/...]]` | Treat the plugin as if it could be installed *without* `ravenclaude-core` — your agent file shouldn't break if so. Document the dependency in `requires`, not in path references. |
| Imported skill content checked in without a `NOTICE.md` | Add the attribution before merging. License compliance is non-negotiable. |
| MCP server declared in `plugin.json` but consumer can't install the prerequisite | Document the prerequisite in `CLAUDE.md` §<MCP section> and in the README. Make the failure mode clear (the agent should say "the MCP isn't running — install X" rather than silently giving wrong answers). |
