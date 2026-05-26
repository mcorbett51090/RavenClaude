#!/usr/bin/env python3
"""thing-decision.py — the routing brain of the command-review tribunal ("the Thing").

Given a shell command, this answers three questions the orchestrator hook
(`thing-orchestrator.sh`, the "Lawspeaker") needs before it spends an LLM call:

  1. Which comfort-posture category does the command belong to? (reuses the
     EMISSIONS table in apply-comfort-posture.py — the ONE source of truth, so
     category matching never drifts from the permission translator).
  2. Is command review toggled ON for that category? (reads the per-category
     `thing:` field in .ravenclaude/comfort-posture.yaml — written by the
     dashboard's Command-review toggle).
  3. What seat config applies? (reads the optional .ravenclaude/thing.yaml;
     falls back to built-in defaults when absent).

It prints ONE JSON object to stdout and always exits 0 (so the bash orchestrator
can `jq` the result without worrying about exit codes). A malformed thing.yaml
is reported via a `config_error` field — the orchestrator fails closed (ask) on
that, never a silent skip.

T2 scope: single category supported end-to-end (`shell_readonly`), single seat.
Classification covers all categories so T3+ only flips toggles, no code change.

Usage:
    thing-decision.py --root <project-dir> classify "<command string>"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── Reuse the EMISSIONS table from apply-comfort-posture.py (single source of
#    truth for category ⇄ command-pattern mapping). Same importlib trick the
#    dashboard generator uses, so the two never drift. ────────────────────────
import importlib.util

_HERE = Path(__file__).resolve().parent
_APPLY = _HERE / "apply-comfort-posture.py"


def _load_emissions() -> dict[str, list[str]]:
    spec = importlib.util.spec_from_file_location("_apply_comfort_posture", _APPLY)
    if spec is None or spec.loader is None:
        return {}
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return dict(getattr(mod, "EMISSIONS", {}))


_CONCERNS = _HERE / "thing-concerns.py"


def _route(command: str, category: str | None) -> dict:
    """Deterministic seat routing + pre-LLM screen, via thing-concerns.py.

    Returns the routing subset {concerns, max_severity, pre_llm_deny,
    deny_concern, convened_seats}. On any failure to load/evaluate, returns a
    conservative fallback that convenes the full panel (never silently empties
    the routing) so the orchestrator still reviews the command.
    """
    fallback = {
        "concerns": [],
        "max_severity": None,
        "pre_llm_deny": False,
        "deny_concern": None,
        "convened_seats": ["forseti", "mimir", "heimdall"],
        "high_blast": False,
    }
    try:
        spec = importlib.util.spec_from_file_location("_thing_concerns", _CONCERNS)
        if spec is None or spec.loader is None:
            return fallback
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        catalog = mod._load_catalog()
        res = mod.evaluate(catalog, command, category)
        return {k: res[k] for k in fallback}
    except Exception:
        return fallback


def _screen_always(command: str) -> dict:
    """Category-independent self-disable screen (§B.9.5), via thing-concerns.py.

    Runs regardless of the per-category toggle: a command that would disable or
    tamper with the Thing is denied pre-LLM whenever the orchestrator reached us
    (i.e. some category is toggled on), even if THIS command's own category is
    off. On any failure to load/evaluate, returns a conservative no-deny (the
    orchestrator's other fail-closed paths still apply) rather than crashing.
    """
    fallback = {"self_disable_deny": False, "self_disable_concern": None}
    try:
        spec = importlib.util.spec_from_file_location("_thing_concerns", _CONCERNS)
        if spec is None or spec.loader is None:
            return fallback
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        catalog = mod._load_catalog()
        res = mod.screen_always(catalog, command)
        return {k: res[k] for k in fallback}
    except Exception:
        return fallback


_BASH_PATTERN_RE = re.compile(r"^Bash\((.+?)(:\*)?\)$")


def _command_prefixes() -> list[tuple[str, str, bool]]:
    """Flatten EMISSIONS into (category, prefix, is_wildcard) for Bash patterns.

    `Bash(ls:*)`      -> ("shell_readonly", "ls", True)   # command starts with "ls"
    `Bash(pwd)`       -> ("shell_readonly", "pwd", False) # command IS exactly "pwd"
    """
    out: list[tuple[str, str, bool]] = []
    for category, patterns in _load_emissions().items():
        for pat in patterns:
            m = _BASH_PATTERN_RE.match(pat)
            if not m:
                continue  # non-Bash pattern (Read/Edit/WebFetch/...) — irrelevant here
            prefix = m.group(1).strip()
            is_wildcard = m.group(2) is not None
            out.append((category, prefix, is_wildcard))
    return out


def classify(command: str) -> str | None:
    """Return the comfort-posture category for a Bash command, or None.

    Longest matching prefix wins (so `git status` beats a bare `git`). A
    wildcard prefix matches when the command equals it or is followed by a
    space; an exact prefix (no `:*`) matches only an exact command. The match
    is on the leading segment of the command so a pipe/chain classifies by its
    first command (`ls | grep x` -> shell_readonly).
    """
    cmd = command.strip()
    if not cmd:
        return None
    # Leading segment only — split on the first shell separator so `ls | grep`
    # classifies as its first command. Keep it conservative (T2 is low-stakes).
    lead = re.split(r"\s*(?:\||\|\||&&|;)\s*", cmd, maxsplit=1)[0].strip()

    best_cat: str | None = None
    best_len = -1
    for category, prefix, is_wildcard in _command_prefixes():
        if is_wildcard:
            matched = lead == prefix or lead.startswith(prefix + " ")
        else:
            matched = lead == prefix
        if matched and len(prefix) > best_len:
            best_cat, best_len = category, len(prefix)
    return best_cat


# ── Config reading ───────────────────────────────────────────────────────────


def _load_yaml(path: Path):
    """Load a YAML file with pyyaml; raise ValueError on a parse error."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        # pyyaml is present in the devcontainer + CI; this path only triggers on
        # a stripped consumer environment. Be honest rather than guess.
        raise ValueError("pyyaml not available to parse YAML")


_TRUTHY = {True, "on", "true", "yes", "1", 1}


def thing_enabled_for(posture: dict, category: str | None) -> bool:
    """Is the per-category `thing:` toggle ON in comfort-posture.yaml?"""
    if not category:
        return False
    cats = (posture or {}).get("categories", {}) or {}
    cfg = cats.get(category)
    if isinstance(cfg, dict):
        val = cfg.get("thing")
        return val in _TRUTHY or (isinstance(val, str) and val.strip().lower() in {"on", "true", "yes"})
    return False  # bare-string (legacy) category has no toggle


# ── T3 panel defaults (design §B.4.3) ─────────────────────────────────────────
# The four seats, each filled by an existing ravenclaude-core agent (no new
# agents — House Rule). Heterogeneous backbones break seat correlation: spend
# the budget on the security + tie-break seats, run the fast seats on Haiku.
_DEFAULT_PANEL = {
    "forseti": {"agent": "security-reviewer", "model": "claude-opus-4-7"},
    "mimir": {"agent": "code-reviewer", "model": "claude-haiku-4-5"},
    "heimdall": {"agent": "prompt-engineer", "model": "claude-haiku-4-5"},
    "thor": {"agent": "architect", "model": "claude-opus-4-7"},
}
_DEFAULT_CONFIDENCE_THRESHOLD = 0.5
_DEFAULT_SEAT_TIMEOUT = 45  # per-seat soft cap (s); parallel `claude -p` cold-starts
#   contend and run ~24-29s (a single warm seat is ~8s), so 18s abstained the
#   whole panel on modest machines. 45s clears the observed parallel latency with
#   margin and stays well under panel_deadline_seconds (75) and the 90s hook timeout.
_DEFAULT_PANEL_DEADLINE = 75  # panel hard deadline (s); must stay < hook timeout (90)
_DEFAULT_AUDIT_DIR = ".ravenclaude/runs/thing"
# Timeout / abstention posture per category. The high-stakes categories fail
# CLOSED (deny) — *deviation from design §B.3.5* (which says "ask"): deny is the
# only verdict that holds under bypass modes, and these are exactly where
# failing open is catastrophic. shell_readonly keeps "ask".
_DEFAULT_TIMEOUT_POSTURE = {
    "shell_remote_mutate": "deny",
    "shell_code_exec": "deny",
    "shell_readonly": "ask",
}
_SEATS = ("forseti", "mimir", "heimdall", "thor")


def _merge_panel(base: dict, override) -> None:
    """Per-seat merge of a panel override (mutates base in place)."""
    if not isinstance(override, dict):
        return
    for seat in _SEATS:
        entry = override.get(seat)
        if isinstance(entry, dict):
            if isinstance(entry.get("agent"), str):
                base[seat]["agent"] = entry["agent"]
            if isinstance(entry.get("model"), str):
                base[seat]["model"] = entry["model"]


def resolve_panel_config(root: Path, posture: dict | None) -> tuple[dict, str | None]:
    """Resolve the tribunal panel config with precedence:

        comfort-posture.yaml `command_review:`  (dashboard-authored)
          >  .ravenclaude/thing.yaml             (advanced / manual)
          >  built-in defaults

    Dashboard authors only per-seat models + the confidence threshold; the
    timers, audit dir, and per-category timeout posture come from thing.yaml or
    the defaults. Returns (config, error); a malformed thing.yaml yields an
    error so the orchestrator fails closed.
    """
    cfg = {
        "panel": {s: dict(_DEFAULT_PANEL[s]) for s in _SEATS},
        "confidence_threshold": _DEFAULT_CONFIDENCE_THRESHOLD,
        "seat_timeout_seconds": _DEFAULT_SEAT_TIMEOUT,
        "panel_deadline_seconds": _DEFAULT_PANEL_DEADLINE,
        "audit_dir": _DEFAULT_AUDIT_DIR,
        "timeout_posture_map": dict(_DEFAULT_TIMEOUT_POSTURE),
    }
    error: str | None = None

    # Layer 1: thing.yaml (advanced / manual).
    path = root / ".ravenclaude" / "thing.yaml"
    if path.exists():
        try:
            data = _load_yaml(path) or {}
            if not isinstance(data, dict):
                error = "thing.yaml: top level is not a mapping"
            else:
                _merge_panel(cfg["panel"], data.get("panel"))
                # Legacy T2 single-seat config maps to the Mímir seat.
                legacy = data.get("seat")
                if isinstance(legacy, dict) and not data.get("panel"):
                    if isinstance(legacy.get("agent"), str):
                        cfg["panel"]["mimir"]["agent"] = legacy["agent"]
                    if isinstance(legacy.get("model"), str):
                        cfg["panel"]["mimir"]["model"] = legacy["model"]
                if isinstance(data.get("confidence_threshold"), (int, float)):
                    cfg["confidence_threshold"] = float(data["confidence_threshold"])
                # Accept the new timer names and the legacy internal_timeout_seconds.
                for key in ("seat_timeout_seconds", "internal_timeout_seconds"):
                    if isinstance(data.get(key), int):
                        cfg["seat_timeout_seconds"] = data[key]
                if isinstance(data.get("panel_deadline_seconds"), int):
                    cfg["panel_deadline_seconds"] = data["panel_deadline_seconds"]
                if isinstance(data.get("timeout_posture"), dict):
                    cfg["timeout_posture_map"].update(
                        {k: v for k, v in data["timeout_posture"].items() if isinstance(v, str)}
                    )
                audit = data.get("audit")
                if isinstance(audit, dict) and isinstance(audit.get("dir"), str):
                    cfg["audit_dir"] = audit["dir"]
        except Exception as exc:  # malformed YAML — fail closed upstream
            error = f"thing.yaml: {exc}"

    # Layer 2: comfort-posture.yaml `command_review:` (dashboard-authored; wins).
    cr = (posture or {}).get("command_review")
    if isinstance(cr, dict):
        _merge_panel(cfg["panel"], cr.get("panel"))
        if isinstance(cr.get("confidence_threshold"), (int, float)):
            cfg["confidence_threshold"] = float(cr["confidence_threshold"])

    return cfg, error


# ── T5 tier model (risk = category base tier + severity escalation bump) ──────
# Every reviewed command resolves to one of four tiers. The category sets a base
# tier; a deterministic high/critical concern bumps it up. The tier drives which
# seats convene, the confidence bar, and whether a panel-ALLOW is surfaced to the
# human (gate_floor). A clean low command (a read with no escalation) is cleared
# by the zero-cost deterministic screen alone — no LLM panel.

_TIER_ORDER = ("low", "medium", "high", "extreme")
_TIER_RANK = {t: i for i, t in enumerate(_TIER_ORDER)}

# Read-shaped categories are never surfaced to the human as an `ask`: a clean
# read auto-allows, an escalated read is auto-decided by the panel. The low base
# tier and this set coincide by construction.
_READ_CATEGORIES = {
    "file_read_project",
    "file_read_global",
    "shell_readonly",
    "network_read",
}

# Category -> base risk tier, over the 12 comfort-posture categories (EMISSIONS).
_DEFAULT_CATEGORY_TIER_MAP = {
    "file_read_project": "low",
    "file_read_global": "low",
    "shell_readonly": "low",
    "network_read": "low",
    "file_edit_project": "medium",
    "shell_local_mutate": "medium",
    "shell_package_install": "medium",
    "network_write": "medium",
    "mcp_tools": "medium",
    "file_edit_global": "high",
    "shell_remote_mutate": "high",
    "shell_code_exec": "extreme",
}

# Per-tier panel shape. `seats` = which seats convene; `mandatory` can't be
# removed by a dashboard override (re-unioned in); `confidence` is the per-tier
# bar (escalating with stakes) below which a seat vote convenes Thor. `low` runs
# no panel.
_DEFAULT_TIERS = {
    "low": {"seats": [], "mandatory": [], "confidence": _DEFAULT_CONFIDENCE_THRESHOLD},
    "medium": {"seats": ["mimir", "heimdall"], "mandatory": ["heimdall"], "confidence": 0.5},
    "high": {"seats": ["forseti", "mimir", "heimdall"], "mandatory": ["heimdall"], "confidence": 0.6},
    "extreme": {"seats": ["forseti", "mimir", "heimdall"], "mandatory": ["forseti", "heimdall"], "confidence": 0.7},
}

# Default lowest tier whose panel-ALLOW is surfaced to the human for confirmation.
# medium..extreme is the dashboard-exposed range; `high` is the conservative
# default (reads + low mutates auto-resolve via the panel; high/extreme surface).
_DEFAULT_GATE_FLOOR = "high"


def _norm_tier(value, fallback: str) -> str:
    return value if isinstance(value, str) and value in _TIER_RANK else fallback


def _escalate_tier(base: str, max_severity: str | None) -> str:
    """Severity bump: a high concern bumps the base up one tier; a critical
    concern bumps straight to extreme; low/medium/none does not bump."""
    rank = _TIER_RANK.get(base, _TIER_RANK["medium"])
    if max_severity == "critical":
        rank = _TIER_RANK["extreme"]
    elif max_severity == "high":
        rank = min(_TIER_RANK["extreme"], rank + 1)
    return _TIER_ORDER[rank]


def resolve_tier_config(root: Path, posture: dict | None) -> tuple[dict, str | None]:
    """Resolve the tier model, same precedence as the panel config:

        comfort-posture.yaml `command_review:`  >  .ravenclaude/thing.yaml  >  defaults

    Returns (cfg, error). cfg carries everything resolve_panel_config returns
    (per-seat models, timers, audit dir) PLUS tiers, category_tier_map, gate_floor.
    """
    panel_cfg, error = resolve_panel_config(root, posture)
    tiers = {t: dict(_DEFAULT_TIERS[t]) for t in _TIER_ORDER}
    cat_map = dict(_DEFAULT_CATEGORY_TIER_MAP)
    gate_floor = _DEFAULT_GATE_FLOOR

    def _apply(block) -> None:
        nonlocal gate_floor
        if not isinstance(block, dict):
            return
        gf = block.get("gate_floor")
        if isinstance(gf, str) and gf in _TIER_RANK and gf != "low":
            gate_floor = gf
        tm = block.get("category_tier_map")
        if isinstance(tm, dict):
            for cat, tier in tm.items():
                if isinstance(tier, str) and tier in _TIER_RANK:
                    cat_map[cat] = tier
        tcfg = block.get("tiers")
        if isinstance(tcfg, dict):
            for t in _TIER_ORDER:
                entry = tcfg.get(t)
                if not isinstance(entry, dict):
                    continue
                if isinstance(entry.get("seats"), list):
                    tiers[t]["seats"] = [s for s in entry["seats"] if s in _SEATS]
                if isinstance(entry.get("mandatory_seats"), list):
                    tiers[t]["mandatory"] = [s for s in entry["mandatory_seats"] if s in _SEATS]
                if isinstance(entry.get("confidence_threshold"), (int, float)):
                    tiers[t]["confidence"] = float(entry["confidence_threshold"])

    # Layer 1: thing.yaml. Layer 2: comfort-posture command_review: (wins).
    path = root / ".ravenclaude" / "thing.yaml"
    if path.exists():
        try:
            data = _load_yaml(path) or {}
            if isinstance(data, dict):
                _apply(data)
        except Exception as exc:
            if not error:
                error = f"thing.yaml: {exc}"
    _apply((posture or {}).get("command_review"))

    cfg = dict(panel_cfg)
    cfg["tiers"] = tiers
    cfg["category_tier_map"] = cat_map
    cfg["gate_floor"] = gate_floor
    return cfg, error


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="project root (consumer cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify", help="classify a command + report toggle state")
    c.add_argument("command", help="the shell command string")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    category = classify(args.command)

    result: dict = {"category": category, "thing_enabled": False}

    # §B.9.5 — the self-disable guard is CATEGORY-INDEPENDENT. The orchestrator
    # only reaches us when some category is toggled on, and disabling the Thing
    # affects every category, so this is screened regardless of THIS command's
    # category or whether that category's own toggle is on.
    result.update(_screen_always(args.command))

    posture: dict = {}
    posture_path = root / ".ravenclaude" / "comfort-posture.yaml"
    if posture_path.exists():
        try:
            posture = _load_yaml(posture_path) or {}
            result["thing_enabled"] = thing_enabled_for(posture, category)
        except Exception as exc:
            # Malformed posture: can't determine the toggle. Fall through to the
            # settings.json floor (do NOT claim enabled). Report for visibility.
            result["posture_error"] = f"comfort-posture.yaml: {exc}"

    if result["thing_enabled"]:
        cfg, cfg_err = resolve_tier_config(root, posture)
        cfg.pop("timeout_posture_map", None)  # superseded by the tier/gate model
        result["seat_timeout_seconds"] = cfg["seat_timeout_seconds"]
        result["panel_deadline_seconds"] = cfg["panel_deadline_seconds"]
        result["audit_dir"] = cfg["audit_dir"]
        if cfg_err:
            result["config_error"] = cfg_err

        # Deterministic screen — concerns, max severity, pre-LLM deny, high-blast.
        route = _route(args.command, category)
        result.update(route)

        # Risk tier = category base tier + severity escalation bump.
        base_tier = _norm_tier(cfg["category_tier_map"].get(category), "medium")
        final_tier = _escalate_tier(base_tier, route.get("max_severity"))
        tier_cfg = cfg["tiers"][final_tier]
        is_read = category in _READ_CATEGORIES
        gate_floor = cfg["gate_floor"]

        # Convened panel comes from the TIER (mandatory seats re-unioned), in panel
        # order — overrides the legacy severity routing carried by _route. Thor is
        # never pre-convened; it is summoned at aggregation on a split.
        want = set(tier_cfg["seats"]) | set(tier_cfg["mandatory"])
        convened = [s for s in _SEATS if s in want and s != "thor"]
        # A medium+ tier must convene at least one seat (else the orchestrator's
        # aggregation has nothing to tally). If a config emptied it, fall back to
        # the full review panel rather than silently running no review.
        if _TIER_RANK[final_tier] >= _TIER_RANK["medium"] and not convened:
            convened = ["forseti", "mimir", "heimdall"]
        result["panel"] = cfg["panel"]
        result["convened_seats"] = convened
        result["confidence_threshold"] = float(tier_cfg["confidence"])
        result["tier"] = final_tier
        result["base_tier"] = base_tier
        result["is_read"] = is_read
        result["gate_floor"] = gate_floor
        # Panel runs at medium+; a clean low command is cleared by the screen alone.
        result["panel_required"] = _TIER_RANK[final_tier] >= _TIER_RANK["medium"]
        # A confident panel-ALLOW is surfaced to the human (ask) when the tier is
        # at/above gate_floor. Reads are never surfaced (handled in the hook).
        result["gate_allow"] = (not is_read) and _TIER_RANK[final_tier] >= _TIER_RANK[gate_floor]
        # Abstention / inconclusive panel always fails CLOSED (deny). Clean reads
        # no longer convene a panel; an escalated read that abstains fails closed
        # (P9b), never asks — so the old per-category `ask` posture is retired.
        result["timeout_posture"] = "deny"

    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
