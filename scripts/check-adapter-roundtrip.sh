#!/usr/bin/env bash
# check-adapter-roundtrip.sh — Gate 208 (P17 adapter payload loss)
#
# Deny + reason must survive translation on every host whose host-support.json
# `hooks.how` names an adapter / env shim. Generalizes Gate 167 (Copilot deny
# still fires) and Gate 164 (Gemini reason on stderr) into one per-adapter
# round-trip, closing the v0.250.0 "adapters kept the deny, threw away the
# reason" regression.
#
# Hosts and adapter paths are DERIVED from host-support.json (the `how` field
# of each supported hooks cell). There is no hand-typed host list. A new
# adapter basename the driver does not know is a fail-closed finding — add a
# driver in the same commit that names it in the map.
#
# M10 HONEST LIMIT: live-host behavior is un-exercisable in CI. This gates
# adapter I/O against a planted stub hook. A host binary that ignores a
# correctly-wired hooks file stays owner-verified.
#
# Exit 0 = pass. Exit 2 = a finding. Exit 1 is never used for a finding.
#
# Usage:
#   bash scripts/check-adapter-roundtrip.sh              # live adapters
#   bash scripts/check-adapter-roundtrip.sh --self-test  # good + mutant halves
#   bash scripts/check-adapter-roundtrip.sh --must-fail  # mutant halves only
#   bash scripts/check-adapter-roundtrip.sh --drive-mutant
#       # emit the reason-dropping mutant's exit (suite asserts it is 2)

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
CORE="$REPO/plugins/ravenclaude-core"
HOSTMAP="$CORE/knowledge/host-support.json"
HOOKS="$CORE/hooks"

PASS=0
FAIL=0
ok()  { PASS=$((PASS + 1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL + 1)); printf '  ✗ %s\n' "$1"; }
die2() { printf 'adapter-roundtrip: %s\n' "$1" >&2; exit 2; }

[ -f "$HOSTMAP" ] || die2 "missing $HOSTMAP"

# Unique adapter paths named by the map, one per line. Derived, not typed.
adapters_from_map() {
  python3 -c '
import json, re, sys
path = sys.argv[1]
try:
    data = json.loads(open(path, encoding="utf-8").read())
except Exception as exc:
    sys.stderr.write("unreadable host-support.json: %s\n" % exc)
    sys.exit(2)
hosts = data.get("hosts") or {}
hooks = (data.get("components") or {}).get("hooks") or {}
if not hosts:
    sys.stderr.write("no hosts declared\n")
    sys.exit(2)
seen = []
for host in hosts:
    cell = hooks.get(host) or {}
    if cell.get("supported") is not True:
        continue
    how = cell.get("how") or ""
    for m in re.findall(r"hooks/[A-Za-z0-9_.-]+\.sh", how):
        if m not in seen:
            seen.append(m)
            sys.stdout.write(m + "\n")
' "$HOSTMAP"
}

SENTINEL="DENY_REASON_SENTINEL: blocked because of a specific named rule"

# Stub guard: swallow stdin, print the sentinel on stderr, exit 2.
write_loud_stub() {
  local dest="$1"
  cat >"$dest" <<'STUB'
#!/usr/bin/env bash
cat >/dev/null
printf 'DENY_REASON_SENTINEL: blocked because of a specific named rule\n' >&2
exit 2
STUB
  chmod +x "$dest"
}

# Per-basename envelope. Keyed on the *adapter filename the map named*,
# never on a host identifier.
payload_for() {
  local base="$1" cwd="$2"
  case "$base" in
    copilot-hook-adapter.sh)
      python3 -c '
import json, sys
print(json.dumps({
    "toolName": "bash",
    "toolArgs": json.dumps({"command": "echo hi"}),
    "cwd": sys.argv[1],
    "sessionId": "g208",
}))
' "$cwd"
      ;;
    cursor-hook-adapter.sh)
      python3 -c '
import json, sys
print(json.dumps({
    "conversation_id": "g208",
    "hook_event_name": "beforeShellExecution",
    "workspace_roots": [sys.argv[1]],
    "command": "echo hi",
    "cwd": sys.argv[1],
    "sandbox": False,
}))
' "$cwd"
      ;;
    gemini-hook-adapter.sh)
      python3 -c '
import json, sys
print(json.dumps({
    "session_id": "g208",
    "cwd": sys.argv[1],
    "hook_event_name": "BeforeTool",
    "tool_name": "run_shell_command",
    "tool_input": {"command": "echo hi"},
}))
' "$cwd"
      ;;
    codex-hook-env.sh)
      python3 -c '
import json, sys
print(json.dumps({
    "tool_name": "Bash",
    "tool_input": {"command": "echo hi"},
    "cwd": sys.argv[1],
    "session_id": "g208",
}))
' "$cwd"
      ;;
    *)
      return 2
      ;;
  esac
}

invoke_adapter() {
  # stdin: payload. args: adapter_path basename stub
  # writes stdout/stderr/rc into $RC_OUT/{out,err,rc}
  local adapter="$1" base="$2" stub="$3"
  local rc=0
  case "$base" in
    copilot-hook-adapter.sh)
      bash "$adapter" bash-pretool "$stub" >"$RC_OUT/out" 2>"$RC_OUT/err" || rc=$?
      ;;
    cursor-hook-adapter.sh)
      bash "$adapter" shell-pretool "$stub" >"$RC_OUT/out" 2>"$RC_OUT/err" || rc=$?
      ;;
    gemini-hook-adapter.sh)
      bash "$adapter" pretool "$stub" >"$RC_OUT/out" 2>"$RC_OUT/err" || rc=$?
      ;;
    codex-hook-env.sh)
      bash "$adapter" "$stub" >"$RC_OUT/out" 2>"$RC_OUT/err" || rc=$?
      ;;
    *)
      return 2
      ;;
  esac
  printf '%s' "$rc" >"$RC_OUT/rc"
  return 0
}

# Reason channel per adapter contract (v0.250.0):
#   copilot — JSON permissionDecisionReason (stderr is captured into it)
#   gemini  — exit 2 + stderr (no JSON verdict)
#   cursor  — JSON permission=deny AND stderr (verdict is a fixed literal;
#             interpolating the reason would fail-open on malformed JSON)
#   codex   — exit 2 + stderr (passthrough; no envelope)
reason_survived() {
  local base="$1" out="$2" err="$3" rc="$4"
  case "$base" in
    copilot-hook-adapter.sh)
      python3 -c '
import json, sys
try:
    d = json.loads(open(sys.argv[1], encoding="utf-8").read() or "{}")
except Exception:
    sys.exit(1)
if d.get("permissionDecision") != "deny":
    sys.exit(1)
reason = d.get("permissionDecisionReason") or ""
sys.exit(0 if "DENY_REASON_SENTINEL" in reason else 1)
' "$out"
      ;;
    cursor-hook-adapter.sh)
      python3 -c '
import json, sys
try:
    d = json.loads(open(sys.argv[1], encoding="utf-8").read() or "{}")
except Exception:
    sys.exit(1)
sys.exit(0 if d.get("permission") == "deny" else 1)
' "$out" || return 1
      grep -q "DENY_REASON_SENTINEL" "$err"
      ;;
    gemini-hook-adapter.sh|codex-hook-env.sh)
      [ "$rc" -eq 2 ] || return 1
      grep -q "DENY_REASON_SENTINEL" "$err"
      ;;
    *)
      return 1
      ;;
  esac
}

deny_survived() {
  local base="$1" out="$2" rc="$3"
  case "$base" in
    copilot-hook-adapter.sh)
      python3 -c '
import json, sys
try:
    d = json.loads(open(sys.argv[1], encoding="utf-8").read() or "{}")
except Exception:
    sys.exit(1)
sys.exit(0 if d.get("permissionDecision") == "deny" else 1)
' "$out"
      ;;
    cursor-hook-adapter.sh)
      python3 -c '
import json, sys
try:
    d = json.loads(open(sys.argv[1], encoding="utf-8").read() or "{}")
except Exception:
    sys.exit(1)
sys.exit(0 if d.get("permission") == "deny" else 1)
' "$out"
      ;;
    gemini-hook-adapter.sh|codex-hook-env.sh)
      [ "$rc" -eq 2 ]
      ;;
    *)
      return 1
      ;;
  esac
}

# Build a mutant that keeps the deny and drops the reason. Anchor is the
# adapter's real invoke line; a missing anchor fails loud (vacuous teeth).
build_reason_mutant() {
  local src="$1" dest="$2" base="$3"
  python3 - "$src" "$dest" "$base" <<'PY'
import pathlib
import sys

src, dest, base = sys.argv[1], sys.argv[2], sys.argv[3]
text = pathlib.Path(src).read_text(encoding="utf-8")
# One substitution per adapter. If the invoke line moves, FAIL LOUD rather
# than "mutating" nothing and reporting teeth we do not have.
# Quotes assembled so this file is valid Python 3.9 (no \' inside '...').
q = "'"
anchors = {
    "gemini-hook-adapter.sh": (
        '    _normalise | bash "$real" "$@" >/dev/null\n',
        '    _normalise | bash "$real" "$@" >/dev/null 2>&1\n',
    ),
    "cursor-hook-adapter.sh": (
        "    printf " + q + "%s" + q + ' "$stdin_json" | bash "$real" "$@" >/dev/null\n',
        "    printf " + q + "%s" + q + ' "$stdin_json" | bash "$real" "$@" >/dev/null 2>&1\n',
    ),
    "copilot-hook-adapter.sh": (
        "    out=\"$(printf " + q + "%s" + q + ' "$claude_stdin" | THING_SEAT_ACTIVE="${THING_SEAT_ACTIVE:-}" bash "$real" "$@" 2>"$err_file")"; rc=$?\n',
        "    out=\"$(printf " + q + "%s" + q + ' "$claude_stdin" | THING_SEAT_ACTIVE="${THING_SEAT_ACTIVE:-}" bash "$real" "$@" 2>/dev/null)"; rc=$?\n',
    ),
    "codex-hook-env.sh": (
        "printf " + q + "%s" + q + ' "$_payload" | "$_hook" "$@"\n',
        "printf " + q + "%s" + q + ' "$_payload" | "$_hook" "$@" >/dev/null 2>&1\n',
    ),
}
pair = anchors.get(base)
if pair is None:
    sys.stderr.write("no mutant recipe for %s\n" % base)
    sys.exit(3)
old, new = pair
if old not in text:
    sys.stderr.write("MUTATION ANCHOR NOT FOUND in %s\n" % base)
    sys.exit(3)
pathlib.Path(dest).write_text(text.replace(old, new, 1), encoding="utf-8")
PY
}

run_one() {
  local rel="$1"  # hooks/foo.sh
  local base="${rel##*/}"
  local adapter="$CORE/$rel"
  [ -f "$adapter" ] || { bad "$rel: named by host-support.json but missing on disk"; return; }

  case "$base" in
    copilot-hook-adapter.sh)
      if ! command -v jq >/dev/null 2>&1; then
        printf '  ‼ %s SKIPPED — jq absent (adapter no-ops without it)\n' "$base"
        printf '    THIS IS NOT A PASS. CI must provide jq.\n'
        if [ -n "${CI:-}" ]; then
          bad "$base unrunnable in CI (jq missing)"
        fi
        return
      fi
      ;;
    cursor-hook-adapter.sh|gemini-hook-adapter.sh|codex-hook-env.sh)
      ;;
    *)
      bad "$rel: no envelope driver — add one in check-adapter-roundtrip.sh (fail-closed)"
      return
      ;;
  esac

  local tmp
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/g208-rt.XXXXXX")"
  write_loud_stub "$tmp/loud.sh"
  RC_OUT="$tmp"
  export RC_OUT
  if ! payload_for "$base" "$tmp" >"$tmp/payload"; then
    rm -rf "$tmp"
    bad "$rel: could not build a payload"
    return
  fi
  invoke_adapter "$adapter" "$base" "$tmp/loud.sh" <"$tmp/payload"
  local rc
  rc="$(cat "$tmp/rc")"
  if reason_survived "$base" "$tmp/out" "$tmp/err" "$rc"; then
    ok "$rel: deny + reason survived translation"
  else
    bad "$rel: deny/reason lost (rc=$rc out=$(wc -c <"$tmp/out" | tr -d ' ') err=$(wc -c <"$tmp/err" | tr -d ' '))"
  fi
  rm -rf "$tmp"
}

# bash 3.2 has no lastpipe, so a `| while` would lose PASS/FAIL. Drive from a
# temp list instead.
run_good() {
  printf '── Gate 208 adapter round-trip ──\n'
  local listfile rel
  listfile="$(mktemp "${TMPDIR:-/tmp}/g208-adapters.XXXXXX")"
  adapters_from_map >"$listfile" || { rm -f "$listfile"; die2 "could not derive adapters from host-support.json"; }
  if [ ! -s "$listfile" ]; then
    rm -f "$listfile"
    die2 "host-support.json names zero hook adapters — the walk was empty"
  fi
  while IFS= read -r rel; do
    [ -n "$rel" ] || continue
    run_one "$rel"
  done <"$listfile"
  rm -f "$listfile"
}

# Mutant half: first map-derived adapter whose recipe we have. Drop the reason,
# keep the deny, assert THIS checker flags it (exit 2).
drive_mutant() {
  local listfile rel base adapter tmp mutant rc
  listfile="$(mktemp "${TMPDIR:-/tmp}/g208-m.XXXXXX")"
  adapters_from_map >"$listfile" || { rm -f "$listfile"; printf '%s\n' "3"; return 0; }
  rel=""
  while IFS= read -r line; do
    base="${line##*/}"
    case "$base" in
      copilot-hook-adapter.sh)
        if ! command -v jq >/dev/null 2>&1; then
          continue
        fi
        rel="$line"
        break
        ;;
      cursor-hook-adapter.sh|gemini-hook-adapter.sh|codex-hook-env.sh)
        rel="$line"
        break
        ;;
    esac
  done <"$listfile"
  rm -f "$listfile"
  if [ -z "$rel" ]; then
    printf '%s\n' "3"
    return 0
  fi
  base="${rel##*/}"
  adapter="$CORE/$rel"
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/g208-mut.XXXXXX")"
  mutant="$tmp/adapter-mutant.sh"
  if ! build_reason_mutant "$adapter" "$mutant" "$base"; then
    rm -rf "$tmp"
    printf '%s\n' "3"
    return 0
  fi
  chmod +x "$mutant"
  write_loud_stub "$tmp/loud.sh"
  RC_OUT="$tmp"
  export RC_OUT
  payload_for "$base" "$tmp" >"$tmp/payload" || { rm -rf "$tmp"; printf '%s\n' "3"; return 0; }
  invoke_adapter "$mutant" "$base" "$tmp/loud.sh" <"$tmp/payload"
  rc="$(cat "$tmp/rc")"
  # The mutant MUST keep the deny (otherwise we are testing the wrong thing)
  # and MUST lose the sentinel.
  if ! deny_survived "$base" "$tmp/out" "$rc"; then
    rm -rf "$tmp"
    # Mutant also lost the deny — vacuous for the reason-loss class.
    printf '%s\n' "3"
    return 0
  fi
  if reason_survived "$base" "$tmp/out" "$tmp/err" "$rc"; then
    rm -rf "$tmp"
    # Reason still present: the mutation did not drop it.
    printf '%s\n' "0"
    return 0
  fi
  rm -rf "$tmp"
  # Deny kept, reason gone: the v0.250.0 shape. Caught, exit 2.
  printf '%s\n' "2"
}

run_must_fail() {
  printf '── Gate 208 adapter mutant halves ──\n'
  local rc
  rc="$(drive_mutant)"
  if [ "$rc" -eq 2 ]; then
    ok "teeth: a mutant that drops the deny reason is caught (exit 2)"
  elif [ "$rc" -eq 3 ]; then
    bad "teeth: could not build a reason-dropping mutant (anchor missing?)"
  else
    bad "teeth: reason-dropping mutant was NOT caught (got $rc, want 2)"
  fi
}

MODE="${1:-}"
case "$MODE" in
  --drive-mutant)
    rc="$(drive_mutant)"
    exit "$rc"
    ;;
  --must-fail)
    run_must_fail
    if [ "$FAIL" -gt 0 ]; then exit 2; fi
    exit 0
    ;;
  --self-test)
    run_good
    run_must_fail
    ;;
  "")
    run_good
    ;;
  *)
    printf 'usage: check-adapter-roundtrip.sh [--self-test|--must-fail|--drive-mutant]\n' >&2
    exit 2
    ;;
esac

printf '  (%d pass, %d fail)\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 2
fi
exit 0
