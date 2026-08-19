#!/usr/bin/env bash
# Gate 234 — the handoff `--host` contract: both writers, one vocabulary.
#
# ⛔ GATE NUMBER. The synthesis plan named this "Gate 232". By the time it was
# built, 232 and 233 were taken (test-gate232-cause-taxonomy.sh,
# test-gate233-triage-outcome.sh) and audit-gates.sh's `Supported:` string ended
# at 233. The plan's own risk R-14 says to re-verify the number against that
# string and `ls hooks/tests/` rather than a remembered one, which is what
# happened. 234 was free on both.
#
# ── (1) WHAT EACH ROW ASSERTS, AND WHEN IT WAS MEASURED ──────────────────────
# Every row below drives BOTH seed writers — handoff-spawn.sh and
# context-handoff.py — for the same `--host` input, and asserts three things:
# the bash exit code, the bash seed CLASS, and the python seed CLASS. All the
# "before" values quoted per-row were measured in this worktree on 2026-08-19
# against origin/main, with controls.
#
# The defect this gate exists for: an agent read `--host grok|cli|chat` in the
# usage string, concluded Claude Code was unsupported, passed `--host chat` from
# a Claude Code session, and produced a Copilot-Chat seed telling a Claude Code
# successor to press Cmd+N (2026-08-18). The capability had shipped in 0.276.0.
# So the interface, not the code, was the defect — and an interface that RESOLVES
# an unrecognised name by guessing from the ambient environment is the same bug
# one layer down. That guess is what rows 12/19 pin.
#
# ── (2) THE OWNER RULING BEHIND THE D2 SPLIT, QUOTED ─────────────────────────
#   "A host **in `host-support.json` but unmapped** -> resolve to the
#    **host-neutral** copy-paste block, exit 0. Never a different agent's launch
#    command, and never a hard stop on a supported host.
#    A string in **neither** the enum nor the registry (typo, garbage) ->
#    **exit 2**, as D2 intended."
#                          — owner-decisions.md, "D2 — REFINED at G5", 2026-08-19
# The first draft of D2 hard-errored ANY unrecognised `--host`. Measured, that
# would have exit-2'd five hosts the marketplace officially declares — codex,
# cursor, gemini, aider, windsurf — each of which exits 0 today with a 573-byte
# host-neutral block. Destroying a working path AND pressuring an agent on an
# unlisted host toward the nearest recognised token (almost certainly `cli`) is
# the wrong-vendor failure this whole change set exists to prevent. Rows 12-17
# are that ruling; `--must-fail-registry` is what makes them measured.
#
# ── (3) WHAT IS DELIBERATELY UNCHANGED ───────────────────────────────────────
#   * Case (a) — nothing named AND nothing detected still gets the grok-first
#     fallback (row 20). This tooling exists for Grok->Grok handoff and the skill
#     records that Grok's markers are unreliable inside the agent process
#     ("Detection is hook-only"), so a REAL Grok session can land here. The D2
#     work NARROWS the grok fallback, and a gate that only checked the narrowing
#     would be satisfied by deleting the fallback outright.
#   * The `TERM_PROGRAM=vscode` ambiguity carve-out in handoff-spawn.sh. Kept per
#     the D5 tiebreak; measured load-bearing (it is the only thing between a
#     Cursor session and a grok launch).
#   * Gates 213, 215 and 230 and their expectations. None moved. The default was
#     NOT flipped to claude-code: Claude Code resolves by DETECTION and never
#     reaches the default, so the flip had a zero-case benefit (D1, reversed).
#
# ── (4) WHERE ELSE EACH PROPERTY IS PINNED ───────────────────────────────────
#   Gate 213 (test-gate213-handoff-spawn.sh) — positional grok seed only; the
#       copy-paste path; its one mutant anchors on the eager `seed="grok \"...`.
#   Gate 215 (test-gate215-handoff-host-spawn.sh) — "unset host still grok", and
#       chat/cli must not emit grok; two mutant anchors.
#   Gate 230 (test-gate227-handoff-seed-host.sh, filename != gate number) — the
#       per-host seed VALUE across both writers; five mutant anchors.
#   This gate does not re-assert those. Row 20 is the ONE deliberate overlap,
#   for the reason in (3).
#
# ── (5) ⛔ THE D4 ROW (23) PINS AN INVARIANT WITH NO MEASURED LIVE TRIGGER ────
# Row 23 asserts RC_HOST outranks THING_HOST in context-handoff.py. The critic
# reported this as live ("four adapters export THING_HOST, so a valid
# `--host claude-code` would break on Codex"). The RED TEAM CORRECTED THAT and
# could not reach the path from any shipped caller: THING_HOST is exported only
# INSIDE hook processes, no hook invokes context-handoff.py, handoff-nudge.py
# contains zero spawn references, bin/rc sets neither variable, and RC_HOST is
# written in exactly one place — main(), by `--host` itself. An explicit flag
# outranking ambient environment is right regardless of how often it fires.
# ⛔ Do NOT re-tell row 23 as a live incident. The next reader would inherit a
# false premise about how often it fires.
#
# ── MED-6 — THE ACCEPTANCE CRITERION FOR A MOVED MUTANT ANCHOR ───────────────
# ⛔ If a mutant anchor below stops matching, do not "fix" it by pasting the new
# source. Re-derive that the mutant reconstructs the ORIGINAL defect the row was
# written for, then confirm the must-fail half reports `fail > 0` ON THAT ROW,
# not on an incidental one.
#
# ── HONEST SCOPE ─────────────────────────────────────────────────────────────
# This gate does NOT drive a live spawn. Exercising handoff-spawn.sh's
# launch-successor branch end-to-end starts a real interactive agent, which no
# CI gate may do. Same limit Gate 230 states.
#
# bash 3.2-safe. No GNU-only tools.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/../.." && pwd)"
SPAWN="$PLUGIN_ROOT/scripts/handoff-spawn.sh"
PY="$PLUGIN_ROOT/scripts/context-handoff.py"
HOSTS_JSON="$PLUGIN_ROOT/knowledge/host-support.json"
TEMPLATE="$PLUGIN_ROOT/skills/session-handoff/templates/handoff.md"

# _rc_timeout: timeout -> gtimeout -> perl alarm -> UNBOUNDED.
. "$PLUGIN_ROOT/hooks/_portable.sh"

# ⛔ AC-5 — NEVER BARE `timeout`. Measured on this host 2026-08-19:
#     command -v timeout   -> rc=1  ABSENT
#     command -v gtimeout  -> rc=1  ABSENT
#     command -v perl      -> /usr/bin/perl
# In the repo's usual shape `out="$(timeout 5 cmd)" || ...`, an absent `timeout`
# is exit 127 — the command under test NEVER RUNS — and an "exits non-zero"
# assertion passes VACUOUSLY. Green on Linux CI, green-for-the-wrong-reason on
# macOS. That is why every bounded row below goes through _rc_timeout.
#
# ⛔ AND _rc_timeout's LAST fallback is `"$@"` — UNBOUNDED. On a host with none
# of the three, the arity mutant would run a known infinite loop to the GitHub
# Actions 6-hour job ceiling and block every PR in the repo, because
# audit-gates.sh wraps ZERO gate invocations in a timeout. A skip is not a pass.
if ! command -v timeout >/dev/null 2>&1 \
   && ! command -v gtimeout >/dev/null 2>&1 \
   && ! command -v perl >/dev/null 2>&1; then
  echo "Gate 234: NO WALL-CLOCK BOUND AVAILABLE (timeout/gtimeout/perl all absent)." >&2
  echo "  The arity rows execute a known infinite loop. THIS IS NOT A PASS." >&2
  if [ -n "${CI:-}" ]; then exit 1; fi
  exit 1
fi

MUST_FAIL=""
case "${1:-}" in
  "") ;;
  --must-fail-arity|--must-fail-d2|--must-fail-registry|--must-fail-namedunknown\
  |--must-fail-parity|--must-fail-precedence|--must-fail-flagauthority)
    MUST_FAIL="${1#--must-fail-}" ;;
  *) echo "Gate 234: unknown argument $1" >&2; exit 2 ;;
esac

pass=0
fail=0
FAILED=""
ok() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
no() { fail=$((fail + 1)); FAILED="$FAILED
    - $1"; printf '  FAIL %s\n' "$1"; }

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t gate234)"
cleanup() { [ -n "${TMP:-}" ] && [ -d "$TMP" ] && rm -rf "$TMP"; }
trap cleanup EXIT

REPO="$TMP/repo"
mkdir -p "$REPO/.ravenclaude/runs/t1"
printf 'brief\n' > "$REPO/.ravenclaude/runs/t1/handoff.md"
REPO_Q="$(printf '%q' "$REPO")"

# ---- must-fail halves -----------------------------------------------------
# Every mutation is an EXACT-STRING replacement in a COPY, done in python, with
# an existence check on every anchor (Gate 230's discipline). A half-applied
# mutant proves teeth it does not have, so a missing anchor is a hard exit 1.
_mutate() { # _mutate SRC DST  (edits on stdin as repr pairs)
  python3 - "$1" "$2" || {
    echo "Gate 234 must-fail half ($MUST_FAIL): an anchor moved — could not rebuild the defect" >&2
    echo "  ⛔ Re-derive that the mutant still reconstructs the ORIGINAL defect." >&2
    echo "     Do NOT paste the new source in to make it match." >&2
    exit 1
  }
}

if [ -n "$MUST_FAIL" ]; then
  PYPLUG="$TMP/pyplug"
  mkdir -p "$PYPLUG/scripts" "$PYPLUG/skills/session-handoff/templates"
  cp "$TEMPLATE" "$PYPLUG/skills/session-handoff/templates/handoff.md"
fi

case "$MUST_FAIL" in
  arity)
    # Restore the pre-fix SHIFT MECHANICS and nothing else: `host_flag="${2:-}";
    # shift 2`. With --host as the FINAL argument, `shift 2` cannot shift, $#
    # never decreases, and the loop spins forever at 100% CPU (measured
    # EXIT=142 BYTES=0 under a 5 s alarm; control with a value: EXIT=0, 443 B).
    #
    # ⛔ THIS MUTANT IS DELIBERATELY SURGICAL, AND AN EARLIER VERSION WAS NOT.
    # The first draft also removed `host_flag_seen=1`, which additionally
    # disabled flag authority — 30 assertions went red including rows 3-17, and
    # the half would have reported "teeth confirmed" off rows that have nothing
    # to do with arity. That is precisely the false tooth MED-6 names. Keeping
    # `host_flag_seen=1` means the ONLY behaviour this mutant changes is the
    # shift, so the red row is the arity row.
    #
    # Must turn red: row 24. ⛔ Rows 25 and 26 stay GREEN under this mutant and
    # that is CORRECT, not a gap: with host_flag_seen still set,
    # classify_host_flag("") and classify_host_flag("--dry-run") both return
    # `reject`, so the D2 block catches them on a second, independent mechanism.
    # `--must-fail-d2` and `--must-fail-namedunknown` are what pin those.
    #
    # ⛔ THIS MUTANT EXECUTES A KNOWN INFINITE LOOP. Every invocation of the
    # script below goes through _rc_timeout $BOUND. Row 24 asserts exit 2 AND
    # BYTES>0, so the hang's signature (124/142 with 0 bytes) is what turns it
    # red — the fix is what makes it green.
    MUT="$TMP/mutant-spawn.sh"
    _mutate "$SPAWN" "$MUT" <<'MUTATE'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
old = ('      host_flag_isflag=0\n'
       '      case "${2:-}" in\n'
       '        --*) host_flag_bad=1; host_flag_isflag=1 ;;\n'
       '        "") host_flag_bad=1 ;;\n'
       '        *) host_flag="$2" ;;\n'
       '      esac\n'
       '      shift\n'
       '      if [ "$host_flag_isflag" -eq 0 ] && [ $# -gt 0 ]; then shift; fi ;;\n')
new = '      host_flag="${2:-}"; shift 2 ;;\n'
if old not in text:
    sys.stderr.write("anchor not found: --host) shift mechanics\n")
    raise SystemExit(1)
open(dst, "w", encoding="utf-8").write(text.replace(old, new, 1))
MUTATE
    SPAWN="$MUT"
    ;;
  namedunknown)
    # Revert the named_but_unknown assignment to the pre-fix test, which keyed
    # on the flag's VALUE (`[ -n "$host_flag" ]`) rather than its PRESENCE.
    # This is the single bit that decides whether a host we cannot name a launch
    # command for gets host-neutral text or inherits the eager grok seed.
    # Must turn red:
    #   row 21 — THING_HOST=gemini with no flag emitted a LIVE `grok "..."`
    #            launch for a session that had named itself gemini (MED-7).
    #   row 25 — `--host ''` still exits 2 via D2, but the block it prints
    #            carries a GROK LAUNCH. That is the measured second-order defect:
    #            the naive shift fix converts the hang into a SILENT grok seed.
    MUT="$TMP/mutant-spawn.sh"
    _mutate "$SPAWN" "$MUT" <<'MUTATE'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
old = ('if [ "$host" = "unknown" ] && { [ "$host_flag_seen" -eq 1 ] '
       '|| [ -n "${RC_HOST:-}" ] || [ -n "${THING_HOST:-}" ]; }; then')
new = 'if [ -n "$host_flag" ] && [ "$host" = "unknown" ]; then'
if old not in text:
    sys.stderr.write("anchor not found: named_but_unknown assignment\n")
    raise SystemExit(1)
open(dst, "w", encoding="utf-8").write(text.replace(old, new, 1))
MUTATE
    SPAWN="$MUT"
    ;;
  d2)
    # Neuter the D2 rejection. A typo would exit 0 again.
    # Must turn red: row 18.
    MUT="$TMP/mutant-spawn.sh"
    _mutate "$SPAWN" "$MUT" <<'MUTATE'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
old = ('if [ "$host_flag_seen" -eq 1 ] && '
       '[ "$(classify_host_flag "$host_flag")" = "reject" ]; then')
if old not in text:
    sys.stderr.write("anchor not found: D2 reject guard\n")
    raise SystemExit(1)
open(dst, "w", encoding="utf-8").write(text.replace(old, "if false; then", 1))
MUTATE
    SPAWN="$MUT"
    ;;
  registry)
    # Drop codex from the duplicated registry literal. This is THE mutant that
    # proves AC-1 is measured rather than merely asserted: without it, rows
    # 12-16 would pass identically against a script that never learned the
    # registry at all.
    # Must turn red: rows 12 (codex would exit 2) and 31 (set mismatch).
    MUT="$TMP/mutant-spawn.sh"
    _mutate "$SPAWN" "$MUT" <<'MUTATE'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
old = "    claude-code|copilot|codex|cursor|gemini|aider|windsurf) return 0 ;;"
new = "    claude-code|copilot|cursor|gemini|aider|windsurf) return 0 ;;"
if old not in text:
    sys.stderr.write("anchor not found: is_registry_host literal\n")
    raise SystemExit(1)
open(dst, "w", encoding="utf-8").write(text.replace(old, new, 1))
MUTATE
    SPAWN="$MUT"
    ;;
  flagauthority)
    # Restore the environment fall-through. With CLAUDECODE set, `--host codex`
    # prints a CLAUDE CODE recipe again — the original claims-table row 8 defect.
    # Must turn red: row 19.
    MUT="$TMP/mutant-spawn.sh"
    _mutate "$SPAWN" "$MUT" <<'MUTATE'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
old = ('  if [ "$host_flag_seen" -eq 1 ]; then\n'
       '    from="$(normalize_host "$host_flag")"\n'
       '    if [ -n "$from" ] && [ "$from" != "unknown" ]; then\n'
       '      echo "$from"\n'
       '    else\n'
       '      echo unknown\n'
       '    fi\n'
       '    return\n'
       '  fi\n')
new = ('  from="$(normalize_host "$host_flag")"\n'
       '  if [ -n "$from" ] && [ "$from" != "unknown" ]; then\n'
       '    echo "$from"\n'
       '    return\n'
       '  fi\n')
if old not in text:
    sys.stderr.write("anchor not found: flag-authority early return\n")
    raise SystemExit(1)
open(dst, "w", encoding="utf-8").write(text.replace(old, new, 1))
MUTATE
    SPAWN="$MUT"
    ;;
  parity)
    # Delete the claude alias row from PYTHON only. bash keeps it, so the two
    # writers name different successors for the same handoff.
    # Must turn red: rows 4 and 5 (py class != bash class).
    MUT="$PYPLUG/scripts/context-handoff.py"
    _mutate "$PY" "$MUT" <<'MUTATE'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
old = ('    if val in ("claude-code", "claude", "claudecode"):\n'
       '        return "claude-code"\n')
if old not in text:
    sys.stderr.write("anchor not found: python claude alias row\n")
    raise SystemExit(1)
open(dst, "w", encoding="utf-8").write(text.replace(old, "", 1))
MUTATE
    PY="$MUT"
    ;;
  precedence)
    # Revert D4: ambient THING_HOST outranks the explicit --host again.
    # Must turn red: row 23.
    MUT="$PYPLUG/scripts/context-handoff.py"
    _mutate "$PY" "$MUT" <<'MUTATE'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
old = '    explicit = os.environ.get("RC_HOST") or os.environ.get("THING_HOST")'
new = '    explicit = os.environ.get("THING_HOST") or os.environ.get("RC_HOST")'
if old not in text:
    sys.stderr.write("anchor not found: detect_host precedence\n")
    raise SystemExit(1)
open(dst, "w", encoding="utf-8").write(text.replace(old, new, 1))
MUTATE
    PY="$MUT"
    ;;
esac

# ---- helpers --------------------------------------------------------------
BOUND=10    # seconds. The measured hang emits 0 bytes and never terminates;
            # every fixed path returns in well under 1 s.
PYBOUND=30  # python shells out to git (its own 8 s cap) before writing.

PRE=""      # optional `VAR=value` prefix applied INSIDE the bare env.

SP_RC=0; SP_OUT=""; SP_BYTES=0
spawn_run() {   # args are appended after --dry-run, so `spawn_run --host`
                # really does leave the flag as the FINAL argument.
  SP_OUT="$(_rc_timeout "$BOUND" env -i PATH=/usr/bin:/bin HOME="$HOME" ${PRE:+$PRE} \
            bash "$SPAWN" --task-id t1 --project-root "$REPO" --dry-run "$@" 2>&1)"
  SP_RC=$?
  SP_BYTES="$(printf '%s' "$SP_OUT" | wc -c | tr -d ' ')"
}

raw_run() {     # full argv, nothing appended.
  SP_OUT="$(_rc_timeout "$BOUND" env -i PATH=/usr/bin:/bin HOME="$HOME" \
            bash "$SPAWN" "$@" 2>&1)"
  SP_RC=$?
  SP_BYTES="$(printf '%s' "$SP_OUT" | wc -c | tr -d ' ')"
}

py_seed() {     # $1 = --host value; "" omits the flag entirely.
  rm -f "$REPO/.ravenclaude/runs/t1/handoff-seed.txt"
  if [ -z "$1" ]; then
    _rc_timeout "$PYBOUND" env -i PATH=/usr/bin:/bin HOME="$HOME" ${PRE:+$PRE} \
      python3 "$PY" write --task-id t1 --project-root "$REPO" >/dev/null 2>&1
  else
    _rc_timeout "$PYBOUND" env -i PATH=/usr/bin:/bin HOME="$HOME" ${PRE:+$PRE} \
      python3 "$PY" write --task-id t1 --project-root "$REPO" --host "$1" >/dev/null 2>&1
  fi
  cat "$REPO/.ravenclaude/runs/t1/handoff-seed.txt" 2>/dev/null
}

# Seed-class recognisers. ⛔ EVERY ONE IS A PRESENCE TEST (AC-6): an absence
# assertion alone ("no grok launch") passes identically against a writer that
# emitted NOTHING, which is exactly how a broken harness scores a free green.
#
# ⛔ Do NOT assert the bare substring `claude` on bash output: the copy-paste
# block prints `cd <repo>`, and any checkout under `.claude/` satisfies it no
# matter what the seed says. Gate 230 records that this exact false-pass was
# verified. Assert the recipe header, which only that branch emits.
#
# A grok LAUNCH is `grok "` or `grok -p`. Bare "grok" is not one — every safe
# seed says "Do not launch grok", and matching that would fire on its own remedy.
bash_class() {
  case "$1" in *'grok "'*|*'grok -p'*) echo grok; return ;; esac
  case "$1" in
    *'(Claude Code, not grok)'*) echo claude ;;
    *'(Copilot CLI, not grok)'*) echo cli ;;
    *'Copilot Chat resume'*) echo chat ;;
    *'NEW session of THIS host'*) echo neutral ;;
    *) echo none ;;
  esac
}

py_class() {
  case "$1" in *'grok "'*|*'grok -p'*) echo grok; return ;; esac
  case "$1" in
    *'claude  # then:'*) echo claude ;;
    *'copilot  # then:'*) echo cli ;;
    *'NEW Copilot Chat session'*) echo chat ;;
    *'Read the handoff at'*) echo neutral ;;
    *) echo none ;;
  esac
}

assert_has() { case "$2" in *"$3"*) ok "$1" ;; *) no "$1 — missing: $3" ;; esac; }

# One row = bash exit + bash BYTES>0 + bash class + python class. The BYTES>0
# assertion is on EVERY row on purpose: it is what separates "refused fast, block
# printed" from the hang's signature (EXIT=142 BYTES=0) and from an absent
# `timeout` (exit 127, nothing ran).
row() { # row N HOSTVALUE EXPECT_RC EXPECT_BASH_CLASS EXPECT_PY_CLASS
  local n="$1" h="$2" erc="$3" ebc="$4" epc="$5" bc pc s label
  label="row $n [${PRE:+$PRE }${h:-<no --host>}]"
  if [ -z "$h" ]; then spawn_run; else spawn_run --host "$h"; fi
  bc="$(bash_class "$SP_OUT")"
  if [ "$SP_RC" = "$erc" ]; then ok "$label bash exit=$erc"
  else no "$label bash exit=$SP_RC (want $erc)"; fi
  if [ "$SP_BYTES" -gt 0 ] 2>/dev/null; then ok "$label bash BYTES=$SP_BYTES > 0"
  else no "$label bash BYTES=0 — nothing was printed"; fi
  if [ "$bc" = "$ebc" ]; then ok "$label bash class=$ebc"
  else no "$label bash class=$bc (want $ebc)"; fi
  s="$(py_seed "$h")"
  pc="$(py_class "$s")"
  if [ "$pc" = "$epc" ]; then ok "$label py class=$epc"
  else no "$label py class=$pc (want $epc)"; fi
}

echo "Gate 234 — handoff --host contract (both writers, one vocabulary)"
echo "  spawn: $SPAWN"
echo "  py:    $PY"
[ -n "$MUST_FAIL" ] && echo "  MUST-FAIL HALF: $MUST_FAIL"

# ---- rows 1-23: the vocabulary, across both writers -----------------------
PRE=""
row 1  grok          0 grok    grok      # POSITIVE CONTROL — the harness can see a seed
row 2  GROK          0 grok    grok      # case parity (was: bash `unknown`)
row 3  claude-code   0 claude  claude    # the headline capability
row 4  claude        0 claude  claude    # alias parity (was: py neutral)
row 5  claudecode    0 claude  claude    # alias parity (was: py neutral)
row 6  CLAUDE-CODE   0 claude  claude    # case parity (was: bash `unknown`)
row 7  cli           0 cli     cli       # regression floor
row 8  CLI           0 cli     cli       # case parity
row 9  copilot       0 cli     cli       # alias, already agreed — kept as a control
row 10 chat          0 chat    chat      # regression floor
row 11 Chat          0 chat    chat      # case parity
row 12 codex         0 neutral neutral   # AC-1
row 13 cursor        0 neutral neutral   # AC-1
row 14 gemini        0 neutral neutral   # AC-1
row 15 aider         0 neutral neutral   # AC-1
row 16 windsurf      0 neutral neutral   # AC-1
row 17 other         0 neutral neutral   # the truthful value for an unlisted host
row 18 codxe         2 neutral neutral   # D2 + AC-2: block printed, THEN exit 2

# Row 19 — claims-table row 8. With CLAUDECODE set, `--host codex` used to print
# a CLAUDE CODE recipe, because detect_origin_host fell through to environment
# detection whenever the flag did not normalise to a recipe host.
PRE="CLAUDECODE=1"
row 19 codex         0 neutral neutral
# Control in the SAME environment: the flag is honoured, not merely disabled.
row 19b cli          0 cli     cli

# Row 20 — case (a). Deliberate overlap with Gates 215/230; see header (3).
PRE=""
row 20 ""            0 grok    grok

# Rows 21/22 — MED-7. `THING_HOST=gemini` with no flag emitted a LIVE grok
# launch, because the named-but-unknown test keyed on $host_flag only. ⛔ Every
# existing gate clears THING_HOST (`-u THING_HOST`, or `env -i`), which is
# correct hygiene for the flag rows and is exactly why no gate could see this.
# Row 22 is the AC-6 control: grok named through the same variable KEEPS its seed,
# so row 21 is measuring a choice and not a blanket suppression.
PRE="THING_HOST=gemini"
row 21 ""            0 neutral neutral
PRE="THING_HOST=grok"
row 22 ""            0 grok    grok

# Row 23 — D4. See header (5): AN INVARIANT, NOT A MEASURED LIVE FAILURE.
PRE="THING_HOST=copilot"
row 23 claude-code   0 claude  claude
PRE=""

# ---- rows 24-30: arity, bash-only, every one bounded ----------------------
# ⛔ `shift 2` when the flag is the LAST argument does not shift at all: bash
# reports "shift count out of range", $# never decreases, and the loop spins at
# 100% CPU forever. Measured 2026-08-19 through the DOCUMENTED shape
# (`rc handoff ... --host $H` with H empty): EXIT=142 BYTES=0 at a 5 s alarm;
# control with a value: EXIT=0 BYTES=443.
arity_row() { # arity_row N LABEL -- args...
  local n="$1" lbl="$2"; shift 3
  raw_run "$@"
  if [ "$SP_RC" = "2" ]; then ok "row $n $lbl exits 2"
  else no "row $n $lbl exit=$SP_RC (want 2) — a hang shows as 124/142 with BYTES=0"; fi
  if [ "$SP_BYTES" -gt 0 ] 2>/dev/null; then ok "row $n $lbl BYTES=$SP_BYTES > 0"
  else no "row $n $lbl BYTES=0 — hung, or the command never ran"; fi
}

# Rows 24-26 also assert the seed class is NEUTRAL, never grok: the naive shift
# fix converts the hang into a SILENT GROK SEED, which an exit-code-only
# assertion would not distinguish from the correct refusal.
arity_class_row() { # arity_class_row N LABEL -- args...
  local n="$1" lbl="$2"; shift 3
  arity_row "$n" "$lbl" -- "$@"
  local bc; bc="$(bash_class "$SP_OUT")"
  if [ "$bc" = "neutral" ]; then ok "row $n $lbl class=neutral (no grok launch)"
  else no "row $n $lbl class=$bc (want neutral) — a grok seed here is the silent-fallback defect"; fi
}

arity_class_row 24 "--host as the FINAL argument" -- \
  --task-id t1 --project-root "$REPO" --dry-run --host
arity_class_row 25 "--host '' (explicit empty)" -- \
  --task-id t1 --project-root "$REPO" --dry-run --host ''
arity_class_row 26 "--host --dry-run (MED-8 flag swallow)" -- \
  --task-id t1 --project-root "$REPO" --dry-run --host --dry-run

# Row 27 — ⛔ AC-5 POSITIVE CONTROL, in the SAME bounded harness. Without it, a
# harness that cannot run the script at all (absent `timeout` -> exit 127) scores
# a free green on every "exits non-zero" row above.
raw_run --task-id t1 --project-root "$REPO" --dry-run --host claude-code
if [ "$SP_RC" = "0" ] && [ "$SP_BYTES" -gt 0 ] 2>/dev/null; then
  ok "row 27 POSITIVE CONTROL: the bounded harness CAN run the script (exit 0, $SP_BYTES bytes)"
else
  no "row 27 POSITIVE CONTROL BROKEN: exit=$SP_RC bytes=$SP_BYTES — every arity row above is vacuous"
fi

# Rows 28/29 — the arity fix is not --host-only.
arity_row 28 "--task-id as the final argument" -- \
  --project-root "$REPO" --dry-run --task-id
arity_row 29a "--recipe as the final argument" -- \
  --task-id t1 --project-root "$REPO" --dry-run --recipe
arity_row 29b "--project-root as the final argument" -- \
  --task-id t1 --dry-run --project-root
arity_row 29c "--wait-ack-seconds as the final argument" -- \
  --task-id t1 --project-root "$REPO" --dry-run --wait-ack-seconds

# Row 30 — HIGH-2 second-order. ⛔ "Uniformising" --wait-ack-seconds to `${2:-}`
# would SILENTLY kill the successor-ack wait: `[ "$wait_ack" -gt 0 ] 2>/dev/null`
# is false on an empty string, so the handshake dies with no error at all.
if grep -q 'wait_ack=45' "$SPAWN"; then ok "row 30 --wait-ack-seconds default 45 is still in the source"
else no "row 30 wait_ack=45 default is GONE — the successor-ack wait can be silently skipped"; fi
raw_run --task-id t1 --project-root "$REPO" --dry-run --wait-ack-seconds 1
if [ "$SP_RC" = "0" ]; then ok "row 30 --wait-ack-seconds 1 still accepted (exit 0)"
else no "row 30 --wait-ack-seconds 1 exit=$SP_RC (want 0)"; fi

# ---- row 31: the duplicated registry table cannot drift silently ----------
# is_registry_host duplicates host-support.json as a bash literal ON PURPOSE —
# this script runs under `env -i PATH=/usr/bin:/bin` and may not shell out to
# python3/jq. This row is what stops the duplicate from rotting. It runs in the
# GATE process, which is not under env -i, so python3 is available here.
reg_cmp="$(python3 - "$SPAWN" "$HOSTS_JSON" <<'PY'
import json, re, sys
src = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"is_registry_host\(\)\s*\{\s*case[^\n]*\n\s*([^)]*)\)\s*return 0", src)
if not m:
    print("PARSE-FAIL"); raise SystemExit(0)
literal = set(p.strip() for p in m.group(1).split("|") if p.strip())
declared = set(json.load(open(sys.argv[2], encoding="utf-8"))["hosts"].keys())
print("MATCH" if literal == declared else
      "MISMATCH only-in-bash=%s only-in-json=%s" % (
          sorted(literal - declared), sorted(declared - literal)))
PY
)"
if [ "$reg_cmp" = "MATCH" ]; then
  ok "row 31 is_registry_host literal == host-support.json hosts (as sets)"
else
  no "row 31 registry literal drifted from host-support.json: $reg_cmp"
fi

# ---- rows 32/33: byte-exact regression floor for grok / cli / chat --------
# gap-delta row 10. Pinned as exact literal strings rather than a git diff: the
# children run under `env -i`, so a git-based baseline would need git inside
# them. A one-character change in an unrelated arm turns these red.
PRE=""
spawn_run --host grok
assert_has "row 32 grok seed is byte-exact" "$SP_OUT" \
'# copy-paste into a new terminal in this repo (same app as this session):
cd '"$REPO_Q"'
grok "Continue task t1 in this repo. Read .ravenclaude/runs/t1/handoff.md first (then meta.json, decisions.md, summary.md if present). Fresh window. Do not /fork. Do not /compact. Do not re-derive the brief from history you do not have. Execute the next steps in the brief."'

spawn_run --host cli
assert_has "row 33a cli copy-paste block is byte-exact" "$SP_OUT" \
'# copy-paste into a new terminal in this repo (Copilot CLI, not grok):
cd '"$REPO_Q"'
copilot
# then paste: Continue task t1. Read .ravenclaude/runs/t1/handoff.md first. Do not /fork. Do not launch grok.'

spawn_run --host chat
assert_has "row 33b chat copy-paste block is byte-exact" "$SP_OUT" \
'# Copilot Chat resume (same window, NEW session):
# 1. Cmd+N / Ctrl+N  (or Command Palette: "Chat: New Chat")
# 2. Paste the block below  OR  open chat-resume.md / handoff.md via @file
Read .ravenclaude/runs/t1/handoff.md first (then meta.json, decisions.md, summary.md if present). Fresh Chat session. Do not /fork. Do not launch grok. Execute the next steps in the brief.'

spawn_run --host claude-code
assert_has "row 33c claude-code copy-paste block is byte-exact" "$SP_OUT" \
'# copy-paste into a new terminal in this repo (Claude Code, not grok):
cd '"$REPO_Q"'
claude
# then paste: Continue task t1. Read .ravenclaude/runs/t1/handoff.md first. Fresh window — do not /fork, do not /compact, do not launch grok.'

# ---- row 34: syntax floor -------------------------------------------------
if bash -n "$SPAWN" 2>/dev/null; then ok "row 34 bash -n handoff-spawn.sh"
else no "row 34 bash -n handoff-spawn.sh FAILED"; fi
# ⛔ cfile into TMP, not `python3 -m py_compile`: the plain form writes a
# __pycache__ directory next to the source, i.e. INSIDE plugins/, every time the
# gate runs. A gate must not mutate the tree it is measuring.
if python3 -c 'import py_compile,sys; py_compile.compile(sys.argv[1], cfile=sys.argv[2], doraise=True)' \
     "$PY" "$TMP/context-handoff.pyc" 2>/dev/null; then
  ok "row 34 py_compile context-handoff.py"
else
  no "row 34 py_compile context-handoff.py FAILED"
fi

# ---- row 35: the D4 swap really did reach stamp_meta() -------------------
# stamp_meta() calls detect_host() independently of cmd_write(). Threading the
# resolved host through as a parameter would be a second mechanism for a fact one
# mechanism already carries — so this asserts the one mechanism reached it,
# rather than arguing that it must have.
rm -f "$REPO/.ravenclaude/runs/t1/meta.json"
PRE=""
py_seed claude-code >/dev/null 2>&1
meta_host="$(python3 -c 'import json,sys
try: print(json.load(open(sys.argv[1])).get("last_handoff_host",""))
except Exception: print("")' "$REPO/.ravenclaude/runs/t1/meta.json" 2>/dev/null)"
if [ "$meta_host" = "claude-code" ]; then
  ok "row 35 meta.json last_handoff_host == claude-code"
else
  no "row 35 meta.json last_handoff_host='$meta_host' (want claude-code)"
fi

# ---- verdict --------------------------------------------------------------
echo "  pass=$pass fail=$fail"

if [ -n "$MUST_FAIL" ]; then
  if [ "$fail" -gt 0 ]; then
    echo "Gate 234 must-fail half ($MUST_FAIL): mutant CAUGHT ($fail assertion(s) went red) — teeth confirmed"
    echo "  rows that went red:$FAILED"
    echo "  ⛔ Read that list. A must-fail half that goes green because a DIFFERENT"
    echo "     row broke is a false tooth (MED-6)."
    exit 0
  fi
  echo "Gate 234 must-fail half ($MUST_FAIL): MUTANT NOT CAUGHT — the assertions do not measure the property" >&2
  exit 1
fi

if [ "$fail" -gt 0 ]; then
  echo "Gate 234 FAILED"
  echo "  rows that went red:$FAILED"
  exit 1
fi
echo "Gate 234 PASSED"
exit 0
