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
    # Pins from cross-tool-model-lineup-2026.md as re-verified in #1451
    # (ee923b3d, retrieved 2026-11-16). Fast leaf grok-4.3; balanced and top
    # are grok-4.7, the Grok Build default. grok-4.6 is not a tier.
    if grok_fast["model"] != "grok-4.3":
        errors.append("grok fast must be grok-4.3")
    if grok_bal["model"] != "grok-4.7" or grok_top["model"] != "grok-4.7":
        errors.append("grok balanced and top must be grok-4.7")
    if "grok-4.6" in {grok_fast["model"], grok_bal["model"], grok_top["model"]}:
        errors.append("grok tiers must not pin grok-4.6")
    if grok_fast.get("effort") == grok_bal.get("effort") and grok_fast.get(
        "perspective"
    ) == grok_bal.get("perspective"):
        errors.append("grok fast vs balanced must differ on effort and perspective")
    if grok_fast.get("effort") == grok_bal.get("effort"):
        errors.append("grok fast vs balanced must differ on effort")
    if grok_fast.get("perspective") == grok_bal.get("perspective"):
        errors.append("grok fast vs balanced must differ on perspective")
    if grok_bal.get("perspective") == grok_top.get("perspective"):
        errors.append("grok balanced vs top must differ on perspective")
    if grok_top["model"].startswith("claude-"):
        errors.append("grok top must not be a claude-* id")
    claude_fast = resolve_tier("claude", "fast", data=data)
    claude_bal = resolve_tier("claude", "balanced", data=data)
    if claude_fast["model"] != "claude-haiku-5-5":
        errors.append("claude fast must be claude-haiku-5-5")
    if claude_bal["model"] != "claude-sonnet-5-5":
        errors.append("claude balanced must be claude-sonnet-5-5")
    codex_fast = resolve_tier("codex", "fast", data=data)
    codex_bal = resolve_tier("codex", "balanced", data=data)
    codex_top = resolve_tier("codex", "top", data=data)
    if codex_fast["model"] != "gpt-6-luna":
        errors.append("codex fast must be gpt-6-luna")
    if codex_bal["model"] != "gpt-6.1-sol":
        errors.append("codex balanced must be gpt-6.1-sol")
    # The lineup names GPT-6 Astra as the flagship and records no CLI slug.
    if codex_top["model"] != "gpt-6.1-sol":
        errors.append("codex top stays gpt-6.1-sol until the lineup records a GPT-6 Astra slug")
    copilot_fast = resolve_tier("copilot", "fast", data=data)
    copilot_bal = resolve_tier("copilot", "balanced", data=data)
    copilot_top = resolve_tier("copilot", "top", data=data)
    if copilot_fast["model"] != "Claude Haiku 5.5":
        errors.append("copilot fast must be Claude Haiku 5.5")
    if copilot_bal["model"] != "Claude Sonnet 5.5":
        errors.append("copilot balanced must be Claude Sonnet 5.5")
    if copilot_top["model"] != "Claude Opus 5.5":
        errors.append("copilot top must be Claude Opus 5.5")
    missing = resolve_tier(None, "top", data=data)
    if missing["model"] != "claude-opus-5-5":
        errors.append(f"default host top should be claude-opus-5-5, got {missing}")
    blank = resolve_tier("  ", "top", data=data)
    if blank["model"] != "claude-opus-5-5":
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
