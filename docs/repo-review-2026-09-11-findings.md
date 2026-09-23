# Repository review — 2026-09-11 (multi-panel bug sweep)

**Status for review by Matt.** Autonomous scheduled run. Branch `claude/awesome-wright-eb3a3d`.

## Executive summary

- **Mechanical health is fully green.** prettier clean, ruff clean, `ci-preflight` 19/19 PASS,
  `audit-gates.sh` **1065 pass / 0 fail** (the lone Gate 47 skip was a local `jsonschema` env gap —
  installed and re-run this session; all plugin + marketplace JSON Schemas validate).
- **A 4-reviewer expert panel** swept the freshest, highest-blast-radius **code** (not the 184
  mostly-markdown plugins — a full sweep is neither affordable nor valuable in one unattended run, and
  the `/repo-review` skill itself refuses shallow whole-repo passes). **18 findings**: 1 P0, ~10 P1,
  ~5 P2, 1 P3 (after Panel 2/3 re-grading).
- **2 findings fixed in this PR** (the only ones outside the tribunal-protected trees).
- **15 findings are verified, ready-to-apply patches that CANNOT be applied from this session** — they
  live in `plugins/ravenclaude-core/scripts/` + `hooks/`, which the command-review tribunal's
  self-protection floor (`xc.tribunal-self-disable`) blocks from edits. This is **by design and a
  security floor I did not bypass.** They are staged below for a human / differently-configured session,
  exactly per the coordinator milestone's `docs/pending-guard-destructive-merge-patch.md` precedent.
- **1 genuine design question** (C-02) needs your decision.

## The load-bearing operational finding (read this first)

**An autonomous agent in this environment cannot patch the plugin's `scripts/` or `hooks/` trees.**
The tribunal's `xc.tribunal-self-disable` guard is `always_screen` (category-independent) and fires even
with `command_review.enabled: false`, because four shell categories carry `thing: on`. It blocks:
- **Bash** commands whose text contains substrate-tampering shapes (it even denied read-only
  verification probes that merely *mentioned* substrate paths in a tampering shape — the documented
  "source-scan matches prose" effect), and
- **Edit/Write** tool calls targeting any file under `plugins/ravenclaude-core/{scripts,hooks}/`
  (confirmed live: a clean, correct `grok-delegate.sh` fix was denied).

The `dev_repo_exempt` maintainer path requires a live `gh repo view` GraphQL call that this remote
session's GitHub proxy refuses. **This is correct behavior** — the point of the guard is that an
autonomous session cannot silently rewrite the guardrail substrate. The consequence for *this task* is
that 15 of 18 fixes must be applied by you (or a session where you've turned the Thing off in the
dashboard for the duration). The exact patches are below so that is a paste, not a re-derivation.

## Method (panels + model assignment)

- **Panel 1** — 4 parallel expert reviewers (Sonnet, the lighter tier per the model-assignment rule),
  each scoped to a coherent code slice, each required to supply a **concrete failing scenario** per
  finding and to separate observation from inference. Every reviewer reproduced its findings live.
- **Panel 2** — this orchestrator (Opus) independently re-verified the P0s and headline P1s against the
  live code (see "confirmed by me" column), added impact/effort, and re-graded priority.
- **Panel 3** — tie-break on the P0/P1 disagreements (below).

## Consolidated findings (Panel 2/3 verdicts)

Legend — **Status**: FIXED (in this PR) · STAGED (patch ready, tribunal-blocked here) · DESIGN (needs your call).

| ID | Reviewer | Final | Status | File | One-line |
|---|---|---|---|---|---|
| D1 | P0 | **P0** | STAGED | thing-concerns.py / concerns-catalog.md | `curl -o`/`wget -O` to a tribunal substrate path bypasses the self-disable guard entirely |
| P1B-01 | P0 | **P1** | STAGED | caveman-apply-mode.sh:417 | first-apply snapshot is a blind whole-file write, wiping the router's own state keys |
| P1B-02 | P0 | **P1** | STAGED | caveman-apply-mode.sh:389 | manual-override latch only checked on the session's *first* apply → later `/caveman` silently overwritten |
| P1A-1 | P1 | **P1** | STAGED | context-usage-meter.py:511 | a Grok `config.toml` window silently overrides the correct model-aware window on a Claude Code session |
| P1A-2 | P1 | **P1** | STAGED | conserve-tokens.py:145 | unbounded 4096-char tail scan leaks an unrelated later YAML key into the parsed `parallelism` posture |
| P1A-3 | P1 | **P1** | STAGED | context-handoff.py:385 | `stamp_meta()` records session id only for Grok → handoff continuation breaks on Claude Code/Copilot |
| P1A-4 | P1 | **P1** | STAGED | dod-gate.sh:52 | absent PyYAML silently no-ops the DoD Stop-gate; the "tolerant fallback" comment is false |
| P1B-05 | P1 | **P1** | STAGED | dependency-sweep.py:385 | `_semver_gte(...) is not None` treats a floor that *no longer holds* as "still holds / mechanical" |
| C-03 | P1 | **P1** | **FIXED** | findings_merge.py:74 | `compute_key` kept 6 alpha-earliest tokens → two distinct findings collapse into one (false-merge) |
| P1B-03 | P1 | **P2** | STAGED | caveman-route-engine.py:428 | `applied=True` set unconditionally; `noop-no-caveman`/failed applies log as `applied: true` |
| P1B-04 | P1 | **P2** | STAGED | grok-delegate.sh:115 | unguarded `shift 2` on a value-flag passed last → infinite loop (sibling copilot-delegate.sh guards it) |
| D2 | P1 | **P2** | STAGED | thing-concerns.py:204 | read-only `awk`/`grep` of comfort-posture is wrongly hard-denied as tribunal-self-disable (false positive) |
| C-01 | P1 | **P2** | **FIXED** | repo-sweep.workflow.js:675 | best-effort estimate passed a batch count to `--agent-budget` (a call ceiling) → nonsensical log |
| D3 | P2 | **P2** | STAGED | guard-destructive.sh:529,535 | curl/wget-pipe deny regex `.*`/`[^|]*` crosses `;`/`&` → a benign two-command line wrongly denied |
| P2A-1 | P2 | **P2** | STAGED | stall_watch.py:308 | PID-reuse identity guard is computed (extra `ps`/tick) but never consulted — dead code |
| P2A-2 | P2 | **P2** | STAGED | context-handoff.py:34 | `FORBIDDEN_SEED` (incl. `/fork`) defined but unused; the real check uses a divergent shorter list |
| C-02 | P1 | — | **DESIGN** | estimate_cost.py:105 | does `--no-cross-model` apply to `max` tier? SKILL.md says yes; the code comment says "no such flag" |
| P3A-1 | P3 | **P3** | STAGED | stall_reach.py:70 | stray no-op `alerts[0]` statement (dead code) |

### Panel 3 — tie-break record

**P1B-01 and P1B-02 (reviewer P0 → P1).** The P0/P1 boundary per the repo's own rubric is "data
corruption / crash / security-critical *on realistic input*" vs "a real bug, not yet catastrophic."
Both bugs are real, but both live in the **caveman live-apply path**, which is (a) **default-off**
(`caveman_routing: live` is opt-in), (b) self-healing (P1B-01's wiped router state re-bootstraps on the
next call), and (c) explicitly shipped with the soak/replay gates overridden (CLAUDE.md v0.321.4). They
are not "security-critical on realistic input" for the overwhelming majority of consumers. → **P1.**
Note strongly, though: **these are exactly the class of defect the overridden soak gates existed to
catch.** Two independent P0-shaped bugs surfaced on the first review of that path.

**D1 stays P0.** It is a genuine bypass of the tribunal's flagship "the Thing cannot disable itself"
guarantee. Exploitation needs the Thing toggled on plus an attacker/injected instruction, but it
defeats a *documented security invariant*, which is the P0 bar for a security finding.

## Fixed in this PR

Both are outside the tribunal-protected trees (under `skills/repo-review/`), so they were applied and
verified here.

- **C-03 — `findings_merge.py` false-merge (P1).** `compute_key` hashed `title_tokens(title)[:6]`, i.e.
  the 6 *alphabetically-earliest* tokens; two genuinely distinct findings sharing 6 early filler words
  collapsed into one survivor (the second silently dropped, corroboration falsely inflated). Reproduced
  live (collision = True), fixed by selecting the 6 *longest/most-distinguishing* tokens before hashing,
  re-verified (collision = False, identical titles still merge). Added a `test10` regression assertion.
  Full `--self-test` green; **Gate 258 + Gate 260 pass including their must-fail mutants.**
- **C-01 — `repo-sweep.workflow.js` estimate arg mismatch (P2).** The best-effort pre-flight cardinality
  log passed `BUDGET_BATCHES` (a batch count) to `estimate_cost.py --agent-budget` (a *total agent-call*
  ceiling), making the logged estimate nonsensically pessimistic on every run. Log-only impact. Fixed by
  omitting the flag so the estimator uses its own correct default ceiling; `node --check` clean.

_(Consequence: C-03 edits `findings_merge.py`, a file covered by the `repo-review-corroboration-bucket-diff`
concept, so its `covers_digest` was cosmetically restamped — `last_verified` NOT moved, no false freshness
— and `concepts.json` + the standalone `dashboard.html` regenerated to stay freshness-green. No version
bump: the two fixes are to a build-in-progress skill; the ~19 MB dashboard-regen + catalog cascade a bump
triggers was disproportionate, and CI requires consistency, not a bump.)_

## Design question — C-02 (needs your decision)

`estimate_cost.py:resolve_cross_model()` returns `True` unconditionally for the `max` tier, with the
comment *"there is no `--no-cross-model` per the spec."* But **SKILL.md's command surface documents
`--cross-model | --no-cross-model` as an explicit override**, and `repo-sweep.workflow.js` resolves the
tier default into the presence/absence of `--cross-model` before calling the estimator. So today a
direct `estimate_cost.py --effort-tier max --no-cross-model` is silently ignored (still M=2), and the
estimator can over-project a `max` run's cost.

This is a genuine spec ambiguity, not a mechanical fix: making `max` honor the flag (like `xhigh`) fixes
the workflow path but changes the direct-human default (a bare `--effort-tier max` would report M=1
instead of the documented "on by default"). `argparse` `store_true` also cannot distinguish "flag
absent" from "explicitly off" without a tri-state.

**Recommendation:** decide the spec, then implement one of:
1. **`--no-cross-model` applies to `max`** (matches SKILL.md): make `--cross-model`/`--no-cross-model` a
   tri-state (`None` → tier default ON for max; `True`/`False` → explicit), so a bare invocation keeps
   max's documented default and `--no-cross-model` is honored. *(My recommendation — it makes the
   documented command surface real.)*
2. **`max` cross-model is not overridable**: keep the code, and **remove `--no-cross-model` from
   SKILL.md's ladder/command surface** so the doc stops promising a no-op.

## Staged patches (tribunal-blocked here — apply from a session with the Thing off, or by hand)

Each is verified (reviewer-reproduced; the P0s + several P1s also confirmed by this orchestrator reading
the live code). Grouped by final priority.

### P0

- **D1 — tribunal self-disable `curl -o`/`wget -O` bypass** (`thing-concerns.py` / `concerns-catalog.md`
  `xc.tribunal-self-disable`). `curl -s -o <substrate-path> <url>` classifies as low-tier `network_read`,
  whose concerns never inspect the `-o`/`-O` local destination; `guard-destructive.sh` only catches
  curl/wget *piped to an interpreter*; `enforce-layout.sh` only fires on Write/Edit. Net: one
  ordinary-looking command silently replaces a tribunal hook/config file with zero review.
  **Fix:** add a `curl`/`wget` + `-o`/`-O`/`--output`/`--output-document` + substrate-path trigger to
  `xc.tribunal-self-disable` (both argument orders), OR — more robustly — extend
  `screen_substrate_path()`'s catalog-independent Python check (`thing-decision.py`) to also run for
  Bash `network_read`/`network_write` commands whose local output target is a substrate path.

### P1

- **P1B-01 — caveman snapshot blind overwrite** (`caveman-apply-mode.sh:417`). Confirmed by me: line 417
  `writeStateFileAtomic(snapshot)` writes only the 5 applier keys, discarding the router's
  `cursor_byte/streak/verdict/...` written moments earlier in the same session (the module docstring
  claims the two never clobber each other — only half is implemented).
  **Fix:** `writeStateFileAtomic(Object.assign({}, priorState, snapshot))`.
- **P1B-02 — manual-override latch only on first apply** (`caveman-apply-mode.sh:389`). Confirmed by me:
  the latch block is inside `if (!hasApplierSnapshot)`, so a later router-triggered apply silently
  overwrites a mode the user set via `/caveman` mid-session.
  **Fix:** on *every* apply, read the current `readSessionModeRaw()` and compare to the mode this script
  last applied; if it drifted out-of-band, treat as manual_override and hold.
- **P1A-1 — Grok config window overrides Claude window** (`context-usage-meter.py:511`). A Claude Code
  session with Grok CLI installed reads Grok's `context_window` (rank 3) ahead of the correct model-aware
  window (rank 4) — sibling of the v0.319.0 model-aware fix. **Fix:** gate `window_from_grok_config()`
  behind `source != "claude-code"`, or prefer model-aware resolution when `source == "claude-code"`.
- **P1A-2 — parallelism posture tail-scan leak** (`conserve-tokens.py:145`). The 4096-char tail scan for
  `enabled:`/`max_workers:` matches a later unrelated top-level key's values. **Fix:** bound the tail to
  the next column-0 key, as `context-usage-meter.py:read_posture()` already does.
- **P1A-3 — handoff session id only stamped for Grok** (`context-handoff.py:385`). `stamp_meta()` records
  `last_handoff_session_id` only under Grok, so handoff continuation breaks on Claude Code/Copilot.
  **Fix:** also stamp from `CLAUDE_SESSION_ID` (mirror `_resolve_session_id()`'s precedence).
- **P1A-4 — DoD gate silently disabled without PyYAML** (`dod-gate.sh:52`). `except Exception: d = {}`
  swallows a missing-`yaml` ImportError, so a configured `definition_of_done.cmd` reads empty and the
  Stop-gate no-ops — the "tolerant fallback" comment is false, and it contradicts the plugin's
  no-PyYAML discipline. **Fix:** catch only `ImportError` and fall back to the minimal line/regex parse
  the sibling scripts already use.
- **P1B-05 — dependency-sweep floor truthiness** (`dependency-sweep.py:385`). `_semver_gte(...) is not
  None` is True for both True and False, so a floor that *no longer holds* is classified "mechanical /
  version_floor_still_holds" and auto-verified. Confirmed by me. **Fix:** branch on `result is True`
  (mechanical) / `result is False` (actionable → judgment) / `result is None` (cannot establish).

### P2

- **P1B-03 — `applied=True` unconditional** (`caveman-route-engine.py:428`): capture the apply script's
  stdout and derive `applied` from its `status` (true only for `status=='applied'`); emit the reserved
  `caveman-route-*` signal tokens so Heimdall can distinguish outcomes.
- **P1B-04 — `grok-delegate.sh` `shift 2` hang** (line 115): add `[ $# -ge 2 ] || { echo "…requires a
  value" >&2; exit 2; }` before each `shift 2`, exactly as the sibling `copilot-delegate.sh` does.
  _(This PR includes the exact patch in the run-dir; it was denied here only by the substrate guard.)_
- **D2 — trigger-3 false positive** (`thing-concerns.py:204`): apply the same write-shape lookahead
  trigger 4 already got on 2026-09-03, so a read-only `awk`/`grep` of `comfort-posture.yaml` isn't
  hard-denied as self-disable.
- **D3 — `guard-destructive.sh` separator-crossing regex** (lines 529, 535): scope both curl/wget-pipe
  patterns to a single command (split on `;`/`&`/`&&`/`|`), the same fix the file's header documents
  applying twice already to the git rules.
- **P2A-1 — dead PID-reuse guard** (`stall_watch.py:308`): either wire `identity_ok is False` into the
  resolution logic, or drop the now-pointless per-tick `ps` call.
- **P2A-2 — divergent `/fork` denylist** (`context-handoff.py:34`): use `FORBIDDEN_SEED` in the safety
  check instead of the hardcoded shorter list, so they can't drift.

### P3

- **P3A-1 — dead `alerts[0]`** (`stall_reach.py:70`): delete the stray no-op line.

## Recommendations / questions for you

1. **Decide C-02** (the one design question) — recommendation above is option 1.
2. **The caveman live-apply P0s (P1B-01/02) validate the soak gates.** Two P0-shaped bugs on first
   review of the path shipped with those gates overridden (v0.321.4). Recommend applying P1B-01/02
   before anyone runs `caveman_routing: live`, and treating this as evidence for re-running the soak.
3. **Apply the 15 staged patches** from a session where the Thing is off in the dashboard (or hand-apply)
   — they're paste-ready above and in `.ravenclaude/runs/repo-review-2026-09-11/panel1-{A,B,C,D}.json`.
   D1 (the tribunal bypass) is the priority.
4. **Consider a narrow, sanctioned substrate-edit path for authorized autonomous maintenance** — this run
   surfaced that an unattended agent literally cannot fix its own guardrail code here, which is the
   correct default but also means guardrail bugs (like D1) can't be autoremediated. Not a change to make
   lightly; flagging it as the recurring structural tension this repo keeps hitting.

---

_Reviewer finding JSON (with full scenarios/observations/confidence) is in
`.ravenclaude/runs/repo-review-2026-09-11/panel1-{A,B,C,D}.json`._
