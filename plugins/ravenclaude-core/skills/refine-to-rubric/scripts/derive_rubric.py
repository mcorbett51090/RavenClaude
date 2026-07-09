#!/usr/bin/env python3
"""derive_rubric.py — deterministic, MODEL-FREE assembly of a convergence rubric.

`derive-rubric` is the retrieval half of the Convergence Engine. It reads the
externalized, versioned rubric library (knowledge/convergence-rubrics.md — the
SPINE, the anti-reward-hack boundary) and emits a rubric.schema.json document for
a given artifact kind, merging in explicit user requirements at maximum weight.

What it DOES (deterministic):
  - parse the library's per-kind dimension tables (single source of truth);
  - select the kind's dimensions (or the generic fallback for a low-confidence /
    unknown kind);
  - bind each dimension's objective_signal + hard_gate from the table;
  - add explicit user requirements as source=explicit, verified=true, weight=MAX
    (a stated requirement always outranks a library default);
  - OPTIONALLY merge a set of model-proposed "commonly-missed" dimensions, but
    ONLY additively and ONLY as source=derived, verified=false — never graded.

What it does NOT do:
  - It never invents dimensions itself, and it never marks a derived dimension
    verified. The "commonly-missed" model pass happens OUTSIDE this script
    (a constrained prompt, see SKILL.md / the library); its raw output is passed
    in via --derived-json and is forcibly normalized to the unverified contract
    here, so even a misbehaving model cannot get a derived dim auto-graded.

CLI:
  python3 derive_rubric.py --kind code [--kind-confidence high]
        [--explicit "Must support offline mode" --explicit "..."]
        [--derived-json path/to/proposals.json]
      → prints a rubric.schema.json document to stdout. exit 0 on success,
        2 on I/O/parse/contract error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

SCHEMA_VERSION = "1.0.0"

REPO_RELATIVE_LIBRARY = os.path.join(
    "plugins", "ravenclaude-core", "knowledge", "convergence-rubrics.md"
)

# Kinds whose rubric is delegated to another skill rather than graded from the
# library tables directly. (agent-file → agent-quality-rubric.)
DELEGATED_KINDS = {"agent-file": "agent-quality-rubric"}

# The empty-signal sentinel the library uses for a judge-graded dimension.
_JUDGE_TOKENS = {"_(judge)_", "—", "", "-"}


def _find_library(explicit_path=None):
    """Locate the rubric library markdown. Honors an explicit path; otherwise
    walks up from this file to the repo root."""
    if explicit_path:
        return explicit_path
    here = os.path.dirname(os.path.abspath(__file__))
    cur = here
    for _ in range(8):
        cand = os.path.join(cur, REPO_RELATIVE_LIBRARY)
        if os.path.isfile(cand):
            return cand
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    # last resort: relative to cwd
    return REPO_RELATIVE_LIBRARY


_HEADING_RE = re.compile(r"^###\s+([a-z0-9][a-z0-9_-]*)\b", re.IGNORECASE)
_ROW_RE = re.compile(r"^\|(.+)\|\s*$")


def _clean_cell(cell):
    return cell.strip().strip("`").strip()


def parse_library(path):
    """Parse the per-kind dimension tables into a dict:
        {kind: [ {id, title, weight, hard_gate, objective_signal}, ... ]}

    Only sections whose markdown table has the canonical 5-column header
    (id | title | weight | hard_gate | objective_signal) are parsed as gradable
    library tables. The delegated agent-file table (different columns) is skipped
    here — delegation is handled by the caller.
    """
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    kinds = {}
    cur_kind = None
    in_table = False
    header_ok = False
    for line in lines:
        m = _HEADING_RE.match(line)
        if m:
            cur_kind = m.group(1).lower()
            in_table = False
            header_ok = False
            continue
        if cur_kind is None:
            continue
        rm = _ROW_RE.match(line)
        if not rm:
            in_table = False
            header_ok = False
            continue
        cells = [_clean_cell(c) for c in rm.group(1).split("|")]
        # header row?
        lowered = [c.lower() for c in cells]
        if lowered[:5] == ["id", "title", "weight", "hard_gate", "objective_signal"]:
            in_table = True
            header_ok = True
            kinds.setdefault(cur_kind, [])
            continue
        # separator row (---)
        if header_ok and all(set(c) <= set("-: ") for c in cells if c):
            continue
        if in_table and header_ok and len(cells) >= 5:
            did, title, weight_s, hard_s, sig = cells[0], cells[1], cells[2], cells[3], cells[4]
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", did or ""):
                continue
            try:
                weight = float(weight_s)
            except ValueError:
                continue
            hard_gate = hard_s.strip().lower() in ("yes", "true", "**yes**")
            signal = "" if sig in _JUDGE_TOKENS else sig
            # A judge-graded (empty objective_signal) dimension cannot be a hard
            # gate: the evaluator routes empty-signal dims to judge_dims and never
            # records a hard_gates entry, so a hard_gate=true here would silently
            # never block convergence (2026-07-09 review, Decision 3). Objective
            # gates are deterministic by design — judge scorecards are never
            # tripwires. Warn and neutralize so the rubric reflects real behavior
            # rather than carrying an unenforceable flag.
            if hard_gate and not signal:
                print(
                    f"derive_rubric: warning: dimension {did!r} in kind {cur_kind!r} "
                    "declares hard_gate=yes with no objective_signal — a judge-graded "
                    "hard gate is not enforceable and is being downgraded to a scored "
                    "(non-gating) dimension. Give it an objective_signal to make it a "
                    "real hard gate.",
                    file=sys.stderr,
                )
                hard_gate = False
            kinds.setdefault(cur_kind, []).append(
                {
                    "id": did,
                    "title": title,
                    "weight": weight,
                    "source": "library",
                    "verified": True,
                    "hard_gate": hard_gate,
                    "objective_signal": signal,
                }
            )
    return kinds


def _explicit_dimension(text, idx, max_weight):
    """Turn an explicit user requirement string into a graded dimension at
    weight-max. The id is derived deterministically; the title carries the text."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or f"req-{idx}"
    slug = f"explicit-{slug}"[:64]
    return {
        "id": slug,
        "title": text[:200],
        "weight": max_weight,
        "source": "explicit",
        "verified": True,
        "hard_gate": False,
        "objective_signal": "",
    }


def _normalize_derived(raw, existing_ids):
    """Force every model-proposed dimension onto the unverified contract:
    source=derived, verified=false, low weight, provenance marker. Drop any
    proposal that collides with an existing id (additive-only — cannot mutate the
    spine)."""
    out = []
    for i, d in enumerate(raw or []):
        did = str(d.get("id", "")).lower()
        did = re.sub(r"[^a-z0-9_-]+", "-", did).strip("-")[:64]
        if not did or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", did):
            did = f"derived-{i}"
        if did in existing_ids:
            continue  # additive only — never overwrite a graded dimension
        existing_ids.add(did)
        title = str(d.get("title", did))[:200] or did
        try:
            weight = float(d.get("weight", 1))
        except (TypeError, ValueError):
            weight = 1.0
        weight = max(0.0, min(weight, 5.0))  # derived dims are low-weight by contract
        out.append(
            {
                "id": did,
                "title": title,
                "weight": weight,
                "source": "derived",
                "verified": False,  # forced — a model can never get a derived dim graded
                "hard_gate": False,
                "objective_signal": "",
                "provenance": "[unverified — derived]",
            }
        )
    return out


def derive_rubric(kind, kind_confidence="high", explicit=None, derived=None, library_path=None):
    """Assemble a rubric dict (rubric.schema.json shape). Pure + deterministic for
    a given (kind, confidence, explicit, derived, library)."""
    lib = _find_library(library_path)
    if not os.path.isfile(lib):
        raise FileNotFoundError(f"rubric library not found: {lib}")
    tables = parse_library(lib)
    library_version = _library_version(lib)

    effective_kind = kind
    note_generic = False
    unknown_kind = kind not in tables and kind not in DELEGATED_KINDS
    if kind_confidence == "low" or unknown_kind:
        effective_kind = "generic"
        note_generic = True

    if kind in DELEGATED_KINDS and kind_confidence != "low":
        # Delegated kinds (agent-file) are handled by the caller; we still emit a
        # valid rubric whose single dimension records the delegation so the
        # scorecard contract holds and the schema validates.
        dims = [
            {
                "id": "delegated",
                "title": f"Delegated to {DELEGATED_KINDS[kind]}",
                "weight": 100,
                "source": "library",
                "verified": True,
                "hard_gate": False,
                "objective_signal": DELEGATED_KINDS[kind],
            }
        ]
    else:
        dims = [dict(d) for d in tables.get(effective_kind, tables.get("generic", []))]

    max_lib_weight = max((d["weight"] for d in dims), default=0.0)
    explicit_weight = max(max_lib_weight, 1.0)  # weight-max for explicit requirements

    existing_ids = {d["id"] for d in dims}
    for i, req in enumerate(explicit or []):
        ed = _explicit_dimension(req, i, explicit_weight)
        if ed["id"] in existing_ids:
            ed["id"] = f"{ed['id']}-{i}"[:64]
        existing_ids.add(ed["id"])
        dims.append(ed)

    dims.extend(_normalize_derived(derived, existing_ids))

    rubric = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": effective_kind if note_generic else kind,
        "kind_confidence": kind_confidence,
        "library_version": library_version,
        "dimensions": dims,
    }
    return rubric


_LIB_VERSION_RE = re.compile(r"Library version:\s*\*\*([0-9]+\.[0-9]+\.[0-9]+)\*\*")


def _library_version(path):
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = _LIB_VERSION_RE.search(line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return "0.0.0"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deterministically derive a convergence rubric.")
    ap.add_argument(
        "--kind",
        required=True,
        help="artifact kind (code/prose/visual-report/data/agent-file/generic)",
    )
    ap.add_argument("--kind-confidence", default="high", choices=["low", "medium", "high"])
    ap.add_argument(
        "--explicit", action="append", default=[], help="an explicit user requirement (repeatable)"
    )
    ap.add_argument(
        "--derived-json", help="path to a JSON array of model-proposed 'commonly-missed' dims"
    )
    ap.add_argument("--library", help="override the rubric library markdown path")
    args = ap.parse_args(argv)

    derived = None
    if args.derived_json:
        try:
            with open(args.derived_json, encoding="utf-8") as fh:
                derived = json.load(fh)
            if not isinstance(derived, list):
                raise ValueError("derived-json must be a JSON array")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"derive_rubric: bad --derived-json: {exc}", file=sys.stderr)
            return 2

    try:
        rubric = derive_rubric(
            args.kind,
            kind_confidence=args.kind_confidence,
            explicit=args.explicit,
            derived=derived,
            library_path=args.library,
        )
    except (OSError, ValueError) as exc:
        print(f"derive_rubric: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(rubric, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
