# Repository review — 2026-09-17

Scheduled whole-repo review: four independent expert reviewers (Panel 1) swept the
executable surface, findings were validated and re-priced (Panel 2), and the confirmed,
design-free fixes were implemented autonomously. This document is the review record plus
the one item that needs your decision.

## Scope and method

The manifest/markdown/freshness layer is already covered by CI gates and was green at review
time — `scripts/ci-preflight.py` reported **19 PASS / 0 FAIL** (JSON validity, shell syntax,
prettier, ruff, all inventory/dashboard/index freshness + ratchet gates). So the review
targeted where real defects can still hide: the **executable code** (~70K LOC of Python in
`scripts/`, 188 plugin Python scripts, ~200 shell scripts/hooks) plus a first-party pass over
`.github/workflows/`.

Reviewers (risk-sampled, high-confidence-only bar — a concrete failure scenario required for
every finding):

| Reviewer | Surface | Result |
|---|---|---|
| A | `scripts/*.sh` (23 files) | 2 bugs (1 P2, 1 P3) + 1 cosmetic |
| B | `plugins/ravenclaude-core/hooks/*.sh` (enforcement hooks) | 1 P3 (fails safe) |
| C | `scripts/check-*.py` gates (31 read) | no paper-tigers; 1 P3 |
| D | non-core `plugins/*/hooks/*.sh` + `plugins/*/scripts/*.py` (sample) | no bugs |
| (self) | `.github/workflows/*` CI-security | no findings |

## Severity tally

- **P0 / P1: none.** No critical or high-severity defects were found anywhere in the sampled
  surface. The codebase is unusually well-hardened (bidirectional `--must-fail`/`--self-test`
  fixtures on nearly every gate; consistent `|| true` guarding around command substitutions
  that precede a deny; `exit 2`-only blocking with EXIT traps).
- **P2: 1** — fixed.
- **P3: 3** — 2 fixed, 1 blocked by a gate (below).
- **Cosmetic: 1** — intentionally not fixed.

## Fixes implemented in the accompanying PR

1. **[P2] `scripts/premerge-refresh.sh:64` — infinite loop on `--base` with no value.**
   Under `set -uo pipefail` (no `-e`), `--base) BASE="${2:-origin/main}"; shift 2` never exits:
   `shift 2` with `$# < 2` no-ops and its non-zero status is ignored, and the `${2:-…}` default
   suppresses the nounset trap that protects the other arg handlers, so `$1` stays `--base` and
   the loop re-matches forever. Fixed by guarding the value (`[ $# -ge 2 ] || { …; exit 2; }`)
   before consuming it. Verified: `premerge-refresh.sh --base` now exits 2 immediately.

2. **[P3] `scripts/check-github-status.sh:38` — IndexError on an empty `incident_updates`.**
   `i.get("incident_updates", [{}])[0]` crashes when the key is *present but an empty list*
   (`[]`) — the `[{}]` default only applies when the key is *absent*. That uncaught exception
   made the script exit non-zero and print a traceback, breaking its documented "always exits 0
   (advisory)" contract. Fixed with `(i.get("incident_updates") or [{}])[0]`. Verified against
   real-shaped API input.

3. **[P3] `scripts/check-data-platform-skill-reachability.py:116` — substring reachability
   match.** `name in agents_text` reports a skill reachable whenever its name is a *substring*
   of a referenced longer name (e.g. `cube-schema` passes purely because `cube-schema-scaffolding`
   is referenced), so a genuinely-unreachable skill can slip past this gate — its own
   "structurally invisible at runtime" failure mode. Fixed with a word-boundary regex
   (`(?<![\w-])name(?![\w-])`), the idiom already used at `check-mcp-attribution.py:101`.
   Verified: real tree still passes (15/15), the audit must-fail fixture still fails, and the
   short-name collision is now correctly flagged.

## Needs your input — 1 item (gate-blocked)

**[P3] `plugins/ravenclaude-core/hooks/route-decision-review.sh:69` — stray non-zero exit when
the posture file has no `decision_review:` key.**

- **Defect:** the line runs
  `mode="$(grep -E '^\s*decision_review:' "$posture" … | tr …)"` under `set -euo pipefail`.
  When the posture file exists but contains no `decision_review:` key at all, `grep` exits 1,
  `pipefail` propagates it, and `errexit` aborts the hook at line 69 — it never reaches the
  nested-form `awk` fallback (:70–81, which already carries `|| true`) or the intended
  `emit_allow` (:84).
- **Severity/direction:** P3, **fails safe.** Claude Code treats a non-zero hook exit as a
  non-blocking error, so the `AskUserQuestion` proceeds — exactly the intended behavior when
  decision-review is unconfigured. The only cost is a stray non-zero exit / possible log noise
  instead of a clean `emit_allow`.
- **Recommended fix:** append `|| true` to the line-69 command substitution, matching the
  guarded idiom already used elsewhere in the same file (lines 138, 141–144).
- **Why it isn't in the PR:** the command-review tribunal (the Thing) **denied** the edit as
  `xc.tribunal-self-disable` — it refuses unilateral edits to its own routing hook by design and
  directs changes through the comfort-posture dashboard / maintainer path. That gate did its
  job; I did not bypass it. **Please apply via the sanctioned path, or approve editing this
  file for this one-line fail-safe guard.**

## Noted but intentionally not fixed

**[Cosmetic] `scripts/check-hook-failclosed.sh:168–173, 183–188`** — in `--self-test` "teeth"
mode the failure branch calls `bad` (which already increments `FAIL`) *and* then increments
`FAIL` again, double-counting. It never changes the pass/fail verdict (any `FAIL>0` still exits
2) and only triggers if the teeth self-test itself regresses. Left as-is; flagging for
awareness only.

## CI-security pass (no findings)

All `.github/workflows/*` actions are SHA-pinned; there is no `pull_request_target`; and every
untrusted `github.event.*` value flows through an `env:` block (the sanctioned injection
mitigation) rather than inline `run:` interpolation — on top of the existing `zizmor` and
workflow-hygiene gates.
