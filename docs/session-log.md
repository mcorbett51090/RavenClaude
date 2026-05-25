# Session log — pick up where you left off

A rolling log of the **last 3 prompt/response pairs**, newest first. When a new
turn happens, the newest pair is prepended and the oldest is dropped so only 3
remain. Committed directly to `main` (no PR) so it survives Codespace rebuilds
and is always findable regardless of which branch work is happening on.

> Maintained by Claude each turn. "Response" is a concise summary of what was
> done plus the current state and next step — not a verbatim transcript.

---

## 1 — 2026-05-25 · "405 on Save & apply from my phone" → diagnose + ship PR #89

**Prompt:** "cont" → (clarified) "we were fixing a 405 on the save & apply
button; double-check the status, I thought we merged it" → "go" → "keep live
pages up to date with dashboard updates" → "I want to apply from my phone if
possible" → "go".

**Response:**

- **Diagnosed the 405 — it is NOT a bug.** "Save & apply" POSTs to the local
  `serve-dashboards.py` `/__save` endpoint. The README link points at **GitHub
  Pages** (static host), which 405s on POST. Verified live: Pages `POST /__save`
  → 405, `HEAD` → 404. The save infra (`do_HEAD`/`OPTIONS`/`POST` + client probe)
  has been on `main` since #65/#81; the deployed `dashboard.html` is byte-identical
  to `main` (not stale code). So Matt's "I thought we merged it" was **correct**.
- **Reverted a stray uncommitted `.claude/settings.json`** — test residue from
  clicking the button (empty `allow`, everything→`ask`); not real posture.
- **Pages already auto-serves `main`** (legacy deploy-from-branch). The real gap:
  `dashboard.html` had no freshness gate (repo-guide did).
- **Shipped PR #89 (open + green), no version bump** (dev tool + CI, not shipped
  to consumers): (A) `serve-dashboards.py` prints a **scannable QR of the
  forwarded URL** so the dashboard opens on a phone where Save & apply works for
  real; `qrcode` optional dep + devcontainer install + URL/hint fallback +
  context-aware security note + stdout flush. (B) **"Verify dashboard.html is
  fresh"** CI step (`generate-dashboards.py --check`) + **Gate 13** in
  `audit-gates.sh`. 30/30 gates green, prettier clean.

**Current state / next step:** PR #89 **open + green**, awaiting Matt's merge.
Phone-apply path = open the **Codespace forwarded URL** (scan the QR), never the
README/Pages link. Tribunal **T2 still unblocked** (single-seat orchestrator,
design §B.11; estimate `claude -p` cost first) — unchanged from the prior session.

---

## 2 — 2026-05-25 · Tribunal: ship T1, verify substrate, unblock T2

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
v0.23.0**, regenerated `repo-guide.html`, opened **PR #88** (green, since merged).

**Current state / next step:** PR #88 merged (`5087e7e`). **T2 is UNBLOCKED** —
next build is the single-seat orchestrator (`code-reviewer`-shaped via `claude -p`,
ALLOW/DENY only, `shell_readonly` only, writes audit trail; design doc §B.11).
Worth estimating `claude -p` credit-pool cost (open question #4) before T2. Full
track status in auto-memory `project_2026-05-25_tribunal_track`.

---

## 3 — 2026-05-24 · Resume build → ship v0.19.0 + description cap

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
