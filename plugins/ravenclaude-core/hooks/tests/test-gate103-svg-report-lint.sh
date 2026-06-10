#!/usr/bin/env bash
# Gate 103 — svg-report-lint (geometry + security), bidirectional + teeth.
#
# Proves lint.py is a real gate, not a rubber stamp:
#   Geometry:
#   • must_fail: no viewBox → exit 1 (viewbox-present).
#   • must_fail: extreme aspect ratio → exit 1 (viewbox-sane-aspect).
#   • must_fail: font-size below minimum → exit 1 (text-min-fontsize).
#   Security:
#   • must_fail: <script> element → exit 1 (no-script).
#   • must_fail: on* event attribute → exit 1 (no-inline-handlers).
#   • must_fail: <foreignObject> element → exit 1 (no-foreign-object).
#   • must_fail: remote xlink:href → exit 1 (no-remote-href).
#   Path safety: ".." path → exit 2.
#   Teeth: a mutant that hardcodes exit 0 must let known-bad fixtures through.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
L="python3 plugins/ravenclaude-core/skills/svg-report-lint/lint.py"
F="tests/fixtures/svg-report"
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

echo "── Gate 103: svg-report-lint ──────────────────────────────────────────────"

# ── Clean fixture must pass ───────────────────────────────────────────────────
expect "clean SVG badge passes"                     0 "$F/good-badge.svg"

# ── Geometry checks (must_fail) ───────────────────────────────────────────────
expect "no viewBox → exit 1"                        1 "$F/bad-svg-no-viewbox.svg"
expect "extreme aspect ratio → exit 1"              1 "$F/bad-svg-bad-aspect.svg"
expect "tiny font-size → exit 1"                    1 "$F/bad-svg-tiny-font.svg"

# ── Security checks (must_fail) ───────────────────────────────────────────────
expect "<script> element → exit 1"                  1 "$F/bad-svg-script.svg"
expect "on* event attribute → exit 1"               1 "$F/bad-svg-on-attr.svg"
expect "<foreignObject> element → exit 1"           1 "$F/bad-svg-foreign-object.svg"
expect "remote xlink:href → exit 1"                 1 "$F/bad-svg-remote-href.svg"
expect "entity-encoded javascript: href → exit 1"   1 "$F/bad-svg-entity-encoded-href.svg"

# ── --min-fontsize flag ───────────────────────────────────────────────────────
# bad-svg-tiny-font.svg has font-size 4px; raising threshold to 3 should still fail,
# but lowering to 3 (below 4) should pass.
expect "tiny font passes with --min-fontsize 3"     0 "$F/bad-svg-tiny-font.svg" "--min-fontsize" "3"
expect "tiny font fails with --min-fontsize 5"      1 "$F/bad-svg-tiny-font.svg" "--min-fontsize" "5"

# ── Path safety ───────────────────────────────────────────────────────────────
rc=0; $L "../../etc/passwd" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 2 ]]; then
  echo "  ✓ path-traversal rejected (exit 2)"
else
  echo "  ✗ path-traversal NOT rejected — wanted exit 2, got $rc"
  rc_total=1
fi

# ── Teeth: a mutant that always exits 0 must let known-bad fixtures through ──
MUT="$(mktemp --suffix=.py)"
trap 'rm -f "$MUT"' EXIT
sed 's/sys.exit(main())/sys.exit(0)/' \
  plugins/ravenclaude-core/skills/svg-report-lint/lint.py >"$MUT"

rc=0; python3 "$MUT" "$F/bad-svg-script.svg" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets <script> through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-svg-script (got $rc) — teeth assertion broken"
  rc_total=1
fi

rc=0; python3 "$MUT" "$F/bad-svg-on-attr.svg" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets on* attribute through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-svg-on-attr (got $rc) — teeth assertion broken"
  rc_total=1
fi

rc=0; python3 "$MUT" "$F/bad-svg-no-viewbox.svg" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets no-viewBox through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-svg-no-viewbox (got $rc) — teeth assertion broken"
  rc_total=1
fi

rc=0; python3 "$MUT" "$F/bad-svg-remote-href.svg" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant lets remote xlink:href through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass bad-svg-remote-href (got $rc) — teeth assertion broken"
  rc_total=1
fi

if [[ "$rc_total" -eq 0 ]]; then
  echo "  Gate 103: PASS"
else
  echo "  Gate 103: FAIL"
fi
exit "$rc_total"
