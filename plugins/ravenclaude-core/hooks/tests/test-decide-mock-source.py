#!/usr/bin/env python3
"""test-decide-mock-source.py — THING_DECIDE_* test-hook source gate (Gate 303, decide half).

A cloned repo can plant THING_DECIDE_* test hooks through the `env` block of its
.claude/settings.json, and Claude Code exports that block into every hook process.
Unguarded, THING_DECIDE_MOCK_VERDICT=yes would make every routed yes/no auto-resolve
"yes" under decision_review: binding. thing-decide.py's _mock_gate honours a mock only
when THING_DECIDE_ALLOW_MOCK=1 is set, no project-scope settings file (under
$CLAUDE_PROJECT_DIR and the --root dir) has a THING_DECIDE_* key in .env (an
unparseable or empty file counts as planted), and, under a live session (CLAUDECODE
or THING_DECIDE_LIVE_SESSION=1), only a defer-producing verdict mock. This is the
decide-engine twin of test-mock-verdict-source.sh (the seat half of Gate 303).

Hermetic: a STUB `claude` first on PATH stands in for a real seat. It records each
call and always votes "no", so the three outcomes are distinguishable:
  mock honoured  -> "yes"   (stub never called)
  real seat ran  -> "no"    (stub called)
  seats abstain  -> "defer" (stub never called)
No live model is ever called.

Run: python3 test-decide-mock-source.py   (exit 0 = pass)
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ENGINE = (Path(__file__).resolve().parents[2] / "scripts" / "thing-decide.py").resolve()
PASS = 0
FAIL = 0


def ok(msg: str) -> None:
    global PASS
    PASS += 1
    print(f"  ✓ {msg}")


def bad(msg: str) -> None:
    global FAIL
    FAIL += 1
    print(f"  ✗ {msg}")


def hermetic_env(stub_dir: Path, extra: dict) -> dict:
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("THING_DECIDE_")
        and k not in ("CLAUDECODE", "CLAUDE_PROJECT_DIR", "ANTHROPIC_API_KEY", "THING_SEAT_BARE")
    }
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '/usr/bin:/bin')}"
    env["RC_CLAUDE_HOME_LOOKUP"] = "0"
    env.update(extra)
    return env


def make_project(
    base: Path, name: str, settings: str | None = None, local: str | None = None
) -> Path:
    d = base / name
    (d / ".claude").mkdir(parents=True, exist_ok=True)
    (d / ".ravenclaude").mkdir(parents=True, exist_ok=True)
    (d / ".ravenclaude" / "comfort-posture.yaml").write_text(
        "schema_version: 5\ndecision_review: binding\n", encoding="utf-8"
    )
    if settings is not None:
        (d / ".claude" / "settings.json").write_text(settings, encoding="utf-8")
    if local is not None:
        (d / ".claude" / "settings.local.json").write_text(local, encoding="utf-8")
    return d


def run(
    stub_dir: Path, sentinel: Path, root: Path, cwd: Path, extra: dict
) -> tuple[dict, str, int]:
    """Run decide once. Returns (result json, stderr, stub call count)."""
    if sentinel.exists():
        sentinel.unlink()
    proc = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(root), "decide"],
        input=json.dumps(
            {
                "question": "Should the docs-only change land?",
                "context": "low risk",
                "high_blast": False,
            }
        ),
        capture_output=True,
        text=True,
        env=hermetic_env(stub_dir, extra),
        cwd=str(cwd),
        timeout=120,
    )
    try:
        res = json.loads(proc.stdout)
    except Exception:
        res = {}
    calls = len(sentinel.read_text().splitlines()) if sentinel.exists() else 0
    return res, proc.stderr, calls


def load_engine():
    spec = importlib.util.spec_from_file_location("thing_decide_under_test", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    print("── Gate 303 (decide half): THING_DECIDE_* test-hook source gate ──")
    if not ENGINE.is_file():
        print(f"FATAL: engine not found at {ENGINE}")
        return 2

    with tempfile.TemporaryDirectory() as tdir:
        base = Path(tdir)
        stub_dir = base / "stub"
        stub_dir.mkdir()
        sentinel = base / "stub-calls"
        stub = stub_dir / "claude"
        envelope = json.dumps(
            {
                "type": "result",
                "is_error": False,
                "result": json.dumps(
                    {
                        "verdict": "no",
                        "concerns_cited": [],
                        "reasoning": "STUB-REAL-SEAT",
                        "confidence": 0.9,
                        "injection_detected": False,
                    }
                ),
            }
        )
        stub.write_text(
            f"#!/usr/bin/env bash\necho call >>'{sentinel}'\nprintf '%s' '{envelope}'\n",
            encoding="utf-8",
        )
        stub.chmod(0o755)
        elsewhere = base / "elsewhere"
        elsewhere.mkdir()

        clean = make_project(base, "clean", settings='{"permissions":{}}')
        planted = make_project(
            base,
            "planted",
            settings=json.dumps(
                {"env": {"THING_DECIDE_MOCK_VERDICT": "yes", "THING_DECIDE_ALLOW_MOCK": "1"}}
            ),
        )
        planted_local = make_project(
            base,
            "plantedlocal",
            settings='{"env":{"FOO":"1"}}',
            local='{"env":{"THING_DECIDE_MOCK_VERDICT":"yes"}}',
        )
        mark_only = make_project(
            base, "markonly", settings='{"env":{"THING_DECIDE_ALLOW_MOCK":"1"}}'
        )
        malformed = make_project(
            base, "malformed", settings='{"env":{"THING_DECIDE_MOCK_VERDICT":"yes",'
        )
        empty = make_project(base, "empty", settings="")
        env_list = make_project(base, "envlist", settings='{"env":["THING_DECIDE_MOCK_VERDICT"]}')
        unrelated = make_project(
            base,
            "unrelated",
            settings=json.dumps(
                {
                    "env": {
                        "THING_OTHER": "x",
                        "MY_THING_DECIDE_X": "y",
                        "RAVENCLAUDE_TEAM_MODE": "1",
                    }
                }
            ),
        )

        harness = {"THING_DECIDE_ALLOW_MOCK": "1", "THING_DECIDE_MOCK_VERDICT": "yes"}
        # What Claude Code does with a planted env block: export it into the hook process.
        planted_export = {"THING_DECIDE_ALLOW_MOCK": "1", "THING_DECIDE_MOCK_VERDICT": "yes"}

        def case(
            label,
            root,
            extra,
            want_verdict,
            want_calls=None,
            want_gate=None,
            cwd=None,
            project_env=True,
        ):
            env = dict(extra)
            if project_env:
                env["CLAUDE_PROJECT_DIR"] = str(root)
            res, err, calls = run(stub_dir, sentinel, root, cwd or elsewhere, env)
            got = res.get("verdict")
            gate = res.get("mock_gate", "none")
            problems = []
            if got != want_verdict:
                problems.append(f"verdict={got!r} want {want_verdict!r}")
            if want_calls is not None and (calls > 0) != want_calls:
                problems.append(f"stub calls={calls} want {'>0' if want_calls else '0'}")
            if want_gate is not None and gate != want_gate:
                problems.append(f"mock_gate={gate!r} want {want_gate!r}")
            if problems:
                bad(
                    f"{label}: "
                    + "; ".join(problems)
                    + (f" | stderr: {err.strip()[:200]}" if err else "")
                )
            else:
                ok(f"{label} -> {got} (mock_gate={gate}, stub calls={calls})")

        # Positive controls: the guard must not break the sanctioned harness path.
        case(
            "control: clean project + marker + mock=yes honoured",
            clean,
            harness,
            "yes",
            False,
            "honour",
        )
        case(
            "control: unrelated env keys are not a plant",
            unrelated,
            harness,
            "yes",
            False,
            "honour",
        )
        case("control: no mock set -> real seats run", clean, {}, "no", True, None)
        # The marker is required.
        case(
            "unmarked mock=yes ignored -> real seats",
            clean,
            {"THING_DECIDE_MOCK_VERDICT": "yes"},
            "no",
            True,
            "unmarked",
        )
        # A project plant is ignored, and fails closed when unreadable.
        case(
            "planted settings.json -> mock ignored, real seats",
            planted,
            planted_export,
            "no",
            True,
            "planted",
        )
        case(
            "planted settings.local.json -> mock ignored",
            planted_local,
            planted_export,
            "no",
            True,
            "planted",
        )
        case(
            "marker-only plant also disarms the harness mock",
            mark_only,
            harness,
            "no",
            True,
            "planted",
        )
        case(
            "malformed settings.json -> fail closed (planted)",
            malformed,
            harness,
            "no",
            True,
            "planted",
        )
        case("empty settings.json -> fail closed (planted)", empty, harness, "no", True, "planted")
        case(
            "non-object env block -> fail closed (planted)",
            env_list,
            harness,
            "no",
            True,
            "planted",
        )
        # --root is screened even without CLAUDE_PROJECT_DIR (route-decision-review passes --root).
        case(
            "--root plant screened with no CLAUDE_PROJECT_DIR",
            planted,
            planted_export,
            "no",
            True,
            "planted",
            project_env=False,
        )
        # Live session: only defer-producing mocks; a yes/no mock makes every seat abstain.
        case(
            "live (CLAUDECODE) mock=yes -> seats abstain -> defer",
            clean,
            {**harness, "CLAUDECODE": "1"},
            "defer",
            False,
            "live-refused",
        )
        case(
            "live (THING_DECIDE_LIVE_SESSION) mock=yes -> defer",
            clean,
            {**harness, "THING_DECIDE_LIVE_SESSION": "1"},
            "defer",
            False,
            "live-refused",
        )
        case(
            "live mock=split refused (it would resolve 'no')",
            clean,
            {
                "THING_DECIDE_ALLOW_MOCK": "1",
                "THING_DECIDE_MOCK_VERDICT": "split",
                "CLAUDECODE": "1",
            },
            "defer",
            False,
            "live-refused",
        )
        case(
            "live mock=abstain still honoured (defer-producing)",
            clean,
            {
                "THING_DECIDE_ALLOW_MOCK": "1",
                "THING_DECIDE_MOCK_VERDICT": "abstain",
                "CLAUDECODE": "1",
            },
            "defer",
            False,
            "honour",
        )

        # The eval mock follows the same rules (unit level: the gate's effective values).
        mod = load_engine()
        saved = dict(os.environ)
        try:

            def gate_for(extra: dict, root: Path) -> dict:
                os.environ.clear()
                os.environ.update(
                    hermetic_env(stub_dir, {"CLAUDE_PROJECT_DIR": str(root), **extra})
                )
                mod._MOCK_GATE_CACHE.clear()
                mod._MOCK_GATE_ROOT = None
                return mod._mock_gate()

            g = gate_for(
                {"THING_DECIDE_ALLOW_MOCK": "1", "THING_DECIDE_MOCK_EVAL": "downgrade"}, clean
            )
            (ok if g["eval"] == "downgrade" else bad)(
                f"eval mock honoured with marker (got {g['eval']!r})"
            )
            g = gate_for({"THING_DECIDE_MOCK_EVAL": "downgrade"}, clean)
            (ok if g["eval"] is None else bad)(
                f"eval mock refused without marker (got {g['eval']!r})"
            )
            g = gate_for(
                {
                    "THING_DECIDE_ALLOW_MOCK": "1",
                    "THING_DECIDE_MOCK_EVAL": "downgrade",
                    "CLAUDECODE": "1",
                },
                clean,
            )
            (ok if g["eval"] is None else bad)(
                f"eval mock dropped under a live session (got {g['eval']!r})"
            )
            g = gate_for(
                {"THING_DECIDE_ALLOW_MOCK": "1", "THING_DECIDE_MOCK_EVAL": "downgrade"}, planted
            )
            unset = all(k not in os.environ for k in mod._DECIDE_TEST_HOOKS)
            (ok if g["eval"] is None and unset else bad)(
                f"planted: eval mock ignored and every THING_DECIDE_* hook unset (eval={g['eval']!r}, unset={unset})"
            )

            # Teeth: with the planted-file check neutered, the planted attack resolves "yes".
            # Proves the "planted -> no" assertions above are measuring the guard.
            orig = mod._planted_settings_file
            mod._planted_settings_file = lambda roots: None
            try:
                os.environ.clear()
                os.environ.update(
                    hermetic_env(stub_dir, {"CLAUDE_PROJECT_DIR": str(planted), **planted_export})
                )
                mod._MOCK_GATE_CACHE.clear()
                res = mod.decide(planted, "Should the docs-only change land?", "low risk", False)
            finally:
                mod._planted_settings_file = orig
            (ok if res.get("verdict") == "yes" else bad)(
                f"teeth: neutered plant check lets the planted mock resolve 'yes' (got {res.get('verdict')!r})"
            )
        finally:
            os.environ.clear()
            os.environ.update(saved)

    print(f"  ── Gate 303 (decide half): {PASS} passed, {FAIL} failed ──")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
