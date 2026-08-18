#!/usr/bin/env bash
# Gate 227 — the handoff seed must name the host it is handing off TO.
#
# WHY THIS GATE EXISTS. Both seed writers defaulted to the grok launch command
# and overrode it only for hosts they recognised by name, so every host they did
# NOT recognise inherited a command that starts a different agent:
#
#   handoff-spawn.sh   `seed=grok "…"` was set ~90 lines before the host was
#                      resolved; only chat / cli / (unknown + TERM_PROGRAM=vscode)
#                      overrode it. Its refusal guard was scoped to chat|cli, so
#                      it could not see the case it most needed to catch.
#   context-handoff.py seed_text()'s fall-through default WAS the grok seed, so
#                      claude-code / codex / unknown / "" all received it.
#
# Measured 2026-08-18 against the shipped 0.271.4 copy: `--host claude-code` in a
# plain terminal emitted `grok "…"`; the SAME invocation under TERM_PROGRAM=vscode
# emitted a safe comment. That asymmetry is why the defect reads as absent when
# you sample only a VS Code session, and it is why this gate drives a bare
# environment (`env -i`) rather than inheriting whatever the runner happens to set.
#
# ⛔ HONEST SCOPE. This gate asserts the SEED VALUE each writer selects per host,
# on the copy-paste/dry-run surface. It does NOT drive a live spawn: exercising
# handoff-spawn.sh's launch-successor branch end-to-end would start a real
# interactive agent, which is not something a CI gate may do. That branch is
# covered only insofar as it consumes the same `$seed` this gate pins, plus the
# no-recipe host now writing an `exit 0` launcher instead of `exec $seed`.
#
# POSITIVE CONTROL IS BUILT IN. The gate asserts grok DOES get the grok seed. A
# blanket "no grok anywhere" assertion would pass just as well against a writer
# that emitted nothing at all, so the grok row is what proves the other rows are
# measuring a choice rather than an absence.
#
# bash 3.2-safe. No GNU-only tools.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/../.." && pwd)"
SPAWN="$PLUGIN_ROOT/scripts/handoff-spawn.sh"
PY="$PLUGIN_ROOT/scripts/context-handoff.py"

MUST_FAIL=0
if [ "${1:-}" = "--must-fail-spawn-default" ]; then
  MUST_FAIL=1
fi

pass=0
fail=0
ok() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
no() { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; }

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t gate227)"
cleanup() { [ -n "${TMP:-}" ] && [ -d "$TMP" ] && rm -rf "$TMP"; }
trap cleanup EXIT

REPO="$TMP/repo"
mkdir -p "$REPO/.ravenclaude/runs/t1"
printf 'brief\n' > "$REPO/.ravenclaude/runs/t1/handoff.md"

# ---- must-fail half -------------------------------------------------------
# Rebuild the defect exactly: restore the unconditional grok default AND neuter
# the non-grok refusal. If the assertions below still come out green against
# that, they are not measuring the seed and the gate is decorative.
if [ "$MUST_FAIL" -eq 1 ]; then
  MUT="$TMP/mutant-spawn.sh"
  # Rebuild the PRE-FIX file: strip claude-code from normalize_host AND from
  # detect_origin_host, drop its seed branch, drop the named-but-unknown branch,
  # and neuter the refusal guard. Every one of those is required — leave the
  # claude-code branch in and the mutant still handles the headline case, so the
  # gate would go red on `codex` alone and understate the teeth for exactly the
  # host that was reported. The grok default itself is NOT reverted here: it is
  # the ORIGINAL behaviour and is deliberately retained (case (a) above).
  # Exact-string replacement in python, not sed: these anchors carry `${...}`,
  # `$var`, and brace-grouped conditionals, which turn BRE quoting into a
  # guessing game. A mutant that silently half-applies is worse than none — it
  # would report teeth it does not have. This refuses unless all five land.
  python3 - "$SPAWN" "$MUT" <<'MUTATE' || {
import sys

src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()

edits = [
    # normalize_host no longer knows the name
    ('    claude-code|claude|claudecode) echo claude-code ;;\n', ''),
    # detect_origin_host no longer sniffs for it either
    ('  if [ -n "${CLAUDECODE:-}" ] || [ -n "${CLAUDE_CODE_ENTRYPOINT:-}" ]; then',
     '  if false; then'),
    # no claude-code seed
    ('elif [ "$host" = "claude-code" ]; then', 'elif false; then'),
    # a NAMED unknown host falls back to grok again — the defect itself
    ('elif [ "$named_but_unknown" -eq 1 ]; then', 'elif false; then'),
    # and the refusal guard cannot see it
    ('if [ "$host" != "grok" ] && { [ "$host" != "unknown" ] '
     '|| [ "$named_but_unknown" -eq 1 ]; }; then', 'if false; then'),
]

for old, new in edits:
    if old not in text:
        sys.stderr.write("anchor not found: %r\n" % old[:60])
        raise SystemExit(1)
    text = text.replace(old, new, 1)

open(dst, "w", encoding="utf-8").write(text)
MUTATE
    echo "must-fail half: could not rebuild the defect (an anchor moved)" >&2
    echo "  fix the mutant to match the current source, not the gate" >&2
    exit 1
  }
  SPAWN="$MUT"
fi

# ---- helpers --------------------------------------------------------------
spawn_out() {
  # $1 = --host value ("" omits the flag). Bare env: the vscode-only override
  # must not be able to mask a defect, and the runner's env must not leak in.
  if [ -z "$1" ]; then
    env -i PATH=/usr/bin:/bin HOME="$HOME" ${2:+"$2"} \
      bash "$SPAWN" --task-id t1 --project-root "$REPO" --dry-run 2>&1
  else
    env -i PATH=/usr/bin:/bin HOME="$HOME" ${2:+"$2"} \
      bash "$SPAWN" --task-id t1 --host "$1" --project-root "$REPO" --dry-run 2>&1
  fi
}

py_seed() {
  rm -f "$REPO/.ravenclaude/runs/t1/handoff-seed.txt"
  env -i PATH=/usr/bin:/bin HOME="$HOME" \
    python3 "$PY" write --task-id t1 --project-root "$REPO" --host "$1" >/dev/null 2>&1
  cat "$REPO/.ravenclaude/runs/t1/handoff-seed.txt" 2>/dev/null
}

# A grok LAUNCH is `grok "` or `grok -p`. The string "grok" alone is not one —
# every safe seed says "Do not launch grok", and matching that would make the
# gate fire on its own remedy text.
has_grok_launch() {
  case "$1" in
    *'grok "'* | *'grok -p'*) return 0 ;;
    *) return 1 ;;
  esac
}

assert_no_grok() {
  if has_grok_launch "$2"; then no "$1 — emitted a grok launch"; else ok "$1"; fi
}
assert_grok() {
  if has_grok_launch "$2"; then ok "$1"; else no "$1 — grok host lost its own seed"; fi
}
assert_has() {
  case "$2" in *"$3"*) ok "$1" ;; *) no "$1 — missing: $3" ;; esac
}

echo "Gate 227 — handoff seed is host-correct"
echo "  spawn: $SPAWN"
echo "  py:    $PY"

# ---- handoff-spawn.sh -----------------------------------------------------
out="$(spawn_out grok)"
assert_grok "spawn/grok keeps the grok seed (POSITIVE CONTROL)" "$out"

out="$(spawn_out claude-code)"
assert_no_grok "spawn/claude-code emits no grok launch" "$out"
# ⛔ NOT `assert_has "$out" "claude"` — the copy-paste block prints `cd <repo>`,
# and any checkout under `.claude/` satisfies that substring no matter what the
# seed says. Verified: the bare string passes even against the pre-fix grok seed.
# Assert the recipe header instead, which only the claude-code branch emits.
assert_has "spawn/claude-code emits the Claude Code recipe" "$out" "(Claude Code, not grok)"
assert_has "spawn/claude-code resolves the host (not unknown)" "$out" "host=claude-code"

out="$(spawn_out codex)"
assert_no_grok "spawn/codex (unrecognised host) emits no grok launch" "$out"

out="$(spawn_out cli)"
assert_no_grok "spawn/cli emits no grok launch" "$out"
assert_has "spawn/cli names copilot" "$out" "copilot"

out="$(spawn_out chat)"
assert_no_grok "spawn/chat emits no grok launch" "$out"

out="$(spawn_out '' CLAUDECODE=1)"
assert_no_grok "spawn/auto-detect via CLAUDECODE emits no grok launch" "$out"
assert_has "spawn/auto-detect resolves claude-code" "$out" "host=claude-code"

# The vscode case was already safe before the fix; pin it so the fix did not
# trade one covered environment for another.
out="$(spawn_out '' TERM_PROGRAM=vscode)"
assert_no_grok "spawn/unknown+vscode still emits no grok launch" "$out"

# ⛔ CASE (a) IS NOT THE DEFECT AND MUST NOT REGRESS. Nothing named and nothing
# detected keeps the grok-first fallback: this tooling exists for Grok->Grok
# handoff, and the skill records that Grok's markers are unreliable inside the
# agent process ("Detection is hook-only"), so a REAL Grok session can land
# here. Gate 215 pins the same default independently ("unset host still grok").
# Asserting it here too is deliberate: the fix narrows the grok fallback to
# case (a), and a gate that only checked the narrowing would be satisfied by
# deleting the fallback outright — which would break the primary flow.
out="$(spawn_out '')"
assert_grok "spawn/nothing named + nothing detected KEEPS grok (case a)" "$out"

# ---- context-handoff.py ---------------------------------------------------
seed="$(py_seed grok)"
assert_grok "py/grok keeps the grok seed (POSITIVE CONTROL)" "$seed"

seed="$(py_seed claude-code)"
assert_no_grok "py/claude-code emits no grok launch" "$seed"

seed="$(py_seed codex)"
assert_no_grok "py/codex (unrecognised host) emits no grok launch" "$seed"

seed="$(py_seed chat)"
assert_no_grok "py/chat emits no grok launch" "$seed"
assert_has "py/chat names a new Chat session" "$seed" "Chat"

seed="$(py_seed cli)"
assert_no_grok "py/cli emits no grok launch" "$seed"
assert_has "py/cli names copilot" "$seed" "copilot"

# The same case (a) as the spawn side. The two scripts write the seed for the
# SAME handoff, so a divergence here is a real defect even though no gate
# outside this file would notice it.
rm -f "$REPO/.ravenclaude/runs/t1/handoff-seed.txt"
env -i PATH=/usr/bin:/bin HOME="$HOME" \
  python3 "$PY" write --task-id t1 --project-root "$REPO" >/dev/null 2>&1
seed="$(cat "$REPO/.ravenclaude/runs/t1/handoff-seed.txt" 2>/dev/null)"
assert_grok "py/nothing named + nothing detected KEEPS grok (case a)" "$seed"

# ---- verdict --------------------------------------------------------------
echo "  pass=$pass fail=$fail"

if [ "$MUST_FAIL" -eq 1 ]; then
  if [ "$fail" -gt 0 ]; then
    echo "Gate 227 must-fail half: mutant CAUGHT ($fail assertion(s) went red) — teeth confirmed"
    exit 0
  fi
  echo "Gate 227 must-fail half: MUTANT NOT CAUGHT — the assertions do not measure the seed" >&2
  exit 1
fi

if [ "$fail" -gt 0 ]; then
  echo "Gate 227 FAILED" >&2
  exit 1
fi
echo "Gate 227 PASSED"
exit 0
