#!/usr/bin/env python3
"""check-derive-rubric.py — bidirectional audit gate for P1 of the Convergence
Engine: the deterministic rubric library + derive_rubric.py.

The DEFAULT run proves:
  - every per-kind rubric the library yields is STRUCTURALLY VALID against the
    rubric.schema.json contract (required fields, id pattern, source enum,
    verified boolean, derived ⇒ verified=false);
  - the library is the single source of truth (every gradable kind parses to a
    non-empty dimension set; objective hard gates carry an objective_signal);
  - EXPLICIT user requirements are graded at WEIGHT-MAX (>= the largest library
    weight) and verified=true;
  - DERIVED ("commonly-missed") proposals are FORCIBLY unverified — even a model
    proposing source=library, verified=true, weight=999 is normalized to
    source=derived, verified=false, low weight, with the [unverified — derived]
    provenance marker (the anti-reward-hack defense in code);
  - a low-confidence / unknown kind falls back to the generic rubric.

Stdlib-only (no jsonschema dependency) — mirrors the streams gates so it runs in
any CI shell.

BIDIRECTIONAL TEETH (--must-fail-grade-derived): disable the derived-normalizer's
verified-forcing and assert that a malicious proposal (verified=true) THEN gets
auto-graded — proving the normalizer is what blocks it. Exit 0 iff the leak is
observed (gate has teeth).

Exit 0 = all assertions held. Exit 1 = an assertion failed (or teeth absent).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_SCRIPTS = os.path.join(
    REPO_ROOT, "plugins", "ravenclaude-core", "skills", "refine-to-rubric", "scripts"
)
DERIVE_PATH = os.path.join(SKILL_SCRIPTS, "derive_rubric.py")
SCHEMA_PATH = os.path.join(
    REPO_ROOT, "plugins", "ravenclaude-core", "skills", "refine-to-rubric",
    "schemas", "rubric.schema.json",
)
GRADABLE_KINDS = ["generic", "code", "visual-report", "prose", "data"]

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_SOURCES = {"library", "explicit", "derived"}


def _load_derive():
    spec = importlib.util.spec_from_file_location("derive_rubric", DERIVE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Fail(Exception):
    pass


def _check(cond, msg):
    if not cond:
        raise _Fail(msg)
    print(f"  ✓ {msg}")


def _validate_rubric_struct(rubric):
    """A minimal structural validator against the rubric.schema.json contract —
    enough to prove the derived documents are schema-shaped without a jsonschema
    dependency. Returns an error string or None."""
    if not isinstance(rubric, dict):
        return "rubric is not an object"
    for req in ("schema_version", "artifact_kind", "dimensions"):
        if req not in rubric:
            return f"missing required top-level field: {req}"
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", rubric["schema_version"]):
        return "schema_version is not semver"
    dims = rubric["dimensions"]
    if not isinstance(dims, list) or not dims:
        return "dimensions must be a non-empty array"
    for d in dims:
        for req in ("id", "title", "weight", "source", "verified"):
            if req not in d:
                return f"dimension missing required field: {req}"
        if not _ID_RE.match(d["id"]):
            return f"dimension id '{d['id']}' violates the id pattern"
        if d["source"] not in _SOURCES:
            return f"dimension source '{d['source']}' not in {_SOURCES}"
        if not isinstance(d["verified"], bool):
            return f"dimension {d['id']} verified is not a boolean"
        if not (0 <= float(d["weight"]) <= 100):
            return f"dimension {d['id']} weight out of [0,100]"
        if d["source"] == "derived" and d["verified"]:
            return f"derived dimension {d['id']} is verified=true (contract violation)"
    return None


def run_default(dr):
    # schema file exists + parses
    _check(os.path.isfile(SCHEMA_PATH), "rubric.schema.json exists")
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        json.load(fh)
    _check(True, "rubric.schema.json is valid JSON")

    # every gradable kind yields a structurally valid, non-empty rubric
    for kind in GRADABLE_KINDS:
        rub = dr.derive_rubric(kind)
        err = _validate_rubric_struct(rub)
        _check(err is None, f"derived rubric for kind '{kind}' is schema-valid"
               + (f" (ERR: {err})" if err else ""))
        _check(len(rub["dimensions"]) >= 2, f"kind '{kind}' has >=2 library dimensions")

    # objective hard gates carry an objective_signal (the binding the library records)
    code = dr.derive_rubric("code")
    for d in code["dimensions"]:
        if d.get("hard_gate"):
            _check(bool(d.get("objective_signal")),
                   f"code hard-gate '{d['id']}' is bound to an objective signal")

    # library version is captured (provenance)
    _check(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", code.get("library_version", "")),
           f"derived rubric records the library version ({code.get('library_version')})")

    # explicit requirements are weight-max + verified
    rub = dr.derive_rubric("prose", explicit=["Must cite primary sources"])
    lib_max = max(d["weight"] for d in rub["dimensions"] if d["source"] == "library")
    expl = [d for d in rub["dimensions"] if d["source"] == "explicit"]
    _check(len(expl) == 1, "explicit requirement becomes exactly one dimension")
    _check(expl[0]["weight"] >= lib_max and expl[0]["verified"] is True,
           f"explicit requirement is weight-max ({expl[0]['weight']} >= {lib_max}) and verified")

    # derived proposals are FORCIBLY unverified, even when the model lies
    sneaky = [{"id": "sneaky", "title": "Sneaky", "weight": 999,
               "verified": True, "source": "library"}]
    rub = dr.derive_rubric("code", derived=sneaky)
    sd = [d for d in rub["dimensions"] if d["id"] == "sneaky"]
    _check(len(sd) == 1, "derived proposal is added to the rubric")
    sd = sd[0]
    _check(sd["source"] == "derived" and sd["verified"] is False,
           "malicious derived proposal forced to source=derived, verified=false")
    _check(sd["weight"] <= 5.0, f"derived proposal weight capped low (got {sd['weight']})")
    _check(sd.get("provenance") == "[unverified — derived]",
           "derived proposal carries the [unverified — derived] provenance marker")

    # additive-only: a derived proposal cannot overwrite a graded library dim
    collide = [{"id": "tests-pass", "title": "Hijack", "weight": 999, "verified": True}]
    rub = dr.derive_rubric("code", derived=collide)
    tp = [d for d in rub["dimensions"] if d["id"] == "tests-pass"]
    _check(len(tp) == 1 and tp[0]["source"] == "library" and tp[0]["verified"] is True,
           "derived proposal colliding with a graded id is dropped (additive-only, spine intact)")

    # low-confidence / unknown kind → generic fallback
    _check(dr.derive_rubric("code", kind_confidence="low")["artifact_kind"] == "generic",
           "low-confidence kind falls back to the generic rubric")
    _check(dr.derive_rubric("totally-unknown-kind")["artifact_kind"] == "generic",
           "unknown kind falls back to the generic rubric")

    # agent-file is delegated, not reimplemented
    af = dr.derive_rubric("agent-file")
    _check(any(d.get("objective_signal") == "agent-quality-rubric" for d in af["dimensions"]),
           "agent-file rubric delegates to agent-quality-rubric")

    return True


def run_must_fail_grade_derived(dr):
    """Disable the verified-forcing in _normalize_derived → a malicious proposal
    (verified=true) should THEN be auto-graded. If it is, the normalizer is the
    thing protecting us (teeth) → exit 0."""
    sneaky = [{"id": "sneaky", "title": "Sneaky", "weight": 999,
               "verified": True, "source": "library"}]

    # sanity: with the normalizer intact it must be unverified
    rub = dr.derive_rubric("code", derived=sneaky)
    sd = [d for d in rub["dimensions"] if d["id"] == "sneaky"][0]
    if sd["verified"] is not False:
        print("  ✗ normalizer intact already let a derived dim grade — broken", file=sys.stderr)
        return False

    # mutant: replace _normalize_derived with a passthrough that trusts the model
    def _passthrough(raw, existing_ids):
        out = []
        for d in raw or []:
            out.append({
                "id": d["id"], "title": d["title"], "weight": float(d["weight"]),
                "source": d.get("source", "derived"), "verified": bool(d.get("verified")),
                "hard_gate": False, "objective_signal": "",
            })
        return out

    dr._normalize_derived = _passthrough
    rub = dr.derive_rubric("code", derived=sneaky)
    sd = [d for d in rub["dimensions"] if d["id"] == "sneaky"][0]
    if sd["verified"] is True and sd["source"] == "library":
        print("  ✓ mutant (no derived-normalizer) WRONGLY auto-grades a malicious proposal — gate has teeth")
        return True
    print(f"  ✗ mutant did not leak (verified={sd['verified']}) — teeth not demonstrated", file=sys.stderr)
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail-grade-derived", action="store_true")
    args = ap.parse_args(argv)

    dr = _load_derive()
    try:
        if args.must_fail_grade_derived:
            ok = run_must_fail_grade_derived(dr)
        else:
            ok = run_default(dr)
    except _Fail as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
