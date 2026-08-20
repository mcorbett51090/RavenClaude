"""_base_ref.py — resolve the PR base commit, in a CI checkout as well as locally.

⛔ WHY THIS EXISTS. Three checks in this initiative compare the working tree
against the PR base: the inception gate, the changed-concept render gate, and the
ratchet-freshness gate. All three asked `git merge-base HEAD origin/main` and, on
not resolving it, reported **UNKNOWN** and failed — which is the right instinct
locally and the wrong outcome in CI.

Measured 2026-08-20 by reproducing the CI checkout: `actions/checkout` fetches the
PR ref, and **`origin/main` is simply not present** —

    git rev-parse --verify origin/main  ->  fatal: Not a valid object name

So all three gates failed on every pull request, forever, for an environment
reason rather than a defect. ⛔ A gate that can never be green is a gate that gets
disabled, and a disabled gate protects nothing — which is exactly the failure this
whole initiative exists to close, reproduced in its own gates.

THE RESOLUTION ORDER, cheapest and most trustworthy first:

  1. the caller's explicit --base, when it resolves
  2. origin/main, origin/master (a normal local clone)
  3. origin/$GITHUB_BASE_REF, then $GITHUB_BASE_REF (CI names the PR base branch)
  4. ⛔ HEAD^1 when HEAD is a MERGE commit — on a pull_request event
     `actions/checkout` checks out the merge commit refs/pull/N/merge, whose FIRST
     parent IS the base. This is the one that actually works in CI, and it needs no
     network at all.
  5. a bounded, fail-safe `git fetch --depth=1` of the base branch
  6. give up -> return None, and the caller reports UNKNOWN

⛔ NONE IS STILL UNKNOWN, NEVER "UP TO DATE". Step 6 returning None must keep
failing the caller. The point of this module is to make the resolvable cases
resolve — never to invent a base so a check can report green without one.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

FETCH_TIMEOUT = 20


def _git(root: Path, *args: str, timeout: int = 60) -> tuple[int, str]:
    try:
        r = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return 127, ""
    return r.returncode, r.stdout.strip()


def _resolves(root: Path, ref: str) -> bool:
    return _git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")[0] == 0


def _is_merge_commit(root: Path) -> bool:
    rc, out = _git(root, "rev-list", "--parents", "-n", "1", "HEAD")
    return rc == 0 and len(out.split()) >= 3


def resolve_base(root: Path, requested: str = "origin/main") -> tuple[str | None, str]:
    """Return (base_commit_sha_or_ref, how) — `how` names which rule fired.

    The caller feeds the returned value to `git merge-base HEAD <base>`; on a
    merge-commit checkout the first parent IS the base, so it is returned directly.
    """
    if _resolves(root, requested):
        return requested, f"explicit base {requested}"

    for ref in ("origin/main", "origin/master"):
        if ref != requested and _resolves(root, ref):
            return ref, f"fallback {ref}"

    ci_base = os.environ.get("GITHUB_BASE_REF", "").strip()
    if ci_base:
        for ref in (f"origin/{ci_base}", ci_base):
            if _resolves(root, ref):
                return ref, f"GITHUB_BASE_REF -> {ref}"

    # ⛔ THE ONE THAT WORKS IN CI, and it is offline. On a pull_request event the
    # checked-out commit is the MERGE of head into base, so HEAD^1 is the base tip.
    if _is_merge_commit(root) and _resolves(root, "HEAD^1"):
        return "HEAD^1", "PR merge commit — first parent is the base"

    # Last resort: ask the network, bounded, and never let a failure propagate.
    branch = ci_base or ("main" if requested.endswith("main") else "master")
    _git(root, "fetch", "--quiet", "--depth=1", "origin", branch, timeout=FETCH_TIMEOUT)
    for ref in (f"origin/{branch}", "FETCH_HEAD"):
        if _resolves(root, ref):
            return ref, f"fetched {ref}"

    return None, "no base ref resolves — UNKNOWN, never up-to-date"


def merge_base(root: Path, requested: str = "origin/main") -> tuple[str | None, str]:
    """The commit to diff against, or (None, why)."""
    base, how = resolve_base(root, requested)
    if base is None:
        return None, how
    # A merge-commit first parent IS the base; asking merge-base for it is both
    # unnecessary and, in a shallow checkout with no shared history, impossible.
    if base == "HEAD^1":
        rc, sha = _git(root, "rev-parse", "HEAD^1")
        return (sha, how) if rc == 0 and sha else (None, "HEAD^1 did not resolve")
    rc, sha = _git(root, "merge-base", "HEAD", base)
    if rc == 0 and sha:
        return sha, how
    # Shallow clones can share no history with the base tip. The base ref itself is
    # still the correct comparison point — say so rather than reporting UNKNOWN.
    rc2, sha2 = _git(root, "rev-parse", f"{base}^{{commit}}")
    if rc2 == 0 and sha2:
        return sha2, how + " (no shared history — using the base tip)"
    return None, f"{how}, but no merge base could be computed"
