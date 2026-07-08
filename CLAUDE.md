# CLAUDE.md — RavenClaude (Claude Code addendum)

@AGENTS.md

This file is Claude Code's entry point. The `@AGENTS.md` import above pulls in the cross-tool conventions (setup, layout, style, testing, PR rules). Anything below is **Claude-Code-specific** and is not meaningful to other agentic tools.

---

## Remote-environment PR mechanics (Claude Code on the web) — the environment VARIES across sessions; **probe, don't assume** (re-verified 2026-07-06)

> **This capability has flip-flopped across sessions — treat the table below as "last observed," not a constant.** 2026-06-02 saw `gh` working; 2026-06-11 saw it absent + the direct API 403ing (MCP-only); **2026-07-06 saw `gh` + the token working again** (created *and* auto-merged PRs #568 and #570 with `gh pr create` / `gh pr merge --auto --squash`, while the github MCP server was *not* connected). The durable rule is the two enduring lessons below: **probe each route this session before concluding anything** — a stale row here has been wrong in both directions.

> **CI auto-run also varies (note added 2026-06-22; updated 2026-07-06).** In some remote sessions a `git push` updated the PR head **without** Actions creating a run — the PR then had *no checks* and "merge when green" never fired (detect + re-trigger per [`docs/remote-ci-autotrigger-runbook.md`](docs/remote-ci-autotrigger-runbook.md); a successful `workflow_dispatch` disproves "Actions minutes exhausted", as on PR #452). **But on 2026-07-06 CI auto-ran normally** on both PRs (Validate Layout / Manifests / Schemas fired on the `pull_request` event within seconds). So after every push: **confirm a run exists for the current head** (`gh pr checks <n>` / `gh run list --branch <b>`, or the MCP `get_check_runs`); if none, re-trigger via `workflow_dispatch`; if present, just wait for green. Don't assume either way.

**Don't generalize a failure on one route into "can't create a PR" — and don't assume a past dead-end still holds.** A prior session (2026-05-31) wrongly reported it "couldn't create a PR" after a CLI/API dead-end; that lesson stands. Its equally-real counter-lesson: the routes below have **changed between sessions**, so re-probe every time rather than trusting a stale row (2026-07-06 found `gh` working after 2026-06-11 found it absent).

The capability chain (last verified 2026-07-06):

| Path | Works? (last seen) | This-session check |
|---|---|---|
| **`gh` CLI** | ✅ 2026-07-06 (❌ on 2026-06-11) | `command -v gh` → `/usr/bin/gh`; `gh auth status` → logged in as `mcorbett51090` via `GITHUB_TOKEN`. Created + auto-merged PRs #568/#570. |
| **Direct GitHub API** (`curl api.github.com`) | ✅ 2026-07-06 (❌ on 2026-06-11) | `GITHUB_TOKEN` **is set** this session; `GET /repos/…` → `HTTP 200` (a `ghu_` app-installation token — `x-oauth-scopes` empty, `x-accepted-oauth-scopes: repo`). |
| **GitHub MCP server** (`mcp__github__*`) | ⚠️ not connected 2026-07-06 | `ToolSearch` for `github`/`pull_request` returned **no** github tools this session (the "dynamic client registration" auth path failed earlier). Was the sanctioned path on 2026-06-11. |
| `git push` | ✅ (push only) | Remote is a local git proxy (`http://local_proxy@127.0.0.1:<port>/git/mcorbett51090/RavenClaude`) forwarding to github.com. |

**Recommended order (2026-07-06):** **probe first**, then use whatever works this session. On 2026-07-06 the fastest path was `gh`: `gh pr create --base main --head <branch> --title … --body-file …`, then `gh pr merge <n> --auto --squash` (arms auto-merge — it lands the instant CI is green), prefixing `GH_TOKEN="${GITHUB_TOKEN}"` if `gh` isn't already authed. If `gh` is absent/403s this session, fall back to the **GitHub MCP server** (`mcp__github__create_pull_request`, loaded via `ToolSearch` first). Don't hard-code either as "the" path — the two `❌`→`✅` flips above are why.

**The two enduring lessons (path-agnostic) — these are why this section still exists:**

1. **MCP tools are deferred + lazy-loaded.** At session start the github MCP server may show as *"still connecting"* and its tools are name-only (no schema) — calling one directly fails with `InputValidationError`. Run `ToolSearch` first (it waits for connecting servers and loads the schema); only declare the capability absent if ToolSearch itself returns nothing. Never infer "tool doesn't exist" from a missing schema. This trap is permanent — it'll still bite when the right path *is* MCP.
2. **A `command not found`, a `401`/`403`, or a missing schema is evidence about ONE route, not the goal.** Don't generalize a CLI/API failure into "no PR capability." The session-start capability hook says it plainly: *consult it before claiming you "can't" do something.* Read the actual error first, name the specific mechanical cause (401 vs 403 vs not-found vs not-loaded-yet), then pick the next-easiest path. The cause selects the fix and is not interchangeable.

**Owner/repo casing:** the git remote reads `mcorbett51090/RavenClaude` (capital R); the MCP scope is `mcorbett51090/ravenclaude` (lowercase). GitHub is case-insensitive, so either works — don't hard-fail on the mismatch.

## Plan-mode default

For non-trivial changes touching more than two files (or any manifest), enter plan mode first and present a Keep / Update / Deny structure before writing. This matches Matt's documented preference; Cursor/Codex users won't see this guidance and don't need to.

## Agentic-Default Principle

When a step is automatable and already authorized, the default is that the agent *does it*, not that you're handed a to-do — unless you've said you want that step manually (a stated preference always wins). Labor-allocation only: it bypasses no gate (design check-ins, the tribunal's high-blast defer, comfort-posture `ask`/`deny`, and irreversible-action confirmations all still pause). Full text: [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) § "Agentic-Default Principle".

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

### Notification channel (marketplace-only) — added 2026-06-23

This repo's scheduled routines run unattended on Claude Code on the web, where the **managed `PushNotification` tool can be absent** (it is, in this environment) — so a routine that surfaces something worth your attention has no built-in egress. The notification channel fills that gap:

- **Hook:** a `Notification`-event entry in `.claude/settings.json` (marketplace-only — deliberately **not** in any plugin's `hooks.json`, so it never ships to consumers and never changes a consumer's behavior) calls [`scripts/notify.sh`](scripts/notify.sh).
- **What it does (both sinks fail-safe, always exit 0):**
  1. **Always** appends one JSON line to `.ravenclaude/runs/notifications/YYYY-MM-DD.jsonl` (gitignored — durable in-session record, never a working-tree diff).
  2. **Opt-in:** if `RAVENCLAUDE_NOTIFY_WEBHOOK` is set, it POSTs `{"text":"<message>"}` to that URL (Slack / Mattermost / Google-Chat-style incoming webhook). Unset → that step no-ops, so the default is secret-free and side-effect-free.
- **To receive phone/desktop pushes:** set `RAVENCLAUDE_NOTIFY_WEBHOOK` to your channel's incoming-webhook URL (in the environment config or `.claude/settings.json` `env`). The script never logs the URL.
- **Ad-hoc use from a routine:** `scripts/notify.sh "one-line summary"` (or pipe a message on stdin) delivers through the same channel.

The curl is bounded (`--connect-timeout 5 -m 10`) so a slow/blocked sink can never stall a session, and a missing `curl`/`jq` or network failure is swallowed. **This is the stand-in for `PushNotification`; if a managed push tool is present in a given environment, prefer it and treat this as the durable fallback record.**

## Layout enforcement (Claude Code path)

The plugin's `hooks/enforce-layout.sh` runs `PreToolUse` on `Write|Edit|MultiEdit`. It reads `.repo-layout.json` at the project root, matches the target path against `allowed_globs`, and denies off-pattern writes with a suggested correct location. The hook silently allows everything if `.repo-layout.json` is absent — so consumers who install the plugin without setting up a layout manifest are not surprised.

The matching CI workflow `.github/workflows/validate-layout.yml` is the cross-tool backstop (catches direct human commits, Cursor/Codex/Aider edits, and any case where the hook didn't fire).

Why both: Claude Code issue [#23478](https://github.com/anthropics/claude-code/issues/23478) confirms that path-scoped rule files (`paths:` frontmatter) load only on Read, not on Write. They cannot prevent off-pattern file *creation*. The hook (in-loop, Claude-only) plus the CI (universal backstop) is the supported enforcement pattern in 2026.

## Slash commands shipped by the plugin

After installing the plugin in any project, consumers get:

- `/init-agent-ready` — guided setup: creates `AGENTS.md`, `CLAUDE.md`, `.repo-layout.json`, and optionally a CI workflow tailored to the consumer's repo type (application / library / monorepo / docs / data / IaC).

The command is defined in `plugins/ravenclaude-core/commands/init-agent-ready.md` and writes from templates in `plugins/ravenclaude-core/templates/agent-ready-repo/`.
