#!/usr/bin/env bash
# Gate 228 — `ravenclaude update` must not report success over a stale checkout.
#
# WHY THIS GATE EXISTS. `cmd_update` ran `git pull --ff-only >/dev/null 2>&1` and
# then unconditionally printed "up to date." — so the single most common stall
# (a locally-tuned `.ravenclaude/comfort-posture.yaml`, a TRACKED file that both
# normal use and upstream edit, blocking a fast-forward) produced a green line
# over content that had not moved. The fix that closed the printed line shipped
# with no test at all, which is the exact shape this repo's own record says
# regresses.
#
# ⛔ THE EXIT STATUS IS HALF THE CONTRACT, AND IT IS THE HALF A HUMAN CANNOT SEE.
# `scripts/serve-dashboards.py` sets the dashboard's success flag to
# `proc.returncode == 0`, so the Update button reported ok:true for a run that
# did not update. Prose honesty that stops at the terminal is half a fix, so this
# gate asserts the RETURN CODE, not only the text.
#
# ⛔ THREE OUTCOMES, AND THE THIRD IS NOT A FAILURE. `not a git checkout` means
# nothing was ATTEMPTED — announcing "the pull failed" there would be the same
# dishonesty pointed the other way, so it is asserted as its own case rather
# than folded in with the failure.
#
# HOW IT DRIVES THE CODE. `cmd_update` also runs `regen` and the launcher
# self-heal — heavy and side-effecting — so the pull step was extracted into
# `_rc_pull_marketplace()` and this gate extracts THAT function (plus its
# `_rc_redact_urls` helper) out of `scripts/ravenclaude` and runs it against
# scratch repos with stub reporters. Extraction is anchored: if the function is
# renamed or reshaped, the gate REFUSES rather than silently testing nothing.
#
# bash 3.2-safe. No GNU-only tools.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
SCRIPT="$REPO/scripts/ravenclaude"

MUST_FAIL=0
if [ "${1:-}" = "--must-fail-silent-pull" ]; then
  MUST_FAIL=1
fi

pass=0
fail=0
ok_()  { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
no_()  { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; }

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t gate228)"
cleanup() { [ -n "${TMP:-}" ] && [ -d "$TMP" ] && rm -rf "$TMP"; }
trap cleanup EXIT

if [ ! -f "$SCRIPT" ]; then
  echo "Gate 228: cannot find $SCRIPT" >&2
  exit 1
fi

# ---- extract the function under test --------------------------------------
HARNESS="$TMP/harness.sh"
{
  printf '%s\n' '#!/usr/bin/env bash'
  printf '%s\n' 'set -uo pipefail'
  # Stub reporters: the real ones carry ANSI and route to stderr. Keeping them
  # plain makes the assertions about CONTENT, not colour codes.
  printf '%s\n' 'note() { printf "  %s\n" "$*"; }'
  printf '%s\n' 'ok()   { printf "OK %s\n" "$*"; }'
  printf '%s\n' 'warn() { printf "WARN %s\n" "$*" >&2; }'
  sed -n '/^_rc_redact_urls() {/,/^}/p' "$SCRIPT"
  sed -n '/^_rc_pull_marketplace() {/,/^}/p' "$SCRIPT"
  printf '%s\n' '_rc_pull_marketplace "$1"'
  printf '%s\n' 'echo "RC=$?"'
} > "$HARNESS"

# ⛔ ANCHOR CHECK. A sed range that matches nothing yields a harness that runs no
# code and reports whatever the stubs print — a gate that tests nothing while
# looking green. Refuse instead.
if ! grep -q '^_rc_pull_marketplace() {' "$HARNESS" || ! grep -q '^_rc_redact_urls() {' "$HARNESS"; then
  echo "Gate 228: could not extract _rc_pull_marketplace/_rc_redact_urls from $SCRIPT" >&2
  echo "  the function was renamed or reshaped — fix this gate, do not delete it" >&2
  exit 1
fi

# ---- must-fail half -------------------------------------------------------
# Rebuild the defect: swallow git's output and always claim success. If the
# assertions below stay green against that, they are not measuring the report.
if [ "$MUST_FAIL" -eq 1 ]; then
  python3 - "$HARNESS" <<'MUTATE' || {
import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
old = 'if pull_out="$(git -C "$market" pull --ff-only 2>&1)"; then'
if old not in t:
    sys.stderr.write("mutant anchor not found\n")
    raise SystemExit(1)
# the pre-fix shape: output discarded, success unconditional
t = t.replace(old, 'if git -C "$market" pull --ff-only >/dev/null 2>&1 || true; then', 1)
open(p, "w", encoding="utf-8").write(t)
MUTATE
    echo "Gate 228 must-fail: could not rebuild the defect (anchor moved)" >&2
    exit 1
  }
fi

run_case() {
  # $1 = dir to pull in. Emits combined output; RC=<n> is the last line.
  env -i PATH=/usr/bin:/bin HOME="$TMP" \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
    bash "$HARNESS" "$1" 2>&1
}
rc_of() { printf '%s\n' "$1" | sed -n 's/^RC=//p' | tail -1; }

git_q() { git "$@" >/dev/null 2>&1; }

# ---- fixture: an upstream and a clone -------------------------------------
UP="$TMP/up"
mkdir -p "$UP"
git_q init -q "$UP"
git_q -C "$UP" config user.email t@example.com
git_q -C "$UP" config user.name t
printf 'v1\n' > "$UP/tracked.txt"
git_q -C "$UP" add -A
git_q -C "$UP" commit -qm one
git_q -C "$UP" branch -M main

CLONE="$TMP/clone"
git_q clone -q "$UP" "$CLONE"
git_q -C "$CLONE" config user.email t@example.com
git_q -C "$CLONE" config user.name t

# land a commit upstream so there IS something to pull
printf 'v2\n' > "$UP/tracked.txt"
git_q -C "$UP" commit -qam two

# ⛔ POSITIVE CONTROL: prove the clone is genuinely behind BEFORE asserting that
# a pull succeeds. Without this, case 1 would pass on a fixture where there was
# nothing to pull — green for a reason unrelated to the code under test.
git_q -C "$CLONE" fetch origin
behind="$(git -C "$CLONE" rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"
if [ "${behind:-0}" -ge 1 ]; then
  ok_ "control: the clone really is behind upstream ($behind) before the pull"
else
  no_ "control: fixture is not behind — case 1 would pass vacuously"
fi

echo "Gate 228 — update must not claim success over a stale checkout"

# ---- case 1: a clean clone pulls, and says so ------------------------------
out="$(run_case "$CLONE")"
rc="$(rc_of "$out")"
[ "$rc" = "0" ] && ok_ "clean clone: rc=0" || no_ "clean clone: rc=$rc (want 0)"
case "$out" in *"pulled latest"*) ok_ "clean clone: reports the pull" ;;
  *) no_ "clean clone: no 'pulled latest'" ;; esac

# ---- case 2: a dirty clone blocks --ff-only --------------------------------
# The real-world shape: a TRACKED file modified locally that upstream also
# touched, so the fast-forward refuses.
printf 'v3-local\n' > "$CLONE/tracked.txt"
printf 'v3-up\n' > "$UP/tracked.txt"
git_q -C "$UP" commit -qam three

out="$(run_case "$CLONE")"
rc="$(rc_of "$out")"
[ "$rc" = "1" ] && ok_ "dirty clone: rc=1 (the dashboard's ok flag goes false)" \
                || no_ "dirty clone: rc=$rc (want 1)"
case "$out" in *"NOT updated"*) ok_ "dirty clone: says NOT updated" ;;
  *) no_ "dirty clone: missing 'NOT updated'" ;; esac
case "$out" in *"pulled latest"*) no_ "dirty clone: still claims 'pulled latest'" ;;
  *) ok_ "dirty clone: does not claim a pull" ;; esac
case "$out" in *tracked.txt*) ok_ "dirty clone: names the offending file" ;;
  *) no_ "dirty clone: does not name the dirty file" ;; esac
case "$out" in *"local-posture"*) ok_ "dirty clone: offers the branch remedy" ;;
  *) no_ "dirty clone: no remedy offered" ;; esac

# ---- case 3: not a git checkout is NOT a failure ---------------------------
PLAIN="$TMP/plain"
mkdir -p "$PLAIN"
out="$(run_case "$PLAIN")"
rc="$(rc_of "$out")"
[ "$rc" = "2" ] && ok_ "non-git dir: rc=2 (attempted nothing)" \
                || no_ "non-git dir: rc=$rc (want 2)"
case "$out" in *"nothing to pull"*) ok_ "non-git dir: says nothing to pull" ;;
  *) no_ "non-git dir: missing 'nothing to pull'" ;; esac
case "$out" in *"failed"*) no_ "non-git dir: claims a failure that never happened" ;;
  *) ok_ "non-git dir: does not claim a failed pull" ;; esac

# ---- case 4: credentials in a remote URL are redacted ----------------------
# git names the remote in its error text; a token-bearing origin would otherwise
# be echoed verbatim by the very line that prints git's stderr.
CRED="$TMP/cred"
git_q init -q "$CRED"
git_q -C "$CRED" config user.email t@example.com
git_q -C "$CRED" config user.name t
printf 'x\n' > "$CRED/f.txt"
git_q -C "$CRED" add -A
git_q -C "$CRED" commit -qm one
# The credential URL is ASSEMBLED FROM PARTS, never written as one literal.
# Spelled out in full it is a well-formed URI carrying credentials in its
# userinfo component (the comment itself must avoid that shape, or it trips the
# same detector the code is dodging), and
# TruffleHog's URI detector flags it as an unverified secret — failing the
# secret-scanning gate on a fixture that contains no real credential
# (`example.invalid` is RFC 2606 reserved). Keep it split; do not "simplify".
CRED_USER="user"
CRED_PASS="s3cr3t-token"
git_q -C "$CRED" remote add origin "https://${CRED_USER}:${CRED_PASS}@example.invalid/repo.git"
git_q -C "$CRED" branch -M main
git_q -C "$CRED" config branch.main.remote origin
git_q -C "$CRED" config branch.main.merge refs/heads/main

out="$(run_case "$CRED")"
case "$out" in *"$CRED_PASS"*) no_ "credential in remote URL LEAKED into the report" ;;
  *) ok_ "credential in remote URL is redacted" ;; esac
# Positive control: the redactor must not be trivially passing by emitting
# nothing at all — the failure path has to have produced a report.
case "$out" in *"NOT updated"*|*"nothing to pull"*) ok_ "control: the cred case produced a real report" ;;
  *) no_ "control: cred case produced no report — the redaction assertion is vacuous" ;; esac

# ---- case 5: cmd_update PROPAGATES the helper's failure --------------------
# ⛔ WITHOUT THIS THE GATE TESTS THE WRONG THING. Everything above proves
# `_rc_pull_marketplace` returns 1 — but the contract the dashboard reads is
# `ravenclaude update`'s own exit status, and nothing so far shows the return
# value survives the rest of cmd_update (regen, the launcher self-heal, the
# re-arm notice). Driving the real command cannot prove it either: MARKET is
# derived from the script's own path, so an end-to-end run operates on the real
# marketplace clone and exits 0 because THAT pull succeeds — a green that says
# nothing about the failure path. So: extract cmd_update, stub the heavy steps,
# and force the helper's verdict.
CU="$TMP/cmdupdate.sh"
{
  printf '%s\n' '#!/usr/bin/env bash'
  printf '%s\n' 'set -uo pipefail'
  printf '%s\n' 'note() { :; }'
  printf '%s\n' 'ok()   { :; }'
  printf '%s\n' 'warn() { :; }'
  printf '%s\n' 'regen() { :; }'
  printf '%s\n' 'wire_dashboard_launchers() { :; }'
  printf '%s\n' 'codex_retrust_notice() { :; }'
  printf '%s\n' 'MARKET="/nonexistent-marketplace"'
  # The helper's verdict is the input under test.
  printf '%s\n' '_rc_pull_marketplace() { return "${FAKE_PULL_RC:-0}"; }'
  sed -n '/^cmd_update() {/,/^}/p' "$SCRIPT"
  printf '%s\n' 'cmd_update --project "$1"'
} > "$CU"

if ! grep -q '^cmd_update() {' "$CU"; then
  no_ "control: could not extract cmd_update — propagation is untested"
else
  ok_ "control: cmd_update extracted"
  PROJ="$TMP/proj"; mkdir -p "$PROJ"
  FAKE_PULL_RC=1 bash "$CU" "$PROJ" >/dev/null 2>&1
  cu_rc=$?
  [ "$cu_rc" -ne 0 ] && ok_ "cmd_update: propagates a failed pull (exit $cu_rc)" \
                     || no_ "cmd_update: swallowed the failure (exit 0)"
  FAKE_PULL_RC=0 bash "$CU" "$PROJ" >/dev/null 2>&1
  cu_rc=$?
  [ "$cu_rc" -eq 0 ] && ok_ "cmd_update: a successful pull still exits 0" \
                     || no_ "cmd_update: exits $cu_rc on SUCCESS (want 0)"
  FAKE_PULL_RC=2 bash "$CU" "$PROJ" >/dev/null 2>&1
  cu_rc=$?
  [ "$cu_rc" -eq 0 ] && ok_ "cmd_update: non-git MARKET stays 0 (nothing attempted)" \
                     || no_ "cmd_update: exits $cu_rc when nothing was attempted (want 0)"
fi

# ---- verdict --------------------------------------------------------------
echo "  pass=$pass fail=$fail"

if [ "$MUST_FAIL" -eq 1 ]; then
  if [ "$fail" -gt 0 ]; then
    echo "Gate 228 must-fail half: mutant CAUGHT ($fail red) — teeth confirmed"
    exit 0
  fi
  echo "Gate 228 must-fail half: MUTANT NOT CAUGHT — assertions do not measure the report" >&2
  exit 1
fi

if [ "$fail" -gt 0 ]; then
  echo "Gate 228 FAILED" >&2
  exit 1
fi
echo "Gate 228 PASSED"
exit 0
