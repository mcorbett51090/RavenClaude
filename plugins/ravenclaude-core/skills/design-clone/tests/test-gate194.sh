#!/usr/bin/env bash
# Gate 194 — design-clone apply-path BIDIRECTIONAL teeth (the P0 headline: a unidirectional
# gate is the defect). Self-contained: drives apply_schema.py --self-test (SURVIVE verbatim +
# NEUTRALIZE whole-drop + IDENTITY structural + FLAG fires), re-exercises the COMMITTED fixtures
# via the CLI + grep of the output tree, validates the pure fixtures against check-design-schema.py,
# and proves teeth with three must-fail mutants (a neutered widened sanitizer that returns its
# input verbatim → the hostile payload appears; a drop-everything sanitizer → the SURVIVE half
# fails; an apply() that reads colors.palette → the reference-color assertion fails).
#
# No network, no port bind — file fixtures only. bash-3.2 / macOS-safe: no declare -A, mapfile,
# ${x^^}, GNU timeout, grep -P, or sed -i. Paths resolve from this script's own location, so it
# runs from any cwd (audit-gates.sh runs it from the repo root; a direct `bash <path>` also works).
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"                 # .../skills/design-clone
ROOT="$(cd "$HERE/../../../../.." && pwd)"       # repo root
APPLY="$SKILL/apply_schema.py"
CHECK="$SKILL/../../scripts/check-design-schema.py"
FX="$ROOT/tests/fixtures/design-clone"
TARGET="$FX/target-brand.json"

fails=0
ok() { printf '  ✓ %s\n' "$1"; }
bad() {
  printf '  ✗ %s\n' "$1"
  fails=$((fails + 1))
}

# 0) the primary self-contained bidirectional assertion
if python3 "$APPLY" --self-test >/dev/null 2>&1; then
  ok "apply_schema --self-test (SURVIVE + NEUTRALIZE + IDENTITY + NO-READ + FLAG)"
else
  bad "apply_schema --self-test FAILED"
  python3 "$APPLY" --self-test 2>&1 | sed 's/^/      /'
fi

# 1) input conformance — the two PURE committed fixtures ARE valid design-schemas (conformant
#    is not the same as safe; the sanitizer is what adds safety on top of conformance)
for f in legit-values.json hostile-shadow.json; do
  if python3 "$CHECK" "$FX/$f" >/dev/null 2>&1; then
    ok "check-design-schema: committed $f conforms"
  else
    bad "check-design-schema: committed $f is NON-conformant"
  fi
done

OUT="$(mktemp -d)"

# 2) SURVIVE — legit structural values present VERBATIM (the false-negative half: a
#    drop-everything sanitizer would ship an empty stylesheet and pass a hostile-only gate)
python3 "$APPLY" "$FX/legit-values.json" --target-brand "$TARGET" --out "$OUT/legit" >/dev/null 2>&1
LCSS="$OUT/legit/design-schema.css"
for n in "8px" "1.5rem" "1200px" "0 2px 8px rgba(0,0,0,0.1)" "#0055ff"; do
  if grep -qF -- "$n" "$LCSS" 2>/dev/null; then
    ok "SURVIVE: $n present verbatim in design-schema.css"
  else
    bad "SURVIVE: $n MISSING from design-schema.css"
  fi
done

# 3) NEUTRALIZE — hostile payloads absent; no shadow emitted (whole value dropped, no salvage)
if ! python3 "$APPLY" "$FX/hostile-shadow.json" --target-brand "$TARGET" --out "$OUT/hostile" >/dev/null 2>&1; then
  bad "NEUTRALIZE: apply_schema.py exited non-zero on hostile-shadow.json fixture"
else
  HCSS="$OUT/hostile/design-schema.css"
  if [ ! -f "$HCSS" ]; then
    bad "NEUTRALIZE: apply_schema.py produced no $HCSS — cannot verify neutralization"
  else
    for n in "url(" "javascript:" "//exfil" "background:" "expression("; do
      if grep -qF -- "$n" "$HCSS" 2>/dev/null; then
        bad "NEUTRALIZE: hostile payload $n LEAKED into design-schema.css"
      else
        ok "NEUTRALIZE: hostile payload $n absent"
      fi
    done
    if grep -qF -- "--shadow-" "$HCSS" 2>/dev/null; then
      bad "NEUTRALIZE: a hostile shadow was emitted (partial salvage — must drop the whole value)"
    else
      ok "NEUTRALIZE: no hostile shadow emitted (whole value dropped)"
    fi
  fi
fi

# 4) IDENTITY (structural) — reference signature color absent (replaced by a target token),
#    and the output tree carries ZERO logo/image files under any name
if ! python3 "$APPLY" "$FX/identity-color-in-shadow.json" --target-brand "$TARGET" --out "$OUT/identity" >/dev/null 2>&1; then
  bad "IDENTITY: apply_schema.py exited non-zero on identity-color-in-shadow.json fixture"
elif ! python3 "$APPLY" "$FX/reference-with-logo-and-primary.json" --target-brand "$TARGET" --out "$OUT/bundle" >/dev/null 2>&1; then
  bad "IDENTITY: apply_schema.py exited non-zero on reference-with-logo-and-primary.json fixture"
elif [ ! -f "$OUT/identity/design-schema.css" ] || [ ! -f "$OUT/bundle/design-schema.css" ]; then
  bad "IDENTITY: apply_schema.py produced no design-schema.css under identity/ or bundle/ — cannot verify neutralization"
else
  if grep -qF -- "#e10098" "$OUT/identity/design-schema.css" "$OUT/bundle/design-schema.css" 2>/dev/null; then
    bad "IDENTITY: the reference signature color reached design-schema.css"
  else
    ok "IDENTITY: reference signature color absent (neutralized to a target token)"
  fi
  if grep -qF -- "var(--brand-shadow-color)" "$OUT/identity/design-schema.css" 2>/dev/null; then
    ok "IDENTITY: neutralized shadow references the target shadow token"
  else
    bad "IDENTITY: neutralized shadow did not use the target shadow token"
  fi
fi
imgs=$(find "$OUT" -type f \( -name '*.svg' -o -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \
  -o -name '*.gif' -o -name '*.webp' -o -name '*.ico' -o -name '*.avif' -o -name '*.bmp' \) 2>/dev/null | wc -l | tr -d ' ')
if [ "$imgs" = "0" ]; then
  ok "IDENTITY(structural): zero logo/image files in the output tree"
else
  bad "IDENTITY(structural): $imgs logo/image file(s) in the output tree"
fi

# 5) must-fail MUTANTS — prove the assertions have teeth (an anchor drift is a HARD fail, never
#    a silent must-fail pass)
_mutant() { # $1 label  $2 file  $3 old  $4 new  — ok iff the mutated self-test FAILS
  local d
  d="$(mktemp -d)"
  cp "$SKILL"/*.py "$d/" 2>/dev/null || {
    bad "$1: could not stage mutant"
    return
  }
  if ! python3 - "$d/$2" "$3" "$4" <<'PY'
import sys, pathlib
p, old, new = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
s = p.read_text()
if old not in s:
    sys.exit(3)  # anchor drifted — the mutant no longer targets real code
p.write_text(s.replace(old, new, 1))
PY
  then
    bad "$1: mutant anchor drifted (update the Gate 194 mutant)"
    return
  fi
  if python3 "$d/apply_schema.py" --self-test >/dev/null 2>&1; then
    bad "$1: self-test still PASSED on the mutant (the assertion is toothless)"
  else
    ok "$1: self-test catches the mutant"
  fi
}

_mutant "teeth m1 (css_shadow returns input verbatim → hostile appears)" \
  sanitizers.py \
  '    v = str(value).strip()
    if not v or _has_forbidden(v):
        return None
    layers = split_top_level(v, ",")' \
  '    return str(value)  # NEUTERED
    v = str(value).strip()
    if not v or _has_forbidden(v):
        return None
    layers = split_top_level(v, ",")'

_mutant "teeth m2 (css_length returns None for everything → SURVIVE fails)" \
  sanitizers.py \
  'def css_length(value: str) -> str | None:' \
  'def css_length(value: str) -> str | None:
    return None  # NEUTERED'

_mutant "teeth m3 (apply() reads colors.palette → reference color leaks)" \
  apply_schema.py \
  '    _ = design_schema
    return []' \
  '    return [c.get("value") for c in design_schema.get("colors", {}).get("palette", []) if isinstance(c, dict)]'

echo
if [ "$fails" -eq 0 ]; then
  echo "Gate 194 — design-clone bidirectional teeth: ALL PASS"
  exit 0
fi
echo "Gate 194 — design-clone: $fails assertion(s) FAILED"
exit 1
