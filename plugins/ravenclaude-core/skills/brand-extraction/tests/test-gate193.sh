#!/usr/bin/env bash
# Gate 193 — static schema extractor (spacing/type/grid/elevation/components) + [RT1-#4]
# _fetch SSRF/LFR hardening + [RT1-#5] brand.css emit sanitization. The heavy lifting is a
# pure-Python driver (property-based, file fixtures only, NO port bind / no http.server) so
# this wrapper is trivially bash-3.2 / macOS-safe: it only resolves paths and exec's python3.
# Paths resolve from this script's own location, so it runs from any cwd (audit-gates.sh runs
# it from the repo root; a direct `bash <path>` also works).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/_gate193.py"
