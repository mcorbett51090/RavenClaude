#!/usr/bin/env python3
"""rc-artifacts.py — the cross-CLI work-file index (`bin/rc artifacts`).

WHAT PROBLEM THIS SOLVES. Any CLI may be the one working in a repo — Claude Code,
Copilot, Codex, Cursor, Gemini, Aider — and the next session may be a different
one. The storage contract in `AGENTS.md` § "Where work files go" says where files
belong; this command is how a CLI *finds* what is already there, and creates a
new directory in the right shape without anyone memorising the layout.

WHY THE LISTING IS DERIVED, NOT MAINTAINED. A hand-kept index of artifacts is a
file that goes stale the first time somebody writes a directory without updating
it — and a stale index is worse than none, because it is believed. This repo has
been bitten by exactly that class of defect repeatedly. So `list` **scans the
filesystem every time**. There is no index file to drift.

PROVENANCE. Each run directory carries a `meta.json` naming the CLI that created
it. That is what lets one tool pick up another's work knowingly rather than by
guessing. A directory without one is reported as `unstamped` — honestly, not
silently — because an unknown origin is a fact worth showing, not hiding.

TWO TIERS, per the contract:
  local      .ravenclaude/runs/<task-id>/     gitignored — this machine only
  committed  docs/plans|decisions|research/   travels via git to teammates + CI

`new` only ever creates in the LOCAL tier. Promoting to the committed tier is a
deliberate human act (`git add`), never a side effect of a helper command —
run artifacts carry command output and paths, and that substrate is kept out of
git on purpose.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

LOCAL_ROOT = Path(".ravenclaude") / "runs"
COMMITTED_ROOTS = (
    Path("docs") / "plans",
    Path("docs") / "decisions",
    Path("docs") / "research",
)

# The standard files, and what each is FOR. Written as headers so a half-filled
# directory still tells the next CLI what was intended.
STANDARD_FILES: dict[str, str] = {
    "summary.md": "# Summary\n\n_What was done, for a human._\n",
    "decisions.md": "# Decisions\n\n_Each choice and WHY — the part that is expensive to recover._\n",
    "events.jsonl": "",
}


def find_project_root(start: Path) -> Path:
    """Walk up to the project root, rather than trusting the caller's cwd.

    Using cwd directly was wrong in both directions: `list` run from a
    subdirectory reported "No work directories yet" while 84 sat one level up,
    and `new` would have created a SECOND .ravenclaude/runs/ inside that
    subdirectory — fragmenting the one place the contract exists to point every
    CLI at. A storage contract with two storage locations is not a contract.

    A directory is the root if it holds `.ravenclaude/` or `.git/`. The walk is
    bounded by the filesystem root and falls back to `start`, so a project with
    neither marker behaves exactly as before.
    """
    cur = start.resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / ".ravenclaude").is_dir() or (candidate / ".git").exists():
            return candidate
    return start


def detect_host() -> str:
    """Name the CLI we are running under, from POSITIVE signals only.

    Ordered most-specific first. Returns "unknown" rather than guessing — an
    honest unknown is the repo's standing rule for host detection, and a wrong
    provenance stamp is worse than an absent one because it will be believed.
    """
    explicit = os.environ.get("THING_HOST") or os.environ.get("RC_HOST")
    if explicit:
        return explicit.strip().lower()
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude-code"
    if any(k.startswith("CODEX_") for k in os.environ):
        return "codex"
    if os.environ.get("COPILOT_HOME") or any(k.startswith("COPILOT_") for k in os.environ):
        return "copilot"
    if os.environ.get("CURSOR_TRACE_ID") or any(k.startswith("CURSOR_") for k in os.environ):
        return "cursor"
    if any(k.startswith("GEMINI_") for k in os.environ):
        return "gemini"
    return "unknown"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_meta(d: Path) -> dict:
    f = d / "meta.json"
    if not f.is_file():
        return {}
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def last_written(d: Path) -> float:
    """Newest mtime anywhere in the directory — the honest 'last touched'.

    The directory's own mtime only changes when an entry is added or removed, so
    it reports a directory as untouched after its files are edited.
    """
    newest = 0.0
    try:
        for p in d.rglob("*"):
            if p.is_file():
                newest = max(newest, p.stat().st_mtime)
    except OSError:
        pass
    try:
        newest = max(newest, d.stat().st_mtime)
    except OSError:
        pass
    return newest


def _is_run_dir(d: Path) -> bool:
    """A directory that IS a run, rather than a container of runs.

    Existing layouts nest — `.ravenclaude/runs/forge/<slug>/` and
    `runs/thing/<...>` are groupings, not single runs. Listing the grouping as
    one artifact would under-report by an order of magnitude and point the next
    CLI at the wrong directory, which defeats the purpose of the listing.
    """
    if (d / "meta.json").is_file():
        return True
    if any((d / name).is_file() for name in STANDARD_FILES):
        return True
    # No marker files, but it holds files directly -> treat it as a run.
    try:
        return any(p.is_file() for p in d.iterdir())
    except OSError:
        return False


def scan(root: Path, tier: str, base: Path, _depth: int = 0) -> list[dict]:
    out: list[dict] = []
    full = base / root
    if not full.is_dir():
        return out
    try:
        # NOT p.is_dir() alone: that follows symlinks, so a link under runs/ would
        # list a directory outside the project as though it were work in it. The
        # index exists to tell the next CLI where the work IS; pointing it out of
        # the repo is worse than omitting the entry.
        entries = sorted(p for p in full.iterdir() if p.is_dir() and not p.is_symlink())
    except OSError:
        return out
    for d in entries:
        # Descend ONE level into a pure container so nested layouts report their
        # real runs. Bounded at one level: deeper nesting is not a convention
        # anyone declared, and an unbounded walk would be a surprise on a big tree.
        if _depth == 0 and not _is_run_dir(d):
            nested = scan(d.relative_to(base), tier, base, _depth + 1)
            if nested:
                out += nested
                continue
        meta = read_meta(d)
        out.append(
            {
                "path": str(d.relative_to(base)),
                "tier": tier,
                "host": meta.get("host") or "unstamped",
                "task": meta.get("task") or d.name,
                "created": meta.get("created") or "",
                "mtime": last_written(d),
            }
        )
    return out


def cmd_list(base: Path, as_json: bool) -> int:
    rows = scan(LOCAL_ROOT, "local", base)
    for r in COMMITTED_ROOTS:
        rows += scan(r, "committed", base)
    rows.sort(key=lambda r: r["mtime"], reverse=True)

    if as_json:
        for r in rows:
            r.pop("mtime", None)
        print(json.dumps({"artifacts": rows}, indent=2))
        return 0

    if not rows:
        print("No work directories yet.")
        print("  create one with:  bin/rc artifacts new <task-id>")
        return 0

    print(f"{len(rows)} work director{'y' if len(rows) == 1 else 'ies'}, newest first:\n")
    for r in rows:
        when = (
            datetime.fromtimestamp(r["mtime"], tz=timezone.utc).strftime("%Y-%m-%d")
            if r["mtime"]
            else "?"
        )
        print(f"  [{r['tier']:9}] {r['path']}")
        print(f"              last written {when} by {r['host']}")
    print()
    print("  local     = .ravenclaude/runs/ — this machine only, gitignored")
    print("  committed = docs/ — travels to teammates via git")
    print("  'unstamped' means no meta.json; the writing CLI is genuinely unknown.")
    return 0


def cmd_new(base: Path, task: str) -> int:
    # Keep the id filesystem-safe and predictable across hosts.
    safe = "".join(c if (c.isalnum() or c in "-_.") else "-" for c in task).strip("-.")
    if not safe:
        print("  task id must contain at least one letter, digit, '-' or '_'", file=sys.stderr)
        return 1
    # Filesystems cap a path COMPONENT (255 bytes on ext4/APFS). Without this the
    # command died with a raw OSError traceback — an unhandled crash where a
    # one-line message belongs. Capped well below the limit so the files inside
    # (meta.json, summary.md) cannot push the full path over either.
    if len(safe) > 64:
        print(
            f"  task id is {len(safe)} characters — keep it under 64 so the "
            "directory name stays readable and portable",
            file=sys.stderr,
        )
        return 1

    d = base / LOCAL_ROOT / safe
    if d.exists():
        # Continuing an existing task is CORRECT per the contract — two
        # half-records is the failure it exists to prevent. Never clobber.
        meta = read_meta(d)
        print(
            f"  {d.relative_to(base)} already exists — continue in it, do not start a parallel one"
        )
        print(f"  created by: {meta.get('host', 'unstamped')}  on {meta.get('created', '?')}")
        return 0

    d.mkdir(parents=True, exist_ok=True)
    host = detect_host()
    meta = {
        "schema_version": 1,
        "task": safe,
        "host": host,
        "created": now_iso(),
        "contract": "AGENTS.md § Where work files go — the cross-CLI storage contract",
    }
    (d / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    for name, body in STANDARD_FILES.items():
        (d / name).write_text(body, encoding="utf-8")

    print(f"  created {d.relative_to(base)}  (stamped: {host})")
    for name in ["meta.json", *STANDARD_FILES]:
        print(f"    {name}")
    if host == "unknown":
        print("  NOTE: the CLI could not be identified from the environment, so this is")
        print("        stamped 'unknown' rather than guessed. Set RC_HOST to name it.")
    print("  This tier is gitignored — promote to docs/ by hand if it should be shared.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="rc artifacts")
    ap.add_argument("action", choices=["list", "new"])
    ap.add_argument("task", nargs="?")
    ap.add_argument("--json", action="store_true", help="machine-readable listing")
    ap.add_argument("--base", type=Path, default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()

    # An explicit --base is honoured verbatim (the gates pass a scratch dir);
    # otherwise resolve the project root rather than trusting cwd. Track
    # explicitness by default=None rather than comparing to Path.cwd(): the
    # equality test silently took the resolve-root branch when a caller passed
    # `--base "$PWD"` on purpose (e.g. to pin the base to a non-.git subdir).
    base = args.base.resolve() if args.base is not None else find_project_root(Path.cwd())
    if args.action == "list":
        return cmd_list(base, args.json)
    if not args.task:
        ap.error("`new` needs a task id, e.g. `bin/rc artifacts new my-task`")
    return cmd_new(base, args.task)


if __name__ == "__main__":
    sys.exit(main())
