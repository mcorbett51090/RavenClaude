#!/usr/bin/env bash
# flag-geo-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on spatial files (.sql/.py/.js/.ts/
# .md). Flags three mechanically-detectable violations of the geospatial-engineering
# team constitution (see plugins/geospatial-engineering/CLAUDE.md and the
# best-practices/ rules):
#
#   1. A geometry/geography column created with NO SRID
#      (e.g. `geometry(Point)` or bare `geometry` with no SRID argument)
#      — always-store-an-srid: a column without an explicit SRID silently mixes
#      coordinate systems.
#   2. ST_Distance / ST_DWithin called on a geometry in degrees instead of
#      geography/projected metres — degree distances are meaningless on the ground.
#   3. An `ST_Distance(...) <` proximity filter (use ST_DWithin so the GiST index
#      applies) — index-geometry-with-gist.
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set GEO_SMELLS_STRICT=1 to make
# violations blocking (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to
# the agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

# Only inspect spatial-shaped files.
case "$base_lc" in
  *.sql | *.py | *.js | *.ts | *.md) ;;
  *) exit 0 ;;
esac

violations=()

# ---------------------------------------------------------------------------
# Check 1: a geometry/geography column declared with no SRID.
# Matches `geometry(Point)` / `geography(MultiPolygon)` / bare `geometry`/`geography`
# used as a column type, where no numeric SRID follows. The SRID form
# `geometry(Point, 4326)` has a digit after a comma inside the parens and is NOT
# flagged.
# ---------------------------------------------------------------------------
# Typed-but-no-SRID: geometry(Point)  geography( LineString )  — closing paren with
# no comma+digits before it.
no_srid_typed_re='\b(geometry|geography)\s*\(\s*(multi)?(point|linestring|polygon|geometrycollection)\s*\)'
# Bare type used as a column declaration: a column name followed by `geometry`/
# `geography` and then NOT an opening paren (so no SRID can be specified).
bare_type_re='\b(geometry|geography)\b'
srid_present_re='\b(geometry|geography)\s*\(\s*(multi)?(point|linestring|polygon|geometrycollection)\s*,\s*[0-9]+'

if grep -niEq "$no_srid_typed_re" "$file" 2>/dev/null; then
  violations+=("A geometry/geography column is declared with a type but NO SRID (e.g. geometry(Point)). Declare the SRID explicitly — geometry(Point, 4326) — or coordinate systems mix silently. (always-store-an-srid)")
elif grep -niEq "add_?geometry_?column" "$file" 2>/dev/null; then
  # AddGeometryColumn(...) without a 4-digit SRID arg is the legacy-API form of the
  # same smell; flag only if no SRID-shaped column is present elsewhere.
  if ! grep -niEq "$srid_present_re" "$file" 2>/dev/null; then
    violations+=("AddGeometryColumn used — confirm an explicit SRID argument is passed. A missing/zero SRID mixes coordinate systems silently. (always-store-an-srid)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 2: distance on a geometry that looks like it is in 4326 / degrees.
# Heuristic: the file uses ST_Distance/ST_DWithin AND mentions 4326/geometry but
# never casts to geography or ST_Transforms — i.e. the distance is in degrees.
# ---------------------------------------------------------------------------
dist_re='st_distance|st_dwithin'
degrees_hint_re='4326|geometry\s*\('
metres_safe_re='::geography|geography\s*\(|st_transform'

if grep -niEq "$dist_re" "$file" 2>/dev/null; then
  if grep -niEq "$degrees_hint_re" "$file" 2>/dev/null; then
    if ! grep -niEq "$metres_safe_re" "$file" 2>/dev/null; then
      violations+=("A distance (ST_Distance/ST_DWithin) is computed on a geometry that looks like EPSG:4326 — those distances are DEGREES, not metres. Cast to ::geography or ST_Transform to a metric CRS. (degree-distance smell)")
    fi
  fi
fi

# ---------------------------------------------------------------------------
# Check 3: ST_Distance(...) < ...  proximity filter (defeats the GiST index).
# ---------------------------------------------------------------------------
# `|| true` keeps a no-match grep (exit 1) under `set -o pipefail` from aborting
# the advisory hook on a clean file.
if grep -niEq 'st_distance\s*\([^)]*\)\s*<' "$file" 2>/dev/null; then
  violations+=("An ST_Distance(...) < d proximity filter computes a distance per row and defeats the GiST index. Use ST_DWithin(a, b, d) so the spatial index applies. (index-geometry-with-gist)")
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

echo "" >&2
echo "[geospatial-engineering-smells] Advisory warnings for ${file}:" >&2
for v in "${violations[@]}"; do
  echo "  - ${v}" >&2
done
echo "" >&2
echo "  Advisory by default. Set GEO_SMELLS_STRICT=1 to make them blocking." >&2
echo "  See plugins/geospatial-engineering/best-practices/ for the fixes." >&2
echo "" >&2

if [[ "${GEO_SMELLS_STRICT:-0}" == "1" ]]; then
  # exit 2 = BLOCK (Claude Code PreToolUse blocking code); exit 1 is non-blocking
  # and would silently allow the edit despite the warning.
  exit 2
fi
exit 0
