#!/usr/bin/env python3
"""check-directory-edition.py - Gate 301: the Anthropic-Directory edition of ravenclaude-core.

Builds the edition from the source plugin and refuses it unless every claim in its README and PRIVACY.md
holds. The point of the edition is that a stranger can install it and be told, truthfully, that every hook
is off until they opt in; this gate is what keeps that sentence true as the source plugin changes weekly.

REAL CHECKS (on the freshly built edition)
  1  the builder's and the audit harness's own self-tests pass (their positive controls)
  2  deterministic build; limits (files, per-file bytes, symlinks, non-image binaries); structure (no
     `experimental`, no bin/ monitors/ CLAUDE.md dashboard.html, every hook wrapped in the posture gate
     except the declared setup prompt); README lists exactly the shipped hooks; every network primitive
     in an executable is classified; no secret-shaped string; the committed file list is fresh
  3  every shipped hook, run from the built hooks.json, is INERT with no posture file, INERT when a posture
     file is present but the person has not trusted the project (a cloned repository can ship a posture
     file, so the file alone must switch nothing on), and SAFE under a hostile posture file in a trusted
     project (scripts/directory-edition-hook-audit.py), writes only under .ravenclaude/, imports no module
     from the project root, and starts only programs on the manifest's allow-list
  4  `claude plugin validate --strict` passes (when the claude CLI is present; otherwise reported as NOT RUN,
     which is not a pass)
  5  the shipped /repo-review workflow refuses to start without an absolute args.pluginRoot (when node is
     present; otherwise NOT RUN), so its scripts can never resolve inside the project under review

MUST-FAIL HALVES (a check that cannot fail proves nothing)
  M1  an always-on hook wrapped in the REAL posture gate is inert; the same hook behind a gate with the
      posture test removed, and behind a gate with the TRUST test removed, is not - so each property comes
      from the gate and the harness can see it go
  M3  a hook that runs `python3 -c` from the project directory is classified unsafe (a planted module in the
      project root is imported); the same hook with `-I` is safe
  M4  the same workflow with its pluginRoot validation neutered starts without a root, so check 5 can fail
  M5  a hook that runs git in the payload's cwd executes a vendored repository's core.fsmonitor and is
      classified unsafe (H7); the same hook at the project root with core.fsmonitor=false is safe
  M8  the source plugin's runaway-brake.sh (it walks up from the payload cwd) honours a posture nested in
      the project and is classified unsafe (H8); the edition's edited copy is safe
  M2  real hooks that ARE unsafe (guard-destructive.sh always on; dod-gate.sh runs a command read from the
      posture file) are classified unsafe by the same audit, so its payloads and seeds reach real triggers

HONEST LIMIT: the syscall lane (network and exec observation) needs `strace`. Without it the audit still
uses tripwires (curl/wget/nc/ssh/gh/claude stubs and a python socket hook) and says so; set
RC_EDITION_REQUIRE_STRACE=1 (the release check) to make its absence a failure.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, HERE / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


build = _load("rc_build_edition", "build-directory-edition.py")
audit = _load("rc_audit_edition", "directory-edition-hook-audit.py")

PASS = FAIL = 0


def ok(label: str) -> None:
    global PASS
    PASS += 1
    print(f"  \033[32m✓\033[0m {label}")


def bad(label: str, why: str = "") -> None:
    global FAIL
    FAIL += 1
    print(f"  \033[31m✗\033[0m {label}" + (f"\n      {why}" if why else ""))


def check(label: str, cond: bool, why: str = "") -> None:
    ok(label) if cond else bad(label, why)


def run_selftest(script: str) -> tuple[bool, str]:
    cp = subprocess.run(
        [sys.executable, str(HERE / script), "--self-test"],
        capture_output=True,
        text=True,
        timeout=900,
    )
    last = (cp.stdout.strip().splitlines() or [""])[-1]
    m = re.search(r"(\d+) passed, (\d+) failed", last)
    return cp.returncode == 0 and bool(m) and m.group(2) == "0", last


def _wrap(cmd: str) -> str:
    return build.GATE_PREFIX + cmd


def main() -> int:
    manifest = build.load_manifest(build.DEFAULT_MANIFEST)
    pa = manifest.get("hook_audit", {})
    write_dirs = tuple(pa.get("write_dirs", ["ravenclaude"]))
    allowed_out = tuple(pa.get("allowed_output", []))
    allowed_execs = set(pa.get("allowed_execs", []))
    require_strace = os.environ.get("RC_EDITION_REQUIRE_STRACE") == "1"
    quick = "--quick" in sys.argv

    print("── 1. the tools' own positive controls ──")
    for script in ("build-directory-edition.py", "directory-edition-hook-audit.py"):
        passed, last = run_selftest(script)
        check(f"{script} --self-test: {last}", passed)

    print("── 2. the built edition ──")
    try:
        problems, paths, _ = build.check_problems(manifest, REPO)
    except build.BuildError as e:
        bad("build", str(e))
        problems, paths = [], []
    for p in problems:
        bad(p)
    if not problems and paths:
        ok(
            f"{len(paths)} files: deterministic, within limits, structure + README parity + network + secrets + file list all clean"
        )

    if quick:
        print(
            f"directory-edition: {PASS} passed, {FAIL} failed (--quick: hook audit and must-fail halves skipped)"
        )
        return 1 if FAIL else 0

    with tempfile.TemporaryDirectory(prefix="rc-edition-gate-") as td:
        dist = Path(td) / "dist"
        try:
            build.full_build(manifest, dist, REPO)
        except build.BuildError as e:
            bad("build for the hook audit", str(e))
            print(f"directory-edition: {PASS} passed, {FAIL} failed")
            return 1

        print("── 3. every shipped hook, measured ──")
        res = audit.measure(dist, allowed_output=allowed_out, write_dirs=write_dirs)
        if not res["strace"]:
            msg = "strace absent: network and exec observed by tripwires only (set RC_EDITION_REQUIRE_STRACE=1 to require it)"
            if require_strace:
                bad(msg)
            else:
                print(f"  NOT RUN  syscall lane - {msg}")
        shipped = {h["id"] for h in manifest["components"]["hooks"]}
        check(
            "the audit measured exactly the manifest's hooks",
            set(res["hooks"]) == shipped,
            f"measured {sorted(res['hooks'])} vs manifest {sorted(shipped)}",
        )
        shipped_scripts = {Path(p).name for p in paths if p.endswith((".sh", ".py"))}
        for hid, e in sorted(res["hooks"].items()):
            check(
                f"{hid}: inert with no posture file ({e['runs']} payloads)",
                e["inert"],
                "; ".join(e["inert_reasons"][:2]),
            )
            check(
                f"{hid}: inert when a posture file is present but the project is not trusted",
                e["untrusted_inert"],
                "; ".join(e["untrusted_reasons"][:2]),
            )
            check(
                f"{hid}: safe under a hostile posture file in a trusted project",
                e["hostile_safe"],
                "; ".join(e["hostile_reasons"][:2]),
            )
            if res["strace"]:
                extra = sorted(set(e["hostile_execs"]) - allowed_execs - shipped_scripts)
                check(
                    f"{hid}: starts only allow-listed programs",
                    not extra,
                    f"unexpected programs: {extra}",
                )

        print("── 4. claude plugin validate --strict ──")
        for target, label in (
            (dist, "marketplace manifest"),
            (dist / ".claude-plugin" / "plugin.json", "plugin manifest"),
        ):
            status, out = _validate(target)
            if status == "unavailable":
                print(f"  NOT RUN  {label}: {out} (not a pass)")
            else:
                check(f"{label}: validate --strict", status == "pass", out)

        print("── the trust helper ──")
        trust_helper_checks(dist)

        print("── the /repo-review workflow's plugin root ──")
        workflow_root_checks(dist)

        print("── must-fail halves ──")
        must_fail_gate_shim(dist)
        must_fail_python_cwd(dist)
        must_fail_git_cwd(dist)
        must_fail_nested_posture(dist)
        must_fail_real_hooks()

    print(f"directory-edition: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


def _validate(target: Path) -> tuple[str, str]:
    exe = shutil.which("claude")
    if not exe:
        return "unavailable", "claude CLI not on PATH"
    cp = subprocess.run(
        [exe, "plugin", "validate", "--strict", str(target)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    return ("pass" if cp.returncode == 0 else "fail"), (cp.stdout + cp.stderr).strip()[-300:]


def _measure_one(plugin: Path, hooks_json: Path | None, only: str, **kw) -> dict:
    return audit.measure(plugin, hooks_json, only={only}, **kw)["hooks"].get(only, {})


def must_fail_gate_shim(dist: Path) -> None:
    """M1: the property comes from the gate. A hook that exits 2 on every call is the stand-in for any
    always-on guard; behind the real shim it is inert, behind a shim without the posture test it is not."""
    with tempfile.TemporaryDirectory(prefix="rc-m1-") as td:
        plug = Path(td) / "p"
        shutil.copytree(dist, plug)
        hook = plug / "hooks" / "zz-always-on.sh"
        hook.write_text('#!/usr/bin/env bash\necho "always on" >&2\nexit 2\n')
        hook.chmod(0o755)
        hj = plug / "hooks" / "hooks.json"
        data = json.loads(hj.read_text())
        data["hooks"].setdefault("UserPromptSubmit", []).append(
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": _wrap('"${CLAUDE_PLUGIN_ROOT}/hooks/zz-always-on.sh"'),
                    }
                ]
            }
        )
        hj.write_text(json.dumps(data))
        real = _measure_one(plug, hj, "zz-always-on.sh")
        check(
            "M1 an always-on hook behind the REAL posture gate is inert with no posture file",
            bool(real.get("inert")),
            "; ".join(real.get("inert_reasons", [])),
        )
        check(
            "M1 ... and inert when a posture file is present but the project is not trusted",
            bool(real.get("untrusted_inert")),
            "; ".join(real.get("untrusted_reasons", [])),
        )
        check(
            "M1 ... and it RUNS (exit 2) when the project is trusted under a hostile posture, so the trusted lanes are not vacuous",
            real.get("hostile_rcs") == [2],
            f"exit codes in the trusted lane: {real.get('hostile_rcs')}",
        )
        gate_file = plug / "hooks" / "posture-gate.sh"
        real_text = gate_file.read_text()
        gate_file.write_text('#!/usr/bin/env bash\nexec "$@"\n')
        mutant = _measure_one(plug, hj, "zz-always-on.sh")
        check(
            "M1 the same hook behind a gate with the posture test removed is NOT inert (the harness can see it)",
            mutant.get("inert") is False,
        )
        # the trust test is its own line of defence: remove only it, and the no-posture lane stays clean
        # while the untrusted lane (posture present, nobody trusted it) sees the hook run
        trust_test = 'grep -Fxq -- "$real$tab$digest" "$tf" 2>/dev/null'
        quick_test = '! grep -Fq -- "$real$tab" "$HOME/.ravenclaude/edition-trusted-projects" 2>/dev/null'
        check(
            "M1 the trust tests are where the shim says they are (so removing them is a real mutation)",
            trust_test in real_text and quick_test in real_text,
        )
        gate_file.write_text(real_text.replace(trust_test, "true").replace(quick_test, "false"))
        no_trust = _measure_one(plug, hj, "zz-always-on.sh")
        check(
            "M1 a gate with only the TRUST test removed: still inert with no posture file",
            bool(no_trust.get("inert")),
        )
        check(
            "M1 ... but NOT inert when a posture file is present and untrusted (the harness can see it)",
            no_trust.get("untrusted_inert") is False,
        )


def must_fail_python_cwd(dist: Path) -> None:
    """M3: `python3 -c` run from the project directory imports the project's own modules. A hook that does it
    must be classified unsafe; the same hook with -I must not be. Both sit behind the real gate in a trusted
    project with a posture file, i.e. exactly where a real hook would run."""
    with tempfile.TemporaryDirectory(prefix="rc-m3-") as td:
        plug = Path(td) / "p"
        shutil.copytree(dist, plug)
        hj = plug / "hooks" / "hooks.json"
        data = json.loads(hj.read_text())
        for name, body in (
            ("zz-py-cwd.sh", 'python3 -c "import shlex" 2>/dev/null; exit 0'),
            ("zz-py-iso.sh", 'python3 -I -c "import shlex" 2>/dev/null; exit 0'),
        ):
            f = plug / "hooks" / name
            f.write_text("#!/usr/bin/env bash\n" + body + "\n")
            f.chmod(0o755)
            data["hooks"].setdefault("UserPromptSubmit", []).append(
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": _wrap('"${CLAUDE_PLUGIN_ROOT}/hooks/' + name + '"'),
                        }
                    ]
                }
            )
        hj.write_text(json.dumps(data))
        bad = _measure_one(plug, hj, "zz-py-cwd.sh", write_dirs=("ravenclaude",))
        check(
            "M3 a hook running python3 -c from the project dir is NOT hostile-safe (H6)",
            bad.get("hostile_safe") is False
            and any(r.startswith("H6") for r in bad.get("hostile_reasons", [])),
            "; ".join(bad.get("hostile_reasons", [])),
        )
        good = _measure_one(plug, hj, "zz-py-iso.sh", write_dirs=("ravenclaude",))
        check(
            "M3 the same hook with python3 -I is hostile-safe",
            bool(good.get("hostile_safe")),
            "; ".join(good.get("hostile_reasons", [])),
        )


def _unprivileged_prefix(scratch: Path) -> list[str] | None:
    """A command prefix that runs as a user without root's permission overrides, or None when that is not
    possible here. As root, `unshare --user --map-user=1000` drops the capabilities on exec; the probe below
    PROVES it by failing to list a directory with mode 0300, so a prefix that does not drop anything is never used."""
    probe = scratch / "probe-dir"
    probe.mkdir(exist_ok=True)
    os.chmod(probe, 0o300)
    candidates: list[list[str]] = [[]] if os.geteuid() != 0 else []
    if os.geteuid() == 0 and shutil.which("unshare"):
        candidates.append(["unshare", "--user", "--map-user=1000", "--map-group=1000", "--"])
    try:
        for prefix in candidates:
            try:
                cp = subprocess.run(prefix + ["ls", str(probe)], capture_output=True, timeout=20)
            except Exception:  # noqa: BLE001
                continue
            if cp.returncode != 0:
                return prefix
        return None
    finally:
        os.chmod(probe, 0o700)


def trust_helper_checks(dist: Path) -> None:
    """scripts/edition-trust.sh and the gate must agree; trust is bound to the CONTENT of the project files the
    hooks read; and the gate refuses any symlink under .ravenclaude/ and any path with a newline or tab."""
    helper, gate = dist / "scripts" / "edition-trust.sh", dist / "hooks" / "posture-gate.sh"
    with tempfile.TemporaryDirectory(prefix="rc-trust-") as td:
        root = Path(td).resolve()
        home, proj, other = root / "home", root / "proj", root / "other"
        for d in (home, proj, other):
            d.mkdir()
        env = {"PATH": "/usr/bin:/bin", "HOME": str(home), "CLAUDE_PROJECT_DIR": str(proj)}

        def run(
            script: Path, *args: str, project: Path = proj, gate_file: Path | None = None
        ) -> subprocess.CompletedProcess:
            e = dict(env, CLAUDE_PROJECT_DIR=str(project))
            return subprocess.run(
                ["bash", str(gate_file or script), *args],
                capture_output=True,
                text=True,
                env=e,
                cwd=project,
            )

        def state(project: Path = proj, detail: bool = False, gate_file: Path | None = None) -> str:
            args = ("--status", "detail") if detail else ("--status",)
            return run(gate, *args, project=project, gate_file=gate_file).stdout.strip()

        def ran(project: Path = proj) -> bool:
            """Does a command behind the gate actually run? (the only thing that matters in the end)"""
            return run(gate, "echo", "ran", project=project).stdout.strip() == "ran"

        tf = home / ".ravenclaude" / "edition-trusted-projects"
        posture = proj / ".ravenclaude" / "comfort-posture.yaml"
        check("trust: no posture file -> the gate says no-posture", state() == "no-posture")
        check(
            "trust: status with no posture file says no-posture",
            run(helper, "status", str(proj)).stdout.strip() == "no-posture",
        )
        r = run(helper, "add", str(proj))
        check(
            "trust: add refuses a project with no posture file, and writes nothing",
            r.returncode == 2 and not tf.exists(),
            r.stderr.strip()[:90],
        )
        (proj / ".ravenclaude").mkdir()
        posture.write_text("schema_version: 5\n")
        check("trust: posture present, nobody trusted it -> untrusted", state() == "untrusted")
        check("trust: ... and the hook behind the gate does not run", not ran())
        check(
            "trust: status says not-trusted",
            run(helper, "status", str(proj)).stdout.strip() == "not-trusted",
        )
        spec = audit.trust_line(proj)
        check(
            "trust: the gate's --line equals the independent specification (path TAB sha256 of the 3 files)",
            run(gate, "--line").stdout.rstrip("\n") == spec,
            f"gate={run(gate, '--line').stdout.strip()!r} spec={spec!r}",
        )
        r = run(helper, "add", str(proj))
        check(
            "trust: add records the REAL path and the content digest, once",
            r.returncode == 0 and tf.read_text().splitlines() == [spec],
            r.stderr.strip()[:90],
        )
        run(helper, "add", str(proj))
        check("trust: add is idempotent", tf.read_text().splitlines() == [spec])
        check("trust: the gate now says active, and the hook runs", state() == "active" and ran())
        link = root / "link"
        link.symlink_to(proj)
        check(
            "trust: a symlink to a trusted project resolves to it (pwd -P)", state(link) == "active"
        )
        check(
            "trust: a different project is not trusted by that entry", state(other) == "no-posture"
        )
        (other / ".ravenclaude").mkdir()
        (other / ".ravenclaude" / "comfort-posture.yaml").write_text("x: 1\n")
        check("trust: ... even with its own posture file", state(other) == "untrusted")

        # trust is bound to CONTENT: change any file the hooks read and the hooks go off
        posture.write_text("schema_version: 5\nrunaway:\n  max_total: 1\n")
        check(
            "trust: editing the posture after trusting it -> changed, and the hook stops running",
            state(detail=True) == "changed" and state() == "untrusted" and not ran(),
        )
        check(
            "trust: status says changed",
            run(helper, "status", str(proj)).stdout.strip() == "changed",
        )
        posture.write_text("schema_version: 5\n")
        check(
            "trust: ... and restoring the exact bytes restores trust", state() == "active" and ran()
        )
        layout = proj / ".repo-layout.json"
        layout.write_text('{"allowed_globs": ["**"]}\n')
        check(
            "trust: a .repo-layout.json that appears after trusting -> changed",
            state(detail=True) == "changed" and not ran(),
        )
        layout.unlink()
        scope = proj / ".ravenclaude" / "task-scope.json"
        scope.write_text('{"in_scope": ["**"]}\n')
        check(
            "trust: a task-scope.json that appears after trusting -> changed",
            state(detail=True) == "changed" and not ran(),
        )
        scope.unlink()
        check("trust: ... and active again once they are gone", state() == "active")
        posture.write_text("schema_version: 5\n# edited\n")
        r = run(helper, "add", str(proj))
        check(
            "trust: re-running add after a change REPLACES the old line (one line per project)",
            r.returncode == 0
            and tf.read_text().splitlines() == [audit.trust_line(proj)]
            and state() == "active",
            r.stderr.strip()[:90],
        )
        posture.write_text("schema_version: 5\n")
        run(helper, "add", str(proj))

        mid = posture
        mid.unlink()
        mid.symlink_to(other / ".ravenclaude" / "comfort-posture.yaml")
        check("trust: a symlinked posture file is never active", state() == "untrusted")
        mid.unlink()
        mid.write_text("schema_version: 5\n")
        (proj / ".ravenclaude" / "runs").symlink_to(root)
        check("trust: a symlinked .ravenclaude/runs is never active", state() == "untrusted")
        (proj / ".ravenclaude" / "runs").unlink()
        (proj / ".ravenclaude" / "runs").mkdir()
        (proj / ".ravenclaude" / "runs" / "thing").symlink_to(root)
        check(
            "trust: a symlink at .ravenclaude/runs/thing (where hooks write) is never active",
            state() == "untrusted" and not ran(),
        )
        old_gate = dist.parent / "gate-no-deep-symlink-check.sh"
        text = gate.read_text()
        needle = '[ "$found" -ne 0 ] || [ -n "$links" ]'
        old_gate.write_text(text.replace(needle, "false"))
        check(
            "trust: M6 a gate that checks only .ravenclaude itself says ACTIVE for that link (the deep check has teeth)",
            needle in text and state(gate_file=old_gate) == "active",
        )
        old_gate.unlink()
        (proj / ".ravenclaude" / "runs" / "thing").unlink()
        (proj / ".ravenclaude" / "runs" / "thing").mkdir()
        (proj / ".ravenclaude" / "runs" / "thing" / "runaway").symlink_to(root)
        check(
            "trust: a symlink three levels down (.ravenclaude/runs/thing/runaway) is never active",
            state() == "untrusted",
        )
        (proj / ".ravenclaude" / "runs" / "thing" / "runaway").unlink()
        # depth 4: the counter file runaway-brake.sh opens. find's start path is depth 0, so
        # runs/thing/runaway/<session_id> is depth 4 — a -maxdepth 3 walk does not see this link.
        (proj / ".ravenclaude" / "runs" / "thing" / "runaway").mkdir()
        counter = proj / ".ravenclaude" / "runs" / "thing" / "runaway" / "sess"
        counter.symlink_to(root / "outside-counter")
        check(
            "trust: a file symlink at .ravenclaude/runs/thing/runaway/<session_id> (depth 4) is never active",
            state() == "untrusted" and not ran(),
        )
        text = gate.read_text()
        shallow = dist.parent / "gate-maxdepth-3.sh"
        find_cmd = 'links="$(find "$proj/.ravenclaude" -type l -print 2>&1)"; found=$?'
        shallow_cmd = 'links="$(find "$proj/.ravenclaude" -maxdepth 3 -type l -print 2>&1)"; found=$?'
        shallow.write_text(text.replace(find_cmd, shallow_cmd, 1))
        check(
            "trust: M6 a gate that stops at depth 3 says ACTIVE for that counter-file link "
            "(the unbounded walk has teeth)",
            find_cmd in text and state(gate_file=shallow) == "active",
        )
        shallow.unlink()
        counter.unlink()
        (proj / ".ravenclaude" / "runs" / "thing" / "runaway").rmdir()
        (proj / ".ravenclaude" / "runs" / "thing").rmdir()
        (proj / ".ravenclaude" / "runs").rmdir()
        check("trust: ... and active again once the links are gone", state() == "active")

        # a newline in the project path would let one trust-file entry stand for two patterns
        nl_dir = root / "proj\nx"
        (nl_dir / ".ravenclaude").mkdir(parents=True)
        (nl_dir / ".ravenclaude" / "comfort-posture.yaml").write_text("schema_version: 5\n")
        dg = audit.trust_digest(nl_dir)
        before_weird = tf.read_text()
        tf.write_text(before_weird + f"{root}/proj\nx\t{dg}\n")
        check(
            "trust: a path with a newline is refused even when the trust file seems to list it",
            state(nl_dir) == "untrusted" and not ran(nl_dir),
        )
        text = gate.read_text()
        nl_gate = dist.parent / "gate-no-newline-check.sh"
        nl_gate.write_text(
            text.replace('case "$real" in ""|*"$nl"*|*"$tab"*) why=path; return 1 ;; esac', "")
        )
        check(
            "trust: M7 a gate without the newline check says ACTIVE for it (the check has teeth)",
            'case "$real" in ""|*"$nl"*' in text and state(nl_dir, gate_file=nl_gate) == "active",
        )
        nl_gate.unlink()
        r = run(helper, "add", str(nl_dir), project=nl_dir)
        check("trust: add refuses a path with a newline", r.returncode == 2, r.stderr.strip()[:90])
        tf.write_text(before_weird)

        # an unreadable directory under .ravenclaude/ could be hiding a symlink: fail closed, not open
        unpriv = _unprivileged_prefix(root)
        if unpriv is None:
            print("  NOT RUN  unreadable-directory check: cannot drop privileges here (not a pass)")
        else:
            hid, outside, home2 = root / "hid", root / "outside", root / "home2"
            (hid / ".ravenclaude" / "runs").mkdir(parents=True)
            outside.mkdir()
            home2.joinpath(".ravenclaude").mkdir(parents=True)
            (hid / ".ravenclaude" / "comfort-posture.yaml").write_text("schema_version: 5\n")
            (hid / ".ravenclaude" / "runs" / "thing").symlink_to(outside)
            (home2 / ".ravenclaude" / "edition-trusted-projects").write_text(audit.trust_line(hid) + "\n")
            os.chmod(hid / ".ravenclaude" / "runs", 0o300)

            def hid_state(gate_file: Path) -> str:
                cp = subprocess.run(
                    unpriv + ["bash", str(gate_file), "--status"],
                    capture_output=True,
                    text=True,
                    env={"PATH": "/usr/bin:/bin", "HOME": str(home2), "CLAUDE_PROJECT_DIR": str(hid)},
                    cwd=str(hid),
                )
                return cp.stdout.strip()

            check(
                "trust: a symlink hidden in a directory the check cannot read -> never active (find errors fail closed)",
                hid_state(gate) == "untrusted",
                f"gate said {hid_state(gate)!r}",
            )
            text = gate.read_text()
            blind = dist.parent / "gate-ignores-find-errors.sh"
            old_find = '-print 2>&1)"; found=$?'
            blind.write_text(text.replace(old_find, '-print 2>/dev/null)"; found=0'))
            check(
                "trust: M9 a gate that ignores find's errors says ACTIVE for it (the fail-closed check has teeth)",
                old_find in text and hid_state(blind) == "active",
                f"mutant said {hid_state(blind)!r}",
            )
            blind.unlink()
            os.chmod(hid / ".ravenclaude" / "runs", 0o700)

        # work before trust: an untrusted project must not cost a hash of its (huge) files, and a huge file is refused
        big = root / "big"
        (big / ".ravenclaude").mkdir(parents=True)
        (big / ".ravenclaude" / "comfort-posture.yaml").write_text("schema_version: 5\n")
        try:
            with open(big / ".repo-layout.json", "wb") as fh:
                fh.truncate(4 << 30)
            sparse = True
        except OSError:
            sparse = False
        if not sparse:
            print("  NOT RUN  huge-file checks: the filesystem refused a sparse 4 GiB file (not a pass)")
        else:
            t0 = time.monotonic()
            untrusted = state(big)
            check(
                "trust: an untrusted project with a 4 GiB layout file is refused at once (no hashing before the trust lookup)",
                untrusted == "untrusted" and time.monotonic() - t0 < 5,
                f"state={untrusted!r} in {time.monotonic() - t0:.1f}s",
            )
            t0 = time.monotonic()
            r = run(gate, "--line", project=big)
            check(
                "trust: a layout file over 1 MiB is refused with a reason, without hashing it",
                r.returncode == 1 and r.stderr.strip() == "size" and time.monotonic() - t0 < 5,
                f"rc={r.returncode} stderr={r.stderr.strip()!r} in {time.monotonic() - t0:.1f}s",
            )

        r = run(helper, "remove", str(proj))
        check(
            "trust: remove drops the entry and the gate follows",
            r.returncode == 0 and state() == "untrusted" and str(proj) not in tf.read_text(),
        )
        redirected = root / "redir"
        (redirected / "real").mkdir(parents=True)
        (redirected / "real" / "comfort-posture.yaml").write_text("x: 1\n")
        (redirected / ".ravenclaude").symlink_to(redirected / "real")
        r = run(helper, "add", str(redirected))
        check(
            "trust: add refuses a redirected .ravenclaude", r.returncode == 2, r.stderr.strip()[:90]
        )


_WF_HARNESS = r"""
import fs from "node:fs";
const [, , file, ...cases] = process.argv;
const src = fs.readFileSync(file, "utf8").replace(/^export const meta/m, "const meta");
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const fn = new AsyncFunction("args", "agent", "log", "pipeline", "parallel", "phase", "budget", src);
for (const c of cases) {
  const r = await fn(JSON.parse(c), async () => ({}), () => {}, null, null, () => {}, { spent: () => 0 });
  console.log(String((r && r.error) || "NO-ERROR").replace(/\s+/g, " ").slice(0, 400));
}
"""
_WF_CASES = (
    ("no args", {}, True),
    ("a project-relative root", {"pluginRoot": "plugins/ravenclaude-core"}, True),
    ("a root with ..", {"pluginRoot": "/a/../b"}, True),
    ("a root with a space (not shell-safe)", {"pluginRoot": "/a b"}, True),
    ("an absolute root (reaches the next check)", {"pluginRoot": "/ok/plugin/root"}, False),
)


def _run_workflow(node: str, harness: Path, wf: Path) -> list[str]:
    cp = subprocess.run(
        [node, str(harness), str(wf)] + [json.dumps(c[1]) for c in _WF_CASES],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(harness.parent),
        env={"PATH": os.environ.get("PATH", "")},
    )
    return cp.stdout.splitlines() if cp.returncode == 0 else ["NODE-ERROR " + cp.stderr.strip()[-200:]]


def workflow_root_checks(dist: Path) -> None:
    """The edition's /repo-review workflow takes its plugin root from args and has no fallback, so a hostile
    project can never supply the scripts it runs. Exercised with node when present (NOT RUN is not a pass)."""
    wf = dist / "skills" / "repo-review" / "workflows" / "repo-sweep.workflow.js"
    if not wf.is_file():
        return
    node = shutil.which("node")
    if not node:
        print("  NOT RUN  workflow plugin-root validation: node not on PATH (not a pass)")
        return
    with tempfile.TemporaryDirectory(prefix="rc-edition-wf-") as td:
        h = Path(td) / "harness.mjs"
        h.write_text(_WF_HARNESS)
        out = _run_workflow(node, h, wf)
        for (label, _args, must_refuse), line in zip(_WF_CASES, out + [""] * len(_WF_CASES)):
            refused = "args.pluginRoot" in line
            check(f"workflow: {label} -> {'refused' if must_refuse else 'accepted'}", refused == must_refuse, line[:120])
        src = wf.read_text()
        mutant = src.replace("if (!/^", "if (false && !/^", 1)
        check("workflow: the mutant differs from the build (the teeth are real)", mutant != src)
        mp = Path(td) / "mutant.workflow.js"
        mp.write_text(mutant)
        mout = _run_workflow(node, h, mp)
        check(
            "workflow: M4 with the validation neutered, no-args is NOT refused (so check 5 can fail)",
            bool(mout) and "args.pluginRoot" not in mout[0],
            (mout[0] if mout else "")[:120],
        )


def must_fail_git_cwd(dist: Path) -> None:
    """M5: every scratch project holds a vendored git repository whose .git/config runs a command on
    `git status`. A hook that runs git in the payload's cwd (which can drift into it) runs that command."""
    bodies = (
        (
            "zz-git-cwd.sh",
            """c=$(sed -n 's/.*"cwd": *"\\([^"]*\\)".*/\\1/p'); git -C "${c:-.}" status --porcelain >/dev/null 2>&1; exit 0""",
        ),
        (
            "zz-git-root.sh",
            """git -c core.fsmonitor=false -C "$CLAUDE_PROJECT_DIR" status --porcelain >/dev/null 2>&1; exit 0""",
        ),
    )
    with tempfile.TemporaryDirectory(prefix="rc-m5-") as td:
        plug = Path(td) / "p"
        shutil.copytree(dist, plug)
        hj = plug / "hooks" / "hooks.json"
        data = json.loads(hj.read_text())
        for name, body in bodies:
            f = plug / "hooks" / name
            f.write_text("#!/usr/bin/env bash\n" + body + "\n")
            f.chmod(0o755)
            data["hooks"].setdefault("UserPromptSubmit", []).append(
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": _wrap('"${CLAUDE_PLUGIN_ROOT}/hooks/' + name + '"'),
                        }
                    ]
                }
            )
        hj.write_text(json.dumps(data))
        bad = _measure_one(plug, hj, "zz-git-cwd.sh", write_dirs=("ravenclaude",))
        check(
            "M5 a hook running git in the payload cwd is NOT hostile-safe (H7)",
            bad.get("hostile_safe") is False
            and any(r.startswith("H7") for r in bad.get("hostile_reasons", [])),
            "; ".join(bad.get("hostile_reasons", [])),
        )
        good = _measure_one(plug, hj, "zz-git-root.sh", write_dirs=("ravenclaude",))
        check(
            "M5 the same hook at the project root with core.fsmonitor=false is hostile-safe",
            bool(good.get("hostile_safe")),
            "; ".join(good.get("hostile_reasons", [])),
        )


def must_fail_nested_posture(dist: Path) -> None:
    """M8: the source runaway-brake.sh uses the first .ravenclaude/ found walking up from the payload cwd, so a
    posture inside a vendored directory of a cloned repository is honoured and its state is written there. The
    edition's copy resolves the root from CLAUDE_PROJECT_DIR only. Both run behind the real gate."""
    with tempfile.TemporaryDirectory(prefix="rc-m8-") as td:
        plug = Path(td) / "p"
        shutil.copytree(dist, plug)
        good = _measure_one(plug, None, "runaway-brake.sh", write_dirs=("ravenclaude",))
        check(
            "M8 the edition's runaway-brake.sh ignores a posture nested in the project",
            bool(good.get("hostile_safe")),
            "; ".join(good.get("hostile_reasons", [])),
        )
        shutil.copyfile(
            REPO / "plugins" / "ravenclaude-core" / "hooks" / "runaway-brake.sh",
            plug / "hooks" / "runaway-brake.sh",
        )
        bad = _measure_one(plug, None, "runaway-brake.sh", write_dirs=("ravenclaude",))
        check(
            "M8 ... while the source copy (walk-up) honours it: NOT hostile-safe (H8), so the edit is necessary",
            bad.get("hostile_safe") is False
            and any(r.startswith("H8") for r in bad.get("hostile_reasons", [])),
            "; ".join(bad.get("hostile_reasons", [])),
        )


def must_fail_real_hooks() -> None:
    """M2: real hooks that are unsafe must be classified unsafe, from the SOURCE plugin where they exist."""
    src = REPO / "plugins" / "ravenclaude-core"
    for hid, lane in (("guard-destructive.sh", "inert"), ("dod-gate.sh", "hostile")):
        e = _measure_one(src, None, hid, write_dirs=("ravenclaude",))
        if not e:
            bad(f"M2 {hid} was not found in the source hooks.json (the control has gone stale)")
        elif lane == "inert":
            check(
                "M2 guard-destructive.sh (always on, denies a destructive command) is classified NOT inert",
                e["inert"] is False,
                "the audit's payloads no longer reach this guard",
            )
        else:
            check(
                "M2 dod-gate.sh (runs a command read from the posture file) is classified NOT hostile-safe",
                e["hostile_safe"] is False,
                "the hostile posture/seed no longer reaches the command it runs",
            )


if __name__ == "__main__":
    sys.exit(main())
