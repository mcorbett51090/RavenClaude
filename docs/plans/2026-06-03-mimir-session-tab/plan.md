# Plan — Mímir Session-State Dashboard Tab

**Slug:** `mimir-session-tab` · **Depth:** quick · **Date:** 2026-06-03 · **Route:** stays local (pending G7)
**Synthesized from:** `plan-A.md` (Opus, system-architect), `plan-B.md` (Sonnet, claude-code-mechanics), `gap-delta.md`. Resolutions applied per gap-delta column 5.

---

## Why we're doing this

Matt opened `/status`, `/usage`, `/effort`, `/theme` in his Claude Code session and asked whether that info appears in the RavenClaude dashboard. Today: **no.** The dashboard reads from `.ravenclaude/runs/*/*.jsonl` + manifests + `git log` — not from Claude Code's own session state. Per Matt's memory `feedback_dashboards_over_slash_commands`: "every tool, setting, AND activity metric visible in a dashboard; no memorized commands."

This /forge adds a new generated tab — **"Session"** (Norse alias **"Mímir's well"**) — that surfaces what's actually reachable from on-disk Claude Code session-state files: the persistent knobs in `~/.claude/settings.json`, the per-project session JSONLs in `~/.claude/projects/<encoded>/`, the pre-computed activity aggregates in `~/.claude/stats-cache.json`, and the live-session index in `~/.claude/sessions/<pid>.json`. Anything in-process-only (`/effort` dial, `/status` cached view) renders as an honest empty state with a pointer ("in-process — run `/status` in Claude Code") — not a mock.

---

## Phase 0 — Reachability research (DONE in panels — persisted here)

Panel B (Sonnet, claude-code-mechanics lens) probed `~/.claude` this session. Authoritative summary:

| Source | Carries | Notes |
|---|---|---|
| `~/.claude/settings.json` | `theme`, `permissions`, `enabledPlugins`, `skipWorkflowUsageWarning`, `skipAutoPermissionPrompt` | **NO `model` key.** No `effort` key. Theme confirmed `"dark"`. |
| `<project>/.claude/settings.json` | **`model: "claude-opus-4-7"`** + permissions + hooks | **The configured-model surface.** Read via `$CLAUDE_PROJECT_DIR/.claude/settings.json`. |
| `~/.claude/projects/<encoded>/*.jsonl` | Event stream: `permission-mode`, `user`, `assistant`, `file-history-snapshot`, `ai-title`, `attachment`, `last-prompt`, `queue-operation`, `system`, `pr-link` | 201 files on this host. Encoded path: dash-replaced absolute (`/workspaces/RavenClaude` → `-workspaces-RavenClaude`). |
| `~/.claude/stats-cache.json` | `dailyActivity`, `dailyModelTokens`, `modelUsage`, `totalSessions`, `totalMessages`, `lastComputedDate` | **Pre-computed. Up to 24h stale.** `costUSD: 0` on subscription. |
| `~/.claude/sessions/<pid>.json` | `{pid, sessionId, cwd, startedAt, version, kind, entrypoint, status, updatedAt}` | Live-session index. Match by `cwd == project_root` AND `status == "busy"`. |

**JSONL event shapes verified:**
- `permission-mode`: `{"type":"permission-mode","permissionMode":"default","sessionId":"..."}` — leading event per session.
- `assistant`: `{"type":"assistant","model":"claude-opus-4-7","usage":{...}}` — **the per-turn actually-used model surface.**

**Unreachable (honest empty state):**
- `/effort` reasoning dial (in-process only).
- Plan tier (Pro/Max/Team) — `costUSD: 0` confirms subscription but tier label not stored.
- `/status` live cache (in-process only).

---

## Phases

### Phase 1 — Contract + skill (1d)

**Pre-build gate:** none (Phase 0 reachability map is in this plan).

**Work:** `plugins/ravenclaude-core/skills/mimir/SKILL.md` documenting the reachability map + the encoded-path algorithm with fallback (gap-delta C3 / Panel-A R1: on miss, reverse-decode candidates in `~/.claude/projects/`) + hard scrubbing contract (gap-delta C7 + C8 — NEVER surface `type=user` content; universal `_scrub_reason()` on all string values) + torn-write discipline (gap-delta C4 — per-line try-except on `json.loads`) + stats-cache staleness disclosure (Panel-B R1 — `as of YYYY-MM-DD` pill mandatory) + worktree-aware encoded-key rule (gap-delta C5 / Panel-B R2 — use exact `$CLAUDE_PROJECT_DIR` verbatim, never normalized).

**LESSONS from Phase 1 of adaptive-run-classifier (PRs #244-#247):**
- Quote `description:` in YAML frontmatter if it contains `:` / `{` / `}` (PR #245).
- Regen `dashboard.html` + `repo-guide.html` + `copilot/plugin.json` when adding a skill (PR #246, #247).
- Bump skill counts in `marketplace.json` (metadata + plugin entry) + `plugin.json` (PR #246).
- Update `scripts/audit-gates.sh:443` fixture literal if skill count moves (PR #247).

**Acceptance:** SKILL.md scored ≥4/6 by `agent-quality-rubric`; frontmatter passes `scripts/check-frontmatter.py`.

**Agents:** `prompt-engineer` (primary), `architect`.

### Phase 2 — `_read_mimir` server helper (2d)

**Pre-build gate:** Phase 1 merged.

**Work:** Add `_read_mimir(project_root, claude_home) -> dict` to **both** `serve-dashboards.py` copies byte-identically. 5-card payload: settings (theme from user-level + model from project-level), session (sessions/<pid>.json matching cwd), activity (stats-cache.json with `as_of` field), recent sessions (mtime-desc glob, bounded 50KB per JSONL, count `type=assistant` events, sum `output_tokens`, first `gitBranch` — **never read user-prompt text**), universal scrub at JSON-encoding boundary.

**Endpoint:** `GET /__mimir` — no query params; `claude_home` + `project_root` fixed at server start (path-traversal defense per gap-delta C4); CSRF-guarded + Origin/Host-guarded + 127.0.0.1-bound.

**Empty state:** missing `~/.claude/projects/<encoded>` → `{exists: false, ...}` with empties; never 500.

**Acceptance:** byte-identical reader in both server copies; Python unit test with synthetic `~/.claude` tmpdir; worktree-path fixture; torn-write fixture; encoded-path fallback fixture.

**Agents:** `backend-coder` (primary), `architect`, `security-reviewer` (mandatory).

### Phase 3 — Generator tab + client render (1d, parallel with Phase 4)

**Pre-build gate:** Phase 2's `/__mimir` JSON contract frozen.

**Work:** in `scripts/generate-dashboards.py`: `#/mimir` route, tab title "Session" / alias "Mímir's well" (parenthetical, matches Norns convention), client `fetchMimir()` populates 4 card shells (Current session / Activity summary with as-of pill / Recent project sessions / static-host empty state). **Honest empty state for unreachable items** (`Model` effort, `Reasoning effort`): explicit "in-process only — run `/status`" pill, not a dash. **Inlining discipline (RM3):** zero on-disk-derived bytes inlined at generator time. Static markup only. Static-host fallback = render layout + "open the served dashboard" callout.

**Acceptance:** dashboard.html regenerated; Gate 13 passes; render gate (Phase 4) green.

**Agents:** `frontend-coder` (primary), `architect`.

### Phase 4 — Render-gate fixture + Gate 49 (1d, parallel with Phase 3)

**Pre-build gate:** Phase 2 JSON contract frozen.

**Work:** `scripts/check-mimir-render.mjs` mirroring `check-heimdall-render.mjs`. 4 fixtures: populated, empty-projects-dir, unreachable-fields, worktree-path. Assertions: permission-mode pill class matches mode; unreachable-card explanatory text; recent-sessions sorts by `last_active` desc; **`as of` pill rendered** (gap-delta C2); **sentinel-string scrubbing** (gap-delta C8 — `MIMIR_SENTINEL_PROMPT_TEXT` does NOT appear in render); **branch-name scrub** (gap-delta C7 — `feature/Bearer-eyJtokenfoo` → `[REDACTED]`); **both-copies-present** check. Must-fail half: drop `renderMimir` symbol; stubbed scrubber → sentinel leaks. Wire **Gate 49** in `scripts/audit-gates.sh` (Gate 48 = WebFetch sanitizer, Gate 50 = Phase-0 emit/scrub; Gate 49 is open — verified this session). Extend Gate 32 endpoint-parity diff to cover `/__mimir`.

**Acceptance:** Gate 49 positive + must-fail half; Gate 32 catches asymmetric edits; Gate 13 passes after regen.

**Agents:** `tester-qa` (primary), `code-reviewer`.

### Phase 5 — Ship (1d)

**Pre-build gate:** Phase 4 Gate 49 green.

**Work:** Version bump lockstep + milestones entry in `plugins/ravenclaude-core/CLAUDE.md` alongside Heimdall/Víðarr/Norns/Níðhöggr/Bifröst + prettier + **regen copilot package** + **bump skill count** if Mímir was the first/only new skill (skill count moves from 27 → 28). Update `scripts/audit-gates.sh` fixture literal if needed (per Phase-1 lessons above).

**Acceptance:** plugin-release-checklist passes; audit-gates clean; migration note in PR body (rollback = revert merge; no consumer state to undo).

**Agents:** maintainer, `project-manager`.

---

## Dependency DAG

```
Phase 0 (reachability — DONE this session, persisted in this plan)
   │
   ▼
Phase 1 (skill + contract, 1d)
   │
   ▼
Phase 2 (_read_mimir + /__mimir endpoint, 2d)
   │
   ├──────────────────────────┐
   ▼                          ▼
Phase 3 (generator + render, 1d)   Phase 4 (Gate 49 fixture, 1d) [parallel]
   │                          │
   └────────────┬─────────────┘
                ▼
            Phase 5 (ship + release)
```

**Critical path:** P0 (done) → P1 → P2 → P3 → P5 ≈ **5d serialized; 4-5d with Phase 4 parallel**.

---

## Alternatives (load-bearing choices kept on the record)

| # | Decision | Chosen | Trade-off |
|---|---|---|---|
| A1 | Model field reachability | **Configured (project-level `.claude/settings.json`) + Last-used (newest JSONL `assistant.model`)** | Both signals are honest and cheap; catches `/model` mid-session switches without hiding the persistent default |
| A2 | Activity data source | **`stats-cache.json` with `as of YYYY-MM-DD` pill** | Pre-computed by Claude Code (free); per-model breakdown is rich; staleness disclosure handles ≤24h lag |
| A3 | Multi-project view | **Current project only** (`$CLAUDE_PROJECT_DIR` only) | Avoids cross-project leakage in shared Codespaces |
| A4 | User-prompt content surfacing | **NEVER** | Hard rule; keeps the contract auditable; reject `ai-title` surfacing because titles can echo prompts |
| A5 | Scrubbing scope | **Universal** (all string values at JSON-encoding boundary) | Negligible compute; closes false-negative class |
| A6 | Encoded-path computation | **Server-side from `$CLAUDE_PROJECT_DIR` + fallback reverse-decode** | Server-side defends against path-traversal; fallback defends against Anthropic ABI drift |
| A7 | Inlining strategy | **All-served** (zero on-disk-derived bytes inlined) | All-Mímir-data is host-local; Gate 13 has no whitelist mechanism |
| A8 | `claude --help` / `--version` JSON status surface | **DEFERRED** | Verified-unreachable this session (permission denied); file-system surface is sufficient for MVP |

---

## Risk matrix (Panel A R1-R3 + Panel B R1-R3, merged)

| # | Risk | P × I | Mitigation | Owner |
|---|---|---|---|---|
| RM1 | **Project-encoding-scheme drift** (Panel A R1) | Medium × High | Fallback: after computing encoded key, scan `~/.claude/projects/` and reverse-decode each candidate; if computed key misses but fallback matches, log + use fallback | `backend-coder` |
| RM2 | **JSONL torn-write corruption** (Panel A R2) | High × Medium | Per-line try-except; corrupt lines silently dropped; explicit in SKILL.md as a hard contract | `backend-coder` |
| RM3 | **Freshness-gate trap** (Panel A R3) | High × High | Generator emits ONLY static markup; render gate asserts inlined HTML carries no project-specific tokens; all dynamic values JS-rendered from `/__mimir` | `frontend-coder` + `tester-qa` |
| RM4 | **stats-cache.json staleness** (Panel B R1) | Medium × High | First-class "as of YYYY-MM-DD" pill; render gate asserts presence | `frontend-coder` |
| RM5 | **Encoded-path mismatch for worktrees** (Panel B R2) | Medium × Medium | Use exact `$CLAUDE_PROJECT_DIR` verbatim; Gate 49 fixture covers worktree case | `backend-coder` |
| RM6 | **Server-parity gate is name-based** (Panel B R3) | Medium × Medium | DoD discipline: two-file diff before commit; follow-up Gate-32-body-diff proposed | `code-reviewer` |
| RM7 | **User-prompt content leakage** (gap-delta C8) | Low × High | Hard contract: NEVER surface `type=user` content. Gate 49 sentinel assertion proves it | `security-reviewer` |
| RM8 | **CSRF + path-traversal on `/__mimir`** | Medium × High | `claude_home` + `project_root` fixed at server start; CSRF + Origin/Host check + path-resolve-and-assert-under-claude-home before glob | `security-reviewer` |

---

## Definition of Done

- [ ] Phase 0 reachability map persisted in `plugins/ravenclaude-core/skills/mimir/SKILL.md`.
- [ ] **Version bumps lockstep** — plugin.json + marketplace.json minor on Phase 5.
- [ ] **`_read_mimir` byte-identical** in both `serve-dashboards.py` copies.
- [ ] **`/__mimir` endpoint** CSRF + Origin/Host-guarded + 127.0.0.1-bound + path-resolved.
- [ ] **Gate 49** registered in `scripts/audit-gates.sh` with `--check 49` runner.
- [ ] **Gate 32 extended** to cover `/__mimir`.
- [ ] **Gate 13** dashboard.html freshness passes after regen.
- [ ] **Prettier** `--write` then `--check` exit 0.
- [ ] **CLAUDE.md milestone entry** added alongside other Norse tabs.
- [ ] **Strict-YAML frontmatter** discipline (PR #245 lesson) — quote SKILL.md `description:` if it contains `:` / `{` / `}`.
- [ ] **Regen copilot package** + bump skill counts + update `audit-gates.sh:443` literal if skill count moves (PR #246, #247 lessons).
- [ ] **Security review sign-off** (RM7, RM8 — critical path of consumer's `~/.claude` contents).
- [ ] **Migration note in PR body**: rollback = revert; no consumer state.

---

## Open questions parked

- **`claude --status --json` or equivalent CLI subcommand** — if Anthropic adds one, becomes primary source. Re-evaluate at Researcher cadence.
- **Cross-project / workspace view** — useful for global activity; out of MVP per A3.
- **Edit affordances** — surfacing knobs but NOT editing them is MVP shape.
- **Token-spend cost** — needs Anthropic `usage` API or wallet introspection; out of MVP per A8.
- **Plan tier (Pro/Max/Team)** — no documented machine-readable surface.
- **`/effort` runtime dial** — in-process only; honest empty state.
- **Gate-32-body-diff** — RM6 follow-up; propose after MVP ships.
