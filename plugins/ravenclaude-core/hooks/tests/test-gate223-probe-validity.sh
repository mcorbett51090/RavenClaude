#!/usr/bin/env bash
# Gate 223 — guard-probe-validity.sh · rule pv.grep-v-quiet
#
# Proves the ONE rule: `grep -v` in QUIET MODE. Quiet is entered two ways —
# a -q/--quiet/--silent flag (including inside a bundled cluster), and stdout
# redirected to /dev/null SPECIFICALLY (no -q required, and that is the form
# nobody expects). Both must fire; every legitimate neighbouring form must stay
# silent; and NOTHING may ever exit non-zero, because this hook has no deny path.
#
# ⛔ THE HARNESS HAS AN EXIT-CODE CONTRACT, AND THE SUITE PROVES IT.
# The 5-rule prototype this rule was extracted from shipped a runner that exited
# 0 whether 11 assertions failed or none did — a gate that is green forever. So
# this script exits 1 on any failure, AND ships `--prove-nonzero`, which routes a
# deliberately FALSE assertion through the real assertion path. Gate 223 asserts
# must_fail on that invocation, which means "the harness reddens" is re-checked
# on every CI run rather than being a claim someone once made in a commit message.
#
# ⛔ THE MIXED FIXTURE. ugrep and BSD/GNU AGREE unless the input holds BOTH a
# matching and a non-matching line — 2 of the 3 plausible fixtures (all-match,
# none-match) report "no bug" and silently prove nothing. The fixture's
# mixedness is therefore asserted here as a first-class, count-based fact.
#
# ⛔ NO HOST PROBE, and this test asserts NO divergence. The hook warns
# unconditionally and the reason is in its header: a probe run from a hook
# measures the hook's grep, while the judged command runs under the agent's
# grep. Asserting a divergence here would be asserting a property of the CI
# runner's grep, which is not the shell the defect lives in.
#
# ⛔ This file must never USE `grep -q -v` — that is the defect under test and
# it inverts. Every assertion below is count-based. The bad forms appear only as
# command STRINGS handed to the hook as data; none of them is executed.
#
# Invoked via `bash "$HOOK"`, so it passes regardless of the hook's executable
# bit — a property of THIS HARNESS, not of the shipped hook. Production
# (direct-exec) and CI's executability step do require the bit.
#
# bash 3.2 safe. No GNU-only tools, no sed -i, no grep -P.
set -uo pipefail

HOOK="$(cd "$(dirname "$0")/.." && pwd)/guard-probe-validity.sh"
fails=0

T="$(mktemp -d)"
PROJ="$T/proj"
mkdir -p "$PROJ/.ravenclaude" # a project WITH a posture file
BARE="$T/bare"
mkdir -p "$BARE" # a project with NO posture file

cleanup() { rm -rf "$T"; }
trap cleanup EXIT

_mkpayload() { # $1 = command string  (no .cwd -> hook falls back to CLAUDE_PROJECT_DIR)
  python3 -c 'import json,sys
print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1"
}

_set_mode() { printf 'probe_validity: %s\n' "$1" >"$PROJ/.ravenclaude/comfort-posture.yaml"; }
_clear_mode() { printf 'schema_version: 5\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"; }

last_exit=0
_run() { # $1=hook $2=projectdir $3=command
  printf '%s' "$(_mkpayload "$3")" | CLAUDE_PROJECT_DIR="$2" bash "$1" >/dev/null 2>"$T/err"
  last_exit=$?
}

# Count-based: how many stderr lines carry the hook's banner token.
# ⛔ `grep -c` PRINTS 0 and EXITS 1 when nothing matches, so a `|| printf 0`
# fallback emits "0\n0" and every downstream [ ] test dies with "integer
# expression expected" — which is a broken probe, not a finding. Take the
# output, ignore the status, and default only when the output is EMPTY.
_warn_lines() {
  local n
  n="$(grep -c '\[probe-validity\]' "$T/err" 2>/dev/null)"
  case "$n" in
    '' | *[!0-9]*) n=0 ;;
  esac
  printf '%s' "$n"
}

_assert_fires() { # $1=label
  local n
  n="$(_warn_lines)"
  if [ "$last_exit" = "0" ] && [ "$n" -ge 1 ]; then
    printf '  ok   FIRES   %-58s (exit 0, %s banner line)\n' "$1" "$n"
  else
    printf '  FAIL FIRES   %-58s exit=%s banners=%s\n' "$1" "$last_exit" "$n"
    fails=$((fails + 1))
  fi
}

_assert_silent() { # $1=label
  local n
  n="$(_warn_lines)"
  if [ "$last_exit" = "0" ] && [ "$n" -eq 0 ]; then
    printf '  ok   SILENT  %-58s (exit 0, no banner)\n' "$1"
  else
    printf '  FAIL SILENT  %-58s exit=%s banners=%s err=[%s]\n' \
      "$1" "$last_exit" "$n" "$(cat "$T/err" 2>/dev/null | head -2)"
    fails=$((fails + 1))
  fi
}

echo "Gate 223 — guard-probe-validity (pv.grep-v-quiet)"

# ─────────────────────────────────────────────────────────────────────────────
# 0. The fixture is genuinely MIXED — asserted, not assumed.
#    Counted with awk + `grep -c`. No -v and no -q are used to establish this,
#    so the measurement cannot be distorted by the very defect under test.
# ─────────────────────────────────────────────────────────────────────────────
printf 'alpha one\nbeta two\nalpha three\ngamma four\n' >"$T/mixed.txt"
_total="$(awk 'END{print NR}' "$T/mixed.txt")"
_hits="$(grep -c 'alpha' "$T/mixed.txt" 2>/dev/null)"
case "$_hits" in
  '' | *[!0-9]*) _hits=0 ;;
esac
if [ "$_hits" -ge 1 ] && [ "$_hits" -lt "$_total" ]; then
  printf '  ok   FIXTURE %-58s (%s of %s lines match — genuinely mixed)\n' \
    "mixed.txt has BOTH matching and non-matching lines" "$_hits" "$_total"
else
  printf '  FAIL FIXTURE %-58s hits=%s total=%s — an all-match or none-match fixture\n' \
    "mixed.txt is NOT mixed" "$_hits" "$_total"
  printf '       makes ugrep and BSD agree, so a divergence test over it proves NOTHING.\n'
  fails=$((fails + 1))
fi

# ─────────────────────────────────────────────────────────────────────────────
# 1. FIRES — quiet via a -q FLAG (incl. bundled clusters)
# ─────────────────────────────────────────────────────────────────────────────
_set_mode warn
echo
echo "  -- fires: quiet by flag --"

_run "$HOOK" "$PROJ" 'grep -qv alpha mixed.txt'
_assert_fires "-qv cluster"

_run "$HOOK" "$PROJ" 'grep -vq alpha mixed.txt'
_assert_fires "-vq cluster (order reversed)"

_run "$HOOK" "$PROJ" 'grep -rqv alpha .'
_assert_fires "-rqv cluster (three letters)"

_run "$HOOK" "$PROJ" 'grep -q -v alpha mixed.txt'
_assert_fires "separated -q -v"

_run "$HOOK" "$PROJ" 'grep --quiet --invert-match alpha mixed.txt'
_assert_fires "--quiet --invert-match long forms"

_run "$HOOK" "$PROJ" 'grep --silent -v alpha mixed.txt'
_assert_fires "--silent with -v"

_run "$HOOK" "$PROJ" 'egrep -qv alpha mixed.txt'
_assert_fires "egrep family"

_run "$HOOK" "$PROJ" '/usr/bin/grep -qv alpha mixed.txt'
_assert_fires "absolute path to grep"

# The single real catch from the 17,410-command corpus: a PR ALL_GREEN verdict
# decided by the inverted form.
_run "$HOOK" "$PROJ" "gh pr checks 967 --repo mcorbett51090/RavenClaude --json state --jq '.[].state' 2>/dev/null | grep -qvE 'SUCCESS|SKIPPED|NEUTRAL'"
_assert_fires "the real corpus catch (gh pr checks | grep -qvE)"

# ─────────────────────────────────────────────────────────────────────────────
# 2. FIRES — quiet via >/dev/null, with NO -q anywhere. The surprising half.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- fires: quiet by >/dev/null, no -q present --"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt >/dev/null'
_assert_fires ">/dev/null, no -q"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt > /dev/null'
_assert_fires "> /dev/null with a space"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt >/dev/null 2>&1'
_assert_fires ">/dev/null 2>&1"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt >>/dev/null'
_assert_fires ">>/dev/null (append)"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt 1>/dev/null'
_assert_fires "explicit 1>/dev/null"

_run "$HOOK" "$PROJ" 'cat mixed.txt | grep -v alpha >/dev/null'
_assert_fires "downstream of a pipe, redirected to /dev/null"

# ─────────────────────────────────────────────────────────────────────────────
# 3. SILENT — every legitimate neighbouring form
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- silent: legitimate forms --"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt'
_assert_silent "plain grep -v to stdout (the CORRECT idiom)"

_run "$HOOK" "$PROJ" 'grep -q alpha mixed.txt'
_assert_silent "grep -q without -v"

_run "$HOOK" "$PROJ" 'grep -q alpha mixed.txt >/dev/null'
_assert_silent "grep -q >/dev/null, still no -v"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt > out.txt'
_assert_silent "redirected to a REGULAR FILE (not quiet)"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt > /tmp/real-file.txt'
_assert_silent "redirected to an absolute regular file"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt 2>/dev/null'
_assert_silent "only STDERR to /dev/null (harmless)"

_run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt | wc -l'
_assert_silent "piped downstream (not quiet)"

_run "$HOOK" "$PROJ" 'grep -c -v alpha mixed.txt'
_assert_silent "counting with -c (this IS the recommended fix)"

_run "$HOOK" "$PROJ" 'rg -qv alpha .'
_assert_silent "ripgrep (rg) — different tool, no divergence"

_run "$HOOK" "$PROJ" 'pgrep -q claude'
_assert_silent "pgrep is not a grep-family name"

_run "$HOOK" "$PROJ" 'git log --grep=fix -v --oneline'
_assert_silent "git log --grep is an option, not a grep invocation"

_run "$HOOK" "$PROJ" 'ls -la'
_assert_silent "a command with no grep at all"

_run "$HOOK" "$PROJ" 'grep -q alpha a.txt && grep -v beta b.txt'
_assert_silent "-q and -v on DIFFERENT commands in one line"

# ─────────────────────────────────────────────────────────────────────────────
# 4. Knob + opt-in behaviour
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- knob --"

_set_mode off
_run "$HOOK" "$PROJ" 'grep -qv alpha mixed.txt'
_assert_silent "probe_validity: off silences the fire case"

_clear_mode
_run "$HOOK" "$PROJ" 'grep -qv alpha mixed.txt'
_assert_fires "knob ABSENT from an existing posture file defaults to warn"

_run "$HOOK" "$BARE" 'grep -qv alpha mixed.txt'
_assert_silent "ABSENT posture file is a no-op (opt-in)"

# ─────────────────────────────────────────────────────────────────────────────
# 5. There is no deny path — the exit code is 0 even on the loudest input.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- no deny path --"
_set_mode warn
_run "$HOOK" "$PROJ" 'grep -qv a x >/dev/null; grep -vq b y >/dev/null'
if [ "$last_exit" = "0" ]; then
  printf '  ok   NODENY  %-58s (exit 0)\n' "two fire-shaped segments still exit 0, never 2"
else
  printf '  FAIL NODENY  %-58s exit=%s (a deny path exists — it must not)\n' \
    "two fire-shaped segments" "$last_exit"
  fails=$((fails + 1))
fi

# ─────────────────────────────────────────────────────────────────────────────
# 6. TEETH — two mutants. Without these, the FIRES block would print identically
#    if the hook simply warned on anything containing the word "grep".
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- teeth (mutants) --"

_mutate() { # $1=out path  $2=python replacement pair marker
  python3 - "$HOOK" "$1" "$2" <<'MUTPY'
import sys
src = open(sys.argv[1], encoding="utf-8").read()
which = sys.argv[3]
if which == "quiet":
    anchors = ["_PV_QFLAG_RE='", "_PV_DEVNULL_RE='"]
else:
    anchors = ["_PV_INVERT_RE='"]
out = []
changed = 0
for line in src.split("\n"):
    hit = False
    for a in anchors:
        if line.startswith(a):
            hit = True
            break
    if hit:
        name = line.split("=", 1)[0]
        out.append(name + "='(^|X)ZZ_NEVER_MATCHES_ZZ($|X)'")
        changed += 1
    else:
        out.append(line)
# Refuse to write an unmutated copy: an unmutated copy passes its own test and
# the gate would report teeth it does not have.
assert changed == len(anchors), (
    "mutator anchors stopped matching (%d of %d) — refusing to write an "
    "unmutated copy" % (changed, len(anchors))
)
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
MUTPY
}

_set_mode warn

MUT_Q="$T/mutant-quiet.sh"
if _mutate "$MUT_Q" quiet 2>"$T/muterr"; then
  _run "$MUT_Q" "$PROJ" 'grep -qv alpha mixed.txt'
  _q1="$(_warn_lines)"
  _run "$MUT_Q" "$PROJ" 'grep -v alpha mixed.txt >/dev/null'
  _q2="$(_warn_lines)"
  if [ "$_q1" -eq 0 ] && [ "$_q2" -eq 0 ]; then
    printf '  ok   TEETH   %-58s (both fire cases go silent)\n' "neutering QUIET detection kills the catches"
  else
    printf '  FAIL TEETH   %-58s -qv=%s devnull=%s — the FIRES block is not\n' \
      "neutering QUIET detection" "$_q1" "$_q2"
    printf '       measuring the quiet detector.\n'
    fails=$((fails + 1))
  fi
else
  printf '  FAIL TEETH   %-58s %s\n' "quiet mutator refused to build" "$(head -3 "$T/muterr" | tr '\n' ' ')"
  fails=$((fails + 1))
fi

MUT_V="$T/mutant-invert.sh"
if _mutate "$MUT_V" invert 2>"$T/muterr"; then
  _run "$MUT_V" "$PROJ" 'grep -qv alpha mixed.txt'
  _v1="$(_warn_lines)"
  if [ "$_v1" -eq 0 ]; then
    printf '  ok   TEETH   %-58s (fire case goes silent)\n' "neutering INVERT detection kills the catch"
  else
    printf '  FAIL TEETH   %-58s banners=%s — -v is not load-bearing.\n' \
      "neutering INVERT detection" "$_v1"
    fails=$((fails + 1))
  fi
else
  printf '  FAIL TEETH   %-58s %s\n' "invert mutator refused to build" "$(head -3 "$T/muterr" | tr '\n' ' ')"
  fails=$((fails + 1))
fi

# ─────────────────────────────────────────────────────────────────────────────
# 7. --prove-nonzero: route a deliberately FALSE claim through the real
#    assertion path, so the SUITE can prove this harness actually reddens.
#    (Gate 223 asserts must_fail on this invocation.)
# ─────────────────────────────────────────────────────────────────────────────
if [ "${1:-}" = "--prove-nonzero" ]; then
  echo
  echo "  -- --prove-nonzero: the assertion below is MEANT to fail --"
  _run "$HOOK" "$PROJ" 'grep -v alpha mixed.txt'
  _assert_fires "SELF-BREAK: plain 'grep -v' must NOT fire, so this must redden"
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "Gate 223 PASS"
  exit 0
else
  echo "Gate 223 FAIL ($fails)"
  exit 1
fi
