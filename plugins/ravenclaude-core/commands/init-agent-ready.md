---
description: Set up agent-readable boundary files (AGENTS.md + CLAUDE.md + .repo-layout.json + optional CI) tailored to this repo's purpose.
---

You are helping the user make this repository agent-readable. Your goal is to create a small set of boundary files that both humans and agentic AI tools (Claude Code, Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, Windsurf) can use to navigate and contribute correctly.

## What you will produce

1. **`AGENTS.md`** — cross-tool agent instructions following the published [AGENTS.md spec](https://agents.md/) (Setup, Code style, Testing, PR conventions). This is the canonical agent-readable doc; every major coding-AI tool reads it.
2. **`CLAUDE.md`** — Claude-Code-specific addendum that imports AGENTS.md via `@AGENTS.md`, imports the local team-constitution copy via `@docs/team-constitution.md`, and adds anything Claude-only (plan-mode preferences, memory pointers, etc.). Stays under 100 lines.
3. **`docs/team-constitution.md`** — a **literal copy** of `${CLAUDE_PLUGIN_ROOT}/CLAUDE.md` (the team constitution) into the consumer's repo. This is what gives the consumer-side Team Lead the team roster, dispatch playbook, and Structured Output Protocol on first session open. Copying at init time (rather than `@`-importing from the plugin cache) makes the import portable across users and survives `/plugin marketplace update`.
4. **`.repo-layout.json`** — machine-readable allow-list of file path globs. Both the layout-enforcement hook (in Claude Code) and an optional CI workflow read this file to block off-pattern file creation.
5. **(optional) `.github/workflows/validate-layout.yml`** — CI backstop that fails PRs adding files outside the allow-list. Recommended for any repo with a GitHub remote.
6. **(optional) CI-hygiene scaffold** — `.prettierrc.json`, `.prettierignore`, and `scripts/audit-gates.sh` (the gate-audit scaffold defined by [`audit-ci-gates`](../skills/audit-ci-gates/SKILL.md)). Recommended for any repo that ships CI workflows meant to enforce properties — see [`docs/best-practices/ci-gate-audit.md`](https://github.com/mcorbett51090/RavenClaude/blob/main/docs/best-practices/ci-gate-audit.md) in the marketplace for the rule this scaffold encodes.
7. **(optional) Portable quality gates** — `.github/workflows/validate-quality.yml` (a language-agnostic LINT / FORMAT / SYNTAX CI: Prettier format-check, **Ruff** Python lint+format, shell `bash -n`, JSON/YAML config-parse, and checksum-pinned actionlint) plus `ruff.toml` (a conservative starting ruleset). This is the installable version of the gates RavenClaude runs on itself — each step is a real gate (fails on bad input, passes on good). Recommended for any repo with a GitHub remote; tailor by deleting jobs for languages you don't use.

## How to proceed

### Step 1 — Detect what's already here

Inspect the working directory. Note which of these already exist: `AGENTS.md`, `CLAUDE.md`, `.repo-layout.json`, `.github/workflows/validate-layout.yml`. Also inspect for repo-type signals:

- `package.json` / `tsconfig.json` → Node application or library
- `pyproject.toml` / `setup.py` / `requirements.txt` → Python project
- `go.mod` → Go project
- `Cargo.toml` → Rust project
- `pom.xml` / `build.gradle` → Java
- Multiple `package.json` under `packages/` or `apps/` → monorepo
- `mkdocs.yml` / `docusaurus.config.js` / large `docs/` → documentation site
- `terraform/`, `*.tf`, `Pulumi.yaml` → infrastructure-as-code
- `notebooks/`, `dvc.yaml`, `mlflow/` → data / ML pipeline
- `.claude-plugin/marketplace.json` → Claude Code plugin marketplace (this is RavenClaude itself or similar)

### Step 2 — Ask the user four questions (use AskUserQuestion)

Ask in one batch:

1. **What kind of repo is this?** Options: application, library, monorepo, documentation, data/ML pipeline, infrastructure-as-code, plugin marketplace, other. Pre-select the most likely option based on your detection in Step 1.
2. **Should we add the CI workflow `.github/workflows/validate-layout.yml`?** Options: yes (recommended) / no.
3. **Should we add the portable quality gates (`.github/workflows/validate-quality.yml` + `ruff.toml`)?** Options: yes (recommended) / no. This is the lint/format/syntax CI — Prettier, Ruff (Python), shell `bash -n`, config-parse, actionlint. Mention the conservative-ruleset-first discipline: the first `ruff check --fix . && ruff format .` will surface and fix a lot on a never-linted codebase, so run it once and commit before turning the gate on.
4. **Should we add the CI-hygiene scaffold (`.prettierrc.json`, `.prettierignore`, `scripts/audit-gates.sh`)?** Options: yes (recommended if your repo has CI workflows that enforce properties) / no. Adding `audit-gates.sh` as a scaffold ships with one example fixture — fill in real gates (incl. fixtures for the quality gates above) as you wire CI.
5. **For any boundary file that already exists, what should we do?** Options: skip / overwrite / merge intelligently. Only ask this if at least one already exists.

### Step 3 — Plan the files and show Keep / Update / Deny

Generate the proposed content for each file in memory. Show the user a brief plan:

```
About to create / update:
- AGENTS.md           (NEW, ~80 lines)
- CLAUDE.md           (NEW, ~30 lines)
- .repo-layout.json   (NEW, allow-list tailored to <repo-type>)
- .github/workflows/validate-layout.yml   (NEW, optional CI gate)
- .github/workflows/validate-quality.yml  (NEW, optional lint/format/syntax gates)
- ruff.toml                                (NEW, optional — Python repos only)
```

Then ask the user via AskUserQuestion: Keep all / Update specific files / Deny.

### Step 4 — Write the files

After approval, write each file using the Write tool. Tailor content per repo type.

**Special handling for `docs/team-constitution.md`:** instead of writing template content, copy the plugin constitution verbatim. Use the Read tool on `${CLAUDE_PLUGIN_ROOT}/CLAUDE.md`, then Write the same content to `docs/team-constitution.md` in the consumer's repo, prefixed with a one-line note:

```markdown
<!-- Copied from ravenclaude-core@<version> at init time via /init-agent-ready.
     Re-run /init-agent-ready after `/plugin marketplace update ravenclaude` to refresh this file.
     Edits to this file are local to this repo. -->
```

This pin-at-init approach is intentional. `@`-importing from the plugin cache (e.g. `~/.claude/plugins/cache/...`) is not portable across users; a local copy works for every contributor regardless of their Claude Code install layout.


**AGENTS.md** must include sections (in this order):
- Title and 1-2 sentence repo purpose
- Setup commands (install, build, run) — derive from the detected ecosystem
- Repo layout — short paragraph + directory tree
- Code style — 3-6 bullets, language-appropriate
- Testing instructions — exact commands
- PR conventions — branch names, commit style, review rules
- Layout & boundary rules — point at `.repo-layout.json` and the hook + CI as enforcement; cite Claude Code issue [#23478](https://github.com/anthropics/claude-code/issues/23478) explaining why path-scoped rule files alone can't block file creation

Keep AGENTS.md under 200 lines. Frontier models reliably follow only ~150-200 instructions.

**CLAUDE.md** is a 20-40 line Claude-only addendum that starts with `@AGENTS.md`. Include only what's Claude-specific: plan-mode default, memory location, any plugin-distributed hooks active in this project.

**`.repo-layout.json`** schema:
```json
{
  "description": "Allow-list of file path globs for <repo-name>.",
  "schema_version": 1,
  "allowed_globs": ["..."],
  "forbidden_globs": [],
  "suggestions": {}
}
```

Tailor `allowed_globs` per repo type. Use these starter sets:

- **application (Node)**: `package.json`, `tsconfig*.json`, `*.md`, `LICENSE`, `.gitignore`, `src/**`, `tests/**`, `public/**`, `scripts/**`, `.github/**`, `docs/**`, `.claude/**`
- **library**: `package.json` (or `pyproject.toml` etc.), `*.md`, `LICENSE`, `src/**`, `tests/**`, `examples/**`, `docs/**`, `.github/**`, `.claude/**`
- **monorepo**: `*.md`, `LICENSE`, `package.json`, `pnpm-workspace.yaml` (or equivalent), `apps/**`, `packages/**`, `tools/**`, `docs/**`, `.github/**`, `.claude/**`
- **documentation**: `*.md`, `mkdocs.yml` (or `docusaurus.config.js`), `docs/**`, `assets/**`, `static/**`, `.github/**`, `.claude/**`
- **data/ML**: `*.md`, `pyproject.toml`, `data/**`, `notebooks/**`, `src/**`, `models/**`, `pipelines/**`, `tests/**`, `.github/**`, `.claude/**`
- **infrastructure-as-code**: `*.md`, `*.tf`, `terraform/**`, `modules/**`, `environments/**`, `policies/**`, `scripts/**`, `.github/**`, `.claude/**`
- **plugin marketplace**: see RavenClaude's own `.repo-layout.json` as the canonical example.

Always include `AGENTS.md`, `CLAUDE.md`, `README.md`, `.repo-layout.json`, and `docs/team-constitution.md` in `allowed_globs`.

**`.github/workflows/validate-layout.yml`** (only if user approved): copy the structure from RavenClaude's own workflow at `${CLAUDE_PLUGIN_ROOT}/templates/agent-ready-repo/validate-layout.yml.template` — adjust nothing except header comments.

**Portable quality gates** (only if user approved): copy two files from `${CLAUDE_PLUGIN_ROOT}/templates/agent-ready-repo/`:

- `validate-quality.yml.template` → `.github/workflows/validate-quality.yml` (the lint/format/syntax CI). **Tailor it:** delete the Ruff job if there's no Python, the Prettier job if there's no JS/TS/JSON/YAML/CSS, etc. — keep only the gates that apply.
- `ruff.toml.template` → `ruff.toml` (the conservative Python ruleset) — only if the repo has Python. Then tell the user to run `ruff check --fix . && ruff format .` once, review + commit the result, and only then rely on the gate (the first lint of a never-linted codebase surfaces a lot). Add `ruff.toml` to `.repo-layout.json` `allowed_globs`.

When the quality workflow is added, point the user at the [`audit-ci-gates`](../skills/audit-ci-gates/SKILL.md) skill to add a fail-on-bad/pass-on-good fixture per gate in `scripts/audit-gates.sh`, then uncomment the meta-gate step in `validate-quality.yml`.

**CI-hygiene scaffold** (only if user approved): copy three files from `${CLAUDE_PLUGIN_ROOT}/templates/agent-ready-repo/`:

- `.prettierrc.json.template` → `.prettierrc.json` (sensible defaults, markdown line-wrap preserved).
- `.prettierignore.template` → `.prettierignore` (markdown excluded by default — see the file's comments).
- `audit-gates.sh.template` → `scripts/audit-gates.sh` (the gate-audit scaffold). After writing, make it executable: `chmod +x scripts/audit-gates.sh`. Add `.prettierrc.json` and `scripts/**` to `.repo-layout.json` `allowed_globs` (the latter is already in the default starter set).

### Step 5 — Confirm and explain

After writing, summarize for the user:

```
✓ Created N files
- AGENTS.md
- CLAUDE.md
- .repo-layout.json
- .github/workflows/validate-layout.yml (optional)

What now:
1. The plugin's enforce-layout hook is already active — it will read .repo-layout.json on every Write/Edit and block off-pattern paths.
2. If you push this branch, the CI workflow runs on PRs.
3. Edit .repo-layout.json whenever you add a new top-level directory.
4. AGENTS.md is read by Cursor / Codex / Aider / Copilot natively; CLAUDE.md is Claude-Code-only.

Next: review the generated files and adjust the Setup / Testing / Code style sections to match your project's exact commands.
```

## Constraints

- Never overwrite an existing file without explicit user approval in Step 2.
- Keep AGENTS.md under 200 lines. Cut content if it grows past that.
- Don't restate things a linter / formatter / CI already enforces — that just wastes the model's instruction budget.
- Don't invent setup commands you haven't verified. If you can't tell what the test command is, leave a clear `TODO: confirm` placeholder.
- The user is in charge. If they push back on any choice, adjust and re-show the plan.
