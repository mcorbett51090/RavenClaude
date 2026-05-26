# CLAUDE.md — RavenClaude (Claude Code addendum)

@AGENTS.md

This file is Claude Code's entry point. The `@AGENTS.md` import above pulls in the cross-tool conventions (setup, layout, style, testing, PR rules). Anything below is **Claude-Code-specific** and is not meaningful to other agentic tools.

---

## Plan-mode default

For non-trivial changes touching more than two files (or any manifest), enter plan mode first and present a Keep / Update / Deny structure before writing. This matches Matt's documented preference; Cursor/Codex users won't see this guidance and don't need to.

## Post-PR decision review (added 2026-05-26)

After opening each PR, run a **decision review** before considering the task done — this is a standing step, not an optional extra:

1. **Enumerate** every yes/no (binary) decision made during the work — both the ones surfaced to Matt and the ones taken autonomously.
2. **Classify** each as _tribunal-eligible_ (a defensible answer is derivable from rules, CI gates, repo conventions, or facts) or _needs-human_ (a genuine preference / taste / risk-appetite call).
3. **Route the tribunal-eligible ones through the tribunal (the Thing)** for a verdict, and record the outcome. The Thing currently adjudicates shell commands only, so live decision-adjudication is staged — see [`docs/post-pr-decision-review.md`](docs/post-pr-decision-review.md) for the classification rubric, the seat-routing map, and the engine extension that makes it real.
4. **Log** the review as a comment on the PR (the per-PR artifact).

Goal: shrink the set of decisions that interrupt Matt to only genuine-preference calls, and give the rule-derivable ones an auditable second opinion instead of a silent autonomous choice.

## Memory references

User-scoped memory lives under your Claude Code home (e.g. `~/.claude/projects/<encoded-project-path>/memory/` on Linux/macOS or the equivalent on Windows). `MEMORY.md` is the index inside that directory. Update it when something durable about the user, project, or working style changes.

## Marketplace-dev hooks

Two registration paths exist, **both required**:

1. **Plugin canonical** — `plugins/ravenclaude-core/hooks/hooks.json` registers all of its hooks with `${CLAUDE_PLUGIN_ROOT}` paths. This is the path consumers get when they `/plugin install ravenclaude-core@ravenclaude`. The hooks fire from the installed-plugin cache (e.g. `~/.claude/plugins/cache/ravenclaude/ravenclaude-core/<version>/hooks/...`), not from the repo on disk.
2. **Marketplace dev** — `.claude/settings.json` registers the same hooks with `${CLAUDE_PROJECT_DIR}` paths against the working tree. This is what fires when you're editing the marketplace itself, because **Claude Code does NOT auto-load plugins from filesystem discovery** — plugins only load via `/plugin install` (verified against [Create plugins](https://code.claude.com/docs/en/plugins) and [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) docs, 2026-05). Without this block, edits in the working tree would fire the *installed* (possibly stale) plugin's hooks, not the version under development.

Both wirings call idempotent scripts, but the two paths *do* fire on the same events when both are active. This is intentional during dev. To migrate to plugin-only, the maintainer would need to either (a) launch Claude Code with `claude --plugin-dir ./plugins/ravenclaude-core` (per the Create-plugins doc), or (b) run `/plugin marketplace update ravenclaude` after every commit and accept the cached-copy lag. The dev-mirror block is the pragmatic choice.

If you need a marketplace-only hook (i.e., one that should NOT ship to consumers), add it to `.claude/settings.json` under `hooks` separately from the dev-mirror block above.

## Layout enforcement (Claude Code path)

The plugin's `hooks/enforce-layout.sh` runs `PreToolUse` on `Write|Edit|MultiEdit`. It reads `.repo-layout.json` at the project root, matches the target path against `allowed_globs`, and denies off-pattern writes with a suggested correct location. The hook silently allows everything if `.repo-layout.json` is absent — so consumers who install the plugin without setting up a layout manifest are not surprised.

The matching CI workflow `.github/workflows/validate-layout.yml` is the cross-tool backstop (catches direct human commits, Cursor/Codex/Aider edits, and any case where the hook didn't fire).

Why both: Claude Code issue [#23478](https://github.com/anthropics/claude-code/issues/23478) confirms that path-scoped rule files (`paths:` frontmatter) load only on Read, not on Write. They cannot prevent off-pattern file *creation*. The hook (in-loop, Claude-only) plus the CI (universal backstop) is the supported enforcement pattern in 2026.

## Slash commands shipped by the plugin

After installing the plugin in any project, consumers get:

- `/init-agent-ready` — guided setup: creates `AGENTS.md`, `CLAUDE.md`, `.repo-layout.json`, and optionally a CI workflow tailored to the consumer's repo type (application / library / monorepo / docs / data / IaC).

The command is defined in `plugins/ravenclaude-core/commands/init-agent-ready.md` and writes from templates in `plugins/ravenclaude-core/templates/agent-ready-repo/`.
