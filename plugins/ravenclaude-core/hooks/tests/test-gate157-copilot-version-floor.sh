#!/usr/bin/env bash
# Gate 157 — the Copilot version floor is checked, and checking it can NEVER
# break the installer (multi-host audit MH-23).
#
# WHY THIS GATE EXISTS
#
# The floor is a SAFETY floor, quoted verbatim from the github/copilot-cli
# changelog (retrieved 2026-07-28):
#
#   1.0.52 (2026-05-23) — "Hooks (preToolUse, postToolUse, subagentStart,
#   subagentStop) now fire correctly for sub-agent tool…"
#
# Below it a SUB-AGENT's tool calls are not hooked at all, so a subagent runs Bash
# straight past the tribunal, guard-destructive, the runaway brake and the layout
# gate — silently, while `install` prints success. Nothing checked this until now.
#
# THE SECOND HALF IS THE ONE THAT ALREADY BIT. `scripts/ravenclaude` runs under
# `set -euo pipefail`. The first version of this check used a bare
# `$(… | grep -E … | head -1)`; a `copilot` printing an unparseable version made
# grep exit 1, pipefail propagated it, and `set -e` ABORTED `ravenclaude status`
# outright (verified: EXIT=1, output truncated mid-run). A version check that kills
# the installer is strictly worse than no version check — it is the same
# fail-in-the-dangerous-direction defect the audit exists to close, committed by
# the guard against it. Hence: every scenario below asserts EXIT=0.
#
# Driven through the REAL `scripts/ravenclaude status` against stub `copilot`
# binaries on PATH — never a reimplementation of the comparison.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RC="$HERE/../../../../scripts/ravenclaude"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  ✗ %s\n' "$1"; }

[ -f "$RC" ] || { printf 'FATAL: installer not found at %s\n' "$RC" >&2; exit 1; }

PROJ="$TMP/proj"; mkdir -p "$PROJ"
BIN="$TMP/bin"; mkdir -p "$BIN"

# run_with <stub-body> -> prints "EXIT|output"
run_with() {
  printf '#!/bin/sh\n%s\n' "$1" >"$BIN/copilot"
  chmod +x "$BIN/copilot"
  local out rc
  out="$(PATH="$BIN:$PATH" bash "$RC" status --project "$PROJ" 2>&1)"; rc=$?
  printf '%s\n' "$rc"
  printf '%s\n' "$out" >"$TMP/last.out"
}

expect() { # <label> <stub> <exit> <regex-that-must-appear>
  local label="$1" stub="$2" want_rc="$3" want_re="$4" got_rc
  got_rc="$(run_with "$stub")"
  if [ "$got_rc" != "$want_rc" ]; then
    bad "$label — exit $got_rc, wanted $want_rc"; return
  fi
  if grep -qE "$want_re" "$TMP/last.out"; then ok "$label"; else
    bad "$label — output did not match /$want_re/"
  fi
}

printf '── Gate 157: Copilot version floor + fail-safe ──\n'

# ── the floor actually fires ────────────────────────────────────────────────
expect "below floor (1.0.41) warns that sub-agent calls are unhooked" \
  'echo "copilot version 1.0.41"' 0 'BELOW 1\.0\.52'
expect "at floor (1.0.52) is accepted" \
  'echo "copilot version 1.0.52"' 0 'meets the 1\.0\.52 safety floor'
expect "above floor (1.0.75) is accepted" \
  'echo "copilot version 1.0.75"' 0 'meets the 1\.0\.52 safety floor'

# 1.0.75 vs 1.0.57 is the case a naive string compare gets WRONG ("1.0.75" <
# "1.0.57" lexically is false, but "1.0.9" < "1.0.57" lexically is true). Assert a
# two-digit-vs-one-digit patch pair explicitly.
expect "version compare is numeric, not lexical (1.0.9 < 1.0.52)" \
  'echo "copilot version 1.0.9"' 0 'BELOW 1\.0\.52'

# ── fail-safe: NONE of these may be fatal, and none may claim you are fine ──
expect "unparseable version does not abort, and does not claim the floor is met" \
  'echo "totally unparseable"' 0 'could not parse a version'
expect "copilot exiting non-zero does not abort" \
  'exit 3' 0 'could not parse a version'
expect "copilot printing nothing does not abort" \
  'true' 0 'could not parse a version'

# ── the diagnostic is ACTIONABLE, not merely non-fatal ──────────────────────
# The three assertions above prove only that we did not abort and did not claim
# the floor is met. They pass just as happily on a bare one-line shrug, so
# without the four below the "clear error" contract is UNGATED and a regression
# that drops the raw output or the expected format stays green forever.
expect "unparseable error quotes the RAW copilot output verbatim" \
  'echo "copilot build nightly-xyz"' 0 'raw output.*nightly-xyz'
expect "unparseable error states the EXPECTED version format" \
  'echo "copilot build nightly-xyz"' 0 'expected.*x\.y\.z'
expect "unparseable error states the REQUIRED floor" \
  'echo "copilot build nightly-xyz"' 0 'required.*>= 1\.0\.52'
expect "empty output reads as '(no output)', never a blank quote" \
  'true' 0 'raw output.*\(no output\)'

# ── build-qualified versions parse (the bug this gate could not see) ────────
# `1.0.52.3` is ABOVE the floor, but the pre-fix whole-token parser matched
# NOTHING and reported "could not parse" — a silently-unverified floor on a
# compliant copilot. The floor being unverified is the failure mode this whole
# gate exists to prevent, and it was reachable through the parser.
expect "four-component version parses to its first three (1.0.52.3)" \
  'echo "copilot version 1.0.52.3"' 0 'copilot 1\.0\.52 .* meets the 1\.0\.52 safety floor'
expect "prerelease-suffixed version parses (v1.0.75-beta.1)" \
  'echo "copilot version v1.0.75-beta.1"' 0 'copilot 1\.0\.75 .* meets the 1\.0\.52 safety floor'
expect "four-component version BELOW the floor still warns (1.0.41.9)" \
  'echo "copilot version 1.0.41.9"' 0 'BELOW 1\.0\.52'

# copilot entirely absent from PATH.
out="$(PATH="/usr/bin:/bin" bash "$RC" status --project "$PROJ" 2>&1)"; rc=$?
if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q 'not on PATH'; then
  ok "copilot absent from PATH does not abort"
else
  bad "copilot absent from PATH — exit $rc"
fi

# ── TEETH ───────────────────────────────────────────────────────────────────
# 1. Strip the `|| true` guards and prove an unparseable version becomes FATAL
#    again. This is the regression that already happened once.
MUT="$TMP/ravenclaude-mutant"
sed 's/ | head -1 || true)"/ | head -1)"/; s/2>\/dev\/null | head -1 || true)"/2>\/dev\/null | head -1)"/' "$RC" >"$MUT"
if ! grep -q "head -1)\"" "$MUT"; then
  bad "teeth: could not build the fail-open mutant (guard text changed?)"
else
  printf '#!/bin/sh\necho "totally unparseable"\n' >"$BIN/copilot"; chmod +x "$BIN/copilot"
  PATH="$BIN:$PATH" bash "$MUT" status --project "$PROJ" >/dev/null 2>&1
  mrc=$?
  if [ "$mrc" -ne 0 ]; then
    ok "teeth: without '|| true' an unparseable version ABORTS (exit $mrc) — the guard is real"
  else
    bad "teeth: mutant still exited 0 — the '|| true' guards may be vacuous"
  fi
fi

# 2. Raise the floor above every test version and prove the comparison is live
#    rather than a constant that happens to read well.
MUT2="$TMP/ravenclaude-mutant2"
sed 's/^COPILOT_FLOOR="1.0.52"$/COPILOT_FLOOR="9.9.9"/' "$RC" >"$MUT2"
printf '#!/bin/sh\necho "copilot version 1.0.75"\n' >"$BIN/copilot"; chmod +x "$BIN/copilot"
# CAPTURE THEN GREP — never `cmd | grep -q` under `set -o pipefail`.
# `grep -q` exits on first match and closes the pipe; the upstream command then
# takes SIGPIPE/EPIPE and exits non-zero, and pipefail propagates that into the
# `if`, so a MATCH reads as a FAILURE. That exact trap made this assertion report
# a broken guard while the guard was working correctly.
mut2_out="$(PATH="$BIN:$PATH" bash "$MUT2" status --project "$PROJ" 2>&1 || true)"
if printf '%s' "$mut2_out" | grep -q 'BELOW 9\.9\.9'; then
  ok "teeth: raising the floor flips a previously-passing version to BELOW"
else
  bad "teeth: floor appears not to drive the comparison"
fi

# 3. Drop the `-o` from the version extractor — the one flag that makes it
#    capture the TOKEN rather than the whole matching line — and prove the
#    build-qualified assertions above are what catch it. Without this half those
#    assertions could be passing for some unrelated reason.
MUT3="$TMP/ravenclaude-mutant3"
sed 's/grep -Eo /grep -E /' "$RC" >"$MUT3"
if ! grep -q "grep -E '\[0-9\]" "$MUT3"; then
  bad "teeth: could not build the extractor mutant (extractor text changed?)"
else
  printf '#!/bin/sh\necho "copilot version 1.0.52.3"\n' >"$BIN/copilot"; chmod +x "$BIN/copilot"
  # CAPTURE THEN GREP — never `cmd | grep -q` under `set -o pipefail` (see above).
  mut3_out="$(PATH="$BIN:$PATH" bash "$MUT3" status --project "$PROJ" 2>&1 || true)"
  if printf '%s' "$mut3_out" | grep -qE 'copilot 1\.0\.52 .* meets'; then
    bad "teeth: without 'grep -Eo' the build-qualified version still parsed cleanly"
  else
    ok "teeth: without 'grep -Eo' the four-component version no longer parses"
  fi
fi

printf '\n  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
