#!/usr/bin/env python3
"""oath_hook.py — Oath-hook (GUPP) SessionStart assembler.

Comfort-posture gate (Matthew LOCK 2026-09-15):
  `runes: off|on` in .ravenclaude/comfort-posture.yaml (absent ⇒ off).
  Off  → quiet (no auto orientation). CLI `rc runes …` still works.
  On   → hanging MUST-RUN + ready summary + may auto-claim next ungated
         ready Rune (human_gate walls refuse; never auto Longship merge).

SessionStart cannot block; fail-open / fail-silent → empty stdout, exit 0.
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
    parser.add_argument(
        "--force-on",
        action="store_true",
        help="test seam: ignore posture and run On path",
    )
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

        if not args.force_on and not R.runes_posture_on(root):
            # Default OFF / kill switch — quiet SessionStart auto path.
            return 0

        items, _errors, _cfg = R._project_items(root)
        hanging = R._hanging_on_hook(items, actor)
        ready = R._ready_items(items)

        lines = [
            "OATH-HOOK (GUPP) — Runes at session start (posture: on)",
            "Kill switch: set `runes: off` in .ravenclaude/comfort-posture.yaml + Save.",
            "Flat Runes + strands only (kind is a tag, not an epic tree).",
            "Auto-claim: next ungated ready Rune only; gates refuse; never auto Longship merge.",
            "",
        ]

        if hanging:
            lines.extend(
                [
                    "MUST-RUN — hanging on your Oath-hook",
                    f"You have {len(hanging)} Rune(s) hanging on hook_owner={actor}.",
                    "If work hangs on your Oath-hook, you MUST surface and continue it — no silent idle.",
                    "Inspect: `rc runes hanging` · resume: `rc runes show <id>`",
                    "",
                ]
            )
            for item in hanging[:12]:
                lines.append(
                    f"- {item['item_id']} [{item.get('state')}] {item.get('subject', '')[:100]}"
                )
            if len(hanging) > 12:
                lines.append(f"- … +{len(hanging) - 12} more")
            lines.append("")

        lines.append(f"READY QUEUE — {len(ready)} ungated Verðandi Rune(s)")
        if ready:
            for item in ready[:8]:
                kind = item.get("kind")
                kind_s = f" kind={kind}" if kind else ""
                lines.append(
                    f"- {item['item_id']}{kind_s} {item.get('subject', '')[:100]}"
                )
            if len(ready) > 8:
                lines.append(f"- … +{len(ready) - 8} more")
        else:
            lines.append("- (empty)")
        lines.append("")

        # Auto-depth B: claim next ungated ready (never gated; never Longship).
        claimed = R.auto_claim_next_ungated(root, actor)
        if claimed:
            lines.append(
                f"AUTO-CLAIMED (ungated): {claimed['item_id']} → hook_owner={actor}"
            )
            lines.append(f"  {claimed.get('subject', '')[:120]}")
            lines.append("Continue this Rune now. Gated Runes stay blocked until a human clears the wall.")
        else:
            lines.append("AUTO-CLAIM: none (queue empty or only gated/blocked remain).")

        lines.append("")
        lines.append(
            "Names: Rune · Oath-hook · Longship (delivery; Sage sole; no auto-merge)."
        )
        lines.append(
            "Hosts: SessionStart-hook hosts only (MH-18) — see knowledge/host-support.json."
        )

        # If nothing to say beyond empty queue and no claim and no hanging, still
        # emit a short on-banner so agents know the opt-in is live.
        msg = "\n".join(lines)
        envelope = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": msg,
            }
        }
        print(json.dumps(envelope, ensure_ascii=False))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
