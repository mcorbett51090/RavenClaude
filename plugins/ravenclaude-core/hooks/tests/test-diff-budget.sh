#!/usr/bin/env bash
# Gate 182 — the pre-commit blast-radius guard (scripts/check-diff-budget.py).
#
# THE INCIDENT THIS GUARDS (incidents.md, Incident 2): `render-trees.py` printed
# `ok` and deleted 806 tree SVGs + 186 concept visuals, and NOTHING in the commit
# path flagged that a documentation change was about to delete 806 tracked files.
#
# This file builds its OWN scratch repos and drives the guard through its CLI —
# deliberately not reusing the Python fixture builder, so a bug in that builder
# cannot make both halves agree with each other and neither with git.
#
# The exit codes are a CONTRACT, so they are asserted as VALUES, never as
# "nonzero": 0 = within budget, 2 = over budget, 1 = could-not-run. Collapsing
# 1 into 2 (or into 0) is the failure this whole design exists to prevent — a
# checker that cannot measure must not report clean.
#
# PORTABILITY (stock macOS bash 3.2 / BSD userland — four shipped incidents came
# from exactly these): no `declare -A`, no `mapfile`, no `${x^^}`, no
# `shopt -s globstar`, no `grep -P`, no `sed -i`, no GNU `timeout`.
set -uo pipefail

R="$(cd "$(dirname "$0")/../../../.." && pwd)"
GUARD="$R/scripts/check-diff-budget.py"
PY="$(command -v python3)"

T=$(mktemp -d)
REPO="$T/repo"
OUT="$T/out"
ERR="$T/err"

pass=0
fail=0

chk() {
  if [ "$2" = "$3" ]; then
    echo "  OK   $1"
    pass=$((pass + 1))
  else
    echo "  FAIL $1 (expected exit $2, got $3)"
    fail=$((fail + 1))
  fi
}

chk_out() { # label, grep-ERE pattern
  if grep -Eq "$2" "$OUT"; then
    echo "  OK   $1"
    pass=$((pass + 1))
  else
    echo "  FAIL $1 (pattern not in output: $2)"
    fail=$((fail + 1))
  fi
}

run() { # -> prints the exit code; stdout/stderr land in $OUT/$ERR
  "$PY" "$GUARD" --repo "$REPO" "$@" >"$OUT" 2>"$ERR"
  echo $?
}

git_q() { git -C "$REPO" "$@" >/dev/null 2>&1; }

seed() {
  mkdir -p "$REPO/docs/trees" "$REPO/src"
  i=0
  while [ $i -lt 100 ]; do
    printf '<svg id="%s"/>\n' "$i" >"$REPO/docs/trees/t$i.svg"
    i=$((i + 1))
  done
  i=0
  while [ $i -lt 12 ]; do
    printf 'x\n' >"$REPO/src/s$i.txt"
    i=$((i + 1))
  done
  git -C "$REPO" -c init.defaultBranch=main init -q
  git_q add -A
  git_q -c user.name=gate -c user.email=gate@example.invalid \
    -c commit.gpgsign=false commit -q --no-verify -m seed
}

restore() { git_q reset -q --hard HEAD; }

del_trees() { # n [stage]
  i=0
  while [ $i -lt "$1" ]; do
    rm -f "$REPO/docs/trees/t$i.svg"
    i=$((i + 1))
  done
  if [ "${2:-stage}" = "stage" ]; then git_q add -A; fi
}

mkdir -p "$REPO"
seed

echo "-- 1. THE REPLAY: a mass deletion riding along with a docs edit --"
del_trees 60
printf 'a doc change\n' >"$REPO/src/s0.txt"
git_q add -A
chk "60 deletions -> exit 2 (over budget)" 2 "$(run)"
chk_out "says OVER BUDGET" 'OVER BUDGET'
chk_out "prints the deletion count" 'deleted +60 files'
chk_out "names the top directory" 'docs/trees'
chk_out "names the rule that fired" 'max-deleted-files'

echo "-- 2. DELETIONS ARE NOT EDITS: 60 modifications must not trip --"
restore
i=0
while [ $i -lt 60 ]; do
  printf '<svg id="edited"/>\n' >"$REPO/docs/trees/t$i.svg"
  i=$((i + 1))
done
git_q add -A
chk "60 modifications -> exit 0" 0 "$(run)"
chk_out "and they are counted as modified, not deleted" 'modified +60 files'
chk_out "with the deleted bucket at zero" 'deleted +0 files'

echo "-- 3. The friction floor: ordinary work must stay silent --"
restore
del_trees 1
chk "1 deletion -> exit 0" 0 "$(run)"

echo "-- 4. A whole directory wiped UNDER the absolute count --"
restore
i=0
while [ $i -lt 12 ]; do
  rm -f "$REPO/src/s$i.txt"
  i=$((i + 1))
done
git_q add -A
chk "12 deletions = 100% of src/ -> exit 2" 2 "$(run)"
chk_out "and the dir-fraction rule is what names it" 'dir-fraction +src'

echo "-- 5. --json is machine-readable and carries the same verdict --"
restore
del_trees 60
chk "json run still exits 2" 2 "$(run --json)"
"$PY" -c 'import json,sys
d = json.load(open(sys.argv[1]))
ok = (d["verdict"] == "over-budget" and d["exit_code"] == 2
      and d["counts"]["deleted"] == 60 and d["counts"]["modified"] == 0
      and any(b["rule"] == "max-deleted-files" for b in d["breaches"]))
sys.exit(0 if ok else 1)' "$OUT"
chk "json parses with deleted=60 and the breach named" 0 "$?"

echo "-- 6. The printed override must be COMPLETE, not just plausible --"
# The two rules are independent: 60 deletions breaches the absolute count AND
# wipes 60% of docs/trees. Raising one bound alone leaves the stop in place, so
# a hint naming one flag would send the reader into a re-run loop. Assert the
# hint names both AND that following it verbatim actually clears the commit.
chk "raising only the file count still stops (dir-fraction holds)" \
  2 "$(run --max-deleted-files 900)"
"$PY" "$GUARD" --repo "$REPO" --json >"$OUT" 2>"$ERR"
HINT="$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["override_hint"])' "$OUT")"
case "$HINT" in
  *--max-deleted-files*--max-dir-fraction*)
    echo "  OK   the hint names both breached bounds"
    pass=$((pass + 1))
    ;;
  *)
    echo "  FAIL the hint is incomplete: $HINT"
    fail=$((fail + 1))
    ;;
esac
# shellcheck disable=SC2086  # deliberate word-splitting: the hint IS a flag list
chk "following the printed hint verbatim clears it" 0 "$(run $HINT)"

echo "-- 7. COULD-NOT-RUN is never reported as clean --"
mkdir -p "$T/not-a-repo"
"$PY" "$GUARD" --repo "$T/not-a-repo" >"$OUT" 2>"$ERR"
chk "outside a repo -> exit 1, not 0 and not 2" 1 "$?"
if grep -Fq "NOT a clean result" "$ERR"; then
  echo "  OK   and it says so out loud"
  pass=$((pass + 1))
else
  echo "  FAIL a blind run did not announce itself"
  fail=$((fail + 1))
fi

mkdir -p "$T/nobin"
env PATH="$T/nobin" "$PY" "$GUARD" --repo "$REPO" >"$OUT" 2>"$ERR"
chk "git absent from PATH -> exit 1" 1 "$?"

echo "-- 8. The guard's own fixtures and its teeth --"
"$PY" "$GUARD" --self-test >"$OUT" 2>"$ERR"
chk "--self-test passes" 0 "$?"
"$PY" "$GUARD" --must-fail >"$OUT" 2>"$ERR"
chk "--must-fail proves the deletion rule is load-bearing" 0 "$?"
if grep -Fq "TEETH PROVEN" "$OUT"; then
  echo "  OK   the mutant MISSED the known-bad case"
  pass=$((pass + 1))
else
  echo "  FAIL the neutered check still caught it — the teeth are elsewhere"
  fail=$((fail + 1))
fi

echo
echo "  $pass passed, $fail failed"
rm -rf "$T"
[ "$fail" -eq 0 ] || exit 1
