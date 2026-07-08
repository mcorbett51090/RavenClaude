#!/usr/bin/env python3
"""Seed a DOCUMENT-MAP.md — a flat topic->path index that lets a cold non-Claude-Code
agent (Copilot CLI / Cursor / Aider) resolve a known document in ~1 tool call instead of
re-running find/grep every turn. See plugins/ravenclaude-core/knowledge/copilot-cli-customization.md §7
and docs/best-practices/agent-onboarding.md.

SEED, NOT SOURCE OF TRUTH. This enumerates files and derives a *best-effort* title (frontmatter
`title:` / first `# H1` / humanised filename). It CANNOT synthesise good topic keys — the judgement
"this is the file an agent looks up when asked about X" is the load-bearing part and stays human.
Run it once to seed a map, then hand-curate the topic column. A stale map is worse than none.

Design guarantees (so a consumer *may* keep it generator-owned behind --check):
  * deterministic — every list is sorted; NO git-derived / timestamp fields (those go flaky under a
    shallow CI checkout, the Norns/Nidhogg class of bug this repo has hit before);
  * idempotent — the table lives between <!-- DOCUMENT-MAP:BEGIN/END --> markers; a hand-written
    preamble outside the markers is preserved across runs;
  * generic — scan roots / excludes are config-driven (--config), never hard-coded to one repo layout.

Usage:
  generate-document-map.py [--root DIR] [--output PATH] [--config PATH]
  generate-document-map.py --check      # exit 1 if the on-disk map differs from a fresh generation
  generate-document-map.py --self-test  # build a throwaway fixture tree, assert behaviour, exit 0/1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

BEGIN = "<!-- DOCUMENT-MAP:BEGIN -->"
END = "<!-- DOCUMENT-MAP:END -->"

DEFAULT_CONFIG = {
    "scan_globs": [
        "docs/**/*.md",
        "plugins/*/knowledge/*.md",
        "plugins/*/best-practices/*.md",
    ],
    # posix relpath prefixes to skip (point-in-time-by-convention trees)
    "exclude_prefixes": ["docs/plans/", "docs/research/", "docs/staging/"],
    # file-name regexes to skip: underscore-prefixed (_TEMPLATE.md &c) and dated one-offs
    "exclude_name_regexes": [r"^_", r"^\d{4}-\d{2}-\d{2}-"],
}


def load_config(path: Path | None) -> dict:
    if path is None:
        return DEFAULT_CONFIG
    user = json.loads(path.read_text(encoding="utf-8"))
    merged = dict(DEFAULT_CONFIG)
    merged.update(user)
    return merged


def is_excluded(relposix: str, name: str, cfg: dict) -> bool:
    if any(relposix.startswith(p) for p in cfg["exclude_prefixes"]):
        return True
    return any(re.search(rx, name) for rx in cfg["exclude_name_regexes"])


def humanise(stem: str) -> str:
    return re.sub(r"[-_]+", " ", stem).strip().title()


def derive_topic(path: Path) -> str:
    """frontmatter title -> first H1 -> humanised filename. The no-frontmatter/no-H1 path is the
    PRIMARY case (the overwhelming majority of docs have neither)."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return humanise(path.stem)
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            m = re.match(r"\s*title\s*:\s*(.+?)\s*$", line)
            if m:
                return m.group(1).strip().strip("\"'")
    for line in lines:
        m = re.match(r"#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip()
    return humanise(path.stem)


def escape_cell(text: str) -> str:
    """Markdown table cells: neutralise the pipe (column break) and angle/backtick chars that
    would render as HTML or break inline-code."""
    return (
        text.replace("\\", "")
        .replace("|", r"\|")
        .replace("`", "'")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def discover(root: Path, cfg: dict, skip: frozenset[str] = frozenset()) -> list[tuple[str, str, str]]:
    """Return sorted (group_label, topic, relposix) triples. `skip` names relposix paths to omit —
    notably the output map itself, which would otherwise index itself and break idempotency."""
    seen: set[str] = set()
    rows: list[tuple[str, str, str]] = []
    for glob in cfg["scan_globs"]:
        for path in root.glob(glob):
            if not path.is_file():
                continue
            rel = path.relative_to(root)
            relposix = rel.as_posix()
            if relposix in seen or relposix in skip or is_excluded(relposix, path.name, cfg):
                continue
            seen.add(relposix)
            group = rel.parent.as_posix() or "."
            rows.append((group, derive_topic(path), relposix))
    rows.sort(key=lambda r: (r[0], r[1].lower(), r[2]))
    return rows


def build_table(rows: list[tuple[str, str, str]]) -> str:
    if not rows:
        return "_No documents matched the scan roots._"
    out: list[str] = []
    current: str | None = None
    for group, topic, relposix in rows:
        if group != current:
            current = group
            out.append(f"\n### `{group}`\n")
            out.append("| Topic | File |")
            out.append("|---|---|")
        out.append(f"| {escape_cell(topic)} | `{escape_cell(relposix)}` |")
    return "\n".join(out).strip()


def coverage_note(cfg: dict) -> str:
    scanned = ", ".join(f"`{g}`" for g in cfg["scan_globs"])
    excluded = ", ".join(
        [f"`{p}`" for p in cfg["exclude_prefixes"]]
        + [f"`/{rx}/`" for rx in cfg["exclude_name_regexes"]]
    )
    return f"> Scanned: {scanned}. Excluded: {excluded}."


def render_default(table: str, cfg: dict) -> str:
    return (
        "# Document Map — quick reference for AI agents\n\n"
        "> Read this at session start: one grep or one view resolves any mapped document.\n"
        "> Topic labels are HAND-CURATED — the generator seeds paths + best-effort titles; edit the\n"
        "> topics, then treat this file as hand-owned. Re-running the generator overwrites the table.\n"
        f"{coverage_note(cfg)}\n\n"
        f"{BEGIN}\n{table}\n{END}\n"
    )


def splice(existing: str, table: str, cfg: dict) -> str:
    if BEGIN in existing and END in existing:
        head, rest = existing.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        return f"{head}{BEGIN}\n{table}\n{END}{tail}"
    # No markers in a hand-written file: append a fresh generated block, preserving the file.
    sep = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
    return f"{existing}{sep}{coverage_note(cfg)}\n\n{BEGIN}\n{table}\n{END}\n"


def _skip_for(root: Path, output: Path) -> frozenset[str]:
    try:
        return frozenset({output.relative_to(root).as_posix()})
    except ValueError:
        return frozenset()


def generate(root: Path, output: Path, cfg: dict) -> str:
    table = build_table(discover(root, cfg, _skip_for(root, output)))
    if output.exists():
        return splice(output.read_text(encoding="utf-8"), table, cfg)
    return render_default(table, cfg)


def cmd_write(root: Path, output: Path, cfg: dict) -> int:
    fresh = generate(root, output, cfg)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(fresh, encoding="utf-8")
    n = len(discover(root, cfg, _skip_for(root, output)))
    print(f"wrote {output} ({n} documents mapped)")
    return 0


def cmd_check(root: Path, output: Path, cfg: dict) -> int:
    if not output.exists():
        print(f"--check: {output} does not exist (nothing committed to keep fresh)", file=sys.stderr)
        return 1
    fresh = generate(root, output, cfg)
    if fresh == output.read_text(encoding="utf-8"):
        print(f"--check: {output} is fresh")
        return 0
    print(f"--check: {output} is STALE — re-run the generator", file=sys.stderr)
    return 1


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir()
        (root / "docs" / "plans").mkdir()
        (root / "plugins" / "x" / "knowledge").mkdir(parents=True)
        (root / "docs" / "foo.md").write_text("# Foo Report\n\nbody\n", encoding="utf-8")
        (root / "docs" / "2026-01-01-old-plan.md").write_text("# Old Plan\n", encoding="utf-8")
        (root / "docs" / "_TEMPLATE.md").write_text("# <placeholder>\n", encoding="utf-8")
        (root / "docs" / "plans" / "p.md").write_text("# Plan P\n", encoding="utf-8")
        (root / "plugins" / "x" / "knowledge" / "k.md").write_text(
            "---\ntitle: Kilo Concepts\n---\n# ignored h1\n", encoding="utf-8"
        )
        out = root / "docs" / "DOCUMENT-MAP.md"
        cfg = DEFAULT_CONFIG

        first = generate(root, out, cfg)
        checks = {
            "includes H1-derived topic": "Foo Report" in first,
            "includes frontmatter title": "Kilo Concepts" in first,
            "ignores H1 when frontmatter present": "ignored h1" not in first.lower(),
            "excludes dated-prefix file": "old-plan" not in first and "Old Plan" not in first,
            "excludes underscore file": "TEMPLATE" not in first and "placeholder" not in first,
            "excludes plans/ subtree": "Plan P" not in first,
            "escapes angle brackets (none leaked)": "<placeholder>" not in first,
            "has markers": BEGIN in first and END in first,
        }
        out.write_text(first, encoding="utf-8")
        # idempotency: a second generation over identical input is byte-identical
        checks["idempotent"] = generate(root, out, cfg) == first
        # --check passes on the fresh file
        checks["check-fresh-passes"] = cmd_check(root, out, cfg) == 0
        # preamble outside markers survives a regenerate
        edited = first.replace("body", "body").replace(
            "# Document Map", "# Document Map (hand-edited preamble)"
        )
        out.write_text(edited, encoding="utf-8")
        checks["preserves-preamble"] = "hand-edited preamble" in generate(root, out, cfg)
        # drift detection: mutating a mapped file makes --check fail
        (root / "docs" / "foo.md").write_text("# Foo Renamed\n", encoding="utf-8")
        checks["drift-detected"] = cmd_check(root, out, cfg) == 1

    failed = [name for name, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if failed:
        print(f"self-test FAILED: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("self-test OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Seed/refresh a DOCUMENT-MAP.md topic->path index.")
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="repo root to scan (default: cwd)")
    ap.add_argument("--output", type=Path, default=None, help="output path (default: <root>/docs/DOCUMENT-MAP.md)")
    ap.add_argument("--config", type=Path, default=None, help="JSON config overriding scan_globs/exclude_*")
    ap.add_argument("--check", action="store_true", help="exit 1 if the on-disk map is stale")
    ap.add_argument("--self-test", action="store_true", help="run built-in fixture tests and exit")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"root {root} is not a directory", file=sys.stderr)
        return 1
    output = (args.output or (root / "docs" / "DOCUMENT-MAP.md")).resolve()
    cfg = load_config(args.config)

    if args.check:
        return cmd_check(root, output, cfg)
    return cmd_write(root, output, cfg)


if __name__ == "__main__":
    raise SystemExit(main())
