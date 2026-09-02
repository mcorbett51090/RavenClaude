# AGENTS.md — RavenClaude

Cross-tool agent-instruction file. This is the canonical version of the marketplace's coding-agent guidance. `CLAUDE.md` imports this file and adds Claude-Code-specific notes.

**Which tools actually read it** (corrected 2026-07-28 — the previous blanket claim that "Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, and Windsurf read this file natively" was **false for Aider**, and the repo's own Claim-Grounding protocol had been applied to the Copilot claim but not to the ones beside it):

| Tool | Reads `AGENTS.md` automatically? | Basis |
|---|---|---|
| **GitHub Copilot CLI** | **Yes** | `[docs-verified]` — see [`plugins/ravenclaude-core/knowledge/copilot-cli-customization.md`](plugins/ravenclaude-core/knowledge/copilot-cli-customization.md) §1, which cites the instruction-file precedence. VS Code **Copilot Chat** is a distinct product: Preview hooks *may* load `.github/hooks`; do not claim CLI coverage as Chat coverage. See [`plugins/ravenclaude-core/knowledge/copilot-chat-customization.md`](plugins/ravenclaude-core/knowledge/copilot-chat-customization.md). |
| **OpenAI Codex CLI** | **Yes** | `[docs-verified]` — Codex reads `AGENTS.md` from the repo root; see [`plugins/ravenclaude-core/skills/external-agent-onboarding/SKILL.md`](plugins/ravenclaude-core/skills/external-agent-onboarding/SKILL.md). |
| **Claude Code** | Indirectly | `CLAUDE.md` `@`-imports this file. |
| **Aider** | **NO — this was the false claim** | `[docs-verified 2026-07-28]` — [aider.chat/docs/usage/conventions.html](https://aider.chat/docs/usage/conventions.html) documents **`CONVENTIONS.md`**, loaded only on explicit opt-in (`aider --read CONVENTIONS.md` or `read:` in `.aider.conf.yml`). `AGENTS.md` is not mentioned on that page at all. An Aider user gets **nothing** from this file unless they opt in by hand. |
| **Cursor** | `[unverified]` | Cursor's documented native mechanism is `.cursor/rules/*.mdc`. Whether it also auto-loads `AGENTS.md` was **not** verified; do not rely on it. |
| **Windsurf** | `[unverified — and the product was renamed]` | Reported renamed to Devin Desktop (2026-06-02). Treat this lane as unmaintained until someone re-verifies it. |

**The honest summary:** this file is reliably read by **Copilot CLI and Codex**, reaches **Gemini CLI** through a `GEMINI.md` `@AGENTS.md` import, and reaches Claude Code by import. **Aider** gets it only as a projected `CONVENTIONS.md`. Cursor and Devin Desktop remain opt-in, unverified, or both. Do not add a tool to this table without a dated source — a false claim of support is worse than an admitted gap, because it stops anyone from building the bridge that would make it true.

> **Two Geminis, and they are not the same thing** (added 2026-07-29, audit MH-36 + MH-30):
>
> 1. **Gemini CLI is a supported HOST** since v0.222.0 `[docs-verified 2026-07-29]` — `ravenclaude install --host gemini` wires the
>    guardrails into `.gemini/settings.json` and points `GEMINI.md` at this file. Per-component truth: [`plugins/ravenclaude-core/knowledge/host-support.json`](plugins/ravenclaude-core/knowledge/host-support.json).
> 2. **Gemini is also used as a MODEL**, in exactly one place: the Power Platform `visual-qa` skill's
>    optional Gemini API integration for test-recording review. That is a supplemental feature, not
>    required, and it has nothing to do with host support.
>
> They were conflated because the second was the repo's only Gemini anything and was buried in a skill
> resource — so a reader looking for "Gemini support" found neither the host lane nor the integration.

## What this repo is

RavenClaude is a private Claude Code **plugin marketplace**. The "product" of this repo is the contents of `plugins/`, distributed via Claude Code's built-in plugin marketplace mechanism. There are two distinct CLAUDE.md / AGENTS.md audiences:

- **This file (root)** — working *on* the marketplace itself (adding plugins, editing manifests, CI).
- **`plugins/ravenclaude-core/CLAUDE.md`** — the team constitution that ships *inside* the plugin and governs the agents.

Don't let them drift toward each other.

## Setup commands

There is **no package install** — the marketplace is markdown + shell + JSON manifests. How you wire it in depends on your host, and **the three paths are not interchangeable** (corrected 2026-07-28, multi-host audit MH-18: this section previously showed only the Claude Code slash commands, so the first substantive thing a Codex or Copilot agent read was a procedure it structurally could not execute).

| Your host | Wire it in with | Notes |
|---|---|---|
| **Claude Code** | `/plugin marketplace add ./` then `/plugin install ravenclaude-core@ravenclaude` | Run from a separate Claude Code project. Slash commands work here and only here. |
| **GitHub Copilot CLI** | `bash <marketplace>/scripts/ravenclaude install --project <your-repo>` | Wires skills → `.claude/skills`, guardrails → `.github/hooks`, and points `.github/copilot-instructions.md` at the projected discipline. **Requires Copilot CLI ≥ 1.0.52** — below that a sub-agent's tool calls are not hooked at all; the installer checks and warns. **If a hook error blocks every tool call** (reported on very old builds, e.g. 1.0.3), run `bash <marketplace>/scripts/ravenclaude repair --host copilot --project <your-repo>` to safely disable the generated hooks file, update Copilot CLI, then re-run `install` — see [`plugins/ravenclaude-core/knowledge/copilot-cli-hook-incompatibility.md`](plugins/ravenclaude-core/knowledge/copilot-cli-hook-incompatibility.md). |
| **OpenAI Codex CLI** | `bash <marketplace>/scripts/ravenclaude install --host codex --project <your-repo>` | Wires skills → `.agents/skills` and guardrails → `.codex/hooks.json` (native contract, no adapter), and projects your comfort posture onto Codex's OS sandbox. **Then run `/hooks` inside Codex to trust them — and again after every update**, because Codex tracks hook trust by hash. |

`jq` and `python3` are required for the CI workflows and the layout-enforcement hook. Both are present in the devcontainer.

> **Claude-Code note (newer install sources).** Beyond the local-path `/plugin marketplace add ./` above, recent Claude Code also supports two additional marketplace source types: an **`archive`** source (install from a zip over HTTPS, with optional SHA-256 pinning — v2.1.224, 2026-08-07) and a **`command`** source (a local command prints the plugin directory, re-resolved each session, no restart — v2.1.229, 2026-08-12). RavenClaude itself is distributed by local path / git; these are options for other hosting shapes. `[platform fact, verified 2026-08-19 against the Claude Code changelog; changelog through 2.1.250 on 2026-08-28 does not reverse it]`

**Scaffolding the agent-in-CI protocol (any host).** After install, `bash <marketplace>/scripts/ravenclaude init-agent-ci --project <your-repo>` copies the agent-in-CI GitHub protocol set into your repo's `.github/`: the `github-protocol-*` workflows, the anti-self-approval `agent-approval-check.yml` **plus its companion `check-workflow-hygiene.py`** (the workflow invokes it — copied together so the scaffold is runnable, not green-but-broken), and an agent PR template. It is **opt-in and non-destructive** — it never overwrites an existing file without `--force`, and `--only <comma-list>` cherry-picks a subset. This is the path a **Copilot or Codex** consumer uses to adopt what only Claude Code's `/init-agent-ready` scaffolded before. **Honest limit:** these are **host-agnostic GitHub Actions artifacts** — they run in _your_ CI regardless of which agent CLI you use, but a non-Claude host reads the accompanying knowledge (identity, issue-triage, CI-signing) as **context, not as an enforced hook**. The anti-self-approval workflow stays inert until you CODEOWNERS-protect it, make it a required status check, and set its `EXCLUDED_APPROVERS` — see [`plugins/ravenclaude-core/knowledge/claude-in-ci.md`](plugins/ravenclaude-core/knowledge/claude-in-ci.md).

**Opening the dashboard.** The host-agnostic launcher is `bin/rc` — invoke it by **full path**, because a plain `rc` may resolve to something else on your `PATH`:

```shell
bash plugins/ravenclaude-core/bin/rc dashboard
```

`/dashboard` is the Claude Code shorthand for exactly that command; it does not exist on any other host.

For a guided, copy-paste install (with per-step verification and a "if the bridge is down…" troubleshooting accordion), open the dashboard's **Install a plugin (Bifröst)** tab (`#/bifrost`) — it walks the Claude Code steps above and lights each one as you paste back the command output.

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

## Where work files go — the cross-CLI storage contract (READ THIS BEFORE WRITING ANY FILE)

**Any CLI may be the one working here — Claude Code, Copilot, Codex, Cursor, Gemini, Aider — and the
next session may be a different one.** So where you put a file is not a personal preference: it is the
only thing that lets the next tool find your work. Put it in the right tier, stamp it, and any other
CLI can pick it up as if it had written it itself.

This section is the canonical statement. It is projected into every host's own instruction file, so
**edit it here, not in the projections.**

### The two tiers, and how to choose

| Tier | Path | Who can see it | Use it for |
|---|---|---|---|
| **Local run** | `.ravenclaude/runs/<task-id>/` | **this machine only** — gitignored | working notes, gate output, evidence, anything mid-flight |
| **Committed** | `docs/plans/`, `docs/decisions/`, `docs/research/` | you, teammates, CI | anything meant to outlive the task or be read by a human later |
| **Ledger** | `.ravenclaude/ledger/<YYYY-MM>.jsonl` | you, teammates, CI — **committed**, `merge=union` | the append-only work/change record: what is still open, how each item ended, and which PR/worktree it ended in |

**The test:** *would a teammate cloning this repo need it?* Yes → committed tier. No → local run tier.
When unsure, start local and promote it later; promoting is a `git add`, but un-committing something
that should not have travelled is not.

> **`.ravenclaude/runs/` is gitignored on purpose.** Run artifacts carry command output, absolute
> paths, branch names, and whatever the run happened to touch. That substrate is deliberately kept out
> of git and secret-scrubbed. **Do not "helpfully" commit it** — that reverses a deliberate decision,
> and it is a decision about other people's data, not just yours.

### What a run directory looks like

Create it with `plugins/ravenclaude-core/bin/rc artifacts new <task-id>` so the shape and the
provenance stamp are right without anyone memorising this:

```
.ravenclaude/runs/<task-id>/
├── meta.json            who made it, which CLI, when   <- the provenance stamp
├── summary.md           what was done, for a human
├── decisions.md         choices + WHY (the part that is expensive to recover)
├── structured-output.json   machine-readable result
└── events.jsonl         chronological actions, one JSON object per line
```

Every file is optional except `meta.json`. **Write the ones you actually have content for** — an empty
`decisions.md` is worse than none, because the next CLI reads it as "no decisions were made."

### Picking work up from another CLI

1. `plugins/ravenclaude-core/bin/rc artifacts list` — shows both tiers, newest first, with **which CLI wrote each one**. It is
   computed by scanning, so it cannot go stale.
2. Read `meta.json` first. If it was written by a different CLI, nothing special is required — the
   layout is identical — but knowing the origin tells you what *else* might exist (e.g. a Claude Code
   session leaves transcripts that a Codex session does not).
3. Continue in the **same directory**. Do not start a parallel one for the same task; two half-records
   is the failure this contract exists to prevent.

### What is NOT shared, and never will be

Naming this is part of the contract — an honest gap beats a false promise of parity:

| Host-private | Why |
|---|---|
| `~/.claude/` (session transcripts, memory), `~/.copilot/`, `~/.codex/` | each CLI's own state, in its own format, outside the repo |
| Session/conversation history | not a file the other tools can read, and not portable |
| A CLI's own caches | machine- and version-specific |

If work needs to survive across CLIs, **it has to be written into one of the two tiers above.** Nothing
in a host's private area crosses over — assume it is lost the moment the session ends.

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
7. **For every new agent, fill in the scenario-authoring schema** (`audience`, `works_with`, `scenarios`, `quickstart`) in the agent's YAML frontmatter — see [`docs/best-practices/agent-scenario-authoring.md`](docs/best-practices/agent-scenario-authoring.md). The portal generator (`index.html`) picks them up automatically and surfaces them in per-agent cards + the Overview tab use-case lookup table. **This is gated:** `scripts/check-frontmatter.py` fails the build if an `agents/*.md` is missing the schema (each `scenarios` item needs `intent` / `trigger_phrase` / `outcome` / `difficulty`).
8. **Keep each agent `description` ≤ 300 characters.** It's the only frontmatter field loaded into the orchestrator's prompt to route to subagents — see the agent-description token budget below. **This is gated:** `scripts/check-frontmatter.py` fails the build on any `agents/*.md` whose `description` exceeds 300 chars. Lead with what the agent is for + its distinctive keywords, keep the one most important `NOT for X → other-agent` boundary, and drop verbose restatements and example "spawn for '…'" phrase lists.
9. **Declare an explicit `tools:` allowlist on every agent (least-privilege).** Each `agents/*.md` MUST carry a `tools:` line in its frontmatter — the tool set is the only real bound on a dispatched subagent's blast radius: under a parent running `bypassPermissions`/`acceptEdits` the subagent inherits that mode and can't be restricted below it, so `tools:` (plus a hook `deny`) is what actually caps it (see [`plugins/ravenclaude-core/knowledge/claude-code-permissions.md`](plugins/ravenclaude-core/knowledge/claude-code-permissions.md) § "Subagents inherit the parent's permission mode"). An omitted `tools:` line silently grants ALL tools — the opposite of least-privilege; opt into all tools explicitly with `tools: "*"` when that is genuinely intended. **This is gated:** `scripts/check-frontmatter.py` fails the build on any `agents/*.md` with a missing or empty `tools`.

## The agent-description token budget (~15K) — why descriptions are capped

Claude Code loads the `name` + `description` of **every agent in every *enabled* plugin** into the orchestrator's system prompt so it can route to subagents (agent bodies load lazily, only when an agent is invoked). The combined descriptions count against a **~15K-token budget**; cross it and Claude Code warns *"agent descriptions are over the 15.0K token limit — /agents to free up context."*

This marketplace ships **~182 plugins / 600+ agents**, so two levers keep the budget affordable — they're complementary, not either/or:

1. **Per-agent cap (this repo's job).** Every agent `description` is held to ≤ 300 chars (~75 tokens) by the `check-frontmatter.py` gate above. No single plugin is the problem; the cap is what lets a consumer enable *many* plugins before hitting the warning.
2. **Enable only what you need (the consumer's job).** You cannot fit all ~182 plugins under 15K regardless of how tight the descriptions are — that's expected, not a defect. Enable the plugins relevant to your work and disable the rest via **`/agents`** (or `/plugin`). That's exactly what the warning's `/agents` hint points at, and it's the correct response to it. **Budget before you enable, not after the warning fires:** the `/plugin` **Discover** tab now surfaces a per-plugin **Context cost** estimate (the tokens a plugin adds to every turn — Claude Code v2.1.143+) and a **Will install** inventory of its commands/agents/skills/hooks/MCP+LSP servers (v2.1.145+), so you can see what a plugin costs the orchestrator prompt _before_ installing it rather than discovering the 15K overrun afterward. (Verified against [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins), 2026-06-21.)

## Modifying an existing plugin

1. Edit files inside `plugins/<plugin-name>/`.
2. Bump `version` in `plugins/<plugin-name>/.claude-plugin/plugin.json` — the **single source of truth** — then run `python3 scripts/sync-plugin-versions.py` to derive the `.claude-plugin/marketplace.json` entry. Never hand-edit the catalog version: two hand-edited copies of one fact is what made concurrent PRs conflict (one PR was re-bumped three times on 2026-08-17). CI still fails on drift (Gate 8), and Gate 226 (`sync-plugin-versions.py --check`) fails if the catalog is not derived.
3. For `ravenclaude-core` only, a bump also needs `python3 scripts/generate-copilot-plugin.py` — its `copilot/plugin.json` is generated and has its own freshness gate. The sync script deliberately does not call it (that generator rewrites the whole projected agent tree, not just a version).
4. Update consumers via `/plugin marketplace update ravenclaude`. `/reload-plugins` is **often no longer required** — since **v2.1.221 (2026-08-04)** plugins installed from `/plugin` activate immediately when safe, and the same release made `/plugin install` refresh a stale marketplace catalog and retry before reporting a plugin not found; run `/reload-plugins` only if a change doesn't take effect. `[verified 2026-08-19 against the Claude Code changelog; still present as a fallback after 2.1.243/246]`

### CHANGELOG convention (optional per plugin)

A per-plugin `CHANGELOG.md` is **optional, not required** — the authoritative version history is the `version` field (semver, bumped every user-visible change) plus git history, and each plugin's `CLAUDE.md` carries a milestones narrative for the larger arcs. Newer plugins ship a `CHANGELOG.md`; older ones intentionally don't, and that is not a defect. **The rule:** if a plugin *has* a `CHANGELOG.md`, keep its top entry current on every version bump; if it doesn't, don't add one just to satisfy symmetry — the version field + git log are the source of truth. (`.repo-layout.json` already allows `plugins/*/CHANGELOG.md` so adding one never trips the layout gate.)

## Layout & boundary rules

A new file's path must match at least one glob in `.repo-layout.json` `allowed_globs`. Enforcement has two layers:

- **In-Claude-Code (fast feedback)** — `plugins/ravenclaude-core/hooks/enforce-layout.sh` runs `PreToolUse` on `Write|Edit|MultiEdit` and denies off-pattern paths with a suggested correct location.
- **CI (cross-tool backstop)** — `.github/workflows/validate-layout.yml` runs on every PR; fails the build if any added file violates the allow-list.

> Why a hook + CI instead of `paths:`-scoped rule files: Claude Code issue [#23478](https://github.com/anthropics/claude-code/issues/23478) — path-scoped rule files load on Read, not on Write, so they cannot block file *creation*. The hook + CI pair is the supported pattern.

## Testing instructions

> **⚠️ If steps 3 or 4 fail with a network error, the cause is probably your host's sandbox — not a
> broken checkout** (added 2026-07-29, audit MH-34). `npx --yes prettier@…` and `pip install ruff`
> both **download**, and several hosts run the agent inside a sandbox that blocks outbound network by
> default:
>
> - **OpenAI Codex CLI** — `sandbox_mode = workspace-write` (the default) has network **off** unless
>   `[sandbox_workspace_write] network_access = true` `[docs-verified]`. You get a denial, not a lint
>   result.
> - **Cursor / Gemini** — may be sandboxed depending on configuration.
>
> This repo's own Capability Grounding Protocol tells you to *"read the actual error first and name
> its specific mechanical cause"* — so here it is, named, because nothing used to say it and the
> honest-looking conclusion ("linting is broken") is the wrong one. **Fixes, cheapest first:** run the
> two commands outside the sandboxed session; or install `prettier`/`ruff` once so no download is
> needed; or enable network for the workspace deliberately. **Do not skip the steps** — CI runs
> `prettier --check .` and `ruff check .` on the whole tree, so a skipped local run just moves the
> failure to the PR.

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
#    NOTE: `find … -exec test -x {} \;` does NOT fail on a non-executable file —
#    find's exit status reflects only traversal errors, not the -exec result — so
#    it was a silent no-op. Use a loop that propagates the per-file failure, and
#    cover scripts/*.sh syntax too (CI's validate-marketplace does the same).
bash -n plugins/*/hooks/*.sh scripts/*.sh
for f in plugins/*/hooks/*.sh; do [ -x "$f" ] || { echo "NOT EXECUTABLE: $f"; exit 1; }; done

# 3. Prettier formatting (YAML / JSON / JS / TS / CSS — markdown is excluded)
#    REQUIRED before pushing any branch that touches .yml / .yaml / .json / .js / .ts / .css files.
#    Prettier check runs on the WHOLE TREE in CI, so a formatting failure on one file blocks
#    every subsequent PR until fixed in main — even PRs that don't touch the failing file.
#    Always auto-fix with --write before committing rather than --check + manual fix.
npx --yes prettier@3.9.4 --write . --log-level warn   # auto-format any out-of-style files
npx --yes prettier@3.9.4 --check . --log-level warn   # verify clean — must return exit 0

# 4. Ruff (Python lint) — config in ruff.toml; runs as a CI gate (validate-marketplace Gate 9b)
#    and inside audit-gates.sh. Same whole-tree discipline as prettier: a ruff violation
#    landing in main can surface as a surprise CI failure on a later PR, so lint before pushing
#    any branch that touches .py files. (audit-gates Gate 9b _skip_or_fail's if ruff is absent.)
#    ⚠️ Use `python3 -m pip`, NOT bare `pip`. On a stock macOS toolchain `pip` is
#    `command not found` (only `pip3`/`python3 -m pip` exist), so the bare form fails
#    at the INSTALL step and the honest-looking conclusion — "ruff is unavailable here,
#    Gate 9b has to stay skipped" — is wrong. Verified 2026-08-12: bare `pip` → not
#    found; `python3 -m pip install --user ruff` → installed, `ruff check .` clean.
python3 -m pip install --quiet --user ruff   # bare `pip` is absent on stock macOS
ruff check .                                 # must return exit 0
#    If `ruff` is then not on PATH, it installed to the user scheme — either add
#    `$(python3 -m site --user-base)/bin` to PATH, or run it as `python3 -m ruff check .`

# 5. Audit every gate (the meta-test)
scripts/audit-gates.sh
# Proves each CI gate fails on a known-bad fixture AND passes on a known-good one.
# Required reading before adding or changing any CI step: docs/best-practices/ci-gate-audit.md
# NOTE: Gate 10 (actionlint) uses a checksum-pinned actionlint binary (rhysd/actionlint
#       v1.7.7, sha256-verified) — NO Docker. It resolves actionlint from PATH, a cached
#       /tmp/actionlint, or a pinned download. On a host with none of those AND no network,
#       it LOUD-skips locally ("THIS IS NOT A PASS" — a skip is not a pass); in CI an
#       unrunnable Gate 10 is a hard failure, never a silent skip.

# 6. Local install test (from a separate test project)
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

- **When a PR is required vs. not** — changes that ship inside `plugins/` (agents, skills, hooks, manifests, scripts, generated `dashboard.html`) or that touch CI / config / boundary files (`AGENTS.md`, `CLAUDE.md`, `.repo-layout.json`, `.github/`) go through a **PR**. Pure **documentation** under `docs/` — plan, design, proposal, and research write-ups, plus the rolling `docs/session-log.md` — commits **straight to `main`, no PR**. (Rationale: docs can't break a consumer's `/plugin marketplace update`, and the PR overhead slows the planning loop. The boundary is "could this change a consumer's installed plugin?" — if no, it's docs-only.)
- **Branches** — `feat/<plugin-name>-<slug>`, `fix/<plugin-name>-<slug>`, `chore/<slug>`.
- **Versioning** — bump the plugin's semver on every user-visible change.
- **Migration notes** — if the change could break a consumer's existing project on `/plugin marketplace update`, add a "Migration" section to the plugin's release notes.
- **Privacy** — the marketplace is private by default. Don't push to a public-readable remote without removing the `email` field from `marketplace.json` and `plugin.json`.

### Required status checks — never add `paths:` to a required workflow (added 2026-07-17)

The `main` ruleset requires three checks before a PR can merge: **Validate manifests and hooks** (`validate-marketplace.yml`), **Validate file paths against .repo-layout.json** (`validate-layout.yml`), and **Validate plugin and marketplace JSON Schemas** (`validate-schemas.yml`).

**None of these three may carry a `paths:` filter on its `pull_request` trigger.** GitHub: _"If a workflow is skipped due to path filtering, branch filtering or a commit message, then checks associated with that workflow will remain in a Pending state. A pull request that requires those checks to be successful will be blocked from merging"_ — and, explicitly, _"You should not use path or branch filtering to skip workflow runs if the workflow is required to pass before merging"_ ([troubleshooting required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks), retrieved 2026-07-17). A path filter on a required check doesn't cost coverage — it **hangs the PR forever**.

This is not hypothetical: `validate-schemas.yml` used to run only on manifest changes, so every docs-only PR (including the external-intake bot's `docs/staging/incoming/external/**` PRs) would have hung permanently the moment it became required. Both filters were removed when the checks were made required.

The filters were also the wrong shape independently: `validate-marketplace.yml`'s gates (`prettier --check .`, `ruff check .`, `audit-gates.sh`) are **whole-tree readers**, so no glob list can be correct — that list was patched three times (2026-05-31, 2026-06-20, 2026-07-06) and still missed `index.html` / `tests/**` / `.repo-layout.json`. An allow-list that fails **open** (the gate silently never runs) is the wrong shape for a whole-tree validator.

**If PR minutes ever need trimming, gate individual _steps_ with `if:` inside the job — never the workflow trigger.** A skipped *job* reports Success; a skipped *workflow* reports nothing at all. Adding a fourth required check? Check its trigger for `paths:` first.

> **Admin bypass is deliberate.** `RepositoryRole 5` (admin) keeps `bypass_mode: always` on the ruleset — the documented docs-straight-to-main flow and the `[skip ci]` artifact commits both depend on it, and it is the escape hatch if a required check ever does hang. The trade-off is real and accepted: **required checks do not bind an admin merge**, so `gh pr merge --auto` as an admin can still land ahead of a running check. If you want CI to gate your own merge, wait for green before merging — the ruleset will not do it for you.

## House rules

1. The `ravenclaude-core` plugin stays **domain-neutral**. Power Platform / finance / EdTech / Salesforce specifics live in their own plugins.
2. Plugin agents reference *plugin-internal* files only. They never hard-code paths inside a consumer's repo unless those paths are conventional (e.g. `docs/pm/raid-log.md`).
3. Before merging any plugin change, simulate: "what happens when a consumer runs `/plugin marketplace update`?" If the answer is "their project breaks," add a migration note.
4. Don't restate things the lint / CI / hook already enforces. They are the source of truth.
5. **Force-deleting a branch (`git branch -D`) is blocked by `guard-destructive.sh` — the sanctioned escape hatch is `scripts/archive-branch.sh`.** It tags the branch tip as `archive/<branch>-<timestamp>`, pushes the tag to origin (recoverable forever), writes an audit log under `.ravenclaude/runs/branch-archive/`, then deletes the local branch via the lower-level `git update-ref -d` primitive that the guard doesn't pattern-match. Requires `--reason` (one-line why) and accepts `--evidence` (PR number / decision doc / commit SHA). Full contract: [`plugins/ravenclaude-core/skills/branch-archive/SKILL.md`](plugins/ravenclaude-core/skills/branch-archive/SKILL.md). Do NOT bypass the guard with `git update-ref -d` outside this script — the script's preconditions are what make its use of that primitive sound.
   - **Scope — this is for *unmerged* / abandoned work, not merged branches.** A cleanly-merged branch needs no archive tag: its commits already live in `main`, and GitHub keeps them attached to the closed PR (restorable for ~90 days), so the tag is pure ceremony. Just **delete** it — turn on **Settings → Pull Requests → "Automatically delete head branches"** so merged branches clean themselves up on merge, and use GitHub's *Delete branch* button for any stragglers. Reserve `archive-branch.sh` for branches whose work is **not** in `main` (the tag is then the only recovery anchor). _Note: the script's tag push needs write access to non-branch refs; a restricted web-session git proxy can `403` that — one more reason to invoke it only when its recovery value is real, and to do merged-branch cleanup through GitHub instead._
6. **Agentic-Default Principle (cross-tool).** At a fork between handing the user a manual to-do and doing the automatable, already-authorized step itself, default to *doing it* — unless the user reserved that step (a stated preference always wins). Labor-allocation only; it overrides no gate (design check-ins, the tribunal's high-blast/irreversible defer, comfort-posture `ask`/`deny` + `security_deny`, irreversible-action confirmations). Full text: [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) § "Agentic-Default Principle".

## Accuracy discipline (cross-tool pointer)

Confident reasoning errors — a flawed belief about a tool/platform/API stated as fact with no uncertainty marker — are as dangerous as hallucinations and harder to catch. For any **consequential** claim (one that gates an irreversible action or gets written into a durable doc): **cite the this-session check that backs it inline, or mark it `[unverified — training knowledge]` and offer to verify before acting** — and never falsely concede (or dig in) when corrected; verify first. This applies to every agentic tool reading this file (Claude Code, GitHub Copilot CLI routing Claude/GPT/Grok, Cursor, Codex). Full protocol + the enforced complements: [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) § "Claim Grounding & Source Honesty".

**Before you CLAIM: say whether you are stating an OBSERVATION or an INFERENCE.** These are different axes from sourced-vs-unsourced, and conflating them is how a *correctly sourced* claim still turns out false. The case this rule was written from (2026-08-18): an agent stated *"the failure is caused by my change"* and *"the status page is correctly green"* as facts. Both rested on true, in-session observations. Both were conclusions **drawn from** those observations, and both were wrong. An **observation** is what the tool actually returned — quote it (`scripts/audit-gates.sh` → 703 pass, 0 fail). An **inference** is what you concluded from it — name the leap and what would falsify it ("exit 137, which I read as OOM `[unverified — I did not check the memory limit]`"). **The separating test:** could this sentence be false while every command you ran returned exactly what it returned? If yes, it is an inference. "X failed and my change touched X" is an observation; "X failed **because of** my change" is an inference until you have run the check that would have come out **differently** if the cause were something else. Causal claims are the highest-risk shape because they select the fix — attribute a cause you have not isolated and the next hour of work goes at the wrong thing, succeeding mechanically while solving nothing.

**Before you ACT on an under-specified request: ask ONE question.** When a request admits more than one plausible reading **and those readings lead to different work**, ask before starting rather than picking one silently and building on it. The cost is asymmetric — a question costs one turn; a wrong interpretation costs the work plus the unwinding, and it surfaces late. This is **not** a licence to interrogate: if one reading is clearly intended, proceed; if several readings converge on the same work, proceed and say in one clause which you took; ask only when the readings diverge, and always when the work is also expensive or hard to reverse. Whenever you do proceed under a reading, **state it in one clause** ("taking this as the portal build, not the CLI") — that clause is what lets the user correct you at turn 1 instead of turn 9.

> **Both of these rules are prose, and prose has no gate on the surface that matters.** No hook event carries a model's chat answer — hooks fire on tool calls, and an answer is not a tool call — so neither rule can be machine-enforced where the error usually lands. RavenClaude ships two narrow, advisory, opt-in complements: a `PostToolUse` lint over causal claims **written into `knowledge/`/`docs/` markdown**, and a `UserPromptSubmit` nudge on a narrow under-specified-prompt **shape**. Each is a sliver of its rule, each names what it misses, and neither is a control. Full scope table, including the measured gap where "because" is not mechanically separable into explanatory vs diagnostic: [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) § "Claim Grounding & Source Honesty".

**The same discipline governs the mirror-image error — falsely claiming you _can't_ do something** (the costlier one in practice: it silently abandons work and wastes a round-trip). A `command not found`, an HTTP 401/403, a deferred/MCP tool whose schema isn't loaded yet, or an "API doesn't support X" recalled from training is evidence about **one route**, **never** proof the capability is absent. Before any "I can't" / "that's not possible" / "no PR capability here" leaves an agent: (0) **read the actual error first and name its specific mechanical cause** — the status code *and* the body/stderr, not the headline. The cause **selects** the next move and is not interchangeable: an expired/missing-token `401` means re-authenticate then **retry the same route** (do not switch surfaces); an insufficient-scope `403` means a surface that already holds the scope; a `command not found` means the tool is absent *on this host*; an unloaded MCP schema means search/await it. Guessing the cause picks the wrong fix. (1) **load the sanctioned route first** — e.g. an MCP tool that shows as "still connecting" or name-only must be searched/awaited before you call it, and a missing-schema error is a not-loaded-yet signal, not an absent tool; (2) **enumerate ≥2 alternative paths and try the next-easiest** before reporting blocked; (3) report blockage only with the this-session checks you ran (`command + output`, or `file:line`) and the alternatives tried — same falsifiability bar as a positive claim. A wrong path is not a missing capability, and a CLI/API dead-end is not a verdict on the goal. _Worked example (this repo): creating a PR in the web/remote environment is **only** the GitHub MCP path — `gh`/`hub` are absent and the direct API 403s, so a session that concluded "can't create a PR" from those two dead-ends skipped step 1 (load the MCP tool) and step 2 (try the sanctioned route)._

## Naming a cause (the portable floor)

Projected from [`plugins/ravenclaude-core/knowledge/cause-taxonomy.md`](plugins/ravenclaude-core/knowledge/cause-taxonomy.md), which is the single source. Edit it there, not here.

A negative or empty result names ONE outcome. It never names its cause. The ritual, in three steps:

> (1) Before asserting a cause, list the classes that could produce **this exact output**.
> (2) Name the ONE discriminating probe that splits the top two.
> (3) Run it, then assert — and if you cannot run it, **write the cause as a hypothesis, not a fact.**

The classes, so step 1 has something to enumerate against:

| class | the output looked that way because… |
|---|---|
| **E** | the command did not run as intended — the shell never reached the subject, so nothing in the output is evidence about the subject at all |
| **F** | the read looked in the wrong place — the subject exists, but the target examined was not the one holding the answer |
| **G** | the answer was produced and then discarded — the subject answered correctly and the answer was lost between producer and reader |
| **H** | the subject genuinely has no such thing — the only class that licenses an absence conclusion, reachable only after E, F and G are excluded |
| **I** | indeterminate — the transport failed, which is evidence about reachability and never about the subject |

⛔ **`H1` — "the thing is absent" — is never available as the rank-1 answer.** It becomes credible only once E, F and G are excluded **and** a positive control on the same subsystem shows the probe was capable of returning something else. An empty result from a blind probe and an empty result from an empty subject are the same bytes; only the control separates them.

**The honest limit.** No hook on any host carries the model's chat text, so the place the confident inference is most often spoken is structurally out of reach. This is a behavioural rule with an enforced sliver beneath it — not the rule's enforcement.

What the sliver covers: a failed or empty Bash result is triaged after the fact, and a durable write or a remediating command that rests on an unsettled cause meets a gate. What it does not cover: a cause asserted in conversation and acted on in the same breath.
