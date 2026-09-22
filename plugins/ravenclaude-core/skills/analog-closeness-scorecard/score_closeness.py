#!/usr/bin/env python3
"""score_closeness.py — the analog-repos-gap-fill weighted closeness formula, reusable.

Reproduces the scoring arithmetic from docs/plans/2026-08-14-analog-repos-gap-fill/catalog.md
("Rubric" section) so a future analog comparison doesn't hand-derive it.

    weighted = 3*M + 3*H + 3*G + 2*O + 2*E + 2*I + 2*T + 1*V   (max 36)
    closeness bucket: 0-8 -> 1, 9-14 -> 2, 15-20 -> 3, 21-27 -> 4, 28-36 -> 5
    quality bar: at least one of M/H/G >= 1, AND >= 3 of the 8 dims are kind:"obs"

Usage:
    python3 score_closeness.py --json '{"dims": {...}, "provenance": {...}}'
    python3 score_closeness.py --self-test
"""

from __future__ import annotations

import json
import sys

DIMS = ("M", "H", "G", "O", "E", "I", "T", "V")
WEIGHTS = {"M": 3, "H": 3, "G": 3, "O": 2, "E": 2, "I": 2, "T": 2, "V": 1}
_MHG = ("M", "H", "G")


def closeness_bucket(weighted: int) -> int:
    if weighted <= 8:
        return 1
    if weighted <= 14:
        return 2
    if weighted <= 20:
        return 3
    if weighted <= 27:
        return 4
    return 5


def compute(dims: dict, provenance: dict | None = None) -> dict:
    """Return {weighted, closeness, quality_bar_pass, reasons}. Raises ValueError on a
    malformed dims map (missing dim, out-of-range score) — fail loud, never guess."""
    provenance = provenance or {}
    reasons: list[str] = []

    missing = [d for d in DIMS if d not in dims]
    if missing:
        raise ValueError(f"missing dimension(s): {missing}")
    for d in DIMS:
        v = dims[d]
        if not isinstance(v, int) or v not in (0, 1, 2):
            raise ValueError(f"dimension {d!r} must score 0/1/2, got {dims[d]!r}")

    weighted = sum(WEIGHTS[d] * dims[d] for d in DIMS)
    closeness = closeness_bucket(weighted)

    mhg_ok = any(dims[d] >= 1 for d in _MHG)
    if not mhg_ok:
        reasons.append("none of M/H/G scored >= 1")

    obs_count = sum(1 for d in DIMS if provenance.get(d) == "obs")
    if obs_count < 3:
        reasons.append(f"only {obs_count}/8 dims are kind:observation (need >= 3)")

    return {
        "weighted": weighted,
        "closeness": closeness,
        "quality_bar_pass": mhg_ok and obs_count >= 3,
        "reasons": reasons,
    }


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("--self-test", "self-test"):
        return self_test()
    if not argv or argv[0] != "--json":
        print("usage: score_closeness.py --json '<json>' | --self-test", file=sys.stderr)
        return 2
    if len(argv) < 2:
        print("--json requires an argument", file=sys.stderr)
        return 2
    try:
        payload = json.loads(argv[1])
        result = compute(payload.get("dims", {}), payload.get("provenance"))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


def self_test() -> int:
    errors = 0

    def _ok(name: str, cond: bool) -> None:
        nonlocal errors
        if cond:
            print(f"OK    {name}")
        else:
            print(f"FAIL  {name}", file=sys.stderr)
            errors += 1

    # Catalog row #1 (jeremylongshore/claude-code-plugins-plus-skills):
    # M H G O E I T V = 2 1 2 2 0 2 0 2 -> published weighted 25, closeness 4.
    row1 = compute(
        {"M": 2, "H": 1, "G": 2, "O": 2, "E": 0, "I": 2, "T": 0, "V": 2},
        dict.fromkeys(DIMS, "obs"),
    )
    _ok("row #1 weighted == 25 (survey-published)", row1["weighted"] == 25)
    _ok("row #1 closeness == 4 (survey-published)", row1["closeness"] == 4)
    _ok("row #1 passes quality bar (all obs, M/H/G nonzero)", row1["quality_bar_pass"] is True)

    # Catalog row #13 (snarktank/ralph): M H G O E I T V = 0 1 1 1 0 0 0 0
    # -> published weighted 8, closeness 1.
    row13 = compute(
        {"M": 0, "H": 1, "G": 1, "O": 1, "E": 0, "I": 0, "T": 0, "V": 0},
        dict.fromkeys(DIMS, "obs"),
    )
    _ok("row #13 weighted == 8 (survey-published)", row13["weighted"] == 8)
    _ok("row #13 closeness == 1 (survey-published)", row13["closeness"] == 1)

    # Bucket boundaries (the range table, both edges of each band).
    _ok("bucket(8) == 1, bucket(9) == 2", closeness_bucket(8) == 1 and closeness_bucket(9) == 2)
    _ok("bucket(14) == 2, bucket(15) == 3", closeness_bucket(14) == 2 and closeness_bucket(15) == 3)
    _ok("bucket(20) == 3, bucket(21) == 4", closeness_bucket(20) == 3 and closeness_bucket(21) == 4)
    _ok("bucket(27) == 4, bucket(28) == 5", closeness_bucket(27) == 4 and closeness_bucket(28) == 5)
    _ok("bucket(36) == 5 (max)", closeness_bucket(36) == 5)
    _ok("bucket(0) == 1 (min)", closeness_bucket(0) == 1)

    # Must-fail-shaped fixture: high arithmetic total via O/E/I/T/V, but M=H=G=0
    # and every dim scored from inference only -> quality bar MUST reject this,
    # proving the bar is load-bearing and not just decorative on top of the score.
    high_but_unqualified = compute(
        {"M": 0, "H": 0, "G": 0, "O": 2, "E": 2, "I": 2, "T": 2, "V": 2},
        dict.fromkeys(DIMS, "inf"),
    )
    _ok(
        "high weighted score does NOT buy a quality-bar pass",
        high_but_unqualified["weighted"] >= 18 and high_but_unqualified["quality_bar_pass"] is False,
    )
    _ok(
        "rejection names BOTH failure reasons (M/H/G and obs-count)",
        len(high_but_unqualified["reasons"]) == 2,
    )

    # Only-2-observed fixture: M/H/G satisfied, but obs count is 2 (< 3) -> still fails.
    two_obs = compute(
        {"M": 2, "H": 0, "G": 0, "O": 0, "E": 0, "I": 0, "T": 0, "V": 0},
        {"M": "obs", "H": "obs", "G": "inf", "O": "inf", "E": "inf", "I": "inf", "T": "inf", "V": "inf"},
    )
    _ok("2-of-8 observed fails the obs-count half alone", two_obs["quality_bar_pass"] is False)
    _ok("2-of-8 observed: M/H/G half still passes (only 1 reason)", len(two_obs["reasons"]) == 1)

    # Malformed input must raise, never silently coerce or guess.
    try:
        compute({"M": 1, "H": 1, "G": 1, "O": 1, "E": 1, "I": 1, "T": 1})  # missing V
        _ok("missing dimension raises ValueError", False)
    except ValueError:
        _ok("missing dimension raises ValueError", True)

    try:
        compute({**dict.fromkeys(DIMS, 1), "M": 3})  # out-of-range score
        _ok("out-of-range score raises ValueError", False)
    except ValueError:
        _ok("out-of-range score raises ValueError", True)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
