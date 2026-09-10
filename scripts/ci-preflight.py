#!/usr/bin/env python3
"""ci-preflight.py — a read-only preflight coordinator for the recurring CI
failure classes identified in this repo's own CI-failure sample (ratchet/
merge-base binding, inventory staleness/schema, dashboard/index/concepts-doc
freshness, Copilot package freshness, Codex-agents projection, inventory
census/sweep/inception).

It shells the exact same standalone `--check` commands `scripts/audit-gates.sh`
itself runs for these gates — unconditionally, every invocation, with no
glob-based selection — so a contributor gets, in one command before `git push`,
the same verdict CI will compute for these specific classes.

⛔ NARROWED CLAIM (this sentence is repeated verbatim in three places — this
docstring/--help, the run banner below, and AGENTS.md — never reword it away):

    This reproduces production freshness/lint/ratchet diagnostics only — not
    audit-harness or must-fail-fixture integrity. `scripts/audit-gates.sh`
    remains the required pre-PR check.

Specifically excluded: the `rc_mustfail` teeth-verification halves
`audit-gates.sh` runs alongside each `--check` (they verify the CHECKER's own
detection logic against a planted mutant, not the repo's current state — only
the full `scripts/audit-gates.sh` run exercises them).

Strictly read-only in v1 — no --fix / --force / --stamp / generator write mode.
Every failing class names the exact, already-documented remediation command
owned by that checker; this tool never runs it.

Exit codes (three-tier, not binary):
    0   every selected check ran and passed.
    1   at least one class is UNAVAILABLE (soft-skip — missing tool, network-
        blocked, unresolvable base even after the force-fetch pre-warm, or a
        bounded timeout) but nothing that actually ran reported a failure.
        A soft-skip is NOT a pass — read the UNAVAILABLE rows before trusting
        exit 0 would have followed.
    2   at least one class that ran reported a real failure; or the tree
        changed mid-run (content-fingerprint mismatch — rerun); or --strict
        was passed and any soft-skip occurred; or --base was not a
        syntactically valid ref.

Usage:
    ci-preflight.py [--base origin/main] [--strict]
    ci-preflight.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base_ref import merge_base as _resolve_merge_base  # noqa: E402

PASS = "PASS"
FAIL = "FAIL"
UNAVAILABLE = "UNAVAILABLE"

NARROWED_CLAIM = (
    "This reproduces production freshness/lint/ratchet diagnostics only — not "
    "audit-harness or must-fail-fixture integrity. `scripts/audit-gates.sh` "
    "remains the required pre-PR check."
)

# §3.8's timeout budget — a G6 engineering default, not an architecture call.
T_FLOOR = 60
T_HOTSPOT = 60
T_SWEEP = 180  # measured ~76s on a clean checkout; >2x headroom.


@dataclass
class CheckResult:
    name: str
    verdict: str
    detail: str = ""
    remediation: str = ""
    elapsed_s: float = 0.0


@dataclass
class BoundedRun:
    returncode: int | None
    stdout: str
    stderr: str
    elapsed_s: float
    timed_out: bool
    start_error: str = ""


# ── the bounded-subprocess + process-group-kill primitive (§3.8) ───────────
#
# Every child is started in its OWN process group (`start_new_session=True`).
# On timeout, the coordinator kills the WHOLE group, not just the direct
# child — a hung `npx` download or `git fetch` can leave grandchildren that
# survive a plain `proc.kill()`. This is the one primitive every floor and
# hotspot check is built on; nothing here calls `subprocess.run(..., timeout=
# ...)` directly, because that primitive lets an orphaned grandchild keep
# running after the timeout fires.
def run_bounded(cmd: list[str], cwd: Path, timeout: int, env: dict | None = None) -> BoundedRun:
    start = time.monotonic()
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            env=env,
        )
    except OSError as e:
        return BoundedRun(None, "", "", time.monotonic() - start, False, start_error=str(e))

    try:
        out, err = proc.communicate(timeout=timeout)
        return BoundedRun(
            proc.returncode,
            out.decode("utf-8", "replace"),
            err.decode("utf-8", "replace"),
            time.monotonic() - start,
            False,
        )
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            out, err = proc.communicate(timeout=5)
        except Exception:
            out, err = b"", b""
        return BoundedRun(
            None,
            out.decode("utf-8", "replace") if out else "",
            err.decode("utf-8", "replace") if err else "",
            time.monotonic() - start,
            True,
        )


def _as_check_result(name: str, run: BoundedRun, remediation: str, timeout: int) -> CheckResult:
    if run.timed_out:
        return CheckResult(
            name, UNAVAILABLE, f"timed out after {timeout}s", remediation, run.elapsed_s
        )
    if run.returncode is None:
        return CheckResult(
            name,
            UNAVAILABLE,
            f"could not start ({run.start_error or run.stderr.strip()[:200] or 'unknown'})",
            remediation,
            run.elapsed_s,
        )
    if run.returncode == 0:
        return CheckResult(name, PASS, "", "", run.elapsed_s)
    detail = (run.stdout + run.stderr).strip()[-2000:]
    return CheckResult(name, FAIL, detail, remediation, run.elapsed_s)


def _repo_root() -> Path:
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10
    )
    if r.returncode != 0:
        raise SystemExit("ci-preflight.py must run inside a git checkout")
    return Path(r.stdout.strip())


# ── floor checks (§5 P0) — always on, every invocation ──────────────────────


def _default_json_targets(root: Path) -> list[Path]:
    targets = [root / ".claude-plugin" / "marketplace.json", root / ".repo-layout.json"]
    targets += sorted((root / "plugins").glob("*/.claude-plugin/plugin.json"))
    return targets


def check_json_validity(root: Path, paths: list[Path] | None = None) -> CheckResult:
    start = time.monotonic()
    targets = paths if paths is not None else _default_json_targets(root)
    bad = []
    for p in targets:
        p = Path(p)
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except FileNotFoundError:
            bad.append(f"{p}: missing")
        except json.JSONDecodeError as e:
            bad.append(f"{p}: {e}")
    elapsed = time.monotonic() - start
    if bad:
        return CheckResult(
            "floor:json-validity",
            FAIL,
            "; ".join(bad),
            "fix the JSON syntax in the named file(s)",
            elapsed,
        )
    return CheckResult("floor:json-validity", PASS, f"{len(targets)} file(s) parse", "", elapsed)


def _default_shell_syntax_targets(root: Path) -> list[Path]:
    """AGENTS.md step 2's `bash -n` scope: both hooks AND plain scripts."""
    targets = sorted((root / "plugins").glob("*/hooks/*.sh"))
    targets += sorted((root / "scripts").glob("*.sh"))
    return targets


def _default_shell_exec_targets(root: Path) -> list[Path]:
    """AGENTS.md step 2's `-x` loop scope: `plugins/*/hooks/*.sh` ONLY — not
    `scripts/*.sh`. Confirmed by reading AGENTS.md directly: hooks are exec'd
    by path (Claude Code invokes them directly, so a missing +x bit is a real
    defect), while everything under `scripts/**` is invoked as `bash
    scripts/foo.sh` from audit-gates.sh / workflows / AGENTS.md itself, where
    the +x bit is irrelevant to whether the script runs. Checking it on
    `scripts/*.sh` too would redden a clean tree on files this repo's own
    convention never required to be executable — the false-positive risk
    Ruling 1's "small, unconditional set" spirit exists to avoid.
    """
    return sorted((root / "plugins").glob("*/hooks/*.sh"))


def check_shell_syntax_and_exec(
    root: Path,
    syntax_paths: list[Path] | None = None,
    exec_paths: list[Path] | None = None,
    timeout: int = T_FLOOR,
) -> CheckResult:
    start = time.monotonic()
    syntax_targets = (
        syntax_paths if syntax_paths is not None else _default_shell_syntax_targets(root)
    )
    exec_targets = exec_paths if exec_paths is not None else _default_shell_exec_targets(root)
    bad = []
    for p in syntax_targets:
        p = Path(p)
        run = run_bounded(["bash", "-n", str(p)], root, timeout)
        if run.timed_out:
            bad.append(f"{p}: bash -n timed out after {timeout}s")
            continue
        if run.returncode is None or run.returncode != 0:
            msg = (run.stderr or run.stdout).strip()[:200]
            bad.append(f"{p}: syntax error ({msg})")
    for p in exec_targets:
        p = Path(p)
        if not os.access(p, os.X_OK):
            bad.append(f"{p}: not executable")
    elapsed = time.monotonic() - start
    n = len(set(syntax_targets) | set(exec_targets))
    if bad:
        return CheckResult(
            "floor:shell-syntax-exec",
            FAIL,
            "; ".join(bad),
            "fix the syntax and/or `chmod +x` the named file(s)",
            elapsed,
        )
    return CheckResult("floor:shell-syntax-exec", PASS, f"{n} file(s) OK", "", elapsed)


def check_prettier(root: Path, timeout: int = T_FLOOR, env: dict | None = None) -> CheckResult:
    run = run_bounded(
        ["npx", "--yes", "prettier@3.9.4", "--check", ".", "--log-level", "warn"],
        root,
        timeout,
        env=env,
    )
    return _as_check_result("floor:prettier", run, "npx --yes prettier@3.9.4 --write .", timeout)


def check_ruff(root: Path, timeout: int = T_FLOOR, env: dict | None = None) -> CheckResult:
    run = run_bounded(["ruff", "check", "."], root, timeout, env=env)
    return _as_check_result("floor:ruff", run, "ruff check --fix .", timeout)


def run_floor(root: Path) -> list[CheckResult]:
    return [
        check_json_validity(root),
        check_shell_syntax_and_exec(root),
        check_prettier(root),
        check_ruff(root),
    ]


# ── the narrowed diff/rename/untracked resolution (§3.1 constraint 5) ──────
#
# Retained for exactly two purposes, per Ruling 1's consequence text — NEVER to
# decide which hotspot class runs (that set is unconditional, §3.1):
#   (a) an informational "what changed" report/context section;
#   (b) a fail-closed UNSTAGED-SENSITIVE-PATH check: an untracked or renamed
#       path under one of these roots would be invisible to a `git ls-files`-
#       based hotspot check (census, some inventory checks) unless it is
#       staged first.
SENSITIVE_ROOTS = ("scripts/", "plugins/", ".claude-plugin/", "tests/fixtures/")
SENSITIVE_FILES = (
    ".github/workflows/validate-marketplace.yml",
    ".github/workflows/validate-layout.yml",
    ".github/workflows/validate-schemas.yml",
)


def _is_sensitive(relpath: str) -> bool:
    if relpath in SENSITIVE_FILES:
        return True
    return any(relpath.startswith(root) for root in SENSITIVE_ROOTS)


def _split_nul(text: str) -> list[str]:
    """Split NUL-delimited git output (`-z`) into tokens, dropping the trailing
    empty token every NUL-terminated stream leaves behind.

    Empirically verified this session (scratch `mktemp -d` repos, since a
    positive control matters more here than trusting the git docs alone):
    `git status --porcelain=v1 -z --untracked-files=all --no-renames` emits
    each entry as ONE NUL-terminated `"XY path"` token — no `old\\0new\\0`
    pairing, even for a staged rename (`A  new` + `D  old`, two ordinary
    tokens). `run_bounded`'s `BoundedRun` already decodes subprocess bytes via
    `utf-8/replace`; NUL (0x00) round-trips through UTF-8 as a single valid
    codepoint, so splitting the already-decoded str on "\\x00" here is exact
    for every path this repo's sensitive roots actually contain (plain ASCII
    filenames) — it is not exact for arbitrary non-UTF-8 bytes, which
    `run_bounded`'s "replace" policy already lossily maps to U+FFFD upstream
    of this function.
    """
    parts = text.split("\x00")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return parts


def _git_status_entries(root: Path, timeout: int = T_FLOOR) -> list[tuple[str, str]]:
    """[(XY, path), ...] via `git status --porcelain=v1 -z --untracked-files=all
    --no-renames`. `--no-renames` is deliberate: verified this session that an
    UNSTAGED rename's new path then shows as an ordinary `??` token (old path
    shows ` D`) — identical in kind to any brand-new untracked file. That is
    what lets the untracked-under-a-sensitive-root check below reduce to a
    single `??` scan with no separate rename-pairing logic.
    """
    run = run_bounded(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames"],
        root,
        timeout,
    )
    if run.returncode != 0:
        return []
    out = []
    for tok in _split_nul(run.stdout):
        if len(tok) < 4:
            continue
        out.append((tok[:2], tok[3:]))
    return out


def _git_diff_entries(root: Path, timeout: int = T_FLOOR) -> list[tuple[str, str]]:
    """[(status_letter, path), ...] via `git diff --no-renames -z --name-status
    HEAD`. Verified this session: unlike `git status -z`, this emits status and
    path as two SEPARATE NUL-terminated tokens per entry (alternating), not one
    combined token — hence the `zip(evens, odds)` pairing rather than a fixed
    slice offset.
    """
    run = run_bounded(["git", "diff", "--no-renames", "-z", "--name-status", "HEAD"], root, timeout)
    if run.returncode != 0:
        return []
    toks = _split_nul(run.stdout)
    return list(zip(toks[0::2], toks[1::2]))


def build_report(root: Path, timeout: int = T_FLOOR) -> dict:
    """The informational 'what changed' report/context section (§3.1 constraint
    5a) — never consulted to decide which hotspot class runs."""
    return {
        "status": _git_status_entries(root, timeout),
        "diff_vs_head": _git_diff_entries(root, timeout),
    }


def check_unstaged_sensitive_paths(root: Path, timeout: int = T_FLOOR) -> CheckResult:
    start = time.monotonic()
    entries = _git_status_entries(root, timeout)
    bad = sorted(path for xy, path in entries if xy == "??" and _is_sensitive(path))
    elapsed = time.monotonic() - start
    if bad:
        return CheckResult(
            "context:unstaged-sensitive-path",
            FAIL,
            "; ".join(bad),
            "stage or commit the listed path(s), then rerun",
            elapsed,
        )
    return CheckResult("context:unstaged-sensitive-path", PASS, "", "", elapsed)


# ── the unconditional hotspot check set (§3.1) — 6 classes, 13 commands,  ──
# ── every one run every invocation, no glob-based selection (Ruling 1)     ──


def _script_exists(root: Path, argv: list[str]) -> bool:
    """Every HOTSPOTS entry and `check_class1_ratchet`'s own subprocess call
    share one convention: argv[0] is the interpreter (`python3` or `bash`),
    argv[1] is the checker script's repo-relative path. Without this guard, a
    missing/renamed checker still lets the INTERPRETER start successfully and
    exit nonzero on its own ("can't open file ...") — `_as_check_result` would
    then misclassify that as a real FAIL, not the UNAVAILABLE that a checker
    genuinely absent from disk must report (P2's explicit DoD: never silently
    PASS, never a crash, and never mistaken for a real failure either)."""
    if len(argv) < 2:
        return True  # nothing to check; let it run and surface whatever happens
    return (root / argv[1]).is_file()


def check_class1_ratchet(root: Path, base: str, timeout: int = T_HOTSPOT) -> CheckResult:
    """Class 1 — the #1 recurring failure. Pre-warms via P1's
    `merge_base(force_fetch=True)` for its fetch/unshallow SIDE EFFECT on the
    on-disk git state (§3.2 "how the coordinator uses this") before shelling
    the standalone `--check` command; the subprocess's own unforced internal
    resolution then finds the just-refreshed ref directly. `None` -> report
    UNAVAILABLE without even invoking the subprocess (an unforced subprocess
    call would only produce an ambiguous generic exit 1 here, indistinguishable
    from a real content mismatch)."""
    start = time.monotonic()
    sha, how = _resolve_merge_base(root, base, force_fetch=True)
    if sha is None:
        elapsed = time.monotonic() - start
        return CheckResult(
            "hotspot:1-ratchet-merge-base",
            UNAVAILABLE,
            f"no base ref resolves even after force-fetch pre-warm ({how})",
            "resolve network access to origin, or pass --base explicitly",
            elapsed,
        )
    argv = ["python3", "scripts/check-ratchet-freshness.py", "--check", "--base", base]
    if not _script_exists(root, argv):
        elapsed = time.monotonic() - start
        return CheckResult(
            "hotspot:1-ratchet-merge-base",
            UNAVAILABLE,
            f"checker script missing on disk: {argv[1]}",
            "restore scripts/check-ratchet-freshness.py",
            elapsed,
        )
    run = run_bounded(argv, root, timeout)
    result = _as_check_result(
        "hotspot:1-ratchet-merge-base",
        run,
        "python3 scripts/check-ratchet-freshness.py --stamp",
        timeout,
    )
    result.elapsed_s = time.monotonic() - start
    return result


# name, argv, remediation, timeout — §3.1's table, classes 2-6 (12 commands;
# class 1 above is the 13th and is handled specially, not via this registry).
HOTSPOTS: list[tuple[str, list[str], str, int]] = [
    (
        "hotspot:2a-gate237-inventory-staleness",
        ["bash", "plugins/ravenclaude-core/hooks/tests/test-gate237-inventory-staleness.sh"],
        "investigate: bash plugins/ravenclaude-core/hooks/tests/"
        "test-gate237-inventory-staleness.sh",
        T_HOTSPOT,
    ),
    (
        "hotspot:2b-covers-completeness",
        ["python3", "scripts/check-covers-completeness.py", "--check"],
        "add the missing path to the entry's covers[], or record why it is "
        "exempt in covers_exempt[]",
        T_HOTSPOT,
    ),
    (
        "hotspot:2c-gate239-inventory-schema",
        ["bash", "plugins/ravenclaude-core/hooks/tests/test-gate239-inventory-schema.sh"],
        "investigate: bash plugins/ravenclaude-core/hooks/tests/test-gate239-inventory-schema.sh",
        T_HOTSPOT,
    ),
    (
        "hotspot:2d-inventory-evidence",
        ["python3", "scripts/check-inventory-evidence.py", "--check"],
        "investigate: python3 scripts/check-inventory-evidence.py --check",
        T_HOTSPOT,
    ),
    (
        "hotspot:3a-dashboard-freshness",
        [
            "python3",
            "scripts/check-artifact-freshness.py",
            "--check",
            "--surface",
            "plugins/ravenclaude-core/dashboard.html",
        ],
        "python3 scripts/generate-dashboards.py",
        T_HOTSPOT,
    ),
    (
        "hotspot:3b-index-freshness",
        ["python3", "scripts/check-artifact-freshness.py", "--check", "--surface", "index.html"],
        "python3 scripts/generate-index-dashboard.py",
        T_HOTSPOT,
    ),
    (
        "hotspot:3c-concepts-doc-freshness",
        ["python3", "scripts/generate-concepts-doc.py", "--check"],
        "python3 scripts/generate-concepts-doc.py",
        T_HOTSPOT,
    ),
    (
        "hotspot:4-copilot-package-freshness",
        ["python3", "scripts/generate-copilot-plugin.py", "--check"],
        "python3 scripts/generate-copilot-plugin.py",
        T_HOTSPOT,
    ),
    (
        "hotspot:5-codex-agents-projection",
        ["python3", "scripts/generate-codex-agents.py", "--check"],
        "python3 scripts/generate-codex-agents.py",
        T_HOTSPOT,
    ),
    (
        "hotspot:6a-inventory-census",
        ["python3", "scripts/inventory-census.py", "--check"],
        "investigate: python3 scripts/inventory-census.py --explain",
        T_HOTSPOT,
    ),
    (
        "hotspot:6b-inventory-sweep",
        ["python3", "scripts/inventory-sweep.py", "--check", "--no-record"],
        "investigate: python3 scripts/inventory-sweep.py --check",
        T_SWEEP,
    ),
    (
        "hotspot:6c-inception-coverage",
        ["python3", "scripts/check-inception-coverage.py", "--check"],
        "add the newly-added artifact to an inventory entry's covers[]",
        T_HOTSPOT,
    ),
]


def _run_one_hotspot(
    root: Path, name: str, argv: list[str], remediation: str, timeout: int
) -> CheckResult:
    """The per-entry body of the `HOTSPOTS` loop, factored out so the
    missing-checker guard can be exercised hermetically (no network, no real
    repo) in `_self_test()` — see the "missing checker" self-test cases."""
    if not _script_exists(root, argv):
        return CheckResult(
            name,
            UNAVAILABLE,
            f"checker script missing on disk: {argv[1]}",
            remediation,
            0.0,
        )
    run = run_bounded(argv, root, timeout)
    return _as_check_result(name, run, remediation, timeout)


def run_hotspots(root: Path, base: str) -> list[CheckResult]:
    results = [check_class1_ratchet(root, base)]
    for name, argv, remediation, timeout in HOTSPOTS:
        results.append(_run_one_hotspot(root, name, argv, remediation, timeout))
    return results


# ── the three-tier exit contract (§3.7) ─────────────────────────────────────


def aggregate(results: list[CheckResult], strict: bool) -> int:
    if any(r.verdict == FAIL for r in results):
        return 2
    if any(r.verdict == UNAVAILABLE for r in results):
        return 2 if strict else 1
    return 0


def _valid_ref_syntax(ref: str, timeout: int = 10) -> bool:
    r = subprocess.run(
        ["git", "check-ref-format", "--allow-onelevel", ref], capture_output=True, timeout=timeout
    )
    return r.returncode == 0


# ── printing ─────────────────────────────────────────────────────────────


def print_banner() -> None:
    print("── ci-preflight (read-only; NOT a substitute for `scripts/audit-gates.sh`) ──")
    print(f"  {NARROWED_CLAIM}")
    print()


def print_results(title: str, results: list[CheckResult]) -> None:
    print(f"── {title} ──")
    for r in results:
        print(f"  {r.verdict:<11} {r.name:<32} ({r.elapsed_s:.2f}s)")
        if r.detail:
            for line in r.detail.splitlines()[:20]:
                print(f"      {line}")
        if r.verdict != PASS and r.remediation:
            print(f"      remediation: {r.remediation}")
    print()


def print_report(report: dict) -> None:
    status = report["status"]
    diff = report["diff_vs_head"]
    print("── report/context (informational — never gates a decision) ──")
    print(f"  git status entries : {len(status)}")
    for xy, path in status[:20]:
        print(f"    {xy}  {path}")
    if len(status) > 20:
        print(f"    … {len(status) - 20} more")
    print(f"  diff vs HEAD       : {len(diff)} path(s)")
    for st, path in diff[:20]:
        print(f"    {st}  {path}")
    if len(diff) > 20:
        print(f"    … {len(diff) - 20} more")
    print()


def print_verdict(results: list[CheckResult], rc: int) -> None:
    n_fail = sum(1 for r in results if r.verdict == FAIL)
    n_unavailable = sum(1 for r in results if r.verdict == UNAVAILABLE)
    n_pass = sum(1 for r in results if r.verdict == PASS)
    print(f"── verdict: {n_pass} PASS, {n_fail} FAIL, {n_unavailable} UNAVAILABLE ──")
    if n_unavailable and rc != 2:
        print("  ⛔ a soft-skip (UNAVAILABLE) is NOT a pass — read the rows above.")
    print(f"  exit {rc}")


# ── self-test (§3.9, §5 P4 — grows across phases; floor-only for now) ──────


def _self_test() -> int:
    import tempfile

    ok = fail = 0

    # P0 good: clean tree, real floor targets all parse/lint clean.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        good = root / "good.json"
        good.write_text("{}", encoding="utf-8")
        r = check_json_validity(root, paths=[good])
        label = "floor JSON: a well-formed scratch file passes"
        if r.verdict == PASS:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: {r.detail}")

    # P0 bad: trailing comma in a SCRATCH copy of a manifest, never the real
    # file, fed via the `paths=` test seam.
    with tempfile.TemporaryDirectory() as td:
        bad = Path(td) / "bad.json"
        bad.write_text('{"a": 1,}', encoding="utf-8")
        r = check_json_validity(Path(td), paths=[bad])
        label = "floor JSON: a trailing comma in a scratch copy FAILs and names the file"
        if r.verdict == FAIL and str(bad) in r.detail:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: got {r.verdict} ({r.detail})")

    # P0 good: a valid, executable shell scratch file passes.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        good = root / "good.sh"
        good.write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
        good.chmod(0o755)
        r = check_shell_syntax_and_exec(root, syntax_paths=[good], exec_paths=[good])
        label = "floor shell: a valid, executable scratch script passes"
        if r.verdict == PASS:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: {r.detail}")

    # P0 bad: `chmod -x` on a scratch copy of a hook script.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        noexec = root / "noexec.sh"
        noexec.write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
        noexec.chmod(0o644)
        r = check_shell_syntax_and_exec(root, syntax_paths=[noexec], exec_paths=[noexec])
        label = "floor shell: a non-executable scratch hook script FAILs and names the file"
        if r.verdict == FAIL and str(noexec) in r.detail and "not executable" in r.detail:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: got {r.verdict} ({r.detail})")

    # P0 good: a NON-executable scratch `scripts/*.sh`-shaped file must NOT
    # fail the exec-bit half — AGENTS.md's own `-x` loop is scoped to
    # `plugins/*/hooks/*.sh` only.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        plain_script = root / "plain.sh"
        plain_script.write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
        plain_script.chmod(0o644)
        r = check_shell_syntax_and_exec(root, syntax_paths=[plain_script], exec_paths=[])
        label = "floor shell: a non-executable scratch PLAIN script passes (not a hook)"
        if r.verdict == PASS:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: {r.detail}")

    # P0 bad: a genuine bash syntax error in a scratch script.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        broken = root / "broken.sh"
        broken.write_text("#!/usr/bin/env bash\nif [ 1 -eq 1\n", encoding="utf-8")
        broken.chmod(0o755)
        r = check_shell_syntax_and_exec(root, syntax_paths=[broken], exec_paths=[broken])
        label = "floor shell: a genuine bash -n syntax error FAILs and names the file"
        if r.verdict == FAIL and str(broken) in r.detail:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: got {r.verdict} ({r.detail})")

    # P0 skip: a missing tool (simulated via a PATH override, not the real
    # PATH) must report UNAVAILABLE, and that must escalate to exit 1 — never
    # a silent 0 (Ruling 4).
    with tempfile.TemporaryDirectory() as td:
        empty_bin = Path(td) / "empty-bin"
        empty_bin.mkdir()
        starved_env = {"PATH": str(empty_bin)}
        root = Path(td)
        r_prettier = check_prettier(root, timeout=5, env=starved_env)
        r_ruff = check_ruff(root, timeout=5, env=starved_env)
        label = "floor prettier/ruff: absent tool (PATH override) -> UNAVAILABLE, not PASS/crash"
        if r_prettier.verdict == UNAVAILABLE and r_ruff.verdict == UNAVAILABLE:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: prettier={r_prettier.verdict}, ruff={r_ruff.verdict}")

        rc = aggregate([r_prettier, r_ruff], strict=False)
        label = "exit contract: UNAVAILABLE-only (unforced) escalates to exit 1, not 0"
        if rc == 1:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: got exit {rc}")

    # P0 bad: a fixture child process that sleeps past its timeout — the
    # WHOLE process group must die, not just the direct child (a bare
    # `proc.kill()` would leave the grandchild `sleep` running).
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        marker = f"ci-preflight-selftest-{os.getpid()}"
        run = run_bounded(
            ["bash", "-c", f"sleep 20 & disown; echo {marker}; wait"], root, timeout=1
        )
        label = 'timeout primitive: a sleeping child times out and reports "timed out after Ns"'
        if run.timed_out:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: run={run}")

        time.sleep(0.3)  # give the killed group's children a moment to actually exit
        ps = subprocess.run(["ps", "ax", "-o", "command"], capture_output=True, text=True)
        label = (
            "timeout primitive: process-GROUP kill leaves no orphaned grandchild (verified via ps)"
        )
        if marker not in ps.stdout and "sleep 20" not in ps.stdout:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: a sleep/marker process is still visible in `ps`")

    # P2 bad: a checker script missing on disk must report UNAVAILABLE — never
    # a silent PASS, never a crash, and never mistaken for a real FAIL (the
    # interpreter itself would otherwise start fine and exit nonzero on its
    # own "can't open file" error, which _as_check_result would misclassify).
    # Hermetic: a scratch root with no `scripts/` dir at all, so this can never
    # hit the network or the real repo.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r = _run_one_hotspot(
            root,
            "hotspot:test-missing-checker",
            ["python3", "scripts/does-not-exist-checker.py", "--check"],
            "investigate: python3 scripts/does-not-exist-checker.py --check",
            10,
        )
        label = "missing-checker guard: an absent checker script reports UNAVAILABLE, not FAIL"
        if r.verdict == UNAVAILABLE and "missing on disk" in r.detail:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: got {r.verdict} ({r.detail})")

    # P2 good: the same guard must NOT block a checker that genuinely exists —
    # proving this is a presence check, not an accidental blanket skip.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "scripts").mkdir()
        present = root / "scripts" / "present-checker.py"
        present.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
        r = _run_one_hotspot(
            root,
            "hotspot:test-present-checker",
            ["python3", "scripts/present-checker.py", "--check"],
            "n/a",
            10,
        )
        label = "missing-checker guard: a checker script that exists still runs and PASSes"
        if r.verdict == PASS:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: got {r.verdict} ({r.detail})")

    # Exit-aggregation contract: every tier combination, both strict settings.
    _p = CheckResult("p", PASS)
    _f = CheckResult("f", FAIL)
    _u = CheckResult("u", UNAVAILABLE)
    cases = [
        ([_p], False, 0),
        ([_p, _p], True, 0),
        ([_p, _u], False, 1),
        ([_p, _u], True, 2),
        ([_p, _f], False, 2),
        ([_p, _f], True, 2),
        ([_f, _u], False, 2),
    ]
    for results, strict, want in cases:
        got = aggregate(results, strict)
        label = f"exit contract: {[r.verdict for r in results]} strict={strict} -> {want}"
        if got == want:
            ok += 1
            print(f"  ok   {label}")
        else:
            fail += 1
            print(f"  FAIL {label}: got {got}")

    print(f"  pass={ok} fail={fail}")
    return 0 if fail == 0 else 1


# ── main ─────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--base", default="origin/main", help="base ref for the ratchet pre-warm (class 1)"
    )
    ap.add_argument(
        "--strict", action="store_true", help="escalate any UNAVAILABLE (soft-skip) to exit 2"
    )
    ap.add_argument(
        "--self-test", action="store_true", help="exercise this coordinator's own primitives"
    )
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not _valid_ref_syntax(args.base):
        print(f"error: --base {args.base!r} is not a syntactically valid git ref")
        return 2

    root = _repo_root()
    print_banner()

    floor_results = run_floor(root)
    print_results("floor", floor_results)

    print_report(build_report(root))
    context_results = [check_unstaged_sensitive_paths(root)]
    print_results("context", context_results)

    hotspot_results = run_hotspots(root, args.base)
    print_results("hotspot (6 classes / 13 commands, unconditional)", hotspot_results)

    results: list[CheckResult] = floor_results + context_results + hotspot_results
    rc = aggregate(results, args.strict)
    print_verdict(results, rc)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
