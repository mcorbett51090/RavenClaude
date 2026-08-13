#!/usr/bin/env bash
# Gate 101 — declarative-visualization linter (security + quality), bidirectional + teeth.
#
# Proves lint.py is a real gate, not a rubber stamp:
#   Tier 1 (security):
#   • must_fail: data.url, loader override, transform.lookup w/ remote URL,
#     remote $schema, SVG <script>, SVG on*, <foreignObject>, remote href → exit 1.
#   Tier 2 (quality / correctness):
#   • must_fail: encoding-incomplete bar → exit 1 (encoding-completeness).
#   • must_fail: unknown mark type → exit 1 (spec-hygiene-mark).
#   • must_pass: Vega signal WITHOUT --strict → exit 0 (warning only).
#   • must_fail: Vega signal WITH --strict → exit 1 (security-surface-flag).
#   • must_pass: color-only encoding → exit 0 (accessibility-channel is warning only).
#   Path safety: ".." path → exit 2.
#   Teeth: a mutant that hardcodes exit 0 must let known-bad fixtures through.
#   Spec-patterns library: all committed templates must pass.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
L="python3 plugins/ravenclaude-core/skills/declarative-visualization/lint.py"
F="tests/fixtures/declarative-viz"
rc_total=0

expect() { # desc, want_rc, file [extra_args...]
  local desc="$1" want="$2" file="$3"
  shift 3
  local rc=0
  $L "$file" "$@" >/dev/null 2>&1 || rc=$?
  if [[ "$rc" -eq "$want" ]]; then
    echo "  ✓ $desc (exit $rc)"
  else
    echo "  ✗ $desc — wanted exit $want, got $rc"
    rc_total=1
  fi
}

echo "── Gate 101: declarative-viz linter ──────────────────────────────────────"

# ── Tier 1: security (must_pass clean, must_fail each vector) ────────────────
expect "clean JSON spec passes"                    0 "$F/good-spec.json"
expect "clean SVG passes"                          0 "$F/good-svg.svg"
expect "SVG local fragment href passes"            0 "$F/good-svg-local-ref.svg"

expect "data.url → exit 1"                         1 "$F/bad-spec-data-url.json"
expect "loader override → exit 1"                  1 "$F/bad-spec-loader.json"
expect "transform.lookup w/ remote URL → exit 1"   1 "$F/bad-spec-transform-lookup.json"
expect "remote \$schema host → exit 1"             1 "$F/bad-spec-remote-schema.json"
expect "SVG <script> → exit 1"                     1 "$F/bad-svg-script.svg"
expect "SVG on* attribute → exit 1"                1 "$F/bad-svg-on-attr.svg"
expect "SVG <foreignObject> → exit 1"              1 "$F/bad-svg-foreign-object.svg"
expect "SVG remote xlink:href → exit 1"            1 "$F/bad-svg-remote-href.svg"
expect "SVG javascript: href → exit 1"             1 "$F/bad-svg-javascript-href.svg"
expect "SVG entity-encoded javascript: href → exit 1" 1 "$F/bad-svg-entity-encoded-href.svg"

# ── Tier 2: quality / correctness ────────────────────────────────────────────
expect "encoding-incomplete bar → exit 1"          1 "$F/bad-spec-encoding-incomplete.json"
expect "unknown mark type → exit 1"                1 "$F/bad-spec-unknown-mark.json"
expect "Vega signal (default) → exit 0 (warn)"     0 "$F/bad-spec-vega-signal.json"
expect "Vega signal (--strict) → exit 1"           1 "$F/bad-spec-vega-signal.json" "--strict"
expect "color-only encoding → exit 0 (warn)"       0 "$F/good-spec-color-only.json"

# ── Path safety ───────────────────────────────────────────────────────────────
rc=0; $L "../../etc/passwd" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 2 ]]; then
  echo "  ✓ path-traversal rejected (exit 2)"
else
  echo "  ✗ path-traversal NOT rejected — wanted exit 2, got $rc"
  rc_total=1
fi

# ── Teeth: a mutant that always exits 0 must let known-bad fixtures through ──
# PORTABILITY: `mktemp --suffix=` is a GNU long option; BSD/macOS mktemp rejects it
# ("usage: mktemp ..."), which failed this gate on every mac. `mktemp -d` + a fixed
# filename is portable and gives the same .py suffix. (2026-07-15)
MUT="$(mktemp -d)/mut.py"
trap 'rm -f "$MUT"' EXIT
sed 's/sys.exit(main())/sys.exit(0)/' \
  plugins/ravenclaude-core/skills/declarative-visualization/lint.py >"$MUT"
rc=0; python3 "$MUT" "$F/bad-spec-data-url.json" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets data.url through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-spec-data-url (got $rc) — teeth assertion broken"
  rc_total=1
fi
rc=0; python3 "$MUT" "$F/bad-spec-encoding-incomplete.json" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets encoding-incomplete through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-spec-encoding-incomplete (got $rc) — teeth broken"
  rc_total=1
fi
rc=0; python3 "$MUT" "$F/bad-svg-foreign-object.svg" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets <foreignObject> through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-svg-foreign-object (got $rc) — teeth assertion broken"
  rc_total=1
fi
rc=0; python3 "$MUT" "$F/bad-svg-remote-href.svg" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets remote xlink:href through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-svg-remote-href (got $rc) — teeth assertion broken"
  rc_total=1
fi

# ── Spec-patterns library: all committed templates must pass ─────────────────
echo "  -- spec-patterns library --"
for f in plugins/ravenclaude-core/skills/declarative-visualization/spec-patterns/*.json; do
  rc=0; $L "$f" >/dev/null 2>&1 || rc=$?
  if [[ "$rc" -eq 0 ]]; then
    echo "  ✓ $(basename "$f") passes"
  else
    echo "  ✗ $(basename "$f") FAILED (exit $rc) — committed template must not have violations"
    rc_total=1
  fi
done

if [[ "$rc_total" -eq 0 ]]; then
  echo "  Gate 101: PASS"
else
  echo "  Gate 101: FAIL"
fi
exit "$rc_total"
