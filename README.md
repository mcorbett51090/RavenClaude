# 🐦‍⬛ RavenClaude

**A private Claude Code plugin marketplace** — bundled team rules, specialist agents, dispatch playbooks, and templates that travel with you across projects.

Today this marketplace ships a single plugin, **`ravenclaude-core`**, which gives any project the Team Lead + 13 specialists pattern (architect, coders, reviewers, designer, documentarian, deep-researcher, project-manager, partner-success-manager, prompt-engineer, etc.). Future plugins for domain-specific work (Power Platform, finance, EdTech, Salesforce) will land alongside it.

---

## Install (recommended)

In any Claude Code project where you want the agents:

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

That's it. The 13 agents become available via the `Agent` tool under their namespaced `ravenclaude-core:<agent-name>` form (e.g. `ravenclaude-core:architect`, `ravenclaude-core:code-reviewer`). The dispatch skills (`spawn-team`, `new-worktree`, `cleanup-worktrees`, `create-pr`, `run-full-test-suite`) are loaded, and the format/lint/test hooks fire automatically.

To pin a specific version (recommended for client engagements where you don't want surprise updates):

```shell
/plugin marketplace add mcorbett51090/RavenClaude#<git-sha>
```

To update later:

```shell
/plugin marketplace update ravenclaude
/reload-plugins
```

---

## Local development install

If you want to iterate on this marketplace itself (or test a change before pushing):

```shell
# From any test project, point at your local checkout:
/plugin marketplace add /path/to/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

After editing files in `plugins/ravenclaude-core/`, run `/plugin marketplace update ravenclaude` and `/reload-plugins` again to pick up the changes.

---

## Fallback — clone instead of install

If you're on a Claude Code plan or in an enterprise environment that restricts marketplace installs, you can clone this repo and copy the plugin folder manually:

```bash
git clone https://github.com/mcorbett51090/RavenClaude.git
# User scope (available across all your projects on this machine):
cp -r RavenClaude/plugins/ravenclaude-core/* ~/.claude/

# Or project scope (just one project):
cp -r RavenClaude/plugins/ravenclaude-core/* /path/to/your/project/.claude/
```

You lose auto-update and version pinning. To update, `git pull` and re-copy. Otherwise the agents, skills, hooks, rules, and templates work identically.

---

## What's in `ravenclaude-core`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 13 | `plugins/ravenclaude-core/agents/` |
| Skills | 10 (dispatch via `spawn-team`, `new-worktree` / `cleanup-worktrees`, `create-pr`, `run-full-test-suite`, `draft-agent-brief`, `structured-output`, plus `contribute-finding` / `review-staged-contributions` for the cross-domain staging loop; the `researcher/` meta-skill sits alongside as a folder) | `plugins/ravenclaude-core/skills/` |
| Hooks | 3 (format-on-write, guard-destructive, remind-tests) | `plugins/ravenclaude-core/hooks/` |
| Rules | 4 (coding-standards, security, git-workflow, agent-collaboration) | `plugins/ravenclaude-core/rules/` |
| Templates | 21 (memos, runbooks, design specs, RAID logs, partner-success artifacts) | `plugins/ravenclaude-core/templates/` |

The team rules ship inside the plugin as [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md). Copy or adapt that into your consumer project's root `CLAUDE.md` and fill in your project's stack-specific gates (formatter, linter, type-checker, test runner).

For a full list of agents and when to spawn each, see the team-roster table in [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) §5.

---

## How agents actually get invoked

Plugin agents are exposed as **namespaced** `subagent_type` values on the `Agent` tool: `ravenclaude-core:architect`, `ravenclaude-core:code-reviewer`, `ravenclaude-core:backend-coder`, and so on. The **bare name** (e.g. `subagent_type: "code-reviewer"`) is reserved for Claude Code's built-in agents and will fail with `InputValidationError` for plugin-supplied agents — always include the `ravenclaude-core:` prefix.

The agents fire through the **Team Lead orchestration pattern**:

1. The top-level Claude session acts as **Team Lead** — it reads `plugins/ravenclaude-core/CLAUDE.md`, sees the team roster, and decides which specialist(s) the user's request needs.
2. To dispatch one or more specialists, the Team Lead invokes the [`spawn-team`](plugins/ravenclaude-core/skills/spawn-team.md) skill — that's the playbook for picking the right specialist, briefing it like a new colleague, and integrating the structured handoff payload that comes back.
3. The Team Lead calls `Agent(subagent_type="ravenclaude-core:<role>", …)` directly. Specialists return a Markdown report ending in a `---RESULT_START--- … ---RESULT_END---` JSON block, and the Team Lead re-routes from there.
4. **Sub-agents never spawn other sub-agents.** They return a slice; the Team Lead re-dispatches. This keeps the dependency graph a flat tree.

If you want to talk to a specific agent directly (e.g. "have the architect look at this"), say so in plain English to the Team Lead and it will use `spawn-team` to dispatch the architect via the namespaced `subagent_type`.

For the dispatch playbook itself, see [`plugins/ravenclaude-core/skills/spawn-team.md`](plugins/ravenclaude-core/skills/spawn-team.md).

---

## Working on the marketplace itself

If you're **developing** RavenClaude (adding plugins, updating agents), see [`CLAUDE.md`](CLAUDE.md) at this repo's root — it's the meta-repo dev guide.

Repo layout:

```
RavenClaude/
├── .claude-plugin/marketplace.json    ← marketplace catalog
├── plugins/
│   └── ravenclaude-core/              ← the domain-neutral plugin
├── .claude/                           ← settings for working ON the marketplace
├── docs/                              ← meta-repo docs
└── CLAUDE.md                          ← meta-repo dev guide
```

The container at `.devcontainer/` auto-installs the Claude Code CLI on rebuild, so a fresh Codespace is ready to work on plugins without setup.

---

## Roadmap

Planned future plugins (each in its own subfolder under `plugins/`, all in this same repo):

- **`power-platform`** — Power Apps / Power Automate / Dataverse specialists.
- **`finance`** — FP&A, variance analysis, financial-modeling specialists.
- **`edtech`** — partner-success, rostering, FERPA-aware translation specialists.
- **`salesforce`** — Salesforce metadata, Apex, Flow specialists.

Each builds on top of `ravenclaude-core` (which provides the neutral team) and adds domain-specific agents that the consumer can choose to install or skip.

---

## License

MIT — see [`LICENSE`](LICENSE) for the full text. Bundled third-party content carries its own attribution; see [`plugins/power-platform/NOTICE.md`](plugins/power-platform/NOTICE.md) for the Daniel Kerridge skills import and the pbix-mcp server attribution.
