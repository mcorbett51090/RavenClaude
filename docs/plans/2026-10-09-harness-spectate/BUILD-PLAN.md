# Harness Spectate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a gold-standard, multi-harness livestream Spectate surface so users can see, understand, and (later) direct coding-agent harness activity in real time — familiar to Cursor / Claude Code / Codex, simple, highly customizable.

**Architecture:** Local loopback web app under `plugins/ravenclaude-core/dashboard-assets/spectate/`, served by `serve-dashboards.py`. Event bus is append-only `.ravenclaude/runs/<id>/spectate-events.jsonl`. Statuses are *derived on the server* from events + capability matrix + hook-deny join — never inferred from silence. One observe-only emitter hook (v0.2) rides existing host adapters. Steering (v0.3) is opt-in via comfort posture; ACP process-ownership is deferred.

**Tech Stack:** Vanilla HTML/CSS/JS (no framework, no build step), Python 3 (`spectate_store.py`), existing dashboard server + CSRF, IBM Plex Sans/Mono (vendored woff2 from v0.2), JSON Schema gate.

**Companion specs:**
- Visual system: [`design-system-spec.md`](./design-system-spec.md)
- Atlas: `docs/research/2026-10-04-coding-agent-harness-atlas/`
- Loop concept: `plugins/ravenclaude-core/knowledge/concepts/agent-harness-loop.md`

## Global Constraints

- Surface is **loopback-only** (127.0.0.1 / Codespaces); no Electron; no new backend service (`docs/dashboard-buildout-plan.md` §5.9).
- Ship inside **`ravenclaude-core`** (domain-neutral Observe infrastructure). No premature plugin split.
- Support harnesses: `claude-code`, `codex-cli`, `copilot-cli`, `copilot-vscode`, `cursor`, `gemini-cli`, `grok-build`, `grok-bot` (honest `unavailable-harness`).
- **No raw prompts / tool output / secrets** in spectate payloads (Streams Gate 110 discipline).
- Both `scripts/serve-dashboards.py` and `plugins/ravenclaude-core/scripts/serve-dashboards.py` stay byte-parity on wrappers (Gate 32).
- Never add CORS. CSRF + Origin for state-changing routes.
- UI uses `textContent` only — no `innerHTML`.
- Status never color-only: **color + shape + exact label** (11 statuses including `denied-harness`).
- Silence ≠ unavailable. Empty feed → `idle` + “never seen — cause not established” (`cause-taxonomy.md`).
- Layout globs already cover all paths; do not invent top-level dirs.
- Version: bump `ravenclaude-core` from `0.328.0` → `0.329.0` for v0.1; then `sync-plugin-versions.py` + `generate-copilot-plugin.py`.
- Docs under `docs/plans/` land with the PR that ships product code (this feature is not docs-only).

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

Canonical URL: `/spectate` (302 to `/dashboard-assets/spectate/`). Query: `?session=<id>` when the opener has one, else `?follow=latest`. Guardrails stay Heimdall / Víðarr.

---

## File tree (v0.1–v0.3)

```
plugins/ravenclaude-core/
  knowledge/spectate-event-schema-v1.json
  knowledge/spectate-capabilities.json
  knowledge/spectate.md
  scripts/spectate_store.py
  scripts/spectate_demo.py
  scripts/serve-dashboards.py              # thin /__spectate/* wrappers
  hooks/spectate-emit.sh                   # v0.2
  hooks/tests/test-spectate-emit.sh        # v0.2
  dashboard-assets/spectate/
    index.html
    app.js
    spectate.css
    status-icons.svg
    fonts/                                 # v0.2 OFL woff2
  templates/run-artifacts/spectate-events.jsonl.template
scripts/
  serve-dashboards.py                      # parity wrappers
  check-spectate.py                        # new gate
  generate-dashboards.py                   # Activity entry card
tests/fixtures/spectate/
  demo-session.jsonl
  hook-events-deny.jsonl
  bad-raw-prompt.jsonl
  bad-status.jsonl
  expected-reduce.json
docs/plans/2026-10-09-harness-spectate/
  BUILD-PLAN.md
  design-system-spec.md
  gap-analysis.md
```

---

## Event schema v1 (locked)

Each JSONL line:

| Field | Rules |
|---|---|
| `schema` | `"rc.spectate.v1"` |
| `ts` | RFC 3339 UTC ms |
| `session_id` | sanitized `[A-Za-z0-9._-]{1,128}` |
| `harness` | enum of 8 + `unknown` |
| `source` | `hook` \| `demo` \| `steer` |
| `kind` | `session.start/end`, `prompt.submit`, `turn.end`, `tool.pre/post/fail`, `permission.request/resolve`, `subagent.start/stop`, `compact.pre`, `steer.applied`, `emitter.truncated` |
| `step` | `assemble` \| `call-model` \| `classify` \| `execute-tools` \| `package` \| `update-context` |
| `node_id` / `parent_id` / `agent_id` | stable IDs |
| `tool` | `{name, family, target}` — scrubbed; no args/output |
| `asserted_status` | optional harness-stated status |
| `deny` | `{by, source, rule}` or null |
| `metrics` | numbers only (`duration_ms`, `out_bytes`, `prompt_chars`) |
| `detail` | `minimal` \| `standard` |
| `synthetic` | bool |

**Reducer statuses (11):** `available`, `unavailable-harness`, `denied-org`, `denied-plugin`, `denied-user`, `denied-harness`, `running`, `succeeded`, `failed`, `waiting-approval`, `idle`.

**Capability matrix** keys (`spectate-capabilities.json`): `session`, `prompt`, `tool_pre`, `tool_post`, `tool_fail`, `permission_request`, `subagent`, `compact`, `stop`, `deny_plugin`, `deny_harness_visible`, `deny_user_visible`, `deny_org_visible`, `steer_context`. Seeded from atlas F06; grok-bot all `undocumented` → UI `unavailable-harness`.

---

## Visual / UX (locked from design-system-spec)

- Three panes: Sessions (240) · Live graph (flex) · Inspector (320).
- Chrome: product name, density, columns, theme. Hairlines, not cards.
- Loop spine: Assemble → Model → Classify → Tools → Package → Context; tools branch from Execute.
- Customizable: `data-theme`, `data-density`, layout presets (`default` \| `graph-focus` \| `inspector-focus` \| `sessions-focus`), agent-column visibility — persisted in `localStorage`.
- Motions: running pulse, edge draw + node enter, inspector cross-fade; honor `prefers-reduced-motion`.
- Type: IBM Plex Sans + Mono (fallback stack in v0.1; vendored fonts v0.2).

---

## Phased delivery

### v0.1 — Demo + poll + gold UI (THIS PR)

Complete, beautiful, customizable Spectate on synthetic + fixture data; polls real `spectate-events.jsonl` when present. No hooks yet.

### v0.2 — Real hooks

`spectate-emit.sh` + host projection + deny join + font vendor + measured probes.

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

- [ ] Write schema JSON (required fields, enums, additionalProperties false on root)
- [ ] Write capabilities matrix for all 8 harnesses with atlas evidence ids where known
- [ ] Write demo-session.jsonl covering all 11 statuses + multi-harness columns
- [ ] Write bad fixtures (raw prompt field, illegal status)
- [ ] Write `expected-reduce.json` golden for reducer
- [ ] Implement `check-spectate.py --check` (pass demo; fail bad fixtures; fail missing evidence)
- [ ] Add must-pass / must-fail rows to `audit-gates.sh`
- [ ] Run: `python3 scripts/check-spectate.py --check` → exit 0
- [ ] Commit: `feat(spectate): schema, capabilities, fixtures, Gate check-spectate`

### Task 2: `spectate_store.py` + `/__spectate` routes

**Files:**
- Create `plugins/ravenclaude-core/scripts/spectate_store.py`
- Create `plugins/ravenclaude-core/scripts/spectate_demo.py`
- Modify both `serve-dashboards.py` copies (thin wrappers only)

Endpoints (GET, read-only, Host-checked):
- `/__spectate/sessions`
- `/__spectate/events?session=&cursor=&limit=` (opaque byte-offset cursor; limit ≤ 500)
- `/__spectate/capabilities`
- `/__spectate/nodes?session=` (reduced node statuses)

- [ ] Implement allow-list parse + re-scrub + 5 MB cap semantics
- [ ] Implement `reduce(events, hook_denies, capabilities) → nodes`
- [ ] Golden test: fixtures → `expected-reduce.json` (never-seen → `idle`, not `unavailable-harness`)
- [ ] Add thin routes to plugin server; mirror in root server
- [ ] Run Gate 32 parity check
- [ ] `spectate_demo.py` writes a synthetic session under `.ravenclaude/runs/`
- [ ] Commit: `feat(spectate): store, demo writer, /__spectate poll API`

### Task 3: Spectate UI (gold-standard shell)

**Files:**
- Create `plugins/ravenclaude-core/dashboard-assets/spectate/{index.html,app.js,spectate.css,status-icons.svg}`
- Modify `scripts/generate-dashboards.py` Activity tab → Spectate entry card
- Regenerate dashboard.html via generator

- [ ] CSS tokens from design-system-spec (dark default + light mirror)
- [ ] Three-pane layout + responsive breakpoints
- [ ] Status icon set (SVG) for all 11 statuses — shape + label
- [ ] Session rail with harness chips + live/idle
- [ ] Loop spine graph + tool nodes; agent columns toggle
- [ ] Inspector: status, deny source, capability evidence, metrics, timing
- [ ] Customization chrome: theme, density, layout preset, columns → `localStorage`
- [ ] Poll `/__spectate/*` every 2s; DEMO badge for synthetic sessions
- [ ] Grep gate / assert: no `innerHTML` in spectate assets
- [ ] Smoke: open via `serve-dashboards.py`, load demo session, verify all statuses visible
- [ ] On load: `session=` pins; otherwise `follow=latest` selects the newest session. Never an empty picker while a run file exists. Poll failure renders disconnected, not `idle`
- [ ] Commit: `feat(spectate): Spectate UI shell`

### Task 3b: Launchers (`rc spectate`, `/spectate`)

**Files:**
- Modify `plugins/ravenclaude-core/bin/rc` — new `spectate` verb
- Modify both `serve-dashboards.py` copies — `GET /spectate` 302; open-path flag. Do not retarget bare `/`
- Create `plugins/ravenclaude-core/commands/spectate.md`

- [ ] `rc spectate [--session ID] [--no-open] [--port N]` starts the server only when this project has none. If one is already listening, open against that port. Do **not** call `_reclaim_port` on a live server — that SIGTERMs any `serve-dashboards.py` whose cwd is this project, with no idle check
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

- [ ] Operator doc: how to open Spectate, demo mode, honesty about v0.1 (no hooks yet)
- [ ] Version bump + `python3 scripts/sync-plugin-versions.py`
- [ ] `python3 scripts/generate-copilot-plugin.py`
- [ ] prettier + ruff on touched files
- [ ] `python3 scripts/ci-preflight.py` + targeted audit rows
- [ ] Commit: `chore(spectate): docs, template, bump core 0.329.0`

### Task 5: Manual walkthrough evidence

- [ ] Start `serve-dashboards.py`, run demo, screenshot/record three-pane UI
- [ ] Save artifacts under `/opt/cursor/artifacts/`
- [ ] Push branch + open/update draft PR

---

## Tasks — v0.2 (follow-up PR)

- [ ] `hooks/spectate-emit.sh` — exit 0, empty stdout, scrubbed JSONL append
- [ ] Register in `hooks/hooks.json` on SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStart, PreCompact
- [ ] Ensure projectors place or skip; pass `check-crosshost-hook-coverage.py`
- [ ] Grok-build env detection override
- [ ] Deny join from `hook-events.jsonl`
- [ ] Vendor IBM Plex OFL fonts
- [ ] Bump to `0.330.0`

## Tasks — v0.3 (follow-up PR)

- [ ] `GET /__spectate/stream` SSE (≤4 streams, 15s heartbeat, Last-Event-ID)
- [ ] `POST /__spectate/steer` CSRF+Origin; posture `spectate_steer: on`
- [ ] Pause-as-deny + capped note injection where `steer_context` supported
- [ ] CSP header on spectate assets
- [ ] Bump to `0.331.0`

## Deferred (v0.4+)

- Approve/deny waiting-approval from browser
- True interrupt
- ACP control channel (process ownership)
- VS Code extension deep-link
- Claude monitor push mirror

---

## Testing matrix (v0.1)

| Check | Command / method |
|---|---|
| Schema + fixtures | `python3 scripts/check-spectate.py --check` |
| Reducer golden | unit inside check-spectate / spectate_store |
| Server parity | Gate 32 |
| No CORS | Gate 142 cases for `/__spectate` |
| Lint | prettier + ruff |
| Preflight | `python3 scripts/ci-preflight.py` |
| UI a11y | status shape+label; reduced-motion; contrast per design spec |
| Manual | demo session walkthrough recording |

---

## Security checklist

- [x] No raw prompts in schema
- [x] Dual scrub (write + read)
- [x] Host check on GET; CSRF+Origin on steer (v0.3)
- [x] No CORS
- [x] No `innerHTML`
- [x] File size cap + truncate marker
- [x] Synthetic flag for demo

---

## Open questions (resolved for v0.1)

| Q | Decision |
|---|---|
| Steering in Codespaces? | Defer to v0.3; same CSRF/Origin rules as other dashboard POSTs |
| Default detail level | `minimal` for shell targets; `standard` for path/domain |
| `denied-org` | Reserved; matrix marks `deny_org_visible` unsupported/unverified until probed |
| Status naming | `denied-harness` (matches `denied-org` pattern); hexagon shape |

---

## Success criteria (v0.1 gold bar)

1. User opens Spectate from Activity and immediately understands the three-pane composition.
2. Demo session shows all 11 statuses with shape + label; grok-bot column shows `unavailable-harness` with atlas-backed reason.
3. Theme / density / layout / columns persist across reload.
4. Polling updates the graph without full page refresh.
5. No secrets or raw prompts appear in network responses.
6. Feels like a Cursor/Claude/Codex tool — dense, calm, teal accent only for focus.
