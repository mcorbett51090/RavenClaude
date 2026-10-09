# Harness Spectate — Surface decision (friction-first)

**Status:** LOCKED (2026-10-09, Pass C)  
**#1 criterion:** Frictionless use (time-to-first-sight + stay-in-flow)  
**Secondary:** Multi-harness reach, RavenClaude constraints (§5.9 no new backend service / no Electron), familiarity, customization, steer path.

This file is the **source of truth for surface**. The build plan must not contradict it once locked.

---

## The friction problem (why surface dominates)

Spectate fails if watching the harness is harder than just staring at the agent transcript.

| Anti-pattern | Why it kills the product |
|---|---|
| “Open the comfort-posture dashboard, find Activity, click Spectate” | Second home; unrelated chrome; >5 steps |
| “Install a VS Code extension first” | Blocks CLI-only users; existing extension is Copilot-precompact-only |
| “Start Electron / Docker / another service” | Violates §5.9; another process to babysit |
| “Learn a new TUI that isn’t your agent” | Splits attention; poor multi-harness graph |
| Fake live status when no emitter | Trains distrust |

**Gold bar:** From “I want to watch” → live feed of the *current* session in ≤2 actions on the host you’re already using.

---

## Pass 0 — Orchestrator evidence (this session)

### What already exists (reuse, don’t reinvent)

| Asset | Path / fact | Friction implication |
|---|---|---|
| Loopback server | `serve-dashboards.py` via `rc dashboard` / `/dashboard` | Zero new backend; already CSRF + Host-checked |
| One-verb launcher | `rc dashboard` auto-opens browser | Proven pattern; extend to `rc spectate` |
| Slash command | `/dashboard` | Claude Code users already know this shape → add `/spectate` |
| VS Code extension | `vscode-extension/` = **Precompact Guard only** — cannot see live Chat | Not a spectate bus today; webview would be greenfield |
| Host hooks | Projected for claude/copilot/codex/cursor/gemini | Event *collection* is host-agnostic; *UI chrome* need not be |
| Dashboard note | Codespaces: prefer real browser tab, not Simple Browser, keep port Private | Steer/save need real browser; observe-only can be Simple Browser |

### Candidate surfaces (shortlist)

1. **Dedicated Spectate URL on existing loopback server** (`/spectate` → assets) — not buried in Activity chrome  
2. **`rc spectate` / `/spectate`** — one verb, auto-start server if needed, open URL with `?session=` for active run  
3. **Cursor/VS Code webview or Simple Browser** wrapping the same URL — stay-in-IDE for P1  
4. **Activity dashboard tab only** — prior lean; high “second home” risk  
5. **TUI companion** — CLI stay-in-flow for P2/P3; weak for gold viz  
6. **ACP spectator client** — richest protocol stream; requires owning/attaching agent process  
7. **Electron / new service** — rejected (§5.9)

### Pass 0 provisional lean (NOT locked)

**Primary delivery vehicle:** same loopback server + **first-class Spectate page** (not a nested dashboard tab).  
**Primary entry points (friction layer):**

| Host | ≤2-action open |
|---|---|
| Any (CLI) | `rc spectate` → browser to live/latest session |
| Claude Code | `/spectate` → same |
| Cursor / VS Code | Command “RavenClaude: Open Spectate” → Simple Browser / external browser to same URL (v0.1 can shell-open; webview later) |
| Copilot CLI | `rc spectate` or ask agent to open |

**Secondary (same assets):** optional IDE sidebar webview in a later phase — **same HTML/JS**, no fork.  
**Not primary:** burying Spectate inside the full comfort-posture dashboard IA.  
**Not v0.1:** ACP process ownership, Electron, TUI-as-main.

Rationale: one codebase (static Spectate SPA + `/__spectate` API); many doors. Friction lives in the *doors*, not a second product.

---

## Pass A — product-strategist (claude-opus-5-5-high) — COMPLETE

**Agent:** [product-strategist](bc-9ecae830-b072-5d8e-9126-473e7ed73814)  
**Verdict:** Keep the web UI; kill dashboard-tab primacy. Highest scored option (37/40).

**Primary (v0.1):** Option 9 — one web UI, many entry points.
- Own URL `/spectate` (alias of `/dashboard-assets/spectate/`) on existing `serve-dashboards.py` — no second server/port.
- Idempotent `rc spectate`: reuse/start server, open `?follow=latest`.
- Claude `/spectate` alias.
- Activity card stays as *one* entry point, never the required path.

**Secondary (v0.2 with real hooks):**
- SessionStart / status-line `Spectate →` link where host supports it (Copilot `-p` skips SessionStart — measured).
- ~20-line IDE command opening **built-in Simple Browser** on same URL — no second UI codebase.
- Optional auto-start server from SessionStart behind opt-in posture (not default).

**Later:** `rc spectate --tail` line stream if CLI users ask. Not curses TUI.

**Do not build:** extension panel with own UI · separate server · ACP client (can't attach mid-run) · Electron · full TUI · vendor remote-control integrations · Claude-only surface.

**Score insight:** Prior lean (dashboard tab) = 31; loses only on time-to-first-sight (2) and stay-in-flow (2) — the #1 criterion. Fix the *path*, keep the *vehicle*.

**Friction bans (add to v0.1):** no dashboard navigation required · no HTML regen for events · no extension required · no second port · no empty picker while a run is live (`follow=latest` + pin) · auto-poll ≤2s · GET/view never CSRF-bounces · no setup wizard before first sight · attach-only (don't launch agents) · host-agnostic launcher (agent may run `bin/rc` by full path) · never blank (show emitter/waiting).

**Unverified assumptions flagged:** Cursor Simple Browser availability; clickable status-line links; Codespaces Simple Browser + port forwarding.

## Pass B — ux-designer (gpt-5.6-sol-high) — COMPLETE

**Agent:** [ux-designer](bc-b5473010-dbde-57e4-9c8a-6f180574031a)  
**Verdict:** Aligns with Pass 0. Strengthens chrome placement.

**Primary:** One local-first Spectate app with host-native entry points. Canonical experience = direct full-page `/spectate` on existing local runtime. Same responsive UI can render as a narrow IDE panel.

**Do not:** Make Spectate primarily a dashboard tab (discovery only). Dashboard nesting wastes the three-pane width in `design-system-spec.md`.

**Friction ranking (5 = lowest friction):** adaptive local app + native launchers **4.8** ≫ slash→browser 4.2 ≫ dual products 4.0 ≫ dashboard tab 3.8 ≫ TUI 3.4 ≫ standalone SPA 3.2 ≫ IDE-only 1.8.

**Open contracts (≤2 actions):**

| Host | Primary | Fallback |
|---|---|---|
| Cursor / VS Code | Click `Spectate ●` → right panel | Command Palette → `Spectate: Open` |
| Claude Code | `/spectate` | Printed `Open Spectate` link |
| Codex / Copilot / Gemini / Grok CLIs | `rc spectate` | Printed link |
| Copilot VS Code | Command Palette → `Spectate: Open` | Status control |
| Team lead / browser | Pinned Spectate tab | Dashboard → Spectate discovery |

Every launcher deep-links repo + active session. Never open a generic landing when context exists.

**Chrome placement:**
- **Cursor/VS Code:** right secondary sidebar = *glance mode* (current action, blockers, approvals) — not a squeezed three-pane; link to full view.
- **CLI hosts:** terse in-terminal status + link; full page in browser on demand.
- **Browser:** full three-pane composition; quiet escape link to dashboard only.
- **Overlay:** transient only (search / urgent approval) — never the sustained feed.

**Opening states required:** connecting · live · no active session · disconnected/error+retry · completed.

**Distinction vs “dual IDE+web”:** one app, one interaction model, multiple shells — not two products that drift.

## Pass C — web-architect (grok-4.7-high) — COMPLETE (locked)

**Agent:** [web-architect](bc-ed95ba74-af5f-5209-8171-70410eeb9449)  
**Verdict:** The prior lean (Activity tab as the door) is the second home. Keep the vehicle. Change the door.

**Primary vehicle:** one static page, `plugins/ravenclaude-core/dashboard-assets/spectate/`, served by the existing `serve-dashboards.py`. No new process, no new port, no framework. Poll `GET /__spectate/*` (SSE in v0.3).

**Primary doors (v0.1, both required):**

| Door | Who | Lands on |
|---|---|---|
| `rc spectate` | every host | system browser, spectate URL, session already selected |
| `/spectate` | Claude Code only | the same URL. Thin sibling of `/dashboard` |

**Not a door:** finding Observe → Activity inside the posture dashboard. That card stays as a link for someone already there.

### 1. Can a Cursor / VS Code webview host the same assets with zero duplication?

The files, yes. The embedded panel, no — not without breaking the guard or copying the UI.

Observations from `plugins/ravenclaude-core/scripts/serve-dashboards.py`:

- Static files are served from `PLUGIN_DIR`. One directory is the whole UI.
- Every GET, including the static fallback, calls `_local_request_ok()` (around the static-fallback comment after `do_GET`). That rejects a present `Origin` outside `{http://127.0.0.1:<port>, http://localhost:<port>}` plus the exact Codespace host, and rejects `Sec-Fetch-Site` when it is present and not `same-origin` or `none`.
- `_ALLOWED_ORIGINS` is built in `main()` from those loopback (and exact Codespace) strings only. There is no `vscode-webview://` entry. The file header on `_local_request_ok` forbids adding `Access-Control-Allow-Origin`.
- `commands/dashboard.md` tells the user to open a real browser tab, not VS Code Simple Browser / Live Preview, which sandboxes the page and shows “content is blocked”.
- `vscode-extension/` is the Precompact Guard (`package.json` name `ravenclaude-precompact-guard`). It has no webview contribution.

Inference, not a live webview test: a panel that loads the HTML via `asWebviewUri` makes `fetch('/__spectate')` hit the webview origin, not the Python server. A panel that iframes `http://127.0.0.1` is a cross-site or sandboxed embed; a present `Origin: null` or `Sec-Fetch-Site: cross-site` is a 403 under the guard as written. Do not widen the allow-list to make the embed work.

Zero duplication means: host chrome calls the system browser (`webbrowser.open` now, `vscode.env.openExternal` later) on the loopback URL. It does not mean a second HTML tree, and it does not mean Simple Browser.

Pass B’s right-hand glance panel is the same constraint. It is not v0.1. If it is ever built, it is `?chrome=glance` on this page after a top-level load from that webview is shown to pass `_local_request_ok`. Until that probe exists, do not promise the panel.

Pass A’s “Simple Browser command in v0.2” is rejected. The dashboard command already records that host as blocked.

### 2. Can `rc spectate` open the UI in one command and auto-load the session?

Yes. `bin/rc` `dashboard)` already `exec`s `serve-dashboards.py` with the caller’s cwd as project root. `main()` already calls `webbrowser.open` on a local URL. Today that URL is hardcoded to `DASH_PATH` (`/dashboard.html`). The spectate verb sets a different open path. It does not land on the posture editor.

Auto-load is the opener’s job. The server does not know which session is “active”.

1. `--session` if passed.
2. Else `CLAUDE_SESSION_ID` when set (the run-directory key in `knowledge/run-state-monitor.md`; Codex/Gemini shims export it).
3. Else `follow=latest`: the page selects the newest session from `GET /__spectate/sessions`.

Pin beats follow. `rc spectate` with no id opens `?follow=latest`, so a live run is selected and the rail still lets you switch. No modal, no empty picker.

Attach, don’t kill. `_reclaim_port` SIGTERMs every `serve-dashboards.py` whose cwd is this project. The docstring says “stale”; the function does not check idle time. `rc spectate` must probe for a live server of this project and open against that port. It starts a server only when none is listening. It must not call `_reclaim_port` on the open path.

`--no-open` prints the URL and one status line from the store (session, harness, latest derived status). That print is the CLI fallback. It is not a TUI.

Codespaces: `webbrowser.open` is skipped, and `onAutoForward` opens `DASH_PATH`. Print the forwarded `/spectate?...` URL. Do not retarget bare `/`, or `rc dashboard` and `rc spectate` fight over one process.

`rc dashboard --spectate` may alias the verb. The name people learn is `rc spectate`.

### 3. Can `/spectate` deep-link the browser to the right session?

Yes, Claude Code only. Same shape as `commands/dashboard.md`: Bash, start or reuse the server, open the spectate URL with `?session=$CLAUDE_SESSION_ID` when that variable is set, else `?follow=latest`. Copilot has no user slash commands; Copilot, Codex, Cursor, and Gemini use `rc spectate`. A slash-only surface fails multi-host, which the old lock already said.

Add `GET /spectate` and `GET /spectate/` **as a served route** (not a 302) that maps to `plugins/ravenclaude-core/dashboard-assets/spectate/` on **both** server copies. A 302 to `/dashboard-assets/spectate/` 404s under the root marketplace server (`directory=REPO_ROOT`). Leave `GET /` → `/dashboard.html`. Asset URLs inside the page are absolute (`/spectate/app.js`). Query strings (`?session=` / `?follow=latest`) are preserved because there is no redirect.

### 4. ACP spectator vs JSONL tail

JSONL tail through v0.3. The bus is `.ravenclaude/runs/<id>/spectate-events.jsonl`. Hooks and the demo writer append. The reducer in `spectate_store.py` is the only interpreter. The page polls `/__spectate/nodes`.

ACP is worth it only when all three are true: the harness speaks ACP, it has no hook or JSONL the emitter can join, and that harness is one you need live (not an honest `unavailable-harness`). When that day comes, ACP is a writer into the same JSONL. It is not a client UI and it does not own the agent process. Process ownership is a new runtime beside the server §5.9 already refused to add. OTel is the same rule: a source adapter, not a surface. v0.3 steer stays `POST /__spectate/steer` with the existing CSRF and Origin checks.

### 5. TUI and web — one event bus?

One bus, one reducer. The web page is the product. A curses TUI in v0.1 splits the three-pane goal and ships a second interaction model. Do not build it.

v0.1 CLI-only behavior is the `--no-open` print. A later `rc spectate --tail` (plain lines, same reducer) is allowed only if browser-open goes unused. No second schema.

### What shares one codebase vs host chrome

| Shared, one tree | Host chrome only |
|---|---|
| `dashboard-assets/spectate/*` | `rc spectate` verb |
| `spectate_store.py` reducer | `commands/spectate.md` |
| event schema + capability matrix | later: an `openExternal` command |
| `/__spectate` routes, both server copies (Gate 32) | Activity card href |

### Hard no

- Electron, or any new dashboard backend (`docs/dashboard-buildout-plan.md` §5.9).
- A second port or a second server process for Spectate.
- React, a bundler, or a copied three-pane inside `vscode-extension/`.
- CORS, or adding `vscode-webview://` / `*` to `_ALLOWED_ORIGINS`.
- Simple Browser, Live Preview, or an embedded webview as a supported host.
- ACP or OTel as the v0.1 client.
- A TUI product in v0.1.
- Spectate’s only door being the Activity tab.
- `innerHTML`, raw prompts, tool output, or secrets in the feed.
- Inferring status from silence. Poll failure is disconnected, not `idle`.
- `rc spectate` reclaiming (killing) a live dashboard server.
- Retargeting bare `/` at the spectate page.

### Phased rollout

| Phase | Ships | Does not ship |
|---|---|---|
| v0.1 | Page, poll, `/spectate` alias, `rc spectate`, `/spectate`, `session` / `follow=latest`, Activity card as a link, demo data | Hooks, IDE panel, TUI, ACP |
| v0.2 | Observe-only emit hook so the opened session is real | Steer, webview |
| v0.3 | SSE + opt-in steer on the same page | ACP process ownership |
| Later, only if the door still fails | `openExternal` command; `?chrome=glance` after a guard probe passes; `--tail` if headless use is real; ACP/OTel writers into the same JSONL for a harness with no hook | A second UI |

---

## Lock (2026-10-09, after A/B/C)

Passes 0, A, B, and C agree on the vehicle and the doors. C overrules two chrome ideas:

| Topic | Lock |
|---|---|
| Vehicle | Existing loopback server + one static page |
| v0.1 doors | `rc spectate` and `/spectate`. Activity card = discovery only |
| Deep link | `?session=<id>` pin when known, else `?follow=latest` |
| IDE | Not v0.1. Later door is the system browser via `openExternal`. Not Simple Browser. Glance panel only after a `_local_request_ok` probe |
| Bus | `spectate-events.jsonl` + one reducer. ACP/OTel are later writers, not clients |
| TUI | Not a product. `--no-open` prints a URL and one status line |

## Decision one-liner

> Spectate is one loopback page. `rc spectate` and `/spectate` open it on the current session. The Activity tab is a link, not a home. IDE panels, ACP, and a TUI do not get their own UI.

---

## Friction killers banned in v0.1

- [x] Requiring navigation through the posture dashboard to reach Spectate
- [x] Requiring an extension install or Marketplace publish before first sight
- [x] Electron, Docker, or a second server/port
- [x] Opening with no session selected while a run file exists
- [x] Rendering poll failure as `idle`
- [x] A second copy of the UI for the IDE
- [x] A modal or a squeezed three-pane as the sustained feed
- [x] Simple Browser / webview embed as a supported host *(Pass C)*
- [x] Killing a live `serve-dashboards.py` in order to open Spectate *(Pass C)*
