#!/usr/bin/env bash
# flag-seo-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on SEO-shaped files
# (.txt/.xml/.html/.htm/.md). Flags four mechanically-detectable violations of the
# technical-seo-engineering team constitution (see the CLAUDE.md and best-practices/):
#
#   1. A path that is both robots.txt `Disallow`-ed AND carries a `noindex` /
#      `rel=canonical` in the same file — the engine never crawls a disallowed URL,
#      so the directive is never read. (noindex-removes-disallow-hides /
#      never-block-a-page-you-also-canonicalize / one-canonical-signal-set)
#   2. A redirect CHAIN, or a 302 used for what reads as a permanent move —
#      permanent moves are 301, one hop, direct to the final URL.
#      (redirects-are-301-and-one-hop)
#   3. An HTTP 200 returned alongside "not found"/"no results" text — a likely
#      SOFT 404. Return a real 404/410. (render-what-you-want-indexed)
#   4. A quoted FID (First Input Delay) metric — FID was replaced by INP; quoting
#      it dates the analysis and the threshold. (measure-core-web-vitals-in-the-field)
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set SEO_SMELLS_STRICT=1 to make
# violations blocking (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to the
# agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

# Only inspect SEO-shaped files.
case "$base_lc" in
  *.txt | *.xml | *.html | *.htm | *.md) ;;
  *) exit 0 ;;
esac

violations=()

# ---------------------------------------------------------------------------
# Check 1: a Disallow rule alongside a noindex / rel=canonical in the same file.
# A disallowed URL is never crawled, so the noindex/canonical tag is never read.
# Heuristic: the file contains both a robots.txt-style `Disallow:` AND a `noindex`
# or `rel=canonical` — the classic contradictory-signal own-goal.
# ---------------------------------------------------------------------------
if grep -niEq '^\s*disallow\s*:' "$file" 2>/dev/null; then
  if grep -niEq 'noindex|rel\s*=\s*["'\'']?canonical' "$file" 2>/dev/null; then
    violations+=("This file mixes a robots.txt 'Disallow' with a 'noindex'/'rel=canonical'. A disallowed URL is never crawled, so the engine never reads the noindex/canonical — to deindex, ALLOW the crawl and serve noindex; to consolidate, keep it crawlable and canonical. (noindex-removes-disallow-hides / one-canonical-signal-set)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 2: a redirect chain or a 302 used for a permanent move.
# ---------------------------------------------------------------------------
# A line with two redirect arrows / two target URLs is a likely chain.
if grep -niEq '(->|=>).*(->|=>)' "$file" 2>/dev/null && grep -niEq 'redirect|301|302' "$file" 2>/dev/null; then
  violations+=("A redirect line appears to have more than one hop (a chain A->B->C). Point each redirect DIRECTLY at the final URL — chains bleed signal and waste crawl budget. (redirects-are-301-and-one-hop)")
fi
# A 302 next to "permanent" / migration language.
if grep -niEq '\b302\b' "$file" 2>/dev/null; then
  if grep -niEq 'permanent|migrat|moved|replatform' "$file" 2>/dev/null; then
    violations+=("A 302 (temporary) redirect appears next to permanent-move language. A permanent move is a 301 — a 302 tells the engine to keep the OLD URL indexed. (redirects-are-301-and-one-hop)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 3: HTTP 200 alongside "not found" / "no results" — a likely soft 404.
# ---------------------------------------------------------------------------
if grep -niEq '\b200\b' "$file" 2>/dev/null; then
  if grep -niEq 'not[ _-]?found|no results|no matches|page does not exist' "$file" 2>/dev/null; then
    violations+=("An HTTP 200 appears alongside 'not found'/'no results' text — a likely SOFT 404. A not-found page must return a real 404 (or 410), not a 200 with empty content. (render-what-you-want-indexed)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 4: a quoted FID metric (replaced by INP).
# ---------------------------------------------------------------------------
if grep -niEq 'first input delay|\bFID\b' "$file" 2>/dev/null; then
  violations+=("This references FID (First Input Delay), which was replaced by INP (Interaction to Next Paint) as a Core Web Vital. Quoting FID dates the analysis and the threshold — use INP. (measure-core-web-vitals-in-the-field)")
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

echo "" >&2
echo "[technical-seo-engineering-smells] Advisory warnings for ${file}:" >&2
for v in "${violations[@]}"; do
  echo "  - ${v}" >&2
done
echo "" >&2
echo "  Advisory by default. Set SEO_SMELLS_STRICT=1 to make them blocking." >&2
echo "  See plugins/technical-seo-engineering/best-practices/ for the fixes." >&2
echo "" >&2

if [[ "${SEO_SMELLS_STRICT:-0}" == "1" ]]; then
  # exit 2 = BLOCK (Claude Code PreToolUse blocking code); exit 1 is non-blocking
  # and would silently allow the edit despite the warning.
  exit 2
fi
exit 0
