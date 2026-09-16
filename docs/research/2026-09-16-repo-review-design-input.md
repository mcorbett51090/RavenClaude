# Whole-repo bug sweep — findings needing design input (2026-09-16)

A multi-panel review of RavenClaude's executable surface (Python scripts, shell
hooks, GitHub Actions) ran on 2026-09-16: five parallel reviewers scanned focused
slices, findings were validated and priority-assigned, and ambiguous ones were
tie-broken. **Eleven findings survived. Seven were mechanically fixable and shipped**
in the PR that lands alongside this doc (`fix: correct 7 P1/P2 defects from a
whole-repo bug sweep`). The remaining four need a decision — a concurrency-semantics
call, a which-value-is-canonical call, or a write to a tribunal-protected directory
this session cannot touch — so they are written up here rather than fixed blindly.

Baseline: `python3 scripts/ci-preflight.py` reported **19 PASS / 0 FAIL** — every
freshness/lint/ratchet/inventory gate the repo enforces is healthy. These findings
are in code those gates don't cover.

---

## D1 — `coordinator-lock.sh`: `STALE_SECONDS` is declared and documented but never consulted (P1)

- **Where:** [`plugins/ravenclaude-core/bin/coordinator-lock.sh`](../../plugins/ravenclaude-core/bin/coordinator-lock.sh) lines 33-36 (declaration + doc) vs. `_is_stale()` lines 107-116.
- **Observation (with control):** `STALE_SECONDS` (default 1800) is declared with a
  comment stating a holder is presumed dead *"IF ALSO its pid fails a `kill -0` check
  (both signals required — see `_is_stale` below)."* But `_is_stale()` only runs
  `_pid_alive` (`kill -0`); it never reads the lease's `heartbeat_at` or compares it to
  `STALE_SECONDS`.
  control: `grep -n STALE_SECONDS plugins/ravenclaude-core/bin/coordinator-lock.sh`
  returns exactly one line — 36, the declaration — and no other; `_is_stale` (107-116)
  references neither `STALE_SECONDS` nor `heartbeat_at`. If the variable were consulted
  the grep would return a second occurrence in the reap path; it does not. So this is
  an observation about the code, not an inference about intent.
- **Consequence (inference):** a holder whose process stays alive but is **wedged** (the
  parent `claude` process is up, but the agent stopped heart-beating) is never reaped —
  the lock would block until the process actually dies, and the documented dual-signal
  staleness does not exist in code.
- **Why it's a decision, not a mechanical fix:** implementing heartbeat-age reaping
  means **reaping a lock whose holder process is still alive**. If that judgment is
  wrong (the holder was merely slow, not dead), two coordinators acquire the same
  lock — the exact double-acquisition this lock exists to prevent. The current
  conservative behavior (only reap a dead pid) is *safer* but leaves the wedged-holder
  case unhandled and the documentation false.
- **Options:**
  1. **Implement the documented dual-signal reap** — add `heartbeat_at` age to
     `_is_stale`: reap when `kill -0` fails **OR** heartbeat older than `STALE_SECONDS`.
     Closes the wedged-holder case; accepts a small double-acquisition risk on a
     genuinely-slow-but-alive holder. (This is what the doc *claims* already happens.)
  2. **Keep pid-only reaping, fix the docs** — delete `STALE_SECONDS` and rewrite the
     comment to state reaping is pid-liveness-only. Zero double-acquisition risk;
     wedged holders stay stuck until the process actually dies.
  3. **Dual-signal, but require BOTH for reap** (heartbeat old **AND** pid dead) — the
     literal reading of "both signals required." This is *stricter* than today (a
     recently-heart-beating dead pid would not reap), which is probably not the intent.
- **Recommendation:** Option 1, matching the documented intent, with `STALE_SECONDS`
  kept generous (30 min default already is). The wedged-holder-blocks-forever failure
  is the more likely real-world problem; a 30-minute heartbeat gap is a strong dead
  signal. But this is a genuine safety trade-off — **your call.**

## D2 — `runes.py`: unguarded check-then-append claim races across concurrent sessions (P1)

- **Where:** [`plugins/ravenclaude-core/scripts/runes.py`](../../plugins/ravenclaude-core/scripts/runes.py) ~line 321 (`_claim()` / `auto_claim_next_ungated()`).
- **Observation:** the claim does an unguarded check-then-append against the ledger's
  derived `hook_owner`, with no lock. It fires from a `SessionStart` hook wired to
  `startup|resume|clear|fork` — i.e. on **every** session start, including the
  concurrent multi-worktree sessions this repo's own conventions encourage.
- **Consequence:** two sessions starting close together can both "win" a claim on the
  same Rune.
- **Sibling precedent:** `apply-comfort-posture.py`, `stream-ops.py`, and
  `thing-denial-kb.py` all added an **flock-based lock** for the structurally identical
  load-mutate-save pattern. `runes.py` did not.
- **Why it's not fixed here:** (a) `plugins/ravenclaude-core/scripts/` is protected by
  the command-review tribunal's `THING_SUBSTRATE` self-tamper guard, which denies writes
  to that directory — this session cannot edit it; (b) the fix is a small design call
  (lock granularity, whether to lock the whole claim or just the append) that should be
  made deliberately, not blind-ported.
- **Recommendation:** port the sibling flock pattern (wrap the check-then-append in the
  same lock helper the three siblings use). Low risk, proven pattern. Needs a
  differently-configured session (or the maintainer) to write under the protected dir.

## D3 — `plugin-lifecycle.py`: unguarded ledger load-mutate-save loses telemetry updates (P2)

- **Where:** [`plugins/ravenclaude-core/scripts/plugin-lifecycle.py`](../../plugins/ravenclaude-core/scripts/plugin-lifecycle.py) ~line 303 (`cmd_record()`).
- **Observation:** the load-mutate-save cycle has no lock, so concurrent telemetry
  writes (fired on every namespaced Agent/Skill/slash dispatch) can lose updates.
- **Consequence:** an actively-used plugin could look unused to the deprecation sweep
  if its usage-record write is clobbered by a concurrent one. Rated P2 — the impact
  is telemetry drift, not a correctness failure.
- **Why it's not fixed here:** same `THING_SUBSTRATE` protection as D2, plus the same
  lock-granularity design call.
- **Recommendation:** same flock port as D2. Lower priority than D2 (telemetry drift,
  not a correctness race). Bundle with D2 if touching the protected dir anyway.

## D4 — `guard-premise.sh` vs `log-probe.sh`: scope-key fallback mismatch when `cwd` is absent (P2)

- **Where:** [`plugins/ravenclaude-core/hooks/guard-premise.sh`](../../plugins/ravenclaude-core/hooks/guard-premise.sh) and [`plugins/ravenclaude-core/hooks/log-probe.sh`](../../plugins/ravenclaude-core/hooks/log-probe.sh).
- **Observation (medium confidence):** the two hooks share a stated contract to "derive
  the identical scope key," but the reviewer reported **different fallback values** when
  the payload's `cwd` field is absent — `guard-premise.sh` falling back to `path`,
  `log-probe.sh` to `proj`. This repo's own `worktree-guard.sh` documents that Copilot
  and Cursor genuinely omit `cwd` on PreToolUse. **Not independently re-verified in this
  session** — confirm the exact fallback tokens and reproduce the desync before acting.
- **Consequence (inference):** on those hosts the two hooks could silently desync scope —
  the premise-gate checks an empty ledger for a scope key that `log-probe.sh` never wrote
  to, so the gate reads "clean" for a scope that actually has an unresolved negative.
- **Why it's a decision, not a mechanical fix:** which fallback value is **canonical**
  is a judgment call — the two hooks must agree, but picking `path` vs `proj` (or a
  third derived value) requires knowing which one correctly identifies the scope on the
  hosts that omit `cwd`. Also `THING_SUBSTRATE`-protected (`hooks/`).
- **Recommendation:** extract the scope-key derivation into a single shared helper both
  hooks source (the repo already uses `_scrub.sh` / `_emit-event.sh` sourced helpers),
  so they cannot drift. Decide the `cwd`-absent fallback once, in that helper, verified
  against a real Copilot/Cursor PreToolUse payload.

---

## Note: pre-existing, not from this sweep

`python3 scripts/concepts.py --check` currently **exits 1** on `main`.
control: the same command run against `origin/main`'s own `scripts/concepts.py`
(`git show origin/main:scripts/concepts.py`) against the current tree also exits 1 —
so the failure predates this work and is not introduced by the code-fix PR. It is a
content-staleness gate on the `staleness-double-exemption` concept ("a covered
artifact changed after the entry was stamped") — a **knowledge-freshness restamp**,
not a code defect. The repo's own rules (CLAUDE.md § "don't blind-bump a date") forbid
restamping without re-verifying the covered artifact, so it is flagged here for a
maintainer rather than touched by the code-fix PR.
