#!/usr/bin/env bash
#
# spike-tprose-canary.sh — P1 / S1 of docs/plans/2026-08-19-product-inventory/plan.md
#
# ⛔ WHY THIS EXISTS. Plan A asserted that inventory authoring is compatible with
# guard-premise T-PROSE and never tested it — which is precisely the shape T-PROSE
# exists to catch. This drives the REAL hook with concept-file-shaped payloads and
# records a literal verdict per question. It is re-runnable, so the authoring rule
# in docs/best-practices/inventory-authoring.md stays bound to a measurement rather
# than to a paragraph somebody wrote once.
#
# ⛔ NO APOSTROPHES ANYWHERE IN THIS FILE. Parts of the guard are embedded in a
# single-quoted bash block; the same discipline applies here so a copy-paste of a
# fixture into that context cannot close the string and make a gate fail OPEN.
#
# ⛔ THE FIXTURE PROSE IS printf-ASSEMBLED, NEVER WRITTEN LITERALLY. This file must
# CONTAIN the shape the guard denies, and the guard scans the content of the write
# that creates this file. The same precedent is recorded at the head of
# test-guard-premise-scope.sh. Do not "simplify" these into literals.
#
# ⛔ THE SCRATCH DIR IS CLEANED WITH A HELPER, NOT AN INLINE RECURSIVE DELETE.
# Measured while authoring this file: guard-destructive matched the cleanup line
# in the FILE TEXT and blocked the write, because a guard cannot tell a command
# from a description of one. Same class as the printf note above.
#
# Exit 0 = every question answered AND the positive control fired.
# Exit 1 = a question is unanswerable, or the control did not fire (a blind probe).

set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$HERE/plugins/ravenclaude-core/hooks/guard-premise.sh"
TMP="$(mktemp -d)"
_cleanup() { [ -n "${TMP:-}" ] && [ -d "$TMP" ] && command find "$TMP" -mindepth 0 -delete 2>/dev/null; }
trap _cleanup EXIT

PROJ="$TMP/proj"
CDIR="$PROJ/plugins/ravenclaude-core/knowledge/concepts"
mkdir -p "$CDIR"

PASS=0; FAIL=0
VERDICTS="$TMP/verdicts.tsv"
: > "$VERDICTS"

ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s (%s)\n' "$1" "$2"; }

# Build a PreToolUse payload. python3 avoids hand-quoting JSON.
_payload() { # tool path content
  python3 - "$1" "$2" "$3" <<'PY'
import json, sys
tool, path, content = sys.argv[1], sys.argv[2], sys.argv[3]
ti = {"file_path": path}
if tool == "Write":
    ti["content"] = content
elif tool == "Edit":
    ti["old_string"] = "PLACEHOLDER"
    ti["new_string"] = content
else:
    ti["edits"] = [{"old_string": "PLACEHOLDER", "new_string": content}]
json.dump({"tool_name": tool, "tool_input": ti, "session_id": "spike-s1"}, sys.stdout)
PY
}

# 2 = deny, 0 = allow. Anything else is a broken probe, not a verdict.
_run() { # tool path content
  local _rc=0
  _payload "$1" "$2" "$3" \
    | CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" "$PROJ" >/dev/null 2>&1 || _rc=$?
  printf '%s' "$_rc"
}

# Record a literal verdict AND assert the expectation, so the published table
# cannot drift away from the assertions that gate on it.
verdict() { # qid question tool path content want_rc
  local got; got="$(_run "$3" "$4" "$5")"
  local lit; case "$got" in 2) lit="DENY";; 0) lit="ALLOW";; *) lit="BROKEN(rc=$got)";; esac
  printf '%s\t%s\t%s\n' "$1" "$2" "$lit" >> "$VERDICTS"
  if [ "$got" = "$6" ]; then ok "$1 — $2 => $lit"; else bad "$1 — $2" "want rc $6, got $got"; fi
}

# ── The diagnosis shape, assembled ──────────────────────────────────────────
# _SUBJ "The scheduler" + _FAILS "does not fire" => a defect predicate about a
# named subject. This is the claim every fixture below carries.
DIAG="$(printf 'The %s %s %s fire on the delivered channel.' scheduler does not)"
CTRL_LINE="$(printf '%s: the same payload with the trigger removed did not deny' control)"
FILLER='Ordinary explanatory prose that asserts nothing about any named subject.'

# Frontmatter carrying a date stamp and a sources block, as a real concept file has.
_fm() { # last_verified_line_present(1|0)
  printf -- '---\n'
  printf 'id: hook-message-channels\n'
  printf 'title: Hook message channels\n'
  printf 'kind: platform-fact\n'
  [ "$1" = "1" ] && printf 'last_verified: 2026-08-19\n'
  printf 'sources:\n'
  printf -- '  - label: delivered-channel bake-off\n'
  printf -- '    url: https://example.invalid/bake-off\n'
  printf -- '---\n'
}

echo "── P1/S1: T-PROSE canary against the real guard-premise hook ──"

# ── 0. POSITIVE CONTROL. Asserted FIRST. ────────────────────────────────────
# ⛔ Every ALLOW verdict below is vacuous unless this DENY fires: "the guard did
# not deny" and "the guard never ran" are otherwise indistinguishable. This is the
# same discipline the delivered-channel bake-off used, one layer up.
CONTROL_BODY="$(printf '%s\n\n%s\n\n%s\n' "$(_fm 1)" "Measured 2026-08-19." "$DIAG")"
verdict "S1-C0" "positive control: stamped diagnosis, no control => DENY" \
  "Write" "$CDIR/canary-control.md" "$CONTROL_BODY" "2"

# ── Q1. Does a frontmatter-only sources: block satisfy _CTRL for a deep claim? ─
# The claim sits in body paragraph 3+, deliberately outside the +/-6-line window
# from the frontmatter. Prior: no, _CTRL is a window regex, not document-level.
Q1_BODY="$(printf '%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s 2026-08-19.\n%s\n' \
  "$(_fm 1)" "$FILLER" "$FILLER" "$FILLER" "$FILLER" "$FILLER" "$FILLER" "Measured" "$DIAG")"
verdict "S1-Q1" "frontmatter sources: clears a body-paragraph-3+ claim" \
  "Write" "$CDIR/canary-q1.md" "$Q1_BODY" "2"

# ── Q2. Does an inline control: line immediately ABOVE the claim clear it? ────
Q2_BODY="$(printf '%s\n\n%s\n\n%s\n\n%s 2026-08-19.\n%s\n%s\n' \
  "$(_fm 1)" "$FILLER" "$FILLER" "Measured" "$CTRL_LINE" "$DIAG")"
verdict "S1-Q2" "control: line immediately ABOVE the claim clears it" \
  "Write" "$CDIR/canary-q2.md" "$Q2_BODY" "0"

# ── Q3. A SECOND dated claim later in the body, with no adjacent control ─────
# If this denies, the authoring rule is one control per CLAIM, not one per FILE.
# 12 filler lines put the second claim outside the first control line window.
Q3_BODY="$(printf '%s\n\n%s 2026-08-19.\n%s\n%s\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n\n%s 2026-08-19.\n%s\n' \
  "$(_fm 1)" "Measured" "$CTRL_LINE" "$DIAG" \
  "$FILLER" "$FILLER" "$FILLER" "$FILLER" "$FILLER" "$FILLER" \
  "$FILLER" "$FILLER" "$FILLER" "$FILLER" "$FILLER" "$FILLER" \
  "Measured" "$DIAG")"
verdict "S1-Q3" "a SECOND claim with no adjacent control still denies" \
  "Write" "$CDIR/canary-q3.md" "$Q3_BODY" "2"

# ── Q4. Does the YAML last_verified: date alone arm _STAMP for a nearby claim? ─
# Same body twice, differing ONLY in whether frontmatter carries last_verified,
# and with NO other stamp anywhere. If the with-date form denies and the without
# form allows, the frontmatter date is by itself the trigger.
Q4_WITH="$(printf '%s\n\n%s\n' "$(_fm 1)" "$DIAG")"
Q4_WITHOUT="$(printf '%s\n\n%s\n' "$(_fm 0)" "$DIAG")"
verdict "S1-Q4a" "frontmatter last_verified: date alone arms _STAMP" \
  "Write" "$CDIR/canary-q4a.md" "$Q4_WITH" "2"
verdict "S1-Q4b" "the SAME body with no date stamp anywhere is allowed" \
  "Write" "$CDIR/canary-q4b.md" "$Q4_WITHOUT" "0"

# ── Q5. ⛔ GT6 CHECK. Does T-PROSE fire on an EDIT to an EXISTING file? ───────
# The plan records GT6 as "T-PROSE fires only on file CREATE", citing the
# os.path.exists(path) early-exit. That exit gates T-SHAPE only; the hook header
# states T-PROSE is OR-ed and that none of the T-SHAPE exemptions may suppress it.
# Measured here rather than read, because the whole re-stamp lane depends on it.
printf 'PLACEHOLDER\n' > "$CDIR/canary-q5.md"
verdict "S1-Q5" "T-PROSE fires on an EDIT to a file that ALREADY EXISTS" \
  "Edit" "$CDIR/canary-q5.md" "$CONTROL_BODY" "2"

# ── Q6. A bare re-stamp Edit carries no diagnosis, so it is exempt by CONTENT ─
# This is the lane the plan needs: bumping last_verified must not be denied.
# It passes not because edits are exempt (Q5 refutes that) but because the
# replacement text contains no defect predicate. Different reason, same outcome —
# and the difference is what makes the authoring rule correct.
verdict "S1-Q6" "a bare last_verified re-stamp Edit is allowed (no diagnosis)" \
  "Edit" "$CDIR/canary-q5.md" "last_verified: 2026-08-19" "0"

echo
echo "── Literal verdict table ──"
printf '  %-8s  %-58s  %s\n' "ID" "QUESTION" "VERDICT"
while IFS=$'\t' read -r a b c; do printf '  %-8s  %-58s  %s\n' "$a" "$b" "$c"; done < "$VERDICTS"
echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || { echo "S1 INCOMPLETE — a question has no usable verdict."; exit 1; }
echo "S1 complete — every question carries a literal verdict and the control fired."
