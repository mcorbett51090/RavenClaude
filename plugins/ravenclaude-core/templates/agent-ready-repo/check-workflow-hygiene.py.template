#!/usr/bin/env python3
# check-workflow-hygiene.py — scan .github/workflows/*.yml for GitHub Actions
# hygiene. Scaffolded by RavenClaude's /init-agent-ready (gold-standard GitHub
# protocol tier). stdlib-only (no PyYAML) — runs on any python3 with no install.
#
# Encodes the enforceable rules from RavenClaude's
# knowledge/github-actions-hardening.md:
#   Rule 1 — least-privilege: every workflow MUST carry a top-level `permissions:`
#            floor (deny-all `{}` or read-only), then elevate per-job.   [HARD]
#   Rule 2 — pin third-party actions to a full 40-hex commit SHA, not a mutable,
#            re-pointable tag. actions/* (official) and local ./ are exempt. [HARD]
#   Rule 3 — the default `GITHUB_TOKEN` downstream-suppression trap: a push /
#            PR-creation authenticated with the default token does NOT fire
#            downstream workflow runs, so an agent that then arms auto-merge waits
#            on a required check that never starts. Fix: a GitHub App / custom token
#            / OIDC. Heuristic (can't tell if a push MEANS to trigger).  [ADVISORY]
#   Rule 5 — a paths:/branches: filter on a pull_request trigger can leave a
#            would-be-required check Pending and block the PR forever. This file
#            cannot see the repo's required-checks list, so it can only ADVISE,
#            not fail.                                                     [ADVISORY]
#
# CONSUMER: verify each pinned SHA in your workflows is current for your adoption
# date; keep any would-be-required trigger path-filter-free.
#
# Exit 1 on any HARD finding; advisory findings print but do not fail the build.
from __future__ import annotations

import re
import sys
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"\buses:\s*([^\s#]+)")
TOPKEY_RE = re.compile(r"^([A-Za-z_][\w-]*):")
PR_RE = re.compile(r"^\s*pull_request:\s*$")
FILTER_RE = re.compile(r"^\s*(paths|paths-ignore|branches|branches-ignore):")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _block_children(lines: list[str], start: int) -> list[tuple[int, str]]:
    """Lines strictly more-indented than lines[start], up to the next sibling."""
    base = _indent(lines[start])
    out: list[tuple[int, str]] = []
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        if not ln.strip():
            continue
        if _indent(ln) <= base:
            break
        out.append((j, ln))
    return out


def check_workflow(path: Path) -> tuple[list[str], list[str]]:
    hard: list[str] = []
    advisory: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    # ── Rule 1: a top-level `permissions:` key must exist. ──
    top_keys = set()
    for ln in lines:
        if _indent(ln) == 0:
            m = TOPKEY_RE.match(ln)
            if m:
                top_keys.add(m.group(1))
    if "permissions" not in top_keys:
        hard.append(
            "no top-level `permissions:` — add `permissions: {}` (deny-all floor) "
            "or a read-only floor, then elevate per-job."
        )

    # ── Rule 2: every third-party `uses:` pinned to a 40-hex commit SHA. ──
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("#"):
            continue
        m = USES_RE.search(ln)
        if not m:
            continue
        ref = m.group(1)
        if ref.startswith("./"):
            continue  # local action — allowed
        name, _sep, gitref = ref.partition("@")
        if name.startswith("actions/"):
            continue  # official GitHub actions — allowed
        if not HEX40.match(gitref):
            hard.append(
                f"line {i}: third-party action `{ref}` is NOT pinned to a 40-hex "
                "commit SHA (a tag or branch is mutable and re-pointable). Resolve "
                "the tag to its SHA and keep the version in a trailing `# vX.Y.Z` "
                "comment."
            )

    # ── Rule 5 (advisory): a paths/branches filter on the pull_request trigger. ──
    on_idx = None
    for i, ln in enumerate(lines):
        if _indent(ln) == 0 and re.match(r"^on:", ln):
            on_idx = i
            break
    if on_idx is not None:
        for j, ln in _block_children(lines, on_idx):
            if PR_RE.match(ln):
                for _k, child in _block_children(lines, j):
                    if FILTER_RE.match(child):
                        advisory.append(
                            "a `paths:`/`branches:` filter on the `pull_request` "
                            "trigger — if this workflow ever becomes a REQUIRED "
                            "check, a filtered-out run stays Pending and blocks the "
                            "PR forever. Gate individual steps with `if:` instead."
                        )
                        break

    # ── Rule 3 (advisory, heuristic): the default-GITHUB_TOKEN downstream trap. ──
    # A push / PR-creation authenticated with the default GITHUB_TOKEN does not fire
    # downstream workflow runs. If an agent then arms auto-merge, the required check
    # never starts. This file can't tell whether the push is MEANT to trigger
    # downstream, so it only ADVISES — it NEVER adds a hard finding.
    noncomment = "\n".join(ln for ln in lines if not ln.lstrip().startswith("#"))
    push_signal = re.search(
        r"peter-evans/create-pull-request|stefanzweifel/git-auto-commit-action"
        r"|ad-m/github-push-action|\bgit\s+push\b",
        noncomment,
    )
    app_pat_signal = re.search(
        r"_PAT\b|APP_TOKEN|GH_APP_TOKEN|APP_PRIVATE_KEY"
        r"|create-github-app-token|github-app-token",
        noncomment,
    )
    if push_signal and not app_pat_signal:
        advisory.append(
            "a push / PR-creation step with no GitHub-App/PAT token in the file. If "
            "this push is meant to fire downstream workflows (e.g. an agent then arms "
            "auto-merge), the default `GITHUB_TOKEN` does NOT trigger them — "
            "authenticate as a GitHub App / custom token / OIDC instead. (Heuristic — "
            "ignore if the push need not trigger anything downstream.)"
        )
    return hard, advisory


def _self_test() -> int:
    """In-file fixtures proving each rule's verdict. The NEW Rule 3 is the must-pass
    invariant (fires ADVISORY, never HARD — RT-5); Rules 1/2/5 ride the same harness.
    Returns 0 iff every case matches its expected verdict."""
    import tempfile

    sha = "a" * 40
    cases = [
        (
            "rule1-bad-no-permissions",
            "name: x\non:\n  push:\njobs:\n  a:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - run: echo hi\n",
            lambda h, a: any("permissions" in m for m in h),
            "missing top-level permissions -> HARD",
        ),
        (
            "rule1-good",
            "name: x\non:\n  push:\npermissions: {}\njobs:\n  a:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - run: echo hi\n",
            lambda h, a: not h,
            "permissions floor present -> no hard",
        ),
        (
            "rule2-bad-unpinned",
            "name: x\non:\n  push:\npermissions: {}\njobs:\n  a:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - uses: trufflesecurity/trufflehog@v3\n",
            lambda h, a: any("40-hex" in m for m in h),
            "unpinned third-party uses -> HARD",
        ),
        (
            "rule2-good-pinned",
            f"name: x\non:\n  push:\npermissions: {{}}\njobs:\n  a:\n    runs-on: ubuntu-latest\n"
            f"    steps:\n      - uses: trufflesecurity/trufflehog@{sha}\n",
            lambda h, a: not h,
            "SHA-pinned third-party uses -> no hard",
        ),
        (
            "rule5-bad-paths-filter",
            "name: x\non:\n  pull_request:\n    paths:\n      - src/**\npermissions: {}\n"
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo hi\n",
            lambda h, a: not h and any("Pending" in m for m in a),
            "paths filter on pull_request -> ADVISORY, not hard",
        ),
        (
            "rule3-bad-push-no-apptoken",
            "name: x\non:\n  push:\npermissions:\n  contents: write\njobs:\n  a:\n"
            "    runs-on: ubuntu-latest\n    steps:\n      - run: git push origin HEAD\n",
            lambda h, a: not h and any("downstream" in m for m in a),
            "push + no App/PAT -> Rule 3 ADVISORY, NEVER hard (RT-5)",
        ),
        (
            "rule3-good-push-with-apptoken",
            f"name: x\non:\n  push:\npermissions:\n  contents: write\njobs:\n  a:\n"
            f"    runs-on: ubuntu-latest\n    steps:\n"
            f"      - uses: actions/create-github-app-token@{sha}\n"
            f"      - run: git push origin HEAD\n",
            lambda h, a: not any("downstream" in m for m in a),
            "push WITH an App token -> no Rule 3 advisory",
        ),
    ]
    rc = 0
    with tempfile.TemporaryDirectory() as d:
        for name, content, predicate, desc in cases:
            p = Path(d) / f"{name}.yml"
            p.write_text(content, encoding="utf-8")
            hard, advisory = check_workflow(p)
            ok = predicate(hard, advisory)
            print(f"  {'PASS' if ok else 'FAIL'}  {name}: {desc}")
            if not ok:
                print(f"        hard={hard}")
                print(f"        advisory={advisory}")
                rc = 1
    print("\nself-test: " + ("all cases passed." if rc == 0 else "FAILURES above."))
    return rc


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "--self-test":
        return _self_test()
    root = Path(argv[1]) if len(argv) > 1 else Path(".github/workflows")
    if not root.exists():
        print(f"OK no workflows directory at {root} — nothing to check.")
        return 0
    files = sorted(p for p in root.iterdir() if p.suffix in (".yml", ".yaml"))
    if not files:
        print(f"OK no workflow files under {root} — nothing to check.")
        return 0

    total_hard = 0
    for wf in files:
        hard, advisory = check_workflow(wf)
        for msg in hard:
            print(f"ERROR {wf}: {msg}")
        for msg in advisory:
            print(f"ADVISORY {wf}: {msg}")
        if not hard and not advisory:
            print(f"OK {wf}")
        total_hard += len(hard)

    if total_hard:
        print(f"\n{total_hard} hard finding(s) — see ERROR lines above.")
        return 1
    print("\nWorkflow hygiene: no hard findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
