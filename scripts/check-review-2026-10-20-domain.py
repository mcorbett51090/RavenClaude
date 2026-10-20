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
        stdin=subprocess.DEVNULL,
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


# ---------------------------------------------------------------------------
# H-10  data-streaming-engineering/stream_sizing.py: float ceiling adds a phantom partition
# ---------------------------------------------------------------------------

STREAM_SIZING = "plugins/data-streaming-engineering/scripts/stream_sizing.py"


def _partitions(target: str, per_consumer: str, headroom: str) -> int:
    args = ["--target-msgs-per-sec", target, "--per-consumer-msgs-per-sec", per_consumer]
    proc = run(STREAM_SIZING, "partitions", *args, "--headroom", headroom)
    need(proc.returncode == 0, "partitions must succeed", proc)
    found = re.search(r"minimum partitions:\s*(\d+)", proc.stdout)
    need(found is not None, "partitions must print a count", proc)
    return int(found.group(1))


@case("H-10", "stream_sizing partitions does not round 11.000000000000002 up to 12")
def _h10() -> None:
    need(_partitions("100", "10", "1.1") == 11, "100 msg/s x 1.1 / 10 must be 11 partitions")
    need(_partitions("40000", "5000", "1.5") == 12, "exact 12.0 must stay 12")
    need(_partitions("1000", "300", "1.0") == 4, "a real fraction (3.33) must still round up")


# ---------------------------------------------------------------------------
# H-13 (+ riders H-11, H-12, H-14)  ERE-bracket class in four domain hooks
# ---------------------------------------------------------------------------

I18N_HOOK = (
    "plugins/localization-i18n-engineering/hooks/check-localization-i18n-engineering-anti-patterns.sh"
)
K8S_HOOK = "plugins/cloud-native-kubernetes/hooks/check-cloud-native-kubernetes-anti-patterns.sh"
DS_HOOK = "plugins/data-science-research/hooks/check-data-science-research-anti-patterns.sh"
M365_HOOK = "plugins/microsoft-365-copilot/hooks/flag-copilot-anti-patterns.sh"

# (hook, pattern as it must appear in the hook source, effective regex, grep flags,
#  must-match lines, must-not-match lines). A bracket expression has no escapes in POSIX:
#  `[/\-.]` is an invalid range (grep exits 2, the check is dead), `[^\n]` and `[^.\n]`
#  also exclude the letter 'n', and `\\\$` demands a literal backslash before the dollar.
_ERE_ROWS = [
    (
        I18N_HOOK,
        "MM[/.-]DD[/.-]YYYY|DD[/.-]MM[/.-]YYYY|YYYY[/.-]MM[/.-]DD|yyyy[/.-]MM[/.-]dd",
        r"""(["'`])(MM[/.-]DD[/.-]YYYY|DD[/.-]MM[/.-]YYYY|YYYY[/.-]MM[/.-]DD"""
        r"""|yyyy[/.-]MM[/.-]dd)\1""",
        "-Ei",
        ['const f = "MM/DD/YYYY";', "fmt = 'dd-mm-yyyy'", "f = `yyyy.MM.dd`"],
        ['const f = "MM/DD";', "f = MM/DD/YYYY", "f = \"MM/DD/YYYY'"],
    ),
    (
        I18N_HOOK,
        r'"(\$|€|£|¥|₩|₹|₽|¢)"',
        r'"(\$|€|£|¥|₩|₹|₽|¢)"',
        "-E",
        ['const sym = "$";', 'sym = "€"'],
        ['price = "$5"', 'code = "USD"'],
    ),
    (
        K8S_HOOK,
        "image:[[:space:]]*[^@[:space:]]+[[:space:]]*$",
        "image:[[:space:]]*[^[:space:]]+:latest|image:[[:space:]]*[^@[:space:]]+[[:space:]]*$",
        "-Ei",
        [
            "image: redis:7",
            "  image: registry.example.com/team/app",
            "image: nginx:latest",
        ],
        ["image: redis@sha256:abcdef", "  image: registry.example.com/app@sha256:ab12"],
    ),
    (
        DS_HOOK,
        "KNNImputer).*\\.fit",
        r"(StandardScaler|MinMaxScaler|RobustScaler|OneHotEncoder|OrdinalEncoder|TargetEncoder"
        r"|SimpleImputer|KNNImputer).*\.fit",
        "-E",
        ["s = MinMaxScaler(feature_range=(0, 1)).fit(X)", "StandardScaler().fit(X)"],
        ["s = MinMaxScaler()", "X = pd.read_csv(path)"],
    ),
    (
        M365_HOOK,
        r"\bRCD\b)[^.]{0,80}(security boundary",
        r"(restricted (sharepoint )?search|restricted content discovery|\bRSS\b|\bRCD\b)[^.]{0,80}"
        r"(security boundary|access control|prevents access|blocks access|stops (a )?user)",
        "-Ei",
        [
            "Restricted SharePoint Search is an effective security boundary",
            "RCD is an extra access control for the library",
        ],
        [
            "RSS is a feature. It is described as a security boundary elsewhere",
            "Restricted SharePoint Search narrows what Copilot can reach",
        ],
    ),
]


def _grep_line(flags: str, pattern: str, line: str) -> int:
    proc = subprocess.run(
        ["grep", flags, "--", pattern],
        input=line + "\n",
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )
    return proc.returncode


def _hook_says(hook: str, name: str, text: str, strict_env: str, needle: str) -> bool:
    """Run a hook over a one-line file; True when its advisory mentions `needle`."""
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp, name)
        target.write_text(text + "\n", encoding="utf-8")
        proc = run_hook(hook, target, **{strict_env: "1"})
    return needle in proc.stderr


@case("H-13", "four domain hooks: ERE bracket-class bugs fixed (i18n 4b/4c + riders H-11/12/14)")
def _h13() -> None:
    problems: list[str] = []
    for hook, snippet, regex, flags, must, must_not in _ERE_ROWS:
        if snippet not in (ROOT / hook).read_text(encoding="utf-8"):
            problems.append(f"{Path(hook).name}: fixed pattern {snippet!r} is not in the hook")
        for line in must:
            if (rc := _grep_line(flags, regex, line)) != 0:
                problems.append(f"{Path(hook).name}: grep rc={rc} (want match) on {line!r}")
        for line in must_not:
            if (rc := _grep_line(flags, regex, line)) != 1:
                problems.append(f"{Path(hook).name}: grep rc={rc} (want no match) on {line!r}")

    # End to end: the real hooks fire (strict mode) on the shapes they used to miss.
    e2e = [
        (I18N_HOOK, "L10N_I18N_STRICT", "f.js", 'const f = "MM/DD/YYYY";', "Hard-coded date format"),
        (I18N_HOOK, "L10N_I18N_STRICT", "f.js", 'const s = "$";', "Hard-coded currency symbol"),
        (K8S_HOOK, "K8S_STRICT", "d.yaml", "image: registry.example.com/team/app", "not pinned"),
        (
            DS_HOOK,
            "DS_STRICT",
            "m.py",
            "import numpy as np\n"
            "s = MinMaxScaler(feature_range=(0, 1)).fit(X)\n"
            "train_test_split(X, random_state=0)",
            "before train_test_split",
        ),
        (
            M365_HOOK,
            "M365_COPILOT_STRICT",
            "n.md",
            "Restricted SharePoint Search is an effective security boundary",
            "rss-rcd-not-a-boundary",
        ),
    ]
    for hook, strict, name, text, needle in e2e:
        if not _hook_says(hook, name, text, strict, needle):
            problems.append(f"{Path(hook).name}: did not report {needle!r} on {text!r}")
    # ...and stays silent on a digest-pinned image.
    if _hook_says(K8S_HOOK, "d.yaml", "image: redis@sha256:abcdef", "K8S_STRICT", "not pinned"):
        problems.append("k8s hook flagged a digest-pinned image")
    need(not problems, "hook rows failed:\n  " + "\n  ".join(problems))


# ---------------------------------------------------------------------------
# H-16  tableau/flag-tableau-anti-patterns.sh: `grep -c ... || echo 0` yields "0\n0"
# ---------------------------------------------------------------------------

TABLEAU_HOOK = "plugins/tableau/hooks/flag-tableau-anti-patterns.sh"


def _tableau(text: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp, "wb.twb")
        target.write_text(text, encoding="utf-8")
        return run_hook(TABLEAU_HOOK, target)


@case("H-16", "tableau hook: no bash syntax error without <datasource; blend note still fires")
def _h16() -> None:
    none = _tableau("<workbook><worksheets/></workbook>\n")
    need(none.returncode == 0, "the hook is advisory and must exit 0", none)
    need("syntax error" not in none.stderr, "no bash arithmetic error on a datasource-free file", none)
    need("Multiple data sources" not in none.stderr, "no blend note for zero datasources", none)

    # One datasource per line, as in real .twb XML (the hook counts matching lines).
    blend = _tableau(
        "<workbook>\n<datasource name='a'/>\n<datasource name='b'/>\n"
        "<datasource-dependencies datasource='a'/>\n</workbook>\n"
    )
    need(blend.returncode == 0, "the hook must exit 0 on a blend", blend)
    need("Multiple data sources detected" in blend.stderr, "the blend note must fire", blend)

    single = _tableau("<workbook>\n<datasource name='a'/>\n<col primary-key='id'/>\n</workbook>\n")
    need("Multiple data sources" not in single.stderr, "one datasource is not a blend", single)


# ---------------------------------------------------------------------------
# H-17  qa-test-automation/qa_suite_metrics.py: pyramid_ratio --dir read ancestor names
# ---------------------------------------------------------------------------

QA_METRICS = "plugins/qa-test-automation/scripts/qa_suite_metrics.py"


def _pyramid(root: Path) -> dict[str, int]:
    proc = run(QA_METRICS, "pyramid_ratio", "--dir", str(root))
    need(proc.returncode == 0, "pyramid_ratio --dir must succeed", proc)
    counts = {}
    for level in ("unit", "integration", "e2e"):
        found = re.search(rf"^\s*{level}:\s+(\d+)", proc.stdout, re.MULTILINE)
        need(found is not None, f"no '{level}' line in the report", proc)
        counts[level] = int(found.group(1))
    return counts


@case("H-17", "pyramid_ratio --dir classifies on the path relative to --dir, by whole tokens")
def _h17() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        # The scanned root sits under an ancestor whose name contains '_it'.
        proj = Path(tmp, "x_it", "proj")
        files = {
            "tests/unit/test_a.py": "unit",
            "tests/integration/test_b.py": "integration",
            "tests/e2e/checkout.spec.ts": "e2e",
            "src/Calc.it.java": "integration",
            "web/login.cy.ts": "e2e",
            "tests/test_plain.py": "unit",
        }
        for rel in files:
            target = proj / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("", encoding="utf-8")
        counts = _pyramid(proj)
    want = {"unit": 2, "integration": 2, "e2e": 2}
    need(counts == want, f"expected {want}, got {counts} (ancestor '_it' must not count)")


# ---------------------------------------------------------------------------
# H-18  email-engineering/email_auth_lint.py: SPF redirect= is a valid terminator
# ---------------------------------------------------------------------------

EMAIL_LINT = "plugins/email-engineering/scripts/email_auth_lint.py"


@case("H-18", "email_auth_lint: no 'No terminal all' for redirect=; warn when both appear")
def _h18() -> None:
    redirect = run(EMAIL_LINT, "spf", "v=spf1 redirect=_spf.example.com")
    need("No terminal" not in redirect.stdout, "redirect= is a valid terminator", redirect)
    need(redirect.returncode == 0, "a lone redirect= record has no errors", redirect)

    both = run(EMAIL_LINT, "spf", "v=spf1 redirect=x.example.com -all")
    need("redirect=" in both.stdout and "[WARN]" in both.stdout, "both-present warning", both)
    need(both.returncode == 0, "the both-present case is a warning, not an error", both)

    bare = run(EMAIL_LINT, "spf", "v=spf1 include:_spf.google.com")
    need("No terminal 'all'" in bare.stdout, "no all and no redirect must still warn", bare)


# ---------------------------------------------------------------------------
# H-19  observability-sre/slo_calc.py: burn-rate did not validate --window-days
# ---------------------------------------------------------------------------

SLO_CALC = "plugins/observability-sre/scripts/slo_calc.py"


@case("H-19", "slo_calc burn-rate rejects --window-days <= 0 with exit 2, no ZeroDivisionError")
def _h19() -> None:
    base = ["burn-rate", "--slo", "99.9", "--bad", "10", "--total", "1000", "--elapsed-hours", "1"]
    for days in ("0", "-5"):
        proc = run(SLO_CALC, *base, "--window-days", days)
        need(proc.returncode == 2, f"--window-days {days} must exit 2", proc)
        need("--window-days must be positive" in proc.stderr, "the message must say why", proc)
        need("Traceback" not in proc.stderr, "no ZeroDivisionError traceback", proc)
    ok = run(SLO_CALC, *base, "--window-days", "30")
    need(ok.returncode == 0 and "burn_rate" in ok.stdout, "a valid window still works", ok)


# ---------------------------------------------------------------------------
# H-20  clinical-trials/trials_calc.py: retention-roi footer backwards, impossible break-even
# ---------------------------------------------------------------------------

TRIALS_CALC = "plugins/clinical-trials/scripts/trials_calc.py"


def _retention(dropout: str, program_cost: str) -> subprocess.CompletedProcess[str]:
    args = ["--enrolled", "100", "--dropout-rate", dropout, "--replacement-cost", "1000"]
    return run(TRIALS_CALC, "retention-roi", *args, "--intervention-cost-per-patient", program_cost)


@case("H-20", "trials_calc retention-roi: correct footer, impossible break-even flagged")
def _h20() -> None:
    impossible = _retention("2%", "400")  # needs a 40-point cut out of a 2% rate
    need(impossible.returncode == 0, "retention-roi must succeed", impossible)
    need(
        "cannot break even: required cut exceeds the dropout rate" in impossible.stdout,
        "an impossible break-even must be flagged",
        impossible,
    )
    need("pays for itself" not in impossible.stdout, "no 'pays for itself' footer", impossible)

    normal = _retention("30%", "100")  # a 10-point cut out of 30%
    need("cannot break even" not in normal.stdout, "a reachable break-even is not flagged", normal)
    need("above that cut it pays for itself" in normal.stdout, "corrected footer", normal)
    need("below that it pays for itself" not in normal.stdout, "the backwards footer is gone", normal)


# ---------------------------------------------------------------------------
# H-21  claude-app-engineering/claude_cost_estimator.py: validation + closed-form break-even
# ---------------------------------------------------------------------------

COST_ESTIMATOR = "plugins/claude-app-engineering/scripts/claude_cost_estimator.py"


def _loop_break_even(cached: int, uncached: int, n: int, write: float, read: float) -> int | None:
    """The pre-fix O(requests) loop, kept here as the reference answer."""
    price = 5.0 / 1_000_000.0
    cum_no = cum_cache = 0.0
    for i in range(1, n + 1):
        cum_no += (cached + uncached) * price
        mult = write if i == 1 else read
        cum_cache += cached * price * mult + uncached * price
        if cum_cache < cum_no:
            return i
    return None


@case("H-21", "claude_cost_estimator: rejects negative inputs; closed-form break-even matches")
def _h21() -> None:
    bad = [
        ["cache", "--cached-tokens", "-1", "--requests", "10", "--input-price", "5"],
        ["cache", "--cached-tokens", "100", "--requests", "-3", "--input-price", "5"],
        ["budget", "--prefix-tokens", "100", "--window", "-5"],
        ["batch", "--input-tokens", "10", "--output-tokens", "-1", "--requests", "5",
         "--input-price", "5", "--output-price", "25"],
        ["batch", "--input-tokens", "10", "--output-tokens", "1", "--requests", "5",
         "--input-price", "5", "--output-price", "25", "--batch-discount", "1.5"],
    ]  # fmt: skip
    for argv in bad:
        proc = run(COST_ESTIMATOR, *argv)
        need(proc.returncode == 2, f"{argv} must exit 2", proc)
        need(proc.stderr.startswith("error:"), "a clear error message", proc)

    mismatches = []
    for cached, uncached, n, ttl, read in [
        (40000, 500, 100, "5m", 0.1), (40000, 0, 2, "5m", 0.1), (40000, 500, 1, "5m", 0.1),
        (40000, 500, 3, "1h", 0.1), (1000, 10, 50, "5m", 0.5), (1000, 10, 50, "1h", 0.6),
        (1000, 10, 50, "1h", 1.0), (1000, 10, 50, "5m", 1.5), (0, 500, 10, "5m", 0.1),
        (7, 3, 1000, "1h", 0.85), (123456, 789, 20, "5m", 0.25), (500, 0, 5, "1h", 0.4),
    ]:  # fmt: skip
        write = 2.0 if ttl == "1h" else 1.25
        want = _loop_break_even(cached, uncached, n, write, read)
        argv = ["cache", "--cached-tokens", str(cached), "--uncached-tokens", str(uncached),
                "--requests", str(n), "--input-price", "5.0", "--ttl", ttl,
                "--cache-read-mult", str(read)]  # fmt: skip
        out = run(COST_ESTIMATOR, *argv).stdout
        found = re.search(r"break-even at\s*: request #(\d+)", out)
        got = int(found.group(1)) if found else None
        if got != want:
            mismatches.append(f"{argv[1:]}: closed form {got}, loop {want}")
    need(not mismatches, "break-even differs from the loop: " + "; ".join(mismatches))

    # An exact tie (cumulative costs equal) is not yet "cheaper": the old float loop picked
    # either side of it by rounding noise, the closed form is strict (request 3 ties, 4 wins).
    for cached, uncached, n, read, want in [(1000, 10, 50, 0.5, 4), (7, 3, 1000, 0.9, 12)]:
        argv = ["cache", "--cached-tokens", str(cached), "--uncached-tokens", str(uncached),
                "--requests", str(n), "--input-price", "5.0", "--ttl", "1h",
                "--cache-read-mult", str(read)]  # fmt: skip
        found = re.search(r"break-even at\s*: request #(\d+)", run(COST_ESTIMATOR, *argv).stdout)
        need(found is not None and int(found.group(1)) == want, f"tie {argv[1:]}: want #{want}")

    # O(1): a billion requests must not loop a billion times (the run() timeout is the backstop).
    huge = run(
        COST_ESTIMATOR, "cache", "--cached-tokens", "40000", "--requests", "1000000000",
        "--input-price", "5.0",
    )  # fmt: skip
    need(huge.returncode == 0 and "break-even at" in huge.stdout, "huge N must finish", huge)


# ---------------------------------------------------------------------------
# H-22  hospice-referral-sales/hospice_calc.py: _pct read a bare '1' as 100%
# ---------------------------------------------------------------------------

HOSPICE_CALC = "plugins/hospice-referral-sales/scripts/hospice_calc.py"


def _weight_loss(value: str) -> subprocess.CompletedProcess[str]:
    return run(HOSPICE_CALC, "eligibility-indicators", "--weight-loss", value)


@case("H-22", "hospice_calc: a bare '1' is ambiguous (exit 2); malformed rates are argparse errors")
def _h22() -> None:
    ambiguous = _weight_loss("1")
    need(ambiguous.returncode == 2, "--weight-loss 1 must exit 2", ambiguous)
    need("ambiguous" in ambiguous.stderr, "the error must say it is ambiguous", ambiguous)
    need("100.0%" not in ambiguous.stdout, "no silent 100%", ambiguous)

    for value, shown in (("1%", "1.0%"), ("0.05", "5.0%"), ("12%", "12.0%"), ("12", "12.0%")):
        proc = _weight_loss(value)
        need(proc.returncode == 0, f"--weight-loss {value} must be accepted", proc)
        need(f"weight loss  : {shown}" in proc.stdout, f"{value} must read as {shown}", proc)

    for argv in (
        ["eligibility-indicators", "--weight-loss", "abc"],
        ["funnel", "--referrals", "80", "--admit-rate", "abc"],
        ["funnel", "--referrals", "80", "--admit-rate", "1"],
        ["funnel", "--referrals", "80", "--admit-rate", "-5%"],
    ):
        proc = run(HOSPICE_CALC, *argv)
        need(proc.returncode == 2, f"{argv} must exit 2", proc)
        need("Traceback" not in proc.stderr, f"{argv} must not traceback", proc)

    funnel = run(HOSPICE_CALC, "funnel", "--referrals", "80", "--admit-rate", "65%")
    need("65.0%" in funnel.stdout, "a percent still works", funnel)


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
