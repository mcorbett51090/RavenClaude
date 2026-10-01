# Repo-wide review — 2026-10-01

**Scope:** a comprehensive, autonomous review of the whole repository — bugs, tech debt, performance,
architecture, missing features — categorized P0–P3, with no-design fixes implemented and the rest
written up here for your decision. Run on branch `claude/awesome-wright-hscvdk` from `origin/main`
(4b35028).

## Executive summary

**The repository is in exceptional health.** Every gate it ships to protect itself is green on `main`,
every cross-plugin structural invariant holds, and no mechanically-detectable defect exists. A deep,
reasoning-based review of the executable surface (runtime scripts, CI workflows, gate/checker scripts)
by three independent review panels surfaced **no P0 and no P1 issues** — only **one P2** (a real but
anomalous-input robustness bug, now **fixed**) and **three P3s** (two zero-production-impact consistency
/ hardening nits and one dead-code item that needs a one-line design call).

| ID | Priority | Area | Status |
|---|---|---|---|
| F1 | **P2** | `routine-reserve.py` — far-future `resets_at` → 100% CPU hang | ✅ **Fixed in this PR** |
| F2 | P3 | `stall_watch.py` — PID-reuse guard computed but never used (dead code) | ⏳ Needs a 1-line decision (below) |
| F3 | P3 | `check-frontmatter.py` — missing empty-scope fail-closed floor (siblings have it) | ⏳ Ready patch (below) |
| F4 | P3 | `check-layout.py` — `--all` vacuous-passes on empty `git ls-files` | ⏳ Ready patch (below); reviewer rates negligible |

Nothing here is urgent. F1 was worth an autonomous fix; F2–F4 are deliberately left for you because they
are either a genuine (if tiny) design call (F2) or zero-impact consistency churn on central tooling
(F3/F4) that an unattended agent shouldn't push unilaterally.

## Method (the "panels")

1. **Mechanical baseline (verified, reproducible).** JSON validity (186 files), shell syntax (200),
   hook executability, `prettier --check .`, `ruff check .`, `ci-preflight.py`, and cross-plugin
   invariants (184/184 plugins have `plugin.json`+`README.md`+`CLAUDE.md`; catalog↔dir exact match;
   zero version drift). All green. (Full record: `.ravenclaude/runs/repo-wide-review/baseline/`.)
2. **Three independent reasoning panels** over the executable surface the gates can't see:
   - runtime-correctness (core live scripts/hooks) → F1, F2
   - ci-cd-actions-security (17 workflows + the untrusted-intake path) → **clean, 0 findings**
   - gate-integrity (risk-sampled checker scripts — "a gate that doesn't gate") → F3, F4
3. **Validation / prioritization / tie-break** done by the orchestrator against the real code (every
   finding below was re-confirmed by reading the actual code path, not taken on the panel's word).

### One preflight "FAIL" that is **not** a defect
`ci-preflight.py` reports `hotspot:1-ratchet-merge-base` failing on `scripts/artifact-budgets.seed.json`.
Root-caused: the seed is byte-identical to `origin/main`; the "failure" is the documented behaviour of
running `check-ratchet-freshness.py --check` on a checkout whose HEAD **equals** `origin/main`
(`_base_ref.py::merge_base` deliberately returns `HEAD^1` there). On a real PR branch with commits on
top, the merge-base resolves correctly. No action — handled by the normal pre-push `--stamp` step.

---

## F1 (P2) — FIXED: far-future `resets_at` hangs `routine-reserve` at 100% CPU

**Files:** `plugins/ravenclaude-core/scripts/routine-reserve.py` (`project()` ~L611, `Cron.count_between` ~L244).

**The bug (confirmed by tracing):** `ingest_statusline` (L874) writes the statusline's `resets_at`
**verbatim** with no unit/range check. `parse_ts` (L166) reads a bare numeric string as epoch
**seconds**. So a `resets_at` in epoch **milliseconds** (a common API convention), or a
corrupted/clock-skewed/hand-edited value, becomes a projection horizon ~year 56800. `project()` only
discarded a *past* reset (L611), never a far-future one, so the horizon stayed far-future and
`Cron.count_between(now, horizon)` walked it **minute-by-minute (~5×10¹⁰ iterations)** at 100% CPU — in
the **detached `SessionStart` background `refresh`** (a hung process the user can't easily see), the
`compute`/`status` CLI, and the dashboard `GET /__reserve` request thread.

**The fix (defensive bounds; no behaviour change on valid input):**
1. `project()` now discards a reset more than `2 * WEEK_S` out (a 7-day window never resets that far
   ahead), falling back to `now + WEEK_S` exactly as the rolled-over case already does.
2. `Cron.count_between` carries a belt-and-suspenders one-year iteration cap.

**Verified:** epoch-ms `resets_at` → `project()` completes in 0.3 ms (was a hang), `reset_assumed=True`;
a **valid** ISO reset 3 days out is **unchanged** (`reset_assumed=False`); `count_between` on a
far-future end terminates via the cap. The cap is provably unreachable on any valid horizon (max 20,160
minutes ≪ 527,040 cap). Gate 291 passes with a new **section G** regression test (clamp fires on
corrupt input with no hang; valid reset untouched; `count_between` bounded).

---

## F2 (P3) — OPEN (needs a 1-line decision): dead PID-reuse guard in `stall_watch.py`

**File:** `plugins/ravenclaude-core/scripts/stall_watch.py` — `proc_identity_ok()` (def ~L261,
assigned ~L308).

**Finding:** `proc_identity_ok()` runs a `ps -o etime=` subprocess for every alive session every 5-min
tick, stores the result as `identity_ok`, and **never reads it** (its docstring says it guards against
PID reuse; episodes are keyed on bare `str(pid)` at ~L513/L552). So: (a) a wasted subprocess per alive
session per tick, and (b) the guard it documents is inert — if the OS reuses a PID across two stalled
sessions, the new one inherits the old one's advanced alert "rung" and its first stall alert is delayed
up to ~6 h.

**The decision for you (this is why it's not auto-fixed):**
- **Option A — wire it in** (the guard's original intent): incorporate `identity_ok` (or the process
  start time) into the episode key / resolution so a reused PID starts a fresh episode. This *changes
  stall-detection behaviour* and interacts with Gate 244's fixtures — a real design call.
- **Option B — remove the dead computation** (+ its per-tick `ps` subprocess): simpler, saves the
  subprocess, but abandons the documented PID-reuse protection.

Recommendation: **Option A** if PID-reuse-across-stalls is a real concern for your environment (it's the
correct fix); otherwise **Option B** to stop paying for a guard that does nothing. Low urgency either
way — the trigger (two separate sessions stalling under the same reused PID within one watcher lifetime)
is rare.

## F3 (P3) — OPEN (ready patch): `check-frontmatter.py` lacks the empty-scope fail-closed floor

**File:** `scripts/check-frontmatter.py` — `_violations()` builds `files` from globs (~L159), `main()`
returns 0 when there are no violations (~L286).

**Finding:** if the glob set is empty (e.g. `--root <dir-with-no-plugins>`), it prints "Frontmatter OK"
and exits 0 — an empty measurement reported as a pass. Its structurally-identical sibling gates
(`check-nested-dispatch.py`, `check-model-tier-fit.py`, `check-description-count-literals.py`) all
explicitly fail closed here ("an EMPTY measurement is not a pass"). **Zero production impact** —
`audit-gates.sh` runs it at root `.` against 600+ agents, so scope is never empty; this is a
consistency / defense-in-depth gap only.

**Ready patch:** in `_violations()`, after building `files`, `if not files:` return a synthetic failure
(`"no skill/agent/command files found — an empty scope is not a pass"`) so `main()` exits 1. **To do it
to this repo's standard, also add a teeth assertion** to the `fm-*` block in `audit-gates.sh`
(`check-frontmatter.py --root <empty-dir>` → non-zero), matching the adjacent fixtures. Left for you
because it's zero-impact and touches the central meta-test harness.

## F4 (P3) — OPEN (ready patch; negligible): `check-layout.py --all` vacuous pass

**File:** `scripts/check-layout.py:82-90`.

**Finding:** `--all` mode gives a vacuous pass if `git ls-files` returns rc 0 with empty output (only
reachable outside a git tree / an empty repo; rc≠0 already returns 2). The gate-integrity panel rates
this **negligible** in CI (always inside a populated git tree).

**Ready patch:** treat zero tracked files in `--all` mode as fail-closed. Bundle with F3 if you add the
empty-scope floors as a consistency pass.

---

## What was verified clean (coverage honesty)

- All 17 GitHub Actions workflows + the untrusted-issue-intake path (`quarantine-intake.yml` +
  `process-scenario-submission.py`): no script injection, no `pull_request_target`+head-checkout, all
  actions SHA-pinned, least-privilege `permissions:`, required-check `paths:` discipline upheld, intake
  content treated as data. **0 findings.**
- 13 risk-sampled checker scripts (all 8 recently-changed + 5 load-bearing): enforcement genuinely
  depends on the claimed property; must-fail halves bite. The checker corpus is exceptionally hardened.
- The runtime scripts beyond F1/F2 (`apply-comfort-posture.py` security-deny floor, atomic+flock writes,
  `routine-reserve-hook.sh`, `context-usage-meter.py`, `conserve-tokens.py`, `parallelism-detector.py`,
  `workaround-exhaustion.sh`): clean.
- 184/184 plugin structures; catalog↔dir exact match; zero version drift; no actionable TODO/FIXME debt
  markers in production code.

**Honest coverage limit:** this was a risk-sampled review of the executable surface, not an exhaustive
read of all 10,569 files (infeasible with quality in one pass). The 7,708 markdown/knowledge files and
the 184 domain plugins' prose were not line-read; the structural invariants over them were checked
mechanically. The confidence is high for the core executable layer and the gate harness; it is a sample,
not a proof, for the long tail.
