#!/usr/bin/env python3
"""archetype_score.py — deterministic structural conformance score for a wireframe archetype.

Scores a candidate wireframe MODEL against six weighted BINARY criteria and returns an integer
/100. This keeps the named-archetype library honest: a committed archetype must score >= THRESHOLD,
and a degraded/thin model must fall below it.

HONEST SCOPE (CE-3, stated plainly): the must-PASS half — "every committed archetype scores >= 80
against these criteria" — is near-tautological (an author writes the archetype to satisfy the
rubric). The REAL discrimination is the degraded must-FAIL fixture (`archetype-degraded.json`), which
proves the scorer has teeth. The score measures **structural completeness**, NOT aesthetic quality —
it is deterministic and gateable precisely because it never judges taste.

Weights (sum 100): valid 30 · structure 15 · landmarks 15 · content 15 · hierarchy 15 · labels 10.
A schema-INVALID model scores 0 outright (validity is the gate, not a partial credit).

Stdlib-only; `from __future__ import annotations` for stock-macOS Python 3.9 (RT-5).

CLI:
  --self-test    run the bundled contract checks (good >= 80, degraded < 80, invalid == 0, determinism).
  --score FILE   score a model JSON file; print the breakdown; exit 0 iff score >= THRESHOLD.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _layout  # noqa: E402
from wireframe_lint import validate_model  # noqa: E402

THRESHOLD = 80
WEIGHTS = {
    "valid": 30,
    "structure": 15,
    "landmarks": 15,
    "content": 15,
    "hierarchy": 15,
    "labels": 10,
}
# "Primary" landmark roles — a real page anchors on at least one of these.
LANDMARKS = {"header", "nav", "main", "hero", "sidebar", "footer", "canvas", "card-grid", "toolbar"}
MIN_REGIONS = 2
MIN_CONTENT = 4


def _labeled_component(comp: dict) -> bool:
    return bool(str((comp.get("props") or {}).get("label", "")).strip())


def score(model: object) -> dict:
    zero = dict.fromkeys(WEIGHTS, 0)
    if not isinstance(model, dict) or validate_model(model):
        return {"score": 0, "valid": False, "breakdown": zero}

    screens = _layout.normalize_to_screens(model)
    regions = [r for s in screens for r in (s.get("regions") or []) if isinstance(r, dict)]
    b = dict(zero)
    b["valid"] = WEIGHTS["valid"]

    # structure: at least MIN_REGIONS regions total.
    b["structure"] = WEIGHTS["structure"] if len(regions) >= MIN_REGIONS else 0

    # landmarks: at least one region is a primary landmark role.
    if any(r.get("role") in LANDMARKS for r in regions):
        b["landmarks"] = WEIGHTS["landmarks"]

    # content: at least MIN_CONTENT leaf items carry non-empty text/labels.
    leaves = 0
    for r in regions:
        for sec in r.get("sections") or []:
            for comp in sec.get("components") or []:
                if isinstance(comp, dict) and _labeled_component(comp):
                    leaves += 1
            for slot in sec.get("content_slots") or []:
                if isinstance(slot, dict) and str(slot.get("text", "")).strip():
                    leaves += 1
    b["content"] = WEIGHTS["content"] if leaves >= MIN_CONTENT else 0

    # hierarchy: emphasis set on at least one region or section (information hierarchy present).
    has_emph = any(r.get("emphasis") for r in regions) or any(
        sec.get("emphasis") for r in regions for sec in (r.get("sections") or [])
    )
    b["hierarchy"] = WEIGHTS["hierarchy"] if has_emph else 0

    # labels: nothing blank — each section either has a heading or every component is labeled.
    all_labeled = True
    for r in regions:
        for sec in r.get("sections") or []:
            comps = sec.get("components") or []
            if (
                not sec.get("heading")
                and comps
                and not all(_labeled_component(c) for c in comps if isinstance(c, dict))
            ):
                all_labeled = False
    b["labels"] = WEIGHTS["labels"] if all_labeled else 0

    return {"score": sum(b.values()), "valid": True, "breakdown": b}


# ── bundled self-test ─────────────────────────────────────────────────────────
_GOOD = {
    "meta": {"title": "Pricing", "type": "page", "viewport": "desktop"},
    "regions": [
        {
            "role": "header",
            "emphasis": "secondary",
            "sections": [
                {
                    "kind": "nav",
                    "heading": "Acme",
                    "components": [{"type": "nav-item", "props": {"label": "Pricing"}}],
                }
            ],
        },
        {
            "role": "main",
            "emphasis": "primary",
            "sections": [
                {
                    "kind": "plans",
                    "heading": "Plans",
                    "components": [
                        {"type": "card", "props": {"label": "Starter"}},
                        {"type": "card", "props": {"label": "Pro"}},
                        {"type": "card", "props": {"label": "Team"}},
                    ],
                }
            ],
        },
        {
            "role": "footer",
            "sections": [{"kind": "legal", "content_slots": [{"slot": "text", "text": "© Acme"}]}],
        },
    ],
}
_DEGRADED = {  # valid but thin: 1 region, no emphasis, blank labels -> must score < 80
    "meta": {"title": "Thin", "type": "page"},
    "regions": [
        {
            "role": "modal",
            "sections": [{"kind": "x", "components": [{"type": "button"}, {"type": "button"}]}],
        }
    ],
}
_INVALID = {"meta": {"title": "X"}, "regions": []}  # missing meta.type + empty regions


def _self_test() -> int:
    failures: list[str] = []
    g = score(_GOOD)
    if g["score"] < THRESHOLD:
        failures.append(f"good archetype scored {g['score']} < {THRESHOLD}: {g['breakdown']}")
    if score(_GOOD)["score"] != g["score"]:
        failures.append("score() is non-deterministic")
    d = score(_DEGRADED)
    if d["score"] >= THRESHOLD:
        failures.append(
            f"degraded model scored {d['score']} >= {THRESHOLD} (no teeth): {d['breakdown']}"
        )
    inv = score(_INVALID)
    if inv["score"] != 0 or inv["valid"]:
        failures.append(f"invalid model did not score 0: {inv}")

    if failures:
        print("archetype_score --self-test: FAIL")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(
        f"archetype_score --self-test: OK (good>={THRESHOLD}, degraded<{THRESHOLD}, invalid=0, deterministic)"
    )
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Deterministic wireframe archetype scorer.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--score", metavar="FILE", help="score a model JSON file")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    with open(args.score, encoding="utf-8") as fh:
        model = json.load(fh)
    result = score(model)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["score"] >= THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
