#!/usr/bin/env python3
"""Gate 163 — Mímir's "current" fields are read from the TAIL, not the head.

Multi-host audit MH-06 (P0).

THE DEFECT, and why it is the worst direction to be wrong in:

The session card reported the session's **opening** permission mode as its current
one — it said `default` while the session was in `auto`. Two independent causes,
and fixing either alone leaves the bug:

  1. FIRST-WINS. The loop read `if first_perm_mode is None`, keeping the OLDEST
     permission-mode event — in the very same pass that deliberately OVERWRITES to
     keep the NEWEST model. One loop, two opposite policies, one of them wrong.
  2. HEAD-READ. `_mimir_iter_jsonl_bounded` did `fh.read(cap)` from offset 0, so on
     any transcript larger than the 50 KiB cap the scanned slice is the OLDEST part
     of the session. Even a correct last-wins loop would then report the last value
     *in the opening minutes*.

A permissions surface that reports a LAXER state than reality is the bad direction:
it tells an operator they are more constrained than they are. Hence a P0.

WHAT THIS GATE ASSERTS, on a transcript deliberately larger than the cap so head
and tail genuinely differ:
  * the tail read sees the LATE events and the head read does not (fixture validity —
    without this, the rest could pass on a file small enough that both ends match,
    which would make the whole gate vacuous);
  * permission mode resolves to the LAST value, not the first;
  * last-used model resolves to the LAST value (same fix, same loop);
  * `from_end` defaults to False, so the aggregate caller's behaviour is unchanged;
  * a partial leading line from landing mid-record is dropped, not fed to json.loads.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent


def _load(rel: str):
    spec = importlib.util.spec_from_file_location("sd_" + rel.replace("/", "_"), _REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fixture(tmp: Path, cap: int) -> Path:
    """A transcript >2x the cap whose OPENING and CLOSING state differ."""
    f = tmp / "session.jsonl"
    lines = [json.dumps({"type": "permission-mode", "permissionMode": "default"})]
    filler = json.dumps(
        {
            "type": "assistant",
            "message": {"model": "old-model", "usage": {"output_tokens": 1}},
            "filler": "x" * 400,
        }
    )
    while sum(len(x) + 1 for x in lines) < cap * 2:
        lines.append(filler)
    lines.append(json.dumps({"type": "permission-mode", "permissionMode": "auto"}))
    lines.append(
        json.dumps(
            {"type": "assistant", "message": {"model": "new-model", "usage": {"output_tokens": 2}}}
        )
    )
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return f


def _modes(events):
    return [e.get("permissionMode") for e in events if e.get("type") == "permission-mode"]


def _last_model(events):
    ms = [
        (e.get("message") or {}).get("model")
        for e in events
        if e.get("type") == "assistant" and isinstance(e.get("message"), dict)
    ]
    return ms[-1] if ms else None


def check(rel: str) -> list:
    errs = []
    mod = _load(rel)
    cap = mod._MIMIR_JSONL_READ_CAP
    with tempfile.TemporaryDirectory() as td:
        f = _fixture(Path(td), cap)
        if f.stat().st_size <= cap:
            return [f"{rel}: fixture is not larger than the cap — the gate would be vacuous"]

        head = list(mod._mimir_iter_jsonl_bounded(f))
        tail = list(mod._mimir_iter_jsonl_bounded(f, from_end=True))

        # Fixture validity FIRST: if head and tail see the same thing, every
        # assertion below passes for free and proves nothing.
        if "auto" in _modes(head):
            errs.append(f"{rel}: head read reached the late events — fixture too small to be a test")
        if "auto" not in _modes(tail):
            errs.append(f"{rel}: tail read did NOT reach the late events — from_end is not seeking")

        # The actual contract.
        if (_modes(tail) or [None])[-1] != "auto":
            errs.append(f"{rel}: tail permission mode is {_modes(tail)!r}, expected to end at 'auto'")
        if _last_model(tail) != "new-model":
            errs.append(f"{rel}: tail last model is {_last_model(tail)!r}, expected 'new-model'")

        # Default must stay head-read: the aggregate caller relies on it, and
        # flipping it would silently change reported counts.
        if _modes(head) != ["default"]:
            errs.append(f"{rel}: default (head) read changed — aggregate callers would shift")

        # Landing mid-record must drop the fragment, never feed json.loads a
        # partial line. Every yielded item being a dict is the observable proof.
        if not all(isinstance(e, dict) for e in tail):
            errs.append(f"{rel}: tail read yielded a non-dict — a partial line leaked through")
    return errs


def main() -> int:
    errs = []
    for rel in (
        "scripts/serve-dashboards.py",
        "plugins/ravenclaude-core/scripts/serve-dashboards.py",
    ):
        errs.extend(check(rel))
    if errs:
        print("Gate 163 FAILURES:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("Mimir recency OK — permission mode + last model read from the TAIL in both server copies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
