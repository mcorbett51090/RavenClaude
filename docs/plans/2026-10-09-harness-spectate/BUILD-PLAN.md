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

**Plan gap status:** G1–G5 closed in this revision (2026-10-09). Streak for `NO_GAPS` restarts at Plan G6.

premise-ok: serve-dashboards Host/Origin guard + Gate 142 + Cache-Control no-store (control.md under premise run scopes)

## Global Constraints

- Surface is **loopback-only** for Spectate (127.0.0.1 / exact Codespace host); no Electron; no new backend service (SURFACE lock / proposal 003). Even when the root server is started with `--bind 0.0.0.0`, Spectate routes refuse non-loopback peer/Host/Origin except the exact Codespace forward host (G4-1).
- Ship inside **`ravenclaude-core`** (domain-neutral Observe infrastructure). No premature plugin split.
- Support harnesses: `claude-code`, `codex-cli`, `copilot-cli`, `copilot-vscode`, `cursor`, `gemini-cli`, `grok-build`, `grok-bot`.
- **No raw prompts / tool output / secrets** in spectate payloads (Streams Gate 110 discipline). Nested objects scrub recursively (G1-2).
- Both `scripts/serve-dashboards.py` and `plugins/ravenclaude-core/scripts/serve-dashboards.py` stay byte-parity on wrappers (Gate 32) **and** have behavioral smoke for `/spectate` + `/__spectate/*` (G1-14).
- Never add CORS. CSRF + Origin for state-changing routes. GETs use the existing `_local_request_ok` Host/Origin check (forged Host → refuse).
- UI uses `textContent` only — no `innerHTML`.
- Status never color-only: **color + shape + exact label** (11 statuses including `denied-harness`).
- Silence ≠ unavailable. Empty feed → `idle` + “never seen — cause not established” (`cause-taxonomy.md`). Capability `unknown` ≠ `unavailable-harness` (G1-1).
- Layout globs already cover all paths; do not invent top-level dirs.
- Version: rebase onto `origin/main` before bumping. Bump `ravenclaude-core` to the **next minor above** the current `origin/main` plugin.json (today that is already `0.329.1` — so v0.1 is `0.330.0`, not a downgrade to `0.329.0`) (G5-1). Then `sync-plugin-versions.py` + `generate-copilot-plugin.py`. Do not hard-code stale versions in later task text — always read plugin.json at implement time.
- Docs under `docs/plans/` land with the PR that ships product code (this feature is not docs-only).
- **Do not commit** regenerated `dashboard.html` in the feature PR (G1-15). Modify the generator; exercise locally; leave `dashboard.html` regen to post-merge self-heal.
- **Do commit** Gate 242 inventory concept + regenerated `docs/concepts.md` (and any structural `index.html` freshness required by `check-artifact-freshness`) in this PR (G2-1). `dashboard.html` is the only generated artifact deferred to post-merge.

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

**Canonical URL (G1-7 / G2-4):** both servers expose a guarded **serve** (not 302) for `/spectate`, `/spectate/`, and `/spectate/<allow-listed name>` via one `_handle_spectate_asset` / `_read_spectate_*` helper. It maps to `plugins/ravenclaude-core/dashboard-assets/spectate/` regardless of plugin vs root server. Do **not** 302 to `/dashboard-assets/spectate/` (404 under root server). Activity discovery links use `/spectate`.

Route rules (G2-4, G2-17, G3-1, G3-7):
- Match on `path.split("?", 1)[0]` only (query must not break the match). Exact `/spectate` / `/spectate/` or prefix `/spectate/` — never bare `startswith("/spectate")` (would match `/spectatex`). Keep the raw query for the page.
- Smoke: `GET /spectate?follow=latest` and `GET /spectate?session=<id>` return HTML 200, not 404.
- Allow-list filenames to the spectate asset directory listing + `fonts/*.woff2`; resolve under `PLUGIN_SPECTATE_DIR`; refuse escapes. Strip query before filename allow-list.
- `_local_request_ok()` on every spectate GET/HEAD. Spectate HEAD is a **guarded** branch that calls the same handler (or 405) — do **not** append `/spectate` or `/__spectate` to the ungated `do_HEAD` 200/`Allow` list.
- Set G1-13 headers + explicit `Content-Type` map: `.html` → `text/html; charset=utf-8`, `.js` → `text/javascript`, `.css` → `text/css`, `.svg` → `image/svg+xml`, `.woff2` → `font/woff2`.
- `index.html` references assets as absolute `/spectate/app.js` (relative URLs break when served at `/spectate` without trailing slash).
- While touching servers: fix stale `do_GET` comments that still say “static GETs are intentionally ungated” (fallback already guards).

Query: `?session=<id>` when the opener has one, else `?follow=latest`. Guardrails stay Heimdall / Víðarr.

---

## File tree (v0.1–v0.3)

```
plugins/ravenclaude-core/
  knowledge/spectate-event-schema-v1.json
  knowledge/spectate-capabilities.json
  knowledge/spectate.md
  knowledge/concepts/harness-spectate.md   # Gate 242 inventory (G2-1)
  scripts/spectate_store.py
  scripts/spectate_demo.py
  scripts/serve-dashboards.py              # /spectate + /__spectate/* wrappers
  hooks/spectate-emit.sh                   # v0.2 (add to concept covers then)
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
  check-spectate-render.mjs                # stub-DOM UI checks (G2-15)
  generate-dashboards.py                   # Activity entry card (href=/spectate)
tests/fixtures/spectate/
  demo-session.jsonl
  hook-events-deny.jsonl
  bad-raw-prompt.jsonl
  bad-nested-args.jsonl
  bad-secret-in-target.jsonl
  bad-url-query-target.jsonl
  bad-status.jsonl
  bad-session-traversal.jsonl
  expected-reduce.json
docs/plans/2026-10-09-harness-spectate/
  BUILD-PLAN.md
  design-system-spec.md
  gap-analysis.md
  SURFACE-DECISION.md
docs/concepts.md                           # regenerated + committed (G2-1)
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
| `kind` | `session.start/end`, `prompt.submit`, `turn.end`, `tool.pre/post/fail`, `permission.request/resolve`, `subagent.start/stop`, `compact.pre`, `steer.applied`, `stream.truncated`, `emitter.truncated` |
| `step` | `assemble` \| `call-model` \| `classify` \| `execute-tools` \| `package` \| `update-context` |
| `node_id` / `parent_id` / `agent_id` | stable IDs (see Correlation) |
| `corr_id` | shared correlation id when joining deny/hook rows; omit rather than invent |
| `tool` | `{name, family, target}` only — scrubbed; **no** `args` / `input` / `output` / `result` / `prompt` |
| `asserted_status` | optional harness-stated status (never overrides observed deny/fail) |
| `deny` | `{by, source, rule}` or null — `by` enum below; short rule id only, not deny-message body or path |
| `metrics` | numbers only (`duration_ms`, `out_bytes`, `prompt_chars`) — no nested freeform |
| `detail` | `minimal` \| `standard` |
| `synthetic` | bool |

**Schema hardening (G1-2):**
- Root and every nested object: `additionalProperties: false`.
- String length caps on all string fields; reject control characters (`\x00`–`\x08`, `\x0b`, `\x0c`, `\x0e`–`\x1f`).
- Write-path and read-path both run recursive sensitive-key reject (`args`, `input`, `output`, `result`, `prompt`, `content`, `messages`, `secret`, `token`, `password`, `authorization`, `raw`).
- **Value scrub (G2-10):** every string field also runs the existing value scrubber (`_scrub.sh` / `_mimir_*` equivalent) so secrets in *values* cannot ride `tool.target`.
- Fixtures: `bad-raw-prompt.jsonl`, `bad-nested-args.jsonl`, `bad-secret-in-target.jsonl`, `bad-url-query-target.jsonl` must fail `check-spectate.py`.

**Target derivation (G2-10)** — both `minimal` and `standard` detail levels:

| `tool.family` | Stored `target` |
|---|---|
| `shell` | first token / binary name only |
| `url` | scheme + host only (strip path, query, fragment) |
| `path` | repo-relative path when under project root; else omitted |
| other | omit `target` |

Deny join copies only `{by, source, rule}` — never hook-event `path`.

**`deny.by` enum (G2-7):** `org` → `denied-org`; `plugin` → `denied-plugin`; `user` → `denied-user`; `harness` → `denied-harness`. `permission.resolve` with deny uses the same map from the resolve payload's `by` (default `user` if absent).

**Reducer statuses (11):** `available`, `unavailable-harness`, `denied-org`, `denied-plugin`, `denied-user`, `denied-harness`, `running`, `succeeded`, `failed`, `waiting-approval`, `idle`.

UI-only (not reducer statuses): **capability unknown**, connection chrome, source badges — see Source-mode UI.

---

## Correlation identities (G1-4)

| Identity | Uniqueness / rules |
|---|---|
| `session_id` | Key for `.ravenclaude/runs/<session_id>/`. Sanitized per Path rules. Groups one spectate stream. |
| `harness` | **Session-rail chip only** (G2-9 / G3-4). Composite node key includes harness for uniqueness; it is not a graph column. |
| `agent_id` | Stable within session; default `"main"` when absent. **Graph columns = `agent_id`** (main + subagents). Harness is a session-rail chip, not a graph column (G2-9). |
| `node_id` | Unique within `(session_id, harness, agent_id)`. Required on every non-session event. |
| `parent_id` | Optional; when set must reference an existing `node_id` in the same session+harness+agent (else `parent_truncated: true`). Tool nodes parent to the `execute-tools` step node. |
| `corr_id` | When joining `hook-events.jsonl` denies: both sides must share `corr_id`. **No heuristic join** when absent. v0.2 source: payload `tool_use_id` (G2-12). |

**Multi-harness view (G2-9 / G4-2):** sessions from all harnesses appear together in the session rail (chips). The graph shows **one session at a time**. Each `spectate-events.jsonl` stream has **exactly one** `harness` value (enforced by store + gate). Cross-session multi-harness graph deferred to v0.4+. Demo mode writes **separate** run directories per harness for the gallery (not one file with many harnesses).

---

## Path & session resolution (G1-5)

- Accept `session_id` matching `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`.
- Reject: `.`, `..`, empty, pure-dot, any `/` or `\`, URL-encoded separators (`%2e`, `%2f`, `%5c`), NUL.
- Resolve path as: `runs_root = <project>/.ravenclaude/runs` → `candidate = (runs_root / session_id).resolve()` → require `candidate` is under `runs_root.resolve()` and is a directory → open only the fixed file `spectate-events.jsonl` (name constant, not caller-supplied).
- Refuse if `candidate` is a symlink escape (final resolved path must remain under `runs_root`).
- Also resolve `event_file = (candidate / "spectate-events.jsonl").resolve()`; require it stays under `runs_root` and is a regular file (or open with `O_NOFOLLOW`) (G2-18).
- Fixture `bad-session-traversal.jsonl` + store unit tests cover `..`, encoded separators, dir symlink escape, **file** symlink escape.

---

## Poll / cursor / sessions API semantics (G1-6)

Endpoints (GET, read-only, `_local_request_ok`):

| Route | Contract |
|---|---|
| `/__spectate/sessions?cursor=&limit=&harness=` | Paginated. Default `limit=50`, max `200`. Opaque `next_cursor`. Each item: `{session_id, harness, synthetic, mtime, latest_status}` (G3-8). `latest_status` from session-summary reducer (G4-3). Follow ranking: non-synthetic first, then mtime desc; synthetic only if nothing else matches. Optional `harness=` filters ranking + rail (not graph columns). |
| `/__spectate/events?session=&cursor=&limit=` | Opaque **absolute byte-offset** cursor into the session file. Default `limit=100`, max `500`. |
| `/__spectate/capabilities` | Full matrix JSON. |
| `/__spectate/nodes?session=` | Reduced node list for the session. |

**Cursor / file rules:**
- Snapshot file size at open; never read past that snapshot in one response (concurrent appends appear on the next poll).
- Skip incomplete trailing lines (no final `\n`); do not advance cursor past a partial line.
- Malformed JSONL lines: skip, increment `skipped_malformed`, continue.
- Cursors are **absolute file offsets** (G3-9). First response range is `[max(0, size-5MiB), size_snapshot]`, with one synthetic `stream.truncated` at the window start when truncated. `next_cursor` = absolute offset after last complete line. Cursor `0` is valid only when `size ≤ 5 MiB`. Cursor `> size` → `cursor_reset: true` and restart at **tail start** (not byte 0).
- Response includes `next_cursor`, `truncated`, `etag`/`file_mtime`.
- Client dedupe on events (inspector only): key = `(session_id, node_id, kind, ts)` when replaying after reset.

---

## Reducer contract (G1-3 / G2-7 / G2-8 / G2-16)

`reduce(events, hook_denies, capabilities) → nodes` — **server-only**. The UI never reduces; it polls `/__spectate/nodes` (G2-16).

**Step ↔ capability seed map (G2-7):**

| Spine step | Capability key | Seed when step not started |
|---|---|---|
| `assemble` | `session` | see precedence |
| `call-model` | `prompt` | see precedence |
| `classify` | `prompt` | see precedence |
| `execute-tools` | `tool_pre` | see precedence |
| `package` | `tool_post` | see precedence |
| `update-context` | `compact` | see precedence |

**Seed precedence (G3-2)** — apply first match:
1. capability `unsupported` → `unavailable-harness` (matrix is the evidence; **even at 0 events**)
2. capability `unknown` → `idle` + `capability_state: unknown` (even at 0 events; never upgrade to unavailable)
3. capability supported/partial + session event count = 0 → `idle` (“never seen — cause not established”)
4. capability supported/partial + ≥1 event + step not started → `available`
5. otherwise follow transition table

Tool child nodes seed from `tool_pre` / `tool_post` / `tool_fail` / `permission_request` / `subagent` as applicable.

**Ordering:** sort by `ts` ascending; tie-break `kind` order covering the full enum: `session.start` < `prompt.submit` < `*.pre` / `subagent.start` / `compact.pre` < `permission.request` < `tool.post` / `tool.fail` / `permission.resolve` / `turn.end` / `subagent.stop` / `steer.applied` < `session.end` < `stream.truncated` < `emitter.truncated`. Same-ts same-kind: stable by file order.

**Kind split (G2-20):** `stream.truncated` = file-tail window marker; `emitter.truncated` = dropped/invalid field annotation from the emitter. Do not overload one kind.

**Per-node transitions (terminal wins):**

| From \ Event | Effect |
|---|---|
| seed per table above | as mapped |
| * → `tool.pre` / step start | `running` (unless already terminal) |
| * → `tool.post` / success end | `succeeded` (terminal) |
| * → `tool.fail` | `failed` (terminal) |
| * → deny join (`denied-*` via `deny.by`) | that deny status (terminal; **deny beats** later success/`asserted_status`) |
| * → `permission.request` open | `waiting-approval` |
| waiting-approval → resolve allow | `running` or `succeeded` per following events |
| waiting-approval → resolve deny | matching `denied-*` |
| any + `asserted_status` | apply **only if** non-terminal and no observed deny/fail |
| `session.end` or session not live | non-terminal nodes keep status + `unterminated: true` (UI: stop pulse; “no completion observed — cause not established”) (G2-8) |

**Precedence (highest wins):** joined deny (`denied-org` > `denied-plugin` > `denied-user` > `denied-harness`) > `failed` > `succeeded` > `waiting-approval` > `running` > `available` > `idle`. `unavailable-harness` only from explicit `unsupported` seed.

**Nodes response bounds (G2-16):** reduce over the same 5 MiB tail window; orphan parents → `parent_truncated: true`; cap 2,000 nodes newest-first with `nodes_truncated`; graph shows latest N turns (default 3) + “show earlier turns”. `/__spectate/nodes?session=&since_etag=` supports 304. `/__spectate/events` is inspector timeline only.

**Dedup:** last-writer for non-terminal; terminal states sticky. Golden: `expected-reduce.json` includes available, deny maps, unterminated, unknown↛unavailable.

**Session-summary reducer (G4-3)** → `latest_status` for sessions list / `--no-open`:
1. If any node `failed` → `failed`
2. Else if any joined deny → that deny status (org > plugin > user > harness)
3. Else if any `waiting-approval` → `waiting-approval`
4. Else if any `running` or `unterminated` → `running`
5. Else if any `succeeded` and `session.end` present → `succeeded`
6. Else if only `session.start` (or empty after start) → `idle`
7. Else → `idle`

Golden cases: start-only, completed, failed, denied, unterminated.

---

## Source + connection chrome (G1-8 / G2-8)

Two independent axes (not one mutually exclusive badge):

| Axis | Values | Rule |
|---|---|---|
| `source` | `demo` \| `recorded` \| `live` | `demo` = synthetic; `live` = last event `ts` ≤ 60s ago and no `session.end` (show “last event Ns ago”); else `recorded` |
| `connection` | `connecting` \| `ok` \| `stale` \| `disconnected` | first poll / success / last success >3× interval while **visible** / fetch failure |

Also: `observe-only` subtitle in v0.1–v0.2 (“steering unavailable until v0.3”); `no-session` empty state.

Poll failure must not clear existing nodes; overlay disconnected chrome. After N consecutive failures, show relaunch command `rc spectate` (G2-11).

**Visibility (G2-11):** stop polling when `document.visibilityState === "hidden"`; resume on visible. `stale` only while visible. Hidden tab → zero requests (test row).

---

## Visual / UX (locked from design-system-spec; G1-9…G1-12)

- Three panes: Sessions (240) · Live graph (flex) · Inspector (320).
- Chrome: product name, density, columns, theme, **source badge**, **status legend placement**, **session filter**.
- Loop spine: Assemble → Model → Classify → Tools → Package → Context; tools branch from Execute.
- Customizable (persisted `localStorage`, namespaced `rc.spectate.v1.*`): `data-theme`, `data-density`, layout presets (`default` \| `graph-focus` \| `inspector-focus` \| `sessions-focus`), **agent-column** visibility (`agent_id` tracks, all on by default — no host-off defaults) (G2-9), legend placement (`footer` \| `inspector`), session filter query. Corrupt/missing storage → safe defaults (no throw).
- **`follow=latest` (G2-19):** re-targets only while no node is selected; non-synthetic sessions rank above synthetic; selecting a session pins via `history.replaceState(?session=)`; rail toggle restores follow. Show “following latest — session not pinned” when unpinned.
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
- Spectate CSP (HTML document): `default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'` (G2-20 — no `'unsafe-inline'`; token theming uses CSS variables / `el.style` from script, which CSP does not block)

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
- [ ] Write demo fixtures as **separate run dirs per harness** covering all 11 statuses across the gallery; rail shows several harness chips; each stream one harness; graph columns = `agent_id`; grok-bot capability-unknown (G3-4 / G4-2)
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
- [ ] Add thin routes to plugin server; mirror in root server; set `Cache-Control: no-store`, `nosniff`, Spectate CSP on HTML (G1-13); explicit Content-Type map (G2-17)
- [ ] Serve `/spectate` assets via `_read_spectate_*` helpers (Gate 32 body-diff) + extend parity checker to assert `/spectate` dispatch; `/__spectate` via `startswith("/__spectate")` for MH-33 (G2-5)
- [ ] Add `--no-reclaim` / `--open-path` via **module-level** named helpers in both copies, listed in Gate 32 `_BODY_DIFF_NAMES` (e.g. arg on shared `_bind_server` + `_open_browser(path)`) — never inline-only in `main()` (G3-6)
- [ ] Must-pass: same-project listener on 8000 + `--no-reclaim` binds another port and 8000 pid still alive, on **both** copies
- [ ] Behavioral smoke both servers: `/spectate?follow=latest` HTML 200; `/__spectate/sessions` JSON (G1-7, G1-14, G3-1)
- [ ] Run Gate 32 parity check + must-fail: mutated `_read_spectate_*` in one copy is caught
- [ ] Gate 142: forged-Host case against **plugin** server too (G2-20)
- [ ] `spectate_demo.py` writes a synthetic session under `.ravenclaude/runs/`
- [ ] Commit: `feat(spectate): store, demo writer, /__spectate poll API`

### Task 3: Spectate UI (gold-standard shell)

**Files:**
- Create `plugins/ravenclaude-core/dashboard-assets/spectate/{index.html,app.js,spectate.css,status-icons.svg}`
- Modify `scripts/generate-dashboards.py` Activity tab → Spectate entry card (`href=/spectate`)
- Modify `plugins/ravenclaude-core/dashboard-assets/README.md` — list Spectate as surface #3; estate surfaces inline `--rc-*`; Spectate is the runtime-`spectate.css` exception (G3-10 / G2-14)
- **Do not commit** regenerated `dashboard.html` / portal outputs (G1-15); exercise generator locally only

- [ ] CSS tokens from design-system-spec (dark default + light mirror) including **`denied-harness`** (G1-9)
- [ ] Three-pane layout + responsive breakpoints
- [ ] Status icon set (SVG) for all 11 statuses — shape + label; hexagon for `denied-harness`
- [ ] Session rail with harness chips + live/idle + **session filter** (G1-12)
- [ ] Loop spine graph + tool nodes; agent columns toggle
- [ ] Inspector: Overview / Policy / Payload — Payload scrubbed fields only (G1-10)
- [ ] Customization chrome: theme, density, layout preset, columns, legend placement → `localStorage` with safe defaults (G1-12)
- [ ] Source-mode badges + disconnected/stale/connecting/observe-only (G1-8)
- [ ] Poll `/__spectate/nodes?session=&since_etag=` every 2s while visible; events endpoint for inspector only (G2-16); never map poll failure → idle
- [ ] Pause polling when tab hidden (G2-11)
- [ ] Keyboard/a11y contracts (G1-11); reduced-motion — **manual** Task 5 evidence for breakpoints/focus-trap/reduced-motion (G2-15)
- [ ] Expose pure view/state helpers from `app.js` for Node stub checks; add `scripts/check-spectate-render.mjs` (disconnected+nodes kept, corrupt storage, all 11 statuses shape+label, no `innerHTML`) (G2-15)
- [ ] Smoke: open via both server entrypoints, load demo, verify all 11 statuses + capability-unknown
- [ ] On load: `session=` pins; otherwise `follow=latest` per G2-19. Never empty picker while a run file exists
- [ ] Commit: `feat(spectate): Spectate UI shell` (assets + generator source only)

### Task 3b: Launchers (`rc spectate`, `/spectate`)

**Files:**
- Modify `plugins/ravenclaude-core/bin/rc` — new `spectate` verb
- Modify both `serve-dashboards.py` copies — `GET /spectate` maps to plugin spectate assets (G1-7). Do not retarget bare `/`
- Create `plugins/ravenclaude-core/commands/spectate.md`

- [ ] `rc spectate [--session ID] [--no-open] [--port N] [--foreground]` — **attach, don't kill** (G2-2 / G3-5):
  - Probe: walk ports **8000–8010**; identity = lsof LISTEN + `ps` cmdline contains `serve-dashboards.py` + cwd equals this project; then `GET /__spectate/capabilities` must return 200. **Do not** call `open-dashboard.sh` `find_our_live_port` (it curls `/index.html` without following redirects and only walks `WALK=5`)
  - If live same-project server lacks `/__spectate`: leave it running; start a new server on the next free port with `--no-reclaim`; print the **new** URL and that the older server was left untouched (narrow upgrade-coexistence exception to SURFACE “no second port” — G4-5)
  - If `lsof` absent: fail closed → start second server; never kill
  - Always pass `--no-reclaim` when starting; never call `_reclaim_port` on the open path
  - Audit-gates must-pass: an old-style live server survives `rc spectate`
- [ ] Detach by default (G2-3 / G4-4): `mkdir -p .ravenclaude/runs` **before** redirect; then `nohup python3 serve-dashboards.py --no-reclaim --open-path '/spectate?…' … >.ravenclaude/runs/spectate-server.log 2>&1 &`, wait ≤5s for port, print URL, exit 0. `--foreground` keeps blocking. Clean-project launcher test: empty project (no prior `.ravenclaude/runs`) still starts
- [ ] Open browser rule (G3-12): `webbrowser` **only** for local attach with a TTY and without `--no-open`. Codespaces, no TTY, and `--no-open` **only print** the URL (forwarded `/spectate?...` in Codespaces). Never both print-and-launch in Codespaces
- [ ] Open URL `http://127.0.0.1:<port>/spectate?session=<id>` when an id is known, else `?follow=latest` (+ optional `&harness=`). `--no-open` prints URL + `session_id` / `harness` / `latest_status` for the session follow would select (G3-8)
- [ ] Session id order (G2-6 / G3-11): explicit `--session`, else `CLAUDE_SESSION_ID` when set, else `follow=latest`. Before writing `commands/spectate.md`, probe whether slash/command env expands a session id; **do not claim absence until that probe output is pasted into the doc**. Fallback if unavailable: `?follow=latest&harness=claude-code` + “following latest — session not pinned”
- [ ] `/spectate` slash is a thin sibling of `/dashboard` (Claude Code only). Same URL. Copilot/Codex/Cursor/Gemini use `rc spectate`
- [ ] Codespaces: print the forwarded `/spectate` URL. `onAutoForward` still opens `/` → dashboard; do not hijack `DASH_PATH`
- [ ] Activity entry card links to `/spectate`. It is not the smoke path
- [ ] Commit: `feat(spectate): rc spectate and /spectate open the session URL`

### Task 4: Knowledge + version + preflight

**Files:**
- Create `plugins/ravenclaude-core/knowledge/spectate.md`
- Create `plugins/ravenclaude-core/templates/run-artifacts/spectate-events.jsonl.template`
- Bump `plugins/ravenclaude-core/.claude-plugin/plugin.json` → next minor above origin/main (expect `0.330.0` if main is `0.329.1`) (G5-1)
- Update CHANGELOG if present
- Run sync + copilot generate

- [ ] Operator doc: how to open Spectate, demo mode, honesty about v0.1 (no hooks; observe-only)
- [ ] Author `knowledge/concepts/harness-spectate.md` (`entry_class: inventory`) covering `spectate_store.py`, `spectate_demo.py`, `commands/spectate.md` (and v0.2 `spectate-emit.sh` when added) (G2-1)
- [ ] `python3 scripts/generate-concepts-doc.py` and **commit** `docs/concepts.md`; `python3 scripts/check-artifact-freshness.py --check --surface index.html` — commit structural index drift if required. `dashboard.html` alone stays post-merge (G2-1)
- [ ] Version bump + `python3 scripts/sync-plugin-versions.py`
- [ ] `python3 scripts/generate-copilot-plugin.py`
- [ ] `npx prettier@3.9.4 --write .` then `--check .`; `ruff check .` (whole tree)
- [ ] `python3 scripts/ci-preflight.py`
- [ ] Full `scripts/audit-gates.sh` (not targeted-only) (G1-14)
- [ ] Commit: `chore(spectate): docs, template, bump core` (version from plugin.json)

### Task 5: Manual walkthrough evidence

- [ ] Start `serve-dashboards.py` (plugin **and** root modes), run demo, screenshot/record three-pane UI
- [ ] Save artifacts under `/opt/cursor/artifacts/`
- [ ] Push branch + open/update draft PR

---

## Tasks — v0.2 (follow-up PR)

- [ ] `hooks/spectate-emit.sh` — exit 0, empty stdout, scrubbed JSONL append; set `corr_id` from payload `tool_use_id` (G2-12)
- [ ] Extend `_emit_hook_event` with optional 7th arg `corr_id` (backward-compatible); deny join via `corr_id` only
- [ ] Register in `hooks/hooks.json` on SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStart, PreCompact
- [ ] Ensure projectors place or skip; pass `check-crosshost-hook-coverage.py`
- [ ] Grok-build env detection override; upgrade capability cells from measured probes; record per-harness `tool_use_id` support
- [ ] Add `spectate-emit.sh` to Gate 242 inventory `covers:` and regenerate concepts-doc
- [ ] Vendor IBM Plex OFL fonts
- [ ] Bump to next minor after v0.1

## Tasks — v0.3 (follow-up PR)

- [ ] `GET /__spectate/stream` SSE (≤4 streams, 15s heartbeat, Last-Event-ID)
- [ ] `POST /__spectate/steer` CSRF+Origin; posture `spectate_steer: on`
- [ ] Pause-as-deny + capped note injection where `steer_context` supported
- [ ] Bump to next minor after v0.2

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
| Poll failure UI | stub-DOM: disconnected badge, nodes retained |
| Hidden tab | zero poll requests over 10s while hidden |
| Customization persistence | set theme/density/legend/filter; reload; corrupt key → defaults |
| Stub UI gate | `node scripts/check-spectate-render.mjs` |
| Responsive + a11y | **manual** Task 5 at 3 widths + reduced-motion (not CI Chromium) |
| Attach-don't-kill | old live server survives `rc spectate` |
| Lint | whole-tree prettier + ruff |
| Preflight | `python3 scripts/ci-preflight.py` |
| Full gate audit | `scripts/audit-gates.sh` |
| Manual | demo walkthrough recording (both servers) |

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

## G1 / G2 close index

| ID | Close location |
|---|---|
| G1-1…G1-15 | Prior revision (capability, scrub, reducer, correlation, path, cursor, `/spectate`, source UI, design, Payload, a11y, customization, headers, tests, no dashboard.html commit) |
| G2-1 | File tree + Task 4 inventory concept + commit concepts-doc |
| G2-2 | Task 3b `--no-reclaim` + probe |
| G2-3 | Task 3b detach + `--open-path` |
| G2-4 | Canonical URL serve-not-302 + SURFACE amend |
| G2-5 | Task 2 `_read_spectate_*` + parity extend |
| G2-6 | Task 3b CLAUDE_SESSION_ID honesty + harness filter |
| G2-7 | Reducer seed map + deny.by + available rule |
| G2-8 | Source/connection axes + unterminated |
| G2-9 | Session-rail multi-harness; graph columns = agent_id |
| G2-10 | Target derivation + value scrub |
| G2-11 | Visibility-gated polling |
| G2-12 | v0.2 corr_id = tool_use_id |
| G2-13 | design-system-spec light contrast |
| G2-14 | design-system-spec relationship section |
| G2-15 | check-spectate-render.mjs + manual a11y |
| G2-16 | UI polls nodes only; bounds/turns |
| G2-17 | Explicit Content-Type map |
| G2-18 | Event-file symlink refuse |
| G2-19 | follow=latest pin semantics |
| G2-20 | CSP tighten, kind split, Gate 142 plugin, glyph/handoff notes in design spec |
| G3-1 | Query-strip before `/spectate` match + smoke |
| G3-2 | Seed precedence (unsupported/unknown beat 0-event idle) |
| G3-3 | `stream.truncated` in schema enum; drop `truncate_marker` name |
| G3-4 | Harness = rail chip; Task 1 demo wording |
| G3-5 | Probe without `find_our_live_port` /index.html |
| G3-6 | `--no-reclaim` / `--open-path` as Gate-32-named helpers |
| G3-7 | Guarded spectate HEAD; no ungated Allow list |
| G3-8 | Sessions payload fields + harness= filter |
| G3-9 | Absolute cursor + tail-start reset |
| G3-10 | README Task 3 file + surface #3 exception |
| G3-11 | Probe-before-claim for CLAUDE_SESSION_ID |
| G3-12 | Codespaces/no-TTY print-only open rule |
| G4-1 | Spectate refuses non-loopback even on `--bind 0.0.0.0` |
| G4-2 | One harness per stream; demo = separate run dirs |
| G4-3 | Session-summary reducer for `latest_status` |
| G4-4 | `mkdir -p` before spectate-server.log redirect |
| G4-5 | SURFACE narrow upgrade-coexistence second-port exception |
| G5-1…G5-13 | G5 closes section (version, bind helper, peer_ok, open ownership, validation, probe range, kind→step, nodes shape, deny join, read cache, demo first-sight, test homes, design tokens) |

---

## G5 closes (folded)

### G5-1 Version
See Global Constraints — next minor above `origin/main` at implement time (not hard-coded `0.329.0`).

### G5-2 `--no-reclaim` / root bind helper
- Extract root server's inline bind into a module-level `_bind_server(port, *, reclaim: bool, span: int)` present in **both** copies.
- Root keeps `span=6` (ports PORT..PORT+5); plugin may keep `span=10`. Helper takes `span` so they stay intentional.
- Add `_bind_server` and `_open_browser` to Gate 32 `_BODY_DIFF_NAMES` explicitly.
- Update `open-dashboard.sh` `WALK` to match the root span (`span-1`) when changing root; document the mirror.

### G5-3 G4-1 mechanism (Task 2 checklist + matrix)
- Spectate GET/HEAD handlers call `_spectate_peer_ok()` after `_local_request_ok()`: peer `client_address[0]` must be loopback (`127.0.0.1` / `::1`) **or** the request Host must be the exact Codespace forward host. LAN IP Host/Origin alone is insufficient when peer is non-loopback.
- In Codespaces the TCP peer is the forwarder — allow when Host matches the exact Codespace hostname:port already in `_ALLOWED_HOSTS`.
- Must-fail Gate 142-style: `--bind 0.0.0.0` + LAN-IP Host + non-loopback peer → 403 on `/spectate` and `/__spectate/*`.

### G5-4 Browser open ownership
- **`rc` owns open.** Always start the server with `--no-open`. After bind/attach succeeds, `rc` opens via `python3 -m webbrowser` only when local TTY and user did not pass `--no-open`. Codespaces / no TTY / `--no-open` → print only.
- Never pass `--open-path` to a detached nohup server for the purpose of opening a browser (server may still accept `--open-path` for foreground/debug).
- Discover bound port by probe (`GET /__spectate/capabilities` on candidate ports), not by parsing the log.
- Cap `spectate-server.log` at 2 MiB with truncate-on-start (or rotate once); document.

### G5-5 Launcher input validation
- `rc` validates `--session` / `CLAUDE_SESSION_ID` against the session_id regex; on mismatch print note and fall back to `follow=latest`.
- Server accepts `--open-path` only if it matches `^/spectate(/|\?|$)`; else refuse start.

### G5-6 Probe range
- Probe range is `[--port, --port+10]` (default base 8000). Gate tests for attach-don't-kill / clean-project use base ≥8015 so they never touch a developer dashboard on 8000.

### G5-7 kind → step map
| kind | step started/affected |
|---|---|
| `session.start` | seeds spine; no step running |
| `prompt.submit` | `assemble` then `call-model` (model call unobservable → leave `call-model`/`classify` as `available` if capability supported; never invent model tokens) |
| `tool.pre` | `execute-tools` + tool child |
| `tool.post` / `tool.fail` | tool child terminal; may advance toward `package` |
| `permission.request/resolve` | tool child / waiting-approval |
| `subagent.start/stop` | agent column lifecycle |
| `compact.pre` | `update-context` |
| `turn.end` / `session.end` | package/context complete or session terminal |
| `stream.truncated` / `emitter.truncated` | annotations only |

Unobservable steps stay `available` (or capability-unknown) — never inferred from silence.

### G5-8 `/__spectate/nodes` response shape
```json
{
  "session_id": "...",
  "harness": "...",
  "synthetic": false,
  "server_now": "RFC3339",
  "last_event_ts": "RFC3339|null",
  "session_ended": false,
  "source_hint": "demo|recorded|live",
  "nodes_truncated": false,
  "skipped_malformed": 0,
  "nodes": [ {"node_id","parent_id","agent_id","step","kind","status","capability_state","unterminated","deny","metrics","ts"} ]
}
```
UI computes live badge from `source_hint` / `server_now` vs `last_event_ts` (server clock), never browser clock alone.

### G5-9 Hook-deny join (v0.1 fixtures + v0.2)
- Map `hook`/`verdict` → `deny.by`: plugin-hook deny → `plugin`; user permission deny → `user`; harness-native → `harness`; org policy (when present) → `org`. Default `plugin` for marketplace hook denies.
- Joined `rule` = scrubbed, charset `[A-Za-z0-9._:/-]`, max 64 chars.
- Without `corr_id`: no join (status from spectate events only).
- Store refuses to append into a stream whose first event harness differs; session dir literally named `unknown` is listed but never auto-followed; demo never uses `unknown`.

### G5-10 Read-path cost
- Sessions summary cache keyed by `(path, mtime_ns, size)` → `{harness, synthetic, latest_status}`; invalidate on stat change.
- `/nodes` `etag` = `mtime_ns-size` from `stat` **before** reduce; 304 skips reduce.
- UI polls `/sessions` every 5s (rail / follow); `/nodes` every 2s while visible.

### G5-11 Fresh-project first sight
- `rc spectate --demo` (and in-page “Load demo” when sessions empty) runs `spectate_demo.py` writing synthetic per-harness dirs under `.ravenclaude/runs/`.
- Demo data ships inside the plugin (or is generated by `spectate_demo.py`); fixtures under `tests/fixtures/` are CI-only.
- Pinned `?session=` missing/invalid/empty → empty-state “session not found / no events yet” + button to follow-latest or load demo — never a blank graph pretending live.
- `/__runs` Activity feed skips dirs whose only artifact is `spectate-events.jsonl` with `synthetic: true` (or mark them DEMO so they don’t pollute posture Activity).

### G5-12 Executable test homes
- Wire `check-spectate-render.mjs` into `audit-gates.sh` (must_pass / must_fail) + CI node step; skip loud if `node` absent locally.
- Behavioral smoke + header assertions: `scripts/check-spectate-http.sh` (or python) hitting both servers; in audit-gates.
- Hidden-tab: stub-DOM fake clock / visibilityState toggle — **no sleep-based timing**.
- Attach-don't-kill + clean-project: gate script with base port ≥8015; skip loud if `lsof` absent.

### G5-13 Design tokens
- Swap tertiary/secondary hierarchy: tertiary must be lower contrast than secondary (use `neutral-400` for tertiary if needed).
- `available` stroke uses `--color-neutral-200` / blue-info — **not** accent teal. Teal remains selection/focus/active-edge only. Update design-system-spec status tokens accordingly.

## Success criteria (v0.1 gold bar)

1. User runs `rc spectate` (or `/spectate`) and lands on the live/demo session in ≤2 actions — Activity is never required.
2. Demo session shows all 11 statuses with shape + label; grok-bot shows **capability unknown**, not a false `unavailable-harness`.
3. Theme / density / layout / columns / legend / filter persist across reload; corrupt storage safe-defaults.
4. Polling updates the graph without full page refresh; poll failure shows disconnected, not idle.
5. No secrets or raw prompts/args/results appear in network responses or Payload tab.
6. Feels like a Cursor/Claude/Codex tool — dense, calm, teal accent only for focus.
7. `/spectate` works from both plugin and root `serve-dashboards.py` entrypoints.
