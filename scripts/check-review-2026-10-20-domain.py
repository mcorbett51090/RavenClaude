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


# ---------------------------------------------------------------------------
# H-3  security-engineering/sec_risk.py: --auth-required fail-safe was inverted
# ---------------------------------------------------------------------------

SEC_RISK = "plugins/security-engineering/scripts/sec_risk.py"


def _sec_band(*extra: str) -> str:
    base = ["risk-band", "--cvss", "8.0", "--reachable", "yes", "--kev", "no"]
    proc = run(SEC_RISK, *base, "--internet-exposed", "yes", *extra)
    need(proc.returncode == 0, "risk-band must succeed", proc)
    found = re.search(r"RISK BAND\s*:\s*(\w+)", proc.stdout)
    need(found is not None, "risk-band must print a band", proc)
    return found.group(1)


@case("H-3", "sec_risk treats --auth-required unknown/omitted as no authentication")
def _h3() -> None:
    need(_sec_band("--auth-required", "unknown") == "CRITICAL", "unknown must be CRITICAL")
    need(_sec_band() == "CRITICAL", "the omitted flag must be CRITICAL")
    need(_sec_band("--auth-required", "no") == "CRITICAL", "no must be CRITICAL")
    need(_sec_band("--auth-required", "yes") == "HIGH", "yes must stay the lower HIGH band")


# ---------------------------------------------------------------------------
# H-4  salesforce/apex_governor_smell.py: loops whose '{' is on a later line
# ---------------------------------------------------------------------------

APEX_SMELL = "plugins/salesforce/scripts/apex_governor_smell.py"

_APEX_ALLMAN = """public class A {
    public static void run(List<Contact> cons) {
        for (Contact c : cons)
        {
            c.AccountId = [SELECT Id FROM Account LIMIT 1].Id;
            update c;
        }
    }
}
"""
_APEX_MULTILINE_HEADER = """public class B {
    public static void run(List<Id> ids) {
        for (Contact c :
                [SELECT Id FROM Contact WHERE AccountId IN :ids])
        {
            insert new Task(WhoId = c.Id);
        }
    }
}
"""
_APEX_BRACELESS = """public class C {
    public static void run(List<Contact> cons) {
        for (Contact c : cons) insert new Task(WhoId = c.Id);
    }
}
"""
_APEX_SAME_LINE = """public class D {
    public static void run(List<Contact> cons) {
        for (Contact c : cons) { update c; }
    }
}
"""
# Controls that must stay clean: a header-only bulk-safe query, DML after a do-while
# terminator and after a loop, and a lower-case SOQL `for update`.
_APEX_CLEAN = """public class E {
    public static void run(List<Contact> cons, Boolean flag) {
        for (Contact c : [SELECT Id FROM Contact]) { c.Name = 'x'; }
        Integer n = 0;
        do {
            n++;
        } while (n < 3);
        if (flag) { update cons; }
        List<Account> locked = [SELECT Id FROM Account for update];
        update locked;
    }
}
"""


def _apex_kinds(name: str, source: str) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, name).write_text(source, encoding="utf-8")
        proc = run(APEX_SMELL, "--format", "json", tmp)
        need(proc.returncode in (0, 1), f"{name}: scanner crashed", proc)
        return sorted(f["kind"] for f in json.loads(proc.stdout))


@case("H-4", "apex_governor_smell carries a pending loop across lines to its body")
def _h4() -> None:
    both = ["dml-in-loop", "soql-in-loop"]
    need(_apex_kinds("A.cls", _APEX_ALLMAN) == both, "Allman-style loop must flag SOQL+DML")
    need(
        _apex_kinds("B.cls", _APEX_MULTILINE_HEADER) == ["dml-in-loop"],
        "multi-line header: body DML flagged, header-only SOQL not flagged",
    )
    need(_apex_kinds("C.cls", _APEX_BRACELESS) == ["dml-in-loop"], "brace-less loop body")
    need(_apex_kinds("D.cls", _APEX_SAME_LINE) == ["dml-in-loop"], "same-line control changed")
    need(_apex_kinds("E.cls", _APEX_CLEAN) == [], "clean controls must stay unflagged")


# ---------------------------------------------------------------------------
# H-6  graph-engineering lint_graph_shape.py + flag-graph-smells.sh: typed unbounded paths
# ---------------------------------------------------------------------------

GRAPH_LINT = "plugins/graph-engineering/scripts/lint_graph_shape.py"
GRAPH_HOOK = "plugins/graph-engineering/hooks/flag-graph-smells.sh"

_GRAPH_UNBOUNDED = [
    "MATCH (a:P)-[:KNOWS*]->(b) RETURN b",
    "MATCH (a:P)-[r:KNOWS*1..]->(b) RETURN b",
    "MATCH (a:P)-[:KNOWS|FRIEND*..]->(b) RETURN b",
    "MATCH (a:P)-[:KNOWS*]-(b) RETURN b",
    "MATCH (a:P)<-[:KNOWS|:FRIEND*]-(b) RETURN b",
    "MATCH (a:P)-[*]->(b) RETURN b",  # untyped control: flagged before and after
]
_GRAPH_BOUNDED = [
    "MATCH (a:P)-[:KNOWS*1..3]->(b) RETURN b",
    "MATCH (a:P)-[r:KNOWS*..5]->(b) RETURN b",
    "MATCH (a:P)-[:KNOWS|FRIEND*1..4]->(b) RETURN b",
    "MATCH (a:P)-[:KNOWS*2]->(b) RETURN b",
]


def run_hook(
    hook: str, target: Path, **env: str
) -> subprocess.CompletedProcess[str]:
    """Run an advisory domain hook the way Claude Code does: file path as $1."""
    return subprocess.run(
        ["bash", str(ROOT / hook), str(target)],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        env={**os.environ, **env},
        check=False,
    )


@case("H-6", "unbounded variable-length paths on typed edges are flagged by script and hook")
def _h6() -> None:
    wrong: list[str] = []  # collect every miss so a failure shows script AND hook coverage
    with tempfile.TemporaryDirectory() as tmp:
        for n, line in enumerate(_GRAPH_UNBOUNDED + _GRAPH_BOUNDED):
            path = Path(tmp, f"q{n}.cypher")
            path.write_text(line + "\n", encoding="utf-8")
            should_flag = line in _GRAPH_UNBOUNDED
            lint = run(GRAPH_LINT, "--strict", str(path))
            hook = run_hook(GRAPH_HOOK, path, GRAPH_SMELLS_STRICT="1")
            if (lint.returncode == 1) != should_flag:
                wrong.append(f"script flagged={lint.returncode == 1} on {line!r}")
            if (hook.returncode == 2) != should_flag:
                wrong.append(f"hook flagged={hook.returncode == 2} on {line!r}")
    need(not wrong, "typed unbounded path coverage is wrong: " + "; ".join(wrong))


# ---------------------------------------------------------------------------
# H-7 / H-8  edtech-partner-success export-psm-dashboard.py (Snowflake exporter)
# ---------------------------------------------------------------------------

PSM_EXPORT = (
    "plugins/edtech-partner-success/templates/dashboard-tier-0.5-reference/export-psm-dashboard.py"
)
_PSM_ORG = "11111111-2222-4333-8444-555555555555"

_SNOWFLAKE_STUB = """
import datetime
import decimal

class SnowflakeConnection: ...
class DictCursor: ...

class _Cur:
    sql = ""
    def execute(self, sql): self.sql = sql
    def fetchall(self):
        if "from dim_partner" in self.sql:
            return [{
                "ACCOUNT_UID": "a1", "ARR": decimal.Decimal("1200.50"),
                "CONTRACT_START": datetime.date(2026, 1, 2),
                "STAGE_ENTERED_AT": datetime.datetime(2026, 3, 4, 5, 6, 7),
                "COMPONENTS": '{"a": 1}', "SPARK": "[1, 2, 3]", "FLAGS": '["renewal"]',
            }]
        if "from timeline_events" in self.sql:
            return [{"TS": "2026-01-01", "PAYLOAD": '{"priority": "high"}'}]
        return []
    def close(self): pass

class _Conn:
    def cursor(self, cls=None): return _Cur()
    def close(self): pass

def connect(**kwargs): return _Conn()
"""


def _psm_env(tmp: Path) -> dict[str, str]:
    """A fake snowflake.connector package on PYTHONPATH plus the env the exporter wants."""
    pkg = Path(tmp, "stub", "snowflake")
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "connector.py").write_text(_SNOWFLAKE_STUB, encoding="utf-8")
    key = Path(tmp, "key.p8")
    key.write_bytes(b"not-a-real-key")
    names = ("ACCOUNT", "USER", "WAREHOUSE", "DATABASE", "ROLE")
    env = {f"SNOWFLAKE_{name}": "x" for name in names}
    env["SNOWFLAKE_PRIVATE_KEY_PATH"] = str(key)
    env["PYTHONPATH"] = str(Path(tmp, "stub"))
    return env


def _psm_run(tmp: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    out = str(Path(tmp, "out", "data.json"))
    args = ["--out", out, "--as-of", "2026-06-04", "--org-uid", _PSM_ORG, *extra]
    return subprocess.run(
        [sys.executable, str(ROOT / PSM_EXPORT), *args],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        env={**os.environ, **_psm_env(tmp)},
        cwd=tmp,
        check=False,
    )


@case("H-7", "exporter serialises Decimal/date values and decodes OBJECT/ARRAY columns")
def _h7() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proc = _psm_run(Path(tmp))
        need(proc.returncode == 0, "exporter must finish with typed rows, not crash", proc)
        data = json.loads(Path(tmp, "out", "data.json").read_text(encoding="utf-8"))
    partner = data["partners"][0]
    need(partner["arr"] == 1200.5, f"Decimal must become a number, got {partner['arr']!r}")
    need(partner["contract_start"] == "2026-01-02", "date must become an ISO string")
    need(partner["stage_entered_at"].startswith("2026-03-04T05:06:07"), "datetime -> ISO")
    need(partner["components"] == {"a": 1}, "OBJECT column must be decoded to an object")
    need(partner["spark"] == [1, 2, 3], "ARRAY column must be decoded to an array")
    need(partner["flags"] == ["renewal"], "ARRAY of strings must be decoded")
    need(data["timeline_events"][0]["payload"] == {"priority": "high"}, "payload object")


# ---------------------------------------------------------------------------
# H-9  fintech-payments-engineering/recon_diff.py: short rows and BOM CSVs
# ---------------------------------------------------------------------------

RECON_DIFF = "plugins/fintech-payments-engineering/scripts/recon_diff.py"


def _recon(ledger: bytes, psp: bytes, *flags: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        ledger_path = Path(tmp, "ledger.csv")
        psp_path = Path(tmp, "psp.csv")
        ledger_path.write_bytes(ledger)
        psp_path.write_bytes(psp)
        return run(RECON_DIFF, "--ledger", str(ledger_path), "--psp", str(psp_path), *flags)


@case("H-9", "recon_diff: a short row exits 2 with its row number; a BOM CSV parses")
def _h9() -> None:
    ledger = b"reference,amount,currency\nr1,1000,usd\n"
    # Control: a well-formed fee column nets out and balances.
    ok = _recon(ledger, b"reference,amount,currency,fee\nr1,1030,usd,30\n", "--net-fees")
    need(ok.returncode == 0, "well-formed --net-fees pair must balance", ok)
    # Short row: the row ends before the 'fee' cell.
    short = _recon(ledger, b"reference,amount,currency,fee\nr1,1000,usd\n", "--net-fees")
    need(short.returncode == 2, "a short row must exit 2 (input error), not crash with 1", short)
    need("row 2" in short.stderr, "the error must name the row", short)
    need("Traceback" not in short.stderr, "no traceback for a malformed row", short)
    # BOM on the first header (Excel / PSP export).
    bom = b"\xef\xbb\xbf"
    parsed = _recon(bom + ledger, bom + b"reference,amount,currency\nr1,1000,usd\n")
    need(parsed.returncode == 0, "a BOM-prefixed CSV must parse and balance", parsed)
    # Undecodable bytes are an input error too.
    junk = _recon(ledger, b"reference,amount,currency\n\xff\xfe,1,usd\n")
    need(junk.returncode == 2, "an undecodable file must exit 2", junk)


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
