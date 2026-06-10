#!/usr/bin/env bash
# Gate 101 — declarative-visualization security linter, bidirectional + teeth.
#
# Proves lint.py is a real gate, not a rubber stamp:
#   • must_pass: a clean spec + a clean SVG → exit 0.
#   • must_fail: data.url, loader override, transform.lookup w/ remote URL,
#     remote $schema, SVG <script>, SVG on* attribute → exit 1 each.
#   • path safety: a ".." path is rejected → exit 2.
#   • teeth: a mutant linter that hardcodes exit 0 makes a known-bad pass —
#     proving the real fail verdict is the logic, not luck.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
L="python3 plugins/ravenclaude-core/skills/declarative-visualization/lint.py"
F="tests/fixtures/declarative-viz"
rc_total=0

expect() { # desc, want_rc, file
  local rc=0
  $L "$3" >/dev/null 2>&1 || rc=$?
  if [[ "$rc" -eq "$2" ]]; then
    echo "  ✓ $1 (exit $rc)"
  else
    echo "  ✗ $1 — wanted exit $2, got $rc"
    rc_total=1
  fi
}

echo "── Gate 101: declarative-viz linter ──────────────────────────────────────"

# must_pass — clean fixtures
expect "clean JSON spec passes"                    0 "$F/good-spec.json"
expect "clean SVG passes"                          0 "$F/good-svg.svg"
expect "SVG local fragment href passes"            0 "$F/good-svg-local-ref.svg"

# must_fail — each security vector individually
expect "data.url → exit 1"                         1 "$F/bad-spec-data-url.json"
expect "loader override → exit 1"                  1 "$F/bad-spec-loader.json"
expect "transform.lookup w/ remote URL → exit 1"   1 "$F/bad-spec-transform-lookup.json"
expect "remote \$schema host → exit 1"             1 "$F/bad-spec-remote-schema.json"
expect "SVG <script> → exit 1"                     1 "$F/bad-svg-script.svg"
expect "SVG on* attribute → exit 1"                1 "$F/bad-svg-on-attr.svg"
expect "SVG <foreignObject> → exit 1"              1 "$F/bad-svg-foreign-object.svg"
expect "SVG remote xlink:href → exit 1"            1 "$F/bad-svg-remote-href.svg"
expect "SVG javascript: href → exit 1"             1 "$F/bad-svg-javascript-href.svg"

# path safety — ".." traversal → exit 2
rc=0; $L "../../etc/passwd" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 2 ]]; then
  echo "  ✓ path-traversal rejected (exit 2)"
else
  echo "  ✗ path-traversal NOT rejected — wanted exit 2, got $rc"
  rc_total=1
fi

# teeth — a mutant that always exits 0 must let known-bad fixtures through
# (proving the real failure is logic, not coincidence or environment).
MUT="$(mktemp --suffix=.py)"
trap 'rm -f "$MUT"' EXIT
# Replace sys.exit(main()) with sys.exit(0) so the mutant always passes.
sed 's/sys.exit(main())/sys.exit(0)/' \
  plugins/ravenclaude-core/skills/declarative-visualization/lint.py >"$MUT"
rc=0; python3 "$MUT" "$F/bad-spec-data-url.json" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets data.url through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-spec-data-url (got $rc) — teeth assertion broken"
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

# also confirm the spec-patterns templates all pass the real linter
echo "  -- spec-patterns library --"
for f in plugins/ravenclaude-core/skills/declarative-visualization/spec-patterns/*.json; do
  rc=0; $L "$f" >/dev/null 2>&1 || rc=$?
  if [[ "$rc" -eq 0 ]]; then
    echo "  ✓ $(basename "$f") passes"
  else
    echo "  ✗ $(basename "$f") FAILED (exit $rc) — committed template must not have security violations"
    rc_total=1
  fi
done

if [[ "$rc_total" -eq 0 ]]; then
  echo "  Gate 101: PASS"
else
  echo "  Gate 101: FAIL"
fi
exit "$rc_total"
