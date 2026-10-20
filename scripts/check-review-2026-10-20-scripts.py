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
import importlib.util
import json
import os
import re
import shutil
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
    cmd: list[str],
    *,
    cwd: str | None = None,
    env: dict | None = None,
    stdin: str | None = None,
    drop: tuple[str, ...] = (),
):
    full_env = dict(os.environ)
    for name in drop:
        full_env.pop(name, None)
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


@case("A-33")
def case_a33() -> None:
    """A required provenance field only counts as present when it is a non-blank string."""
    good = {
        "asset": "media/a.avif",
        "prompt": "p",
        "model": "grok-image",
        "provider": "xai",
        "license": "commercial",
        "indemnity": "none",
    }
    with tempfile.TemporaryDirectory() as td:
        ledger = os.path.join(td, "ok.jsonl")
        Path(ledger).write_text(json.dumps(good) + "\n")
        r = _prov_audit(ledger)
        expect(r.returncode == 0, f"control: a complete entry must pass: {describe(r)}")

        for label, patch in {
            "null asset + prompt": {"asset": None, "prompt": None},
            "empty list": {"license": []},
            "empty object": {"provider": {}},
            "number": {"indemnity": 0},
            "boolean": {"model": False},
            "blank string": {"prompt": "   "},
        }.items():
            bad = os.path.join(td, "bad.jsonl")
            Path(bad).write_text(json.dumps({**good, **patch}) + "\n")
            r = _prov_audit(bad)
            expect(
                r.returncode == 1 and "AUDIT FAILED" in r.stderr,
                f"{label}: a non-string / blank required field is missing provenance: {describe(r)}",
            )
            field = next(iter(patch))
            expect(
                f"missing provenance field '{field}'" in r.stderr,
                f"{label}: the finding must name '{field}': {describe(r)}",
            )
        # The finding must not call a null asset 'None'.
        Path(td, "nul.jsonl").write_text(json.dumps({**good, "asset": None}) + "\n")
        r = _prov_audit(os.path.join(td, "nul.jsonl"))
        expect("None —" not in r.stderr, f"a null asset must not be named 'None': {describe(r)}")


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
# gh-health.py status-page probe (D-4)
# --------------------------------------------------------------------------------------
GH_HEALTH = "scripts/gh-health.py"


def _load_module(rel: str, name: str):
    """Import a hyphen-named script by path (registered in sys.modules so dataclasses work)."""
    spec = importlib.util.spec_from_file_location(name, target(rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@case("D-4")
def case_d4() -> None:
    """The status probe must treat a 200 body of the wrong shape as UNKNOWN, and never crash."""
    gh = _load_module(GH_HEALTH, "gh_health_under_test")
    green = {
        "status": gh.GREEN_STATUS,
        "components": gh.OK_COMPONENTS,
        "incidents": gh.NO_INCIDENTS,
    }

    def probe(**override):
        return gh.probe_status_page(gh.FakeTransport(**{**green, **override}))

    p = probe()
    expect(
        (p.state, p.finding) == (gh.RAN, gh.CLEAN), f"control: valid green is RAN/clean: {p.state}"
    )
    p = probe(incidents=gh.AN_INCIDENT)
    expect(
        (p.state, p.finding) == (gh.RAN, gh.DEGRADED),
        f"control: a real incident: {p.state}/{p.finding}",
    )

    bad_bodies = {
        "incidents: null": {"incidents": {"incidents": None}},
        "incidents: {}": {"incidents": {}},
        "incidents: message body": {"incidents": {"message": "Service Unavailable"}},
        "incidents: a bare list": {"incidents": []},
        "components: {}": {"components": {}},
        "components: null": {"components": {"components": None}},
        "status: {}": {"status": {}},
        "status: no indicator": {"status": {"status": {"description": "x"}}},
        "status: indicator not a str": {"status": {"status": {"indicator": None}}},
    }
    for label, override in bad_bodies.items():
        try:
            p = probe(**override)
        except Exception as exc:  # the old behaviour for 'incidents: null' was a TypeError
            raise AssertionError(
                f"{label}: probe crashed with {type(exc).__name__}: {exc}"
            ) from exc
        expect(
            p.state == gh.FAILED,
            f"{label}: a wrongly-shaped 200 must be a FAILED (UNKNOWN) probe, got {p.state}/{p.finding}",
        )
        expect(
            "unexpected status-page shape" in p.reason, f"{label}: reason says why: {p.reason!r}"
        )


# --------------------------------------------------------------------------------------
# worktree-new.sh (D-6)
# --------------------------------------------------------------------------------------
WORKTREE_NEW = "scripts/worktree-new.sh"
GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX")


@case("D-6")
def case_d6() -> None:
    """Attaching to a stale agent/<slug> branch must warn loudly and report the real tip."""
    with tempfile.TemporaryDirectory() as td:
        repo = os.path.join(td, "repo")
        os.makedirs(repo)

        def git(*a: str) -> subprocess.CompletedProcess:
            ident = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
            r = run(["git", *ident, "-c", "commit.gpgsign=false", *a], cwd=repo, drop=GIT_ENV)
            expect(r.returncode == 0, f"git {' '.join(a)} failed: {describe(r)}")
            return r

        git("init", "-q")
        git("symbolic-ref", "HEAD", "refs/heads/main")
        Path(repo, "a.txt").write_text("a\n")
        git("add", "a.txt")
        git("commit", "-q", "-m", "one")
        old_sha = git("rev-parse", "--short", "HEAD").stdout.strip()
        git("branch", "agent/job1")  # a stale branch left behind by an earlier, cleaned swarm
        for name in ("b.txt", "c.txt"):
            Path(repo, name).write_text("x\n")
            git("add", name)
            git("commit", "-q", "-m", name)

        r = run(["bash", target(WORKTREE_NEW), "job1", "main"], cwd=repo, drop=GIT_ENV)
        out = r.stdout + r.stderr
        expect(
            r.returncode == 0, f"attaching must still succeed (warn, do not fail): {describe(r)}"
        )
        expect("WARNING" in out, f"a loud WARNING is required: {out!r}")
        expect(old_sha in out, f"the existing tip sha {old_sha} must be reported: {out!r}")
        expect("2 commit(s) behind" in out, f"how far behind base must be reported: {out!r}")
        expect(
            "attached to existing branch agent/job1" in out, f"report must say attached: {out!r}"
        )
        expect("base:   main" not in out, f"must not claim a base it did not use: {out!r}")
        expect(
            not Path(repo, ".claude", "worktrees", "job1", "c.txt").exists(),
            "(sanity) the worktree really is on the stale tip, without main's newer files",
        )

        # Control: a fresh slug is created from the base and still reports it, with no warning.
        r = run(["bash", target(WORKTREE_NEW), "job2", "main"], cwd=repo, drop=GIT_ENV)
        out = r.stdout + r.stderr
        expect(r.returncode == 0, f"fresh slug failed: {describe(r)}")
        expect("base:   main" in out and "WARNING" not in out, f"fresh slug report: {out!r}")
        expect(
            Path(repo, ".claude", "worktrees", "job2", "c.txt").exists(),
            "(sanity) a fresh worktree is on main's tip",
        )


# --------------------------------------------------------------------------------------
# Power Platform PostToolUse hooks without jq (B-21)
# --------------------------------------------------------------------------------------
PP_TMDL_HOOK = "plugins/power-platform/hooks/validate-tmdl-measure-metadata.sh"
PP_FLOW_HOOK = "plugins/power-platform/hooks/validate-flow-action-names.sh"


def _bin_dir_without(td: str, *, drop: tuple[str, ...]) -> str:
    """A PATH directory of symlinks to the tools the hooks need, minus `drop`."""
    bindir = tempfile.mkdtemp(prefix="bin-", dir=td)
    for tool in ("cat", "awk", "sed", "grep", "dirname", "python3", "jq", "env", "tr"):
        found = shutil.which(tool)
        if found and tool not in drop:
            os.symlink(found, os.path.join(bindir, tool))
    return bindir


@case("B-21")
def case_b21() -> None:
    """Without jq the hooks must still run their check (python3) or say they were skipped."""
    bash = shutil.which("bash")
    expect(bash is not None and shutil.which("python3") is not None, "bash + python3 are required")
    with tempfile.TemporaryDirectory() as td:
        tmdl = os.path.join(td, "model", "Sales.tmdl")
        flow = os.path.join(td, "sol", "workflows", "f.json")
        for path, text in (
            (tmdl, "table Sales\n  measure Total = SUM(Sales[Amount])\n"),
            (
                flow,
                json.dumps({"properties": {"definition": {"actions": {"Compose_2": {}}}}}),
            ),
        ):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            Path(path).write_text(text)

        def fire(hook: str, path: str, bindir: str) -> subprocess.CompletedProcess:
            payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": path}})
            return run([bash, target(hook)], stdin=payload, env={"PATH": bindir})

        no_jq = _bin_dir_without(td, drop=("jq",))
        for hook, path, needle in (
            (PP_TMDL_HOOK, tmdl, "measure Total"),
            (PP_FLOW_HOOK, flow, "Compose_2"),
        ):
            r = fire(hook, path, no_jq)
            expect(
                r.returncode == 0, f"{Path(hook).name}: advisory hook must exit 0: {describe(r)}"
            )
            expect(
                needle in r.stderr,
                f"{Path(hook).name}: with jq missing the check must still run: {describe(r)}",
            )

        # Neither jq nor python3: the hook cannot read its payload, so it must SAY so.
        bare = os.path.join(td, "bare")
        os.makedirs(bare)
        for tool in ("cat", "awk", "sed", "grep", "dirname"):
            os.symlink(shutil.which(tool), os.path.join(bare, tool))
        for hook, path in ((PP_TMDL_HOOK, tmdl), (PP_FLOW_HOOK, flow)):
            r = fire(hook, path, bare)
            expect(r.returncode == 0, f"{Path(hook).name}: must stay fail-safe: {describe(r)}")
            expect(
                "check skipped" in r.stderr and "jq" in r.stderr,
                f"{Path(hook).name}: with no jq and no python3 it must print a skip line: {describe(r)}",
            )

        # Control: with jq present the behaviour is unchanged.
        with_jq = _bin_dir_without(td, drop=())
        r = fire(PP_TMDL_HOOK, tmdl, with_jq)
        expect("measure Total" in r.stderr, f"control (jq present): {describe(r)}")
        # A payload for a non-matching file is still silent.
        other = os.path.join(td, "notes.txt")
        Path(other).write_text("x")
        r = fire(PP_TMDL_HOOK, other, no_jq)
        expect(r.stderr == "", f"a non-TMDL path must stay silent without jq: {describe(r)}")


# --------------------------------------------------------------------------------------
# pbir-ref-integrity check_refs.py: documented exit codes match behaviour (B-24)
# --------------------------------------------------------------------------------------
CHECK_REFS = "plugins/power-platform/skills/pbir-ref-integrity/check_refs.py"


def _documented_exit_codes(source: str) -> dict[int, str]:
    """The `Exit codes` block of the module docstring as {code: text}."""
    block = re.search(r"Exit codes\n-+\n(.*?)\n\"\"\"", source, re.S)
    expect(block is not None, "check_refs.py docstring has no 'Exit codes' block")
    codes: dict[int, str] = {}
    current = None
    for line in block.group(1).splitlines():
        m = re.match(r"^ {2}(\d)\s+(\S.*)$", line)
        if m:
            current = int(m.group(1))
            codes[current] = m.group(2)
        elif current is not None and line.startswith("      "):
            codes[current] += " " + line.strip()
    return codes


@case("B-24")
def case_b24() -> None:
    """The exit codes the docstring promises must be the exit codes the tool returns."""
    source = Path(target(CHECK_REFS)).read_text()
    with tempfile.TemporaryDirectory() as td:
        # Run a copy placed so the script's own repo-root resolves to the temp dir.
        home = Path(td, "plugins", "power-platform", "skills", "pbir-ref-integrity")
        home.mkdir(parents=True)
        script = home / "check_refs.py"
        script.write_text(source)
        pages = Path(td, "torn.Report", "definition", "pages")
        pages.mkdir(parents=True)
        (pages / "pages.json").write_text("{not json")

        r = run(["python3", str(script), str(Path(td, "torn.Report")), "--format", "json"])
        parse_rc = r.returncode
        findings = json.loads(r.stdout)["findings"]
        expect(any(f["check_id"] == "parse" for f in findings), f"no parse finding: {describe(r)}")
        r = run(["python3", str(script), str(Path(td, "empty.Report"))])
        missing_def_rc = r.returncode
        r = run(["python3", str(script), "../x"])
        rejected_rc = r.returncode
        expect(rejected_rc == 2, f"a '..' path must be rejected with 2: {describe(r)}")
        expect(parse_rc == missing_def_rc, "torn JSON and a missing definition/ must agree")

    codes = _documented_exit_codes(source)
    for code, text in codes.items():
        if "parse" in text.lower():
            expect(
                code == parse_rc,
                f"docstring says parse errors exit {code} but the tool exits {parse_rc}: {text!r}",
            )
    expect(2 in codes and "parse" not in codes[2].lower(), f"exit 2 line: {codes.get(2)!r}")
    expect(
        any("parse" in t.lower() for t in codes.values()),
        "the docstring should say where parse errors land (exit 1)",
    )


# --------------------------------------------------------------------------------------
# report-visualization-design grid.py (B-25)
# --------------------------------------------------------------------------------------
GRID_PY = "plugins/power-platform/skills/report-visualization-design/grid.py"


def _grid_regions(*argv: str) -> dict:
    r = run(["python3", target(GRID_PY), "--format", "json", *argv])
    expect(r.returncode == 0, f"grid.py {' '.join(argv)} must succeed: {describe(r)}")
    return json.loads(r.stdout)


@case("B-25")
def case_b25() -> None:
    """Common 16:9 canvases and off-grid margin/gap must be snapped, not rejected."""
    for canvas in ("1600x900", "1440x810", "960x540", "1280x720", "1920x1080"):
        w, h = (int(v) for v in canvas.split("x"))
        for template in ("golden-overview", "3-30-300", "kpi-strip"):
            out = _grid_regions("--template", template, "--canvas", canvas)
            for reg in out["regions"]:
                vals = (reg["x"], reg["y"], reg["width"], reg["height"])
                expect(all(v % 8 == 0 for v in vals), f"{template} {canvas}: {reg} is off-grid")
                expect(
                    reg["x"] + reg["width"] <= w and reg["y"] + reg["height"] <= h,
                    f"{template} {canvas}: {reg} leaves the canvas",
                )
    # Off-grid margin / gap are snapped to the grid, and the payload reports what was used.
    for template in ("golden-overview", "3-30-300", "kpi-strip"):
        out = _grid_regions("--template", template, "--margin", "20", "--gap", "12")
        expect(
            out["margin_px"] % 8 == 0 and out["gap_px"] % 8 == 0,
            f"{template}: margin/gap must be reported on-grid: {out['margin_px']}/{out['gap_px']}",
        )
    # Control: the default canvas is unchanged.
    out = _grid_regions("--template", "golden-overview")
    hero = next(r for r in out["regions"] if r["name"] == "hero")
    expect((hero["width"], hero["height"]) == (1080, 904), f"default golden-overview moved: {hero}")


# --------------------------------------------------------------------------------------
# content-scan.py: SSRF guard (D-11) and digest rendering (D-12)
# --------------------------------------------------------------------------------------
CONTENT_SCAN = "scripts/content-scan.py"


@case("D-11")
def case_d11() -> None:
    """The SSRF guard must refuse CGNAT / metadata addresses and IPv4-in-IPv6 wrappers."""
    import socket

    cs = _load_module(CONTENT_SCAN, "content_scan_under_test")
    real = socket.getaddrinfo

    def public(ip: str) -> bool:
        socket.getaddrinfo = lambda host, port, *a, **k: [(2, 1, 6, "", (ip, 0))]
        try:
            return cs._host_is_public("http://resolves.example/")
        finally:
            socket.getaddrinfo = real

    for ip in (
        "100.100.100.200",  # Alibaba Cloud metadata, 100.64.0.0/10
        "100.64.0.1",
        "::ffff:169.254.169.254",  # IPv4-mapped link-local / cloud metadata
        "::ffff:127.0.0.1",
        "::ffff:10.0.0.1",
        "::ffff:100.100.100.200",
        "2002:a9fe:a9fe::",  # 6to4 wrapping 169.254.169.254
        "2002:7f00:1::",  # 6to4 wrapping 127.0.0.1
        "64:ff9b::a9fe:a9fe",  # NAT64 wrapping 169.254.169.254
        "169.254.169.254",
        "127.0.0.1",
        "10.0.0.1",
        "192.168.1.1",
        "::1",
        "fe80::1",
        "0.0.0.0",
        "224.0.0.1",
    ):
        expect(public(ip) is False, f"{ip} must be refused by the SSRF guard")
    for ip in (
        "93.184.216.34",
        "8.8.8.8",
        "2606:2800:220:1:248:1893:25c8:1946",
    ):
        expect(public(ip) is True, f"public address {ip} must stay allowed")
    # A mixed resolution (one public, one internal) fails closed.
    socket.getaddrinfo = lambda host, port, *a, **k: [
        (2, 1, 6, "", ("93.184.216.34", 0)),
        (2, 1, 6, "", ("100.100.100.200", 0)),
    ]
    try:
        expect(
            cs._host_is_public("http://mixed.example/") is False, "mixed result must fail closed"
        )
    finally:
        socket.getaddrinfo = real


@case("D-12")
def case_d12() -> None:
    """Untrusted titles/excerpts must render as inert single-line text in the digest."""
    import argparse

    cs = _load_module(CONTENT_SCAN, "content_scan_under_test_d12")
    evil_title = "[x](http://evil)\n# H"
    result = {
        "title": evil_title,
        "url": "https://blog.example/post",
        "host": "blog.example",
        "age": "2 days ago\n## injected",
        "query": "q",
        "body_excerpt": "# Heading\n[guide](../../plugins/nope/README.md) `code` <b>x</b>"
        + "y" * 5000,
    }
    args = argparse.Namespace(queries=["q"], freshness=None, site=None)
    digest = cs._render_digest([result], args)

    expect("](http://evil)" not in digest, "the title must not render as a live link")
    expect("](../../plugins/nope/README.md)" not in digest, "the excerpt must not render a link")
    expect(
        not [ln for ln in digest.splitlines() if ln.startswith("# H") or ln.startswith("## inj")],
        "no title/age/excerpt line may start a markdown heading",
    )
    expect("<b>" not in digest, "raw HTML from untrusted text must be escaped")
    rows = [ln for ln in digest.splitlines() if ln.startswith("| blog.example")]
    expect(len(rows) == 1 and "H" in rows[0], f"the title must stay on one table row: {rows!r}")
    expect(len(digest) < 6000, f"the excerpt must be capped (digest is {len(digest)} chars)")
    expect("\\[x\\]" in digest, "the title text should be shown literally (escaped)")

    # A hostile URL cannot break out of the link destination, and non-http schemes are not linked.
    hostile = dict(result, url="https://a.example/x) [pwn](javascript:alert(1)")
    digest = cs._render_digest([hostile], args)
    expect("[pwn](javascript" not in digest, "a hostile URL must not open a second link")
    js = dict(result, url="javascript:alert(1)")
    expect(
        "](javascript:" not in cs._render_digest([js], args), "a javascript: url must not be linked"
    )

    # The md-links gate stays green on a digest built from a hostile title.
    with tempfile.TemporaryDirectory() as td:
        Path(td, "scripts").mkdir()
        shutil.copy(
            REPO / "scripts" / "check-md-links.py", Path(td, "scripts", "check-md-links.py")
        )
        out = Path(td, "docs", "research", "scan")
        out.mkdir(parents=True)
        link_title = dict(result, title="tip [guide](../../plugins/nope/README.md)")
        (out / "digest.md").write_text(cs._render_digest([link_title], args))
        r = run(["python3", str(Path(td, "scripts", "check-md-links.py"))])
        expect(
            r.returncode == 0, f"the md-links gate must not see a link in the digest: {describe(r)}"
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
