#!/usr/bin/env python3
"""Unpack or clean tests/fixtures/visual-feedback-loop/fixtures.pack.json.

  unpack-vfl-fixtures.py <pack.json> <dest-dir>           # unpack members
  unpack-vfl-fixtures.py --clean <pack.json> <dest-dir>   # remove members only

When DEST is the canonical fixtures directory, member bodies are written
verbatim (path strings stay repo-relative for driver.py path guards).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CANON = "tests/fixtures/visual-feedback-loop"


def _members(pack: Path) -> dict:
    return json.loads(pack.read_text())


def unpack(pack: Path, dest: Path) -> int:
    members = _members(pack)
    dest.mkdir(parents=True, exist_ok=True)
    rewrite = dest.resolve() != Path(CANON).resolve()
    for rel, body in members.items():
        out = dest / rel
        if out.resolve() == pack.resolve():
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body.replace(CANON, str(dest)) if rewrite else body)
    print(f"unpacked {len(members)} fixtures -> {dest}")
    return 0


def clean(pack: Path, dest: Path) -> int:
    members = _members(pack)
    for rel in members:
        p = dest / rel
        if p.is_file() and p.resolve() != pack.resolve():
            p.unlink()
    for d in sorted(dest.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    print(f"cleaned {len(members)} fixtures from {dest}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--clean":
        if len(args) != 3:
            print(f"usage: {sys.argv[0]} --clean <pack.json> <dest-dir>", file=sys.stderr)
            return 2
        return clean(Path(args[1]), Path(args[2]))
    if len(args) != 2:
        print(f"usage: {sys.argv[0]} <pack.json> <dest-dir>", file=sys.stderr)
        print(f"       {sys.argv[0]} --clean <pack.json> <dest-dir>", file=sys.stderr)
        return 2
    return unpack(Path(args[0]), Path(args[1]))


if __name__ == "__main__":
    raise SystemExit(main())
