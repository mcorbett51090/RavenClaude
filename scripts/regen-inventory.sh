#!/usr/bin/env bash
#
# regen-inventory.sh — P9 §11.6. ONE command for the whole regeneration chain.
#
# ⛔ WHY A WRAPPER IS NOT A CONVENIENCE. Every authoring batch must regenerate in
# this exact order:
#
#     concepts.py -> render-concepts.py -> generate-dashboards.py
#                 -> generate-index-dashboard.py
#
# Twelve batches times four manual steps is forty-eight chances to regenerate out
# of order, and a stale generated artifact reddens CI for the RIGHT reason in a way
# that looks like the WRONG reason to an unfamiliar reader — they see the dashboard
# gate fail and go looking at the dashboard.
#
# ⛔ dashboard.html IS GENERATED AND ~10 MB. Regenerate it; never hand-edit it.
#
# ⛔ RENDERING IS OPT-IN AND BATCHED. Diagrams are optional on an inventory entry
# (concepts.py enforces that), and render-concepts.py needs mermaid-cli plus
# Chromium. So the render step only runs with --render, and the changed-concept
# gate caps a batch at 20.
#
# ⛔ THE BUDGETS ARE RE-CHECKED AT THE END, NOT ASSUMED. A batch that grows the
# island payload or the byte size past its ceiling must fail here, on the author
# machine, rather than on a PR where the cause is three steps away.
#
# ⛔ NO APOSTROPHES. See scripts/spike-tprose-canary.sh for why.
#
# Usage:
#   scripts/regen-inventory.sh              # registry + dashboards + budget check
#   scripts/regen-inventory.sh --render     # also re-render changed diagrams

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 2

RENDER=0
[ "${1:-}" = "--render" ] && RENDER=1

rc=0
step() { # label command...
  local label="$1"; shift
  printf '── %s\n' "$label"
  if "$@"; then
    printf '   ok\n'
  else
    printf '   FAILED (%s)\n' "$label"
    rc=1
  fi
}

# 1. The registry FIRST. Everything downstream embeds it.
step "1/5 concepts.py — rebuild the registry" python3 scripts/concepts.py

# 2. Diagrams, only when asked and only for what changed.
if [ "$RENDER" -eq 1 ]; then
  step "2/5 render-concepts.py — re-render diagrams (needs mermaid-cli + Chromium)" \
    python3 scripts/render-concepts.py
else
  printf '── 2/5 render-concepts.py — SKIPPED (pass --render to run it)\n'
  printf '   ⛔ A skip is not a pass. Diagrams are opt-in per entry; if this batch\n'
  printf '      added or changed one, re-run with --render or the SVGs go stale.\n'
fi

# 3+4. The two surfaces that embed the registry.
step "3/5 generate-dashboards.py — the plugin dashboard" python3 scripts/generate-dashboards.py
step "4/5 generate-index-dashboard.py — the marketplace index" python3 scripts/generate-index-dashboard.py

# 5. The budgets, re-measured on what was just written.
step "5/5 check-artifact-budgets.py — island payload + byte ceilings" \
  python3 scripts/check-artifact-budgets.py --check

echo
if [ "$rc" -ne 0 ]; then
  echo "⛔ regen-inventory FAILED. Do not commit a half-regenerated tree: the next"
  echo "   reader sees a freshness gate fail and looks at the wrong artifact."
  exit 1
fi
echo "✓ registry, dashboards and budgets are consistent."
echo
echo "  Next, in order:"
echo "    python3 scripts/concepts.py --check              # markers + drift"
echo "    python3 scripts/check-nuance-floor.py --check    # the shape floor"
echo "    python3 scripts/inventory-coverage.py --check    # ratchet + review ledger"
echo "    python3 scripts/check-ratchet-freshness.py --stamp   # ⛔ LAST, before merge"
