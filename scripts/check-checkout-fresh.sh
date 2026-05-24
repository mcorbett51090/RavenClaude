#!/usr/bin/env bash
# check-checkout-fresh.sh — advisory pre-test freshness check.
#
# WHY THIS EXISTS
# ---------------
# Verification run against a stale checkout gives misleading answers: a fix already
# merged to origin/main can look "not done" locally, and local-only work can look
# shipped. This script warns up front when the current checkout is behind
# origin/main so a test run is never silently trusted against a stale tree.
#
# NOT A CI GATE (deliberately). It enforces no property of the committed code, so it
# has no must_fail / must_pass fixture pair in scripts/audit-gates.sh — see the
# "Edge cases" carve-out for advisory / freshness steps in
# docs/best-practices/ci-gate-audit.md ("the exclusion is the documentation"). It is
# wired into AGENTS.md "Testing instructions" (step 0), NOT into the hermetic,
# offline-safe audit-gates.sh.
#
# BEHAVIOR
#   - Advisory by default: prints a warning to stderr when behind, exits 0.
#   - --strict   : exit 1 when behind (for anyone who wants a hard pre-test gate).
#   - --no-fetch : compare against the already-fetched remote-tracking ref only.
#   - Auto-skips entirely when $CI is set: in CI the checkout is the ref under test
#     and being "behind main" is normal/intended for a PR branch.
#   - Bounded + offline-safe: the `git fetch` is timeout-bounded and degrades to an
#     advisory skip if origin is unreachable — an offline laptop must never block the
#     dev loop.
#
# Idempotent and read-only (a fetch updates only remote-tracking refs).

set -euo pipefail

top=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$top" || exit 0

REMOTE=origin
BASE=main

fetch=1
strict=0
for arg in "$@"; do
  case "$arg" in
    --no-fetch) fetch=0 ;;
    --strict) strict=1 ;;
    -h | --help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
  esac
done

# In CI the checkout is exactly the ref under test; "behind main" is expected.
[[ -n "${CI:-}" ]] && exit 0

# Refresh the remote-tracking ref (bounded; offline degrades to an advisory skip).
if [[ "$fetch" -eq 1 ]]; then
  if ! timeout 10 git fetch -q "$REMOTE" "$BASE" 2>/dev/null; then
    echo "  ~ checkout-freshness: could not reach $REMOTE (offline?). Skipping check." >&2
    exit 0
  fi
fi

# Need a remote-tracking origin/main to compare against.
git rev-parse --verify -q "$REMOTE/$BASE" >/dev/null || exit 0

behind=$(git rev-list --count "HEAD..$REMOTE/$BASE" 2>/dev/null || echo 0)
ahead=$(git rev-list --count "$REMOTE/$BASE..HEAD" 2>/dev/null || echo 0)

# Also report distance from the branch's own upstream, if it has one and it differs.
upstream_note=""
if up=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null); then
  if [[ "$up" != "$REMOTE/$BASE" ]]; then
    ub=$(git rev-list --count "HEAD..$up" 2>/dev/null || echo 0)
    upstream_note="  (vs upstream ${up}: behind ${ub})"
  fi
fi

if [[ "$behind" -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Checkout is ${behind} commit(s) BEHIND ${REMOTE}/${BASE} (ahead ${ahead}).${upstream_note}
  Verification may be running against a STALE tree — results can mislead
  (a fix already merged upstream can look "not done", and vice versa).

  Sync before trusting test results:
      git fetch ${REMOTE} && git switch ${BASE} && git pull --ff-only
  (or rebase your feature branch onto ${REMOTE}/${BASE})
────────────────────────────────────────────────────────────────────
EOF
  [[ "$strict" -eq 1 ]] && exit 1
fi

exit 0
