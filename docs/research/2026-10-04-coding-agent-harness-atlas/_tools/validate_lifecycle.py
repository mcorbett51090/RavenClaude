"""Rule R14 for validate.py: the lifecycle layer is internally consistent and grounded in the cells.

Checks data/lifecycle.json (concepts, glossary, row map), data/lifecycle-lines.json (one plain and
one technical line per agent and concept, each tied to its cells by a content hash) and
data/trees.json (decision points quoting the cells verbatim). The files are optional: when none
exists there is nothing to check. Returns ``[(level, rule, where, message)]``.
"""

from pathlib import Path

import lifecycle_common as lc
from atlas_common import load_json

RULE = "R14-lifecycle"
WHO = ("harness code", "a model call", "both")
GAPS = (None, "partial", "full")
UNCOVERED_REASONS = ("product-lifecycle", "packaging", "org-admin", "alternate-context")
MAX_UNCOVERED = 0.15
LIMITS = {
    "name_plain": 60,
    "what_it_does": 300,
    "predicate_general": 200,
    "matters_for_model_choice": 250,
}
DP_MAX = 6


def _err(out, where, message):
    out.append(("error", RULE, where, message))


def _load(path, out):
    if not path.exists():
        return None
    try:
        return load_json(path)
    except (OSError, ValueError) as exc:
        _err(out, path.name, f"unreadable: {exc}")
        return None


def check(data_dir):
    data_dir = Path(data_dir)
    out = []
    life = _load(data_dir / "lifecycle.json", out)
    lines = _load(data_dir / "lifecycle-lines.json", out)
    trees = _load(data_dir / "trees.json", out)
    if life is None:
        if lines is not None or trees is not None:
            _err(out, "lifecycle.json", "missing, but lines or trees exist")
        return out
    facets = _load(data_dir / "facets.json", out)
    surfaces = _load(data_dir / "surfaces.json", out)
    if not isinstance(facets, dict) or not isinstance(surfaces, dict):
        return out
    rows = {r["id"] for f in facets.get("facets", []) for r in f.get("rows", [])}
    sids = [s["id"] for s in surfaces.get("surfaces", [])]
    concepts = _check_skeleton(life, rows, out)
    cells = {}
    for sid in sids:
        path = data_dir / "cells" / f"{sid}.json"
        cells[sid] = load_json(path).get("cells", []) if path.exists() else []
    glossary = list(life.get("glossary", {}))
    if lines is not None:
        _check_lines(lines, concepts, cells, glossary, sids, out)
    if trees is not None:
        _check_trees(trees, cells, sids, out)
    return out


def _check_skeleton(life, rows, out):
    stages = {s.get("id") for s in life.get("stages", [])}
    concepts = {}
    glossary = life.get("glossary", {})
    for c in life.get("concepts", []):
        cid = c.get("id")
        where = f"lifecycle.json {cid}"
        if cid in concepts or not cid:
            _err(out, where, "duplicate or empty concept id")
            continue
        concepts[cid] = c
        if c.get("stage") not in stages:
            _err(out, where, f"unknown stage {c.get('stage')!r}")
        if c.get("who_normally_does_it") not in WHO:
            _err(out, where, f"who_normally_does_it must be one of {WHO}")
        if c.get("gap") not in GAPS:
            _err(out, where, "gap must be null, 'partial' or 'full'")
        if (c.get("gap") == "full") != (not c.get("rows")):
            _err(out, where, "a concept has no rows exactly when its gap is 'full'")
        for key, limit in LIMITS.items():
            text = c.get(key) or ""
            if not text or len(text) > limit:
                _err(out, where, f"{key} is empty or over {limit} characters")
            if key != "name_plain" and lc.code_tokens(text):
                _err(out, where, f"{key} contains code-like text: {lc.code_tokens(text)[:3]}")
        for term in c.get("jargon", []):
            if term not in glossary:
                _err(out, where, f"jargon term {term!r} has no glossary entry")
    ids = set(concepts)
    for cid, c in concepts.items():
        for key in ("typical_after", "depends_on"):
            for other in c.get(key, []):
                if other not in ids:
                    _err(out, f"lifecycle.json {cid}", f"{key} names unknown concept {other!r}")
    by_stage = {}
    for c in concepts.values():
        by_stage.setdefault(c["stage"], []).append(c.get("order"))
    for stage, orders in by_stage.items():
        if sorted(orders) != list(range(1, len(orders) + 1)):
            _err(
                out,
                f"lifecycle.json stage {stage}",
                f"order must run 1..{len(orders)}, got {sorted(orders)}",
            )
    seen = {}
    for cid, c in concepts.items():
        for row in c.get("rows", []):
            if row not in rows:
                _err(out, f"lifecycle.json {cid}", f"unknown row {row}")
            if row in seen:
                _err(out, f"lifecycle.json {cid}", f"row {row} is also mapped by {seen[row]}")
            seen[row] = cid
    uncovered = life.get("uncovered", [])
    for u in uncovered:
        if u.get("reason") not in UNCOVERED_REASONS or u.get("row") not in rows:
            _err(out, "lifecycle.json uncovered", f"bad uncovered entry {u}")
        if u.get("row") in seen:
            _err(out, "lifecycle.json uncovered", f"{u.get('row')} is both mapped and uncovered")
    missing = rows - set(seen) - {u.get("row") for u in uncovered}
    for row in sorted(missing):
        _err(
            out,
            "lifecycle.json",
            f"row {row} is neither mapped to a concept nor listed as uncovered",
        )
    if rows and len(uncovered) / len(rows) > MAX_UNCOVERED:
        _err(
            out,
            "lifecycle.json uncovered",
            f"{len(uncovered)} uncovered rows is over {MAX_UNCOVERED:.0%}",
        )
    return concepts


def _check_lines(lines, concepts, cells, glossary, sids, out):
    agents = lines.get("agents", {})
    for sid in sids:
        entries = agents.get(sid)
        if entries is None:
            _err(out, f"lifecycle-lines.json {sid}", "no lines for this agent")
            continue
        for cid, concept in concepts.items():
            where = f"lifecycle-lines.json {sid}/{cid}"
            entry = entries.get(cid)
            if not concept.get("rows"):
                if entry is not None:
                    _err(out, where, "a gap concept (no rows) must not have an authored line")
                continue
            if entry is None:
                _err(out, where, "missing line")
                continue
            sub = lc.concept_cells(cells, sid, concept)
            for problem in lc.line_problems(entry, sub, glossary):
                _err(out, where, problem)
        for cid in entries:
            if cid not in concepts:
                _err(out, f"lifecycle-lines.json {sid}/{cid}", "line for an unknown concept")
    for sid in agents:
        if sid not in sids:
            _err(out, f"lifecycle-lines.json {sid}", "unknown agent")


def _check_trees(trees, cells, sids, out):
    for sid, tree in trees.get("agents", {}).items():
        if sid not in sids:
            _err(out, f"trees.json {sid}", "unknown agent")
            continue
        index = {c["id"]: c for c in cells.get(sid, [])}
        points = tree.get("decision_points", [])
        if len(points) > DP_MAX:
            _err(out, f"trees.json {sid}", f"{len(points)} decision points, over {DP_MAX}")
        ids = set()
        for dp in points:
            where = f"trees.json {sid}/{dp.get('id')}"
            if dp.get("id") in ids:
                _err(out, where, "duplicate decision point id")
            ids.add(dp.get("id"))
            cell = index.get(dp.get("cell"))
            if cell is None:
                _err(out, where, f"unknown cell {dp.get('cell')}")
                continue
            corpus = lc.squash(f"{cell.get('value') or ''} {cell.get('limitation') or ''}")
            question = dp.get("question", "")
            if not question or len(question) > 110 or lc.code_tokens(question):
                _err(out, where, "question is empty, over 110 characters or contains code")
            branches = dp.get("branches", [])
            if len(branches) < 2:
                _err(out, where, "fewer than 2 branches")
            clauses = []
            for b in branches:
                clause = lc.squash(b.get("clause", ""))
                if len(clause) < 20 or clause not in corpus:
                    _err(
                        out,
                        where,
                        f"clause is not a verbatim stretch of {dp.get('cell')}: {clause[:50]!r}",
                    )
                if clause in clauses:
                    _err(out, where, "two branches use the same clause")
                clauses.append(clause)
                if (
                    not b.get("answer")
                    or len(b["answer"]) > 60
                    or not b.get("outcome")
                    or len(b["outcome"]) > 160
                ):
                    _err(out, where, "a branch answer or outcome is missing or too long")
                for field in ("answer", "outcome"):
                    text = b.get(field, "")
                    if "`" in text or [t for t in lc.code_tokens(text) if t not in lc.ALLOWED_CAPS]:
                        _err(out, where, f"code in branch {field}")
