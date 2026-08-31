#!/usr/bin/env bash
# Gate 199 (execution half) — every PreToolUse enforcement hook must fail CLOSED.
#
# THE CONTRACT. The harness treats a hook exit of 2 as a BLOCK and any other
# non-zero as a non-blocking error — so a hook that errors with exit 1 does not
# fail safe, it fails OPEN: the tool call proceeds and nothing is reported. The
# only two honest outcomes on a malformed or unexpected input are therefore:
#
#     exit 0  — deliberate safe no-op (this input is not mine to judge)
#     exit 2  — deliberate deny
#
# Anything else (1, 127, 126, a signal) is a finding. 127 in particular is the
# stock-macOS shape: an absent command under `set -e`.
#
# WHY A STATIC CHECK CANNOT DO THIS. The constructs that produce these exits are
# syntactically valid and fail only at RUNTIME, on conditional paths, under a
# specific toolchain. `bash -n` sees none of it. This runner EXECUTES each hook
# against inputs it was never written for, which is the only way the class is
# observable.
#
# CONTAINMENT — this drives real guardrails, so it must not let one do real work:
#   * `env -i PATH=/usr/bin:/bin` — the stock-toolchain floor, and it strips every
#     CLAUDE_* variable so a hook cannot find the real project.
#   * CLAUDE_PROJECT_DIR is pointed at a throwaway temp dir with no posture file,
#     so the opt-in-by-posture hooks no-op and nothing writes to the real repo.
#   * every invocation is time-bounded (a hook that hangs is its own finding, and
#     an unbounded runner would hang CI).
#
# Exit codes: 0 = every hook fails closed; 2 = a finding, or the enumeration
# could not be read. Exit 1 is never used — it is the very shape under audit.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
HOOKS_JSON="$REPO/plugins/ravenclaude-core/hooks/hooks.json"

# The portable bounded-run shim. GNU `timeout` is absent on a stock macOS
# toolchain, so calling it directly would make THIS script an instance of the
# class it audits.
# shellcheck source=/dev/null
. "$REPO/plugins/ravenclaude-core/hooks/_portable.sh" 2>/dev/null || {
  _rc_timeout() { shift; "$@"; }   # last-resort stub: unbounded beats not-running
}

SELF_TEST=0
[ "${1:-}" = "--self-test" ] && SELF_TEST=1

PASS=0; FAIL=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/proj"

ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; }

# ── The inputs a hook was never written for ─────────────────────────────────
# Named so a finding says WHICH shape broke it.
_payload() {
  case "$1" in
    empty)      printf '' ;;
    malformed)  printf '{"tool_name": "Bash", ' ;;
    empty-obj)  printf '{}' ;;
    null-input) printf '{"tool_name": null, "tool_input": null}' ;;
    wrong-type) printf '{"tool_name": ["Bash"], "tool_input": "not-an-object"}' ;;
    no-tool)    printf '{"tool_input": {"command": "true"}}' ;;
    deep-null)  printf '{"tool_name": "Write", "tool_input": {"file_path": null, "content": null}}' ;;
  esac
}
SHAPES="empty malformed empty-obj null-input wrong-type no-tool deep-null"

# ── Enumerate the PreToolUse hooks. This is THIS script's own read of
# hooks.json — the keystone gate parses audit-gates.sh, never hooks.json.
_enumerate() {
  python3 - "$1" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as exc:
    print("ENUM-ERROR " + str(exc)); sys.exit(0)
hooks = d.get("hooks", d)
pre = hooks.get("PreToolUse") or []
if not pre:
    print("ENUM-ERROR no PreToolUse hooks declared"); sys.exit(0)
for blk in pre:
    for h in blk.get("hooks", []):
        cmd = h.get("command", "")
        if cmd:
            print(cmd)
PY
}

_drive() { # script args... ; reads payload on stdin; echoes exit code
  local rc=0
  # ⛔ ORDER IS LOAD-BEARING: the bound goes OUTSIDE `env -i`, never inside.
  # `_rc_timeout` is a shell FUNCTION, and `env` can only exec a binary — putting
  # it inside yields exit 127 for every hook, which reads as "all 11 fail open"
  # and is really "the probe never ran". A uniform result across an entire
  # population is a claim about the instrument until proven otherwise.
  _rc_timeout 20 env -i PATH=/usr/bin:/bin HOME="$TMP" \
      CLAUDE_PROJECT_DIR="$TMP/proj" CLAUDE_SESSION_ID=failclosed-audit \
      bash "$@" >/dev/null 2>&1 || rc=$?
  printf '%s' "$rc"
}

_audit_one() { # label script args...
  local label="$1"; shift
  local shape rc bad_shapes=""
  for shape in $SHAPES; do
    rc="$(_payload "$shape" | _drive "$@")"
    case "$rc" in
      0|2) : ;;
      *) bad_shapes="$bad_shapes $shape:exit$rc" ;;
    esac
  done
  if [ -z "$bad_shapes" ]; then
    ok "$label fails closed on all 7 shapes (exit 0 or 2 only)"
  else
    bad "$label FAILS OPEN —$bad_shapes (only 0 or 2 are honest; 1 is non-blocking)"
  fi
}

echo "── hook fail-closed audit (stock toolchain, env -i) ──"

listing="$(_enumerate "$HOOKS_JSON")"
case "$listing" in
  ENUM-ERROR*)
    echo "  FAIL-CLOSED: cannot enumerate PreToolUse hooks — ${listing#ENUM-ERROR }" >&2
    exit 2 ;;
esac

n=0
printf '%s\n' "$listing" | while IFS= read -r cmd; do
  [ -n "$cmd" ] || continue
  # Split the declared command into script + its literal args. Interpolations
  # ($CLAUDE_*, ${CLAUDE_PLUGIN_ROOT}) resolve to nothing under env -i, which is
  # exactly the empty-arg case the hooks must already survive.
  set -- $cmd
  script="$1"; shift
  script="$(printf '%s' "$script" | sed 's|\${CLAUDE_PLUGIN_ROOT}|'"$REPO/plugins/ravenclaude-core"'|; s|\$CLAUDE_PLUGIN_ROOT|'"$REPO/plugins/ravenclaude-core"'|')"
  [ -f "$script" ] || continue
  _audit_one "$(basename "$script")" "$script" "$@"
done > "$TMP/results"
cat "$TMP/results"
# `grep -c` exits 1 on a zero count, so an `|| echo 0` fallback would append a
# SECOND value and break the arithmetic. Take the count and normalise instead.
PASS="$(grep -c '^  ok ' "$TMP/results" 2>/dev/null)" || PASS=0
FAIL="$(grep -c '^  FAIL ' "$TMP/results" 2>/dev/null)" || FAIL=0
n="$((PASS + FAIL))"

if [ "$n" -eq 0 ]; then
  echo "  FAIL-CLOSED: zero hooks were driven — the audit measured nothing" >&2
  exit 2
fi

# ── TEETH ───────────────────────────────────────────────────────────────────
# A runner that never fails is indistinguishable from one that never runs. Plant
# a hook that errors with exit 1 (the fail-open shape) and require it be caught.
if [ "$SELF_TEST" -eq 1 ]; then
  echo
  echo "── teeth ──"
  mut="$TMP/fail-open-hook.sh"
  printf '#!/usr/bin/env bash\nset -euo pipefail\ncat >/dev/null 2>&1 || true\nexit 1\n' > "$mut"
  saw=""
  for shape in $SHAPES; do
    rc="$(_payload "$shape" | _drive "$mut")"
    case "$rc" in 0|2) : ;; *) saw="yes" ;; esac
  done
  if [ -n "$saw" ]; then
    ok "teeth: a hook that exits 1 on error IS detected as fail-open"
  else
    bad "teeth: the exit-1 fail-open mutant was NOT detected — this runner has no teeth"
    FAIL=$((FAIL + 1))
  fi

  # And the inverse: a correct hook must NOT be flagged, or the audit floods.
  clean="$TMP/clean-hook.sh"
  printf '#!/usr/bin/env bash\nset -uo pipefail\ncat >/dev/null 2>&1 || true\nexit 0\n' > "$clean"
  flagged=""
  for shape in $SHAPES; do
    rc="$(_payload "$shape" | _drive "$clean")"
    case "$rc" in 0|2) : ;; *) flagged="yes" ;; esac
  done
  if [ -z "$flagged" ]; then
    ok "teeth: a correct safe-no-op hook is NOT flagged (no flood)"
  else
    bad "teeth: a correct hook was flagged — the audit would flood"
    FAIL=$((FAIL + 1))
  fi
fi

echo
printf '  %d hook(s) audited, %d finding(s)\n' "$n" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 2
exit 0
