#!/usr/bin/env bash
# check-web-anti-patterns.sh
# PostToolUse hook for Edit | Write | MultiEdit on web-conventional files.
# Flags mechanically-detectable violations of the web-design team constitution
# (see plugins/web-design/CLAUDE.md §3 "house opinions" and §4 "anti-patterns"):
#
#   1. Oversized raster image committed (> 500 KB jpg / png / webp).
#      §4 — image > 500 KB above-the-fold.
#   2. `<img>` tag missing alt attribute. §3 #5, §4 — semantic HTML.
#   3. Hardcoded hex color in JSX / TSX / CSS (outside files named tokens.*).
#      §3 #4 — design tokens, not hardcoded values.
#   4. HTML page missing <title> or <meta name="description">. §4 — pages
#      with no title / description.
#   5. <meta name="robots" content="noindex"> in shipped page. §4 — noindex
#      accidentally in production.
#
# Advisory by default: prints warnings to stderr so Claude and the user
# both see them, but exits 0 so the edit is not blocked. To make this hook
# BLOCK on violation, change `exit 0` to `exit 1`.

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Allow token files to define hex colors (that's their job).
case "$file" in
  *tokens*|*design-tokens*|*colors.*|*palette.*) skip_color_check=1 ;;
  *) skip_color_check=0 ;;
esac

# Scope: web-conventional file extensions OR locations.
case "$file" in
  *.html|*.htm|*.jsx|*.tsx|*.vue|*.svelte|*.astro|*.css|*.scss|*.sass|*.less) ;;
  *.jpg|*.jpeg|*.png|*.webp|*.avif|*.gif) ;;
  */src/*|*/public/*|*/assets/*|*/static/*) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: Oversized raster image ---
case "$file" in
  *.jpg|*.jpeg|*.png|*.webp|*.gif)
    size_bytes=$(wc -c < "$file" 2>/dev/null | tr -d ' ')
    # Threshold: 500 KB = 512000 bytes.
    if [[ -n "$size_bytes" && "$size_bytes" -gt 512000 ]]; then
      kb=$(( size_bytes / 1024 ))
      violations+=("  [oversized-raster] $file is ${kb} KB — > 500 KB threshold. Compress, convert to AVIF/WebP, or right-size before commit. See house opinion §4.")
    fi
    ;;
esac

# --- Check 2: <img> missing alt ---
# Heuristic regex: <img with no alt attribute on the same tag.
# Allows alt="" (decorative). Multi-line tags partially caught.
case "$file" in
  *.html|*.htm|*.jsx|*.tsx|*.vue|*.svelte|*.astro|*.md)
    # Find <img tags without alt= in a reasonable lookahead range.
    # Single-line check; multi-line is best-effort.
    if grep -Eni '<img[^>]*>' "$file" 2>/dev/null | grep -Eiv 'alt\s*=' >/dev/null 2>&1; then
      while IFS= read -r line; do
        violations+=("  [img-missing-alt] $file: $line — every <img> needs alt= (decorative uses alt=\"\").")
      done < <(grep -En '<img[^>]*>' "$file" | grep -Eiv 'alt\s*=' | head -3)
    fi
    ;;
esac

# --- Check 3: Hardcoded hex color outside token files ---
if [[ "$skip_color_check" -eq 0 ]]; then
  case "$file" in
    *.css|*.scss|*.sass|*.less|*.jsx|*.tsx|*.vue|*.svelte|*.astro)
      # 3 or 6 hex chars (case-insensitive). Common values that often
      # represent tokens like #fff/#000 are flagged too — review them.
      if grep -Eni '#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?\b' "$file" >/dev/null 2>&1; then
        while IFS= read -r line; do
          violations+=("  [hardcoded-color] $file: $line — use a design token instead. See house opinion §3 #4.")
        done < <(grep -En '#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?\b' "$file" | head -3)
      fi
      ;;
  esac
fi

# --- Check 4: HTML page missing title or description ---
# Apply only to top-level HTML pages, not partials / components.
case "$file" in
  *.html|*.htm)
    # Skip files that look like partials / components.
    case "$file" in
      *partial*|*component*|*include*|*fragment*) ;;
      *)
        if ! grep -qEi '<title>[^<]+</title>' "$file" 2>/dev/null; then
          violations+=("  [missing-title] $file has no <title> tag. House opinion §4 — pages with no title.")
        fi
        if ! grep -qEi '<meta[^>]+name=["'\'']description["'\''][^>]+content=["'\''][^"'\'']+["'\'']' "$file" 2>/dev/null; then
          violations+=("  [missing-meta-description] $file has no <meta name=\"description\"> tag. House opinion §4.")
        fi
        ;;
    esac
    ;;
esac

# --- Check 5: Accidental noindex robots meta in production-looking HTML ---
case "$file" in
  *.html|*.htm)
    if grep -qEi '<meta[^>]+name=["'\'']robots["'\''][^>]+content=["'\''][^"'\'']*noindex' "$file" 2>/dev/null; then
      violations+=("  [accidental-noindex] $file declares <meta name=\"robots\" content=\"noindex\">. Verify this is intentional. House opinion §4.")
    fi
    ;;
esac

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Web-design house-opinion check flagged ${#violations[@]} issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/web-design/CLAUDE.md §3 (house opinions) and §4
  (anti-patterns) for the full rules. This hook is advisory — the
  edit was not blocked. To enforce, change `exit 0` to `exit 1` at
  the bottom of plugins/web-design/hooks/check-web-anti-patterns.sh.
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
