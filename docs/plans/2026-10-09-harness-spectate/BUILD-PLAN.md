# Harness Spectate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a gold-standard, multi-harness livestream Spectate surface so users can see, understand, and (later) direct coding-agent harness activity in real time — familiar to Cursor / Claude Code / Codex, simple, highly customizable.

**Architecture:** Local loopback web app under `plugins/ravenclaude-core/dashboard-assets/spectate/`, served by `serve-dashboards.py`. Event bus is append-only `.ravenclaude/runs/<id>/spectate-events.jsonl`. Statuses are *derived on the server* from events + capability matrix + hook-deny join — never inferred from silence. One observe-only emitter hook (v0.2) rides existing host adapters. Steering (v0.3) is opt-in via comfort posture; ACP process-ownership is deferred.

**Tech Stack:** Vanilla HTML/CSS/JS (no framework, no build step), Python 3 (`spectate_store.py`), existing dashboard server + CSRF, IBM Plex Sans/Mono (vendored woff2 from v0.2), JSON Schema gate.

**Companion specs:**
- Visual system: [`design-system-spec.md`](./design-system-spec.md)
- Surface lock: [`SURFACE-DECISION.md`](./SURFACE-DECISION.md)
- Atlas: `docs/research/2026-10-04-coding-agent-harness-atlas/`
- Loop concept: `plugins/ravenclaude-core/knowledge/concepts/agent-harness-loop.md`

**Plan gap status:** G1 (15 gaps) closed in this revision (2026-10-09). Streak for `NO_GAPS` restarts at Plan G2.

premise-ok: serve-dashboards Host/Origin guard + Gate 142 + Cache-Control no-store (control.md under premise run scopes)

## Global Constraints

- Surface is **loopback-only** (127.0.0.1 / Codespaces); no Electron; no new backend service (`docs/dashboard-buildout-plan.md` §5.9).
- Ship inside **`ravenclaude-core`** (domain-neutral Observe infrastructure). No premature plugin split.
- Support harnesses: `claude-code`, `codex-cli`, `copilot-cli`, `copilot-vscode`, `cursor`, `gemini-cli`, `grok-build`, `grok-bot`.
- **No raw prompts / tool output / secrets** in spectate payloads (Streams Gate 110 discipline). Nested objects scrub recursively (G1-2).
- Both `scripts/serve-dashboards.py` and `plugins/ravenclaude-core/scripts/serve-dashboards.py` stay byte-parity on wrappers (Gate 32) **and** have behavioral smoke for `/spectate` + `/__spectate/*` (G1-14).
- Never add CORS. CSRF + Origin for state-changing routes. GETs use the existing `_local_request_ok` Host/Origin check (forged Host → refuse).
- UI uses `textContent` only — no `innerHTML`.
- Status never color-only: **color + shape + exact label** (11 statuses including `denied-harness`).
- Silence ≠ unavailable. Empty feed → `idle` + “never seen — cause not established” (`cause-taxonomy.md`). Capability `unknown` ≠ `unavailable-harness` (G1-1).
- Layout globs already cover all paths; do not invent top-level dirs.
- Version: bump `ravenclaude-core` from `0.328.0` → `0.329.0` for v0.1; then `sync-plugin-versions.py` + `generate-copilot-plugin.py`.
- Docs under `docs/plans/` land with the PR that ships product code (this feature is not docs-only).
- **Do not commit** regenerated `dashboard.html` / portal artifacts in the feature PR (G1-15). Modify the generator; exercise locally; leave committed regen to post-merge self-heal.

---

## Surface decision (locked)

Source of truth: [`SURFACE-DECISION.md`](./SURFACE-DECISION.md) (Pass C, 2026-10-09). The vehicle is unchanged. The front door is not the Activity tab.

| Option | Verdict |
|---|---|
| Static page on existing `serve-dashboards.py`, opened by `rc spectate` / `/spectate` | **Primary — build this in v0.1** |
| Activity → Spectate card | Discovery link only. Never the required path |
| VS Code / Cursor `openExternal` to the same URL | Later, only if alt-tab is the measured failure. Not a second UI |
| Embedded webview / Simple Browser / glance panel | Not v0.1. Guard rejects non-loopback origins; Simple Browser is already documented as blocked |
| Claude plugin slash alone | Insufficient for multi-host. `/spectate` is one door; `rc spectate` is the host-agnostic one |
| Electron, new backend, ACP spectator client, TUI product | Rejected for v0.1–v0.3 |

**Canonical URL (G1-7):** both servers expose a guarded `GET /spectate` (and `GET /spectate/`) that serves (or 302s to) assets from `plugins/ravenclaude-core/dashboard-assets/spectate/` regardless of whether the process was started as the plugin server (`directory=PLUGIN_DIR`) or the root marketplace server (`directory=REPO_ROOT`). Do **not** rely on `/dashboard-assets/spectate/` alone — that path only resolves under the plugin server. Activity discovery links use `/spectate`, not a plugin-relative static path.

Query: `?session=<id>` when the opener has one, else `?follow=latest`. Guardrails stay Heimdall / Víðarr.

---

## File tree (v0.1–v0.3)

```
plugins/ravenclaude-core/
  knowledge/spectate-event-schema-v1.json
  knowledge/spectate-capabilities.json
  knowledge/spectate.md
  scripts/spectate_store.py
  scripts/spectate_demo.py
  scripts/serve-dashboards.py              # /spectate + /__spectate/* wrappers
  hooks/spectate-emit.sh                   # v0.2
  hooks/tests/test-spectate-emit.sh        # v0.2
  dashboard-assets/spectate/
    index.html
    app.js
    spectate.css
    status-icons.svg
    fonts/                                 # v0.2 OFL woff2
  templates/run-artifacts/spectate-events.jsonl.template
  commands/spectate.md
scripts/
  serve-dashboards.py                      # parity wrappers + same /spectate map
  check-spectate.py                        # new gate
  generate-dashboards.py                   # Activity entry card (href=/spectate)
tests/fixtures/spectate/
  demo-session.jsonl
  hook-events-deny.jsonl
  bad-raw-prompt.jsonl
  bad-nested-args.jsonl
  bad-status.jsonl
  bad-session-traversal.jsonl
  expected-reduce.json
docs/plans/2026-10-09-harness-spectate/
  BUILD-PLAN.md
  design-system-spec.md
  gap-analysis.md
  SURFACE-DECISION.md
```

---

## Capability matrix (G1-1)

Keys in `spectate-capabilities.json` (seeded from atlas F06): `session`, `prompt`, `tool_pre`, `tool_post`, `tool_fail`, `permission_request`, `subagent`, `compact`, `stop`, `deny_plugin`, `deny_harness_visible`, `deny_user_visible`, `deny_org_visible`, `steer_context`.

**Per-capability state enum (not a UI status):**

| State | Meaning | UI derivation |
|---|---|---|
| `supported` | Atlas/probed evidence the harness exposes this | May become `available` / live statuses when events arrive |
| `partial` | Some of the surface works | Same as supported for present fields; inspector notes partial |
| `unsupported` | Evidence the harness does **not** expose this | Only this maps to `unavailable-harness` |
| `unknown` | `undocumented` / unverified / no probe yet | Node shows **capability unknown** (inspector copy). **Never** `unavailable-harness` |

Grok-bot (and any harness whose F06 cells are `undocumented`) seeds as `unknown` across the matrix until a probe upgrades a cell. Absence of events never upgrades `unknown` → `unsupported`.

---

## Event schema v1 (locked; G1-2 nested scrub)

Each JSONL line:

| Field | Rules |
|---|---|
| `schema` | `"rc.spectate.v1"` |
| `ts` | RFC 3339 UTC ms |
| `session_id` | sanitized — see Path & identity |
| `harness` | enum of 8 + `unknown` |
| `source` | `hook` \| `demo` \| `steer` \| `recorded` |
| `kind` | `session.start/end`, `prompt.submit`, `turn.end`, `tool.pre/post/fail`, `permission.request/resolve`, `subagent.start/stop`, `compact.pre`, `steer.applied`, `emitter.truncated` |
| `step` | `assemble` \| `call-model` \| `classify` \| `execute-tools` \| `package` \| `update-context` |
| `node_id` / `parent_id` / `agent_id` | stable IDs (see Correlation) |
| `corr_id` | shared correlation id when joining deny/hook rows; omit rather than invent |
| `tool` | `{name, family, target}` only — scrubbed; **no** `args` / `input` / `output` / `result` / `prompt` |
| `asserted_status` | optional harness-stated status (never overrides observed deny/fail) |
| `deny` | `{by, source, rule}` or null — short rule id only, not deny-message body |
| `metrics` | numbers only (`duration_ms`, `out_bytes`, `prompt_chars`) — no nested freeform |
| `detail` | `minimal` \| `standard` |
| `synthetic` | bool |

**Schema hardening (G1-2):**
- Root and every nested object: `additionalProperties: false`.
- String length caps on all string fields; reject control characters (`\x00`–`\x08`, `\x0b`, `\x0c`, `\x0e`–`\x1f`).
- Write-path and read-path both run recursive sensitive-key reject (`args`, `input`, `output`, `result`, `prompt`, `content`, `messages`, `secret`, `token`, `password`, `authorization`, `raw`).
- Fixtures: `bad-raw-prompt.jsonl`, `bad-nested-args.jsonl` must fail `check-spectate.py`.

**Reducer statuses (11):** `available`, `unavailable-harness`, `denied-org`, `denied-plugin`, `denied-user`, `denied-harness`, `running`, `succeeded`, `failed`, `waiting-approval`, `idle`.

UI-only (not reducer statuses): **capability unknown**, **disconnected**, **stale**, source badges (`demo` / `recorded` / `live`) — see Source-mode UI.

---

## Correlation identities (G1-4)

| Identity | Uniqueness / rules |
|---|---|
| `session_id` | Key for `.ravenclaude/runs/<session_id>/`. Sanitized per Path rules. Groups one spectate stream. |
| `harness` | Column / chip identity within a session. Composite graph key includes harness. |
| `agent_id` | Stable within session; default `"main"` when absent. Parallel columns = distinct `agent_id`. |
| `node_id` | Unique within `(session_id, harness, agent_id)`. Required on every non-session event. |
| `parent_id` | Optional; when set must reference an existing `node_id` in the same session+harness+agent (or be dropped with `emitter.truncated`). Tool nodes parent to the `execute-tools` step node. |
| `corr_id` | When joining `hook-events.jsonl` denies: both sides must share `corr_id`. **No heuristic join** (tool-name+timestamp fuzzy match) when `corr_id` is absent — leave deny unjoined and show status from spectate events only. |

---

## Path & session resolution (G1-5)

- Accept `session_id` matching `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`.
- Reject: `.`, `..`, empty, pure-dot, any `/` or `\`, URL-encoded separators (`%2e`, `%2f`, `%5c`), NUL.
- Resolve path as: `runs_root = <project>/.ravenclaude/runs` → `candidate = (runs_root / session_id).resolve()` → require `candidate` is under `runs_root.resolve()` and is a directory → open only the fixed file `spectate-events.jsonl` (name constant, not caller-supplied).
- Refuse if `candidate` is a symlink escape (final resolved path must remain under `runs_root`).
- Fixture `bad-session-traversal.jsonl` + store unit tests cover `..`, encoded separators, symlink escape.

---

## Poll / cursor / sessions API semantics (G1-6)

Endpoints (GET, read-only, `_local_request_ok`):

| Route | Contract |
|---|---|
| `/__spectate/sessions?cursor=&limit=` | Paginated. Default `limit=50`, max `200`. Opaque `next_cursor`. Ordered by mtime desc of `spectate-events.jsonl`. |
| `/__spectate/events?session=&cursor=&limit=` | Opaque **byte-offset** cursor into the session file. Default `limit=100`, max `500`. |
| `/__spectate/capabilities` | Full matrix JSON. |
| `/__spectate/nodes?session=` | Reduced node list for the session. |

**Cursor / file rules:**
- Snapshot file size at open; never read past that snapshot in one response (concurrent appends appear on the next poll).
- Skip incomplete trailing lines (no final `\n`); do not advance cursor past a partial line.
- Malformed JSONL lines: skip, increment `skipped_malformed`, continue.
- File > 5 MiB: serve from the **tail** window, set `truncated: true` + `truncate_marker` event synthetic at window start.
- Stale cursor (> size): reset to `0` and set `cursor_reset: true` (client must replace, not append-dedupe blindly).
- Response includes `next_cursor` (byte offset after last complete line delivered) and `etag`/`file_mtime` for stale detection.
- Client dedupe: key = `(session_id, node_id, kind, ts)` when replaying after reset.

---

## Reducer contract (G1-3)

`reduce(events, hook_denies, capabilities) → nodes`

**Ordering:** sort by `ts` ascending; tie-break `kind` order: `session.start` < `*.pre` < `permission.request` < `*.post`/`*.fail`/`permission.resolve` < `session.end` < `emitter.truncated`. Same-ts same-kind: stable by file order.

**Per-node state machine (terminal wins):**

| From \ Event | Effect |
|---|---|
| (missing) + capability `unsupported` | seed `unavailable-harness` |
| (missing) + capability `unknown` | seed UI **capability unknown** (status field `idle` + `capability_state: unknown` — never `unavailable-harness`) |
| (missing) + capability supported/partial, no events | `idle` (“never seen — cause not established”) |
| * → `tool.pre` / step start | `running` (unless already terminal deny/fail/succeeded) |
| * → `tool.post` / success end | `succeeded` (terminal for that node) |
| * → `tool.fail` | `failed` (terminal) |
| * → deny join (`denied-*`) | that deny status (terminal; **deny beats** later `succeeded`/`asserted_status`) |
| * → `permission.request` open | `waiting-approval` |
| waiting-approval → resolve allow | `running` or `succeeded` per following events |
| waiting-approval → resolve deny | matching `denied-*` |
| any + `asserted_status` | apply **only if** current is non-terminal and no observed deny/fail evidence |

**Precedence (highest wins):** joined deny (`denied-org` > `denied-plugin` > `denied-user` > `denied-harness`) > `failed` > `succeeded` > `waiting-approval` > `running` > `available` > `idle`. `unavailable-harness` only from explicit `unsupported` capability seed.

**Dedup:** last-writer for non-terminal; terminal states are sticky (ignore contradictory later success/`asserted_status`). Golden: `expected-reduce.json`.

---

## Source-mode UI (G1-8)

Chrome badge + state machine (mutually exclusive primary badge):

| Mode | When | Badge |
|---|---|---|
| `demo` | session `synthetic: true` / demo writer | `DEMO` |
| `recorded` | JSONL present, no live emitter this process | `RECORDED` |
| `live` | v0.2+ emitter heartbeats within threshold | `LIVE` |
| `observe-only` | any non-demo session in v0.1–v0.2 | subtitle: “Observe only — steering unavailable until v0.3” |
| `connecting` | first poll in flight | spinner + “connecting” |
| `disconnected` | fetch network/HTTP failure | **disconnected** (retry). **Never** render as `idle` or empty success |
| `stale` | last successful poll older than 3× interval while tab visible | `STALE` |
| `no-session` | sessions list empty | empty-state copy, not a fake graph |

Poll failure must not clear existing nodes; overlay disconnected chrome instead.

---

## Visual / UX (locked from design-system-spec; G1-9…G1-12)

- Three panes: Sessions (240) · Live graph (flex) · Inspector (320).
- Chrome: product name, density, columns, theme, **source badge**, **status legend placement**, **session filter**.
- Loop spine: Assemble → Model → Classify → Tools → Package → Context; tools branch from Execute.
- Customizable (persisted `localStorage`, namespaced `rc.spectate.v1.*`): `data-theme`, `data-density`, layout presets (`default` \| `graph-focus` \| `inspector-focus` \| `sessions-focus`), agent-column visibility, legend placement (`footer` \| `inspector`), session filter query. Corrupt/missing storage → safe defaults (no throw).
- Motions: running pulse, edge draw + node enter, inspector cross-fade; honor `prefers-reduced-motion`.
- Type: IBM Plex Sans + Mono (fallback stack in v0.1; vendored fonts v0.2).
- **`denied-harness`:** first-class tokens in design-system-spec (hexagon, orange-band twin of `denied-org`, light theme + contrast). Not an “extension note.”
- **Payload tab override (G1-10):** companion wireframe “args / result” is **void**. Payload may render only schema-approved scrubbed fields (`tool.name/family/target`, metrics numbers, deny `{by,source,rule}`, timing). Never raw prompts, arguments, results, transcript, or deny-message bodies.

### Keyboard / a11y acceptance (G1-11)

- Graph: roving `tabindex` among nodes; Arrow keys move along spine / tool children; Enter/Space selects; focus restored to selected node after redraw.
- Session rail and inspector are landmark regions with labels; all icon-only controls have accessible names.
- MD breakpoint drawer and SM bottom sheet: focus trap while open; Escape closes; restore focus to invoking node.
- Automated checks: desktop / tablet / mobile widths; `prefers-reduced-motion: reduce`; status never color-only (shape + label present in DOM).

---

## Response headers (G1-13) — v0.1, not deferred

On every `/__spectate/*` JSON response and on `/spectate` HTML/JS/CSS assets:

- `Cache-Control: no-store`
- `X-Content-Type-Options: nosniff`
- Spectate CSP (HTML document): `default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'`

(Inline style allowance is temporary for token attributes in v0.1; tighten when fonts vendor in v0.2 if feasible.)

---

## Phased delivery

### v0.1 — Demo + poll + gold UI (THIS PR)

Complete, beautiful, customizable Spectate on synthetic + fixture data; polls real `spectate-events.jsonl` when present. No hooks yet. Observe-only chrome explicit.

### v0.2 — Real hooks

`spectate-emit.sh` + host projection + deny join + font vendor + measured probes + capability cell upgrades from `unknown` → `supported`/`unsupported`.

### v0.3 — SSE + steer MVP

SSE stream, comfort-posture `spectate_steer`, pause-as-deny + note injection; ACP deferred to v0.4+.

---

## Tasks — v0.1

### Task 1: Schema, capabilities, fixtures, gate

**Files:**
- Create `plugins/ravenclaude-core/knowledge/spectate-event-schema-v1.json`
- Create `plugins/ravenclaude-core/knowledge/spectate-capabilities.json`
- Create `tests/fixtures/spectate/*`
- Create `scripts/check-spectate.py`
- Wire into `scripts/audit-gates.sh`

- [ ] Write schema JSON (required fields, enums, `additionalProperties: false` on root **and nested**; length + control-char rules)
- [ ] Write capabilities matrix for all 8 harnesses with atlas evidence ids; states `supported|partial|unsupported|unknown` (G1-1)
- [ ] Write demo-session.jsonl covering all 11 statuses + multi-harness columns + capability-unknown column for grok-bot
- [ ] Write bad fixtures: raw prompt, nested args smuggle, illegal status, session traversal ids
- [ ] Write `expected-reduce.json` golden (never-seen → `idle`; unknown ↛ unavailable; deny beats asserted success)
- [ ] Implement `check-spectate.py --check` (pass demo; fail bad fixtures; fail missing evidence; **must_flag_unwired** canary)
- [ ] Add must-pass / must-fail / must_flag_unwired rows to `audit-gates.sh`
- [ ] Run: `python3 scripts/check-spectate.py --check` → exit 0
- [ ] Commit: `feat(spectate): schema, capabilities, fixtures, Gate check-spectate`

### Task 2: `spectate_store.py` + `/__spectate` routes

**Files:**
- Create `plugins/ravenclaude-core/scripts/spectate_store.py`
- Create `plugins/ravenclaude-core/scripts/spectate_demo.py`
- Modify both `serve-dashboards.py` copies (thin wrappers + headers)

Endpoints (GET, read-only, Host/Origin-checked):
- `/__spectate/sessions?cursor=&limit=`
- `/__spectate/events?session=&cursor=&limit=`
- `/__spectate/capabilities`
- `/__spectate/nodes?session=`

- [ ] Implement allow-list parse + recursive re-scrub + 5 MB tail/truncate semantics (G1-2, G1-6)
- [ ] Implement session path resolve (G1-5) + correlation rules (G1-4)
- [ ] Implement `reduce(...)` per Reducer contract (G1-3)
- [ ] Golden test: fixtures → `expected-reduce.json`
- [ ] Add thin routes to plugin server; mirror in root server; set `Cache-Control: no-store`, `nosniff`, Spectate CSP on HTML (G1-13)
- [ ] Behavioral smoke both servers: `/spectate` serves UI; `/__spectate/sessions` JSON (G1-7, G1-14) — Gate 32 alone is insufficient
- [ ] Run Gate 32 parity check
- [ ] `spectate_demo.py` writes a synthetic session under `.ravenclaude/runs/`
- [ ] Commit: `feat(spectate): store, demo writer, /__spectate poll API`

### Task 3: Spectate UI (gold-standard shell)

**Files:**
- Create `plugins/ravenclaude-core/dashboard-assets/spectate/{index.html,app.js,spectate.css,status-icons.svg}`
- Modify `scripts/generate-dashboards.py` Activity tab → Spectate entry card (`href=/spectate`)
- **Do not commit** regenerated `dashboard.html` / portal outputs (G1-15); exercise generator locally only

- [ ] CSS tokens from design-system-spec (dark default + light mirror) including **`denied-harness`** (G1-9)
- [ ] Three-pane layout + responsive breakpoints
- [ ] Status icon set (SVG) for all 11 statuses — shape + label; hexagon for `denied-harness`
- [ ] Session rail with harness chips + live/idle + **session filter** (G1-12)
- [ ] Loop spine graph + tool nodes; agent columns toggle
- [ ] Inspector: Overview / Policy / Payload — Payload scrubbed fields only (G1-10)
- [ ] Customization chrome: theme, density, layout preset, columns, legend placement → `localStorage` with safe defaults (G1-12)
- [ ] Source-mode badges + disconnected/stale/connecting/observe-only (G1-8)
- [ ] Poll `/__spectate/*` every 2s; never map poll failure → idle
- [ ] Keyboard/a11y contracts (G1-11); reduced-motion
- [ ] Grep gate / assert: no `innerHTML` in spectate assets
- [ ] Smoke: open via both server entrypoints, load demo, verify all statuses + capability-unknown
- [ ] On load: `session=` pins; otherwise `follow=latest`. Never empty picker while a run file exists
- [ ] Commit: `feat(spectate): Spectate UI shell` (assets + generator source only)

### Task 3b: Launchers (`rc spectate`, `/spectate`)

**Files:**
- Modify `plugins/ravenclaude-core/bin/rc` — new `spectate` verb
- Modify both `serve-dashboards.py` copies — `GET /spectate` maps to plugin spectate assets (G1-7). Do not retarget bare `/`
- Create `plugins/ravenclaude-core/commands/spectate.md`

- [ ] `rc spectate [--session ID] [--no-open] [--port N]` starts the server only when this project has none. If one is already listening, open against that port. Do **not** call `_reclaim_port` on a live server
- [ ] Open `http://127.0.0.1:<port>/spectate?session=<id>` when an id is known, else `?follow=latest`. `--no-open` prints the URL plus one status line from the store
- [ ] Session id order: explicit `--session`, else `CLAUDE_SESSION_ID`, else `follow=latest`
- [ ] `/spectate` slash is a thin sibling of `/dashboard` (Claude Code only). Same URL. Copilot/Codex/Cursor/Gemini use `rc spectate`
- [ ] Codespaces: print the forwarded `/spectate` URL. `onAutoForward` still opens `/` → dashboard; do not hijack `DASH_PATH`
- [ ] Activity entry card links to `/spectate`. It is not the smoke path
- [ ] Commit: `feat(spectate): rc spectate and /spectate open the session URL`

### Task 4: Knowledge + version + preflight

**Files:**
- Create `plugins/ravenclaude-core/knowledge/spectate.md`
- Create `plugins/ravenclaude-core/templates/run-artifacts/spectate-events.jsonl.template`
- Bump `plugins/ravenclaude-core/.claude-plugin/plugin.json` → `0.329.0`
- Update CHANGELOG if present
- Run sync + copilot generate

- [ ] Operator doc: how to open Spectate, demo mode, honesty about v0.1 (no hooks; observe-only)
- [ ] Version bump + `python3 scripts/sync-plugin-versions.py`
- [ ] `python3 scripts/generate-copilot-plugin.py`
- [ ] `npx prettier@3.9.4 --write .` then `--check .`; `ruff check .` (whole tree)
- [ ] `python3 scripts/ci-preflight.py`
- [ ] Full `scripts/audit-gates.sh` (not targeted-only) (G1-14)
- [ ] Commit: `chore(spectate): docs, template, bump core 0.329.0`

### Task 5: Manual walkthrough evidence

- [ ] Start `serve-dashboards.py` (plugin **and** root modes), run demo, screenshot/record three-pane UI
- [ ] Save artifacts under `/opt/cursor/artifacts/`
- [ ] Push branch + open/update draft PR

---

## Tasks — v0.2 (follow-up PR)

- [ ] `hooks/spectate-emit.sh` — exit 0, empty stdout, scrubbed JSONL append; write `corr_id` into deny-joinable events
- [ ] Register in `hooks/hooks.json` on SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStart, PreCompact
- [ ] Ensure projectors place or skip; pass `check-crosshost-hook-coverage.py`
- [ ] Grok-build env detection override; upgrade capability cells from measured probes
- [ ] Deny join from `hook-events.jsonl` via `corr_id` only
- [ ] Vendor IBM Plex OFL fonts; tighten CSP if inline styles removable
- [ ] Bump to `0.330.0`

## Tasks — v0.3 (follow-up PR)

- [ ] `GET /__spectate/stream` SSE (≤4 streams, 15s heartbeat, Last-Event-ID)
- [ ] `POST /__spectate/steer` CSRF+Origin; posture `spectate_steer: on`
- [ ] Pause-as-deny + capped note injection where `steer_context` supported
- [ ] Bump to `0.331.0`

## Deferred (v0.4+)

- Approve/deny waiting-approval from browser
- True interrupt
- ACP control channel (process ownership)
- IDE `openExternal` to the same `/spectate` URL (only if alt-tab is the measured failure; not Simple Browser, not a second UI)
- Claude monitor push mirror

---

## Testing matrix (v0.1) — G1-14

| Check | Command / method |
|---|---|
| Schema + fixtures + unwired canary | `python3 scripts/check-spectate.py --check` |
| Reducer golden | unit inside check-spectate / spectate_store |
| Path traversal | bad-session fixtures + store unit |
| Nested scrub | bad-nested-args fixture |
| Server name parity | Gate 32 |
| Server **behavior** parity | hit `/spectate` + `/__spectate/sessions` on both entrypoints |
| No CORS / Host refuse | Gate 142 cases for `/__spectate` |
| Headers | assert `Cache-Control: no-store`, `nosniff`, CSP on spectate HTML |
| Poll failure UI | mock fetch fail → disconnected badge, nodes retained |
| Customization persistence | set theme/density/legend/filter; reload; corrupt key → defaults |
| Responsive + a11y | desktop/tablet/mobile + reduced-motion checks |
| Lint | whole-tree prettier + ruff |
| Preflight | `python3 scripts/ci-preflight.py` |
| Full gate audit | `scripts/audit-gates.sh` |
| Manual | demo session walkthrough recording (both servers) |

---

## Security checklist

- [x] No raw prompts in schema; nested additionalProperties false + recursive scrub
- [x] Dual scrub (write + read)
- [x] Host check on GET; CSRF+Origin on steer (v0.3)
- [x] No CORS
- [x] No `innerHTML`
- [x] File size cap + truncate marker
- [x] Session path resolve under runs root; reject traversal
- [x] Synthetic flag for demo
- [x] Cache-Control no-store + Spectate CSP in v0.1
- [x] Payload UI cannot show args/result

---

## Open questions (resolved for v0.1)

| Q | Decision |
|---|---|
| Steering in Codespaces? | Defer to v0.3; same CSRF/Origin rules as other dashboard POSTs |
| Default detail level | `minimal` for shell targets; `standard` for path/domain |
| `denied-org` | Reserved; matrix marks `deny_org_visible` unsupported/unverified until probed |
| Status naming | `denied-harness` (matches `denied-org` pattern); hexagon shape — **shipped in design tokens** |
| F06 `undocumented` | → capability `unknown`, not `unavailable-harness` |
| Wireframe Payload args/result | Overridden; scrubbed fields only |
| Commit dashboard.html in feature PR? | No — generator source only |

---

## G1 close index

| ID | Close location |
|---|---|
| G1-1 | Capability matrix section |
| G1-2 | Event schema nested scrub + fixtures |
| G1-3 | Reducer contract |
| G1-4 | Correlation identities |
| G1-5 | Path & session resolution |
| G1-6 | Poll / cursor / sessions API |
| G1-7 | Surface decision canonical URL + Task 2/3b |
| G1-8 | Source-mode UI |
| G1-9 | Visual/UX + design-system-spec |
| G1-10 | Payload tab override + design-system-spec |
| G1-11 | Keyboard / a11y acceptance |
| G1-12 | Customization axes (filter/legend/storage) |
| G1-13 | Response headers v0.1 |
| G1-14 | Testing matrix + Task 4 full audit |
| G1-15 | Global Constraints + Task 3 no-commit generated artifacts |

---

## Success criteria (v0.1 gold bar)

1. User runs `rc spectate` (or `/spectate`) and lands on the live/demo session in ≤2 actions — Activity is never required.
2. Demo session shows all 11 statuses with shape + label; grok-bot shows **capability unknown**, not a false `unavailable-harness`.
3. Theme / density / layout / columns / legend / filter persist across reload; corrupt storage safe-defaults.
4. Polling updates the graph without full page refresh; poll failure shows disconnected, not idle.
5. No secrets or raw prompts/args/results appear in network responses or Payload tab.
6. Feels like a Cursor/Claude/Codex tool — dense, calm, teal accent only for focus.
7. `/spectate` works from both plugin and root `serve-dashboards.py` entrypoints.
