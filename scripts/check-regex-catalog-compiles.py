#!/usr/bin/env python3
"""Compile every regex in every registered catalog. A malformed one fails the build.

A regex catalog is any shipped file whose entries are compiled at RUNTIME by a
consumer of this plugin. That timing is the whole problem: a malformed pattern is
not a syntax error anyone sees at author time, it is a silent disarming of
whatever the pattern was guarding, discovered (if ever) by the absence of an
alarm that should have fired.

Two live consumers, both verified to swallow the failure:

  * `thing-concerns.py::_matches` catches `re.error` and continues, so the soft
    routing path stays available - which means a broken trigger simply stops
    gating. (Gate 16 already compiles this catalog; this checker subsumes it
    through the shared engine rather than re-deriving the parse.)
  * `thing-denial-kb-recall.sh:25` runs the recall with `2>/dev/null || true`,
    so a `re.error` raised while matching a rule is discarded, the digest comes
    back empty, and the hook exits 0. The denial KB stops surfacing resolutions
    and says nothing. Nothing compiled these patterns before this gate.

Fail-closed in three directions, because the ways this check could quietly pass
are the ways its subjects quietly failed:
  * a malformed regex               -> exit 2
  * a catalog file that cannot be read or parsed -> exit 2
  * a selector that matches ZERO regexes -> exit 2. An extractor that silently
    finds nothing reports the same "all clear" as one that found everything and
    is the defect class this whole initiative exists to kill.

Exit codes:  0 = every catalog compiled;  2 = any failure. Exit 1 is never used.

Usage:
    python3 scripts/check-regex-catalog-compiles.py
    python3 scripts/check-regex-catalog-compiles.py --path P --selector S
    python3 scripts/check-regex-catalog-compiles.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple


class CatalogError(Exception):
    """The catalog could not be read, parsed, or yielded no regexes."""


class Found(NamedTuple):
    where: str  # human-readable location within the catalog
    pattern: str


# ── Extractors ───────────────────────────────────────────────────────────────
# Each takes raw file text and a selector, and returns the regexes it names.
# Adding a catalog means registering a (path, extractor, selector) triple - the
# reusable half the build plan asked for.


def extract_json(text: str, selector: str) -> list[Found]:
    """Walk a dotted selector over a JSON document.

    Selector grammar is deliberately tiny: dotted keys, with `[]` meaning "every
    element of this list". e.g. `rules[].match.pattern`.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CatalogError(f"not valid JSON: {exc}") from exc

    out: list[Found] = []

    def walk(node, parts: list[str], trail: str) -> None:
        if not parts:
            if isinstance(node, str):
                out.append(Found(trail, node))
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    if isinstance(item, str):
                        out.append(Found(f"{trail}[{i}]", item))
            return
        head, rest = parts[0], parts[1:]
        if head.endswith("[]"):
            key = head[:-2]
            seq = node.get(key) if isinstance(node, dict) else None
            if isinstance(seq, list):
                for i, item in enumerate(seq):
                    walk(item, rest, f"{trail}.{key}[{i}]" if trail else f"{key}[{i}]")
        elif isinstance(node, dict) and head in node:
            walk(node[head], rest, f"{trail}.{head}" if trail else head)

    walk(data, selector.split("."), "")
    return out


def extract_md_yaml_triggers(text: str, selector: str) -> list[Found]:
    """The concerns-catalog shape: a fenced yaml block whose entries carry
    `triggers.regex` lists, under `cross_cutting` and under every `categories.*`.

    `selector` is accepted for interface parity and names the field walked.
    """
    try:
        import yaml  # noqa: PLC0415 - optional; absence is reported, never swallowed
    except ImportError as exc:
        raise CatalogError(
            "PyYAML is not installed, so this catalog cannot be compiled. "
            "THIS IS NOT A PASS - install PyYAML or run where it is present."
        ) from exc

    m = re.search(r"```yaml\n(.*?)```", text, re.S)
    if not m:
        raise CatalogError("no fenced ```yaml block found")
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except Exception as exc:  # noqa: BLE001 - any parse failure is a hard failure
        raise CatalogError(f"yaml block did not parse: {exc}") from exc

    field = selector.rsplit(".", 1)[-1] or "regex"
    out: list[Found] = []

    def collect(entries, group: str) -> None:
        for entry in entries or []:
            if not isinstance(entry, dict):
                continue
            ident = entry.get("id") or entry.get("name") or "?"
            for rx in ((entry.get("triggers") or {}).get(field) or []):
                out.append(Found(f"{group}/{ident}", rx))

    collect(data.get("cross_cutting"), "cross_cutting")
    for cat, entries in (data.get("categories") or {}).items():
        if isinstance(entries, list):
            collect(entries, f"categories.{cat}")
    return out


EXTRACTORS = {
    "json": extract_json,
    "md-yaml-triggers": extract_md_yaml_triggers,
}


# ── The registry ─────────────────────────────────────────────────────────────
# (label, path, extractor, selector). Every entry is a catalog whose regexes are
# compiled at runtime by something that swallows the failure.

CATALOGS = [
    (
        "concerns-catalog (tribunal triggers)",
        "plugins/ravenclaude-core/knowledge/concerns-catalog.md",
        "md-yaml-triggers",
        "triggers.regex",
    ),
    (
        "thing-denial-resolutions (KB rule category)",
        "plugins/ravenclaude-core/knowledge/thing-denial-resolutions.json",
        "json",
        "rules[].match.category",
    ),
    (
        "thing-denial-resolutions (KB rule pattern)",
        "plugins/ravenclaude-core/knowledge/thing-denial-resolutions.json",
        "json",
        "rules[].match.pattern",
    ),
]


def compile_catalog(path: Path, extractor: str, selector: str) -> list[str]:
    """Return a list of failure strings; empty means the catalog is clean."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]

    try:
        found = EXTRACTORS[extractor](text, selector)
    except CatalogError as exc:
        return [f"{path} [{selector}]: {exc}"]

    if not found:
        return [
            f"{path} [{selector}]: selector matched ZERO regexes. A checker that "
            "finds nothing reports the same 'clean' as one that checked everything - "
            "fix the selector or drop the entry."
        ]

    failures = []
    for where, pattern in found:
        try:
            re.compile(pattern)
        except re.error as exc:
            failures.append(f"{path} [{where}]: uncompilable regex {pattern!r} -> {exc}")
    return failures


def run(catalogs) -> int:
    total = 0
    failures: list[str] = []
    unrunnable: list[str] = []

    for label, rel, extractor, selector in catalogs:
        path = Path(rel)
        errs = compile_catalog(path, extractor, selector)
        if errs and "PyYAML is not installed" in errs[0]:
            unrunnable.append(f"{label}: {errs[0]}")
            continue
        if errs:
            failures.extend(errs)
            continue
        text = path.read_text(encoding="utf-8")
        n = len(EXTRACTORS[extractor](text, selector))
        total += n
        print(f"  ok  {label}: {n} regex(es) compiled")

    if unrunnable:
        # Mirrors the suite's _skip_or_fail contract: a skip is never a pass, and
        # in CI an unrunnable check is a hard failure, not a quiet allowance.
        for u in unrunnable:
            print(f"  !!  {u}", file=sys.stderr)
        if os.environ.get("CI"):
            print("check-regex-catalog-compiles: UNRUNNABLE in CI", file=sys.stderr)
            return 2
        print("  THIS IS NOT A PASS - re-run where PyYAML is present.", file=sys.stderr)

    if failures:
        print(f"check-regex-catalog-compiles: {len(failures)} failure(s)", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 2

    print(f"check-regex-catalog-compiles: {total} regex(es) across "
          f"{len(catalogs) - len(unrunnable)} catalog(s) all compile")
    return 0


# ── Teeth ────────────────────────────────────────────────────────────────────


def self_test() -> int:
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)

        # M1 - a malformed regex in the JSON catalog must be caught.
        src = Path("plugins/ravenclaude-core/knowledge/thing-denial-resolutions.json")
        data = json.loads(src.read_text(encoding="utf-8"))
        data["rules"][0].setdefault("match", {})["pattern"] = "unclosed(group"
        bad_json = work / "bad.json"
        bad_json.write_text(json.dumps(data), encoding="utf-8")
        errs = compile_catalog(bad_json, "json", "rules[].match.pattern")
        if any("uncompilable" in e for e in errs):
            print("  ✓ caught: a malformed regex in the JSON catalog")
        else:
            ok = False
            print(f"  ✗ MISSED: malformed JSON-catalog regex (got {errs})")

        # M2 - a selector that matches nothing must fail, not pass silently.
        errs = compile_catalog(src, "json", "rules[].match.no_such_field")
        if any("ZERO regexes" in e for e in errs):
            print("  ✓ caught: a selector matching zero regexes")
        else:
            ok = False
            print(f"  ✗ MISSED: zero-match selector reported clean (got {errs})")

        # M3 - an unreadable / unparseable catalog must fail closed.
        broken = work / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        errs = compile_catalog(broken, "json", "rules[].match.pattern")
        if errs:
            print("  ✓ caught: an unparseable catalog fails closed")
        else:
            ok = False
            print("  ✗ MISSED: an unparseable catalog was accepted")

        errs = compile_catalog(work / "absent.json", "json", "rules[].match.pattern")
        if errs:
            print("  ✓ caught: a missing catalog file fails closed")
        else:
            ok = False
            print("  ✗ MISSED: a missing catalog file was accepted")

        # M4 - a malformed trigger in the markdown/yaml catalog must be caught.
        md = Path("plugins/ravenclaude-core/knowledge/concerns-catalog.md")
        try:
            import yaml  # noqa: F401,PLC0415
        except ImportError:
            print("  !! md-yaml teeth SKIPPED - PyYAML absent. THIS IS NOT A PASS.")
        else:
            text = md.read_text(encoding="utf-8")
            # Corrupt the FIRST trigger regex line inside the yaml block.
            lines = text.splitlines()
            hit = next(
                (i for i, ln in enumerate(lines) if re.match(r"^\s+-\s+'.*'\s*$", ln)
                 and "regex" in "\n".join(lines[max(0, i - 4):i])),
                None,
            )
            if hit is None:
                ok = False
                print("  ✗ MISSED: could not locate a trigger regex line to corrupt")
            else:
                indent = len(lines[hit]) - len(lines[hit].lstrip())
                lines[hit] = " " * indent + "- 'unclosed(group'"
                bad_md = work / "bad-catalog.md"
                bad_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
                errs = compile_catalog(bad_md, "md-yaml-triggers", "triggers.regex")
                if any("uncompilable" in e for e in errs):
                    print("  ✓ caught: a malformed trigger in the yaml catalog")
                else:
                    ok = False
                    print(f"  ✗ MISSED: malformed yaml-catalog trigger (got {errs})")

        # Companion - the live registry must be clean (anti-flood).
        clean = all(not compile_catalog(Path(p), e, s) for _, p, e, s in CATALOGS)
        if clean:
            print("  ✓ clean:  every registered catalog compiles as shipped")
        else:
            ok = False
            print("  ✗ FLOODED on the live registry")

    print("\nteeth verified" if ok else "\nTEETH BROKEN")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", help="compile a single catalog at this path")
    ap.add_argument("--selector", help="field selector within that catalog")
    ap.add_argument(
        "--extractor",
        choices=sorted(EXTRACTORS),
        default="json",
        help="how to read the catalog (default: json)",
    )
    ap.add_argument("--self-test", action="store_true", help="prove the checker's teeth")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.path:
        if not args.selector:
            print("--path requires --selector", file=sys.stderr)
            return 2
        return run([(args.path, args.path, args.extractor, args.selector)])

    return run(CATALOGS)


if __name__ == "__main__":
    sys.exit(main())
