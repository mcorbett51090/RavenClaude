#!/usr/bin/env bash
# forge-publish-session-plan.sh — copy FORGE plan.md to the host session plan file.
#
# Grok's exit_plan_mode reads ~/.grok/sessions/<encoded-cwd>/<session-id>/plan.md
# (user-guide 19-plan-mode.md). The FORGE run-dir plan.md is a different file.
# Calling ExitPlanMode without this copy opens "No plan written yet".
#
# bash 3.2-safe. Exit 0 on publish or honest skip (not a Grok session tree).
# Exit 2 if the source is empty or the dest is empty after copy.
#
# --self-test runs built-in fixtures (nonzero on failure). It exists because this
# script GATES the mandatory pre-ExitPlanMode publish step with exit-2 semantics
# and shipped with no test at all — an ungated gate. Registered in
# scripts/audit-gates.sh alongside forge-receipt.py and forge-worktree.sh.
set -uo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: forge-publish-session-plan.sh --plan PATH [--session-dir DIR] [--cwd DIR]
       forge-publish-session-plan.sh --self-test
EOF
}

plan=""
session_dir=""
cwd=""

while [ $# -gt 0 ]; do
  case "$1" in
    --plan) plan="${2:-}"; shift 2 ;;
    --session-dir) session_dir="${2:-}"; shift 2 ;;
    --cwd) cwd="${2:-}"; shift 2 ;;
    --self-test|self-test) SELF_TEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "forge-publish-session-plan: unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

# --- self-test --------------------------------------------------------------
# Fixture style mirrors forge-worktree.sh's scratch-fixture idiom, minus git —
# these fixtures are just plan.md files and a fake session tree.

st_fail() { echo "SELF-TEST FAIL: $1" >&2; ST_RC=1; }

self_test() {
  ST_RC=0
  scratch="$(mktemp -d 2>/dev/null || echo '')"
  if [ -z "$scratch" ]; then
    echo "SELF-TEST FAIL: mktemp unavailable" >&2
    return 1
  fi
  # shellcheck disable=SC2064
  trap "rm -rf '$scratch'" EXIT

  script_abs="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

  # Fixture 1: a non-empty source publishes and prints FORGE_SESSION_PLAN.
  (
    src="${scratch}/plan.md"
    printf '# plan\nbody\n' > "$src"
    dest_dir="${scratch}/sess1"
    mkdir -p "$dest_dir"
    out="$(bash "$script_abs" --plan "$src" --session-dir "$dest_dir" 2>&1)" || exit 21
    printf '%s' "$out" | grep -q '^FORGE_SESSION_PLAN ' || exit 22
    [ -s "${dest_dir}/plan.md" ] || exit 23
    # The published bytes must be the SOURCE's bytes, not a truncated/empty file —
    # a publish step that reports success over a wrong-sized copy is the defect
    # the size check downstream exists to catch, so assert it here too.
    src_b="$(wc -c < "$src" | tr -d ' ')"
    dst_b="$(wc -c < "${dest_dir}/plan.md" | tr -d ' ')"
    [ "$src_b" = "$dst_b" ] || exit 24
    printf '%s' "$out" | grep -q " ${dst_b}\$" || exit 25
  ) || st_fail "non-empty source did not publish cleanly ($?)"

  # Fixture 2: an EMPTY source is refused with exit 2 (the documented contract).
  # ⛔ This is the load-bearing half. An empty plan.md that published "successfully"
  # would open ExitPlanMode on "No plan written yet" — the exact failure this
  # script exists to prevent — so the refusal must be exit 2, never 0.
  (
    src="${scratch}/empty.md"
    : > "$src"
    dest_dir="${scratch}/sess2"
    mkdir -p "$dest_dir"
    bash "$script_abs" --plan "$src" --session-dir "$dest_dir" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 26
    [ -e "${dest_dir}/plan.md" ] && exit 27
    exit 0
  ) || st_fail "empty source was not refused with exit 2 ($?)"

  # Fixture 3: a MISSING source is the same refusal.
  (
    dest_dir="${scratch}/sess3"
    mkdir -p "$dest_dir"
    bash "$script_abs" --plan "${scratch}/does-not-exist.md" --session-dir "$dest_dir" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 28
    exit 0
  ) || st_fail "missing source was not refused with exit 2 ($?)"

  # Fixture 4: --plan omitted entirely is refused with exit 2.
  (
    bash "$script_abs" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 29
    exit 0
  ) || st_fail "missing --plan was not refused with exit 2 ($?)"

  # Fixture 5: the HONEST SKIP path — no Grok session group for this cwd.
  # Exit 0 (a FORGE run on a non-Grok host must not be blocked) but the message
  # must say `skip`, so "published" and "there was nowhere to publish" are never
  # the same observation.
  (
    src="${scratch}/plan.md"
    nowhere="${scratch}/nowhere"
    mkdir -p "$nowhere"
    out="$(GROK_HOME="${scratch}/no-grok-home" bash "$script_abs" --plan "$src" --cwd "$nowhere" 2>&1)" || exit 30
    printf '%s' "$out" | grep -q 'skip (no Grok session group' || exit 31
  ) || st_fail "honest skip path broke ($?)"

  # Fixture 6: a Grok session GROUP exists but holds no session dir ⇒ still an
  # honest skip at exit 0, with the second, distinct skip message.
  (
    src="${scratch}/plan.md"
    proj="${scratch}/proj6"
    mkdir -p "$proj"
    gh="${scratch}/grok6"
    enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$proj")"
    mkdir -p "${gh}/sessions/${enc}"
    out="$(GROK_HOME="$gh" bash "$script_abs" --plan "$src" --cwd "$proj" 2>&1)" || exit 32
    printf '%s' "$out" | grep -q 'skip (no session dir under' || exit 33
  ) || st_fail "empty session group did not skip honestly ($?)"

  # Fixture 7: the resolved-session-dir path — a real group with a real session
  # dir publishes there without --session-dir being passed.
  (
    src="${scratch}/plan.md"
    proj="${scratch}/proj7"
    mkdir -p "$proj"
    gh="${scratch}/grok7"
    enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$proj")"
    mkdir -p "${gh}/sessions/${enc}/abc123"
    out="$(GROK_HOME="$gh" bash "$script_abs" --plan "$src" --cwd "$proj" 2>&1)" || exit 34
    printf '%s' "$out" | grep -q '^FORGE_SESSION_PLAN ' || exit 35
    [ -s "${gh}/sessions/${enc}/abc123/plan.md" ] || exit 36
  ) || st_fail "session-dir resolution did not publish ($?)"

  if [ "$ST_RC" -eq 0 ]; then
    echo "SELF-TEST PASS: forge-publish-session-plan.sh (7 fixtures)"
  fi
  return "$ST_RC"
}

if [ "${SELF_TEST:-0}" = "1" ]; then
  self_test
  exit $?
fi

if [ -z "$plan" ]; then
  echo "forge-publish-session-plan: --plan is required" >&2
  exit 2
fi
if [ ! -s "$plan" ]; then
  echo "forge-publish-session-plan: source missing or empty: $plan" >&2
  exit 2
fi

if [ -z "$cwd" ]; then
  cwd="$(pwd)"
fi

if [ -z "$session_dir" ]; then
  grok_home="${GROK_HOME:-$HOME/.grok}"
  enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$cwd")"
  group="$grok_home/sessions/$enc"
  if [ ! -d "$group" ]; then
    echo "forge-publish-session-plan: skip (no Grok session group at $group)"
    exit 0
  fi
  if [ -n "${GROK_SESSION_ID:-}" ] && [ -d "$group/$GROK_SESSION_ID" ]; then
    session_dir="$group/$GROK_SESSION_ID"
  else
    # Newest session directory for this cwd (mtime). Agent env usually lacks GROK_SESSION_ID.
    session_dir="$(ls -1td "$group"/*/ 2>/dev/null | head -1 | sed 's:/*$::')"
  fi
  if [ -z "$session_dir" ] || [ ! -d "$session_dir" ]; then
    echo "forge-publish-session-plan: skip (no session dir under $group)"
    exit 0
  fi
fi

dest="$session_dir/plan.md"
if [ -e "$dest" ] && [ ! -f "$dest" ]; then
  echo "forge-publish-session-plan: dest exists and is not a file: $dest" >&2
  exit 2
fi
cp "$plan" "$dest" || {
  echo "forge-publish-session-plan: copy failed → $dest" >&2
  exit 2
}
if [ ! -f "$dest" ] || [ ! -s "$dest" ]; then
  echo "forge-publish-session-plan: dest empty after copy: $dest" >&2
  exit 2
fi
src_bytes="$(wc -c < "$plan" | tr -d ' ')"
dst_bytes="$(wc -c < "$dest" | tr -d ' ')"
if [ "$src_bytes" != "$dst_bytes" ]; then
  echo "forge-publish-session-plan: size mismatch src=$src_bytes dest=$dst_bytes" >&2
  exit 2
fi
echo "FORGE_SESSION_PLAN $dest $dst_bytes"
exit 0
