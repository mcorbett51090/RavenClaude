"""Shared helpers for the harness-atlas tools.

Every tool imports this module and calls ``assert_worktree()`` first, so a tool
started from the primary checkout (or from any other tree or branch) exits
non-zero instead of validating or writing the wrong tree (plan RT4).

Standard library only. All JSON the tools write goes through ``dump_json`` so
two runs on the same data produce byte-identical files.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

EXPECTED_BRANCH = "forge/coding-agent-harness-atlas"
WORKTREE_MARKER = ".claude/worktrees/forge-coding-agent-harness-atlas"
ATLAS_DIR = (
    Path(__file__).resolve().parents[1]
)  # .../docs/research/<date>-coding-agent-harness-atlas
DATA_DIR = ATLAS_DIR / "data"
TOOLS_DIR = ATLAS_DIR / "_tools"
SCHEMA_DIR = TOOLS_DIR / "schemas"

# Unit tests run in temporary trees and set this; it is never set in a real run.
_TEST_BYPASS_ENV = "ATLAS_TEST_ALLOW_ANY_TREE"


def _git(*args, cwd=None):
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    return out.returncode, out.stdout.strip()


def assert_worktree():
    """Exit 2 unless the cwd is the forge worktree on the forge branch.

    An empty branch name (detached HEAD) is a failure, not a pass.
    """
    if os.environ.get(_TEST_BYPASS_ENV) == "1" or os.environ.get("ATLAS_ANY_TREE") == "1":
        return  # ATLAS_ANY_TREE=1: render from a normal checkout once the branch has landed
    rc, top = _git("rev-parse", "--show-toplevel")
    if rc != 0 or not top:
        sys.exit("atlas: not inside a git work tree; refusing to run")
    rc, branch = _git("branch", "--show-current")
    if rc != 0 or not branch:
        sys.exit("atlas: empty branch name (detached HEAD?); refusing to run")
    if not top.endswith(WORKTREE_MARKER):
        sys.exit(f"atlas: cwd toplevel is {top}, not the forge worktree; refusing to run")
    if branch != EXPECTED_BRANCH:
        sys.exit(f"atlas: branch is {branch}, expected {EXPECTED_BRANCH}; refusing to run")
    tool_top = _git("rev-parse", "--show-toplevel", cwd=str(Path(__file__).resolve().parent))[1]
    if tool_top != top:
        sys.exit("atlas: the tool file and the cwd are in different trees; refusing to run")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path, obj):
    """Canonical JSON: sorted keys, 2-space indent, UTF-8 (no \\u escapes), LF, final newline."""
    text = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def run_dir(arg=None):
    """The run directory (primary checkout, gitignored). --run-dir wins, then ATLAS_RUN_DIR."""
    value = arg or os.environ.get("ATLAS_RUN_DIR")
    if not value:
        sys.exit("atlas: pass --run-dir or set ATLAS_RUN_DIR")
    path = Path(value)
    if not path.is_dir():
        sys.exit(f"atlas: run dir {path} does not exist")
    return path


class Ledger:
    """Append-only unit ledger (units.jsonl), the only run state (plan RT9).

    A unit is one dispatch or one script step: id, brief path, input hash,
    status, receipt path, attempt. ``latest`` folds the log so the newest
    record per unit id wins; a unit whose output exists with a matching input
    hash is skipped on re-run.
    """

    def __init__(self, run_directory):
        self.path = Path(run_directory) / "units.jsonl"

    def append(self, unit_id, **fields):
        record = {"unit": unit_id, **fields}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")

    def latest(self):
        state = {}
        if not self.path.exists():
            return state
        with open(self.path, encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if raw:
                    rec = json.loads(raw)
                    state[rec["unit"]] = rec
        return state

    def is_done(self, unit_id, input_hash):
        rec = self.latest().get(unit_id)
        return bool(rec and rec.get("status") == "done" and rec.get("input_hash") == input_hash)
