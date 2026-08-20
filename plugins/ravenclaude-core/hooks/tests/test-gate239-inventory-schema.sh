#!/usr/bin/env bash
#
# Gate 239 — the inventory schema delta: nuance, evidence, verify, and the
# strength badge (⛔ R9, R12).
#
# ⛔ R12 IS WHY THE BADGE IS DERIVED IN THE REGISTRY, NOT IN A RENDERER.
# ~60% of the inventory — 54 skills, 15 agents, 27 uncalled scripts — gets
# findability and reference-integrity only. Both panel plans recorded that
# honestly IN THE PLAN and then left the distinction invisible on the one surface
# the project exists to make legible. A weak check and a strong one that look
# identical is the inert-gate defect wearing a badge. Deriving the badge text in
# concepts.py means no renderer can quietly substitute a friendlier word, and the
# badge names the LIMIT ("Findable") rather than a reassuring synonym
# ("Verified (static)") that a skimming reader reads as verification.
#
# ⛔ NO APOSTROPHES; scratch cleaned with a helper. See spike-tprose-canary.sh.

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

echo "── Gate 239: inventory schema — nuance, evidence, verify, strength badge ──"

TODAY="$(python3 -c 'import datetime;print(datetime.date.today().isoformat())')"

# $1 root | $2 nuance line ("" = OMIT) | $3 strength | $4 tier | $5 extra evidence lines
_fixture() {
  local root="$1" nuance="$2" strength="$3" tier="$4"
  local cdir="$root/plugins/ravenclaude-core/knowledge/concepts"
  mkdir -p "$cdir" "$root/scripts" "$root/covered"
  cp "$CP" "$root/scripts/concepts.py"
  printf 'covered artifact\n' > "$root/covered/artifact.sh"
  printf '#!/usr/bin/env bash\n:\n' > "$root/scripts/probe.sh"
  {
    printf -- '---\n'
    printf 'id: fixture-entry\ntitle: Fixture\ncategory: Fixtures\nkind: ravenclaude-built\n'
    printf 'entry_class: inventory\norder: 1\n'
    printf 'summary: A fixture inventory entry used only by Gate 239.\n'
    printf 'last_verified: %s\n' "$TODAY"
    printf 'covers:\n  - covered/artifact.sh\n'
    printf 'covers_digest: "sha256:%s"\n' "$(printf '0%.0s' $(seq 1 64))"
    [ -n "$nuance" ] && printf 'nuance: %s\n' "$nuance"
    printf 'nuance_evidence:\n'
    printf '  measured: %s\n' "$TODAY"
    printf '  control: the same payload with the trigger removed did not deny\n'
    printf '  falsifier: a stderr token arriving in any recorded transcript\n'
    printf '  probe: scripts/probe.sh\n'
    printf 'nuance_source: covered/artifact.sh:1-2\n'
    printf 'verify:\n  tier: %s\n' "$tier"
    if [ "$tier" = "none" ]; then
      printf '  rationale: no cheap runtime observable exists for this artifact class\n'
    else
      printf '  strength: %s\n  class: hook-registration\n  probe: scripts/probe.sh\n  teeth_exit: 1\n' "$strength"
    fi
    printf 'sources:\n  - label: fixture\n    url: https://example.invalid/f\n'
    printf -- '---\n\nBody text.\n\n```mermaid\ngraph TD\n  A --> B\n```\n'
  } > "$cdir/fixture-entry.md"
}

_settle() { (cd "$1" && python3 scripts/concepts.py --restamp-cosmetic fixture-entry >/dev/null 2>&1 \
                     && python3 scripts/concepts.py >/dev/null 2>&1); }

# ── 1. A well-formed entry validates ───────────────────────────────────────
# ⛔ Asserted FIRST. Every rejection below is only meaningful if the schema can
# accept a correct entry at all; a schema that rejects everything would pass
# every negative test.
A="$TMP/a"; _fixture "$A" "stderr at exit 0 reaches the model on no event." executed effect; _settle "$A"
if (cd "$A" && python3 scripts/concepts.py --check >/dev/null 2>&1); then
  ok "CONTROL: a well-formed inventory entry validates"
else
  bad "well-formed entry validates" "$(cd "$A" && python3 scripts/concepts.py --check 2>&1 | head -2)"
fi

# ── 2. A missing nuance fails with a SPECIFIC message ──────────────────────
B="$TMP/b"; _fixture "$B" "" executed effect
out_b="$(cd "$B" && python3 scripts/concepts.py --check 2>&1)"
if printf '%s' "$out_b" | grep -q "requires a non-empty 'nuance'"; then
  ok "a missing nuance fails, and the message names the field"
else
  bad "missing nuance fails specifically" "$(printf '%s' "$out_b" | head -1)"
fi

# ── 3. The 4-RENDERED-LINE cap, which is a LAYOUT rule ────────────────────
# A long nuance pushes its control: line outside the premise-guard +/-6-line
# window, which S1 measured. So the cap is enforced on WRAPPED lines, not on
# sentence count — plan A capped by sentences and wrapped to 6-7 lines.
LONG="$(python3 -c "print('the mechanism detail continues at length ' * 14)")"
C="$TMP/c"; _fixture "$C" "$LONG" executed effect
out_c="$(cd "$C" && python3 scripts/concepts.py --check 2>&1)"
if printf '%s' "$out_c" | grep -q 'renders as .* lines'; then
  ok "an over-long nuance fails the 4-RENDERED-line layout cap"
else
  bad "nuance line cap" "$(printf '%s' "$out_c" | head -1)"
fi

# ── 4. tier: none REQUIRES a written rationale ─────────────────────────────
D="$TMP/d"
_fixture "$D" "a fact." executed none; _settle "$D"
if (cd "$D" && python3 scripts/concepts.py --check >/dev/null 2>&1); then
  ok "tier: none validates WHEN it carries a rationale"
else
  bad "tier: none with rationale" "rejected despite a rationale"
fi
python3 - "$D/plugins/ravenclaude-core/knowledge/concepts/fixture-entry.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = s.replace("  rationale: no cheap runtime observable exists for this artifact class\n", "")
open(p, "w", encoding="utf-8").write(s)
PY
out_d="$(cd "$D" && python3 scripts/concepts.py --check 2>&1)"
if printf '%s' "$out_d" | grep -q "requires a written 'rationale'"; then
  ok "tier: none WITHOUT a rationale fails — an absence is not a verdict"
else
  bad "tier: none needs a rationale" "$(printf '%s' "$out_d" | head -1)"
fi

# ── 5. ⛔ R12: the strength badge is DERIVED IN THE REGISTRY ───────────────
for pair in "executed:Probed" "static:Findable" "observational:Observed"; do
  st="${pair%%:*}"; want="${pair##*:}"
  E="$TMP/e-$st"; _fixture "$E" "a fact." "$st" effect; _settle "$E"
  got="$(cd "$E" && python3 -c "
import json;d=json.load(open('plugins/ravenclaude-core/concepts.json'))
print(d['concepts'][0].get('strength_badge'))
" 2>/dev/null)"
  if [ "$got" = "$want" ]; then
    ok "R12 badge: strength '$st' renders as '$want' (states the LIMIT)"
  else
    bad "R12 badge for '$st'" "want '$want', got '$got'"
  fi
done
N="$TMP/e-none"; _fixture "$N" "a fact." executed none; _settle "$N"
got_n="$(cd "$N" && python3 -c "
import json;d=json.load(open('plugins/ravenclaude-core/concepts.json'))
print(d['concepts'][0].get('strength_badge'))
" 2>/dev/null)"
if [ "$got_n" = "Unverified" ]; then
  ok "R12 badge: tier: none renders as 'Unverified', never a softer synonym"
else
  bad "R12 badge for tier: none" "want 'Unverified', got '$got_n'"
fi

# ── 6. ⛔ R9: a pasted output block is rejected ────────────────────────────
rc=0; python3 "$ROOT/scripts/check-inventory-evidence.py" --must-fail >/dev/null 2>&1 || rc=$?
decl="$(python3 "$ROOT/scripts/check-inventory-evidence.py" --must-fail-convention)"
if [ "$rc" = "${decl##*: }" ]; then
  ok "R9 evidence gate: pasted-output shapes caught, honest entry passes, exit matches its declaration"
else
  bad "R9 evidence gate teeth" "declared ${decl##*: }, observed $rc"
fi

# ── 7. The real corpus is untouched ───────────────────────────────────────
if (cd "$ROOT" && python3 scripts/concepts.py --check >/dev/null 2>&1) \
   && (cd "$ROOT" && git diff --quiet -- plugins/ravenclaude-core/concepts.json); then
  ok "CONTROL: 58 real concepts validate and concepts.json is byte-identical to HEAD"
else
  bad "real corpus untouched" "the schema delta was not additive"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
