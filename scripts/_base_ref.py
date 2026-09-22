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
  4. ⛔ HEAD^1 when HEAD is a MERGE commit, on a PUSH event only (not
     pull_request — see the 2026-09-02 correction below). This needs no network
     at all, and on a push to main it is unambiguous: HEAD^1 is "what was there
     immediately before this push."
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

⛔ CORRECTION, 2026-09-02 — rule 4's premise was FALSE for a pull_request event.
Step 4's original comment claimed "on a pull_request event the checked-out
commit is the MERGE of head into base, so HEAD^1 is the base tip" — i.e. that
`actions/checkout` fetches GitHub's synthetic `refs/pull/N/merge` ref. It does
NOT: this repo's `validate-marketplace.yml` (no `ref:` override) checks out the
PR's literal HEAD SHA — verified directly from a real run's job metadata
(`headSha` == the pushed branch tip, not a synthetic merge SHA).

So "HEAD is a merge commit" on a pull_request event means only that the PR
AUTHOR merged the base branch into their own feature branch — the exact,
repo-recommended way to refresh a stale or conflicting PR before merge. HEAD^1
is then that author's own PREVIOUS commit, not the base tip.

control (this session, PR #1070): a `git clone --depth 2 --single-branch` of a
real PR branch whose tip was `git merge origin/main` resolved `HEAD^1` to the
branch's own prior commit — reproduced directly (`git rev-list --parents -n 1
HEAD` showed 2 parents; `git rev-parse HEAD^1` returned the WRONG one), not
inferred. Every PR that self-heals a merge conflict this way — which this
repo's own runbooks and git-workflow rules actively recommend — hit this: the
ratchet/inception/changed-concept-render gates failed on that PR no matter how
correctly the ratchet was re-stamped immediately before push, because the
"base" they compared against was flatly wrong, not merely stale. Confirmed on
PR #1070: three separate re-stamp-and-push cycles all failed identically.

Rule 4 is now scoped to non-pull_request CI runs only (a genuine push event,
where the premise holds). A pull_request run with an unresolvable origin/main
falls through to the live-fetch fallback (step 5), which computes a real
merge-base against CURRENT origin/main regardless of what shape HEAD's own
history takes — the correct behavior for both a linear PR and one that
contains its own merge-from-base commit.

⛔ ADDENDUM, 2026-09-09 — CHERRY-PICKING YOUR OWN COMMITS ONTO A FRESH BRANCH
PERMANENTLY PINS THIS FUNCTION'S ANSWER, EVEN AFTER `--stamp` RE-RUNS.

This is a different failure from the two corrections above (both about what
CI's checkout looks like); this one is about how a CONTRIBUTOR updates a
branch. `git merge-base(HEAD, origin/main)` is a pure function of commit
ANCESTRY, not of when a file was last written or which SHA a caller intended.
Re-creating a branch by cherry-picking your own commits onto a fresh
`origin/main` (`git checkout origin/main -b feature-v2 && git cherry-pick
<shas>`) gives HEAD a NEW ancestry whose merge-base with `origin/main` is
whatever `origin/main` pointed to at that moment — permanently, regardless of
how many times `origin/main` advances afterward or how many times you re-fetch.
Every subsequent `check-ratchet-freshness.py --stamp` recomputes the SAME
stale answer, because the ancestry it is measuring never changed; only a real
`git merge origin/main` (or a rebase) on the EXISTING branch makes `origin/main`
a direct ancestor, which is what lets this function's answer move forward.

control (PR #1145, this repo, 2026-09-09): a branch was re-cut by cherry-pick
three times as `origin/main` advanced (`...v2`, `...v3` naming); each time,
`check-ratchet-freshness.py --check` failed against the FIRST fork point,
and `--stamp` "fixed" it only for that one fork point, not for main's actual
current tip. The failure stopped only once the branch was updated via a real
`git merge origin/main` instead of another cherry-pick-onto-fresh-branch cycle
— this repo's own established convention for catching up a stale branch (see
`scripts/artifact-budgets.seed.json`'s own append-log, which already uses the
phrase "Re-measured on rebased HEAD after merging origin/main" for exactly
this reason). Never obvious from the error message alone: `check-ratchet-
freshness.py` reports "measured against the wrong SHA," which reads like a
forgotten `--stamp`, not like "your branch's git ancestry cannot reach the
current base no matter what you stamp." If `--stamp` keeps producing an
answer that keeps failing `--check` immediately afterward, suspect this before
suspecting the stamp step itself.
"""

from __future__ import annotations

import os
import re
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
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return 127, ""
    return r.returncode, r.stdout.strip()


def _resolves(root: Path, ref: str) -> bool:
    return _git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")[0] == 0


def _is_merge_commit(root: Path) -> bool:
    rc, out = _git(root, "rev-list", "--parents", "-n", "1", "HEAD")
    return rc == 0 and len(out.split()) >= 3


_GITHUB_MERGE_REF_MSG_RE = re.compile(r"^Merge [0-9a-f]{40} into [0-9a-f]{40}\s*$")


def _is_github_synthetic_merge_ref(root: Path) -> bool:
    """True when HEAD is GitHub's own `refs/pull/N/merge` commit.

    ⛔ THE BUG THIS DETECTS, FOUND LIVE (PR #1098, 2026-09-08): this module's
    own docstring claims "on a pull_request event, `actions/checkout` here
    checks out the PR's literal head SHA" — verified true on 2026-08-20, and
    FALSE now. The real checkout log for `validate-marketplace.yml`'s
    "Validate Marketplace" job on a `pull_request` trigger:

        git fetch --no-tags --prune --no-recurse-submodules --depth=2 origin \
          +<sha>:refs/remotes/pull/<n>/merge
        git checkout --progress --force refs/remotes/pull/<n>/merge

    HEAD is GitHub's OWN synthetic 2-parent merge commit (parent 1 = the
    base branch tip AT THE MOMENT GITHUB LAST RECOMPUTED MERGEABILITY,
    parent 2 = the PR's real branch tip). Because rule 4 below is correctly
    scoped OFF for `pull_request` events (the 2026-09-02 correction, which
    protects against a PR AUTHOR's own `git merge origin/main` — a
    different 2-parent shape with the same parent count), every
    `pull_request` run fell through to the network fallback (step 5),
    which fetches CURRENT `origin/main` live and computes
    `merge-base(HEAD, origin/main)`. Since HEAD's own parent 1 already IS
    (approximately) current `origin/main`, that merge-base collapses to
    parent 1 ITSELF — a value that moves forward every time `main` advances
    and GitHub recomputes the ref, which is continuous on an active repo.
    No value stamped ahead of time can ever match a permanently moving
    target: this is the PR #991 / #1070 shape recurring under a THIRD guise.

    control (this session, PR #1098): `git cat-file -p` on the fetched
    `refs/pull/1098/merge` object showed exactly this — two parents
    (`a7cb75da...` = main's tip, `41b4ec6c...` = the real PR tip) and the
    commit message literally `"Merge 41b4ec6c... into a7cb75da..."`.

    THE FIX. GitHub's synthetic ref has a distinctive, auto-generated commit
    message (`"Merge <40-hex> into <40-hex>"`) that a human's own merge
    commit does not produce (git's own default merge-commit message reads
    `"Merge branch 'main'"` / `"Merge remote-tracking branch
    'origin/main'"`, never two bare 40-hex SHAs). Matching on that message
    — never on parent count alone, which is what caused the 2026-09-02
    false positive this rule must not repeat — lets `merge_base()` compute
    `merge-base(HEAD^1, HEAD^2)` DIRECTLY: the true, STABLE common ancestor
    of "the base tip as of ref-computation time" and "the PR's real tip",
    which does not move just because `main` advances further afterward.
    Needs no network call at all (an improvement over the fallback it
    replaces for this shape) and correctly generalizes to a PR author's own
    manual merge too (there, HEAD^1/HEAD^2 are the pre-merge tip and the
    merged-in main snapshot — the nested merge-base is still the right
    answer), but this function's match is deliberately narrow to the
    provably-GitHub-generated shape so it fires only where the fingerprint
    is certain.
    """
    if not _is_merge_commit(root):
        return False
    rc, msg = _git(root, "log", "-1", "--format=%B", "HEAD")
    return rc == 0 and bool(_GITHUB_MERGE_REF_MSG_RE.match(msg))


def resolve_base(
    root: Path, requested: str = "origin/main", force_fetch: bool = False
) -> tuple[str | None, str]:
    """Return (base_commit_sha_or_ref, how) — `how` names which rule fired.

    The caller feeds the returned value to `git merge-base HEAD <base>`; on a
    merge-commit checkout the first parent IS the base, so it is returned directly.

    `force_fetch` (default False, a two-way door — every existing caller is
    unaffected) closes CE-1 (critic-brief.md): on a contributor's laptop, step 1
    below almost always resolves `origin/main` immediately because it is
    RESOLVABLE-BUT-STALE, which is the exact false-green this parameter exists to
    close (`check-ratchet-freshness.py --check`, run standalone with no fetch, is a
    vacuous control on such a clone — it always "passes" against a base that is no
    longer the real merge base). When True, this refreshes the candidate branch
    with a plain (non-`--unshallow`) fetch BEFORE any resolution rule below runs.

    ⛔ ORDERING (R1 amendment, red-team.md R2): the synthetic-merge-ref check is
    network-free and MUST run before this function's own fetch — a force-fetch
    that ran first could make `origin/main` newly resolve inside a
    `refs/pull/N/merge` checkout where it previously didn't (see
    `_is_github_synthetic_merge_ref`'s docstring), short-circuiting resolution at
    the now-fresh `origin/main` step and skipping the synthetic-ref branch
    entirely — returning the wrong, moving-target answer that branch exists to
    avoid. So: check synthetic-ref FIRST, and only fetch if it did not fire.

    ⛔ PLAIN FETCH, NOT `--unshallow`, here (premise-control this session — see
    `.ravenclaude/runs/premise/` — `git fetch --unshallow origin <branch>` on an
    ALREADY-FULL repo fails outright, `fatal: --unshallow on a complete repository
    does not make sense`, exit 128, and updates nothing; using it here would
    silently skip the refresh on every normal, non-shallow contributor clone,
    which is the majority case this parameter exists to fix). A plain `git fetch
    origin <branch>` updates the ref on both a full clone and a shallow one; a
    shallow clone's separate graph-walk gap (the R1 shape) is `merge_base`'s
    problem to fix via its own bounded `--unshallow` retry below, not this
    fetch's.
    """
    if force_fetch:
        if _is_github_synthetic_merge_ref(root):
            return "MERGE_REF_PARENTS", "GitHub synthetic merge ref — nested parent merge-base"
        ci_base = os.environ.get("GITHUB_BASE_REF", "").strip()
        branch = ci_base or ("main" if requested.endswith("main") else "master")
        _git(root, "fetch", "--quiet", "origin", branch, timeout=FETCH_TIMEOUT)
        # Fall through to the resolution order below, unchanged — it now sees
        # whatever the fetch above just refreshed.

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

    # ⛔ GitHub's OWN synthetic `refs/pull/N/merge` checkout (found live, PR
    # #1098, 2026-09-08 — see `_is_github_synthetic_merge_ref`'s docstring for
    # the full incident). Fires on BOTH event types (the fingerprint is the
    # message, not the event name, and is safe either way), and deliberately
    # BEFORE the push-only rule 4 below so a real GitHub merge ref is never
    # misrouted into rule 4's plain-HEAD^1 shortcut. Needs no network call.
    if _is_github_synthetic_merge_ref(root):
        return "MERGE_REF_PARENTS", "GitHub synthetic merge ref — nested parent merge-base"

    # ⛔ PUSH EVENTS ONLY (see the 2026-09-02 correction in this module's
    # docstring) — on a pull_request run, `actions/checkout` here checks out
    # the PR's literal head SHA, so a merge-commit HEAD just means the PR
    # author merged the base branch into their own feature branch. HEAD^1 is
    # then that author's own prior commit, not the base tip; using it there
    # produces a confidently WRONG answer, not merely a stale one, and this
    # module's whole contract is "unresolvable is UNKNOWN, never invented."
    if os.environ.get("GITHUB_EVENT_NAME") != "pull_request":
        if _is_merge_commit(root) and _resolves(root, "HEAD^1"):
            return "HEAD^1", "push event merge commit — first parent is the base"

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


def merge_base(
    root: Path, requested: str = "origin/main", force_fetch: bool = False
) -> tuple[str | None, str]:
    """The commit to diff against, or (None, why).

    `force_fetch` (default False, a two-way door) is passed through to
    `resolve_base` AND additionally gates the R1 fix below: a force-fetch on
    `resolve_base` alone only refreshes WHICH commit a base ref points at — it
    does nothing about a graph-walk failure on a shallow/no-shared-history
    clone, so the "no shared history — using the base tip" branch further down
    would otherwise still hand back a fabricated base even though `force_fetch`
    promised a real one (red-team.md R1).
    """
    base, how = resolve_base(root, requested, force_fetch=force_fetch)
    if base is None:
        return None, how
    # A merge-commit first parent IS the base; asking merge-base for it is both
    # unnecessary and, in a shallow checkout with no shared history, impossible.
    if base == "HEAD^1":
        rc, sha = _git(root, "rev-parse", "HEAD^1")
        return (sha, how) if rc == 0 and sha else (None, "HEAD^1 did not resolve")
    # GitHub's synthetic merge ref: neither parent alone is "the base" (parent 1
    # is main's tip only as of ref-computation time, parent 2 is the PR's real
    # content) — the STABLE answer is where those two histories actually
    # diverge, which does not move just because `main` advances further later.
    if base == "MERGE_REF_PARENTS":
        rc1, p1 = _git(root, "rev-parse", "HEAD^1")
        rc2, p2 = _git(root, "rev-parse", "HEAD^2")
        if rc1 != 0 or not p1 or rc2 != 0 or not p2:
            return None, "MERGE_REF_PARENTS: a parent did not resolve"
        rc3, nested = _git(root, "merge-base", p1, p2)
        if rc3 == 0 and nested:
            return nested, how
        # The real CI checkout is `--depth=2` — the merge commit's own generation
        # plus its two direct parents, but NEITHER parent's own ancestry, so the
        # two sides structurally cannot share a walkable path yet. One bounded
        # `--unshallow` (same primitive the network fallback below already uses,
        # same FETCH_TIMEOUT) deepens whatever is already present rather than
        # fetching a second, redundant ref.
        _git(root, "fetch", "--quiet", "--unshallow", "origin", timeout=FETCH_TIMEOUT)
        rc4, nested2 = _git(root, "merge-base", p1, p2)
        if rc4 == 0 and nested2:
            return nested2, how + " (after --unshallow)"
        return None, how + ", but the parents share no merge base even after --unshallow"
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
        if (
            (not _NEUTER_BASE_TIP)
            and (not _explicit_head)
            and rc_head == 0
            and head
            and sha == head
        ):
            rc_parent, parent = _git(root, "rev-parse", "HEAD^1")
            if rc_parent == 0 and parent:
                return parent, how + " (HEAD is the base tip — first parent is the base)"
            # A root commit has no parent. Per this module's contract that is UNKNOWN,
            # never "up to date" — do not hand back HEAD to buy a green.
            return None, how + ", but HEAD is the base tip with no parent — UNKNOWN"
        return sha, how
    # ⛔ R1 (red-team.md): before falling back to the base-tip fabrication below,
    # force_fetch gets ONE real shot at a true merge base. Same bounded
    # `--unshallow` + retry already used for MERGE_REF_PARENTS above — premise-
    # controlled this session (`.ravenclaude/runs/premise/`) that a bare
    # `--unshallow` deepens the repo's WHOLE shallow boundary (shallow-ness is a
    # repo-wide `.git/shallow` record, not scoped to whichever named branch
    # originally triggered it), so it also recovers a separately shallow-fetched
    # base ref like `origin/main` without needing branch-specific logic here.
    if force_fetch:
        _git(root, "fetch", "--quiet", "--unshallow", "origin", timeout=FETCH_TIMEOUT)
        rc3, sha3 = _git(root, "merge-base", "HEAD", base)
        if rc3 == 0 and sha3:
            return sha3, how + " (after --unshallow retry)"
        return (
            None,
            how + ", but no merge base could be computed even after --unshallow"
            " — UNKNOWN, never the base tip",
        )
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


def _fixture_pr_merge_commit(td):
    """PR #1070 regression shape: a feature branch whose OWN tip is a merge of
    the (advanced) base branch into itself — the repo-recommended way to
    refresh a stale/conflicting PR — with `origin/main` deliberately left
    unresolvable as a ref (the real shallow single-branch CI checkout has no
    such ref; only `HEAD^1` as an object, reachable but structurally wrong).

    Returns (root, wrong_answer) where wrong_answer is what the pre-fix rule 4
    would confidently (and incorrectly) return: the feature branch's own prior
    commit, not the base tip.
    """
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

    commit("a.txt")
    sp.run(["git", "checkout", "-q", "-b", "feat"], **q)
    feat1 = commit("feat1.txt")
    sp.run(["git", "checkout", "-q", "main"], **q)
    commit("main2.txt")  # main advances past the feature branch's fork point
    sp.run(["git", "checkout", "-q", "feat"], **q)
    sp.run(["git", "merge", "-q", "--no-ff", "main"], **q)  # the author's own refresh
    # `origin/main` is deliberately never created here — that absence IS the
    # real shallow single-branch CI shape this fixture reproduces.
    return r, feat1


def _fixture_github_merge_ref(td):
    """GitHub's `refs/pull/N/merge` shape: a detached 2-parent commit whose
    message is GitHub's own auto-generated `"Merge <sha> into <sha>"` format —
    NOT a human's `git merge` default. See `_is_github_synthetic_merge_ref`'s
    docstring for the live incident this reproduces.

    Returns (root, base_tip_sha, pr_tip_sha, fork_point_sha) — fork_point is the
    only correct answer; both tips are wrong ones a naive rule could return.
    """
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

    fork_point = commit("a.txt")
    sp.run(["git", "checkout", "-q", "-b", "feat"], **q)
    pr_tip = commit("feat1.txt")
    sp.run(["git", "checkout", "-q", "main"], **q)
    base_tip = commit("main2.txt")  # main advances past the fork point
    # Build the merge commit exactly the way GitHub does: two parents, a
    # message naming both SHAs literally, no working-tree conflict resolution
    # needed since the two branches touch disjoint files.
    sp.run(["git", "checkout", "-q", "-b", "synthetic-merge", "main"], **q)
    msg = f"Merge {pr_tip} into {base_tip}"
    sp.run(["git", "merge", "-q", "--no-ff", "-m", msg, "feat"], **q)
    return r, base_tip, pr_tip, fork_point


def _fixture_shallow_no_shared_history(td):
    """R1 regression (red-team.md): a depth-one clone of a feature branch, plus
    a SEPARATE depth-one fetch of `main`, cannot walk to a shared ancestor — raw
    `git merge-base` fails outright, and the unforced `merge_base()` falls
    through to the existing "no shared history — using the base tip" branch
    (this is documented BACKWARD-COMPATIBLE legacy behaviour, not a defect to
    fix). `force_fetch=True` must instead recover the TRUE merge base via the
    bounded `--unshallow` retry, never the fabricated tip.

    Remote history: `a` (fork point) -> `b` -> `c` on `main`; branch `feature`
    from `a` with commit `f`. `work` is a `--depth 1 --single-branch feature`
    clone, with `main` separately shallow-fetched at depth 1 into
    `refs/remotes/origin/main` (pointing at `c`).

    Returns (work_root, base_tip_sha_c, fork_point_sha_a).
    """
    import subprocess as sp

    remote = Path(td) / "remote"
    work = Path(td) / "work"
    remote.mkdir()
    q = {"cwd": str(remote), "capture_output": True, "text": True, "timeout": 60}
    sp.run(["git", "init", "-q", "-b", "main", str(remote)], capture_output=True, timeout=60)
    sp.run(["git", "config", "user.email", "t@t"], **q)
    sp.run(["git", "config", "user.name", "t"], **q)

    def commit(name):
        (remote / name).write_text(name, encoding="utf-8")
        sp.run(["git", "add", "-A"], **q)
        sp.run(["git", "commit", "-q", "-m", name], **q)
        return sp.run(["git", "rev-parse", "HEAD"], **q).stdout.strip()

    a = commit("a.txt")
    sp.run(["git", "checkout", "-q", "-b", "feature"], **q)
    commit("f.txt")
    sp.run(["git", "checkout", "-q", "main"], **q)
    commit("b.txt")
    c = commit("c.txt")

    sp.run(
        [
            "git",
            "clone",
            "-q",
            "--branch",
            "feature",
            "--depth",
            "1",
            "--single-branch",
            f"file://{remote}",
            str(work),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    qw = {"cwd": str(work), "capture_output": True, "text": True, "timeout": 60}
    sp.run(["git", "config", "user.email", "t@t"], **qw)
    sp.run(["git", "config", "user.name", "t"], **qw)
    # The separate, manual depth-1 fetch of `main` — reproduces the CE-1/R1
    # shape where a base ref resolves but shares no walkable history with HEAD.
    sp.run(
        ["git", "fetch", "-q", "--depth", "1", "origin", "main:refs/remotes/origin/main"],
        **qw,
    )
    return work, c, a


def _fixture_disjoint_histories(td):
    """R1 negative control (red-team.md item 6): two genuinely orphan
    histories that share no common ancestor even after `--unshallow`.
    `merge_base(force_fetch=True)` must return `(None, ...)`, never a
    fabricated answer — this is what proves the force-fetch retry does not
    just always "succeed" by returning whatever it can reach.

    Returns root — HEAD is on the orphan `feature` branch; `origin/main` is
    pointed at `main`'s tip, a commit with no shared ancestor.
    """
    import subprocess as sp

    root = Path(td)
    q = {"cwd": str(root), "capture_output": True, "text": True, "timeout": 60}
    sp.run(["git", "init", "-q", "-b", "main", str(root)], capture_output=True, timeout=60)
    sp.run(["git", "config", "user.email", "t@t"], **q)
    sp.run(["git", "config", "user.name", "t"], **q)

    def commit(name):
        (root / name).write_text(name, encoding="utf-8")
        sp.run(["git", "add", "-A"], **q)
        sp.run(["git", "commit", "-q", "-m", name], **q)
        return sp.run(["git", "rev-parse", "HEAD"], **q).stdout.strip()

    commit("main.txt")
    main_sha = sp.run(["git", "rev-parse", "main"], **q).stdout.strip()
    sp.run(["git", "checkout", "-q", "--orphan", "feature"], **q)
    sp.run(["git", "rm", "-rq", "--cached", "."], **q)
    commit("feature.txt")
    sp.run(["git", "update-ref", "refs/remotes/origin/main", main_sha], **q)
    return root


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

    # PR #1070 regression: a pull_request run must never mistake the PR
    # author's own merge-from-base commit for the base tip.
    #
    # ⛔ BOTH GITHUB_EVENT_NAME AND GITHUB_BASE_REF are isolated here, not just
    # the one this fix reads. Caught live in this session's own CI run: the
    # fixture's scratch repo is `git init -b main` (its default branch is
    # literally named "main"), so under a REAL CI job's ambient
    # `GITHUB_BASE_REF=main`, rule 3 resolved the fixture's own local `main`
    # branch and returned the CORRECT answer — which then failed the original
    # `got is None` assertion, because that assertion implicitly assumed no
    # other rule could resolve inside this fixture. A self-test whose pass/fail
    # depends on what's ambiently set in the process running it is not a
    # self-test; isolating every env var this module reads is what makes the
    # fixture's outcome deterministic regardless of where `--self-test` runs.
    label = "PR merge-from-base HEAD on pull_request -> never HEAD^1 (rule 4 scoped off)"
    with tempfile.TemporaryDirectory() as td:
        root, wrong_answer = _fixture_pr_merge_commit(td)
        _prior_event = os.environ.get("GITHUB_EVENT_NAME")
        _prior_base = os.environ.get("GITHUB_BASE_REF")
        os.environ["GITHUB_EVENT_NAME"] = "pull_request"
        os.environ.pop("GITHUB_BASE_REF", None)
        try:
            got, how = merge_base(root)
        finally:
            if _prior_event is None:
                os.environ.pop("GITHUB_EVENT_NAME", None)
            else:
                os.environ["GITHUB_EVENT_NAME"] = _prior_event
            if _prior_base is not None:
                os.environ["GITHUB_BASE_REF"] = _prior_base
        if got is None and got != wrong_answer:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: got {got} ({how}) — want None, never {wrong_answer}")

    # GitHub's own `refs/pull/N/merge` shape (found live, PR #1098, 2026-09-08 —
    # see `_is_github_synthetic_merge_ref`'s docstring). Builds the exact fixture:
    # main advances past a feature branch's fork point, and a 2-parent commit
    # combines them carrying GitHub's OWN auto-generated message format
    # (`"Merge <40-hex> into <40-hex>"`) rather than a human's `git merge`
    # default. The correct answer is the TRUE common ancestor (the fork
    # point) — never either tip, and never None.
    #
    # ⛔ BOTH GITHUB_EVENT_NAME AND GITHUB_BASE_REF are isolated here, same
    # trap as the PR-merge-commit fixture above and caught the same way, live
    # in this session's own CI run: this fixture's scratch repo is ALSO
    # `git init -b main`, so a real CI job's ambient `GITHUB_BASE_REF=main`
    # made rule 3 resolve the fixture's own local `main` branch BEFORE this
    # module's new rule was ever reached — a different (and here, WRONG for
    # this fixture's intent) answer than the isolated-env test computed
    # locally. Popping it is what makes the fixture exercise the rule this
    # test exists to prove, regardless of where `--self-test` runs.
    with tempfile.TemporaryDirectory() as td:
        root, base_tip, pr_tip, fork_point = _fixture_github_merge_ref(td)
        _prior_event = os.environ.get("GITHUB_EVENT_NAME")
        _prior_base = os.environ.get("GITHUB_BASE_REF")
        os.environ["GITHUB_EVENT_NAME"] = "pull_request"
        os.environ.pop("GITHUB_BASE_REF", None)
        try:
            got, how = merge_base(root)
        finally:
            if _prior_event is None:
                os.environ.pop("GITHUB_EVENT_NAME", None)
            else:
                os.environ["GITHUB_EVENT_NAME"] = _prior_event
            if _prior_base is not None:
                os.environ["GITHUB_BASE_REF"] = _prior_base
        label = "GitHub synthetic merge ref -> the TRUE fork point, never either tip"
        if got == fork_point:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: want {fork_point}, got {got} ({how})")

        # R2 regression pin: the SAME fixture, but with force_fetch=True. The
        # ordering fix (synthetic-ref check before any fetch, in resolve_base)
        # must not have reopened the bug it was already carrying a fix for —
        # this must STILL return the fork point, not a tip a premature fetch
        # could have exposed.
        _prior_event = os.environ.get("GITHUB_EVENT_NAME")
        _prior_base = os.environ.get("GITHUB_BASE_REF")
        os.environ["GITHUB_EVENT_NAME"] = "pull_request"
        os.environ.pop("GITHUB_BASE_REF", None)
        try:
            got_ff, how_ff = merge_base(root, force_fetch=True)
        finally:
            if _prior_event is None:
                os.environ.pop("GITHUB_EVENT_NAME", None)
            else:
                os.environ["GITHUB_EVENT_NAME"] = _prior_event
            if _prior_base is not None:
                os.environ["GITHUB_BASE_REF"] = _prior_base
        label_ff = (
            "R2 regression: force_fetch=True on the synthetic merge ref -> still the fork point"
        )
        if got_ff == fork_point:
            ok += 1
            print(f"  ok   {label_ff}")
        else:
            fail += 1
            print(f"  FAIL {label_ff}: want {fork_point}, got {got_ff} ({how_ff})")

    # R1 (red-team.md): the depth-one shallow/no-shared-history regression.
    # Both directions matter equally here — the unforced call must keep
    # returning the LEGACY answer (proving no accidental behavior change for
    # every existing caller that never opts in), and the forced call must
    # return the TRUE merge base (the actual fix).
    with tempfile.TemporaryDirectory() as td:
        root, base_tip_c, fork_point_a = _fixture_shallow_no_shared_history(td)

        rc_raw, _ = _git(root, "merge-base", "HEAD", "origin/main")
        label = "R1 fixture control: raw `git merge-base HEAD origin/main` has no shared history"
        if rc_raw != 0:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(
                f"  FAIL {label}: raw merge-base unexpectedly succeeded — fixture is not testing what it claims"
            )

        got_unforced, how_unforced = merge_base(root)
        label = (
            "R1 backward-compat: force_fetch=False (default) still returns the base tip, unchanged"
        )
        if got_unforced == base_tip_c:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: want {base_tip_c}, got {got_unforced} ({how_unforced})")

        got_forced, how_forced = merge_base(root, force_fetch=True)
        label = "R1 fix: force_fetch=True recovers the TRUE merge base, not the fabricated tip"
        if got_forced == fork_point_a:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: want {fork_point_a}, got {got_forced} ({how_forced})")

    # R1 negative control: even force_fetch=True must never fabricate a base
    # when the histories are genuinely disjoint.
    with tempfile.TemporaryDirectory() as td:
        root = _fixture_disjoint_histories(td)
        got, how = merge_base(root, force_fetch=True)
        label = "R1 negative control: disjoint histories -> force_fetch=True still returns None, never a fabrication"
        if got is None:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: want None, got {got} ({how})")

    # Teeth: the SAME two-parent structure, but with a human-shaped message
    # (`git merge`'s own default) instead of GitHub's auto-generated one. The
    # detector must NOT fire here — proving the message match is load-bearing,
    # not a rule that fires on any 2-parent commit regardless of provenance
    # (which would silently readopt this fixture's own wrong-answer risk).
    with tempfile.TemporaryDirectory() as td:
        root, _wrong = _fixture_pr_merge_commit(td)
        label = "message fingerprint teeth: a human's own merge message does NOT fire the rule"
        if _is_github_synthetic_merge_ref(root):
            fail += 1
            print(f"  FAIL {label}: fired on a human-authored merge commit")
        else:
            ok += 1
            print(f"  ok   {label}")

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
