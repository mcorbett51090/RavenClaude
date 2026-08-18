#!/usr/bin/env bash
# Gate 231 — `git push` delete-detection is scoped to the push segment.
#
# WHY THIS GATE EXISTS. `_is_dangerous_git_push_delete` ran its flag regexes over
# the WHOLE command string once any `git push` appeared anywhere in it. So a `-d`
# belonging to a completely different command was read as `git push --delete`.
#
# control (2026-08-18): `git push -u origin b; echo $(wc -w | tr -d ' ')`
# -> DENIED as git-push-remote-branch-delete. Nothing is deleted there; the `-d`
# is `tr`'s. Removing the `tr` from the same line -> allowed, so the trigger was
# the unrelated token and not the push. Observed live: it blocked an ordinary
# `git push -u origin <branch>` in a compound command.
#
# ⛔ THIRD INSTANCE OF ONE DEFECT CLASS. srm.force-push (v0.242.0) and
# sce.curl-pipe-shell (v0.244.0) were the same shape: a rule that matches on a
# token, applied to a string wider than the command that token belongs to. The
# repo's own record says "when you fix a pattern, enumerate every instance of
# that pattern before you close it" — this one was missed both times, and it was
# missed because NOTHING exercised the predicate. That is what this gate is.
#
# ⛔ THE REMEDY IS NOT PORTABLE ACROSS SIBLINGS. Splitting on `;`/`&`/`|` is
# right HERE because a push flag never crosses a separator. curl-pipe-shell must
# NOT exclude `|` — a fetch piped into an interpreter is exactly what it hunts.
# Same class, opposite correct fix; that is why each is tested on its own terms.
#
# The FALSE-NEGATIVE half is the load-bearing one: a predicate that never fires
# would pass every "did it stop crying wolf?" assertion. Every allow case is
# paired with a deny case, including a delete in a LATER segment (proving the
# scan does not stop at the first segment).
#
# bash 3.2-safe. No GNU-only tools.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
GUARD="$(cd "$HERE/.." && pwd)/guard-destructive.sh"

MUST_FAIL=0
[ "${1:-}" = "--must-fail-unscoped" ] && MUST_FAIL=1

pass=0; fail=0
ok_() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
no_() { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; }

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t gate231)"
cleanup() { [ -n "${TMP:-}" ] && [ -d "$TMP" ] && rm -rf "$TMP"; }
trap cleanup EXIT

[ -f "$GUARD" ] || { echo "Gate 231: cannot find $GUARD" >&2; exit 1; }

# Extract the predicate rather than driving the whole hook: the hook needs a full
# PreToolUse payload and emits events, and what is under test is one function.
HARNESS="$TMP/harness.sh"
{
  printf '%s\n' '#!/usr/bin/env bash'
  printf '%s\n' 'set -uo pipefail'
  printf '%s\n' '_CMD_BOUNDARY="(^|[[:space:]]|;|&|\||\(|\{)"'
  sed -n '/^_is_dangerous_git_push_delete() {/,/^}/p' "$GUARD"
  printf '%s\n' 'if _is_dangerous_git_push_delete "$1"; then echo DENY; else echo ALLOW; fi'
} > "$HARNESS"

# ⛔ ANCHOR CHECK. A sed range that matches nothing yields a harness with no
# function, which would error identically for every case and could be misread.
if ! grep -q '^_is_dangerous_git_push_delete() {' "$HARNESS"; then
  echo "Gate 231: could not extract _is_dangerous_git_push_delete from $GUARD" >&2
  echo "  the predicate was renamed or reshaped — fix this gate, do not delete it" >&2
  exit 1
fi

if [ "$MUST_FAIL" -eq 1 ]; then
  # Rebuild the defect: run the flag regexes over the whole string again.
  python3 - "$HARNESS" <<'MUTATE' || {
import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
if 'case "$seg" in *"git push"*) ;; *) continue ;; esac' not in t:
    sys.stderr.write("mutant anchor not found\n"); raise SystemExit(1)
# Make every segment "contain" a push, i.e. drop the scoping entirely.
t = t.replace('case "$seg" in *"git push"*) ;; *) continue ;; esac', ':', 1)
# ...and feed the WHOLE command as one segment.
t = t.replace("$(printf '%s' \"$c\" | tr ';&|' '\\n\\n\\n')", '$c', 1)
open(p, "w", encoding="utf-8").write(t)
MUTATE
    echo "Gate 231 must-fail: could not rebuild the defect (anchor moved)" >&2
    exit 1
  }
fi

verdict() { bash "$HARNESS" "$1" 2>/dev/null | tail -1; }

expect_allow() {
  if [ "$(verdict "$1")" = "ALLOW" ]; then ok_ "allow: $2"; else no_ "DENIED (false positive): $2"; fi
}
expect_deny() {
  if [ "$(verdict "$1")" = "DENY" ]; then ok_ "deny:  $2"; else no_ "ALLOWED (lost its teeth): $2"; fi
}

echo "Gate 231 — push-delete detection is scoped to the push segment"

# ── must ALLOW ──────────────────────────────────────────────────────────────
expect_allow 'git push -u origin my-branch' 'plain push -u'
expect_allow "git push -u origin b; echo \$(wc -w | tr -d ' ')" 'push + tr -d in a later command (the reported FP)'
expect_allow 'git push origin main && rm -d somedir' 'push + rm -d in a later command'
expect_allow 'git push origin HEAD:refs/heads/main' 'src:dst refspec is not a deletion'
expect_allow 'git push origin main' 'ordinary push'
expect_allow 'git push --force-with-lease origin b' 'force-with-lease is not this rule'

# ── must DENY (the teeth) ───────────────────────────────────────────────────
expect_deny 'git push origin --delete my-branch' 'real --delete'
expect_deny 'git push origin -d my-branch' 'real -d'
expect_deny 'git push origin :my-branch' 'colon-refspec deletion'
expect_deny 'git push -qd origin doomed' 'bundled -qd'
# ⛔ Proves the scan does not stop at the first segment: without this, a fix that
# only ever looked at segment 1 would pass every assertion above.
expect_deny 'echo hi; git push origin -d doomed' 'deletion in a LATER segment'
expect_deny 'ls && git push origin --delete b' 'deletion after &&'

echo "  pass=$pass fail=$fail"

if [ "$MUST_FAIL" -eq 1 ]; then
  if [ "$fail" -gt 0 ]; then
    echo "Gate 231 must-fail half: mutant CAUGHT ($fail red) — teeth confirmed"; exit 0
  fi
  echo "Gate 231 must-fail half: MUTANT NOT CAUGHT — the scoping assertions are inert" >&2
  exit 1
fi
[ "$fail" -gt 0 ] && { echo "Gate 231 FAILED" >&2; exit 1; }
echo "Gate 231 PASSED"
exit 0
