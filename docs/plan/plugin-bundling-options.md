# Strategic plan — Expand what RavenClaude plugins bundle

**Status:** strategic (what/why) — updated after Panel 1 review
**Branch:** `claude/plugin-bundling-options-QCDnG`
**Date:** 2026-06-05

> **Panel 1 corrections folded in (verified this session):**
>
> - **Fleet size is 64 plugins, not 44** (`ls -d plugins/*/ | wc -l` → 64).
> - **This is NOT greenfield.** `plugins/power-platform` already ships a bundled MCP
>   server (`powerbi-editor` → community `pbix-mcp`, MIT) in its `plugin.json`, and
>   `plugins/power-platform/CLAUDE.md` §9 / §9a / §9b is a dated, reasoned doctrine
>   that already answers open questions 2 & 3: **first-party → reference published
>   artifact + NOTICE/attribution + loud-but-non-fatal degrade; per-tenant/billed
>   → recommend-don't-bundle; SPN-secret community server → evaluate-first, never
>   default.** The build plan must *codify this existing precedent marketplace-wide*,
>   not re-derive it.
> - **Gate 25 already exists** (`scripts/audit-gates.sh:1698`) — a deterministic MCP
>   `allowed_servers` allowlist where a write verb from a non-listed server is a
>   pre-LLM DENY. Any auto-adding bundled server would collide with this perimeter;
>   the interaction must be designed before shipping, not after.
> - **Containment reality:** MCP servers, `bin/` executables, and monitors are
>   **subprocesses** that run *outside* every model-layer guard (`guard-destructive`,
>   the Thing tribunal, the permission deny-list see only the agent's own tool calls).
>   Only the OS/devcontainer boundary bounds them. The pilot must lead with the
>   lowest-execution-surface tier, not the highest-leverage one.

## Problem / why

RavenClaude ships 44 plugins, but every one uses only a narrow slice of what a
Claude Code plugin can actually bundle: `agents/`, `skills/`, `hooks/`,
`commands/`, plus plain bundled files (`knowledge/`, `best-practices/`,
`templates/`, `rules/`, and a few `*.json` data files). Verified against
`code.claude.com/docs/en/plugins-reference` (2026-06-05), the plugin format
supports several more component types that no RavenClaude plugin uses, and that
would let agents *act* rather than only *advise*:

- **MCP servers** (`.mcp.json` / `mcpServers` in `plugin.json`) — 0 uses in repo
- **LSP servers** (`.lsp.json`) — 0 uses
- **Monitors** (`monitors/monitors.json`) — 0 uses
- **`userConfig`** (prompt-at-enable config + sensitive secrets) — 0 uses
- **Output styles** (`output-styles/`) — 0 uses
- **`bin/` executables** (added to Bash `PATH` while enabled) — 0 uses
- **`settings.json` defaults** (`agent`, `subagentStatusLine`) — 0 uses
- **Themes** (`themes/`, experimental) — 0 uses

The "product" of this repo is the plugins. Today an agent in, say, the
power-platform plugin can *describe* how to call Dataverse but cannot call it;
it has knowledge, not tools. Closing that gap is the strategic opportunity.

## Goal

Decide which of these bundleable asset types are worth adopting, in what order,
and with what guardrails — then pilot the highest-leverage ones in 1-2 plugins
before any fleet-wide rollout. Output is a tactical build plan.

## Candidate bundleable assets (the "nice-to-have" catalog)

### Tier A — turns knowledge into capability (highest leverage)
1. **Bundled MCP servers.** Ship a `.mcp.json` (or `mcpServers` in `plugin.json`)
   so the plugin's agents get real tools on enable. Example: power-platform
   ships a Dataverse/Graph MCP server; api-engineering ships a Postman/OpenAPI
   server. Auto-starts on enable; appears as standard MCP tools.
2. **`userConfig` schema.** The secret-safe way to handle credentials/endpoints
   the env-var question raised. Plugin declares config; Claude Code prompts the
   consumer at enable-time (`sensitive: true` for secrets); values substitute via
   `${user_config.KEY}` into MCP/LSP/hook/monitor configs, and non-sensitive
   ones export as `CLAUDE_PLUGIN_OPTION_<KEY>`. Pairs with #1.

### Tier B — agent ergonomics / dev-loop
3. **`bin/` executables.** Put the repo's `scripts/*.{sh,py}` (thing-decide,
   audit-gates, knowledge-health, etc.) on the consumer's `PATH` so agents can
   invoke them by name without cloning the marketplace.
4. **LSP servers.** For code-heavy plugins (backend, frontend, terraform-iac),
   ship a language server so agents get diagnostics/hover/definitions.
5. **Monitors.** Background watchers (`monitors/monitors.json`) that tail logs /
   CI / build status and notify the agent — e.g. observability-sre shipping a
   monitor that surfaces failing health checks.

### Tier C — output & defaults
6. **`settings.json` defaults.** Set `agent` so enabling ravenclaude-core
   auto-activates Team Lead; set `subagentStatusLine`.
7. **Output styles.** Plugin-specific response formatting (e.g. a structured
   PR-review output style for code-reviewer).

### Tier D — richer bundled *files* agents already pattern after (no new component type)
8. **JSON data / lookup tables & JSON Schemas** — extend the existing
   `concepts.json` / `pattern-explanations.json` pattern; ship validation schemas
   agents can lint against.
9. **Reference datasets / fixtures / checklists** — golden examples agents copy.
10. **Prompt libraries** — extend prompt-pattern-library into shippable prompt
    packs per domain.
11. **`LICENSE` / `CHANGELOG.md`** — distributed, not loaded; marketplace hygiene.

## Constraints & guardrails (RavenClaude house rules)

- Any new top-level dir under `plugins/<plugin>/` MUST be added to
  `.repo-layout.json` `allowed_globs` or CI (`validate-layout.yml`) blocks the PR.
- New dirs must be declared in `plugin.json` and explained in the plugin's CLAUDE.md.
- `ravenclaude-core` stays domain-neutral — MCP servers with domain creds go in
  domain plugins, not core.
- Every user-visible change bumps the plugin's semver **and** the mirror in
  `marketplace.json` (CI fails on drift).
- Secrets never bundled as literals — `userConfig` (sensitive) only.
- Simulate `/plugin marketplace update` for every change; add migration notes if
  a consumer's project could break.
- Prettier-on-the-whole-tree + gate-audit meta-test before push.

## Open questions — answered after Panel 1

1. **Which tier to pilot first?** → **Tier D first** (richer bundled files — zero new
   component type, zero subprocess, fits the existing `concepts.json` schema+generator
   machinery), then **`userConfig` alone** (testable, secret-safe prerequisite), then
   **one *referenced* read-only MCP server in one domain plugin** with the Gate-25
   policy resolved first. Pilot in **1–2 plugins**, never fleet-wide. (Panel reordered
   the *pilot* by risk-adjusted leverage; the strategic *leverage* ranking is unchanged.)
2. **Ship server code in-repo vs. reference external?** → **Already decided in-repo by the
   power-platform precedent**: *third-party → reference the published artifact (pinned +
   checksum) + NOTICE attribution + graceful-degrade-on-absent; first-party (our own
   stdlib scripts) → bundle the code, versioned with plugin semver.* The trust boundary,
   not "in-repo vs external," is the seam. Codify as a marketplace rule + CI check.
3. **Domain plugins only, or a core MCP server?** → A domain-neutral core MCP server is
   sound **but v1 must be read-only/reporting only** (`knowledge-health`, layout-check,
   version-drift). A `thing-decide` MCP tool is **deferred** — wrapping the tribunal as a
   callable tool is a self-disable/bypass hazard (`xc.tribunal-self-disable`) and must be
   designed against that first. Core MCP server code is first-party → bundle it.
4. **How to test without a live backend?** → CI scope is **hermetic only**: JSON-validity
   + JSON-Schema conformance for `.mcp.json`/`.lsp.json`/`monitors.json`;
   `${user_config.KEY}` placeholder resolution + `sensitive:true` presence on secret
   fields; a "no literal secrets bundled" grep gate; a "third-party `mcpServers` entry has
   a NOTICE" gate. Every new gate needs its bad+good fixture pair in `audit-gates.sh`.
   **Live-backend behavior is explicitly out of CI scope** (manual/integration only).
5. **`userConfig` UX?** → Minimize prompts: only what a server genuinely can't default.
   **Secrets resolve to a *reference* (Key Vault URI, `op://`, env-var *name*) that the
   server dereferences at runtime — never the literal value**, and never into a
   `CLAUDE_PLUGIN_OPTION_*` export or a hook/`bin` command line. The `sensitive:true`
   safety claim is `[unverified — training knowledge]` until the on-disk persistence +
   transcript-flow behavior is checked against the live docs.

## Containment posture (added after Panel 1 — load-bearing)

Per `plugins/ravenclaude-core/CLAUDE.md` §"Containment posture" and
`knowledge/claude-code-permissions.md`: **none of the model-layer guards bound a
subprocess.** MCP servers, `bin/` executables, and monitors run outside
`guard-destructive.sh`, the Thing, and the permission deny-list — only the
devcontainer/worktree OS boundary contains them. Three hard invariants follow:

- **Install must remain side-effect-free.** MCP/LSP/monitor components are
  *declared-but-dormant* — never auto-start a backend-reaching server or a background
  process on `/plugin install`/enable. Any always-on behavior is opt-in via `userConfig`.
- **`bin/` is the highest-risk asset, not a "Tier B ergonomic."** PATH injection is
  arbitrary execution on enable and can *shadow* a consumer's own binaries. If adopted:
  namespace every binary (`rc-*`, never a system-tool name), CI-reject collision-prone
  names, checksum-pin, and gate changes behind `security-reviewer` + the Thing. **Prefer
  shipping these as skills the agent calls through the Bash tool** (so the guards *do* see
  the command) over PATH injection that bypasses them.
- **MCP tool *results* are untrusted input.** Backend/API responses flow into agent
  context with no sanitizer today (the tribunal's `_sanitize_reasoning` covers only its
  own reasoning path). Default bundled servers to **read-only verbs**; require least-
  privilege scopes declared in `plugin.json` + README; gate any write-capable server
  behind `security-reviewer`.

## Revised candidate disposition (after Panel 1)

| # | Candidate | Disposition |
|---|---|---|
| 8/9/10 | Tier D — richer JSON data, schemas, fixtures, prompt packs | **PILOT FIRST** — no new runtime, extends existing pattern |
| 2 | `userConfig` (references, not literal secrets) | **PILOT SECOND** — prerequisite for MCP; secret-safety claim still to verify |
| 1 | Bundled MCP server (read-only, *referenced*) | **PILOT THIRD, gated** — codify power-platform precedent; resolve Gate-25 interaction first |
| core MCP | Domain-neutral core MCP (read-only reporting) | **Candidate** — first-party, bundle code; defer tribunal-wrapping tools |
| 3 | `bin/` executables | **DEMOTE** — verify PATH claim; conflicts with live-clone model; prefer Bash-tool skills; namespace + checksum if ever adopted |
| 6 | `settings.json` `agent`/statusline defaults | **OPT-IN ONLY** — auto-activating an agent collides with the orchestrator-only-dispatch rule + mutates consumer config on update; CI-forbid touching `permissions.*` |
| 4 | LSP servers | **DEFER / likely CUT** — high maintenance, low current agent payoff |
| 5 | Monitors | **DEFER / likely CUT** — uncontained background egress; off-by-default opt-in if ever |
| 7 | Output styles | **DEFER / likely CUT** — cosmetic; agents already emit structured output via prompts |
| themes | Themes (experimental) | **CUT** — vanity |
| 11 | LICENSE / CHANGELOG | **Hygiene** — fine but unrelated to the "agents can act" thesis |

> Devil's-advocate dissent to keep on record: the strongest single move may be to
> **collapse to Tier D only** and answer the env-var question with plain README docs
> rather than `userConfig`, gating *any* MCP pilot behind a **logged consumer request**
> (demand-pull, not feature-FOMO). The build plan adopts a middle path — Tier D + a
> demand-gated, heavily-guarded MCP slice that *codifies the precedent already shipping*.
