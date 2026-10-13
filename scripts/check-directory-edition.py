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

MUST-FAIL HALVES (a check that cannot fail proves nothing)
  M1  an always-on hook wrapped in the REAL posture gate is inert; the same hook behind a gate with the
      posture test removed, and behind a gate with the TRUST test removed, is not - so each property comes
      from the gate and the harness can see it go
  M3  a hook that runs `python3 -c` from the project directory is classified unsafe (a planted module in the
      project root is imported); the same hook with `-I` is safe
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

        print("── must-fail halves ──")
        must_fail_gate_shim(dist)
        must_fail_python_cwd(dist)
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
        gate_file.write_text(
            "\n".join(ln for ln in real_text.splitlines() if "grep -Fxq" not in ln) + "\n"
        )
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


def trust_helper_checks(dist: Path) -> None:
    """scripts/edition-trust.sh and the gate's --status must agree, and the helper must refuse to grant trust
    to a project with nothing to run or with a redirected .ravenclaude."""
    helper, gate = dist / "scripts" / "edition-trust.sh", dist / "hooks" / "posture-gate.sh"
    with tempfile.TemporaryDirectory(prefix="rc-trust-") as td:
        root = Path(td).resolve()
        home, proj, other = root / "home", root / "proj", root / "other"
        for d in (home, proj, other):
            d.mkdir()
        env = {"PATH": "/usr/bin:/bin", "HOME": str(home), "CLAUDE_PROJECT_DIR": str(proj)}

        def run(script: Path, *args: str, project: Path = proj) -> subprocess.CompletedProcess:
            e = dict(env, CLAUDE_PROJECT_DIR=str(project))
            return subprocess.run(
                ["bash", str(script), *args], capture_output=True, text=True, env=e, cwd=project
            )

        def state(project: Path = proj) -> str:
            return run(gate, "--status", project=project).stdout.strip()

        tf = home / ".ravenclaude" / "edition-trusted-projects"
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
        (proj / ".ravenclaude" / "comfort-posture.yaml").write_text("schema_version: 5\n")
        check("trust: posture present, nobody trusted it -> untrusted", state() == "untrusted")
        check(
            "trust: status says not-trusted",
            run(helper, "status", str(proj)).stdout.strip() == "not-trusted",
        )
        r = run(helper, "add", str(proj))
        check(
            "trust: add records the REAL path once",
            r.returncode == 0 and tf.read_text().splitlines() == [str(proj)],
            r.stderr.strip()[:90],
        )
        run(helper, "add", str(proj))
        check("trust: add is idempotent", tf.read_text().splitlines() == [str(proj)])
        check("trust: the gate now says active", state() == "active")
        link = root / "link"
        link.symlink_to(proj)
        check("trust: a symlink to a trusted project resolves to it (pwd -P)", state(link) == "active")
        check("trust: a different project is not trusted by that entry", state(other) == "no-posture")
        (other / ".ravenclaude").mkdir()
        (other / ".ravenclaude" / "comfort-posture.yaml").write_text("x: 1\n")
        check("trust: ... even with its own posture file", state(other) == "untrusted")
        mid = proj / ".ravenclaude" / "comfort-posture.yaml"
        mid.unlink()
        mid.symlink_to(other / ".ravenclaude" / "comfort-posture.yaml")
        check("trust: a symlinked posture file is never active", state() == "untrusted")
        mid.unlink()
        mid.write_text("schema_version: 5\n")
        (proj / ".ravenclaude" / "runs").symlink_to(root)
        check("trust: a symlinked .ravenclaude/runs is never active", state() == "untrusted")
        (proj / ".ravenclaude" / "runs").unlink()
        check("trust: ... and active again once the symlink is gone", state() == "active")
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
        check("trust: add refuses a redirected .ravenclaude", r.returncode == 2, r.stderr.strip()[:90])


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
