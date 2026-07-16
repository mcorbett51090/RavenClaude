"""Canonical model-ID catalog — thin sibling shim.

Single source of truth for the current tribunal-seat / dashboard / template model
IDs. Consumed by generate-dashboards.py (seat dropdown + defaults) and
thing-decision.py (seat defaults + fallback diversity), so the two halves cannot
drift. The drift gate (scripts/check-model-ids.py, audit-gates Gate 134) enforces
that every governed claude-* id equals one of CURRENT's values.

Lives in the same dir as thing-decision.py / thing-seat.sh so it ships inside the
plugin (the installed-plugin cache has it). Resolves the JSON by relative path from
this file, so it works regardless of the caller's cwd.
"""

import json
from pathlib import Path

_CATALOG_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "model-catalog.json"
_C = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))

CURRENT = _C["current"]
STALE = _C["stale"]
OPUS = CURRENT["opus"]
SONNET = CURRENT["sonnet"]
HAIKU = CURRENT["haiku"]
FABLE = CURRENT["fable"]

if __name__ == "__main__":
    # Relative-path smoke test: prints the current dict regardless of caller cwd.
    print(json.dumps(CURRENT, indent=2))
