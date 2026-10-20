#!/usr/bin/env python3
"""check-review-2026-10-20-scripts.py - regression cases for review package PK-4.

One case per finding from the 2026-10-20 repo review that landed in the marketplace root
scripts, the Power Platform skills/hooks and the generative-web-media plugin. Findings
whose regression lives in an existing test file (the managed-import and nudge-preflight
shell tests, check-hook-launch-line.py --self-test) are NOT repeated here.

Every case drives the real script as a subprocess against a throwaway fixture, so a
case passes only if the shipped behaviour is right. Stdlib only.

Usage:
  check-review-2026-10-20-scripts.py                 run every case
  check-review-2026-10-20-scripts.py --only A-20,A-4 run a subset
  check-review-2026-10-20-scripts.py --list          list the case ids
  check-review-2026-10-20-scripts.py --root DIR      resolve every target file under DIR
                                                     instead of the repo (used to prove
                                                     a case fails against a pre-fix tree)

Exit 0 = every selected case passed, 1 = at least one failed, 2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO
CASES: dict[str, object] = {}


def case(finding_id: str):
    def deco(fn):
        CASES[finding_id] = fn
        return fn

    return deco


def target(rel: str) -> str:
    return str(ROOT / rel)


def run(
    cmd: list[str], *, cwd: str | None = None, env: dict | None = None, stdin: str | None = None
):
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=full_env,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=120,
    )


def expect(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def describe(r: subprocess.CompletedProcess) -> str:
    return f"rc={r.returncode} stdout={r.stdout[-400:]!r} stderr={r.stderr[-400:]!r}"


# --------------------------------------------------------------------------------------
# generative-web-media: gen-budget.py
# --------------------------------------------------------------------------------------
GEN_BUDGET = "plugins/generative-web-media/scripts/gen-budget.py"


@case("A-20")
def case_a20() -> None:
    """Budget guard must not fail open on NaN prices, NaN lines or a NaN budget."""
    with tempfile.TemporaryDirectory() as td:
        ledger = os.path.join(td, "spend.jsonl")
        base = ["python3", target(GEN_BUDGET)]

        r = run(
            base
            + ["add", "--ledger", ledger, "--model", "m", "--unit-price", "nan", "--count", "1"]
        )
        expect(r.returncode != 0, f"add --unit-price nan must fail loudly: {describe(r)}")
        expect(
            not os.path.exists(ledger) or "NaN" not in Path(ledger).read_text(),
            "add --unit-price nan must not write a NaN line to the ledger",
        )
        r = run(
            base
            + ["add", "--ledger", ledger, "--model", "m", "--unit-price", "inf", "--count", "0"]
        )
        expect(r.returncode != 0, f"add --unit-price inf must fail loudly: {describe(r)}")

        # A good line and a $500 line, then status against a $25 budget must be OVER.
        for price, count in (("0.055", "8"), ("100", "5")):
            r = run(
                base
                + [
                    "add",
                    "--ledger",
                    ledger,
                    "--model",
                    "m",
                    "--unit-price",
                    price,
                    "--count",
                    count,
                ]
            )
            expect(r.returncode == 0, f"valid add failed: {describe(r)}")
        r = run(base + ["status", "--ledger", ledger, "--budget", "25"])
        expect(r.returncode != 0, f"over-budget status must exit non-zero: {describe(r)}")
        r = run(base + ["status", "--ledger", ledger, "--budget", "nan"])
        expect(r.returncode != 0, f"--budget nan must fail loudly, not report ok: {describe(r)}")
        r = run(base + ["status", "--ledger", ledger, "--budget", "inf"])
        expect(r.returncode != 0, f"--budget inf must fail loudly: {describe(r)}")

        # A pre-existing poisoned line (written by an older version) must fail status loudly.
        poisoned = os.path.join(td, "poisoned.jsonl")
        Path(poisoned).write_text(
            '{"tier": "draft", "line_cost": 0.44}\n'
            '{"tier": "draft", "line_cost": NaN}\n'
            '{"tier": "final", "line_cost": 500.0}\n'
        )
        r = run(base + ["status", "--ledger", poisoned, "--budget", "25"])
        expect(r.returncode != 0, f"a NaN line_cost must fail status: {describe(r)}")
        expect(
            '"over_budget": false' not in r.stdout,
            f"must not report over_budget false: {describe(r)}",
        )
        for bad in ('"abc"', "null", "true"):
            Path(poisoned).write_text('{"tier": "draft", "line_cost": %s}\n' % bad)
            r = run(base + ["status", "--ledger", poisoned, "--budget", "25"])
            expect(
                r.returncode != 0, f"non-numeric line_cost {bad} must fail status: {describe(r)}"
            )
            expect(
                "Traceback" not in r.stderr,
                f"non-numeric line_cost {bad} must not traceback: {describe(r)}",
            )

        # Control: a clean ledger under budget still passes.
        clean = os.path.join(td, "clean.jsonl")
        r = run(
            base
            + ["add", "--ledger", clean, "--model", "m", "--unit-price", "0.055", "--count", "8"]
        )
        expect(r.returncode == 0, f"clean add failed: {describe(r)}")
        r = run(base + ["status", "--ledger", clean, "--budget", "25"])
        expect(r.returncode == 0, f"clean ledger under budget must pass: {describe(r)}")
        expect(json.loads(r.stdout)["over_budget"] is False, f"clean ledger: {describe(r)}")


# --------------------------------------------------------------------------------------
# generative-web-media: provenance.py
# --------------------------------------------------------------------------------------
PROVENANCE = "plugins/generative-web-media/scripts/provenance.py"


def _prov_record(ledger: str, model: str, *, license_: str = "commercial", client: bool = True):
    cmd = ["python3", target(PROVENANCE), "record", "--ledger", ledger, "--asset", "media/a.avif"]
    cmd += ["--prompt", "p", "--model", model, "--provider", "fal", "--license", license_]
    cmd += ["--indemnity", "none"]
    if client:
        cmd.append("--client")
    return run(cmd)


def _prov_audit(ledger: str):
    return run(["python3", target(PROVENANCE), "audit", "--ledger", ledger])


@case("A-4")
def case_a4() -> None:
    """The FLUX-dev trap detector must catch every common spelling of the dev mode."""
    dev_spellings = [
        "FLUX.1 [dev]",
        "flux-1-dev",
        "flux_dev",
        "fal-ai/flux-kontext/dev",
        "fal-ai/flux-1/dev",
        "FLUX.1 dev",
        "flux dev",
        "black-forest-labs/FLUX.1-dev",
        "flux1-dev",
        "fal-ai/flux-2/dev",
    ]
    ok_models = [
        "flux-schnell",
        "FLUX.1 [pro]",
        "fal-ai/flux-kontext-pro",
        "flux-pro-1.1",
        "grok-image",
    ]
    with tempfile.TemporaryDirectory() as td:
        for i, model in enumerate(dev_spellings):
            ledger = os.path.join(td, f"dev{i}.jsonl")
            expect(_prov_record(ledger, model).returncode == 0, f"record failed for {model!r}")
            r = _prov_audit(ledger)
            expect(
                r.returncode == 1 and "AUDIT FAILED" in r.stderr,
                f"FLUX-dev spelling {model!r} on a client asset must FAIL the audit: {describe(r)}",
            )
        for i, model in enumerate(ok_models):
            ledger = os.path.join(td, f"ok{i}.jsonl")
            expect(_prov_record(ledger, model).returncode == 0, f"record failed for {model!r}")
            r = _prov_audit(ledger)
            expect(
                r.returncode == 0,
                f"{model!r} is not a dev/non-commercial model, must pass: {describe(r)}",
            )
        # The existing license-field marker still works, and a recorded override still downgrades.
        ledger = os.path.join(td, "lic.jsonl")
        _prov_record(ledger, "some-model", license_="FLUX.1 [dev] Non-Commercial License")
        expect(
            _prov_audit(ledger).returncode == 1, "a non-commercial license string must still fail"
        )
        ledger = os.path.join(td, "override.jsonl")
        cmd = ["python3", target(PROVENANCE), "record", "--ledger", ledger, "--asset", "a.avif"]
        cmd += ["--prompt", "p", "--model", "FLUX.1 [dev]", "--provider", "bfl", "--license"]
        cmd += ["commercial", "--indemnity", "none", "--client", "--override", "paid BFL API"]
        expect(run(cmd).returncode == 0, "record with override failed")
        r = _prov_audit(ledger)
        expect(
            r.returncode == 0 and "OVERRIDDEN" in r.stderr,
            f"override must warn, not fail: {describe(r)}",
        )


# --------------------------------------------------------------------------------------
# generative-web-media: optimize-image.mjs
# --------------------------------------------------------------------------------------
OPTIMIZE = "plugins/generative-web-media/scripts/web-optimize/optimize-image.mjs"
STUB_SHARP = (
    'module.exports = function sharp() { process.stderr.write("STUB-SHARP-CALLED\\n");'
    " process.exit(42); };\n"
)


def _write_stub_sharp(node_modules: str) -> None:
    d = Path(node_modules) / "sharp"
    d.mkdir(parents=True, exist_ok=True)
    (d / "package.json").write_text('{"name":"sharp","version":"0.0.0","main":"index.js"}\n')
    (d / "index.js").write_text(STUB_SHARP)


def _path_without_node_modules_bin() -> str:
    keep = [
        e
        for e in os.environ.get("PATH", "").split(os.pathsep)
        if not e.rstrip("/\\").replace("\\", "/").endswith("node_modules/.bin")
    ]
    return os.pathsep.join(keep)


@case("A-3")
def case_a3() -> None:
    """`npx --package=sharp node optimize-image.mjs` must find the npx-installed sharp."""
    expect(
        run(["node", "--version"]).returncode == 0,
        "node is required for this case; its absence is a failure, not a pass",
    )
    with tempfile.TemporaryDirectory() as td:
        script_dir = os.path.join(td, "script")
        os.makedirs(script_dir)
        script = os.path.join(script_dir, "optimize-image.mjs")
        Path(script).write_text(Path(target(OPTIMIZE)).read_text())
        work = os.path.join(td, "work")
        os.makedirs(work)
        Path(work, "in.png").write_text("not a real png - the stub never reads it")
        args = ["node", script, "--in", "in.png", "--outdir", "out", "--name", "hero"]
        clean_path = _path_without_node_modules_bin()

        def hit(r: subprocess.CompletedProcess) -> bool:
            return "STUB-SHARP-CALLED" in r.stderr and r.returncode == 42

        # (3) the layout `npx --package=sharp` makes: <cache>/node_modules/.bin on PATH.
        npx = os.path.join(td, "npx")
        os.makedirs(os.path.join(npx, "node_modules", ".bin"))
        _write_stub_sharp(os.path.join(npx, "node_modules"))
        npx_path = os.path.join(npx, "node_modules", ".bin") + os.pathsep + clean_path
        r = run(args, cwd=work, env={"PATH": npx_path})
        expect(hit(r), f"sharp under a PATH node_modules/.bin must resolve: {describe(r)}")
        expect("LOUD-SKIP" not in r.stderr, f"must not LOUD-SKIP: {describe(r)}")

        # (1) $SHARP_DIR (a project dir holding node_modules/sharp).
        shdir = os.path.join(td, "shdir")
        _write_stub_sharp(os.path.join(shdir, "node_modules"))
        r = run(args, cwd=work, env={"PATH": clean_path, "SHARP_DIR": shdir})
        expect(hit(r), f"$SHARP_DIR must resolve sharp: {describe(r)}")

        # (2) the current directory.
        proj = os.path.join(td, "proj")
        os.makedirs(proj)
        _write_stub_sharp(os.path.join(proj, "node_modules"))
        Path(proj, "in.png").write_text("x")
        r = run(args, cwd=proj, env={"PATH": clean_path})
        expect(hit(r), f"cwd node_modules must resolve sharp: {describe(r)}")

        # Control: sharp nowhere -> LOUD-SKIP, exit 1, unchanged.
        nowhere = {"PATH": clean_path, "SHARP_DIR": os.path.join(td, "nowhere")}
        r = run(args, cwd=work, env=nowhere)
        expect(r.returncode == 1, f"no sharp anywhere must still exit 1: {describe(r)}")
        expect("LOUD-SKIP" in r.stderr, f"no sharp anywhere must still LOUD-SKIP: {describe(r)}")
        expect("STUB-SHARP-CALLED" not in r.stderr, f"control run reached the stub: {describe(r)}")


def main() -> int:
    global ROOT
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--only", help="comma-separated finding ids to run")
    ap.add_argument("--list", action="store_true", help="list case ids and exit")
    ap.add_argument("--root", help="resolve every target file under this directory")
    args = ap.parse_args()

    if args.list:
        for fid in CASES:
            print(fid)
        return 0
    if args.root:
        ROOT = Path(args.root).resolve()
    selected = list(CASES)
    if args.only:
        selected = [s.strip() for s in args.only.split(",") if s.strip()]
        unknown = [s for s in selected if s not in CASES]
        if unknown:
            sys.stderr.write(f"unknown case id(s): {', '.join(unknown)}\n")
            return 2

    failed = 0
    for fid in selected:
        try:
            CASES[fid]()  # type: ignore[operator]
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {fid}: {exc}")
        except Exception as exc:  # a crashing case is a failing case, never a silent pass
            failed += 1
            print(f"FAIL {fid}: case crashed: {type(exc).__name__}: {exc}")
        else:
            print(f"PASS {fid}")
    print(f"{len(selected) - failed}/{len(selected)} cases passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
