#!/usr/bin/env bash
# check-geospatial-anti-patterns.sh — advisory PreToolUse hook for the geospatial-gis-engineering plugin.
# Flags mechanically-detectable spatial anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set GEOENG_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect files where these patterns are meaningful.
case "$file" in
  *.sql|*.py|*.js|*.ts|*.jsx|*.tsx|*.md|*.geojson|*.json) ;;
  *) exit 0 ;;
esac

findings=()
if grep -nEi 'st_distance[[:space:]]*\([^)]*\)[[:space:]]*<' "$file" >/dev/null 2>&1; then
  findings+=("ST_Distance(...) < d as a filter is non-sargable — use ST_DWithin(geom, pt, d) so the GiST index is used.")
fi
if grep -nEi 'st_(area|length)[[:space:]]*\(.*3857' "$file" >/dev/null 2>&1; then
  findings+=("Area/length computed in EPSG:3857 (Web Mercator) is badly distorted — measure with geography or a projected CRS (UTM/national grid).")
fi
if grep -nEi 'srid[[:space:]]*=[[:space:]]*0|st_setsrid[[:space:]]*\([^,]*,[[:space:]]*0[[:space:]]*\)' "$file" >/dev/null 2>&1; then
  findings+=("SRID 0 (unknown) — set a known SRID with ST_SetSRID/ST_Transform; enforce one SRID per column with a typmod.")
fi
if grep -nEi '\b(geometry|geography)\b[[:space:]]+(not|null|default|references|,)' "$file" >/dev/null 2>&1; then
  findings+=("geometry/geography column without a typmod — declare geometry(Type, SRID) so the SRID and geometry kind are enforced.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── geospatial-gis-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${GEOENG_STRICT:-0}" = "1" ]; then
  echo "(blocking: GEOENG_STRICT=1)" >&2
  exit 2
fi
exit 0
