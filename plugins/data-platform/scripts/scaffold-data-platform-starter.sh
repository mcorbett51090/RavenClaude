#!/usr/bin/env bash
# scaffold-data-platform-starter.sh — copy a data-platform app starter out of
# the plugin (dev checkout or an installed-plugin cache) into a target
# directory, seed its .env from env.example, and print the next commands.
#
# FORGE dashboard-top1pct P3-20 (2026-09-03). Reconciles with CLAUDE.md's
# prior N/A disposition on a plugin bin/ script (§ "Value-add completeness",
# item 6): that reasoning was specifically about a bin/ LINTER duplicating
# the existing advisory hook — it never covered a scaffold-copy helper, and
# doesn't apply here. Without this script, using a starter today means
# manually finding the directory inside the plugin's installed cache and
# copying it by hand — the plugin's own leverage claim ("ten future
# dashboards each take an hour instead of a day") dies at that first manual
# step.
#
# Usage:
#   scaffold-data-platform-starter.sh <nextjs|astro> <target-dir>
#
# Portability: bash 3.2-safe (no associative arrays, no ${x^^}), matching
# ravenclaude-core/scripts/resolve-plugin-root.sh's own documented floor.

set -euo pipefail

usage() {
  echo "Usage: $0 <nextjs|astro> <target-dir>" >&2
  echo "  nextjs -> templates/cube-nextjs-dashboard-starter/ (Case C, always-interactive)" >&2
  echo "  astro  -> templates/cube-astro-dashboard-starter/  (Case C, Astro islands)" >&2
  exit 1
}

[[ $# -eq 2 ]] || usage

STARTER_KEY="$1"
TARGET_DIR="$2"

case "$STARTER_KEY" in
  nextjs) STARTER_DIRNAME="cube-nextjs-dashboard-starter" ;;
  astro) STARTER_DIRNAME="cube-astro-dashboard-starter" ;;
  *) usage ;;
esac

# ── Resolve this plugin's own root (dev checkout OR installed-plugin cache) ──
# Mirrors ravenclaude-core/scripts/resolve-plugin-root.sh's resolution order,
# scoped to this one plugin: $CLAUDE_PLUGIN_ROOT first (set by Claude Code
# when this script runs as part of an installed plugin), then this script's
# own parent directory (works identically whether invoked from the dev repo
# or from ~/.claude/plugins/cache/.../data-platform/<version>/).
if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" && -d "${CLAUDE_PLUGIN_ROOT}/templates/${STARTER_DIRNAME}" ]]; then
  PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
else
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

SOURCE_DIR="${PLUGIN_ROOT}/templates/${STARTER_DIRNAME}"
if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "error: could not find ${STARTER_DIRNAME} under ${PLUGIN_ROOT}/templates/" >&2
  echo "  (resolved plugin root: ${PLUGIN_ROOT} — set \$CLAUDE_PLUGIN_ROOT if this is wrong)" >&2
  exit 2
fi

if [[ -e "$TARGET_DIR" ]]; then
  echo "error: ${TARGET_DIR} already exists — refusing to overwrite" >&2
  exit 2
fi

mkdir -p "$TARGET_DIR"

# ── Copy, excluding build/dependency artifacts that must never travel ──
# (a stale .next/dist/node_modules copied from wherever this script last
# built the starter would shadow a fresh `npm ci` with mismatched binaries).
if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude "node_modules" \
    --exclude ".next" \
    --exclude "dist" \
    --exclude "*.tsbuildinfo" \
    "${SOURCE_DIR}/" "${TARGET_DIR}/"
else
  # rsync-less fallback (portable cp -R + prune) — same exclusion set.
  cp -R "${SOURCE_DIR}/." "${TARGET_DIR}/"
  rm -rf "${TARGET_DIR}/node_modules" "${TARGET_DIR}/.next" "${TARGET_DIR}/dist"
  find "${TARGET_DIR}" -name "*.tsbuildinfo" -delete
fi

# ── Seed .env from env.example — never overwrite an existing .env ──
ENV_TARGET_NAME=".env"
[[ "$STARTER_KEY" == "nextjs" ]] && ENV_TARGET_NAME=".env.local"
if [[ -f "${TARGET_DIR}/env.example" && ! -f "${TARGET_DIR}/${ENV_TARGET_NAME}" ]]; then
  cp "${TARGET_DIR}/env.example" "${TARGET_DIR}/${ENV_TARGET_NAME}"
fi

echo "Scaffolded ${STARTER_DIRNAME} into ${TARGET_DIR}"
echo
echo "Next steps:"
echo "  1. cd ${TARGET_DIR} && fill in ${ENV_TARGET_NAME} (NEXT_PUBLIC_CUBE_API_URL / PUBLIC_CUBE_API_URL, CUBE_API_ORIGIN, JWT_SIGNING_KEY — 32+ bytes)"
echo "  2. npm ci"
echo "  3. npm run dev"
echo
echo "Requires a running Cube instance with ../cube-schema-starter.yml loaded and a Postgres"
echo "database matching ../database-schema-starter.sql — this script scaffolds the APP, not the"
echo "data layer; database-setup-guide and cube-schema-scaffolding own that."
