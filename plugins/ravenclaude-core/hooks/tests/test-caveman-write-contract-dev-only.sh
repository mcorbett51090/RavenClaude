#!/usr/bin/env bash
#
# Gate 265 -- caveman write-contract, DEV-ONLY. NOT in the required/blocking
# CI set (P6 of the caveman-routing-decision-tree plan). Reachable only via
# `bash scripts/audit-gates.sh --check 265` -- never from the main sequence,
# never from a plain `audit-gates.sh` run.
#
# Why this is separate from Gate 264: it depends on a THIRD-PARTY plugin
# (caveman) being installed on THIS host, which CI cannot guarantee. It
# globs the installed caveman plugin READ-ONLY (for locating its
# caveman-config.js module -- verification only, nothing under caveman's own
# cache is ever written or patched, per C11) and round-trips a REAL write
# through caveman's own reader (writeSessionMode -> resolveActiveMode /
# readSessionModeRaw), using a throwaway, cryptographically-random session id
# that can never collide with a real session -- exactly the sanctioned
# pattern P0.3 and P2 already used against this same host.
#
# ⛔ LOUD-SKIP, matching Gate 10's actionlint local-offline precedent: when
# caveman is not installed on this host, this exits 0 with an explicit
# "THIS IS NOT A PASS" banner. A skip is not a pass -- it never gets
# reported as green by silent omission, and it never blocks the required
# suite (this file is never in the main sequence).
#
# ⛔ Full snapshot + restore, both directions verified byte-for-byte: the
# per-session mode file (which cannot pre-exist for a fresh random id -- if
# it does, this aborts with ZERO writes rather than risk touching real
# state) and the machine-wide legacy mirror .caveman-active (R10 -- writes
# here are a real, bounded, cross-session side effect; this test measures
# that the round trip restores it exactly, not that the flicker window is
# zero).
#
# ⛔ HISTORY: the mirror-restoration assertion below was deliberately RED from
# this gate's authoring until the P2 follow-up fix (2026-09-03) -- see the
# "KNOWN GAP" comment inside the assertion's else-branch for the full original
# writeup of the bug (caveman-apply-mode.sh's --restore action read back only
# `user_mode_at_entry`, never `legacy_mirror_at_entry`, so a fresh-session
# apply+restore round trip unconditionally unlinked the mirror). That gap is
# now CLOSED in caveman-apply-mode.sh (see its header's "THE MIRROR HALF"
# note) -- the else-branch below is retained verbatim as the historical record
# of what this gate caught, per this repo's own convention of correcting
# stale docs in the same change that closes the gap they describe, rather
# than silently deleting the evidence of what was found.

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
cd "$ROOT" || exit 1

APPLY_SH="$ROOT/plugins/ravenclaude-core/scripts/caveman-apply-mode.sh"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

PASS=0
FAIL=0
ok() {
  PASS=$((PASS + 1))
  printf '  OK    %s\n' "$1"
}
bad() {
  FAIL=$((FAIL + 1))
  printf '  FAIL  %s (%s)\n' "$1" "$2"
}

_field() {
  # $1=json blob $2=field name -> the field's string value, or "" if absent.
  # Same idiom as caveman-apply-mode.sh's own _json_field -- no jq dependency.
  printf '%s' "$1" | grep -o "\"$2\":\"[^\"]*\"" | head -n1 | sed -E "s/\"$2\":\"([^\"]*)\"/\1/"
}

echo "── Gate 265: caveman write-contract, dev-only (NOT required) ──────────────"

# ── Locate the installed caveman plugin. READ-ONLY glob, verification only. ──
CAVEMAN_CACHE="$CLAUDE_DIR/plugins/cache/caveman/caveman"
CAVEMAN_STANDALONE="$CLAUDE_DIR/hooks/caveman-config.js"

found=""
if [ -d "$CAVEMAN_CACHE" ]; then
  for d in "$CAVEMAN_CACHE"/*/; do
    if [ -f "${d}src/hooks/caveman-config.js" ]; then
      found="${d}src/hooks/caveman-config.js"
      break
    fi
  done
fi
if [ -z "$found" ] && [ -f "$CAVEMAN_STANDALONE" ]; then
  found="$CAVEMAN_STANDALONE"
fi

if [ -z "$found" ]; then
  echo "  ‼ caveman plugin NOT FOUND on this host (checked cache-glob + standalone)." >&2
  echo "    THIS IS NOT A PASS. Re-run on a host with the caveman plugin installed." >&2
  exit 0
fi

echo "  caveman found (read-only): $found"

# ── A throwaway, cryptographically-random session id. Never a real one. ─────
sid="rc-gate265-devonly-$(date +%s)-$$-${RANDOM}${RANDOM}"
if ! printf '%s' "$sid" | grep -Eq '^[A-Za-z0-9_-]{1,128}$'; then
  echo "  ‼ generated throwaway session id failed its own shape check -- aborting, no writes" >&2
  exit 0
fi

SESSFILE="$CLAUDE_DIR/.caveman-sessions/$sid.mode"
MIRROR="$CLAUDE_DIR/.caveman-active"

if [ -e "$SESSFILE" ]; then
  echo "  ‼ throwaway session id collided with an existing file -- aborting, ZERO writes" >&2
  exit 0
fi

# Snapshot the pre-existing mirror state EXACTLY (byte-for-byte), before any write.
mirror_before=""
mirror_before_present=0
if [ -f "$MIRROR" ]; then
  mirror_before="$(cat "$MIRROR")"
  mirror_before_present=1
fi

# A disposable scratch project dir for caveman-apply-mode.sh's OWN internal
# snapshot state file (never CLAUDE_PROJECT_DIR of the real repo).
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
export CLAUDE_PROJECT_DIR="$T"

# ── Real write: apply 'lite' against the REAL installed caveman. ────────────
out1="$(bash "$APPLY_SH" "$sid" lite 2>&1)"
status1="$(_field "$out1" status)"
readback1="$(_field "$out1" readback_ok)"
mode1="$(_field "$out1" applied_mode)"

if [ "$status1" = "applied" ] && [ "$readback1" = "true" ] && [ "$mode1" = "lite" ]; then
  ok "real write: caveman-apply-mode.sh $sid lite -> applied, readback agrees ($out1)"
else
  bad "real write" "$out1"
fi

if [ -f "$SESSFILE" ] && grep -qx 'lite' "$SESSFILE"; then
  ok "the real per-session mode file was written with the literal applied mode"
else
  bad "per-session mode file" "expected literal 'lite' at $SESSFILE"
fi

# ── Restore: undoes the write, using caveman-apply-mode.sh's own --restore. ──
out2="$(bash "$APPLY_SH" --restore "$sid" 2>&1)"
status2="$(_field "$out2" status)"
readback2="$(_field "$out2" readback_ok)"

if [ "$status2" = "restored" ] && [ "$readback2" = "true" ]; then
  ok "restore: caveman-apply-mode.sh --restore $sid -> restored, readback agrees ($out2)"
else
  bad "restore" "$out2"
fi

# Belt-and-suspenders cleanup: the throwaway id never existed before this
# test, so leave ZERO residue rather than the safe-but-present literal 'off'
# --restore writes for an absent prior entry.
rm -f "$SESSFILE"

# ── The machine-wide mirror must be restored to its EXACT pre-test bytes. ───
mirror_after=""
mirror_after_present=0
if [ -f "$MIRROR" ]; then
  mirror_after="$(cat "$MIRROR")"
  mirror_after_present=1
fi

if [ "$mirror_before_present" -eq "$mirror_after_present" ] && [ "$mirror_before" = "$mirror_after" ]; then
  ok "the machine-wide legacy mirror (.caveman-active) was restored to its exact pre-test state"
else
  # ⛔ KNOWN GAP, confirmed live 2026-09-03: caveman-apply-mode.sh's --restore
  # action (its `if (action === 'restore')` branch) reads back ONLY
  # priorState.user_mode_at_entry and calls writeSessionMode(restoreMode) --
  # it never reads priorState.legacy_mirror_at_entry, despite that field
  # being captured in the snapshot at apply time. For a throwaway session id
  # (no prior per-session value) restoreMode resolves to null -> canonical
  # 'off' -> writeSessionMode's own on-off branch unconditionally UNLINKS the
  # legacy mirror -- so a single apply+restore round trip against a fresh
  # session id destroys whatever the mirror held before, regardless of what
  # it held. This is a real gap between caveman-apply-mode.sh's actual
  # restore behavior and the plan's stated mitigation-1 intent ("restore
  # both on --restore"). It is a P2 (applier) defect, out of scope for P6 --
  # not fixed here; flagging honestly rather than softening the assertion to
  # pass. See the P6 tester report for the full writeup.
  bad "mirror restoration" "before=[present=$mirror_before_present '$mirror_before'] after=[present=$mirror_after_present '$mirror_after'] -- KNOWN GAP: --restore does not read back legacy_mirror_at_entry, see comment above"
fi

if [ ! -e "$SESSFILE" ]; then
  ok "zero residue: the throwaway per-session mode file was removed"
else
  bad "zero residue" "$SESSFILE still exists"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
