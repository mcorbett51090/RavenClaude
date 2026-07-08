#!/usr/bin/env python3
"""entity_config.py - load + validate a per-entity profile for the close autopilot.

An entity is DATA, not code: the same engines run for any company by pointing at a
different entity profile + COA mapping. This module is the gate that keeps a bad
profile from silently running the close under unreviewed defaults.

The profile carries the knobs the whole cycle reads: functional currency, the
fiscal period, and the two thresholds that drive controls — `materiality_threshold`
(below which flux/recon lines are suppressed) and `sod_threshold` (at/above which a
same-actor approval is refused by close_state.py).

`schema_version` is REQUIRED and checked hard: when the contract grows (e.g. a
future multi-approver quorum), --validate FAILS on an old profile rather than
running it under implicit defaults — forcing an explicit re-review per entity.

Stdlib only. Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import sys

SCHEMA_VERSION = 1
REQUIRED = {
    "schema_version": int,
    "entity_name": str,
    "functional_currency": str,
    "fiscal_period": str,          # e.g. "2026-06"
    "materiality_threshold": (int, float),
    "sod_threshold": (int, float),
    "coa_mapping": str,            # relative path to the COA mapping CSV
}


def validate(profile: dict) -> list[str]:
    """Return a list of error strings (empty == valid)."""
    errs: list[str] = []
    sv = profile.get("schema_version")
    if sv != SCHEMA_VERSION:
        errs.append(
            f"schema_version {sv!r} != current {SCHEMA_VERSION} — this profile "
            f"predates the current contract; re-review before running the close."
        )
    for key, typ in REQUIRED.items():
        if key not in profile:
            errs.append(f"missing required key: {key}")
        elif not isinstance(profile[key], typ):
            errs.append(f"key {key!r} must be {typ}, got {type(profile[key]).__name__}")
    cur = profile.get("functional_currency")
    if isinstance(cur, str) and len(cur) != 3:
        errs.append(f"functional_currency {cur!r} should be a 3-letter ISO code (e.g. USD, EUR)")
    for tkey in ("materiality_threshold", "sod_threshold"):
        v = profile.get(tkey)
        if isinstance(v, (int, float)) and v < 0:
            errs.append(f"{tkey} must be non-negative, got {v}")
    return errs


def load(path: str) -> dict:
    with open(path) as fh:
        return json.load(fh)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Validate a per-entity close profile.")
    p.add_argument("--validate", metavar="PROFILE.json", required=True)
    a = p.parse_args(argv)
    try:
        profile = load(a.validate)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(f"cannot read {a.validate}: {e}\n")
        return 2
    errs = validate(profile)
    if errs:
        sys.stderr.write("INVALID entity profile:\n")
        for e in errs:
            sys.stderr.write(f"  - {e}\n")
        return 1
    print(f"OK: {profile['entity_name']} ({profile['functional_currency']}, "
          f"period {profile['fiscal_period']}) — profile valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
