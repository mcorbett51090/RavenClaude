# Session log — pick up where you left off

A rolling log of the **last 3 prompt/response pairs**, newest first. When a new
turn happens, the newest pair is prepended and the oldest is dropped so only 3
remain. Committed directly to `main` (no PR) so it survives Codespace rebuilds
and is always findable regardless of which branch work is happening on.

> Maintained by Claude each turn. "Response" is a concise summary of what was
> done plus the current state and next step — not a verbatim transcript.

---

## 1 — 2026-05-26 · Tribunal T4 — injection & self-protection hardening (v0.26.0, PR #94 merged)

**Prompt:** "cont" → (chose) Tribunal T4/T3.5 → "T4, go" → "Keep" (build the plan) →
"merge after pr commit".

**Response:** Built tribunal **T4 (§B.9 hardening)** end-to-end and **squash-merged
PR #94** (`99a53cf`). Grounding showed T4 was mostly already standing from T2/T3
(Heimdall/AlignmentCheck seat, basic `<untrusted>` envelope, injection + secret
concerns already `pre_llm_deny`, the `injection_detected` unilateral DENY). Closed
the genuine gaps: **(1) §B.9.5 "the Thing cannot disable itself"** — new
cross-cutting `xc.tribunal-self-disable` (critical, `pre_llm_deny`, new
`always_screen` flag) denies any Bash mutation of the orchestrator / seat wrapper /
concern+decision scripts / the plugin `hooks/`+`scripts/` **directories** /
`.ravenclaude/thing.yaml`, or a `thing: off` write into `comfort-posture.yaml`.
`always_screen` runs it **category-independently** (`screen_always` →
`_screen_always` → an orchestrator check before the per-category enabled gate), so
a self-disabling command shaped to classify into a toggled-OFF category is still
denied. **(2)** Hardened `xc.injection-attempt` (6→18 patterns) + canonical
AlignmentCheck envelope framing. **(3) §B.9.4** egress secret backstop in
`thing-seat.sh` (deny locally, never transmit) + broadened secret families in the
seat **and** catalog. **Gate 15** (adversarial fixtures + category-independent
self-disable + negative control + seat backstop) and **Gate 16** (every catalog
regex compiles); **47/47 gates green**, prettier clean. Bumped **v0.25.1 →
v0.26.0**. **`security-reviewer` ran pre-merge** and found 2 real shell-level
bypasses of the first-cut literal-filename guard (`tee -a` append; `rm -rf <dir>` /
glob / `$var` path obfuscation) — both fixed via **directory-level matching** +
the `tee` verb and pinned as Gate 15 fixtures; also bounded the trigger-3
lookaheads (ReDoS), made `screen_always` fail **closed** on a bad regex. **Build
finding:** the seat secret-scan `grep` parsed `-`-leading patterns as options,
silently failed, and fell through to a **live `claude` call** — Gate 15 caught it;
fixed with `grep -e`.

**Current state / next step:** **PR #94 merged to `main`** (`99a53cf`); local main
updated; freshness gate green (the `Generated`/`Last updated` lines are
strip-volatile, so the raw-diff "stale" was a false alarm). CI `pull_request`
checks did **not** register runs for the PR (anomalous; push-to-main runs work) —
merged on GitHub's `MERGEABLE/CLEAN/0-checks` + full local gate parity per Matt's
"merge after pr" instruction. **One reviewer item deferred to Matt's call:**
`xc.injection-attempt` stays `pre_llm_deny` (design-faithful to §B.9.3) despite FP
surface — option to demote weak shapes to panel-routed. Tribunal roadmap: **T5**
(per-pattern bypass + caching) or **T3.5** (review Edit/Write tools, not just Bash)
next. Track status in auto-memory `project_2026-05-25_tribunal_track`.

---

## 2 — 2026-05-25 · Tribunal T2 — ship the single-seat command-review orchestrator

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

**Current state / next step:** PR #90 merged (T2, v0.24.0). Next tribunal phase
was **T3** (three-seat panel + Thor + EDIT verdicts; design §B.11) — since shipped.

---

## 3 — 2026-05-25 · "405 on Save & apply from my phone" → diagnose + ship PR #89

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

**Current state / next step:** PR #89 merged. Phone-apply path = open the
**Codespace forwarded URL** (scan the QR), never the README/Pages link.

---
