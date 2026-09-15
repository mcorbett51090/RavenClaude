#!/usr/bin/env python3
"""oath_hook.py — Oath-hook (GUPP) SessionStart assembler.

If Runes hang on this actor's hook (hook_owner == self, state in
ready|in_progress|proposed), surface a MUST-RUN banner via
hookSpecificOutput.additionalContext. SessionStart cannot block; this is
salience + obligation, not a deny gate.

Fail-open / fail-silent: any error → empty stdout, exit 0.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--actor", default=None)
    args = parser.parse_args()
    root = Path(args.root)
    actor = (
        args.actor
        or os.environ.get("RC_ACTOR")
        or os.environ.get("RC_HOOK_OWNER")
        or os.environ.get("USER")
        or "unknown"
    )
    try:
        import runes as R

        items, _errors, _cfg = R._project_items(root)
        hanging = R._hanging_on_hook(items, actor)
    except Exception:
        return 0
    if not hanging:
        return 0

    lines = [
        "OATH-HOOK (GUPP) — MUST-RUN",
        f"You have {len(hanging)} Rune(s) hanging on hook_owner={actor}.",
        "If work hangs on your Oath-hook, you MUST surface and continue it — no silent idle.",
        "Inspect: `rc runes hanging` · resume: `rc runes show <id>`",
        "Names: Rune · Oath-hook · Longship (delivery; Sage sole; no auto-merge).",
        "",
    ]
    for item in hanging[:12]:
        lines.append(
            f"- {item['item_id']} [{item.get('state')}] {item.get('subject', '')[:100]}"
        )
    if len(hanging) > 12:
        lines.append(f"- … +{len(hanging) - 12} more")

    msg = "\n".join(lines)
    envelope = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": msg,
        }
    }
    print(json.dumps(envelope, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
