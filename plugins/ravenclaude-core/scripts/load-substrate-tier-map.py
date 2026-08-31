#!/usr/bin/env python3
"""Load plugins/ravenclaude-core/knowledge/substrate-tier-map.json.

resolve_tier(host, tier) → {model, effort?, perspective?}.
Blank/missing host → claude. Unknown host → claude. Unknown tier → balanced.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MAP_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "substrate-tier-map.json"
DEFAULT_HOST = "claude"
TIERS = ("fast", "balanced", "top")
HOSTS = ("claude", "grok", "codex", "copilot")


def load_map(path: Path | None = None) -> dict:
    p = path or MAP_PATH
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def _normalize_row(row) -> dict:
    if isinstance(row, str):
        return {"model": row}
    if isinstance(row, dict) and row.get("model"):
        out = {"model": row["model"]}
        if row.get("effort"):
            out["effort"] = row["effort"]
        if row.get("perspective"):
            out["perspective"] = row["perspective"]
        return out
    raise ValueError("tier row must be a SKU string or {model, ...}")


def resolve_tier(host, tier, default_host: str = DEFAULT_HOST, data: dict | None = None) -> dict:
    blob = data if data is not None else load_map()
    hosts = blob.get("hosts") or {}
    h = (str(host).strip() if host else "") or default_host
    if h not in hosts:
        h = default_host
    table = hosts[h]
    t = (str(tier).strip() if tier else "") or "balanced"
    if t not in table:
        t = "balanced"
    return _normalize_row(table[t])


def self_test() -> int:
    data = load_map()
    errors = []
    hosts = data.get("hosts") or {}
    for h in HOSTS:
        if h not in hosts:
            errors.append(f"missing host {h}")
            continue
        for t in TIERS:
            if t not in hosts[h]:
                errors.append(f"missing {h}.{t}")
                continue
            row = resolve_tier(h, t, data=data)
            if not row.get("model"):
                errors.append(f"{h}.{t} has no model")
            if "pro" in row["model"].lower() and row["model"].endswith("-pro"):
                errors.append(f"{h}.{t} is a *-pro slug: {row['model']}")
    grok_fast = resolve_tier("grok", "fast", data=data)
    grok_bal = resolve_tier("grok", "balanced", data=data)
    grok_top = resolve_tier("grok", "top", data=data)
    if grok_fast["model"] != "grok-4.5" or grok_bal["model"] != "grok-4.5":
        errors.append("grok fast/balanced must be grok-4.5")
    if grok_top["model"] != "grok-4.6":
        errors.append("grok top must be grok-4.6")
    if grok_fast.get("effort") == grok_bal.get("effort") and grok_fast.get(
        "perspective"
    ) == grok_bal.get("perspective"):
        errors.append("grok fast vs balanced must differ on effort and perspective")
    if grok_fast.get("effort") == grok_bal.get("effort"):
        errors.append("grok fast vs balanced must differ on effort")
    if grok_fast.get("perspective") == grok_bal.get("perspective"):
        errors.append("grok fast vs balanced must differ on perspective")
    if grok_top["model"].startswith("claude-"):
        errors.append("grok top must not be a claude-* id")
    missing = resolve_tier(None, "top", data=data)
    if missing["model"] != "claude-opus-4-8":
        errors.append(f"default host top should be claude-opus-4-8, got {missing}")
    blank = resolve_tier("  ", "top", data=data)
    if blank["model"] != "claude-opus-4-8":
        errors.append("blank host must default to claude")
    if "seats" in hosts:
        errors.append("seats must not live in hosts")
    if errors:
        print("substrate-tier-map self-test FAIL:")
        for e in errors:
            print("  -", e)
        return 1
    print("substrate-tier-map self-test PASS")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    print(json.dumps(resolve_tier(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else "balanced")))
