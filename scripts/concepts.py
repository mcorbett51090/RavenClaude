#!/usr/bin/env python3
"""concepts.py — single-source loader/validator for the Learn-tab concepts.

Reads `plugins/ravenclaude-core/knowledge/concepts/*.md` — one concept per file:
YAML frontmatter + a markdown body + a ```mermaid full diagram and an optional
```mermaid-mini tooltip diagram. Validates the schema and emits the
byte-deterministic portal contract `plugins/ravenclaude-core/concepts.json`.

This is also the import surface for `generate-dashboards.py` (Learn tab +
tooltip registry) and `generate-concepts-doc.py` (docs export): call
`load_concepts(root)` to get validated concept dicts.

Usage:
    concepts.py [--root DIR]            # (re)generate concepts.json
    concepts.py --check [--root DIR]    # schema + staleness + freshness gate
                                        #   (exit 1 on any violation or drift)

The `--check` mode is the CI gate: it re-derives the registry in memory and
diffs it against the committed concepts.json, enforces the schema, and fails
platform-fact concepts whose `last_verified` is older than STALE_DAYS.
"""

from __future__ import annotations

import argparse
import datetime
import glob
import json
import re
import sys
from pathlib import Path

CONCEPTS_GLOB = "plugins/ravenclaude-core/knowledge/concepts/*.md"
REGISTRY_PATH = "plugins/ravenclaude-core/concepts.json"
VISUALS_DIR = "plugins/ravenclaude-core/knowledge/concepts/visuals"
SVG_REL_PREFIX = "knowledge/concepts/visuals"
SCHEMA_VERSION = 1
STALE_DAYS = 90  # platform-fact concepts older than this fail --check

VALID_KINDS = ("platform-fact", "ravenclaude-built")
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_MERMAID_RE = re.compile(r"```(mermaid(?:-mini)?)[^\n]*\n(.*?)```", re.DOTALL)
_MINI_MARKER_RE = re.compile(r"<!--\s*mini\s*-->\s*", re.IGNORECASE)


class ConceptError(Exception):
    """A schema/validation failure tied to a specific concept file."""


def _today() -> datetime.date:
    return datetime.date.today()


def _parse_one(path: Path) -> dict:
    """Parse and schema-validate a single concept file. Raises ConceptError."""
    import yaml  # local import so a missing pyyaml degrades to a clear message

    rel = path.name
    stem = path.stem
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        raise ConceptError(f"{rel}: no YAML frontmatter (missing leading '---' block)")
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as exc:  # strict-YAML parse error
        raise ConceptError(f"{rel}: frontmatter does not parse — {type(exc).__name__}: {str(exc).splitlines()[0]}")
    if not isinstance(fm, dict):
        raise ConceptError(f"{rel}: frontmatter is not a mapping")

    def req(key: str, typ) -> object:
        if key not in fm:
            raise ConceptError(f"{rel}: missing required field '{key}'")
        val = fm[key]
        if not isinstance(val, typ) or (isinstance(val, str) and not val.strip()):
            raise ConceptError(f"{rel}: field '{key}' must be a non-empty {getattr(typ, '__name__', typ)}")
        return val

    cid = req("id", str)
    if not _ID_RE.match(cid):
        raise ConceptError(f"{rel}: id '{cid}' must be a lowercase slug (a-z, 0-9, hyphen)")
    if cid != stem:
        raise ConceptError(f"{rel}: id '{cid}' must match the filename stem '{stem}'")
    title = req("title", str)
    category = req("category", str)
    kind = req("kind", str)
    if kind not in VALID_KINDS:
        raise ConceptError(f"{rel}: kind '{kind}' must be one of {VALID_KINDS}")
    order = req("order", int)
    summary = req("summary", str)
    if len(summary) > 200:
        raise ConceptError(f"{rel}: summary is {len(summary)} chars (max 200 — it is a tooltip)")

    sources = fm.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ConceptError(f"{rel}: 'sources' must be a non-empty list of {{label, url}}")
    norm_sources = []
    for i, s in enumerate(sources):
        if not isinstance(s, dict) or not isinstance(s.get("label"), str) or not isinstance(s.get("url"), str):
            raise ConceptError(f"{rel}: sources[{i}] must have string 'label' and 'url'")
        norm_sources.append({"label": s["label"], "url": s["url"]})

    see_also = fm.get("see_also", [])
    if not isinstance(see_also, list) or not all(isinstance(x, str) for x in see_also):
        raise ConceptError(f"{rel}: 'see_also' must be a list of concept ids")

    last_verified = fm.get("last_verified")
    if last_verified is not None:
        # PyYAML may parse an unquoted YYYY-MM-DD into a date; accept both.
        if isinstance(last_verified, datetime.date):
            last_verified = last_verified.isoformat()
        elif isinstance(last_verified, str):
            try:
                datetime.date.fromisoformat(last_verified)
            except ValueError:
                raise ConceptError(f"{rel}: last_verified '{last_verified}' must be YYYY-MM-DD")
        else:
            raise ConceptError(f"{rel}: last_verified must be a YYYY-MM-DD string")
    if kind == "platform-fact" and not last_verified:
        raise ConceptError(f"{rel}: platform-fact concepts require 'last_verified' (staleness gate)")

    refresh_when = fm.get("refresh_when")
    if refresh_when is not None and not isinstance(refresh_when, str):
        raise ConceptError(f"{rel}: 'refresh_when' must be a string")

    # Body + diagrams.
    rest = m.group(2)
    diagrams = {"mermaid": None, "mermaid-mini": None}
    for kind_tag, src in _MERMAID_RE.findall(rest):
        if diagrams.get(kind_tag):
            raise ConceptError(f"{rel}: more than one ```{kind_tag} block")
        diagrams[kind_tag] = src.strip()
    if not diagrams["mermaid"]:
        raise ConceptError(f"{rel}: missing the required ```mermaid full diagram block")

    body_md = _MERMAID_RE.sub("", rest)
    body_md = _MINI_MARKER_RE.sub("", body_md).strip()
    if not body_md:
        raise ConceptError(f"{rel}: empty body (need an explanation, not just a diagram)")

    has_mini = diagrams["mermaid-mini"] is not None
    return {
        "id": cid,
        "title": title,
        "category": category,
        "kind": kind,
        "order": order,
        "summary": summary,
        "see_also": list(see_also),
        "last_verified": last_verified,
        "refresh_when": refresh_when,
        "sources": norm_sources,
        "body_md": body_md,
        "diagram": diagrams["mermaid"],
        "diagram_mini": diagrams["mermaid-mini"],
        "svg": f"{SVG_REL_PREFIX}/{cid}.svg",
        "svg_mini": f"{SVG_REL_PREFIX}/{cid}.mini.svg" if has_mini else None,
    }


def load_concepts(root: Path) -> list[dict]:
    """Parse + validate every concept. Raises ConceptError on the first problem
    (cross-reference checks run after all files parse). Returns the canonical
    sort order: by (category-min-order, category, order, id)."""
    files = sorted(glob.glob(str(root / CONCEPTS_GLOB)))
    if not files:
        return []
    concepts = [_parse_one(Path(f)) for f in files]

    ids = {c["id"] for c in concepts}
    for c in concepts:
        for ref in c["see_also"]:
            if ref not in ids:
                raise ConceptError(f"{c['id']}: see_also references unknown concept '{ref}'")

    cat_min = {}
    for c in concepts:
        cat_min[c["category"]] = min(cat_min.get(c["category"], c["order"]), c["order"])
    concepts.sort(key=lambda c: (cat_min[c["category"]], c["category"], c["order"], c["id"]))
    return concepts


def build_registry(root: Path) -> dict:
    concepts = load_concepts(root)
    cat_min: dict[str, int] = {}
    for c in concepts:
        cat_min[c["category"]] = min(cat_min.get(c["category"], c["order"]), c["order"])
    categories = [
        {"name": name, "order": order}
        for name, order in sorted(cat_min.items(), key=lambda kv: (kv[1], kv[0]))
    ]
    return {"schema_version": SCHEMA_VERSION, "categories": categories, "concepts": concepts}


def _serialize(registry: dict) -> str:
    return json.dumps(registry, indent=2, ensure_ascii=False) + "\n"


def _staleness_violations(concepts: list[dict]) -> list[str]:
    today = _today()
    out = []
    for c in concepts:
        if c["kind"] != "platform-fact" or not c["last_verified"]:
            continue
        age = (today - datetime.date.fromisoformat(c["last_verified"])).days
        if age > STALE_DAYS:
            out.append(f"  ✗ {c['id']}: last_verified {c['last_verified']} is {age} days old (> {STALE_DAYS})")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--check", action="store_true", help="gate mode: validate + diff, never write")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out_path = root / REGISTRY_PATH

    try:
        registry = build_registry(root)
    except ConceptError as exc:
        print(f"Concept schema validation FAILED:\n  ✗ {exc}")
        return 1

    serialized = _serialize(registry)

    if args.check:
        problems = _staleness_violations(registry["concepts"])
        if problems:
            print("Concept staleness gate FAILED — refresh last_verified after re-checking the source:")
            print("\n".join(problems))
            return 1
        if not out_path.exists():
            print(f"concepts.json missing at {REGISTRY_PATH} — run: scripts/concepts.py")
            return 1
        if out_path.read_text(encoding="utf-8") != serialized:
            print(f"concepts.json is STALE — regenerate with: scripts/concepts.py")
            return 1
        print(f"Concepts OK — {len(registry['concepts'])} concept(s), registry fresh, no stale platform-facts.")
        return 0

    out_path.write_text(serialized, encoding="utf-8")
    print(f"Wrote {REGISTRY_PATH} — {len(registry['concepts'])} concept(s) in {len(registry['categories'])} categor(ies).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
