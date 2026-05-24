# AGENTS.md — RavenClaude

Cross-tool agent-instruction file. This is the canonical version of the marketplace's coding-agent guidance. `CLAUDE.md` imports this file and adds Claude-Code-specific notes. Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, and Windsurf read this file natively.

## What this repo is

RavenClaude is a private Claude Code **plugin marketplace**. The "product" of this repo is the contents of `plugins/`, distributed via Claude Code's built-in plugin marketplace mechanism. There are two distinct CLAUDE.md / AGENTS.md audiences:

- **This file (root)** — working *on* the marketplace itself (adding plugins, editing manifests, CI).
- **`plugins/ravenclaude-core/CLAUDE.md`** — the team constitution that ships *inside* the plugin and governs the agents.

Don't let them drift toward each other.

## Setup commands

```shell
# No package install — the marketplace is markdown + shell + JSON manifests.
# Local development test:
/plugin marketplace add ./    # from a separate Claude Code project
/plugin install ravenclaude-core@ravenclaude
```

`jq` and `python3` are required for the CI workflows and the layout-enforcement hook. Both are present in the devcontainer.

## Repo layout

```
RavenClaude/
├── .claude-plugin/marketplace.json    catalog of plugins
├── .repo-layout.json                  allow-list consumed by hook + CI
├── plugins/
│   ├── ravenclaude-core/              domain-neutral plugin
│   └── power-platform/                Microsoft Power Platform specialists
├── .claude/                           project config for working ON the marketplace
├── .github/workflows/                 CI: validate-marketplace + validate-layout
├── docs/                              meta-repo docs
└── AGENTS.md / CLAUDE.md / README.md  boundary files (root)
```

Every plugin **must** have `.claude-plugin/plugin.json`, `README.md`, and `CLAUDE.md`. It **may** have any of `agents/`, `skills/`, `hooks/`, `rules/`, `templates/`, `commands/`, `knowledge/`. It **may** add purpose-specific directories (e.g. `solutions/`, `flows/`) when justified — declare them in `plugin.json` and explain in the plugin's CLAUDE.md.

## Code style

- **Manifests** — JSON only, validated by `python3 -m json.tool` in CI. No trailing commas.
- **Hooks** — bash with `set -euo pipefail`. Validated by `bash -n` in CI. Must be executable.
- **Markdown** — short, scannable, action-oriented. Use tables for decisions, lists for steps.
- **Filenames** — kebab-case for all new files (`enforce-layout.sh`, `validate-layout.yml`).

## Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json` with `name`, `description`, `version`.
2. Add `CLAUDE.md` and `README.md` at the plugin root.
3. Add `agents/`, `skills/`, `hooks/`, `rules/`, `templates/`, `commands/`, `knowledge/` as needed.
4. Append the plugin to `plugins[]` in `.claude-plugin/marketplace.json`.
5. Add any new top-level dirs to `.repo-layout.json` `allowed_globs`.
6. Bump the plugin's `version` on every user-visible change (semver).
7. **For every new agent, fill in the scenario-authoring schema** (`audience`, `works_with`, `scenarios`, `quickstart`) in the agent's YAML frontmatter — see [`docs/best-practices/agent-scenario-authoring.md`](docs/best-practices/agent-scenario-authoring.md). The repo-guide generator picks them up automatically and surfaces them in per-agent cards + the Overview tab use-case lookup table.

## Modifying an existing plugin

1. Edit files inside `plugins/<plugin-name>/`.
2. Bump `version` in `plugins/<plugin-name>/.claude-plugin/plugin.json` **and** in `.claude-plugin/marketplace.json` (CI fails on drift).
3. Update consumers via `/plugin marketplace update ravenclaude` followed by `/reload-plugins`.

## Layout & boundary rules

A new file's path must match at least one glob in `.repo-layout.json` `allowed_globs`. Enforcement has two layers:

- **In-Claude-Code (fast feedback)** — `plugins/ravenclaude-core/hooks/enforce-layout.sh` runs `PreToolUse` on `Write|Edit|MultiEdit` and denies off-pattern paths with a suggested correct location.
- **CI (cross-tool backstop)** — `.github/workflows/validate-layout.yml` runs on every PR; fails the build if any added file violates the allow-list.

> Why a hook + CI instead of `paths:`-scoped rule files: Claude Code issue [#23478](https://github.com/anthropics/claude-code/issues/23478) — path-scoped rule files load on Read, not on Write, so they cannot block file *creation*. The hook + CI pair is the supported pattern.

## Testing instructions

Before opening a PR:

```shell
# 0. Checkout freshness (advisory) — warn if this tree is behind origin/main, so a
#    test run is never silently trusted against a stale checkout (a fix already merged
#    upstream can otherwise look "not done" locally). Auto-skips in CI; offline-safe.
scripts/check-checkout-fresh.sh

# 1. JSON validity
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
for m in plugins/*/.claude-plugin/plugin.json; do python3 -m json.tool "$m" > /dev/null; done
python3 -m json.tool .repo-layout.json > /dev/null

# 2. Shell syntax + executability
bash -n plugins/*/hooks/*.sh
find plugins/*/hooks -name '*.sh' -exec test -x {} \;

# 3. Prettier formatting (YAML / JSON / JS / TS / CSS — markdown is excluded)
#    REQUIRED before pushing any branch that touches .yml / .yaml / .json / .js / .ts / .css files.
#    Prettier check runs on the WHOLE TREE in CI, so a formatting failure on one file blocks
#    every subsequent PR until fixed in main — even PRs that don't touch the failing file.
#    Always auto-fix with --write before committing rather than --check + manual fix.
npx --yes prettier --write . --log-level warn   # auto-format any out-of-style files
npx --yes prettier --check . --log-level warn   # verify clean — must return exit 0

# 4. Audit every gate (the meta-test)
scripts/audit-gates.sh
# Proves each CI gate fails on a known-bad fixture AND passes on a known-good one.
# Required reading before adding or changing any CI step: docs/best-practices/ci-gate-audit.md
# NOTE: Gate 10 (actionlint) needs a usable docker daemon + the rhysd/actionlint image.
#       Without it the gate LOUD-skips locally ("THIS IS NOT A PASS" — a skip is not a pass);
#       in CI an unrunnable Gate 10 is a hard failure, never a silent skip.

# 5. Local install test (from a separate test project)
# /plugin marketplace add /workspaces/RavenClaude
# /plugin install ravenclaude-core@ravenclaude
# Confirm agents appear in /plugin UI.
```

### Why the prettier-on-the-whole-tree discipline matters

CI's prettier step runs `prettier --check .` against the entire working tree, not just the files in the current diff. Practical consequence: **a single mis-formatted file in main blocks every subsequent PR's CI** until that file is reformatted in main. Always run `prettier --write .` before pushing — even if your PR is markdown-only, an unrelated YAML/JS file added in a previous PR can fail the check. Verified once with `prettier --check .` returning exit 0 before pushing.

### Layout-allow-list discipline (added 2026-05-21 after PR #32 failed)

**Before pushing any PR that introduces a new directory under `plugins/<plugin>/`, update `.repo-layout.json` `allowed_globs` to include the new path.** The CI workflow `validate-layout.yml` reads the allow-list and blocks any added file whose path doesn't match. The local hook (`enforce-layout.sh`) catches this during the session, but only fires on Write/Edit/MultiEdit — if you create a new directory and add files in a single batch with `mkdir -p` + Write to a path the hook hasn't yet seen, the failure surfaces in CI not locally.

**Verification snippet** (run before `git push`):

```shell
# Find any new files outside the allow-list (per CI's check)
python3 - <<'PY'
import fnmatch, json, subprocess
allowed = json.load(open(".repo-layout.json"))["allowed_globs"]
new = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", "main"],
                     capture_output=True, text=True).stdout.splitlines()
violations = [f for f in new if not any(fnmatch.fnmatchcase(f, g) for g in allowed)]
if violations:
    print("LAYOUT VIOLATIONS — add globs to .repo-layout.json first:")
    for v in violations: print(f"  - {v}")
else:
    print("Layout OK — every new file matches at least one allowed glob.")
PY
```

CI runs the same checks plus the gate-audit meta-test.

## PR conventions

- **Branches** — `feat/<plugin-name>-<slug>`, `fix/<plugin-name>-<slug>`, `chore/<slug>`.
- **Versioning** — bump the plugin's semver on every user-visible change.
- **Migration notes** — if the change could break a consumer's existing project on `/plugin marketplace update`, add a "Migration" section to the plugin's release notes.
- **Privacy** — the marketplace is private by default. Don't push to a public-readable remote without removing the `email` field from `marketplace.json` and `plugin.json`.

## House rules

1. The `ravenclaude-core` plugin stays **domain-neutral**. Power Platform / finance / EdTech / Salesforce specifics live in their own plugins.
2. Plugin agents reference *plugin-internal* files only. They never hard-code paths inside a consumer's repo unless those paths are conventional (e.g. `docs/pm/raid-log.md`).
3. Before merging any plugin change, simulate: "what happens when a consumer runs `/plugin marketplace update`?" If the answer is "their project breaks," add a migration note.
4. Don't restate things the lint / CI / hook already enforces. They are the source of truth.
