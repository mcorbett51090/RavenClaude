# Multi-host audit — Round 1 — lens: **Claude Code (the native host)**

**Question:** Is RavenClaude — and specifically its dashboard — fit to serve an agent orchestrating under
Claude Code? Where is it lacking, and what should be BUILT or MODIFIED?

**Date:** 2026-07-28 · **Auditor lens:** prompt/agent-harness engineering · **Repo:** `/Users/matthewcorbett/RavenClaude`
**Honesty:** every finding is tagged `[verified]` (read/executed this session) or `[inferred]`. No finding
ships without `file:line` or a reproduced measurement.

---

## Verdict in one paragraph

RavenClaude is *authored for* Claude Code better than any marketplace I have read: the hook surface is
complete (6 events), the gates have real teeth, and the epistemic protocols are load-bearing. **The
dashboard is where the fit breaks.** Its single Claude-Code-only runtime panel — Mímir / `#/mimir`,
"what does Claude Code know about *this* session?" — is reading the wrong schema and the wrong end of the
file, and as a result it renders a **confidently wrong** answer to the one question that determines whether
the operator's guardrails are in effect at all. Everything else is a gap; that one is a defect. Beyond it,
three first-class Claude Code surfaces have **no representation whatsoever** — MCP servers, subagent
dispatch, and the Claude-Code-only `monitors/` component — and the consumer-facing `dashboard.html` points
at a portal consumers do not possess.

The pending `prompt-engineering-learn` plan **helps this host materially** (a `#/host-context` page with a
liveness-bound host detector is exactly the missing orientation surface, and its detection contract is the
most honest thing in the dashboard). But it is teaching + detection only: it adds **zero** runtime state,
and — the sharpest irony — it *reuses `_read_mimir` as a trusted oracle* while imposing on its own new page
the very honesty rule that `_read_mimir`'s panel currently violates.

**Counts:** P0 = 2 · P1 = 4 · P2 = 3 · P3 = 1

---

## The reproduction that anchors the two P0s

Run this session against the live transcript for this very project
(`~/.claude/projects/-Users-matthewcorbett-RavenClaude/3bdbf43d-b433-42aa-8e59-db05d0ac0406.jsonl`),
emulating `_read_mimir` exactly:

```
file bytes            : 14,582,415
bytes read (cap)      :      51,200   (0.35% of file)
events in head slice  : 12
MIMIR last_used model : None          <- TRUTH: message.model = "claude-opus-4-8"
MIMIR assistant count : 0             <- TRUTH: 2,395 assistant events
MIMIR output_tokens   : 0             <- TRUTH: message.usage.output_tokens present on every one
MIMIR permission_mode : default       <- TRUTH: 325 permission-mode events, default -> acceptEdits -> auto
```

Corpus-wide: **877 of 1,006** `.jsonl` transcripts under `~/.claude/projects/` exceed the 50 KiB cap
(`find ~/.claude/projects -name '*.jsonl' -size +50k | wc -l`). The cap is not an edge case; it is the
normal case, and this session's own transcript exceeds it by **285×**.

---

# Findings, ranked by severity

---

## P0-1 — Mímir reads top-level `model`/`usage`; Claude Code nests them under `message` `[verified]`

**Evidence**

- `plugins/ravenclaude-core/scripts/serve-dashboards.py:1145-1147` — `m = ev.get("model")` (last-used model)
- `plugins/ravenclaude-core/scripts/serve-dashboards.py:1180-1184` — `usage = ev.get("usage")` → `output_tokens`
- Real assistant-event shape, dumped this session: top-level keys are
  `['attributionPlugin','attributionSkill','cwd','entrypoint','gitBranch','isSidechain','message',…]` —
  **no top-level `model`, no top-level `usage`.** They live at `ev["message"]["model"]`
  (`"claude-opus-4-8"`) and `ev["message"]["usage"]`
  (`{input_tokens, cache_creation_input_tokens, cache_read_input_tokens, output_tokens}`).
- **Why every gate passes anyway:** `plugins/ravenclaude-core/hooks/tests/test-mimir-reader.py:108` writes
  the *flat* shape — `{"type":"assistant","model":"claude-opus-4-8","usage":{"output_tokens":42}}` — and
  `scripts/check-mimir-render.mjs:187` feeds a synthetic payload
  (`model: {configured, last_used}`) that never touches the reader. **The reader and its gate agree with
  each other and disagree with Claude Code.** This is the repo's own documented "silent green defect"
  shape, landing on the repo's own Claude-Code-only panel.

**Consequence for the operator:** "Last-used model" is permanently `—` and every *Recent project sessions*
row reports `0` output tokens and an event count truncated to whatever fits in 50 KiB — on every real
session. An orchestrating agent cannot use this panel to answer "which model am I on / what has this run
cost", which is the panel's entire job.

**Remedy (build)**

1. Read `ev["message"]["model"]` and `ev["message"]["usage"]`, keeping the flat form as a fallback so the
   existing fixtures do not silently start failing for the wrong reason.
2. Sum the **four** usage fields, not just `output_tokens` —
   `cache_read_input_tokens` is the number an orchestrator actually needs (it is the prompt-caching
   signal), and it is already on disk.
3. **Re-derive the fixtures from a redacted slice of a real transcript**, and add one assertion to
   `test-mimir-reader.py` that the fixture event contains a `message` wrapper — so the *fixture* can never
   again drift from the platform it claims to model.
4. Apply byte-identically to **both** `serve-dashboards.py` copies (`_read_*` prefix ⇒
   `check-dashboard-server-parity.py` `_BODY_DIFF_PREFIXES` enforces it for free).

**Effort: S**

---

## P0-2 — "Permission mode" reports the session's *opening* mode as current — and says `default` while this session is in `auto` `[verified]`

**Evidence**

- `plugins/ravenclaude-core/scripts/serve-dashboards.py:1148-1151`:

  ```python
  if first_perm_mode is None and ev.get("type") == "permission-mode":
      pm = ev.get("permissionMode")
  ```

  Takes the **first** event in forward order. Contrast `last_model` two lines above (`:1145-1147`), which
  *overwrites* — so the same loop deliberately keeps the newest model and deliberately keeps the **oldest**
  permission mode.
- `_mimir_iter_jsonl_bounded` (`:901-916`) does `fh.read(cap_bytes)` from offset 0 — the **head** of the
  file — with `_MIMIR_JSONL_READ_CAP = 50 * 1024` at `:850`.
- Measured (above): Mímir yields `permission_mode = "default"`; the file's 325 `permission-mode` events run
  `default → default → acceptEdits → acceptEdits → auto → auto → …`.
- Rendered bare at `scripts/generate-dashboards.py:11556` — `["Permission mode", s.permission_mode]` — with
  **no staleness pill**, while the *activity* card 25 lines below (`:11581-11587`) carries a **mandatory**
  `as of` pill (documented as contract RM4). The honesty discipline this repo is proud of is applied to the
  low-stakes card and omitted from the high-stakes one.

**Why this is P0 and not P1.** `plugins/ravenclaude-core/hooks/ensure-default-mode.sh` exists for exactly
one reason, stated in its own header: in `acceptEdits`/`bypassPermissions` the comfort-posture allow/ask/deny
rules "are partially or fully ignored." The dashboard is where an operator checks posture. It is currently
telling a Claude Code operator that the guardrails are live (`default`) while the session has moved to a
mode in which they are not. That is not a missing feature; it is the surface actively vouching for a safety
state that does not hold.

**Remedy (build)**

1. **Scan the tail for `permission-mode`.** Seek to `max(0, size - cap)`, drop the torn first line, take the
   **last** `permission-mode` event. (Keep the head read for anything genuinely session-opening.)
2. Render `plan` as a first-class value (see P2-1).
3. **Add the disclosure the sibling card already has**: an `as of <timestamp>` pill plus a
   `scanned N KiB of M MiB` note whenever the read was capped. If the tail scan cannot establish a mode,
   render the honest in-process pill (`mimirInProcessPill`, `generate-dashboards.py:11528-11533`) — never a
   value.
4. **Derive the verdict, do not print the string.** Cross-read `.claude/settings.json`
   `permissions.defaultMode` (pinned to `"default"` by
   `plugins/ravenclaude-core/scripts/apply-comfort-posture.py:872-880`) and render
   **"posture rules LIVE" / "posture rules BYPASSED"** as the headline, with the raw mode as the subtitle.
   That is the sentence the operator needs; the enum is trivia.
5. **Gate it with a fixture whose mode changes *after* the cap** — a fixture that flips at byte 60,000 and
   asserts the reader reports the flipped value. That fixture is the whole teeth; without it this recurs.

**Effort: M**

---

## P1-1 — No MCP surface anywhere in the dashboard, though 6 shipped plugins declare MCP servers and the repo calls MCP lazy-loading a *permanent* trap `[verified]`

**Evidence**

- `plugins/ravenclaude-core/scripts/serve-dashboards.py` — **zero** MCP references (grep, case-insensitive).
- `scripts/generate-dashboards.py` — the only hits are `:2300`, `:2468`, `:2481`, `:2872`, all of which are
  the tribunal's `mcp_tools` **permission-review category**, not server state.
- Six shipped plugins declare servers: `plugins/{aws-cloud,microsoft-fabric,generative-web-media,
  microsoft-365-copilot,power-platform,microsoft-graph}/.claude-plugin/plugin.json` → `"mcpServers": {…}`.
- `CLAUDE.md:30` names this the *permanent* trap: *"MCP tools are deferred + lazy-loaded… calling one
  directly fails with `InputValidationError`. Run `ToolSearch` first… Never infer 'tool doesn't exist' from
  a missing schema. This trap is permanent."* The repo knows MCP is the #1 recurring capability confusion
  and gives the operator no surface for it.

**Consequence:** an agent that hits `InputValidationError` on an MCP tool has no dashboard answer to "is
this server even declared here, and at what scope?" — it must go read six `plugin.json` files.

**Remedy (build)** — an **MCP card**, ideally seated on the plan's new `#/host-context` page:

- Rows from three disk sources: installed plugins' `plugin.json` `mcpServers`, a project `.mcp.json` (absent
  here — `ls .mcp.json` → not found), and `~/.claude.json` if present.
- Columns: **server name · scope (plugin / project / user) · declared by**.
- An honest in-process pill for connection state: *"whether a server is connected is in-process only — run
  `/mcp`"* — the same `mimirInProcessPill` pattern, never a fabricated green dot.
- **Leak floor:** names and scopes only. Never `args`, never `env` values, never a resolved absolute path —
  `index.html` is a published artifact, so the plan's §6.4 closed-allow-list discipline binds here too.

**Effort: M**

---

## P1-2 — Subagent activity is invisible, though the attribution data is already sitting in the transcript `[verified]`

**Evidence**

- `plugins/ravenclaude-core/hooks/hooks.json:149-159` registers `SubagentStart` →
  `agent-dispatch-evaluator.sh`, which shadow-logs to `.ravenclaude/runs/dispatch-eval/`.
- **No reader consumes it.** grep for `dispatch-eval` / `SubagentStart` across
  `scripts/generate-dashboards.py` returns exactly one hit — `:918`, its *exclusion* reason inside
  `_PIPELINE_EXCLUDED_HOOKS`. There is no `/__dispatch` endpoint in either `serve-dashboards.py`.
- The transcript already carries per-event `attributionSkill`, `attributionPlugin` and `isSidechain`
  (dumped this session). Measured on one session: **688** events attributed to
  `ravenclaude-core:forge-pipeline`, 29 to `claude-in-chrome`, 11 to `artifact-design`, 10 to
  `ravenclaude-core:decision-review`. grep confirms **none of those three field names appears in either
  `serve-dashboards.py` or `generate-dashboards.py`.**

**Consequence:** Claude Code's orchestration primitive is the subagent, and this marketplace's entire thesis
is a Team Lead fanning work out to specialists. The Activity destination shows *runs* and *worktrees*
(Sleipnir) — never *who was dispatched, by what, how often*. An orchestrating agent auditing its own fan-out
has nowhere to look.

**Remedy (build)**

1. **Cheap and immediate:** extend `_read_mimir`'s recent-session rows with a derived
   `by_skill` / `by_plugin` count from `attributionSkill` / `attributionPlugin`. Derived labels + integers
   only — the exact no-egress contract `_read_streams` already follows. Zero new endpoint.
2. **Fuller:** a `/__dispatch` reader over `.ravenclaude/runs/dispatch-eval/`, active only when
   `.ravenclaude/dispatch-config.json` has `enabled: true`; honest empty state otherwise (it defaults off).
3. Surface both on **Activity**, next to the run feed, where an operator already looks for "what is the
   agent doing".

**Effort: M**

---

## P1-3 — The consumer-facing dashboard points at a portal consumers do not have `[verified]`

**Evidence**

- `scripts/generate-dashboards.py:13350-13353` (the Plugin-variables intro, shipped into
  `dashboard.html`): *"For the full reference — agents, scenarios, skills, hooks, templates,
  best-practices — open the plugin in the portal's **Marketplace** section."*
- The portal is `index.html` at the **marketplace repo root**. `ls plugins/ravenclaude-core/index.html` →
  **absent**; the bundled server serves the plugin dir and redirects `/` → `/dashboard.html`. A consumer who
  runs `/plugin install ravenclaude-core@ravenclaude` and then `/dashboard` gets `dashboard.html` and no
  portal.
- `docs/dashboard-removed-routes.md` retires `#/team` with *"Catalog — the specialist roster now lives in
  the marketplace."* The roster genuinely exists only in the portal generator
  (`scripts/generate-index-dashboard.py:517-558`, `_scan_agents`).
- Compounding: `AGENTS.md:63-70` makes the **~15K agent-description budget** explicitly *the consumer's*
  job (*"Enable only what you need… budget before you enable, not after the warning fires"*) — and then the
  consumer's dashboard ships no agent or plugin inventory to budget against.

**Remedy (build/modify)** — pick one, (a) preferred:

- **(a)** Ship a **roster island** into `dashboard.html`: agent name + one-line description + owning plugin
  + per-plugin agent count, emitted inside `<script type="application/json">`. `html.parser` treats script
  content as CDATA, so this is **+0 counted DOM elements** — the same islanding trick `panel-learn` and
  `panel-commands` already use (`scripts/generate-dashboards.py:190-213`). Gate 132's zero-slack ratchet is
  untouched. This directly serves the budget decision the repo asks consumers to make.
- **(b)** One-line honesty fix: change the copy to name a destination a consumer actually has — Claude
  Code's own `/plugin` → **Discover** tab, which surfaces per-plugin **Context cost** and the **Will
  install** inventory natively (already cited at `AGENTS.md:70`).

**Effort: S (b) / M (a)**

---

## P1-4 — Claude-Code-only components have no "is this wired here?" surface — sharpest for `monitors/` `[verified]`

**Evidence**

- `plugins/ravenclaude-core/.claude-plugin/plugin.json` → `"experimental": {"monitors":
  "./monitors/monitors.json"}`; `plugins/ravenclaude-core/monitors/monitors.json` registers
  `run-state-monitor` (`when: "on-skill-invoke:spawn-team"`). The plugin `CLAUDE.md` describes it as
  **Claude-Code-only** — the *push* complement the Heimdall/Víðarr pull readers structurally cannot provide.
- It appears **nowhere** in `scripts/generate-dashboards.py`. And unlike the deliberately-suppressed hooks
  it is not even *excludable*: `_PIPELINE_EXCLUDED_HOOKS` (`:912-928`) and Gate 133
  (`scripts/check-pipeline-lanes.py`) reconcile against `hooks/hooks.json` only, so a monitor is outside the
  drift gate's field of view entirely.
- Same class, other components: `hooks/copilot-hook-adapter.sh` implements modes `bash-pretool` (`:63`),
  `file-pretool` (`:130`), `sessionstart` (`:141`), `posttool` (`:152`), `userpromptsubmit` (`:159`),
  `stop` (`:171`) — **no `subagentstart` mode**, so `agent-dispatch-evaluator.sh` is Claude-Code-only; and
  all eight `plugins/ravenclaude-core/commands/*.md` slash commands are Claude-Code-only (correctly
  disclosed in the Commands surface at `scripts/generate-dashboards.py:1755-1762`, which is the good
  precedent to copy).

**Remedy (build)** — a **"What's wired on this host"** card. This is a natural fit for the plan's D3
`#/host-context` page and costs little there:

- Rows generated from the real manifests: hooks (`hooks/hooks.json`, grouped by event), monitors
  (`plugin.json` `experimental.monitors`), slash commands (`commands/`).
- Each row carries a **Claude Code only / portable** badge, **derived mechanically** from the adapter's mode
  list rather than hand-asserted — so the badge cannot rot when a mode is added.
- **Booleans and fixed labels only** (no paths), per the plan's §6.4 leak floor.
- **Extend Gate 133** to reconcile `experimental.monitors` as well as `hooks.json`, so a future monitor
  cannot land unsurfaced and unexcluded.

**Effort: M**

---

## P2-1 — Plan mode has no representation beyond the (stale) permission-mode string `[verified]`

**Evidence** — `permission_mode` is the sole carrier
(`plugins/ravenclaude-core/scripts/serve-dashboards.py:1073`, `:1148-1155`; rendered
`scripts/generate-dashboards.py:11556`). The reader's own honest-unreachable list (`:1090`) names
`effort_dial`, `plan_tier`, `status_live_cache` — **plan mode is not on it**, so its absence reads as *"not
applicable"* rather than *"not surfaced"*. And `hooks/ensure-default-mode.sh` case-matches only
`acceptEdits | bypassPermissions`, never `plan`.

Plan mode is a first-class Claude Code permission mode and the one the repo's own `CLAUDE.md:35-37`
("Plan-mode default") tells the agent to enter for any change touching >2 files or a manifest. The dashboard
cannot show whether that instruction is being honoured.

**Remedy** — once P0-2's tail-scan lands, render `plan` explicitly with its meaning
(*"agent is planning — no writes will be attempted"*), and if the tail scan cannot establish it, add
`plan_mode` to the `unreachable` list so the silence is *declared* rather than ambiguous.
**Effort: S**

---

## P2-2 — The pending plan adds no runtime state, and applies its own honesty rule only to its new page `[verified]`

**Evidence**

- `docs/plans/2026-07-28-prompt-engineering-learn/plan.md` §6.2 (`:475-500`) is binding and excellent:
  *"a wrong verdict is worse than no verdict"* → verdict bound to **session liveness**, an
  always-visible inheritance caveat, an **age-qualified headline** (*"Claude Code (detected when this server
  started, N min ago)"*), and an **inverse must-fail** in Gate 152. That is a higher honesty bar than any
  existing dashboard panel meets.
- The same plan greps clean for the host's runtime surfaces: `mcp` appears once (`:456`, Copilot's
  `COPILOT_HOME`), `subagent` never, `permission mode` never; `_read_mimir` appears only at `:483` and
  `:490` — where the plan **reuses it as a trusted reachability oracle** for `_session_is_live()`.
- So the plan imposes on `/__host` precisely the rule that `panel-mimir` is currently breaking (P0-2), while
  taking a dependency on that same reader.

**Assessment:** this is **not** a reason to block. The plan is additive, budget-honest (§5.2's byte-level
markup contract is exemplary), and D3 + D1's `directing-the-agent` / `using-plugins-well` /
`prompt-agentic-craft` concepts are genuinely the right teaching for this host.

**Remedy (modify the plan)** — add one phase, or a same-branch follow-up, that applies §6.2's rule
*retroactively* to `panel-mimir` (P0-1 + P0-2). This is not scope creep: `_session_is_live()` is specified
to reuse `_read_mimir`'s reachability path, so fixing the cap and the schema **strengthens the plan's own
detector** and removes a dependency on a reader that is currently wrong about the file it reads.
**Effort: S to amend · M to execute**

---

## P2-3 — Land D8's Gate 142 extension regardless of whether D3 slips `[verified]`

**Evidence** — `plan.md` §6.3 items 4-6 (`:520-528`) document three real, currently-unenforced holes:
Gate 32's `_ENDPOINT_RE = r"/__\w+"` (`scripts/check-dashboard-server-parity.py:46`) is **hyphen-blind**
*and* one-directional; `serve-dashboards.py`'s own NOTE that *"any NEW data-returning GET endpoint MUST call
`self._local_request_ok()` first"* is **enforced by nothing**; and `do_HEAD` needs an allow-list entry or
HEAD 404s while GET 200s.

**Why it belongs to this lens:** the served dashboard's two launch paths are both Claude-Code-only — the
`/dashboard` slash command and the new `dashboard_autostart` SessionStart hook (`hooks/hooks.json:191-196`).
Its exposure surface is disproportionately this host's.

**Remedy** — ship D8 (Gate 142 iterating **every** `/__*` route the server dispatches and asserting 403 on an
evil `Origin`) as an independent commit. One loop, real teeth, and it covers every future endpoint including
the ones this audit asks for (`/__mcp`, `/__dispatch`). **Effort: S**

---

## P3-1 — `dashboard_autostart` shipped with no dashboard control `[verified]`

**Evidence** — `hooks/hooks.json:191-196` registers `dashboard-autostart.sh` (v0.216.0); the plugin
`CLAUDE.md` v0.216.0 entry states plainly *"No DOM control ships — Gate 132 is at zero slack and a visible
toggle costs an owner-approved ratchet raise."* So on the host where the dashboard **is** the intended front
door, its own autostart knob is YAML-only.

**Remedy** — none new: this is exactly the plan's **D4** (`plan.md:53-56`, §5.2 — a measured +6:
`div` + `h3` + `select` + 3 `option`). Noted here only to record that D4 is a genuine Claude-Code-facing
gap-closer, not budget spend on polish. **Ship D4.** **Effort: S (already planned)**

---

# Does the pending plan serve this host well?

**Yes, partially — and it is worth shipping as-is plus one amendment.**

| Plan item | Claude Code verdict |
|---|---|
| **D3 `#/host-context` + `/__host`** | **The single most valuable thing in the plan for this host.** Liveness-bound, age-qualified, refuses a confident wrong verdict (§6.2). It is also the natural seat for the MCP card (P1-1) and the wired-components card (P1-4). |
| **D1's 13 concepts** | Well-targeted: `directing-the-agent` (instruction-file precedence + *a path referenced inside an auto-loaded file is not itself auto-loaded*), `using-plugins-well` (the ~15K budget), `prompt-agentic-craft`, `structured-output-in-practice`. This is the teaching this host needs. |
| **§6.4 leak floor** | Correct and necessary — `index.html` is published, so a closed literal allow-list of env **NAMES**, booleans-not-paths, is the right posture. Reuse it for every card this audit proposes. |
| **D8 gate hardening** | Ship independently (P2-3). |
| **D4 autostart control** | Ship (P3-1). |
| **What it does not do** | Adds **zero** runtime state. Does not touch Mímir, MCP, subagents, plan mode, or permission mode. Its host detector is one-sided by design (§6.1) and will legitimately render *"cannot determine"* on the repo's own reuse-first launch paths — mitigated by §6.2's second probe, but the readout an orchestrating agent actually wants (*"are my posture rules live right now?"*) remains out of scope. |

**Amendment recommended:** one phase applying §6.2's own honesty rule retroactively to `panel-mimir`
(P0-1 + P0-2), on the grounds that `_session_is_live()` already depends on `_read_mimir`.

---

# What to build, in order

| # | Build / modify | Severity | Effort |
|---|---|---|---|
| 1 | `_read_mimir` reads `message.model` / `message.usage`; fixtures re-derived from a real transcript | P0-1 | S |
| 2 | Tail-scan `permission-mode`; staleness pill; derived **"posture rules LIVE / BYPASSED"** headline; post-cap fixture | P0-2 | M |
| 3 | **MCP card** — declared servers + scope + honest `/mcp` in-process pill | P1-1 | M |
| 4 | Subagent visibility — `attributionSkill`/`attributionPlugin` counts now; `/__dispatch` reader next | P1-2 | M |
| 5 | Roster island in `dashboard.html` (+0 counted DOM) **or** fix the dead portal pointer | P1-3 | S/M |
| 6 | **"What's wired on this host"** card + Gate 133 extended to `experimental.monitors` | P1-4 | M |
| 7 | Render `plan` mode explicitly (or declare it unreachable) | P2-1 | S |
| 8 | Amend the plan: retroactive §6.2 pass over `panel-mimir` | P2-2 | S |
| 9 | Land D8 / Gate 142 route sweep independently | P2-3 | S |
| 10 | Ship D4 autostart control | P3-1 | S |

**The through-line:** items 1, 2, 5 and 6 are all the same failure — *a surface that answers confidently
about Claude Code from a source it has not actually checked*. That is the repo's own Claim-Grounding
discipline, unenforced on its own dashboard. The gates cannot catch it because the fixtures were authored
from the same mental model as the readers. **Re-derive the fixtures from real platform artifacts and the
whole class closes.**
