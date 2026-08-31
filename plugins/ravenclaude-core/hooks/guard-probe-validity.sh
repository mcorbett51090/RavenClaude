#!/usr/bin/env bash
#
# guard-probe-validity.sh — PreToolUse(Bash). ONE rule. WARN only.
#
# rc-state-key: none — this hook is PURE. It reads the command string and the
#   comfort-posture knob, and nothing else. No cache, no registry, no probe.
# rc-state-scope: n/a
# rc-state-rationale: a validity advisory needs no cross-invocation state; the
#   only durable artifact is the optional hook-event audit line.
# rc-state-escape: comfort-posture — `probe_validity: off` silences it.
#   An ABSENT posture file is a no-op (opt-in, like the other advisory hooks).
#
# ─────────────────────────────────────────────────────────────────────────────
# THE RULE (the only one this hook implements)
# ─────────────────────────────────────────────────────────────────────────────
# Detect `grep -v` used in QUIET MODE.
#
# `grep -v` normally answers "is there a line that does NOT match?" — its exit
# status is 0 when at least one line was SELECTED. In quiet mode that guarantee
# is lost: the status starts reporting whether the PATTERN is ABSENT from the
# input. The two questions disagree on any input holding BOTH a matching and a
# non-matching line — and the disagreement reads as CLEAN.
#
# Quiet mode is entered TWO ways, and the second is the one nobody expects:
#   1. -q / --quiet / --silent, including inside a bundled cluster
#      (-qv, -vq, -rqv, -qvE).
#   2. stdout redirected to /dev/null SPECIFICALLY — not a regular file, not a
#      pipe. So `grep -v X f >/dev/null` is affected with NO -q anywhere.
#
# Measured 2026-08-18 in the agent's own Bash-tool shell (ugrep 7.5.0), on a
# fixture holding BOTH a matching and a non-matching line:
#
#     grep -v alpha mixed.txt >/dev/null   -> rc=1   (BSD/GNU give 0)
#     grep -qv alpha mixed.txt             -> rc=1
#
# Measured yield: across 17,410 distinct real agent-issued Bash commands (43
# transcripts) this rule fires ONCE — and that catch was real: a PR ALL_GREEN
# verdict decided by `grep -qvE`. One fire in 17,410 is the point. This is a
# rare, high-consequence shape, not a style nag, and it is the ONLY rule here.
# Two sibling candidates were measured on the same corpus and rejected:
# `find -exec test` fired 0 times ever, and `$?`-after-a-pipe fired 13 times at
# an 85% false-positive rate. Do not add them. A channel that is wrong 85% of
# the time is how an agent learns to stop reading the channel.
#
# ─────────────────────────────────────────────────────────────────────────────
# ⛔ WHY THIS IS WARN-ONLY, AND WHY YOU MUST NOT "IMPROVE" IT WITH A HOST PROBE
# ─────────────────────────────────────────────────────────────────────────────
# Two earlier designs proposed deciding WARN-vs-DENY from a host probe: run
# `grep -q -v` against a two-line fixture, and deny only on a host where it
# inverts. Both were overturned, for a mechanical reason that is easy to
# re-introduce and very hard to see afterwards:
#
#     The probe would run in the HOOK's shell.
#     The judged command runs in the AGENT's shell.
#     They are not the same grep.
#
# Measured on one machine at one instant: the agent's Bash tool resolves `grep`
# to a shell function that execs under ARGV0=ugrep (ugrep 7.5.0 — INVERTS),
# while a hook subprocess — /bin/sh -c, or even `env -i /bin/bash -c` — resolves
# plain BSD grep 2.6.0 (does NOT invert). So on the exact machine where the
# defect is real and documented, a hook-side probe answers "this host is fine"
# and the DENY branch is unreachable, on every host, forever.
#
# Worse, it is TESTABLE-GREEN. A test that fakes the probe result "proves" the
# DENY branch reachable over a rule that is dead in the live path — a green test
# over a dead rule, which is precisely the vacuity class this hook exists to
# catch. And it errs the other way too: the hook would report CLEAN a command
# whose ugrep execution is genuinely inverted.
#
# Caching the probe does not rescue it. The same shell delegates to BSD grep
# whenever an argument matches -Z / --null / -z / -@, so `grep --version` and
# `grep --null --version` print DIFFERENT products from the same word in the
# same shell: same cache key, opposite answer. And computing that key costs more
# (two forks, ~7.6 ms) than the live probe it caches (one fork, ~4.1 ms).
#
# So: NO host probe, and NO deny branch. The idiom is fragile on every
# implementation and actively wrong on ugrep; an unconditional warn is correct
# advice everywhere, costs nothing at ~1-in-17,410, and removes the entire
# wrong-shell failure mode BY CONSTRUCTION rather than by vigilance. Adding a
# probe "for accuracy" does not make this hook more accurate — it makes the
# accurate branch unreachable and hides that behind a passing test.
#
# There is no exit-2 path in this file. A warn is exit 0 + stderr, and an EXIT
# trap armed before anything else pins every error path to 0.
#
# ─────────────────────────────────────────────────────────────────────────────
# Portability: bash 3.2 / BSD-safe. No declare -A, no mapfile, no ${x^^}, no
# globstar, no GNU timeout, no grep -P, no sed -i. `sed` appears only with
# literal-character replacements (BSD sed does not expand \n in a replacement —
# that trap is why segment splitting uses tr, not sed).
# ⛔ This file must never itself use `grep -q -v`: that is the defect, and it
# inverts here. The matching below is done with bash's own [[ =~ ]], which forks
# nothing and cannot be affected by whichever grep is on PATH.
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail

# Fail-safe FIRST: whatever happens below, this hook exits 0. It never blocks.
# ── ADVISORY DELIVERY (added 2026-08-19) ────────────────────────────────────
# ⛔ PreToolUse + stderr + exit 0 is MEASURED UNDELIVERED to the model (matched
# trial, hook confirmed fired, positive control arrived — see _advise.sh header).
# This hook's ONE rule fires roughly once in 17,410 commands; when it finally does,
# the warning has been going to the terminal and not to the model.
#
# rc_advise_init installs its OWN EXIT trap, so it REPLACES the `trap 'exit 0' EXIT`
# that used to sit on this line. The forced-exit argument (0) reproduces this hook's
# always-exit-0 fail-safe contract EXACTLY; the else-branch keeps that contract if
# the helper is ever missing.
_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
if [ -f "$_rc_hd/_advise.sh" ]; then . "$_rc_hd/_advise.sh"; rc_advise_init PreToolUse 0; else trap 'exit 0' EXIT; fi

# ── sourced helper (fail-safe: stub if absent) ───────────────────────────────
_pv_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
# shellcheck source=/dev/null
[ -f "$_pv_script_dir/_emit-event.sh" ] && . "$_pv_script_dir/_emit-event.sh" 2>/dev/null || true
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

# ── payload ──────────────────────────────────────────────────────────────────
payload=""
[ ! -t 0 ] && payload="$(cat 2>/dev/null || printf '')"
[ -n "$payload" ] || exit 0

tool_name=""
cmd=""
cwd=""
if command -v jq >/dev/null 2>&1; then
  tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // empty' 2>/dev/null || printf '')"
  cmd="$(printf '%s' "$payload" | jq -r '(.tool_input.command // "") | gsub("\n"; " ")' 2>/dev/null || printf '')"
  cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null || printf '')"
elif command -v python3 >/dev/null 2>&1; then
  # One interpreter start, three fields, newline-separated. Any parse failure
  # yields empty strings, which the guards below turn into a no-op.
  _pv_parsed="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
if not isinstance(d, dict):
    d = {}
ti = d.get("tool_input") or {}
if not isinstance(ti, dict):
    ti = {}


def s(v):
    return v if isinstance(v, str) else ""


print(s(d.get("tool_name")))
print(s(ti.get("command")).replace("\n", " "))
print(s(d.get("cwd")))
' 2>/dev/null || printf '')"
  tool_name="$(printf '%s\n' "$_pv_parsed" | sed -n '1p')"
  cmd="$(printf '%s\n' "$_pv_parsed" | sed -n '2p')"
  cwd="$(printf '%s\n' "$_pv_parsed" | sed -n '3p')"
else
  exit 0 # no JSON parser on this host -> fail open
fi

[ "$tool_name" = "Bash" ] || exit 0
[ -n "$cmd" ] || exit 0

# Cheapest possible prefilter: no grep-family word anywhere, no opinion. This is
# a shell `case`, so the overwhelming majority of commands cost zero forks and
# zero regex work.
case "$cmd" in
  *grep*) ;;
  *) exit 0 ;;
esac

# ── knob: probe_validity: off | warn   (DEFAULT warn; absent FILE => no-op) ───
[ -n "$cwd" ] || cwd="${CLAUDE_PROJECT_DIR:-$PWD}"
posture="${cwd}/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0 # opt-in: no posture file, no opinion

mode="$(sed -n 's/^[[:space:]]*probe_validity:[[:space:]]*\([A-Za-z]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
[ -z "$mode" ] && mode="warn"
case "$mode" in
  off | warn) ;;
  *) mode="warn" ;;
esac
[ "$mode" = "off" ] && exit 0

# ── detection ────────────────────────────────────────────────────────────────
# Split into pipeline/list segments so a redirect is attributed to the segment
# that owns it: `grep -v X f | wc -l` is NOT quiet (its stdout goes to the pipe),
# while `grep -v X f >/dev/null` is. Segmenting is also what keeps a `-v` on one
# command from being read as a flag of a `grep` on another.
#
# `&&` and `||` fold to `;` via a LITERAL-character sed replacement, then `;`
# and `|` become newlines via tr. A bare `&` is deliberately NOT a separator, so
# `2>&1` and `&>/dev/null` stay attached to the command that owns them.
segments="$(printf '%s' "$cmd" | sed -e 's/&&/;/g' -e 's/||/;/g' | tr ';|' '\n\n')"

# A grep-family command word: start-of-segment, whitespace, or a path slash,
# then an optional family letter. Deliberately does NOT match `rg`/`ripgrep`
# (ripgrep has no such divergence), `pgrep`, or a `--grep` option.
_PV_GREP_RE='(^|[[:space:]]|/)(u|e|f|g|z)?grep([[:space:]]|$)'
# A single-dash cluster containing v (-v, -qv, -vq, -rqv, -qvE), or the long form.
_PV_INVERT_RE='(^|[[:space:]])(-[A-Za-z]*v[A-Za-z]*|--invert-match)([[:space:]=]|$)'
# Quiet FLAG: a single-dash cluster containing q, or the long forms.
_PV_QFLAG_RE='(^|[[:space:]])(-[A-Za-z]*q[A-Za-z]*|--quiet|--silent)([[:space:]]|$)'
# Quiet REDIRECT: fd 1 to /dev/null. The `[^0-9]` before `>` is what excludes
# `2>/dev/null` (stderr — harmless); the second alternative covers explicit `1>`.
_PV_DEVNULL_RE='(^|[^0-9])>>?[[:space:]]*/dev/null|(^|[[:space:]])1>>?[[:space:]]*/dev/null'

fired=0
why=""
matched=""

# bash 3.2: no mapfile. A here-string keeps the loop body in THIS shell, so the
# flags set inside it survive (a `... | while read` subshell would lose them).
while IFS= read -r seg; do
  [ -n "$seg" ] || continue
  [[ $seg =~ $_PV_GREP_RE ]] || continue
  [[ $seg =~ $_PV_INVERT_RE ]] || continue

  seg_why=""
  if [[ $seg =~ $_PV_QFLAG_RE ]]; then
    seg_why="-q / --quiet / --silent (it may be buried in a bundled cluster such as -qv, -vq, -rqv)"
  elif [[ $seg =~ $_PV_DEVNULL_RE ]]; then
    seg_why="stdout redirected to /dev/null — no -q required; this is the form nobody expects"
  fi

  [ -n "$seg_why" ] || continue
  fired=1
  [ -n "$why" ] || why="$seg_why"
  if [ -z "$matched" ]; then
    matched="$(printf '%s' "$seg" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | cut -c1-160)"
  fi
done <<<"$segments"

[ "$fired" -eq 1 ] || exit 0

# ── warn (exit 0 + stderr; there is no other verdict in this hook) ───────────
{
  echo "[probe-validity] WARNING: \`grep -v\` in QUIET MODE — its exit status is not answering the question it looks like it is answering."
  echo "  segment:  $matched"
  echo "  quiet by: $why"
  echo
  echo "  Outside quiet mode, \`grep -v\` exits 0 when a line was SELECTED (\"something does NOT match\")."
  echo "  In quiet mode that guarantee is lost — the status starts reporting whether the PATTERN is ABSENT."
  echo "  The two disagree on any input holding BOTH a matching and a non-matching line, and the"
  echo "  disagreement reads as CLEAN. Measured here (ugrep 7.5.0, genuinely mixed fixture):"
  echo "      grep -v alpha mixed.txt >/dev/null   ->  rc=1   (BSD/GNU give 0)"
  echo "  A real PR ALL_GREEN verdict was decided by exactly this shape."
  echo
  echo "  Fix: do not read the status — read a COUNT, which every implementation agrees on."
  echo "      total=\$(awk 'END{print NR}' f); hits=\$(grep -c -E 'pat' f)"
  echo "      [ \"\$hits\" -lt \"\$total\" ] && echo 'a non-matching line exists'"
  echo
  echo "  Advisory only — this hook never blocks and has no deny path. Silence it with"
  echo "  \`probe_validity: off\` in .ravenclaude/comfort-posture.yaml."
} >&2

_emit_hook_event "guard-probe-validity.sh" "warn" "Bash" "" "pv.grep-v-quiet" "0" 2>/dev/null || true

exit 0
