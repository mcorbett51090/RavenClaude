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
  5. a bounded, fail-safe `git fetch --unshallow` of the base branch (⛔ NOT
     `--depth=1` — see the control note at this step's implementation. A
     depth-1 fetch creates a parentless commit that can never share history
     with a shallow HEAD, so `git merge-base` structurally cannot resolve
     against it; `--unshallow` converts the local repo to full history in one
     bounded fetch, which is what actually lets the two sides meet)
  6. give up -> return None, and the caller reports UNKNOWN

⛔ NONE IS STILL UNKNOWN, NEVER "UP TO DATE". Step 6 returning None must keep
failing the caller. The point of this module is to make the resolvable cases
resolve — never to invent a base so a check can report green without one.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

# ⛔ 60, not 20. `--unshallow` (below) fetches full history rather than one
# commit — measured at ~9s over a local `file://` remote for this repo's 1178
# commits; a real network fetch over HTTPS is slower and 20s cut it close for no
# reason, since a slow fetch just falls through to UNKNOWN (fail-safe either way).
FETCH_TIMEOUT = 60


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
    #
    # ⛔ `--unshallow`, NOT `--depth=1`. control 2026-08-26: reproduced the real CI
    # checkout shape (actions/checkout, fetch-depth 2, single-branch, so
    # `origin/main` never resolves — matches the module docstring's own
    # measurement). A `--depth=1` fetch of `main` creates a commit with NO parent
    # pointers, so `git merge-base HEAD FETCH_HEAD` fails (both sides are shallow
    # and share no walkable history) — the "no shared history — using the base
    # tip" branch below then fires and hands back whatever `main`'s tip happened
    # to be AT FETCH TIME. That is not the merge base; it is a moving target that
    # only matches a properly-stamped ratchet value by accident, so every
    # consumer of this fallback (check-ratchet-freshness.py,
    # check-inception-coverage.py, check-changed-concept-renders.py) fails on any
    # workflow_dispatch run once the checked-out branch is more than 0 commits
    # behind `main` — which is most of the time, not an edge case. `--unshallow`
    # converts the WHOLE local repo to full history in one bounded fetch (works
    # even though `origin`'s configured refspec is narrowed to the single
    # checked-out branch — verified this session: `origin/main` still never
    # appears as a ref, but `FETCH_HEAD` and `HEAD` now share real history, and
    # the resulting `git merge-base` matches the SHA a full local clone computes,
    # byte for byte). Errors harmlessly (exit 128, caught by `_git`'s try/except)
    # if the repo is already non-shallow when this line is reached — which the
    # earlier steps make rare, since a fully-cloned repo resolves `origin/main`
    # directly at step 2 and never reaches here.
    branch = ci_base or ("main" if requested.endswith("main") else "master")
    _git(root, "fetch", "--quiet", "--unshallow", "origin", branch, timeout=FETCH_TIMEOUT)
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
        # ⛔ ON THE BASE BRANCH ITSELF, merge-base(HEAD, origin/main) IS HEAD.
        # A push to main runs with HEAD == origin/main, so rule 2 resolves and the
        # "base" comes back as the commit under test. That is not a base at all — it
        # is the thing being compared — and the three consumers degrade in TWO
        # different directions from the one fault.
        #
        # control 2026-08-24, all three run in a checkout where HEAD, origin/main and
        # merge-base were the SAME sha (7025d056), true exit codes captured directly
        # rather than through a pipe:
        #   check-inception-coverage      -> exit 0, "artifacts added vs origin/main : 0"
        #   check-changed-concept-renders -> exit 0, "no concept changed in this diff"
        #   check-ratchet-freshness       -> exit 1
        # So two gates report clean having examined an empty diff, and the third can
        # never be green: a stamped SHA cannot equal the commit it was stamped before.
        # Corroborated in CI — main was red on "every ratchet value is bound to this PR
        # actual merge base" from #1002's merge onward, on BOTH Validate macOS and
        # Validate Marketplace, and no PR could fix it, because a PR cannot stamp a SHA
        # that does not exist until its own merge creates it.
        #
        # On the base branch the honest comparison point is the FIRST PARENT: "what did
        # this push change?". For a squash merge that is the previous tip — exactly the
        # SHA a well-formed PR stamped its ratchets against.
        #
        # ⛔ NOT reachable via `_is_merge_commit`: that needs >=2 parents and this repo
        # SQUASHES to one, so rule 4 never fires on a push to main.
        # ⛔ ONLY when the base resolved to a BRANCH REF. A caller that explicitly
        # asks for `HEAD` is requesting a deliberate self-comparison, not falling
        # into the push-to-main accident — check-ratchet-freshness's --must-fail
        # does exactly that in a single-commit scratch repo, and treating it as
        # the accident returned UNKNOWN and broke that gate's TEETH. The fault
        # this branch exists for is "the resolved branch ref happens to point at
        # HEAD because we are standing on that branch", which cannot be true of a
        # literal HEAD request.
        rc_head, head = _git(root, "rev-parse", "HEAD")
        _explicit_head = base in ("HEAD", "HEAD^1")
        if (not _NEUTER_BASE_TIP) and (not _explicit_head) and rc_head == 0 and head and sha == head:
            rc_parent, parent = _git(root, "rev-parse", "HEAD^1")
            if rc_parent == 0 and parent:
                return parent, how + " (HEAD is the base tip — first parent is the base)"
            # A root commit has no parent. Per this module's contract that is UNKNOWN,
            # never "up to date" — do not hand back HEAD to buy a green.
            return None, how + ", but HEAD is the base tip with no parent — UNKNOWN"
        return sha, how
    # Shallow clones can share no history with the base tip. The base ref itself is
    # still the correct comparison point — say so rather than reporting UNKNOWN.
    rc2, sha2 = _git(root, "rev-parse", f"{base}^{{commit}}")
    if rc2 == 0 and sha2:
        return sha2, how + " (no shared history — using the base tip)"
    return None, f"{how}, but no merge base could be computed"


# ── self-test ───────────────────────────────────────────────────────────────
# Set only by --must-fail: skip the base-tip branch so the OLD behaviour returns,
# and assert the fixtures catch it. This is the single planted defect.
_NEUTER_BASE_TIP = False


def _fixture(td, *, feature=False, root_only=False):
    """Build a scratch repo and return (root, expected_base_sha_or_None, label)."""
    import subprocess as sp

    r = Path(td)
    q = {"cwd": str(r), "capture_output": True, "text": True, "timeout": 60}
    sp.run(["git", "init", "-q", "-b", "main", str(r)], capture_output=True, timeout=60)
    sp.run(["git", "config", "user.email", "t@t"], **q)
    sp.run(["git", "config", "user.name", "t"], **q)

    def commit(name):
        (r / name).write_text(name, encoding="utf-8")
        sp.run(["git", "add", "-A"], **q)
        sp.run(["git", "commit", "-q", "-m", name], **q)
        return sp.run(["git", "rev-parse", "HEAD"], **q).stdout.strip()

    a = commit("a.txt")
    if root_only:
        # HEAD is the base tip AND has no parent -> UNKNOWN, never HEAD.
        sp.run(["git", "update-ref", "refs/remotes/origin/main", a], **q)
        return r, None, "root commit on the base tip -> UNKNOWN"
    b = commit("b.txt")
    if not feature:
        # The push-to-main shape: HEAD == origin/main. Base must be HEAD^1 (a).
        sp.run(["git", "update-ref", "refs/remotes/origin/main", b], **q)
        return r, a, "HEAD is the base tip -> first parent"
    # A real PR shape: two commits off the base, so HEAD^1 != merge-base.
    sp.run(["git", "update-ref", "refs/remotes/origin/main", b], **q)
    sp.run(["git", "checkout", "-q", "-b", "feat"], **q)
    commit("c.txt")
    commit("d.txt")
    return r, b, "feature branch -> the real merge base, NOT HEAD^1"


def _self_test():
    import tempfile

    ok = fail = 0
    cases = [{}, {"feature": True}, {"root_only": True}, {"root_only": True, "explicit_head": True}]
    for kw in cases:
        explicit = kw.pop("explicit_head", False)
        with tempfile.TemporaryDirectory() as td:
            root, want, label = _fixture(td, **kw)
            if explicit:
                # ⛔ REGRESSION PIN. An explicit `HEAD` request on a single-commit
                # repo must return HEAD, not UNKNOWN. Scoping the base-tip branch
                # to branch refs is what makes that true; without it this returns
                # None and check-ratchet-freshness's --must-fail loses its teeth.
                want = _git(root, "rev-parse", "HEAD")[1]
                label = "explicit HEAD request -> HEAD, never UNKNOWN"
            got, how = merge_base(root, "HEAD") if explicit else merge_base(root)
            if got == want:
                ok += 1
                print(f"  ok   {label}")
            else:
                fail += 1
                print(f"  FAIL {label}: want {want}, got {got} ({how})")
    print(f"  pass={ok} fail={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="_base_ref self-test")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    _a = ap.parse_args()

    if _a.must_fail_convention:
        # ⛔ 3, not 1: exit 1 is indistinguishable from a Python traceback, so a
        # crashing tool would masquerade as teeth that bit. Matches the sibling
        # ratchet/inventory checks in this initiative.
        print("must-fail-teeth-exit: 3")
        raise SystemExit(0)

    if _a.must_fail:
        _NEUTER_BASE_TIP = True
        rc = _self_test()
        if rc != 0:
            print("  teeth OK: with the base-tip branch neutered, the fixtures went red")
            raise SystemExit(3)
        print("  MUTANT NOT CAUGHT — the base-tip fixtures are inert", flush=True)
        raise SystemExit(1)

    raise SystemExit(_self_test())
