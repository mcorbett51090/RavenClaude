#!/usr/bin/env bash
#
# Gate 237 — the staleness double-exemption, BOTH escapes, and the two axes.
#
# ⛔ THE DEFECT THIS CLOSES. scripts/concepts.py used to gate on:
#     if c["kind"] != "platform-fact" or not c["last_verified"]: continue
# An OR, so a concept escaped on EITHER limb:
#   escape 1 (kind)  — 41 ravenclaude-built against 17 platform-fact, so the gate
#                      covered the MINORITY kind. Every inventory entry would be
#                      ravenclaude-built and inherit zero staleness pressure.
#   escape 2 (field) — an entry with no last_verified at all was SKIPPED, so
#                      "unverified" rendered identically to "verified recently".
#
# ⛔ BOTH ESCAPES ARE ASSERTED SEPARATELY. A fix that closes only the kind check
# passes an escape-1 test while escape 2 stays wide open, and that is the exact
# silent-green shape the whole initiative exists to end.
#
# ⛔ NO APOSTROPHES; scratch cleaned with a helper, not an inline recursive
# delete. Both notes are recorded at the head of scripts/spike-tprose-canary.sh.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
CP="$ROOT/scripts/concepts.py"

TMP="$(mktemp -d)"
_cleanup() { [ -n "${TMP:-}" ] && [ -d "$TMP" ] && command find "$TMP" -mindepth 0 -delete 2>/dev/null; }
trap _cleanup EXIT

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s (%s)\n' "$1" "$2"; }

echo "── Gate 237: inventory staleness — both escapes, both axes ──"

TODAY="$(python3 -c 'import datetime;print(datetime.date.today().isoformat())')"
OLD="$(python3 -c 'import datetime;print((datetime.date.today()-datetime.timedelta(days=400)).isoformat())')"

# ── Fixture builder ─────────────────────────────────────────────────────────
# $1 root, $2 last_verified (empty string = OMIT the field entirely), $3 covered-file body
_fixture() {
  local root="$1" lv="$2" body="$3"
  local cdir="$root/plugins/ravenclaude-core/knowledge/concepts"
  mkdir -p "$cdir" "$root/scripts" "$root/covered"
  cp "$CP" "$root/scripts/concepts.py"
  printf '%s\n' "$body" > "$root/covered/artifact.sh"
  {
    printf -- '---\n'
    printf 'id: fixture-entry\n'
    printf 'title: Fixture inventory entry\n'
    printf 'category: Fixtures\n'
    printf 'kind: ravenclaude-built\n'
    printf 'entry_class: inventory\n'
    printf 'order: 1\n'
    printf 'summary: A fixture inventory entry used only by Gate 237.\n'
    [ -n "$lv" ] && printf 'last_verified: %s\n' "$lv"
    printf 'covers:\n'
    printf -- '  - covered/artifact.sh\n'
    printf 'covers_digest: "sha256:%s"\n' "$(printf '0%.0s' $(seq 1 64))"
    # ⛔ P5 made nuance/nuance_evidence/verify REQUIRED on entry_class: inventory,
    # which retroactively invalidated this P3 fixture. Adding them here is the
    # correct fix: a fixture that no longer satisfies the schema it exercises is
    # measuring the schema, not the staleness axis this gate exists for.
    printf 'nuance: "The gate skips on an OR, so an entry escapes for not being a platform-fact or merely for lacking the field."\n'
    printf 'nuance_evidence:\n'
    printf '  measured: 2026-08-19\n'
    printf '  control: "a fixture with the field absent now blocks where it used to be skipped"\n'
    printf '  falsifier: "an entry with no last_verified passing the gate"\n'
    printf '  probe: "unprobed: this fixture exists to exercise the gate, not to be probed by it"\n'
    printf 'nuance_source: covered/artifact.sh:1-2\n'
    printf 'verify:\n  tier: none\n  rationale: a Gate 237 fixture has no runtime observable of its own\n'
    printf 'sources:\n'
    printf -- '  - label: fixture\n'
    printf -- '    url: https://example.invalid/fixture\n'
    printf -- '---\n\n'
    printf 'Explanatory body text for the fixture entry.\n\n'
    printf '```mermaid\ngraph TD\n  A[caller] --> B[callee]\n```\n'
  } > "$cdir/fixture-entry.md"
}

# Stamp the digest to its true value so the entry starts NOT drifting.
_settle() { (cd "$1" && python3 scripts/concepts.py --restamp-cosmetic fixture-entry >/dev/null 2>&1 \
                     && python3 scripts/concepts.py >/dev/null 2>&1); }

_lv_of() { sed -n 's/^last_verified: *//p' "$1/plugins/ravenclaude-core/knowledge/concepts/fixture-entry.md" | head -1; }

# ── 1. ESCAPE 1 (kind): a ravenclaude-built entry past the window ───────────
# WARNS on a PR, FAILS the sweep. Before the fix it did neither: the kind check
# skipped it entirely.
A="$TMP/a"; _fixture "$A" "$OLD" "original"; _settle "$A"
out_pr="$(cd "$A" && python3 scripts/concepts.py --check 2>&1)"; rc_pr=$?
out_sw="$(cd "$A" && python3 scripts/concepts.py --check --sweep 2>&1)"; rc_sw=$?

if [ "$rc_pr" -eq 0 ] && printf '%s' "$out_pr" | grep -q 'WARNING'; then
  ok "escape 1: an aged ravenclaude-built inventory entry WARNS on a PR"
else
  bad "escape 1 warns on PR" "rc=$rc_pr, no WARNING in output"
fi
if [ "$rc_sw" -ne 0 ] && printf '%s' "$out_sw" | grep -q 'staleness gate FAILED'; then
  ok "escape 1: the SAME entry FAILS the scheduled sweep (--sweep)"
else
  bad "escape 1 fails the sweep" "rc=$rc_sw"
fi
# ⛔ CONTROL: the two runs must actually DIFFER. If --sweep changed nothing, one
# of the two results above would be an accident of the other.
if [ "$rc_pr" -ne "$rc_sw" ]; then
  ok "CONTROL: PR mode and sweep mode return DIFFERENT verdicts for one tree"
else
  bad "PR vs sweep differ" "both returned $rc_pr — the axis is not wired"
fi

# ── 2. ESCAPE 2 (missing field): absent last_verified BLOCKS on a PR ────────
B="$TMP/b"; _fixture "$B" "" "original"; _settle "$B"
out_b="$(cd "$B" && python3 scripts/concepts.py --check 2>&1)"; rc_b=$?
if [ "$rc_b" -ne 0 ] && printf '%s' "$out_b" | grep -q 'last_verified is ABSENT'; then
  ok "escape 2: an ABSENT last_verified is a violation, not a skip — blocks on PR"
else
  bad "escape 2 blocks on PR" "rc=$rc_b"
fi

# ── 3. CONTENT DRIFT: a mutated covered artifact fails on a PR ─────────────
C="$TMP/c"; _fixture "$C" "$TODAY" "original"; _settle "$C"
if (cd "$C" && python3 scripts/concepts.py --check >/dev/null 2>&1); then
  ok "pre-drift control: the settled fixture passes before anything is mutated"
else
  bad "pre-drift control" "the settled fixture already failed"
fi
printf 'MUTATED\n' >> "$C/covered/artifact.sh"
out_c="$(cd "$C" && python3 scripts/concepts.py --check 2>&1)"; rc_c=$?
if [ "$rc_c" -ne 0 ] && printf '%s' "$out_c" | grep -q 'covers_digest drift'; then
  ok "content drift: a mutated covered artifact BLOCKS on a PR"
else
  bad "content drift blocks on PR" "rc=$rc_c"
fi

# ── 3b. --restamp-cosmetic clears the digest and does NOT move the date ────
lv_before="$(_lv_of "$C")"
(cd "$C" && python3 scripts/concepts.py --restamp-cosmetic fixture-entry >/dev/null 2>&1)
(cd "$C" && python3 scripts/concepts.py >/dev/null 2>&1)
lv_after="$(_lv_of "$C")"
if (cd "$C" && python3 scripts/concepts.py --check >/dev/null 2>&1); then
  ok "--restamp-cosmetic clears the drift"
else
  bad "--restamp-cosmetic clears drift" "still failing after a cosmetic restamp"
fi
if [ "$lv_before" = "$lv_after" ] && [ -n "$lv_before" ]; then
  ok "--restamp-cosmetic did NOT move last_verified ($lv_before -> $lv_after)"
else
  bad "cosmetic must not move the date" "$lv_before -> $lv_after"
fi

# ── 3c. --restamp REQUIRES a real reason, and DOES move the date ───────────
D="$TMP/d"; _fixture "$D" "$OLD" "original"; _settle "$D"
printf 'MUTATED\n' >> "$D/covered/artifact.sh"
if (cd "$D" && python3 scripts/concepts.py --restamp fixture-entry --reason "too short" >/dev/null 2>&1); then
  bad "--restamp rejects a short reason" "a 9-char reason was accepted"
else
  ok "--restamp REJECTS a reason below the minimum (a restamp is a re-READ)"
fi
lv_d_before="$(_lv_of "$D")"
(cd "$D" && python3 scripts/concepts.py --restamp fixture-entry \
   --reason "re-read the covered artifact end to end and re-confirmed the mechanism claim" >/dev/null 2>&1)
lv_d_after="$(_lv_of "$D")"
if [ "$lv_d_before" != "$lv_d_after" ] && [ "$lv_d_after" = "$TODAY" ]; then
  ok "--restamp with a real reason DOES advance last_verified ($lv_d_before -> $lv_d_after)"
else
  bad "--restamp advances the date" "$lv_d_before -> $lv_d_after"
fi
if [ -s "$D/tests/fixtures/inventory-restamp-log.jsonl" ] \
   && grep -q '"digest_before"' "$D/tests/fixtures/inventory-restamp-log.jsonl" \
   && grep -q '"digest_after"' "$D/tests/fixtures/inventory-restamp-log.jsonl"; then
  ok "--restamp appends a committed log line carrying both digests and the reason"
else
  bad "restamp log written" "log missing or incomplete"
fi

# ── 4. The 58 real concepts still validate, registry byte-identical ────────
# ⛔ THIS IS THE POSITIVE CONTROL FOR THE WHOLE PHASE. It is what separates
# "the change is additive" from "the change quietly rewrote the registry".
if (cd "$ROOT" && python3 scripts/concepts.py --check >/dev/null 2>&1); then
  ok "the real corpus still validates under the new gate"
else
  bad "real corpus validates" "concepts.py --check failed on the repo"
fi
if (cd "$ROOT" && git diff --quiet -- plugins/ravenclaude-core/concepts.json); then
  ok "CONTROL: concepts.json is byte-identical to HEAD — the change is additive"
else
  bad "concepts.json byte-identical" "the schema change rewrote the registry"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
