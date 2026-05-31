# CLAUDE.md — RavenClaude (Claude Code addendum)

@AGENTS.md

This file is Claude Code's entry point. The `@AGENTS.md` import above pulls in the cross-tool conventions (setup, layout, style, testing, PR rules). Anything below is **Claude-Code-specific** and is not meaningful to other agentic tools.

---

## Remote-environment PR mechanics (Claude Code on the web) — added 2026-05-31

**In the web/remote execution environment, creating a PR is *always* the GitHub MCP path — never `gh`, never the GitHub API.** A prior session wrongly reported it "couldn't create a PR" after a CLI/API dead-end; this records the one working recipe so that never recurs.

The capability chain here has exactly one live path:

| Path | Works? | Why |
|---|---|---|
| `gh` / `hub` CLI | ❌ | Not installed in the container (`command -v gh` → not found) |
| Direct GitHub API (`curl api.github.com`) | ❌ | Network policy returns `403` |
| `git push` | ✅ (push only) | Remote is a **local git proxy** (`http://local_proxy@127.0.0.1:.../git/...`), not github.com — moves commits, can't open PRs |
| **GitHub MCP server** (`mcp__github__*`) | ✅ | The only sanctioned PR path |

**Working recipe:** `git push -u origin <branch>` → **ToolSearch** the deferred schema (`select:mcp__github__list_pull_requests,mcp__github__create_pull_request`) → `list_pull_requests` (dedupe) → `create_pull_request` with `draft:true`.

**Two traps that caused the false "can't create a PR":**

1. **`mcp__github__*` tools are deferred + lazy-loaded.** At session start the github MCP server may show as *"still connecting"* and its tools are name-only (no schema) — calling one directly fails with `InputValidationError`. **Run `ToolSearch` first** (it waits for connecting servers and loads the schema); only declare the capability absent if ToolSearch itself returns nothing. Never infer "tool doesn't exist" from a missing schema.
2. **A `gh: not found` or API `403` is the *wrong path*, not a missing capability.** Don't generalize a CLI/API failure into "no PR capability." The session-start capability hook says it plainly: *consult it before claiming you "can't" do something.*

**Owner/repo casing:** the git remote reads `mcorbett51090/RavenClaude` (capital R); the MCP scope is `mcorbett51090/ravenclaude` (lowercase). GitHub is case-insensitive, so either works — don't hard-fail on the mismatch.

## Plan-mode default

For non-trivial changes touching more than two files (or any manifest), enter plan mode first and present a Keep / Update / Deny structure before writing. This matches Matt's documented preference; Cursor/Codex users won't see this guidance and don't need to.

## Decision review — route yes/no decisions through the tribunal (added 2026-05-26)

**All yes/no decisions route through the tribunal (the Thing) before they reach Matt.** The `decision-review` skill convenes the same seats as command review on a yes/no question and returns `yes` / `no` / `defer`; the engine is [`plugins/ravenclaude-core/scripts/thing-decide.py`](plugins/ravenclaude-core/scripts/thing-decide.py). Full operating reference: [`docs/post-pr-decision-review.md`](docs/post-pr-decision-review.md).

**Real-time (every yes/no question):** before asking Matt a yes/no question, route it through the tribunal.

- A **binding** `yes`/`no` → act on it without pausing Matt.
- `defer` → ask Matt. The panel defers genuine preferences, low-confidence/split calls, and anything tagged high-blast.

**Enforced (added 2026-05-28), not just behavioral.** A `PreToolUse(AskUserQuestion)` hook — [`plugins/ravenclaude-core/hooks/route-decision-review.sh`](plugins/ravenclaude-core/hooks/route-decision-review.sh) — intercepts the `AskUserQuestion` tool so the real-time routing no longer depends on the model *remembering* to invoke the skill. It is **conservative + fail-safe**: it no-ops (a single `grep`, zero cost) unless `decision_review` is `advisory`/`binding`; it only auto-routes a **single, non-multiselect, binary yes/no-shaped** question (anything multi-option, multi-select, or non-yes/no → the human answers); on a **binding** `yes`/`no` it DENIES the prompt with the verdict + reasoning so the agent proceeds without paging Matt; **defer / advisory / high-blast / low-confidence / any engine error or missing `claude -p` → allow** (Matt answers). The engine ([`thing-decide.py`](plugins/ravenclaude-core/scripts/thing-decide.py)) still owns the safety envelope (off→defer, high-blast→defer, abstain/split/injection→defer) and Sága-logs every routed decision under `.ravenclaude/runs/thing/decisions/` — the refinement substrate. The `decision-review` skill remains the surface for the **post-PR retrospective** (no AskUserQuestion event there to intercept).

**High-blast / irreversible decisions never auto-resolve** (force-push, deletes, prod actions, the `security_deny` family) — always `defer` to Matt, regardless of mode. The mode knob `decision_review: off | advisory | binding` lives in `.ravenclaude/comfort-posture.yaml`; **off by default**, so nothing is auto-decided unless Matt opts in. The seats run via `claude -p`, so live verdicts need that available; absent it, the panel abstains and fails safe to `defer`.

**Post-PR retrospective:** after opening each PR, run the decision review over the PR's decisions — enumerate, classify _tribunal-eligible_ vs _needs-human_, route the eligible ones, and log the result as a PR comment.

Goal: shrink the decisions that interrupt Matt to only genuine-preference calls, and give the rule-derivable ones an auditable panel verdict instead of a silent autonomous choice.

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
