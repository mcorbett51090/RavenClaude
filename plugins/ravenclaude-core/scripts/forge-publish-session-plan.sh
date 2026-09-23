#!/usr/bin/env bash
# forge-publish-session-plan.sh — copy FORGE plan.md to the host session plan file.
#
# Grok's exit_plan_mode reads ~/.grok/sessions/<encoded-cwd>/<session-id>/plan.md
# (user-guide 19-plan-mode.md). The FORGE run-dir plan.md is a different file.
# Calling ExitPlanMode without this copy opens "No plan written yet".
#
# Security (forge-harden 0.323.8 / AppSec F1+F2):
#   - --plan must be a regular file under .ravenclaude/runs/forge/<slug>/
#   - dest (and --session-dir) must realpath-jail under $GROK_HOME/sessions/
#   - refuse symlink dest/source; never follow symlinks on copy (O_NOFOLLOW)
#   - TOCTOU: one resolve+recheck; require GROK_SESSION_ID if >1 session match
#
# bash 3.2-safe. Exit 0 on publish or honest skip (not a Grok session tree).
# Exit 2 if the source is empty, jail refuse, or the dest is empty after copy.
#
# --self-test runs built-in fixtures (nonzero on failure).
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
    --plan)
      if [ $# -lt 2 ]; then
        echo "forge-publish-session-plan: --plan requires a value" >&2
        usage
        exit 2
      fi
      plan="$2"; shift 2 ;;
    --session-dir)
      if [ $# -lt 2 ]; then
        echo "forge-publish-session-plan: --session-dir requires a value" >&2
        usage
        exit 2
      fi
      session_dir="$2"; shift 2 ;;
    --cwd)
      if [ $# -lt 2 ]; then
        echo "forge-publish-session-plan: --cwd requires a value" >&2
        usage
        exit 2
      fi
      cwd="$2"; shift 2 ;;
    --self-test|self-test) SELF_TEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "forge-publish-session-plan: unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

# --- path jail helpers (python3; this repo requires it) ----------------------

_realpath() {
  python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$1" 2>/dev/null
}

# Exit 0 if $1 realpath is under $2 realpath (inclusive).
_under_root() {
  python3 -c '
import os, sys
p = os.path.realpath(sys.argv[1])
r = os.path.realpath(sys.argv[2])
sys.exit(0 if (p == r or p.startswith(r + os.sep)) else 1)
' "$1" "$2"
}

# Exit 0 if plan is a regular non-symlink file under .ravenclaude/runs/forge/<slug>/.
_plan_jail_ok() {
  python3 -c '
import os, re, stat, sys
path = sys.argv[1]
if os.path.islink(path):
    sys.exit(1)
try:
    st = os.lstat(path)
except OSError:
    sys.exit(1)
if not stat.S_ISREG(st.st_mode):
    sys.exit(1)
rp = os.path.realpath(path)
parts = rp.split(os.sep)
try:
    i = parts.index(".ravenclaude")
except ValueError:
    sys.exit(1)
if parts[i : i + 3] != [".ravenclaude", "runs", "forge"]:
    sys.exit(1)
if i + 4 >= len(parts):
    sys.exit(1)
slug = parts[i + 3]
if not re.match(r"^[a-z0-9][a-z0-9-]{1,60}$", slug):
    sys.exit(1)
sys.exit(0)
' "$1"
}

# Copy src→dst without following a symlink dest (O_NOFOLLOW when available).
_safe_copy() {
  python3 -c '
import os, stat, sys
src, dst = sys.argv[1], sys.argv[2]
if os.path.islink(src):
    sys.stderr.write("forge-publish-session-plan: source is a symlink (refused)\n")
    sys.exit(2)
try:
    st = os.lstat(src)
except OSError as e:
    sys.stderr.write("forge-publish-session-plan: source unreadable: %s\n" % e)
    sys.exit(2)
if not stat.S_ISREG(st.st_mode):
    sys.stderr.write("forge-publish-session-plan: source is not a regular file\n")
    sys.exit(2)
if os.path.lexists(dst):
    st2 = os.lstat(dst)
    if stat.S_ISLNK(st2.st_mode):
        sys.stderr.write("forge-publish-session-plan: dest is a symlink (refused): %s\n" % dst)
        sys.exit(2)
    if not stat.S_ISREG(st2.st_mode):
        sys.stderr.write("forge-publish-session-plan: dest exists and is not a file: %s\n" % dst)
        sys.exit(2)
flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
if hasattr(os, "O_NOFOLLOW"):
    flags |= os.O_NOFOLLOW
try:
    fd = os.open(dst, flags, 0o644)
except OSError as e:
    sys.stderr.write("forge-publish-session-plan: open dest failed: %s\n" % e)
    sys.exit(2)
try:
    with open(src, "rb") as fh:
        data = fh.read()
    if not data:
        sys.stderr.write("forge-publish-session-plan: source empty\n")
        sys.exit(2)
    os.write(fd, data)
finally:
    os.close(fd)
' "$1" "$2"
}

_sessions_root() {
  local gh="${GROK_HOME:-$HOME/.grok}"
  printf '%s\n' "$gh/sessions"
}

# --- self-test --------------------------------------------------------------

st_fail() { echo "SELF-TEST FAIL: $1" >&2; ST_RC=1; }

_plant_plan() {
  # $1=scratch $2=slug → prints plan path
  local root="$1" slug="$2"
  local d="${root}/.ravenclaude/runs/forge/${slug}"
  mkdir -p "$d"
  printf '# plan\nbody\n' > "${d}/plan.md"
  printf '%s\n' "${d}/plan.md"
}

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
  src="$(_plant_plan "$scratch" "demo-slug")"

  # Fixture 1: non-empty source publishes under jailed session dir.
  (
    gh="${scratch}/grok1"
    dest_dir="${gh}/sessions/enc1/sessA"
    mkdir -p "$dest_dir"
    out="$(GROK_HOME="$gh" bash "$script_abs" --plan "$src" --session-dir "$dest_dir" 2>&1)" || exit 21
    printf '%s' "$out" | grep -q '^FORGE_SESSION_PLAN ' || exit 22
    [ -s "${dest_dir}/plan.md" ] || exit 23
    src_b="$(wc -c < "$src" | tr -d ' ')"
    dst_b="$(wc -c < "${dest_dir}/plan.md" | tr -d ' ')"
    [ "$src_b" = "$dst_b" ] || exit 24
    printf '%s' "$out" | grep -q " ${dst_b}\$" || exit 25
  ) || st_fail "non-empty source did not publish cleanly ($?)"

  # Fixture 2: EMPTY source refused exit 2.
  (
    empty_dir="${scratch}/.ravenclaude/runs/forge/empty-slug"
    mkdir -p "$empty_dir"
    : > "${empty_dir}/plan.md"
    gh="${scratch}/grok2"
    dest_dir="${gh}/sessions/enc2/sessB"
    mkdir -p "$dest_dir"
    bash "$script_abs" --plan "${empty_dir}/plan.md" --session-dir "$dest_dir" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 26
    [ -e "${dest_dir}/plan.md" ] && exit 27
    exit 0
  ) || st_fail "empty source was not refused with exit 2 ($?)"

  # Fixture 3: MISSING source refused.
  (
    gh="${scratch}/grok3"
    dest_dir="${gh}/sessions/enc3/sessC"
    mkdir -p "$dest_dir"
    bash "$script_abs" --plan "${scratch}/.ravenclaude/runs/forge/demo-slug/nope.md" --session-dir "$dest_dir" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 28
    exit 0
  ) || st_fail "missing source was not refused with exit 2 ($?)"

  # Fixture 4: --plan omitted → exit 2.
  (
    bash "$script_abs" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 29
    exit 0
  ) || st_fail "missing --plan was not refused with exit 2 ($?)"

  # Fixture 5: honest skip — no Grok session group.
  (
    nowhere="${scratch}/nowhere"
    mkdir -p "$nowhere"
    out="$(GROK_HOME="${scratch}/no-grok-home" bash "$script_abs" --plan "$src" --cwd "$nowhere" 2>&1)" || exit 30
    printf '%s' "$out" | grep -q 'skip (no Grok session group' || exit 31
  ) || st_fail "honest skip path broke ($?)"

  # Fixture 6: empty session group → skip.
  (
    proj="${scratch}/proj6"
    mkdir -p "$proj"
    gh="${scratch}/grok6"
    enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$proj")"
    mkdir -p "${gh}/sessions/${enc}"
    out="$(GROK_HOME="$gh" bash "$script_abs" --plan "$src" --cwd "$proj" 2>&1)" || exit 32
    printf '%s' "$out" | grep -q 'skip (no session dir under' || exit 33
  ) || st_fail "empty session group did not skip honestly ($?)"

  # Fixture 7: resolved single session dir publishes.
  (
    proj="${scratch}/proj7"
    mkdir -p "$proj"
    gh="${scratch}/grok7"
    enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$proj")"
    mkdir -p "${gh}/sessions/${enc}/abc123"
    out="$(GROK_HOME="$gh" bash "$script_abs" --plan "$src" --cwd "$proj" 2>&1)" || exit 34
    printf '%s' "$out" | grep -q '^FORGE_SESSION_PLAN ' || exit 35
    [ -s "${gh}/sessions/${enc}/abc123/plan.md" ] || exit 36
  ) || st_fail "session-dir resolution did not publish ($?)"

  # Fixture 8 (F1): symlink dest refused.
  (
    gh="${scratch}/grok8"
    dest_dir="${gh}/sessions/enc8/sessD"
    mkdir -p "$dest_dir" "${scratch}/outside8"
    printf 'SECRET\n' > "${scratch}/outside8/target"
    ln -s "${scratch}/outside8/target" "${dest_dir}/plan.md"
    bash "$script_abs" --plan "$src" --session-dir "$dest_dir" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 37
    # target must be untouched
    grep -qx 'SECRET' "${scratch}/outside8/target" || exit 38
    exit 0
  ) || st_fail "symlink dest was not refused ($?)"

  # Fixture 9 (F2): --plan outside forge run-dir jail refused.
  (
    gh="${scratch}/grok9"
    dest_dir="${gh}/sessions/enc9/sessE"
    mkdir -p "$dest_dir"
    printf 'leak\n' > "${scratch}/outside-plan.md"
    bash "$script_abs" --plan "${scratch}/outside-plan.md" --session-dir "$dest_dir" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 39
    [ -e "${dest_dir}/plan.md" ] && exit 40
    exit 0
  ) || st_fail "unjailed --plan was not refused ($?)"

  # Fixture 10 (F2): --session-dir outside GROK_HOME/sessions refused.
  (
    bad="${scratch}/not-sessions/sess"
    mkdir -p "$bad"
    GROK_HOME="${scratch}/grok10" bash "$script_abs" --plan "$src" --session-dir "$bad" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 41
    exit 0
  ) || st_fail "unjailed --session-dir was not refused ($?)"

  # Fixture 11 (TOCTOU): >1 session without GROK_SESSION_ID → refuse.
  (
    proj="${scratch}/proj11"
    mkdir -p "$proj"
    gh="${scratch}/grok11"
    enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$proj")"
    mkdir -p "${gh}/sessions/${enc}/old" "${gh}/sessions/${enc}/new"
    bash -c "GROK_HOME='$gh' env -u GROK_SESSION_ID bash '$script_abs' --plan '$src' --cwd '$proj'" >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 2 ] || exit 42
    exit 0
  ) || st_fail ">1 session without GROK_SESSION_ID was not refused ($?)"

  # Fixture 12: GROK_SESSION_ID disambiguates when >1.
  (
    proj="${scratch}/proj12"
    mkdir -p "$proj"
    gh="${scratch}/grok12"
    enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$proj")"
    mkdir -p "${gh}/sessions/${enc}/sid-old" "${gh}/sessions/${enc}/sid-new"
    out="$(GROK_HOME="$gh" GROK_SESSION_ID=sid-old bash "$script_abs" --plan "$src" --cwd "$proj" 2>&1)" || exit 43
    printf '%s' "$out" | grep -q '^FORGE_SESSION_PLAN ' || exit 44
    [ -s "${gh}/sessions/${enc}/sid-old/plan.md" ] || exit 45
    [ ! -f "${gh}/sessions/${enc}/sid-new/plan.md" ] || exit 46
  ) || st_fail "GROK_SESSION_ID did not disambiguate ($?)"

  if [ "$ST_RC" -eq 0 ]; then
    echo "SELF-TEST PASS: forge-publish-session-plan.sh (12 fixtures)"
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

# F2: plan jail + regular-file / no-symlink
if ! _plan_jail_ok "$plan"; then
  echo "forge-publish-session-plan: --plan must be a regular file under .ravenclaude/runs/forge/<slug>/ (no symlinks): $plan" >&2
  exit 2
fi
if [ ! -s "$plan" ]; then
  echo "forge-publish-session-plan: source missing or empty: $plan" >&2
  exit 2
fi

if [ -z "$cwd" ]; then
  cwd="$(pwd)"
fi

grok_home="${GROK_HOME:-$HOME/.grok}"
sessions_root="$grok_home/sessions"

if [ -z "$session_dir" ]; then
  enc="$(python3 -c 'import sys; from pathlib import Path; from urllib.parse import quote; print(quote(str(Path(sys.argv[1]).resolve()), safe=""))' "$cwd")"
  group="$grok_home/sessions/$enc"
  if [ ! -d "$group" ]; then
    echo "forge-publish-session-plan: skip (no Grok session group at $group)"
    exit 0
  fi
  if [ -n "${GROK_SESSION_ID:-}" ] && [ -d "$group/$GROK_SESSION_ID" ]; then
    session_dir="$group/$GROK_SESSION_ID"
  else
    # Count session dirs; require GROK_SESSION_ID when ambiguous (AppEng TOCTOU).
    _n=0
    _pick=""
    for _d in "$group"/*/; do
      [ -d "$_d" ] || continue
      _n=$((_n + 1))
      _pick="${_d%/}"
    done
    if [ "$_n" -eq 0 ]; then
      echo "forge-publish-session-plan: skip (no session dir under $group)"
      exit 0
    fi
    if [ "$_n" -gt 1 ]; then
      echo "forge-publish-session-plan: multiple session dirs under $group; set GROK_SESSION_ID" >&2
      exit 2
    fi
    session_dir="$_pick"
  fi
  if [ -z "$session_dir" ] || [ ! -d "$session_dir" ]; then
    echo "forge-publish-session-plan: skip (no session dir under $group)"
    exit 0
  fi
fi

# F1/F2: session-dir + dest jail under GROK_HOME/sessions/
if ! _under_root "$session_dir" "$sessions_root"; then
  echo "forge-publish-session-plan: --session-dir must be under $sessions_root (realpath jail): $session_dir" >&2
  exit 2
fi

# TOCTOU recheck: session dir still a directory under jail.
session_dir="$(_realpath "$session_dir")"
if [ -z "$session_dir" ] || [ ! -d "$session_dir" ]; then
  echo "forge-publish-session-plan: session-dir vanished or not a directory" >&2
  exit 2
fi
if ! _under_root "$session_dir" "$sessions_root"; then
  echo "forge-publish-session-plan: session-dir escaped jail after resolve" >&2
  exit 2
fi

dest="$session_dir/plan.md"
if [ -L "$dest" ]; then
  echo "forge-publish-session-plan: dest is a symlink (refused): $dest" >&2
  exit 2
fi
if [ -e "$dest" ] && [ ! -f "$dest" ]; then
  echo "forge-publish-session-plan: dest exists and is not a file: $dest" >&2
  exit 2
fi

# Dest parent must remain under sessions jail (no symlink parent escape).
dest_parent="$(dirname "$dest")"
if ! _under_root "$dest_parent" "$sessions_root"; then
  echo "forge-publish-session-plan: dest parent outside sessions jail" >&2
  exit 2
fi

_safe_copy "$plan" "$dest" || {
  echo "forge-publish-session-plan: copy failed → $dest" >&2
  exit 2
}
if [ -L "$dest" ]; then
  echo "forge-publish-session-plan: dest became a symlink after copy (refused): $dest" >&2
  exit 2
fi
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
