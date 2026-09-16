#!/usr/bin/env python3
"""alias-deprecation-advisory.py — Phase D soak advisory for posture alias keys.

Detects deprecated comfort-posture keys still present in a consumer's
``.ravenclaude/comfort-posture.yaml``:

  - ``handoff_tax.pin_explore``          → prefer ``model_matrix.surfaces.explore_pin``
  - ``model_tier_surfaces.precompact_fallback_model`` → ``model_matrix.surfaces.precompact_fallback``
  - ``model_tier_surfaces.handoff_fill_model``        → ``model_matrix.surfaces.handoff_fill``

Emits a one-line advisory when an old key is the effective source (new key
absent) or diverges from the new key. Matching seed leftovers (both set to the
same value) stay quiet — no SessionStart spam on a fresh seed install.

Channel: SessionStart additionalContext via the thin hook wrapper (not Stop).
Readers are unchanged: new wins, old alias fallback, haiku default.

House Rule 3: this script never writes posture; marketplace never clobbers
consumer custom old keys. Phase D keeps aliases in seed; seed drop is later.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

ADVISORY_LINE = (
    "RavenClaude: posture alias deprecated — prefer model_matrix.surfaces."
    "{explore_pin,precompact_fallback,handoff_fill} "
    "(old handoff_tax.pin_explore / model_tier_surfaces.* still resolve; "
    "dashboard Save writes new keys only). "
    "See knowledge/unified-model-matrix.md."
)

_PIN_EXPLORE_RE = re.compile(
    r"^[ \t]+pin_explore[ \t]*:[ \t]*([A-Za-z0-9_-]+)\b", re.MULTILINE
)
_HANDOFF_TAX_OFF_RE = re.compile(
    r"^[ \t]*handoff_tax[ \t]*:[ \t]*(off|false)\b", re.MULTILINE | re.IGNORECASE
)
_SURFACES_BLOCK_RE = re.compile(
    r"^[ \t]*model_matrix[ \t]*:[ \t]*\n(?:[ \t]+.+\n)*?"
    r"[ \t]+surfaces[ \t]*:[ \t]*\n((?:[ \t]{2,}.+\n)+)",
    re.MULTILINE,
)
_MTS_BLOCK_RE = re.compile(
    r"^[ \t]*model_tier_surfaces[ \t]*:[ \t]*\n((?:[ \t]+.+\n)+)",
    re.MULTILINE,
)
_KV_RE = re.compile(r"^[ \t]+([A-Za-z0-9_]+)[ \t]*:[ \t]*([A-Za-z0-9_-]+)\b", re.MULTILINE)


def _block_kvs(block: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _KV_RE.finditer(block or ""):
        out[m.group(1)] = m.group(2)
    return out


def scan_posture_text(text: str) -> dict:
    """Return detection detail for advisory decision.

    Keys:
      should_advise (bool)
      reasons (list[str]) — human-readable why
      old (dict) / new (dict) — raw values found
    """
    surfaces = {}
    m = _SURFACES_BLOCK_RE.search(text)
    if m:
        surfaces = _block_kvs(m.group(1))

    mts = {}
    m = _MTS_BLOCK_RE.search(text)
    if m:
        mts = _block_kvs(m.group(1))

    pin_explore = None
    # Scalar handoff_tax: off disables pin — still counts as old key *shape* only
    # if pin_explore appears; bare off is not an explore-pin alias.
    pe = _PIN_EXPLORE_RE.search(text)
    if pe:
        pin_explore = pe.group(1)

    old = {
        "pin_explore": pin_explore,
        "precompact_fallback_model": mts.get("precompact_fallback_model"),
        "handoff_fill_model": mts.get("handoff_fill_model"),
    }
    new = {
        "explore_pin": surfaces.get("explore_pin"),
        "precompact_fallback": surfaces.get("precompact_fallback"),
        "handoff_fill": surfaces.get("handoff_fill"),
    }

    reasons: list[str] = []
    pairs = [
        ("pin_explore", "explore_pin", "handoff_tax.pin_explore"),
        ("precompact_fallback_model", "precompact_fallback", "model_tier_surfaces.precompact_fallback_model"),
        ("handoff_fill_model", "handoff_fill", "model_tier_surfaces.handoff_fill_model"),
    ]
    for old_k, new_k, label in pairs:
        ov = old.get(old_k)
        if ov is None:
            continue
        nv = new.get(new_k)
        if nv is None:
            reasons.append(f"{label} set (new {new_k} absent) → using alias")
        elif nv != ov:
            reasons.append(f"{label}={ov} diverges from surfaces.{new_k}={nv} (new wins)")

    return {
        "should_advise": bool(reasons),
        "reasons": reasons,
        "old": old,
        "new": new,
        "handoff_tax_off": bool(_HANDOFF_TAX_OFF_RE.search(text)),
    }


def scan_posture_file(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return {"should_advise": False, "reasons": [], "error": str(e)}
    return scan_posture_text(text)


def advisory_message(detail: dict | None = None) -> str:
    msg = ADVISORY_LINE
    if detail and detail.get("reasons"):
        msg = msg + " Detected: " + "; ".join(detail["reasons"][:3]) + "."
    return msg


def cmd_check(args: argparse.Namespace) -> int:
    posture = Path(args.project) / ".ravenclaude" / "comfort-posture.yaml"
    if not posture.is_file():
        return 0
    detail = scan_posture_file(posture)
    if not detail.get("should_advise"):
        return 0
    print(advisory_message(detail))
    return 0


def _self_test() -> int:
    fails = 0

    def check(name: str, cond: bool) -> None:
        nonlocal fails
        if not cond:
            print(f"FAIL: {name}", file=sys.stderr)
            fails += 1
        else:
            print(f"ok: {name}")

    # Seed-shaped: both new + old, same values → quiet
    seed = """
schema_version: 5
model_matrix:
  surfaces:
    explore_pin: haiku
    precompact_fallback: haiku
    handoff_fill: haiku
handoff_tax:
  report_cap_words: 400
  brief_cap_words: 600
  pin_explore: haiku
model_tier_surfaces:
  precompact_fallback_model: haiku
  handoff_fill_model: haiku
"""
    d = scan_posture_text(seed)
    check("seed both-same → no advise", d["should_advise"] is False)

    # Old-only explore pin
    old_only = """
schema_version: 5
handoff_tax:
  pin_explore: sonnet
"""
    d = scan_posture_text(old_only)
    check("old-only pin_explore → advise", d["should_advise"] is True)
    check("old-only reason mentions pin_explore", any("pin_explore" in r for r in d["reasons"]))

    # New wins / diverge
    diverge = """
model_matrix:
  surfaces:
    explore_pin: haiku
handoff_tax:
  pin_explore: sonnet
"""
    d = scan_posture_text(diverge)
    check("diverge → advise", d["should_advise"] is True)

    # New-only → quiet
    new_only = """
model_matrix:
  surfaces:
    explore_pin: sonnet
    precompact_fallback: sonnet
    handoff_fill: haiku
"""
    d = scan_posture_text(new_only)
    check("new-only → no advise", d["should_advise"] is False)

    # model_tier_surfaces alone
    mts = """
model_tier_surfaces:
  precompact_fallback_model: sonnet
  handoff_fill_model: haiku
"""
    d = scan_posture_text(mts)
    check("mts alone → advise", d["should_advise"] is True)
    check("mts reason", any("precompact_fallback_model" in r for r in d["reasons"]))

    # handoff_tax: off alone is not an explore alias advisory
    off = "handoff_tax: off\n"
    d = scan_posture_text(off)
    check("scalar off alone → no advise", d["should_advise"] is False)

    # File check path + message non-empty
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cfg = root / ".ravenclaude"
        cfg.mkdir()
        (cfg / "comfort-posture.yaml").write_text(old_only, encoding="utf-8")
        detail = scan_posture_file(cfg / "comfort-posture.yaml")
        check("file scan advises", detail["should_advise"] is True)
        msg = advisory_message(detail)
        check("message names model_matrix.surfaces", "model_matrix.surfaces" in msg)
        check("message is one logical advisory", "alias deprecated" in msg)

    # Absent file → no advise via cmd_check simulation
    with tempfile.TemporaryDirectory() as td:
        ns = argparse.Namespace(project=td)
        rc = cmd_check(ns)
        check("absent posture exit 0", rc == 0)

    if fails:
        print(f"alias-deprecation-advisory self-test: {fails} FAILED", file=sys.stderr)
        return 1
    print("alias-deprecation-advisory self-test: OK")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="Print advisory line if old alias keys warrant it")
    c.add_argument("--project", default=".", help="Project root (default: cwd)")
    sub.add_parser("self-test", help="Run built-in probes")
    args = p.parse_args()
    if args.cmd == "self-test":
        return _self_test()
    if args.cmd == "check":
        return cmd_check(args)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
