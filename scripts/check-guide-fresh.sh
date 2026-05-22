#!/usr/bin/env bash
# check-guide-fresh.sh — verify repo-guide.html (at the repo root) is up-to-date relative to
# the marketplace + plugin manifests + agent/skill/hook/rule/template files.
#
# How it works:
#   1. Regenerate the guide to a tempfile (using --check, which prints to stdout).
#   2. Strip the volatile "Generated …" timestamp line from both the tempfile
#      and the committed file before comparing — so a stale check doesn't
#      trigger just because someone re-ran the script locally and committed
#      a fresh timestamp.
#   3. Diff. Non-zero exit means the committed HTML is stale; the developer
#      must re-run `python3 scripts/generate-repo-guide.py` and commit the result.
#
# Exit codes:
#   0 — committed guide matches the regenerated content (modulo timestamp)
#   1 — committed guide is stale; needs regeneration
#   2 — committed guide is missing entirely
#   3 — generator script itself is missing or failed

set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
generator="$repo_root/scripts/generate-repo-guide.py"
committed="$repo_root/repo-guide.html"

if [[ ! -x "$generator" && ! -f "$generator" ]]; then
  echo "::error::generator script not found at $generator" >&2
  exit 3
fi

if [[ ! -f "$committed" ]]; then
  echo "::error::repo-guide.html is missing. Run: python3 scripts/generate-repo-guide.py" >&2
  exit 2
fi

# Regenerate to a tempfile.
tmp="$(mktemp -t repo-guide.XXXXXX.html)"
trap 'rm -f "$tmp"' EXIT

if ! python3 "$generator" --check > "$tmp" 2>/dev/null; then
  echo "::error::generator failed; cannot verify freshness" >&2
  exit 3
fi

# Strip volatile lines from both sides before diffing.
# - "Generated YYYY-…" — timestamp set at generation time
# - "Last updated</span>" — per-plugin git-log date; CI uses shallow checkout so
#    the value differs from a full-history local clone. Strip from both sides.
strip_volatile() {
  grep -Ev 'Generated 20[0-9][0-9]-|Last updated</span>' "$1" 2>/dev/null || true
}

if diff -q <(strip_volatile "$committed") <(strip_volatile "$tmp") > /dev/null 2>&1; then
  echo "repo-guide.html is up to date."
  exit 0
fi

echo "::error::repo-guide.html is stale relative to the marketplace + plugin sources." >&2
echo "Run \`python3 scripts/generate-repo-guide.py\` and commit the result." >&2
diff <(strip_volatile "$committed") <(strip_volatile "$tmp") | head -40 >&2 || true
exit 1
