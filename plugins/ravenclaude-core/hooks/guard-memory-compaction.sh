#!/usr/bin/env bash
#
# rc-state-key: "${CLAUDE_PROJECT_DIR:-$HOME}/.ravenclaude/runs/${CLAUDE_SESSION_ID:-unknown}/memory-snapshots"
# rc-state-scope: session
# rc-state-rationale: a snapshot is a BEFORE-IMAGE of this session's write, so the
#   session component is exactly right and a finer key would fragment the very
#   history the restore path reads. Note the protected resource — the memory index
#   — is a single global directory, so unlike a per-worktree ledger there is no
#   sibling to collide with: two agents editing it are editing the same file, and
#   the guard is supposed to see both.
# rc-state-escape: none — the guard denies only a >15% unreviewed shrink and the
#   sanctioned path is to make the write smaller or do it in reviewed steps, not
#   to bypass. It was built after a real -41% unreviewed rewrite with no backup.
#
# guard-memory-compaction.sh
# PreToolUse hook for Write|Edit|MultiEdit. Guards the agent's own durable memory
# index against an UNREVIEWED LOSSY REWRITE.
#
# premise-ok: pypi-404-instrument-proven-bidirectional — the unresolved negative in
#   the authoring session's ledger (pypi.org/pypi/graphiti-mcp/json -> 404) was settled
#   with a positive control on the SAME endpoint shape before this file was created:
#     graphiti-core -> 200 | requests -> 200 | graphiti-mcp -> 404 | zzz-not-real-pkg-99 -> 404
#   The probe returns 200 for packages that exist, so the 404 is a fact about the
#   package, not a broken instrument. NOTE: this module does not rest on that finding
#   at all — it rests on a directly-observed local incident (below).
#
# WHY THIS EXISTS — the Memory Engineering Protocol had a rule and no mechanism.
#   plugins/ravenclaude-core/CLAUDE.md § Memory Engineering Protocol:
#     Rule 3: "Memory is context, not enforcement. ... To actually _block_ an action,
#              use a hook or a permission deny. Never cite a memory, an instruction
#              file, or a stored policy as the control that prevents something."
#     Rule 4: "Nothing forgets by default ... Bound the growth or lose the index ...
#              An unbounded store is a decision that was never made."
#   Rule 4 shipped as PROSE ONLY, and Rule 3 says prose is not a control. This hook
#   is the missing control. It was written after a REAL incident on the author's own
#   machine (2026-08-10): MEMORY.md went 20,853 B -> 12,324 B (-41%, 57 -> 51 lines)
#   in ONE unreviewed agent edit, seventeen minutes wide, with no git and no Time
#   Machine underneath it. 8 prose clauses were lost store-wide and had to be
#   recovered from an undocumented content-addressed cache.
#
# WHAT IT DOES
#   1. SNAPSHOT — before any write to a guarded memory file, copy the current bytes
#      into the run dir. This is the part that always runs and is the real value:
#      it converts "unrecoverable" into "recoverable" whether or not we block.
#   2. MEASURE — compute the proposed new size from the tool payload.
#   3. DENY a large shrink (default > 15%) with exit 2, telling the agent to show a
#      diff and get approval rather than rewriting in place.
#
# WHAT IT DELIBERATELY DOES NOT DO
#   It does NOT block growth, and it does NOT block small edits. Appending a memory
#   is the normal path and must stay frictionless — a guard that fires constantly
#   gets disabled, and a disabled guard protects nothing.
#
# FAIL-SAFE BY CONTRACT
#   Every failure path exits 0 (allow). A guard that cannot read its input must not
#   block the session. The snapshot is best-effort for the same reason. The ONLY
#   non-zero exit is the deliberate shrink deny (exit 2 — the only code Claude Code
#   treats as blocking; exit 1 is a NON-blocking error and would silently allow).
#
# PORTABILITY — this file must run on stock macOS bash 3.2.57.
#   No `declare -A`, no `mapfile`, no `${x^^}`, no `shopt -s globstar`,
#   no GNU `timeout`, no `grep -P`, no `sed -i`. See the four macOS-door
#   milestones in the plugin CLAUDE.md; re-introducing any of them here
#   silently disarms this guard on every macOS session.

set -euo pipefail

# --- fail-safe event emitter (sourced; missing helper degrades to a no-op) ---
_emit_event_helper="$(dirname "$0")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

# No stdin => nothing to inspect. Allow.
[ -t 0 ] && exit 0
payload="$(cat 2>/dev/null || true)"
[ -z "$payload" ] && exit 0

# --- parse the tool call -----------------------------------------------------
# jq preferred; python3 fallback. If NEITHER is available we allow (fail-safe) —
# unlike guard-destructive.sh we do not warn, because a per-write warning would be
# noise on every file edit and this guard is narrower than the destructive one.
_field() {
  # $1 = a dotted path into the payload, e.g. '.tool_input.file_path'
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$payload" | jq -r "$1 // empty" 2>/dev/null || true
  elif command -v python3 >/dev/null 2>&1; then
    RC_JQPATH="$1" python3 -c '
import json,sys,os
p=[k for k in os.environ.get("RC_JQPATH","").lstrip(".").split(".") if k]
try:
    d=json.load(sys.stdin)
    for k in p:
        d=d.get(k) if isinstance(d,dict) else None
        if d is None: break
    sys.stdout.write("" if d is None else (d if isinstance(d,str) else json.dumps(d)))
except Exception:
    pass' <<RC_PAYLOAD_EOF 2>/dev/null || true
$payload
RC_PAYLOAD_EOF
  fi
}

tool_name="$(_field '.tool_name')"
file_path="$(_field '.tool_input.file_path')"

[ -z "$file_path" ] && exit 0

case "$tool_name" in
  Write | Edit | MultiEdit) : ;;
  *) exit 0 ;;
esac

# --- is this a guarded memory file? -----------------------------------------
# Guarded: a MEMORY.md (or MEMORY-*.md) inside a directory named `memory`.
# This matches Claude Code's user-scoped auto-memory
# (~/.claude/projects/<encoded>/memory/MEMORY.md) without hard-coding a host path,
# so it works for any consumer on any platform.
case "$file_path" in
  */memory/MEMORY.md | */memory/MEMORY-*.md) : ;;
  *) exit 0 ;;
esac

# Nothing to protect if the file does not exist yet (first write is pure growth).
[ -f "$file_path" ] || exit 0

old_bytes="$(wc -c < "$file_path" 2>/dev/null | tr -d ' ' || echo 0)"
case "$old_bytes" in '' | *[!0-9]*) exit 0 ;; esac
[ "$old_bytes" -lt 1024 ] && exit 0 # too small for a shrink ratio to mean anything

# --- 1. SNAPSHOT (best-effort, never blocks) --------------------------------
# This is the half that matters most: it exists so a lossy rewrite is always
# recoverable, independent of whether the deny below fires.
_snap_root="${CLAUDE_PROJECT_DIR:-$HOME}/.ravenclaude/runs/${CLAUDE_SESSION_ID:-unknown}/memory-snapshots"
if mkdir -p "$_snap_root" 2>/dev/null; then
  _stamp="$(date -u '+%Y%m%dT%H%M%SZ' 2>/dev/null || echo now)"
  cp "$file_path" "$_snap_root/$(basename "$file_path").$_stamp.bak" 2>/dev/null || true
fi

# --- escape hatch ------------------------------------------------------------
# A deliberate, reviewed compaction is a legitimate operation. Two ways to say so:
#   - export RC_MEMORY_COMPACTION_OK=1
#   - include the literal token `compaction-approved` in the new content
# Both are intentionally explicit: the guard blocks the SILENT path, not the
# considered one.
if [ "${RC_MEMORY_COMPACTION_OK:-}" = "1" ]; then
  exit 0
fi

# --- MultiEdit helpers -------------------------------------------------------
# MultiEdit's REAL tool_input shape is {file_path, edits: [{old_string,
# new_string}, ...]} -- there is no top-level old_string/new_string (that's
# Edit's shape). _field's dotted-path model can't express `edits[].new_string`
# either (its python3 fallback only does a plain dict-walk), so MultiEdit gets
# its own tiny jq-preferred/python3-fallback helpers, mirroring _field's own
# two-tier pattern above. Precision here is codepoint-length, not byte-exact --
# consistent with this whole Edit/MultiEdit branch's stated tolerance below
# ("enough precision to catch a wholesale rewrite, not an exact byte count").
_multiedit_new_strings() {
  # One new_string per line, so the compaction-approved escape hatch can be
  # checked across every edit in the call, not just a single new_string.
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$payload" | jq -r '.tool_input.edits[]? | (.new_string // "")' 2>/dev/null || true
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
    edits=(d.get("tool_input") or {}).get("edits") or []
    for e in edits:
        if isinstance(e, dict):
            sys.stdout.write(str(e.get("new_string") or "") + "\n")
except Exception:
    pass' <<RC_PAYLOAD_EOF 2>/dev/null || true
$payload
RC_PAYLOAD_EOF
  fi
}

_multiedit_delta() {
  # Sum of len(new_string) - len(old_string) across every edit.
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$payload" | jq -r \
      '[.tool_input.edits[]? | ((.new_string // "") | length) - ((.old_string // "") | length)] | add // 0' \
      2>/dev/null || true
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
    edits=(d.get("tool_input") or {}).get("edits") or []
    total=0
    for e in edits:
        if isinstance(e, dict):
            total += len(e.get("new_string") or "") - len(e.get("old_string") or "")
    sys.stdout.write(str(total))
except Exception:
    pass' <<RC_PAYLOAD_EOF 2>/dev/null || true
$payload
RC_PAYLOAD_EOF
  fi
}

# --- 2. MEASURE the proposed size -------------------------------------------
new_bytes=""
if [ "$tool_name" = "Write" ]; then
  _content="$(_field '.tool_input.content')"
  case "$_content" in *compaction-approved*) exit 0 ;; esac
  new_bytes="$(printf '%s' "$_content" | wc -c | tr -d ' ')"
elif [ "$tool_name" = "MultiEdit" ]; then
  _all_new="$(_multiedit_new_strings)"
  case "$_all_new" in *compaction-approved*) exit 0 ;; esac
  _delta="$(_multiedit_delta)"
  # Validate _delta is a clean (optionally negative) integer before using it
  # in arithmetic -- an unvalidated non-numeric value here would trip a bash
  # arithmetic error under `set -e`, which is NOT the same as this guard's
  # deliberate exit 2 and must never masquerade as one.
  _delta_valid=0
  case "$_delta" in
    '') _delta_valid=0 ;;
    -*)
      _dtail="${_delta#-}"
      case "$_dtail" in '' | *[!0-9]*) _delta_valid=0 ;; *) _delta_valid=1 ;; esac
      ;;
    *)
      case "$_delta" in *[!0-9]*) _delta_valid=0 ;; *) _delta_valid=1 ;; esac
      ;;
  esac
  if [ "$_delta_valid" = "1" ]; then
    new_bytes=$((old_bytes + _delta))
  fi
else
  # Edit: approximate the delta from the replaced spans. We only need
  # enough precision to catch a wholesale rewrite, not an exact byte count.
  _old_s="$(_field '.tool_input.old_string')"
  _new_s="$(_field '.tool_input.new_string')"
  case "$_new_s" in *compaction-approved*) exit 0 ;; esac
  if [ -n "$_old_s" ]; then
    _o="$(printf '%s' "$_old_s" | wc -c | tr -d ' ')"
    _n="$(printf '%s' "$_new_s" | wc -c | tr -d ' ')"
    new_bytes=$((old_bytes - _o + _n))
  fi
fi

case "${new_bytes:-}" in '' | *[!0-9]*) exit 0 ;; esac

# --- 3. DENY a large shrink --------------------------------------------------
# Threshold: percent of the ORIGINAL size that may be removed in one write.
# Configurable via `memory_guard: max_shrink_pct: N` in comfort-posture.yaml.
max_shrink_pct=15
_posture="${CLAUDE_PROJECT_DIR:-.}/.ravenclaude/comfort-posture.yaml"
if [ -f "$_posture" ]; then
  # Bounded read; plain grep+awk (no `grep -P`, no PyYAML dependency).
  _v="$(head -c 65536 "$_posture" 2>/dev/null |
    grep -E '^[[:space:]]*max_shrink_pct:[[:space:]]*[0-9]{1,3}[[:space:]]*$' 2>/dev/null |
    head -1 | awk -F: '{gsub(/[^0-9]/,"",$2); print $2}' || true)"
  case "$_v" in
    '' | *[!0-9]*) : ;;
    *) [ "$_v" -ge 1 ] && [ "$_v" -le 99 ] && max_shrink_pct="$_v" ;;
  esac
fi

[ "$new_bytes" -ge "$old_bytes" ] && exit 0 # growth is always fine

_removed=$((old_bytes - new_bytes))
_pct=$((_removed * 100 / old_bytes))
[ "$_pct" -le "$max_shrink_pct" ] && exit 0

_emit_hook_event "guard-memory-compaction.sh" "deny" "$tool_name" "$file_path" \
  "memory-compaction-shrink-${_pct}pct" 2

{
  echo "[guard-memory-compaction] BLOCKED: this write shrinks the memory index by ${_pct}% (${old_bytes} -> ${new_bytes} bytes), over the ${max_shrink_pct}% limit."
  echo "[guard-memory-compaction] An unreviewed in-place compaction of durable memory is how facts get lost with no undo."
  echo "[guard-memory-compaction] A snapshot of the current file was saved under .ravenclaude/runs/*/memory-snapshots/."
  echo "[guard-memory-compaction] Do this instead: show the user a diff of what would be REMOVED, and re-file anything"
  echo "[guard-memory-compaction] still needed into its topic file BEFORE trimming the index."
  echo "[guard-memory-compaction] To proceed deliberately: include 'compaction-approved' in the content, or set RC_MEMORY_COMPACTION_OK=1."
} >&2
exit 2 # 2 blocks the tool call; 1 would NOT (non-blocking error)
