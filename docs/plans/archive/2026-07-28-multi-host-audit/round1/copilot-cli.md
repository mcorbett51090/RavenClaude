# RavenClaude fitness audit — GitHub Copilot CLI lens

**Auditor:** Claude (Sonnet 5), reasoning ABOUT Copilot CLI — not running as Copilot. Every finding below
is tagged `[verified]` (read in-repo this session), `[docs-verified]` (fetched current GitHub docs this
session — URL given), or `[inferred]`. No unevidenced finding is included.

**Headline:** the Copilot bridge is architecturally well-designed on paper (correct handling of the
plugin-hooks bug #2540, a real envelope-translation adapter, a generated live-loading package) — but it
was built and tested against an **assumed tool-name vocabulary that mirrors Claude Code's own capitalized
names** (`Bash`, `Read`, `Write`, `Edit`, `MultiEdit`, `WebFetch`, `WebSearch`). GitHub's actual documented
Copilot CLI tool names are a **different, lowercase vocabulary** (`bash`, `view`, `create`, `edit`, `grep`,
`glob`, `web_fetch`, `ask_user`, `task`) that nothing in the adapter, the tribunal engine, the web-access
guard, or the agent-tools projector accounts for. That single mismatch is the root cause of the two most
severe findings (P0-1, P0-2) and shows up a third time in the repo's own test fixtures, which guessed a
*third*, still-wrong value (`"shell"`).

---

## P0 — broken or blocking for this host

### P0-1. The command-review tribunal ("the Thing") is a silent, unconditional no-op under Copilot CLI

**Evidence `[verified]`  + `[docs-verified]`:**
- `plugins/ravenclaude-core/hooks/thing-orchestrator.sh:113-116`:
  ```bash
  case "$tool_name" in
    Bash | Read | Write | Edit | MultiEdit | WebFetch | WebSearch | mcp__*) ;;
    *) exit 0 ;;
  esac
  ```
- Copilot CLI's actual native `toolName` values, per `docs.github.com/en/copilot/reference/hooks-configuration`
  (fetched this session): **`"bash"`, `"powershell"`, `"view"`, `"create"`, `"edit"`, `"grep"`, `"glob"`,
  `"web_fetch"`, `"ask_user"`, `"task"`** — none of which match the case statement's Claude-Code-cased
  patterns (bash's `case` is literal/case-sensitive; `"bash"` is not `"Bash"`, `"edit"` is not `"Edit"`).
- Consequence: **every** Copilot tool call falls to `*) exit 0` before the classifier
  (`thing-decision.py classify-payload`), the self-disable guard (section B.9.5), or the
  category-independent hard-rule screen for force-push / pipe-to-shell installs (section B.9.3) ever run.
  This is the marketplace's single most heavily-engineered safety mechanism (20+ dedicated `CLAUDE.md`
  milestones) and it is completely dark on this host.
- `plugins/ravenclaude-core/scripts/thing-decision.py:343` `classify_payload()`: `if tool_name == "Bash":`
  — the same literal-string dependency one layer down, so fixing only the case statement above is
  insufficient; the classifier itself needs the translated name too.
- Corroborating evidence that this was never resolved, only guessed at differently each time: the
  adapter's own Gate 20 test fixture (`plugins/ravenclaude-core/hooks/tests/test-gate20-adapter-diagnostics.sh:51`)
  hard-codes `toolName:"shell"` — a **third**, still-incorrect value, proving the implementer never
  verified the real one.

**Remedy:** normalize `tool_name` inside `copilot-hook-adapter.sh`'s `bash-pretool`/`file-pretool` modes
(map Copilot's `bash` to `Bash`, `view` to `Read`, `create`/`edit` to `Write`/`Edit`, `web_fetch` to
`WebFetch`, etc.) before building the Claude-shaped stdin JSON, so every downstream script (which already
expects Claude's names) works unmodified. Replace the `"shell"` guess in the Gate 20 fixture with the
docs-verified `"bash"`. Add a fixture that drives `thing-orchestrator.sh` itself (not just the adapter
I/O shape) through a real Copilot-shaped payload and asserts a force-push command is still hard-denied.

**Effort:** M (one clear seam to fix; needs re-verification across `thing-decision.py`,
`thing-concerns.py`, `guard-web-access.sh`, and the Saga-log `tool_input` shape assumptions).

---

### P0-2. `guard-web-access.sh` (the website allow/deny floor) is also fully inert under Copilot — same root cause

**Evidence `[verified]` + `[docs-verified]`:**
- `plugins/ravenclaude-core/hooks/guard-web-access.sh:63`: `[ "$tool" = "WebFetch" ] || exit 0`.
- Copilot's real web-fetch tool name is `"web_fetch"` (docs-verified above) — the comparison never
  matches, so the hook exits 0 on every call, including genuine web fetches.
- The plugin's own `CLAUDE.md` "Website access" milestone explicitly claims this guardrail is
  "usable by Claude when the plugin is installed **AND by any other CLI tool when the repo is cloned**" —
  that cross-tool claim is false for Copilot as shipped.

**Remedy:** same fix as P0-1 (adapter-side tool-name normalization); once `web_fetch` maps to `WebFetch`,
this hook works unmodified (it already parses `.tool_input.url` correctly and is otherwise sound). No
independent engineering needed beyond the shared normalization layer.

**Effort:** S, once P0-1's adapter fix lands (can ship in the same PR).

---

### P0-3. The generated `copilot/AGENTS.md` — the only carrier of the claim-grounding discipline, the dashboard-launch instructions, and Relay mode — never loads into a Copilot session by default

**Evidence `[verified]` + `[docs-verified]`:**
- `scripts/ravenclaude` contains **zero** occurrences of `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (verified via
  `grep -c`) — neither `cmd_install`, `cmd_setup`, nor `add_rc_alias` ever exports it or writes it into
  `~/.bashrc`. `cmd_install` also never writes a `.github/copilot-instructions.md` stub into the consumer
  repo (the pattern `knowledge/copilot-cli-customization.md:80` itself recommends: *"Consumers keep a
  short `.github/copilot-instructions.md` pointing at `AGENTS.md`"* — never actually done by the
  installer).
- Per GitHub's docs (`docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions`,
  fetched this session), `AGENTS.md` is discovered only in *"the repository root, the current working
  directory, intermediate directories between them... [or] directories listed in
  `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`."* A second fetch of the same page confirmed **no mention anywhere
  of `--plugin-dir`** as an AGENTS.md discovery path — matching `copilot-cli-customization.md`'s own
  honest `[verify-at-use]` flag on that exact point (`knowledge/copilot-cli-customization.md:81`).
- Consequence: the `rc` alias (`ravenclaude update && copilot --plugin-dir $COPILOT_PKG`, written by
  `add_rc_alias` in `scripts/ravenclaude:44-53`) launches Copilot **without** the env var set, so
  `copilot/AGENTS.md` — and with it the "Launch the comfort-posture dashboard" block and the "Relay mode"
  block — never enters context. The v0.158.0 milestone's stated goal (*"'open the dashboard' in a Copilot
  session Just Works"*, per `plugins/ravenclaude-core/CLAUDE.md` "`rc` launcher" section) does not hold
  for a default install.
- Confirmed the dashboard's own generator never mentions the variable either: `grep -c
  COPILOT_CUSTOM_INSTRUCTIONS_DIRS scripts/generate-dashboards.py` returns 0. The instructions on how to
  make Copilot load the discipline live **only** inside the file Copilot will not read without already
  knowing to set that variable — a closed loop.

**Remedy:** in `cmd_install`/`cmd_setup`, do the cheap, durable fix: write a 3-line
`.github/copilot-instructions.md` into the consumer repo pointing at the marketplace clone's
`copilot/AGENTS.md` (this loads automatically, no env var, no shell-restart dependency). Optionally also
add the `export COPILOT_CUSTOM_INSTRUCTIONS_DIRS=...` line to the same `~/.bashrc` block `add_rc_alias`
already writes, as a belt-and-suspenders second path.

**Effort:** S (a few lines in `scripts/ravenclaude`).

---

### P0-4. The least-privilege `tools:` allowlist is dropped when agents project to Copilot — every generated agent gets Copilot's default of ALL tools

**Evidence `[verified]`:**
- `scripts/generate-copilot-plugin.py:189-209` (`parse_name_description`) extracts **only** `name` +
  `description` from each canonical agent's frontmatter; the comment at lines 17-19 states this
  explicitly: *"everything else (tools, model, audience, works_with, scenarios, quickstart, ...) is
  intentionally dropped."*
- Confirmed empirically: `plugins/ravenclaude-core/copilot/agents/security-reviewer.agent.md` frontmatter
  is `name` + `description` only. The canonical `plugins/ravenclaude-core/agents/security-reviewer.md`
  declares `tools: Read, Grep, Glob, Bash, WebFetch` — **deliberately no Write/Edit**, per the
  root `AGENTS.md` house rule #9 (*"Declare an explicit `tools:` allowlist on every agent... the tool set
  is the only real bound on a dispatched subagent's blast radius"*), gated by
  `scripts/check-frontmatter.py`.
- Per `knowledge/copilot-cli-customization.md:30` (the repo's own docs-verified reference): *"optional
  `tools`; by default an agent has **all** tools — a `tools` spec only *restricts*."* So the security
  reviewer's Copilot projection — an agent whose canonical design deliberately withholds Write/Edit —
  gets unrestricted tool access (including write + arbitrary shell) the moment it's used as a Copilot
  custom agent.

**Remedy:** project `tools:` into the Copilot `.agent.md` frontmatter, translated through the same
tool-name vocabulary table P0-1/P0-2 need (Copilot's own tool names, not Claude's) — this finding shares
its root cause with P0-1/P0-2. Gate it with the existing `--check` freshness test so a future agent that
adds a `tools:` restriction doesn't silently lose it in translation.

**Effort:** S/M (mostly the shared translation table; verify Copilot's `.agent.md` `tools:` value syntax
before shipping).

---

## P1 — significant gap; the host is materially underserved

### P1-1. The Copilot hook wiring in `scripts/ravenclaude` is hand-maintained and has drifted badly from the canonical `hooks.json` — no freshness gate catches it

**Evidence `[verified]`:** the canonical `plugins/ravenclaude-core/hooks/hooks.json` registers 19 distinct
hook scripts across 6 event types. The Copilot installer's embedded generator
(`scripts/ravenclaude:184-216`, the Python heredoc inside `cmd_install`) wires only 10: `capability-orientation.sh`
(SessionStart); `guard-destructive.sh`, `thing-orchestrator.sh`, `runaway-brake.sh`, `enforce-layout.sh`
(PreToolUse); `format-on-write.sh`, `claim-grounding-lint.sh` (PostToolUse); `dod-gate.sh`,
`remind-tests.sh`, `stream-session-close.sh` (Stop); `stream-prompt-attribute.sh` (UserPromptSubmit).

**Missing entirely from the Copilot wiring:** `guard-recursive-spawn.sh`, `delegation-nudge.sh`,
`mark-web-domain-seen.sh`, `worktree-guard.sh` (both `register` and `check` modes),
`guard-web-access.sh` (separately dead per P0-2, but also simply never registered), `route-decision-review.sh`,
`reapply-posture.sh`, `ensure-default-mode.sh`, and — most notably — the two **brand-new (v0.210.1)**
Muninn hooks `thing-denial-kb-sync.sh`/`thing-denial-kb-recall.sh`, and the **brand-new (v0.216.0)**
`dashboard-autostart.sh`. Every one of these shipped in the canonical plugin after (or independent of) the
last time the installer's embedded hook list was updated, and nothing enforces that the two lists stay in
sync — unlike the agents projection, which has a real `--check` freshness gate
(`generate-copilot-plugin.py --check`).

**Remedy:** derive the Copilot `.github/hooks/ravenclaude.json` from the canonical `hooks.json`
programmatically (a projection function analogous to `generate-copilot-plugin.py`'s agent projection),
with a `--check` gate. Where a hook's *event* has no Copilot equivalent (e.g. `SubagentStart` for
`agent-dispatch-evaluator.sh`), the projector should skip it explicitly and say so, not silently.

**Effort:** M.

---

### P1-2. Copilot's hooks.json has no per-tool `matcher` — undocumented in the repo's own conventions, and it's the structural reason P0-1/P0-2 exist

**Evidence `[docs-verified]` + `[verified]`:** the hooks-configuration example in
`knowledge/copilot-cli-customization.md` section 4 (itself sourced from the docs, re-confirmed by this
session's fetch of `docs.github.com/en/copilot/reference/hooks-configuration`) shows `"hooks": {
"preToolUse": [ {...} ] }` — a flat array with **no tool-scoping field**. Claude Code's `hooks.json`, by
contrast, nests every hook block under an explicit `"matcher": "WebFetch"` (see
`plugins/ravenclaude-core/hooks/hooks.json:37,90`). This asymmetry is never stated in
`copilot-cli-customization.md`'s "How RavenClaude maps onto each surface" table (section 6), even though
it is exactly the blind spot behind P0-1 and P0-2: every registered Copilot preToolUse hook fires on
**every** tool call, and the tool-name filter has to live inside the invoked script — which is precisely
where the wrong string comparisons (P0-1, P0-2) were shipped.

**Remedy:** add one explicit line to section 4 of `copilot-cli-customization.md` stating Copilot has no
per-tool hook matcher, and add it to whatever pre-merge checklist governs new hooks, so the next hook
author doesn't repeat the P0-1/P0-2 mistake.

**Effort:** S (doc-only), but high leverage — this is the guardrail against the *next* instance of P0-1's
defect class.

---

### P1-3. FORGE and Wireframe — two flagship recent features — have zero Copilot-specific bridging, and the plugin's own advertised description overclaims for this host

**Evidence `[verified]`:** `plugins/ravenclaude-core/copilot/plugin.json`'s `description` field states:
*"Slash commands: /init-agent-ready, /wrap, /set-posture, /dashboard, /forge, /wireframe,
/reset-plugin-cache."* But `plugins/ravenclaude-core/CLAUDE.md`'s own Copilot bridge section says plainly:
*"Slash commands (`/set-posture`, `/wrap`) don't port (Copilot CLI has no user slash commands yet)."*
Only `/dashboard` gets a dedicated Copilot-specific bridging block (`DASHBOARD_BLOCK` in
`scripts/generate-copilot-plugin.py:62-102`) telling the host the real equivalent (`bin/rc dashboard`).
`/forge` (the `forge-pipeline` skill) and `/wireframe` (the `wireframe` skill) get **no** equivalent
block — under Copilot, invoking either relies entirely on Copilot's own description-based skill
inference, with no explicit "ask for FORGE / the wireframe studio" guidance anywhere in the generated
package.

**Remedy:** either soften `copilot/plugin.json`'s description to not claim these are slash commands under
Copilot, or add short bridging blocks for `forge-pipeline` and `wireframe` to `generate-copilot-plugin.py`,
mirroring the existing `DASHBOARD_BLOCK` pattern.

**Effort:** S/M.

---

## P2 — clear-value improvement

### P2-1. The in-flight FORGE plan for a dashboard "Host & context" page is the right fix for Copilot instruction-precedence discoverability, and it is not built yet

**Evidence `[verified]`:** `docs/plans/2026-07-28-prompt-engineering-learn/plan.md` (Deliverables table D3,
Phase 4) designs a Control-destination `#/host-context` page that would tell a Copilot operator *which
CLI this is, which files it reads in order, what belongs in each, and what is actually wired* — directly
answering this audit's own framing question. Confirmed **not yet built**: a scan across
`scripts/serve-dashboards.py` for every `/__*` route shows no `/__host` endpoint exists, and
`git log --oneline -5` on the current branch (`feat/ravenclaude-core-0.216.0`) shows only the planning
docs landed (`138b597a docs(plans): land the ... FORGE plan + decision record`) — no implementation
commits. Until this ships, the precedence table in `knowledge/copilot-cli-customization.md` is reachable
only inside the marketplace clone, never inside a typical consumer repo, and never inside the dashboard
itself.

**Remedy:** prioritize landing Phases 1-7 of the existing plan; the plan's own red-team already caught
real bugs (Gate 32's hyphen-blind endpoint regex, an env-name-enumeration leak risk) before build, so the
design work is sound — this is a "finish what's planned" item, not a "design something new" item.

**Effort:** L (the plan itself estimates multiple phases + 2 new gates), but already scoped and
owner-approved for the ratchet cost.

---

### P2-2. Muninn (the Thing-denial knowledge base) is doubly dead under Copilot — its source data can never be written

**Evidence `[verified]`:** `thing-denial-kb-sync.sh`/`thing-denial-kb-recall.sh` (v0.210.1) derive their
entire value from the Saga audit logs the tribunal writes at `.ravenclaude/runs/thing/`. Given P0-1 (the
tribunal never fires under Copilot) **and** P1-1 (the sync/recall hooks aren't even wired into the
Copilot installer), Muninn cannot function on this host in either direction — there is nothing to sync,
and nothing would surface it if there were.

**Remedy:** falls out automatically once P0-1 and P1-1 are fixed; no independent engineering needed. Worth
a regression test once both land, confirming a denial recorded under a real (fixed) Copilot session
actually reaches the KB.

**Effort:** — (consequence of P0-1 + P1-1, not separately actionable).

---

## P3 — nit / polish

### P3-1. The Learn-tab concept card overstates hook portability with no honesty hedge

**Evidence `[verified]`:** `plugins/ravenclaude-core/knowledge/concepts/copilot-bridge.md:20` teaches, as
settled fact with no `[verify-at-use]` marker: *"a hook adapter translates the I/O envelopes so the
*unmodified* hook scripts run under Copilot."* Given P0-1/P0-2, that claim is materially false for the
tool-name-keyed hooks — the envelope shape translates correctly, but the tool-name *values* inside it do
not, so the "unmodified scripts run" framing is optimistic. This is the dashboard's own teaching surface
asserting exactly the kind of unhedged capability claim the marketplace's own Claim-Grounding & Source
Honesty protocol (`plugins/ravenclaude-core/CLAUDE.md`) says should carry a marker.

**Remedy:** once P0-1/P0-2 are fixed this becomes true and needs no change; until then, add a
`last_verified` caveat or soften "unmodified... run under Copilot" to "unmodified... run under Copilot for
hooks that don't branch on the calling tool's name."

**Effort:** S.

---

## Summary table

| # | Sev | Title | Effort |
|---|---|---|---|
| 1 | P0 | Tribunal (the Thing) is a silent no-op under Copilot — tool-name mismatch | M |
| 2 | P0 | `guard-web-access.sh` also fully inert — same root cause | S |
| 3 | P0 | Generated `copilot/AGENTS.md` never loads by default (no env var, no `.github/copilot-instructions.md`) | S |
| 4 | P0 | Least-privilege `tools:` dropped in Copilot agent projection — every agent gets ALL tools | S/M |
| 5 | P1 | Copilot hook wiring hand-maintained, drifted — 12+ hooks unwired incl. Muninn + dashboard-autostart | M |
| 6 | P1 | No-matcher hooks.json undocumented — the structural cause of #1/#2 | S |
| 7 | P1 | FORGE/Wireframe have no Copilot bridging; plugin.json overclaims slash-command support | S/M |
| 8 | P2 | Planned "Host & context" dashboard page not yet built | L |
| 9 | P2 | Muninn doubly dead under Copilot (consequence of #1 + #5) | — |
| 10 | P3 | Learn-tab card overstates hook portability | S |
