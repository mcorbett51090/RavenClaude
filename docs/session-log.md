# Session log — pick up where you left off

A rolling log of the **last 3 prompt/response pairs**, newest first. When a new
turn happens, the newest pair is prepended and the oldest is dropped so only 3
remain. Committed directly to `main` (no PR) so it survives Codespace rebuilds
and is always findable regardless of which branch work is happening on.

> Maintained by Claude each turn. "Response" is a concise summary of what was
> done plus the current state and next step — not a verbatim transcript.

---

## 1 — 2026-05-25 · Tribunal T2 — ship the single-seat command-review orchestrator

**Prompt:** "let's implement the command review (the Thing) now" + side
questions (is the comfort posture applied? why did a command prompt me? design
check-ins vs command review? `--bare` finding).

**Response:** Built tribunal **T2 end-to-end** on `feat/ravenclaude-core-tribunal-t2`
(approved scope: substrate **+** live dashboard toggle). New files:
`hooks/thing-orchestrator.sh` (Lawspeaker — fast-grep short-circuit when no
toggle, pre-LLM injection/secret screen, single-seat convene, Sága-log write,
fail-closed verdicts), `scripts/thing-decision.py` (classifies via the EMISSIONS
table — one source of truth — + reads the per-category `thing:` toggle),
`scripts/thing-seat.sh` (lone code-reviewer seat via `claude -p`, with a
`THING_SEAT_MOCK_VERDICT` test hook so CI never calls a live model),
`skills/thing/SKILL.md`, `templates/thing.yaml`. Dashboard: the `shell_readonly`
Command-review toggle is now **live** (writes `thing: on`; others stay Preview) —
generator + JS + regenerated `dashboard.html`. Gate-audit **Gate 14** added.
Bumped **v0.23.0 → v0.24.0** (+1 skill → 21), regenerated repo-guide,
**35/35 gates green**, prettier clean. **Real finding:** `claude -p --bare` (per
the design) fails under subscription/OAuth — needs `ANTHROPIC_API_KEY`; the seat
defaults to plain `claude -p` from a scratch dir (`--bare` opt-in via
`THING_SEAT_BARE=1`). Verified the live seat: `ls -la`→allow, injection→deny.

**Current state / next step:** PR being opened off `feat/ravenclaude-core-tribunal-t2`.
Did **not** sweep in pre-existing uncommitted local changes (`.gitignore` +
`.claude/settings.json` posture-emptying + applied marker) — flagged to Matt as a
separate decision; restored `settings.json` to `main + hook` only. Cost is real
(~$0.05–0.10/reviewed command), so `shell_readonly` review is a validation
switch, off by default. Next tribunal phase = **T3** (three-seat panel + Thor +
EDIT verdicts; design §B.11).

---

## 2 — 2026-05-25 · "405 on Save & apply from my phone" → diagnose + ship PR #89

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
README/Pages link.

---

## 3 — 2026-05-25 · Tribunal: ship T1, verify substrate, unblock T2

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
next build is the single-seat orchestrator (now shipped, see entry 1). Full track
status in auto-memory `project_2026-05-25_tribunal_track`.

---
