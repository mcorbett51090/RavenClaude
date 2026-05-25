# Session log — pick up where you left off

A rolling log of the **last 3 prompt/response pairs**, newest first. When a new
turn happens, the newest pair is prepended and the oldest is dropped so only 3
remain. Committed directly to `main` (no PR) so it survives Codespace rebuilds
and is always findable regardless of which branch work is happening on.

> Maintained by Claude each turn. "Response" is a concise summary of what was
> done plus the current state and next step — not a verbatim transcript.

---

## 1 — 2026-05-25 · Tribunal: ship T1, verify substrate, unblock T2

**Prompt:** "cont" → "cont" → "go / yes" (resume, proceed, then merge #87 + start
the substrate-verification reconciliation).

**Response:** Oriented from a cold context (this log was stale, covered v0.19.0).
Three things shipped this session:
(1) **T1 merged** — found the read-only "Command review (the Thing)" preview UI
(v0.22.0) committed on `feat/ravenclaude-core-tribunal-t1` with no PR; verified
green, opened + squash-**merged PR #87** (`f9d5c84`). Intentionally inert UI.
(2) **Substrate verified** — the §B.5.1 "both cannot be true" alarm was a **false
alarm**. Re-verified the PreToolUse hook API against primary docs (hooks ref +
hooks-guide + agent-sdk/hooks, cross-checked — the first WebFetch summary wrongly
said bypass behavior was undocumented; a verbatim grep found it). Confirmed:
`updatedInput` is real → **EDIT verdict path stands**; permissionDecision
allow/deny/ask/defer (defer is `-p`-only); prompt/agent hook types real (agent
experimental); a hook `deny` beats `--dangerously-skip-permissions` but a hook
`allow` can't override a settings `deny` (so the Thing can't relax `security_deny`);
platform fails OPEN on timeout. Updated design doc §B.5.1 → **v3 on main**
(`c914998`, docs-commit-to-main).
(3) **Knowledge reconciled** — added an "Advanced JSON output protocol" section to
`knowledge/claude-code-permissions.md`, bumped ravenclaude-core **v0.22.0 →
v0.23.0**, regenerated `repo-guide.html`, opened **PR #88** (green).

**Current state / next step:** PR #88 **open + green**, awaiting Matt's merge.
**T2 is now UNBLOCKED** — next build is the single-seat orchestrator
(`code-reviewer`-shaped via `claude -p`, ALLOW/DENY only, `shell_readonly` only,
writes audit trail; design doc §B.11). Worth estimating `claude -p` credit-pool
cost (open question #4) before T2. Full track status in auto-memory
`project_2026-05-25_tribunal_track`.

---

## 2 — 2026-05-24 · Resume build → ship v0.19.0 + description cap

**Prompt:** "cont" (resume the in-progress build). Two decisions during the turn:
(a) collapse the posture scale from 5 levels to 3 (Deny/Ask/Allow); (b) do the
per-permission UI + the 3-level cleanup together in one PR. Mid-turn add: "make
it a hard rule that marketplace descriptions can only have 1024 characters."

**Response:** Finished the per-permission/per-layer feature and the 5→3 level
collapse end-to-end — schema, translator (old level names still accepted for
back-compat; emits identically), dashboard generator UI+JS (per-permission
User/Local/Project selectors → v5 `overrides:` map), set-posture skill,
pattern-explanations, README, live `comfort-posture.yaml`, plan-doc changelog.
Bumped ravenclaude-core to **v0.19.0**, regenerated dashboard.html + repo-guide,
**27/27 gates green**, opened **PR #82**. Then added the 1024-char description
cap as Check 3 in `check-marketplace-claims.py` + a Gate 12 fixture, trimmed all
8 over-cap descriptions, and folded it into PR #82 (same file as the version
bump). Updated PR conventions in `AGENTS.md` (docs-only changes commit straight
to main — which is why this log entry is a direct-to-main commit).

**Current state / next step:** **MERGED** as v0.19.0 (PR #82, squash `e7f703b`);
Matt confirmed the dashboard UI looks good. He has unspecified dashboard
**improvement ideas parked for a later session** — ask him to enumerate when raised.
Nothing else outstanding.

---

## 3 — 2026-05-24 · Running-log request

**Prompt:** "I need a running log of the last 3 prompts and responses so I can
always pick up my work where I left off. Do not run it through a PR. Just commit
it to main. It only needs to store the last 3, so when another prompt and
response happens then delete the oldest one."

**Response:** Created this file (`docs/session-log.md`) as a rolling 3-entry
continuity log and committed it straight to `main` (no PR). Each new turn
prepends a pair and drops the oldest beyond 3.

**Current state / next step:** Mid-build on branch
`feat/ravenclaude-core-per-permission-layers` — the dashboard per-permission /
per-layer feature (the 8-part plan Matt approved). Schema tooltip rewrite was
in progress when this request came in. Next: resume the build (schema → generator
→ translator → hook → regenerate → gates → PR).

---

