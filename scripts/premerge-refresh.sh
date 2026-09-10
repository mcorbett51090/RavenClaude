#!/usr/bin/env bash
#
# premerge-refresh.sh — the one command to run right before merging a
# long-lived branch, once it is genuinely caught up with origin/main.
#
# ⛔ WHY THIS EXISTS. PR #1145 (2026-09-09, feat/skills-deny-plugins) needed
# five separate push-fix-wait cycles to go green, and every failure was a
# DIFFERENT generated artifact going stale on the SAME branch: dashboard.html,
# docs/concepts.md, the copilot/ package, and a concept's covers_digest each
# surfaced as their own CI failure in turn, because nothing regenerated all of
# them together in one pass — the branch reacted to whichever gate failed
# next instead of converging once. The final failure was worse than stale:
# `check-ratchet-freshness.py --stamp` was run WHILE a merge conflict was
# still being resolved (before `git commit` finalized it), so it silently
# stamped scripts/artifact-budgets.seed.json and
# tests/fixtures/inventory-coverage-ratchet.json against the OLD pre-merge
# merge-base (8734f755...) instead of the real one (41677552...) — exactly
# the PR #991 shape check-ratchet-freshness.py itself exists to catch, self-
# inflicted by running the stamp at the wrong moment.
#
# This script does not replace scripts/regen-inventory.sh (the P9 §11.6
# concepts/dashboard chain) — it CALLS it, then adds the two generators that
# chain does not cover (docs/concepts.md, the copilot/ package) plus the
# ratchet re-stamp, in the dependency order a real merge needs:
#
#     [merge-in-progress guard]
#       -> regen-inventory.sh              (concepts registry + dashboards + budgets)
#       -> generate-concepts-doc.py        (docs/concepts.md, reads the registry)
#       -> generate-copilot-plugin.py      (copilot/ package)
#       -> check-ratchet-freshness.py --stamp   (LAST — needs the real merge commit)
#
# ⛔ HONEST SCOPE. This is not "regenerate every generated artifact in the
# repo" — audit-gates.sh wires roughly a dozen more (generate-aider-
# conventions.py, generate-codex-agents.py, generate-copilot-hooks.py,
# generate-cursor-hooks.py, generate-gemini-hooks.py, generate-skill-
# index.py, sync-plugin-versions.py, generate-bi-report.py, generate-
# feedback-report.py, ...). This script covers exactly the chain one real
# incident (PR #1145) proved goes stale together on a long-lived branch,
# not a general audit of every `--check` gate in the suite. Extend it if
# another chain earns the same repeated-failure evidence.
#
# ⛔ THE MERGE-IN-PROGRESS GUARD IS THE POINT, NOT A NICETY. Re-running
# check-ratchet-freshness.py --stamp after a stale stamp does NOT self-heal
# if it is run again before the merge commit exists — it just re-computes
# the same wrong base. The only fix is running it AFTER `git commit`
# finalizes the merge, which is what this guard enforces.
#
# Usage:
#   scripts/premerge-refresh.sh              # base = origin/main
#   scripts/premerge-refresh.sh --base <ref>
#
# Exit 2 (refuses to run) while a merge is unresolved. Exit 1 if any step
# fails. Exit 0 only when every step succeeded — review `git status` /
# `git diff --stat` afterward and commit the regenerated files.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 2

BASE="origin/main"
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE="${2:-origin/main}"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

# ⛔ Refuse outright if a merge is still in progress — this is the exact
# mistiming that corrupted the ratchet stamp on PR #1145.
if git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1; then
  echo "⛔ MERGE_HEAD is present — a merge is still in progress, not finalized." >&2
  echo "   Resolve every conflict and run 'git commit' first. Stamping the" >&2
  echo "   ratchet now would bind it to the OLD pre-merge base, not the real" >&2
  echo "   one — the exact PR #1145 bug this script exists to prevent." >&2
  exit 2
fi
unmerged="$(git diff --name-only --diff-filter=U 2>/dev/null || true)"
if [ -n "$unmerged" ]; then
  echo "⛔ Unresolved conflict markers remain in:" >&2
  echo "$unmerged" | sed 's/^/     /' >&2
  exit 2
fi

rc=0
step() { # label command...
  local label="$1"; shift
  printf -- '── %s\n' "$label"
  if "$@"; then
    printf '   ok\n'
  else
    printf '   FAILED (%s)\n' "$label"
    rc=1
  fi
}

step "1/4 regen-inventory.sh — concepts registry + dashboards + budgets" \
  bash scripts/regen-inventory.sh

step "2/4 generate-concepts-doc.py — docs/concepts.md" \
  python3 scripts/generate-concepts-doc.py

step "3/4 generate-copilot-plugin.py — copilot/ package" \
  python3 scripts/generate-copilot-plugin.py

# ⛔ LAST, always — see the header. Only reached once the guard above has
# confirmed there is no merge in progress, so HEAD is the real merge commit
# and `merge-base(HEAD, $BASE)` reflects it.
if [ "$rc" -eq 0 ]; then
  step "4/4 check-ratchet-freshness.py --stamp --base $BASE" \
    python3 scripts/check-ratchet-freshness.py --stamp --base "$BASE"
else
  printf '── 4/4 check-ratchet-freshness.py — SKIPPED (an earlier step failed)\n'
fi

echo
if [ "$rc" -ne 0 ]; then
  echo "⛔ premerge-refresh FAILED. Do not commit a half-regenerated tree — fix" \
    "the failing step and re-run the whole chain, not just that one script."
  exit 1
fi
echo "✓ concepts registry, dashboards, docs/concepts.md, copilot/ package, and"
echo "  the ratchet stamp are all fresh against $BASE."
echo
echo "  Review before committing:"
echo "    git status"
echo "    git diff --stat"
