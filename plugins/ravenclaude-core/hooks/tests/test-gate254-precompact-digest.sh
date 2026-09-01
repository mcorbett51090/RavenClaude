#!/usr/bin/env bash
# test-gate254-precompact-digest.sh — Gate 254 audit fixture for the PreCompact
# archival hook (hooks/precompact-digest.sh), P2 of the precompact-critical-context
# FORGE plan (.ravenclaude/runs/forge/precompact-critical-context/plan.md).
#
# REWORKED for the hardened, detached-worker + posture-gated shape from the P4
# security review (.ravenclaude/runs/forge/precompact-critical-context/security-review-p4.md):
#   B1 — the hook is inert unless `cheap_lane.mode` is set in a fixture posture
#        file (absent/off => never even resolves the digest engine's payload).
#        Above that, extract_digest() itself refuses to egress unless the
#        floor (orchestrator_repo_pii: false OR cheap_lane_zdr_confirmed: true)
#        is open.
#   B2 — extraction runs DETACHED. The hook returns near-instantly; a digest
#        (when one is going to appear at all) shows up SECONDS LATER, from a
#        background worker the hook never waits on. A synchronous "check the
#        digest exists right after the hook call returns" assertion would
#        RACE that worker, so every case below either:
#          (a) bounded-POSITIVE-polls for a digest that SHOULD eventually
#              appear (_wait_for_digest), or
#          (b) bounded-NEGATIVE-waits to confirm one that must NEVER appear
#              genuinely never does (_confirm_digest_absent_holds) — not just
#              "wasn't there the instant we checked".
#
# Proves, by construction, not by convention:
#   1  inert-by-default: NO comfort-posture.yaml at all -> hook exits 0
#      immediately and NEVER writes a digest, even with a fully valid
#      transcript_path (negative hold).
#   2  inert: cheap_lane.mode: off -> same as (1), explicit off beats a
#      would-be-valid transcript (negative hold).
#   3  egress-floor-blocked: cheap_lane.mode ON but neither
#      orchestrator_repo_pii: false NOR cheap_lane_zdr_confirmed: true is set
#      -> the hook returns fast, but NO subprocess is ever invoked (a stub
#      delegate script that would drop a sentinel file if called never does)
#      AND no digest file is ever written (negative hold).
#   4  success, floor open: cheap_lane.mode ON + orchestrator_repo_pii: false
#      -> the hook returns near-instantly (asserted against a deliberately
#      SLOW stub delegate, proving detachment structurally, not just that the
#      real path happens to be fast) and a digest appears seconds later, well
#      after the hook's own process already exited (bounded positive poll).
#   5  transcript_path absent -> exits 0, silent, never writes a digest
#      (optional field on the documented PreCompact payload).
#   6  transcript_path points at a file that does not exist -> same as (5).
#   7  engine exhausts every extraction path (cheap-lane + claude-fallback
#      scripts both point nowhere, floor open) -> engine's own exit-3
#      contract; hook still exits 0 fast, and no digest ever appears
#      (negative hold) since nothing succeeded.
#   8  malformed / non-JSON stdin -> exits 0, silent.
#   9  empty stdin -> exits 0, silent.
#  10  the digest engine cannot be resolved at all (a partial / corrupted
#      install: no CLAUDE_PLUGIN_ROOT, no sibling scripts/) -> exits 0,
#      silent, no digest ever (negative hold).
#
# --must-fail-block builds a mutant with the fail-safe wrapping removed — NOT
# the old synchronous `_rc_timeout 10 python3 ...` line, which no longer
# exists verbatim in the detached-worker source. The mechanism that now
# guards the hook's SYNCHRONOUS portion (everything before the extraction is
# backgrounded) is: the EXIT trap (`trap 'exit 0' EXIT`), `set -uo pipefail`
# (deliberately no `-e`), and each individual `|| exit 0` fail-safe guard.
# Since the risky work (the engine call) now runs disowned in its own
# background subshell, its own exit code can no longer propagate to the
# hook's exit status regardless of trap/set -e — so a synchronous mutant has
# to target one of the SYNCHRONOUS guards instead. This one strips the EXIT
# trap, flips `set -uo pipefail` to `set -euo pipefail`, and removes the
# `|| exit 0` fallback from the engine-resolution guard
# (`[ -f "$engine" ] || exit 0`) — then drives the mutant through the exact
# "engine unresolvable" scenario from case 10 above, where the bare
# `[ -f "$engine" ]` test now evaluates false with no `||` to catch it and no
# trap to force exit 0, so under `set -e` the mutant genuinely aborts
# non-zero. This proves the fail-safe wrapping is load-bearing for the
# hook's SYNCHRONOUS failure surface, exactly as the original must-fail half
# proved it for the (now-retired) synchronous engine-wait shape.
#
# A vacuity guard refuses to run if the mutation's target strings are not
# found verbatim in the source (the lesson from Gate 186's own must-fail
# fixture going silently toothless when render()'s signature changed
# underneath it — CLAUDE.md v0.245.0/P2b).
#
# Self-contained: every fixture is a throwaway mktemp project; no network call
# is ever made (the cheap-lane / claude-fallback scripts are always either a
# local stub or pointed at a path that does not exist).
#
# Run directly:
#   bash plugins/ravenclaude-core/hooks/tests/test-gate254-precompact-digest.sh
#   bash plugins/ravenclaude-core/hooks/tests/test-gate254-precompact-digest.sh --must-fail-block
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$HERE/precompact-digest.sh"
ENGINE="$HERE/../scripts/precompact-digest.py"
mode="${1:-normal}"
fails=0

[ -f "$HOOK" ] || { echo "FAIL: hook not found at $HOOK"; exit 1; }
[ -f "$ENGINE" ] || { echo "FAIL: engine not found at $ENGINE"; exit 1; }

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# ---- helpers ------------------------------------------------------------------
_payload() { # $1=transcript_path(optional) $2=session_id(optional, default gate254)
  python3 -c '
import json, sys
sid = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else "gate254"
p = {"hook_event_name": "PreCompact", "session_id": sid, "trigger": "manual"}
if len(sys.argv) > 1 and sys.argv[1]:
    p["transcript_path"] = sys.argv[1]
print(json.dumps(p))' "${1:-}" "${2:-}"
}

_assert_eq() { # $1=label $2=got $3=want
  if [ "$2" = "$3" ]; then printf '  ok   %s\n' "$1"
  else printf '  FAIL %s (got=%s want=%s)\n' "$1" "$2" "$3"; fails=$((fails + 1)); fi
}

_assert_ne() { # $1=label $2=got $3=must-not-equal
  if [ "$2" != "$3" ]; then printf '  ok   %s (got=%s)\n' "$1" "$2"
  else printf '  FAIL %s (got=%s, expected something else)\n' "$1" "$2"; fails=$((fails + 1)); fi
}

_assert_empty() { # $1=label $2=str
  if [ -z "$2" ]; then printf '  ok   %s\n' "$1"
  else printf '  FAIL %s (expected no output, got %s bytes: %s)\n' "$1" "${#2}" "$2"; fails=$((fails + 1)); fi
}

_assert_lt() { # $1=label $2=got(int) $3=ceiling(int)
  if [ "$2" -lt "$3" ]; then printf '  ok   %s (got=%s, ceiling=%s)\n' "$1" "$2" "$3"
  else printf '  FAIL %s (got=%s, wanted under %s)\n' "$1" "$2" "$3"; fails=$((fails + 1)); fi
}

_digest_count() { # $1=run_dir -> number of precompact-digest-*.md files (0 if dir absent)
  if [ -d "$1" ]; then
    find "$1" -maxdepth 1 -name 'precompact-digest-*.md' 2>/dev/null | wc -l | tr -d '[:space:]'
  else
    echo 0
  fi
}

# B2 — bounded POSITIVE poll: a digest is expected to appear EVENTUALLY (the
# detached worker is mid-flight when the hook already returned). Polls every
# 100ms up to $2 seconds. Sets FOUND_DIGEST to the path found, or "".
_wait_for_digest() { # $1=run_dir $2=max_seconds
  local dir="$1" max_s="$2" iters i m
  iters=$((max_s * 10))
  FOUND_DIGEST=""
  for i in $(seq 1 "$iters"); do
    m="$(find "$dir" -maxdepth 1 -name 'precompact-digest-*.md' 2>/dev/null | head -1)"
    if [ -n "$m" ]; then FOUND_DIGEST="$m"; return 0; fi
    sleep 0.1
  done
  return 1
}

# B2 — bounded NEGATIVE hold: a digest must NEVER appear. A single "not there
# yet" check would race the detached worker and pass for the wrong reason
# (checked too early, not because nothing was ever going to write it) — this
# holds the check open for $2 seconds and fails the instant one shows up.
# Sets FOUND_DIGEST to the offending path if the hold breaks, else "".
_confirm_digest_absent_holds() { # $1=run_dir $2=hold_seconds
  local dir="$1" hold_s="$2" iters i m
  iters=$((hold_s * 10))
  for i in $(seq 1 "$iters"); do
    m="$(find "$dir" -maxdepth 1 -name 'precompact-digest-*.md' 2>/dev/null | head -1)"
    if [ -n "$m" ]; then FOUND_DIGEST="$m"; return 1; fi
    sleep 0.1
  done
  FOUND_DIGEST=""
  return 0
}

# Runs the given hook script against $1=payload with $2.. as NAME=VALUE env
# pairs scoped to this one call. Sets LAST_OUT (stdout only), LAST_RC (exit
# code), and LAST_MS (wall-clock milliseconds for the hook's OWN synchronous
# return — the B2 non-blocking invariant).
_run() {
  local hook="$1" payload="$2"
  shift 2
  local rcfile="$T/.lastrc" start_ns end_ns
  : > "$rcfile"
  start_ns="$(python3 -c 'import time; print(time.time_ns())')"
  LAST_OUT="$(
    for kv in "$@"; do export "$kv"; done
    printf '%s' "$payload" | bash "$hook" 2>/dev/null
    echo "$?" > "$rcfile"
  )"
  end_ns="$(python3 -c 'import time; print(time.time_ns())')"
  LAST_RC="$(cat "$rcfile" 2>/dev/null || echo -1)"
  LAST_MS=$(( (end_ns - start_ns) / 1000000 ))
}

# ---- posture fixtures -----------------------------------------------------
# $1=project_dir  $2=cheap_lane_mode ("" -> write no cheap_lane block at all,
# still creates the file with no cheap_lane: key -- distinct from "no file at
# all")  $3=pii_clean(true/false/"")  $4=zdr(true/"")
_write_posture() {
  local dir="$1" mode="$2" pii="$3" zdr="$4"
  mkdir -p "$dir/.ravenclaude"
  {
    if [ -n "$mode" ]; then
      echo "cheap_lane:"
      echo "  mode: $mode"
      echo "  agent: grok"
    fi
    if [ "$pii" = "true" ]; then
      echo "orchestrator_repo_pii: false"
    fi
    if [ "$zdr" = "true" ]; then
      echo "cheap_lane_zdr_confirmed: true"
    fi
  } > "$dir/.ravenclaude/comfort-posture.yaml"
}

# A stub cheap-lane script: succeeds instantly, no network, no real CLI.
CHEAP_OK="$T/cheap-ok.sh"
cat >"$CHEAP_OK" <<'STUB'
#!/usr/bin/env bash
echo "- decision A"
echo "- TODO B"
STUB
chmod +x "$CHEAP_OK"

# A stub cheap-lane script that SLEEPS before responding -- proves the hook
# genuinely does not wait on it (B2), rather than merely "usually being fast".
CHEAP_SLOW="$T/cheap-slow.sh"
cat >"$CHEAP_SLOW" <<'STUB'
#!/usr/bin/env bash
sleep 3
echo "- decision A (slow path)"
echo "- TODO B"
STUB
chmod +x "$CHEAP_SLOW"

# A transcript file good enough to be "readable" -- its content is irrelevant
# to the HOOK (it only hands the path to precompact-digest.py; the hook
# itself never reads transcript content).
TRANSCRIPT="$T/transcript.jsonl"
printf '{"type":"user","message":{"role":"user","content":"hello"}}\n{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"a reply"}]}}\n' > "$TRANSCRIPT"

# ================================================================================
# --must-fail-block: mutant with the fail-safe wrapping removed
# ================================================================================
if [ "$mode" = "--must-fail-block" ]; then
  MUT="$T/mutant.sh"
  python3 - "$HOOK" "$MUT" <<'MUTPY'
import pathlib, sys

src_path, mut_path = sys.argv[1], sys.argv[2]
src = pathlib.Path(src_path).read_text()

replacements = [
    ("trap 'exit 0' EXIT\n", "# [mutant] EXIT trap removed\n"),
    ("set -uo pipefail\n", "set -euo pipefail  # [mutant] -e enabled, no trap to catch it\n"),
    (
        '[ -f "$engine" ] || exit 0\n',
        '[ -f "$engine" ]\n'
        "# [mutant] the exit-0 fallback is gone -- under set -e with no trap, this\n"
        "# line's own test failure (engine genuinely unresolvable) now aborts the\n"
        "# whole script instead of gracefully returning 0.\n",
    ),
]

missing = [old for old, _ in replacements if old not in src]
if missing:
    for m in missing:
        print(f"MUST-FAIL SETUP ERROR: mutation target not found verbatim in {src_path}:", file=sys.stderr)
        print(repr(m), file=sys.stderr)
    sys.exit(1)

for old, new in replacements:
    src = src.replace(old, new, 1)

pathlib.Path(mut_path).write_text(src)
MUTPY
  if [ "$?" -ne 0 ]; then
    echo "Gate 254 — must-fail half SETUP FAILED (see stderr above; the hook's source"
    echo "  changed shape and this fixture needs updating to match)"
    exit 1
  fi

  echo "Gate 254 — must-fail half (fail-safe wrapping removed, driven through the"
  echo "  'engine unresolvable' scenario)"

  # Isolated copy, no CLAUDE_PLUGIN_ROOT, no sibling scripts/ -- exactly case
  # 10's real-world "partial/corrupted install" shape, which is the only
  # synchronous path this hook can genuinely fail on. A real transcript +
  # posture ON just proves we get PAST the early gates and INTO the
  # engine-resolution guard the mutation targets.
  ISO="$T/mutant-isolated/hooks"
  mkdir -p "$ISO"
  cp "$MUT" "$ISO/precompact-digest.sh"
  PROJM="$T/mutant-proj"
  _write_posture "$PROJM" agent true ""

  _run "$ISO/precompact-digest.sh" "$(_payload "$TRANSCRIPT" gate254mut)" \
    "CLAUDE_PROJECT_DIR=$PROJM" \
    "CLAUDE_PLUGIN_ROOT="
  _assert_ne "fail-safe wrapping stripped: the mutant DOES exit non-zero (a real block)" "$LAST_RC" "0"

  if [ "$fails" -gt 0 ]; then
    echo "  UNEXPECTED: the mutant did NOT block — the fail-safe-wrapping assertion is toothless"
    exit 1
  fi
  echo "  (as expected: the mutant DID block, so the fail-safe wrapping is proven load-bearing)"
  exit 0
fi

# ================================================================================
# The real assertions
# ================================================================================
echo "Gate 254 — precompact-digest.sh (PreCompact archival hook, detached + posture-gated)"

# 1. inert-by-default: NO comfort-posture.yaml at all -> hook exits 0
#    immediately, and a digest genuinely NEVER appears even with a fully
#    valid transcript_path (negative hold, not just "not yet").
PROJ1="$T/proj1"
mkdir -p "$PROJ1"   # no .ravenclaude/comfort-posture.yaml written at all
_run "$HOOK" "$(_payload "$TRANSCRIPT" gate254)" \
  "CLAUDE_PROJECT_DIR=$PROJ1" "RC_CHEAP_LANE_SCRIPT=$CHEAP_OK"
_assert_eq "inert-by-default (no posture file): hook exits 0" "$LAST_RC" "0"
_assert_empty "inert-by-default: silent on stdout" "$LAST_OUT"
if _confirm_digest_absent_holds "$PROJ1/.ravenclaude/runs/gate254" 2; then
  printf '  ok   inert-by-default: no digest ever appears (held 2s)\n'
else
  printf '  FAIL inert-by-default: a digest appeared at %s despite no posture file\n' "$FOUND_DIGEST"
  fails=$((fails + 1))
fi

# 2. inert: cheap_lane.mode: off, explicit -> same as (1).
PROJ2="$T/proj2"
_write_posture "$PROJ2" off "" ""
_run "$HOOK" "$(_payload "$TRANSCRIPT" gate254)" \
  "CLAUDE_PROJECT_DIR=$PROJ2" "RC_CHEAP_LANE_SCRIPT=$CHEAP_OK"
_assert_eq "inert (cheap_lane.mode: off): hook exits 0" "$LAST_RC" "0"
_assert_empty "inert (mode: off): silent on stdout" "$LAST_OUT"
if _confirm_digest_absent_holds "$PROJ2/.ravenclaude/runs/gate254" 2; then
  printf '  ok   inert (mode: off): no digest ever appears (held 2s)\n'
else
  printf '  FAIL inert (mode: off): a digest appeared at %s\n' "$FOUND_DIGEST"
  fails=$((fails + 1))
fi

# 3. egress-floor-blocked: cheap_lane.mode ON but NEITHER
#    orchestrator_repo_pii: false NOR cheap_lane_zdr_confirmed: true is set.
#    Sentinel delegate scripts prove NO subprocess is ever invoked, and a
#    negative hold proves no digest is ever written.
SENTINEL_CHEAP="$T/sentinel-cheap-invoked"
SENTINEL_FALLBACK="$T/sentinel-fallback-invoked"
CHEAP_SENTINEL="$T/cheap-sentinel.sh"
cat >"$CHEAP_SENTINEL" <<STUB
#!/usr/bin/env bash
touch "$SENTINEL_CHEAP"
echo "- SHOULD NEVER HAPPEN -- floor was supposed to block this"
STUB
chmod +x "$CHEAP_SENTINEL"
FALLBACK_SENTINEL="$T/fallback-sentinel.sh"
cat >"$FALLBACK_SENTINEL" <<STUB
#!/usr/bin/env bash
touch "$SENTINEL_FALLBACK"
echo "- SHOULD NEVER HAPPEN -- floor was supposed to block this"
STUB
chmod +x "$FALLBACK_SENTINEL"

PROJ3="$T/proj3"
_write_posture "$PROJ3" agent "" ""   # cheap_lane ON, floor NOT open (no pii/zdr)
rm -f "$SENTINEL_CHEAP" "$SENTINEL_FALLBACK"
_run "$HOOK" "$(_payload "$TRANSCRIPT" gate254)" \
  "CLAUDE_PROJECT_DIR=$PROJ3" \
  "RC_CHEAP_LANE_SCRIPT=$CHEAP_SENTINEL" \
  "RC_CLAUDE_ORCHESTRATE_SCRIPT=$FALLBACK_SENTINEL"
_assert_eq "egress-floor-blocked: hook exits 0" "$LAST_RC" "0"
_assert_empty "egress-floor-blocked: silent on stdout" "$LAST_OUT"
if _confirm_digest_absent_holds "$PROJ3/.ravenclaude/runs/gate254" 2; then
  printf '  ok   egress-floor-blocked: no digest ever written (held 2s)\n'
else
  printf '  FAIL egress-floor-blocked: a digest appeared at %s\n' "$FOUND_DIGEST"
  fails=$((fails + 1))
fi
if [ ! -e "$SENTINEL_CHEAP" ]; then
  printf '  ok   egress-floor-blocked: cheap-lane delegate NEVER invoked\n'
else
  printf '  FAIL egress-floor-blocked: cheap-lane delegate WAS invoked despite the floor\n'
  fails=$((fails + 1))
fi
if [ ! -e "$SENTINEL_FALLBACK" ]; then
  printf '  ok   egress-floor-blocked: claude-fallback delegate NEVER invoked\n'
else
  printf '  FAIL egress-floor-blocked: claude-fallback delegate WAS invoked despite the floor\n'
  fails=$((fails + 1))
fi

# 4. success, floor open: cheap_lane.mode ON + orchestrator_repo_pii: false.
#    The hook must return near-instantly even though the stub delegate
#    SLEEPS 3s -- proving detachment structurally. The digest then appears
#    seconds later via a bounded POSITIVE poll, well after the hook's own
#    process already exited.
PROJ4="$T/proj4"
_write_posture "$PROJ4" agent true ""
_run "$HOOK" "$(_payload "$TRANSCRIPT" gate254)" \
  "CLAUDE_PROJECT_DIR=$PROJ4" "RC_CHEAP_LANE_SCRIPT=$CHEAP_SLOW"
_assert_eq "success: hook exits 0" "$LAST_RC" "0"
_assert_empty "success: silent on stdout (archival only, no envelope)" "$LAST_OUT"
_assert_lt "success: hook returns near-instantly (does NOT wait on the 3s-slow delegate)" "$LAST_MS" 2000
if _wait_for_digest "$PROJ4/.ravenclaude/runs/gate254" 8; then
  printf '  ok   success: digest appears within 8s of the hook returning, at %s\n' "$FOUND_DIGEST"
  _assert_eq "success: writes exactly one digest file" \
    "$(_digest_count "$PROJ4/.ravenclaude/runs/gate254")" "1"
else
  printf '  FAIL success: no digest appeared within 8s -- B2 REGRESSION (detached worker never completed or never wrote)\n'
  fails=$((fails + 1))
fi

# 5. transcript_path absent -> silent, exits 0, no digest ever (posture ON,
#    proving this early guard fires regardless of an otherwise-permissive
#    posture).
PROJ5="$T/proj5"
_write_posture "$PROJ5" agent true ""
_run "$HOOK" "$(_payload "" gate254)" "CLAUDE_PROJECT_DIR=$PROJ5"
_assert_eq "absent transcript_path: hook exits 0" "$LAST_RC" "0"
_assert_empty "absent transcript_path: silent" "$LAST_OUT"
if _confirm_digest_absent_holds "$PROJ5/.ravenclaude/runs/gate254" 2; then
  printf '  ok   absent transcript_path: no digest ever written (held 2s)\n'
else
  printf '  FAIL absent transcript_path: a digest appeared at %s\n' "$FOUND_DIGEST"
  fails=$((fails + 1))
fi

# 6. transcript_path points at a file that does not exist -> silent, exits 0.
PROJ6="$T/proj6"
_write_posture "$PROJ6" agent true ""
_run "$HOOK" "$(_payload "$T/does-not-exist.jsonl" gate254)" "CLAUDE_PROJECT_DIR=$PROJ6"
_assert_eq "missing transcript file: hook exits 0" "$LAST_RC" "0"
if _confirm_digest_absent_holds "$PROJ6/.ravenclaude/runs/gate254" 2; then
  printf '  ok   missing transcript file: no digest ever written (held 2s)\n'
else
  printf '  FAIL missing transcript file: a digest appeared at %s\n' "$FOUND_DIGEST"
  fails=$((fails + 1))
fi

# 7. engine exhausts every extraction path (floor OPEN, but both delegate
#    scripts point nowhere) -> the engine's own exit-3 contract; hook still
#    exits 0 fast, and NO digest ever appears (negative hold) since nothing
#    on the worker's side succeeded.
PROJ7="$T/proj7"
_write_posture "$PROJ7" agent true ""
_run "$HOOK" "$(_payload "$TRANSCRIPT" gate254)" \
  "CLAUDE_PROJECT_DIR=$PROJ7" \
  "RC_CHEAP_LANE_SCRIPT=$T/no-such-cheap-lane.sh" \
  "RC_CLAUDE_ORCHESTRATE_SCRIPT=$T/no-such-claude-orchestrate.sh"
_assert_eq "engine exit-3 (extraction failed on every path): hook still exits 0" "$LAST_RC" "0"
if _confirm_digest_absent_holds "$PROJ7/.ravenclaude/runs/gate254" 2; then
  printf '  ok   engine exit-3: no digest file ever written (held 2s)\n'
else
  printf '  FAIL engine exit-3: a digest appeared at %s despite both extraction paths being unavailable\n' "$FOUND_DIGEST"
  fails=$((fails + 1))
fi

# 8. malformed / non-JSON stdin -> silent, exits 0.
PROJ8="$T/proj8"
_write_posture "$PROJ8" agent true ""
_run "$HOOK" 'this is not json at all {' "CLAUDE_PROJECT_DIR=$PROJ8"
_assert_eq "malformed JSON stdin: hook exits 0" "$LAST_RC" "0"
_assert_empty "malformed JSON stdin: silent" "$LAST_OUT"

# 9. empty stdin -> silent, exits 0.
PROJ9="$T/proj9"
_write_posture "$PROJ9" agent true ""
_run "$HOOK" '' "CLAUDE_PROJECT_DIR=$PROJ9"
_assert_eq "empty stdin: hook exits 0" "$LAST_RC" "0"
_assert_empty "empty stdin: silent" "$LAST_OUT"

# 10. the digest engine cannot be resolved at all (a partial/corrupted
#     install: no CLAUDE_PLUGIN_ROOT, and no sibling scripts/ next to the
#     copied hook) -> silent, exits 0, no digest ever. Proves the
#     `[ -f "$engine" ] || exit 0` guard holds even when both resolution
#     paths (plugin-root and in-repo-relative) come up empty.
ISOLATED="$T/isolated/hooks"
mkdir -p "$ISOLATED"
cp "$HOOK" "$ISOLATED/precompact-digest.sh"
PROJ10="$T/proj10"
_write_posture "$PROJ10" agent true ""
_run "$ISOLATED/precompact-digest.sh" "$(_payload "$TRANSCRIPT" gate254)" \
  "CLAUDE_PROJECT_DIR=$PROJ10" "CLAUDE_PLUGIN_ROOT="
_assert_eq "engine unresolvable (no sibling scripts/, no CLAUDE_PLUGIN_ROOT): hook exits 0" "$LAST_RC" "0"
_assert_empty "engine unresolvable: silent" "$LAST_OUT"
if _confirm_digest_absent_holds "$PROJ10/.ravenclaude/runs/gate254" 2; then
  printf '  ok   engine unresolvable: no digest ever written (held 2s)\n'
else
  printf '  FAIL engine unresolvable: a digest appeared at %s\n' "$FOUND_DIGEST"
  fails=$((fails + 1))
fi

echo "Gate 254: $((fails == 0 ? 1 : 0))/1 groups clean ($fails failed assertions)"
[ "$fails" -eq 0 ]
