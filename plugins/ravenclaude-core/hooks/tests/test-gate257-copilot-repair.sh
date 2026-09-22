#!/usr/bin/env bash
# Gate 257 — `ravenclaude repair --host copilot` is the escape hatch for a
# Copilot session bricked by an incompatible/malformed .github/hooks/ravenclaude.json.
#
# WHY THIS GATE EXISTS
#
# An incident report (2026-09) described GitHub Copilot CLI 1.0.3 — well below
# the 1.0.52 sub-agent-hooking floor Gate 157 already checks — producing
# malformed hook output that broke the Copilot hook adapter and blocked EVERY
# tool call, not just sub-agent ones. copilot_version_check() deliberately
# never aborts the installer (owner ruling 2026-08-13, see the comment above
# COPILOT_FLOOR in scripts/ravenclaude) — which is correct — but that means it
# also never refuses to WRITE the hooks file for a critically incompatible
# version. Until `repair` existed, a user in that state had no documented way
# to recover a working Copilot session short of manually finding and deleting
# a file inside .github/hooks/.
#
# This gate proves the escape hatch is SAFE (renames, never deletes — fully
# recoverable) and REACHABLE (a plain project directory, no copilot binary
# required — repair never invokes `copilot` itself).
#
# Driven through the REAL `scripts/ravenclaude repair` command against a
# synthetic tmp project — never a reimplementation of the rename logic.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RC="$HERE/../../../../scripts/ravenclaude"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  ✗ %s\n' "$1"; }

[ -f "$RC" ] || { printf 'FATAL: installer not found at %s\n' "$RC" >&2; exit 1; }

printf '── Gate 257: Copilot hook-repair escape hatch ──\n'

# ── 1. Nothing to repair — clean exit 0, no file created ──────────────────
PROJ1="$TMP/proj1"; mkdir -p "$PROJ1"
out1="$(bash "$RC" repair --project "$PROJ1" --host copilot 2>&1)"; rc1=$?
if [ "$rc1" -eq 0 ] && printf '%s' "$out1" | grep -q 'nothing to repair'; then
  ok "no hooks file present -> exit 0, 'nothing to repair'"
else
  bad "no hooks file present -> exit $rc1, output did not report 'nothing to repair'"
fi

# ── 2. A hooks file present is DISABLED (renamed), never deleted ──────────
PROJ2="$TMP/proj2"; mkdir -p "$PROJ2/.github/hooks"
HOOKS2="$PROJ2/.github/hooks/ravenclaude.json"
printf '{"marker":"gate257-content"}' > "$HOOKS2"
out2="$(bash "$RC" repair --project "$PROJ2" --host copilot 2>&1)"; rc2=$?
if [ "$rc2" -eq 0 ] && [ ! -f "$HOOKS2" ]; then
  ok "original path no longer exists after repair"
else
  bad "original path still exists (or repair exited nonzero: $rc2) — the disable did not fire"
fi
disabled_count="$(find "$PROJ2/.github/hooks" -maxdepth 1 -name 'ravenclaude.json.disabled-*' 2>/dev/null | wc -l | tr -d ' ')"
if [ "${disabled_count:-0}" -eq 1 ]; then
  ok "exactly one .disabled-<ts> file was created"
else
  bad "expected exactly 1 .disabled-<ts> file, found ${disabled_count:-0}"
fi
disabled_file="$(find "$PROJ2/.github/hooks" -maxdepth 1 -name 'ravenclaude.json.disabled-*' 2>/dev/null | head -1)"
if [ -n "$disabled_file" ] && grep -q 'gate257-content' "$disabled_file" 2>/dev/null; then
  ok "disabled file preserves the original content byte-for-byte (renamed, not truncated)"
else
  bad "disabled file is missing or its content does not match the original"
fi

# ── 3. --host other than copilot refuses, and the file is UNTOUCHED ───────
PROJ3="$TMP/proj3"; mkdir -p "$PROJ3/.github/hooks"
HOOKS3="$PROJ3/.github/hooks/ravenclaude.json"
printf '{"marker":"gate257-untouched"}' > "$HOOKS3"
out3="$(bash "$RC" repair --project "$PROJ3" --host codex 2>&1)"; rc3=$?
if [ "$rc3" -eq 2 ] && printf '%s' "$out3" | grep -qi 'only supports --host copilot'; then
  ok "--host codex refuses with exit 2 and a clear message"
else
  bad "--host codex did not refuse as expected (exit $rc3)"
fi
if [ -f "$HOOKS3" ] && grep -q 'gate257-untouched' "$HOOKS3" 2>/dev/null; then
  ok "--host codex left the copilot hooks file completely untouched"
else
  bad "--host codex mutated or removed a file it should never have touched"
fi

# ── TEETH ───────────────────────────────────────────────────────────────────
# Prove the assertions above are measuring the real disable logic, not passing
# for an unrelated reason: build a mutant that ALWAYS reports "nothing to
# repair" (the disable branch's mv is never reached) and confirm the mutant
# leaves a real hooks file in place — i.e. the mutant is caught.
MUT="$TMP/ravenclaude-mutant"
sed 's/if \[ ! -f "\$hooks_file" \]; then/if true; then/' "$RC" > "$MUT"
if ! grep -q 'if true; then' "$MUT"; then
  bad "teeth: could not build the always-nothing-to-repair mutant (guard text changed?)"
else
  PROJ4="$TMP/proj4"; mkdir -p "$PROJ4/.github/hooks"
  HOOKS4="$PROJ4/.github/hooks/ravenclaude.json"
  printf '{"marker":"gate257-teeth"}' > "$HOOKS4"
  bash "$MUT" repair --project "$PROJ4" --host copilot >/dev/null 2>&1
  if [ -f "$HOOKS4" ]; then
    ok "teeth: neutering the disable branch leaves the hooks file in place — the real branch has teeth"
  else
    bad "teeth: the mutant still disabled the file — assertion 2 above may be vacuous"
  fi
fi

printf '\n  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
