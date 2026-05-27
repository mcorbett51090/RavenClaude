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
import hashlib
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


def _normalize_lead(lead: str) -> str:
    """Strip wrappers that would let a command dodge EMISSIONS prefix matching.

    Closes the classification holes from the tribunal assessment (§should-fix #8):
    leading env-var assignments (`LS_COLORS=x ls`), `sudo`/`env` prefixes,
    absolute interpreter paths (`/usr/bin/python3` -> `python3`), and `git`
    global options (`git -c k=v push` -> `git push`). Conservative + idempotent.
    """
    prev = None
    while lead and lead != prev:
        prev = lead
        # leading VAR=value assignments (one or more)
        lead = re.sub(r"^[A-Za-z_][A-Za-z0-9_]*=\S*\s+", "", lead)
        # sudo / env wrappers (with any of their own flags before the real cmd)
        lead = re.sub(r"^(?:sudo|env|command|nohup|nice|stdbuf)\b(?:\s+-\S+)*\s+", "", lead)
        lead = re.sub(r"^(?:sudo|env)\s+[A-Za-z_][A-Za-z0-9_]*=\S*\s+", "", lead)
    # absolute / relative path on the first token -> basename (/usr/bin/python3 -> python3)
    m = re.match(r"^(\S*/)?(\S+)(.*)$", lead, re.S)
    if m and m.group(1):
        lead = m.group(2) + m.group(3)
    # git global options: `git -c k=v -C dir push` -> `git push`
    if lead.startswith("git "):
        rest = lead[4:]
        rest = re.sub(r"^(?:\s*(?:-c\s+\S+|-C\s+\S+|--no-pager|-p|--paginate))+\s*", "", rest)
        lead = "git " + rest.lstrip()
    return lead.strip()


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
    lead = _normalize_lead(lead)

    best_cat: str | None = None
    best_len = -1
    for category, prefix, is_wildcard in _command_prefixes():
        if is_wildcard:
            matched = lead == prefix or lead.startswith(prefix + " ")
        else:
            matched = lead == prefix
        if matched and len(prefix) > best_len:
            best_cat, best_len = category, len(prefix)
    # Flag-aware tribunal override (routing only — does NOT touch the permission
    # EMISSIONS table). EMISSIONS lumps every `git branch` form into
    # shell_readonly, but a FORCE delete (`-D`, or `--delete` together with
    # `--force`) is a destructive local mutation, not a read. Match `-D`
    # case-sensitively so `-d` — the safe merged-only delete — is NOT re-routed.
    # Without this, slm.delete-protected-branch-locally is unreachable: the
    # command auto-allows as a "read" before its concern can ever fire.
    if best_cat == "shell_readonly" and re.match(r"git\s+branch\b", lead):
        # `-D` matched case-sensitively (so safe `-d` is excluded) but allowing
        # other flag letters around it (`-Dr`, `-rD`, `-vD`); or `--delete` +
        # `--force` in any order.
        force_delete = re.search(r"(?:^|\s)-[A-Za-z]*D[A-Za-z]*\b", lead) or (
            re.search(r"(?:^|\s)--delete\b", lead) and re.search(r"(?:^|\s)--force\b", lead)
        )
        if force_delete:
            best_cat = "shell_local_mutate"
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
    # Heimdall is the injection seat — the assessment (must-fix #4) flagged that
    # running the adversarial-content reviewer on the weakest model is exactly
    # where you don't want to economize. Bumped to Sonnet (Mímir, the correctness
    # seat, stays on the fast/cheap Haiku).
    "heimdall": {"agent": "prompt-engineer", "model": "claude-sonnet-4-6"},
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
    # #15 knobs (same precedence: command_review > thing.yaml > defaults).
    bypass: list[str] = []
    cache_ttl = 0
    fatigue = 0

    def _apply(block) -> None:
        nonlocal gate_floor, bypass, cache_ttl, fatigue
        if not isinstance(block, dict):
            return
        gf = block.get("gate_floor")
        if isinstance(gf, str) and gf in _TIER_RANK and gf != "low":
            gate_floor = gf
        if isinstance(block.get("bypass"), list):
            bypass = [p for p in block["bypass"] if isinstance(p, str)]
        for key, attr in (("cache_ttl_seconds", "cache_ttl"), ("fatigue_threshold", "fatigue")):
            v = block.get(key)
            if isinstance(v, int) and v >= 0:
                if attr == "cache_ttl":
                    cache_ttl = v
                else:
                    fatigue = v
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
    cfg["bypass"] = bypass
    cfg["cache_ttl_seconds"] = cache_ttl
    cfg["fatigue_threshold"] = fatigue
    return cfg, error


# Anti-correlated-hallucination rule (Matt 2026-05-26): when >=2 seats convene, at
# least two DISTINCT model backbones must run, so a single model's blind spot can't
# pass the whole panel unseen. If a config collapsed the convened seats onto one
# model, reassign one seat to a different (preferring equal-or-stronger) model.
_DIVERSITY_PREF = ["claude-sonnet-4-6", "claude-opus-4-7", "claude-haiku-4-5"]


def _enforce_model_diversity(panel: dict, convened: list[str]) -> tuple[dict, bool]:
    """Return (panel, adjusted). Guarantees >=2 distinct models among `convened`."""
    if len(convened) < 2:
        return panel, False
    models = [(panel.get(s) or {}).get("model") for s in convened]
    if len({m for m in models if m}) >= 2:
        return panel, False  # already heterogeneous
    common = models[0]
    alt = next((m for m in _DIVERSITY_PREF if m != common), "claude-sonnet-4-6")
    out = {k: dict(v) for k, v in panel.items()}
    out.setdefault(convened[-1], {})["model"] = alt  # diversify the last convened seat
    return out, True


def _decision_detail(root: Path, posture: dict, command: str, category: str | None) -> dict:
    """Full tier/route/gate computation for a (command, category).

    Used by `classify` when the category's toggle is on, AND by `preview`
    unconditionally (the dashboard 'Test a command' simulator) so the preview
    is the REAL engine decision, never a reimplementation that could drift.
    """
    d: dict = {}
    cfg, cfg_err = resolve_tier_config(root, posture)
    cfg.pop("timeout_posture_map", None)
    d["seat_timeout_seconds"] = cfg["seat_timeout_seconds"]
    d["panel_deadline_seconds"] = cfg["panel_deadline_seconds"]
    d["audit_dir"] = cfg["audit_dir"]
    if cfg_err:
        d["config_error"] = cfg_err

    route = _route(command, category)
    d.update(route)

    base_tier = _norm_tier(cfg["category_tier_map"].get(category), "medium")
    final_tier = _escalate_tier(base_tier, route.get("max_severity"))
    tier_cfg = cfg["tiers"][final_tier]
    is_read = category in _READ_CATEGORIES
    gate_floor = cfg["gate_floor"]

    want = set(tier_cfg["seats"]) | set(tier_cfg["mandatory"])
    convened = [s for s in _SEATS if s in want and s != "thor"]
    if _TIER_RANK[final_tier] >= _TIER_RANK["medium"] and not convened:
        convened = ["forseti", "mimir", "heimdall"]
    # Enforce model heterogeneity across the convened panel (anti-correlated
    # hallucination): >=2 seats must run >=2 distinct models.
    panel_models, diversified = _enforce_model_diversity(cfg["panel"], convened)
    d["panel"] = panel_models
    d["convened_seats"] = convened
    d["model_diversity_enforced"] = diversified
    d["confidence_threshold"] = float(tier_cfg["confidence"])
    d["tier"] = final_tier
    d["base_tier"] = base_tier
    d["is_read"] = is_read
    d["gate_floor"] = gate_floor
    d["panel_required"] = _TIER_RANK[final_tier] >= _TIER_RANK["medium"]
    d["gate_allow"] = (not is_read) and _TIER_RANK[final_tier] >= _TIER_RANK[gate_floor]
    d["timeout_posture"] = "deny"

    # ── #15 cost/UX knobs (bypass-list / verdict cache / session-fatigue) ────────
    # These let the orchestrator skip the EXPENSIVE LLM panel; the deterministic
    # screen (pre_llm_deny + self-disable) ALWAYS runs regardless, so the hard
    # floor is never bypassed. bypass also requires a non-critical screen.
    bypass_match = False
    for p in cfg.get("bypass") or []:
        try:
            if re.search(p, command):
                bypass_match = True
                break
        except re.error:
            continue
    # Never bypass a critical-severity screen even if the pattern matches.
    d["bypass_match"] = bool(bypass_match) and route.get("max_severity") != "critical"
    d["cache_ttl_seconds"] = int(cfg.get("cache_ttl_seconds") or 0)
    d["fatigue_threshold"] = int(cfg.get("fatigue_threshold") or 0)
    # config_hash invalidates the verdict cache when the rules (tiers/panel/
    # gate_floor/category map) OR the concern catalog change — so a cached
    # permissive verdict is never reused after the policy that produced it moves.
    cfg_blob = json.dumps(
        {"tiers": cfg["tiers"], "panel": cfg["panel"], "gate_floor": cfg["gate_floor"],
         "category_tier_map": cfg["category_tier_map"]},
        sort_keys=True,
    )
    try:
        cat_text = (_HERE.parent / "knowledge" / "concerns-catalog.md").read_text(encoding="utf-8")
    except OSError:
        cat_text = ""
    d["config_hash"] = hashlib.sha256((cfg_blob + cat_text).encode("utf-8")).hexdigest()[:16]

    # Human-readable predicted outcome for the simulator.
    if d.get("pre_llm_deny"):
        d["predicted_gate"] = f"DENY — blocked before any model runs ({d.get('deny_concern') or 'hard rule'})"
    elif not d["panel_required"]:
        d["predicted_gate"] = "ALLOW — clean low-risk command, no panel convened"
    elif is_read:
        d["predicted_gate"] = "panel auto-decides (reads are never surfaced to you)"
    elif d["gate_allow"]:
        d["predicted_gate"] = "a confident panel-ALLOW is surfaced to you as ASK; DENY blocks, EDIT rewrites"
    else:
        d["predicted_gate"] = "panel decides autonomously (tier is below gate_floor); DENY blocks, EDIT rewrites"
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="project root (consumer cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify", help="classify a command + report toggle state")
    c.add_argument("command", help="the shell command string")
    p = sub.add_parser("preview", help="full tier/seat/gate preview regardless of toggle (dashboard simulator)")
    p.add_argument("command", help="the shell command string")
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

    # `preview` (dashboard simulator) computes the full detail unconditionally;
    # `classify` (the live hook path) only when the category's toggle is on.
    if args.cmd == "preview" or result["thing_enabled"]:
        result.update(_decision_detail(root, posture, args.command, category))

    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
