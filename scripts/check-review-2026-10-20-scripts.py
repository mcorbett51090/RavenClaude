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


@case("A-5")
def case_a5() -> None:
    """`audit --dir media` must not fail a gen-budget spend ledger as missing provenance."""
    with tempfile.TemporaryDirectory() as td:
        media = os.path.join(td, "media")
        expect(
            _prov_record(os.path.join(media, "provenance.jsonl"), "grok-image").returncode == 0,
            "record",
        )
        spend = os.path.join(media, "spend.jsonl")
        r = run(
            ["python3", target(GEN_BUDGET), "add", "--ledger", spend, "--model", "m"]
            + ["--unit-price", "0.055", "--count", "8"]
        )
        expect(r.returncode == 0, f"gen-budget add failed: {describe(r)}")
        audit = ["python3", target(PROVENANCE), "audit", "--dir", media]
        r = run(audit)
        expect(
            r.returncode == 0,
            f"provenance + spend ledger side by side must audit ok: {describe(r)}",
        )
        expect(
            "skipped (gen-budget spend ledger)" in r.stderr and "spend.jsonl" in r.stderr,
            f"the skipped spend ledger must be listed on stderr: {describe(r)}",
        )

        # Fail-closed: only a RECOGNISABLE spend ledger is skipped.
        bad = os.path.join(td, "bad")
        os.makedirs(bad)
        Path(bad, "ledger.jsonl").write_text("this is not json\n")
        r = run(["python3", target(PROVENANCE), "audit", "--dir", bad])
        expect(
            r.returncode == 1,
            f"a malformed ledger.jsonl must still be audited and fail: {describe(r)}",
        )
        mixed = os.path.join(td, "mixed")
        os.makedirs(mixed)
        Path(mixed, "ledger.jsonl").write_text('{"line_cost": 1.0}\n{"model": "grok-image"}\n')
        r = run(["python3", target(PROVENANCE), "audit", "--dir", mixed])
        expect(
            r.returncode == 1,
            f"a half-spend, half-unknown file must still be audited: {describe(r)}",
        )
        has_asset = os.path.join(td, "has_asset")
        os.makedirs(has_asset)
        Path(has_asset, "spend.jsonl").write_text('{"asset": "a.avif", "line_cost": 1.0}\n')
        r = run(["python3", target(PROVENANCE), "audit", "--dir", has_asset])
        expect(
            r.returncode == 1,
            f"an entry that names an asset is provenance, not spend: {describe(r)}",
        )
        only_spend = os.path.join(td, "only_spend")
        os.makedirs(only_spend)
        Path(only_spend, "spend.jsonl").write_text(Path(spend).read_text())
        r = run(["python3", target(PROVENANCE), "audit", "--dir", only_spend])
        expect(
            r.returncode == 1,
            f"a dir holding only spend ledgers has no provenance to audit: {describe(r)}",
        )


# --------------------------------------------------------------------------------------
# workflow hygiene gate + its scaffold template (D-2)
# --------------------------------------------------------------------------------------
HYGIENE = ".github/scripts/check-workflow-hygiene.py"
HYGIENE_TEMPLATE = (
    "plugins/ravenclaude-core/templates/agent-ready-repo/check-workflow-hygiene.py.template"
)
_WF_HEAD = "name: x\non:\n  push:\n"
_WF_JOB = "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
_SHA = "a" * 40


@case("D-2")
def case_d2() -> None:
    """Rule 1 must fail `permissions: write-all`; quoted `uses:` values must classify correctly."""
    expect(
        Path(target(HYGIENE)).read_bytes() == Path(target(HYGIENE_TEMPLATE)).read_bytes(),
        "the gate script and its scaffold template must stay byte-identical",
    )
    fixtures = {
        "write-all": (_WF_HEAD + "permissions: write-all\n" + _WF_JOB + "      - run: echo\n", 1),
        "write-all-quoted": (
            _WF_HEAD + "permissions: 'write-all' # why\n" + _WF_JOB + "      - run: echo\n",
            1,
        ),
        "quoted-unpinned": (
            _WF_HEAD + "permissions: {}\n" + _WF_JOB + '      - uses: "someorg/act@v1"\n',
            1,
        ),
        "read-all": (_WF_HEAD + "permissions: read-all\n" + _WF_JOB + "      - run: echo\n", 0),
        "contents-write": (
            _WF_HEAD + "permissions:\n  contents: write\n" + _WF_JOB + "      - run: echo\n",
            0,
        ),
        "quoted-official-local": (
            _WF_HEAD
            + "permissions: {}\n"
            + _WF_JOB
            + "      - uses: 'actions/checkout@v4'\n      - uses: \"./.github/actions/x\"\n",
            0,
        ),
        "quoted-pinned": (
            _WF_HEAD + "permissions: {}\n" + _WF_JOB + f'      - uses: "someorg/act@{_SHA}"\n',
            0,
        ),
    }
    for which in (HYGIENE, HYGIENE_TEMPLATE):
        for name, (content, want_rc) in fixtures.items():
            with tempfile.TemporaryDirectory() as td:
                Path(td, f"{name}.yml").write_text(content)
                r = run(["python3", target(which), td])
            expect(
                r.returncode == want_rc,
                f"{Path(which).name} on '{name}': want rc {want_rc}: {describe(r)}",
            )
            if name == "quoted-unpinned":
                expect(
                    "`someorg/act@v1`" in r.stdout,
                    f"finding must name the unquoted ref: {describe(r)}",
                )
    # The real workflows still pass.
    r = run(["python3", target(HYGIENE), str(REPO / ".github" / "workflows")])
    expect(
        r.returncode == 0 and "ERROR" not in r.stdout,
        f".github/workflows must still pass: {describe(r)}",
    )


# --------------------------------------------------------------------------------------
# check-github-status.sh (D-3)
# --------------------------------------------------------------------------------------
GH_STATUS = "scripts/check-github-status.sh"
# A fake `curl` that writes a fixture to the -o file. With the fixture "HTTP503" it behaves
# like real curl: without -f/--fail it writes the 503 error body and exits 0; with -f it
# exits 22 and writes nothing.
FAKE_CURL = """#!/usr/bin/env python3
import os, sys
args = sys.argv[1:]
out = args[args.index("-o") + 1] if "-o" in args else None
fail = any(a == "--fail" or (a.startswith("-") and not a.startswith("--") and "f" in a) for a in args)
fixture = os.environ["FAKE_CURL_BODY"]
if fixture == "HTTP503":
    if fail:
        sys.exit(22)
    body = '{"message": "Service Unavailable"}'
else:
    body = fixture
if out:
    open(out, "w").write(body)
"""


def _gh_status(body: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as td:
        shim = Path(td, "curl")
        shim.write_text(FAKE_CURL)
        shim.chmod(0o755)
        env = {"PATH": td + os.pathsep + os.environ.get("PATH", ""), "FAKE_CURL_BODY": body}
        return run(["bash", target(GH_STATUS)], env=env)


def _incident(name: str, components=None, affected=None) -> dict:
    return {
        "name": name,
        "status": "investigating",
        "impact": "major",
        "created_at": "2026-10-20T00:00:00Z",
        "components": components if components is not None else [],
        "incident_updates": [
            {
                "created_at": "2026-10-20T00:01:00Z",
                "body": "looking",
                "affected_components": affected,
            }
        ],
    }


@case("D-3")
def case_d3() -> None:
    """An open Actions incident with no component data must not print a green check."""
    r = _gh_status(json.dumps({"incidents": [_incident("Incident with Actions")]}))
    expect(r.returncode == 0, f"the script is advisory and must exit 0: {describe(r)}")
    expect("Incident with Actions" in r.stdout, f"the incident must be printed: {describe(r)}")
    expect("✓" not in r.stdout, f"no green check for an open Actions incident: {describe(r)}")
    expect("LIVE INCIDENT" in r.stdout, f"a name that mentions Actions is relevant: {describe(r)}")

    # An incident with an unrelated name and no component data is still surfaced.
    r = _gh_status(json.dumps({"incidents": [_incident("Degraded performance somewhere")]}))
    expect(
        "✓" not in r.stdout and "unattributed - may affect you" in r.stdout,
        f"unattributed incident hidden: {describe(r)}",
    )

    # Component association via `components` OR `affected_components` still reads as LIVE.
    for inc in (
        _incident("Disruption", affected=[{"name": "Actions"}]),
        _incident("Disruption", components=[{"name": "Git Operations"}]),
    ):
        r = _gh_status(json.dumps({"incidents": [inc]}))
        expect(
            "LIVE INCIDENT" in r.stdout and "✓" not in r.stdout,
            f"attributed incident: {describe(r)}",
        )

    # An attributed incident for an unrelated component is correctly not alarming.
    r = _gh_status(
        json.dumps({"incidents": [_incident("Codespaces slow", affected=[{"name": "Codespaces"}])]})
    )
    expect("✓" in r.stdout and "none affecting" in r.stdout, f"unrelated incident: {describe(r)}")
    r = _gh_status(json.dumps({"incidents": []}))
    expect("no unresolved incidents" in r.stdout, f"empty incident list: {describe(r)}")

    # A body that is not a dict with an 'incidents' list is UNKNOWN, never clean.
    for body in ('["x"]', '{"message": "Service Unavailable"}', '{"incidents": null}', "not json"):
        r = _gh_status(body)
        expect(
            "UNKNOWN" in r.stdout and "✓" not in r.stdout,
            f"body {body!r} must be UNKNOWN: {describe(r)}",
        )
    # curl must be run with -f so an HTTP error is UNKNOWN, not an empty/clean body.
    r = _gh_status("HTTP503")
    expect(
        "UNKNOWN" in r.stderr + r.stdout and "✓" not in r.stdout,
        f"HTTP 503 must be UNKNOWN: {describe(r)}",
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
