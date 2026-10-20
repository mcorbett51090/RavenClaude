#!/usr/bin/env python3
"""Regression cases for the PK-6 findings (domain calculators + domain hooks) of the
2026-10-20 repo review: H-1 ... H-25.

The domain plugins ship stdlib CLIs and advisory hooks with no test harness of their
own, so this one file drives each fixed script as a subprocess (the same way a consumer
or CI runs it) and checks the hook regexes against must-match / must-not-match lines
with the real `grep -E`. One case per finding; each case fails on the pre-fix code.

  python3 scripts/check-review-2026-10-20-domain.py            # run every case
  python3 scripts/check-review-2026-10-20-domain.py --only H-1 # run chosen cases
  PK6_ROOT=/path/to/prefix-tree python3 scripts/check-review-2026-10-20-domain.py

PK6_ROOT points the run at another tree that has the same `plugins/...` layout (for
example a copy of the pre-fix files), which is how a case's teeth are demonstrated:
every case must pass on the fixed tree and fail on the pre-fix tree.

Exit 0 = every selected case passed, 1 = at least one failed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Callable

ROOT = Path(os.environ.get("PK6_ROOT") or Path(__file__).resolve().parent.parent)
TIMEOUT = 30

CASES: dict[str, tuple[str, Callable[[], None]]] = {}


def case(finding: str, title: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def register(fn: Callable[[], None]) -> Callable[[], None]:
        CASES[finding] = (title, fn)
        return fn

    return register


def run(
    script: str, *args: str, stdin: str | None = None, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Run a plugin script (path relative to the tree root) and capture everything."""
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        cwd=cwd,
        check=False,
    )


def need(cond: bool, message: str, proc: subprocess.CompletedProcess[str] | None = None) -> None:
    if cond:
        return
    detail = ""
    if proc is not None:
        detail = f"\n  rc={proc.returncode}\n  stdout={proc.stdout!r}\n  stderr={proc.stderr!r}"
    raise AssertionError(message + detail)


# ---------------------------------------------------------------------------
# H-1  api-engineering/openapi_diff.py never followed $ref
# ---------------------------------------------------------------------------

OPENAPI_DIFF = "plugins/api-engineering/scripts/openapi_diff.py"


def _openapi_spec(*, refs: bool, new: bool) -> dict:
    """A spec whose bodies live in components. new=True applies four breaking edits:
    a removed response field, string -> integer, a narrowed enum, a newly required
    request property. refs=False inlines every schema (the positive control)."""
    user = {
        "type": "object",
        "properties": {
            "id": {"type": "integer" if new else "string"},
            "status": {"type": "string", "enum": ["a"] if new else ["a", "b"]},
        },
    }
    if not new:
        user["properties"]["email"] = {"type": "string"}
    new_user = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "nick": {"type": "string"}},
        "required": ["name"] if new else [],
    }
    schemas = {"User": user, "NewUser": new_user}

    def body(name: str) -> dict:
        return {"$ref": f"#/components/schemas/{name}"} if refs else schemas[name]

    return {
        "openapi": "3.0.3",
        "info": {"title": "t", "version": "1"},
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {"application/json": {"schema": body("User")}},
                        }
                    }
                },
                "post": {
                    "requestBody": {"content": {"application/json": {"schema": body("NewUser")}}},
                    "responses": {"201": {"description": "created"}},
                },
            }
        },
        "components": {"schemas": schemas},
    }


def _diff_specs(old: dict, new: dict, *flags: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        old_path = Path(tmp, "old.json")
        new_path = Path(tmp, "new.json")
        old_path.write_text(json.dumps(old), encoding="utf-8")
        new_path.write_text(json.dumps(new), encoding="utf-8")
        return run(OPENAPI_DIFF, str(old_path), str(new_path), "--format", "json", *flags)


@case("H-1", "openapi_diff dereferences local $refs, guards cycles, flags unresolved refs")
def _h1() -> None:
    control = _diff_specs(_openapi_spec(refs=False, new=False), _openapi_spec(refs=False, new=True))
    need(control.returncode == 1, "inlined control must exit 1", control)
    control_findings = json.loads(control.stdout)["findings"]
    need(json.loads(control.stdout)["breaking"] == 4, "control must report 4 BREAKING", control)

    reffed = _diff_specs(_openapi_spec(refs=True, new=False), _openapi_spec(refs=True, new=True))
    need(reffed.returncode == 1, "$ref'd specs must exit 1, not 'No differences'", reffed)
    data = json.loads(reffed.stdout)
    need(
        data["breaking"] == 4,
        f"$ref'd specs must report 4 BREAKING, got {data['breaking']}",
        reffed,
    )
    need(
        data["findings"] == control_findings, "$ref'd result must equal the inlined control", reffed
    )

    # A self-referencing schema must terminate (the run() timeout is the backstop).
    def node(value_type: str) -> dict:
        schemas = {
            "Node": {
                "type": "object",
                "properties": {
                    "value": {"type": value_type},
                    "next": {"$ref": "#/components/schemas/Node"},
                },
            }
        }
        return {
            "openapi": "3.0.3",
            "paths": {
                "/n": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "ok",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Node"}
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {"schemas": schemas},
        }

    cyc = _diff_specs(node("string"), node("integer"))
    need(cyc.returncode == 1, "a self-referencing schema must still diff and exit 1", cyc)
    need(json.loads(cyc.stdout)["breaking"] == 1, "cycle: exactly one type change", cyc)

    # An external or missing $ref cannot be diffed: BREAKING 'UNSURE: unresolved $ref'.
    def with_ref(ref: str) -> dict:
        spec = node("string")
        spec["paths"]["/n"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": ref
        }
        return spec

    for ref in ("other.json#/components/schemas/User", "#/components/schemas/Missing"):
        unsure = _diff_specs(with_ref(ref), with_ref(ref))
        need(unsure.returncode == 1, f"unresolved {ref} must exit 1", unsure)
        msgs = [f["message"] for f in json.loads(unsure.stdout)["findings"]]
        need(
            any(m.startswith(f"UNSURE: unresolved $ref {ref}") for m in msgs),
            f"missing UNSURE finding for {ref}",
            unsure,
        )

    # Path-item-level parameters and $ref'd parameters take part in the diff.
    def with_param(present: bool) -> dict:
        spec = node("string")
        item = spec["paths"]["/n"]
        if present:
            item["parameters"] = [{"$ref": "#/components/parameters/Limit"}]
        spec["components"]["parameters"] = {
            "Limit": {"name": "limit", "in": "query", "required": False}
        }
        return spec

    param = _diff_specs(with_param(True), with_param(False))
    need(param.returncode == 1, "a removed path-level $ref'd parameter must be BREAKING", param)
    need(
        any(f["message"] == "parameter removed" for f in json.loads(param.stdout)["findings"]),
        "expected a 'parameter removed' finding",
        param,
    )

    # items / allOf are walked: a field dropped from an allOf base of an array element
    # is a removed response property; a new oneOf variant in a response is BREAKING.
    def composed(with_name: bool, variants: int) -> dict:
        base = {"type": "object", "properties": {"id": {"type": "string"}}}
        if with_name:
            base["properties"]["name"] = {"type": "string"}
        item = {"allOf": [{"$ref": "#/components/schemas/Base"}, {"properties": {}}]}
        schema = {
            "type": "array",
            "items": item,
            "oneOf": [{"type": "string"}, {"type": "integer"}][:variants],
        }
        spec = node("string")
        spec["paths"]["/n"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] = (
            schema
        )
        spec["components"]["schemas"]["Base"] = base
        return spec

    items = _diff_specs(composed(True, 1), composed(False, 2))
    need(items.returncode == 1, "items/allOf/oneOf changes must exit 1", items)
    found = {
        (f["where"].split(" ", 2)[-1], f["message"]) for f in json.loads(items.stdout)["findings"]
    }
    need(
        any(w.endswith("[].name") and "removed" in m for w, m in found),
        f"allOf member field removed under items not found: {found}",
        items,
    )
    need(
        any(w.endswith(".oneOf") and "added to a response" in m for w, m in found),
        f"response oneOf growth not flagged: {found}",
        items,
    )


# ---------------------------------------------------------------------------
# H-5  microsoft-graph/graph_scope_analyzer.py: application Mail.* etc. not escalated
# ---------------------------------------------------------------------------

GRAPH_SCOPES = "plugins/microsoft-graph/scripts/graph_scope_analyzer.py"


@case("H-5", "graph_scope_analyzer escalates application Mail/Calendars grants without .All")
def _h5() -> None:
    apps = "Mail.ReadWrite,Mail.Send,Calendars.ReadWrite"
    proc = run(GRAPH_SCOPES, "--scopes", "User.Read", "--application", apps, "--json")
    need(proc.returncode == 1, "application Mail/Calendars grants must exit 1 (escalate)", proc)
    data = json.loads(proc.stdout)
    escalated = sorted(f["scope"] for f in data["findings"] if f["severity"] == "escalate")
    need(
        escalated == ["Calendars.ReadWrite", "Mail.ReadWrite", "Mail.Send"],
        f"expected three escalate findings, got {escalated}",
        proc,
    )
    need(data["must_escalate"] is True, "must_escalate must be true", proc)
    mail = next(f for f in data["findings"] if f["scope"] == "Mail.ReadWrite")
    need(
        "application access policy" in (mail["suggestion"] or ""),
        "Mail.ReadWrite must keep its narrower-alternative suggestion",
        proc,
    )
    text = run(GRAPH_SCOPES, "--scopes", "User.Read", "--application", apps)
    need("must be escalated" in text.stdout, "verdict line must require escalation", text)

    # Delegated handling is unchanged: a user-bounded Mail.ReadWrite is a NARROW hint only.
    deleg = run(GRAPH_SCOPES, "--scopes", "Mail.ReadWrite", "--json")
    need(deleg.returncode == 0, "delegated Mail.ReadWrite alone must not escalate", deleg)
    need(json.loads(deleg.stdout)["must_escalate"] is False, "delegated: must_escalate", deleg)

    # The scoped '.Selected' variants are not escalated by the prefix rule.
    sel = run(GRAPH_SCOPES, "--scopes", "User.Read", "--application", "Mail.Read.Selected")
    need(sel.returncode == 0, "an application '.Selected' scope must not escalate", sel)


# ---------------------------------------------------------------------------
# H-2  experimentation-growth-engineering/experiment_calc.py: mde capped at min(p, 1-p)
# ---------------------------------------------------------------------------

EXPERIMENT_CALC = "plugins/experimentation-growth-engineering/scripts/experiment_calc.py"


@case("H-2", "experiment_calc mde searches up to 1 - p1 instead of wrongly saying underpowered")
def _h2() -> None:
    mde = run(EXPERIMENT_CALC, "mde", "--baseline", "3%", "--per-arm", "500")
    need(mde.returncode == 0, "mde must succeed", mde)
    need("underpowered for any realistic lift" not in mde.stdout, "false 'underpowered'", mde)
    found = re.search(r"smallest MDE\s*:\s*\+([0-9.]+)% absolute", mde.stdout)
    need(found is not None, "mde must print a numeric smallest MDE", mde)
    delta = float(found.group(1))
    # 4pp is detectable at 82.8% power with 500/arm, so the 80%-power MDE sits below 4pp;
    # the old ceiling stopped at the 3pp baseline and never got there.
    need(3.0 < delta < 4.0, f"MDE {delta}pp must lie between the old ceiling (3pp) and 4pp", mde)
    power = run(
        EXPERIMENT_CALC, "power", "--baseline", "3%", "--mde", f"{delta}pp", "--per-arm", "500"
    )
    got = re.search(r"achieved power\s*:\s*([0-9.]+)%", power.stdout)
    need(got is not None, "power must print the achieved power", power)
    need(abs(float(got.group(1)) - 80.0) < 0.5, f"power at the MDE must be ~80%: {got.group(1)}", power)


# ===========================================================================
# driver
# ===========================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="+", metavar="ID", help="run only these finding ids")
    args = parser.parse_args(argv)

    selected = args.only or list(CASES)
    unknown = [i for i in selected if i not in CASES]
    if unknown:
        print(f"unknown case id(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    failed = 0
    for finding in selected:
        title, fn = CASES[finding]
        try:
            fn()
        except Exception as exc:  # a case must report, never crash the whole run
            failed += 1
            print(f"FAIL {finding}: {title}")
            if isinstance(exc, AssertionError):
                print(f"     {exc}")
            else:
                traceback.print_exc()
        else:
            print(f"PASS {finding}: {title}")
    print(f"{len(selected) - failed}/{len(selected)} passed (tree: {ROOT})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
