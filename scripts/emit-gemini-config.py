#!/usr/bin/env python3
"""Project comfort-posture onto Gemini settings (tighten-only)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_LEVEL = re.compile(r"^\s*(user|local|project)\s*:\s*([A-Za-z]+)\s*$")
APPROVAL_RANK = {"auto_edit": 0, "default": 1, "plan": 2}
NEVER_EMIT_APPROVAL = frozenset({"yolo"})


def read_posture_categories(path: Path) -> dict:
    if not path.is_file():
        return {}
    order = {"allow": 0, "ask": 1, "deny": 2}
    out: dict = {}
    in_cats = False
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            in_cats = line.strip() == "categories:"
            current = None
            continue
        if not in_cats:
            continue
        stripped = line.strip()
        if stripped.endswith(":") and ":" not in stripped[:-1]:
            current = stripped[:-1]
            continue
        m = _LEVEL.match(line)
        if m and current:
            level = m.group(2).lower()
            if level == "inherit" or level not in order:
                continue
            prev = out.get(current)
            if prev is None or order[level] > order[prev]:
                out[current] = level
    return out


def map_posture(cats: dict) -> dict:
    def allowed(name: str) -> bool:
        return cats.get(name) == "allow"

    writes = any(
        allowed(c)
        for c in ("file_edit_project", "shell_local_mutate", "shell_code_exec")
    )
    net = allowed("network_write")
    mode = "default" if writes else "plan"
    return {
        "general.defaultApprovalMode": mode,
        "tools.sandboxNetworkAccess": bool(net),
    }


def get_nested(cfg: dict, dotted: str):
    cur = cfg
    parts = dotted.split(".")
    for p in parts[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return None, parts[-1]
        cur = cur[p]
    return cur, parts[-1]


def decide_approval(want: str, cur: str | None) -> str:
    if want in NEVER_EMIT_APPROVAL:
        raise ValueError(f"refusing to emit approval mode {want!r}")
    if cur is None:
        return "write"
    if cur in NEVER_EMIT_APPROVAL:
        raise ValueError(f"existing approval mode {cur!r} is not managed here")
    if cur == want:
        return "skip"
    if APPROVAL_RANK[want] > APPROVAL_RANK.get(cur, -1):
        return "tighten"
    return "refuse"


def decide_network(want: bool, cur) -> str:
    if cur is None:
        return "write"
    if isinstance(cur, bool):
        cur_b = cur
    elif isinstance(cur, str) and cur.lower() in ("true", "false"):
        cur_b = cur.lower() == "true"
    else:
        raise ValueError("tools.sandboxNetworkAccess exists in an unsupported form")
    if cur_b == want:
        return "skip"
    if want is False and cur_b is True:
        return "tighten"
    return "refuse"


def emit(project: Path) -> int:
    posture = project / ".ravenclaude" / "comfort-posture.yaml"
    dest = project / ".gemini" / "settings.json"
    if not posture.is_file():
        print("emit-gemini-config: no comfort-posture.yaml — skipped", file=sys.stderr)
        return 0
    want = map_posture(read_posture_categories(posture))
    try:
        cfg = json.loads(dest.read_text(encoding="utf-8")) if dest.is_file() else {}
    except Exception:
        cfg = {}
    if not isinstance(cfg, dict):
        cfg = {}
    changes = []
    for key, val in want.items():
        parent, leaf = get_nested(cfg, key)
        if key.startswith("general."):
            cur = None if parent is None else parent.get(leaf)
            action = decide_approval(val, cur if isinstance(cur, str) else None)
            if action == "refuse":
                print(f"emit-gemini-config: leaving {key}={cur!r}", file=sys.stderr)
                continue
            if parent is None:
                cfg.setdefault("general", {})
                parent = cfg["general"]
            if action != "skip":
                parent[leaf] = val
                changes.append(key)
        else:
            cur = None if parent is None else parent.get(leaf)
            try:
                action = decide_network(val, cur)
            except ValueError as exc:
                print(f"emit-gemini-config: {exc}", file=sys.stderr)
                continue
            if action == "refuse":
                print(f"emit-gemini-config: leaving {key}={cur!r}", file=sys.stderr)
                continue
            if parent is None:
                cfg.setdefault("tools", {})
                parent = cfg["tools"]
            if action != "skip":
                parent[leaf] = val
                changes.append(key)
    if not changes:
        print("emit-gemini-config: nothing to change")
        return 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(f"emit-gemini-config: updated {dest} ({', '.join(changes)})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, default=Path.cwd())
    args = ap.parse_args()
    try:
        return emit(args.project.resolve())
    except ValueError as exc:
        print(f"emit-gemini-config: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
