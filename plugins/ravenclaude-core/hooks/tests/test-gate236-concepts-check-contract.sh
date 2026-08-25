#!/usr/bin/env bash
#
# Gate 236 — the concepts --check contract: markers, collect-all, and a self-heal
# that survives a content-freshness failure.
#
# ⛔ WHY THIS TEST EXISTS, AND WHY IT RUNS THE WORKFLOW BLOCK RATHER THAN A COPY.
# regenerate-artifacts.yml step 1b decides whether a failing `concepts.py --check`
# is survivable. On no match it runs exit "$_crc", killing every later self-heal
# step — concept SVGs, decision-tree SVGs, dashboard.html, index.html, BI reports,
# the Copilot package, the feedback report. The workflow comment at that site
# records the incident it re-arms: main left UN-HEALED across many merges.
#
# The block under test is EXTRACTED FROM THE WORKFLOW FILE at run time and
# executed against fixture trees under `bash -e` (the shell GitHub Actions uses
# for `run:`). A restated copy would pass forever after somebody edited the real
# workflow — which is the exact "the test and the thing diverged" shape.
#
# ⛔ Every assertion has a TEETH half. "the self-heal continued" and "the block
# never ran" are otherwise the same observation.
#
# ⛔ NO APOSTROPHES anywhere in this file, and the scratch tree is cleaned with a
# helper rather than an inline recursive delete. Both notes are recorded at the
# head of scripts/spike-tprose-canary.sh.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
WF="$ROOT/.github/workflows/regenerate-artifacts.yml"
CP="$ROOT/scripts/concepts.py"

TMP="$(mktemp -d)"
_cleanup() { [ -n "${TMP:-}" ] && [ -d "$TMP" ] && command find "$TMP" -mindepth 0 -delete 2>/dev/null; }
trap _cleanup EXIT

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s (%s)\n' "$1" "$2"; }

echo "── Gate 236: concepts --check contract (markers, collect-all, self-heal) ──"

[ -f "$WF" ] || { echo "  FAIL  workflow absent at $WF"; exit 1; }
[ -f "$CP" ] || { echo "  FAIL  concepts.py absent at $CP"; exit 1; }

# ── Extract the step-1b block out of the real workflow ──────────────────────
BLOCK="$TMP/selfheal-block.sh"
python3 - "$WF" "$BLOCK" <<'PY'
import sys, textwrap
wf, out = sys.argv[1], sys.argv[2]
lines = open(wf, encoding="utf-8").read().split("\n")
start = None
for i, ln in enumerate(lines):
    if "if ! python3 scripts/concepts.py --check" in ln:
        start = i
        break
if start is None:
    sys.stderr.write("EXTRACT-FAIL: the step-1b opener is not in the workflow\n")
    sys.exit(3)
indent = len(lines[start]) - len(lines[start].lstrip())
end = None
for j in range(start + 1, len(lines)):
    if lines[j].strip() == "fi" and (len(lines[j]) - len(lines[j].lstrip())) == indent:
        end = j
        break
if end is None:
    sys.stderr.write("EXTRACT-FAIL: no closing fi at the opener indent\n")
    sys.exit(3)
body = textwrap.dedent("\n".join(lines[start : end + 1]))
open(out, "w", encoding="utf-8").write(
    "#!/usr/bin/env bash\nset -e\n" + body + "\necho SENTINEL-DOWNSTREAM-STEP-RAN\n"
)
print(f"extracted {end - start + 1} lines")
PY
_ex=$?
if [ "$_ex" -ne 0 ]; then
  echo "  FAIL  could not extract the workflow block (exit $_ex)."
  echo "        A test that cannot find its subject is broken, not passing."
  exit 1
fi

# ⛔ CONTROL ON THE EXTRACTOR ITSELF. If the extracted block does not contain the
# fatal exit, the later "it continued" results are vacuous — a block with no exit
# always continues.
if ! grep -q 'exit "\$_crc"' "$BLOCK"; then
  echo "  FAIL  the extracted block contains no fatal exit path. Every continue"
  echo "        result below would be vacuous, so this test refuses to report."
  exit 1
fi
ok "extractor control: the extracted block really does contain the fatal exit"

# ── Fixture builder ─────────────────────────────────────────────────────────
# $1 = tree root, $2 = last_verified for the platform-fact, $3 = valid|invalid
_fixture() {
  local root="$1" lv="$2" shape="$3"
  local cdir="$root/plugins/ravenclaude-core/knowledge/concepts"
  mkdir -p "$cdir" "$root/scripts"
  cp "$CP" "$root/scripts/concepts.py"
  {
    printf -- '---\n'
    printf 'id: fixture-fact\n'
    printf 'title: Fixture fact\n'
    printf 'category: Fixtures\n'
    if [ "$shape" = "invalid" ]; then
      # kind is outside VALID_KINDS -> a schema failure, i.e. generator-failure.
      printf 'kind: not-a-real-kind\n'
    else
      printf 'kind: platform-fact\n'
    fi
    printf 'order: 1\n'
    printf 'summary: A fixture concept used only by Gate 236.\n'
    printf 'last_verified: %s\n' "$lv"
    printf 'sources:\n'
    printf -- '  - label: fixture\n'
    printf -- '    url: https://example.invalid/fixture\n'
    printf -- '---\n\n'
    printf 'Explanatory body text for the fixture concept.\n\n'
    printf '```mermaid\ngraph TD\n  A[caller] --> B[callee]\n```\n'
  } > "$cdir/fixture-fact.md"
}

_regen() { (cd "$1" && python3 scripts/concepts.py >/dev/null 2>&1); }

# ── Case A: a STALE platform-fact must WARN and let the self-heal continue ──
A="$TMP/case-a"
_fixture "$A" "2020-01-01" valid
_regen "$A"
out_a="$(cd "$A" && bash "$BLOCK" 2>&1)"; rc_a=$?
if [ "$rc_a" -eq 0 ] && printf '%s' "$out_a" | grep -q 'SENTINEL-DOWNSTREAM-STEP-RAN'; then
  ok "content-freshness failure: self-heal continues, downstream step runs"
else
  bad "content-freshness failure: self-heal continues" "rc=$rc_a, sentinel missing"
fi
if printf '%s' "$out_a" | grep -q '::warning::'; then
  ok "content-freshness failure is surfaced as a ::warning::, not swallowed"
else
  bad "content-freshness failure surfaces a warning" "no ::warning:: in output"
fi

# ── Case A-teeth: the marker is what carries it ─────────────────────────────
# Neuter the emitter: strip the marker print from the fixture copy of concepts.py
# and assert the SAME tree now detonates. Without this, "it continued" and "the
# grep matches everything" are indistinguishable.
AT="$TMP/case-a-teeth"
_fixture "$AT" "2020-01-01" valid
_regen "$AT"
python3 - "$AT/scripts/concepts.py" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
# Remove the marker emission AND reword the legacy sentence, so neither the new
# marker term nor the retained compatibility term can match.
s = s.replace('print(f"{MARKER}{CLASS_HUMAN}")', "pass")
s = s.replace("Concept staleness gate FAILED", "Concept freshness problem")
open(p, "w", encoding="utf-8").write(s)
PY
out_at="$(cd "$AT" && bash "$BLOCK" 2>&1)"; rc_at=$?
if [ "$rc_at" -ne 0 ] && ! printf '%s' "$out_at" | grep -q 'SENTINEL-DOWNSTREAM-STEP-RAN'; then
  ok "TEETH: with the marker stripped, the SAME failure kills the self-heal"
else
  bad "TEETH: marker-stripped tree must detonate" "rc=$rc_at — the grep is matching too much"
fi

# ── Case B: a real GENERATOR failure must still abort ───────────────────────
B="$TMP/case-b"
_fixture "$B" "2026-08-19" invalid
out_b="$(cd "$B" && bash "$BLOCK" 2>&1)"; rc_b=$?
if [ "$rc_b" -ne 0 ] && ! printf '%s' "$out_b" | grep -q 'SENTINEL-DOWNSTREAM-STEP-RAN'; then
  ok "generator failure still aborts the self-heal (the fix is not a blanket pass)"
else
  bad "generator failure aborts" "rc=$rc_b — a broken generator was treated as survivable"
fi

# ── Case C: COLLECT-ALL — both violation classes reported together ─────────
# ⛔ The old shape evaluated staleness first and returned 1 before it ever
# compared concepts.json. One stale entry then blinded registry-freshness for the
# whole corpus — the masking-gate defect already in this repo record.
C="$TMP/case-c"
_fixture "$C" "2020-01-01" valid
_regen "$C"
printf '{"schema_version": 1, "categories": [], "concepts": []}\n' \
  > "$C/plugins/ravenclaude-core/concepts.json"
out_c="$(cd "$C" && python3 scripts/concepts.py --check 2>&1)"
has_stale=0; has_registry=0
printf '%s' "$out_c" | grep -q 'days old' && has_stale=1
printf '%s' "$out_c" | grep -q 'concepts.json is STALE' && has_registry=1
if [ "$has_stale" -eq 1 ] && [ "$has_registry" -eq 1 ]; then
  ok "collect-all: a dual-violation tree reports BOTH classes, not the first"
else
  bad "collect-all reports both" "stale=$has_stale registry=$has_registry"
fi
if printf '%s' "$out_c" | grep -q 'RC-CONCEPTS-CLASS: human-reverify-required' \
   && printf '%s' "$out_c" | grep -q 'RC-CONCEPTS-CLASS: generator-failure'; then
  ok "collect-all: BOTH class markers are emitted for a dual-violation tree"
else
  bad "collect-all emits both markers" "one or both markers missing"
fi

# ── Case C-control: a single-violation tree reports exactly ONE class ───────
# Without this, a --check that printed every marker unconditionally would pass
# case C while telling the workflow nothing.
CC="$TMP/case-c-control"
_fixture "$CC" "2020-01-01" valid
_regen "$CC"
out_cc="$(cd "$CC" && python3 scripts/concepts.py --check 2>&1)"
if printf '%s' "$out_cc" | grep -q 'RC-CONCEPTS-CLASS: human-reverify-required' \
   && ! printf '%s' "$out_cc" | grep -q 'RC-CONCEPTS-CLASS: generator-failure'; then
  ok "CONTROL: a single-violation tree emits exactly one class marker"
else
  bad "single-violation emits one marker" "the markers are not discriminating"
fi

# ── Case D: the clean tree still passes ────────────────────────────────────
D="$TMP/case-d"
_fixture "$D" "$(python3 -c 'import datetime;print(datetime.date.today().isoformat())')" valid
_regen "$D"
if (cd "$D" && python3 scripts/concepts.py --check >/dev/null 2>&1); then
  ok "pass-on-good: a fresh, regenerated tree still validates clean"
else
  bad "pass-on-good" "a clean fixture tree failed --check"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
