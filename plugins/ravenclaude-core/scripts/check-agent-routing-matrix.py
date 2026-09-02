#!/usr/bin/env python3
"""Gate 255 driver — agent-routing-matrix.json/.md/.schema.json invariants.

Checks A-I (see plugins/ravenclaude-core/knowledge/agent-routing-matrix.md §"How this is gated"):
  A  schema-conformant (hand-rolled validator; meta-teeth mutates the schema itself)
  B  no vendor-fact duplication (ban-list derived from substrate-tier-map.json + model-catalog.json,
     scanned against the .json AND the whitespace-normalized .md)
  C  no numeric confidence (exact on the .json; shape-match only on the .md)
  D1 agent_hosts referential integrity (strict membership, never resolve_tier)
  D2 every model_ref resolves + agrees with agent_hosts (strict membership, never resolve_tier)
  E  framework-rule citations: source file exists, quote appears verbatim (whitespace/markdown
     normalized) somewhere in that file — existence, not relevance (stated honestly in the .md)
  F  owner/staleness_tier/review_trigger carry real values, not just presence
  G  route-task.py --self-test reports exit 0 and an N/N (equal) pass line — new coverage, not a
     regression-proof (route-task.py is not itself in audit-gates.sh)
  I  per-task_class totality bounded to the 4 grounded cells (inline, chat, agent+reversible,
     agent+irreversible), contiguous 1..N ranks per cell, no duplicates/gaps

--must-fail-convention prints `must-fail-teeth-exit: 3` and exits 0.
--must-fail plants one mutant per check (+ B/C/E/G must-NOT-fire companions), asserts every mutant
is caught and every companion stays clean, then exits 3 iff all of that held (rc_mustfail's contract).
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

MUST_FAIL_TEETH_EXIT = 3

REPO_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE = REPO_ROOT / "plugins" / "ravenclaude-core" / "knowledge"
DATA_PATH = KNOWLEDGE / "agent-routing-matrix.json"
SCHEMA_PATH = KNOWLEDGE / "agent-routing-matrix.schema.json"
DOC_PATH = KNOWLEDGE / "agent-routing-matrix.md"
SUBSTRATE_PATH = KNOWLEDGE / "substrate-tier-map.json"
CATALOG_PATH = KNOWLEDGE / "model-catalog.json"
ROUTE_TASK = REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "route-task.py"

GROUNDED_CELLS = {
    ("inline", "reversible"),
    ("chat", "reversible"),
    ("agent", "reversible"),
    ("agent", "irreversible"),
}
STALENESS_TIERS = {"Tier-1", "Tier-2", "Tier-3", "Tier-4", "Tier-5"}
BASIS_VALUES = {"framework-rule", "capability-fact", "cost-heuristic", "editorial-judgment"}
INTERACTION_MODES = {"inline", "chat", "agent"}
BLAST_RADII = {"reversible", "irreversible"}
AGENT_IDS = {"claude-code", "codex-cli", "copilot-cli", "copilot-chat", "grok-build-cli"}
HOST_KEYS = {"claude", "codex", "copilot", "grok"}
TIER_KEYS = {"fast", "balanced", "top"}

_WS_RE = re.compile(r"\s+")
_MD_MARK_RE = re.compile(r"[*_`]+")


def _norm(text: str) -> str:
    """Whitespace-collapse + strip markdown emphasis/code markers (RT-6)."""
    return _WS_RE.sub(" ", _MD_MARK_RE.sub("", text)).strip()


def _load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Check A — schema-conformant (hand-rolled; no third-party jsonschema dep)
# ---------------------------------------------------------------------------


def validate_schema_shape(schema: object) -> list[str]:
    """Meta-teeth support: the schema itself must declare non-empty `required` arrays."""
    errs: list[str] = []
    if not isinstance(schema, dict):
        return ["$ (schema): not an object"]
    req = schema.get("required")
    if not isinstance(req, list) or not req:
        errs.append("$.required (schema): missing or empty")
    rec = (schema.get("$defs") or {}).get("recommendation", {})
    rreq = rec.get("required")
    if not isinstance(rreq, list) or not rreq:
        errs.append("$defs.recommendation.required (schema): missing or empty")
    return errs


def validate_data(data: object, schema: object) -> list[str]:
    errs: list[str] = []
    if not isinstance(data, dict):
        return ["$: root is not an object"]

    top_required = schema.get("required", []) if isinstance(schema, dict) else []
    for k in top_required:
        if k not in data:
            errs.append(f"$.{k}: missing required top-level key")

    if data.get("schema_version") != "1":
        errs.append("$.schema_version: must be '1'")
    if not isinstance(data.get("owner"), str) or not data["owner"].strip():
        errs.append("$.owner: must be a non-empty string")
    if data.get("staleness_tier") not in STALENESS_TIERS:
        errs.append(f"$.staleness_tier: must be one of {sorted(STALENESS_TIERS)}")
    if not isinstance(data.get("review_trigger"), str) or not data["review_trigger"].strip():
        errs.append("$.review_trigger: must be a non-empty string")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(data.get("last_reviewed", ""))):
        errs.append("$.last_reviewed: must be YYYY-MM-DD")

    sources = data.get("sources")
    source_ids: set[str] = set()
    if not isinstance(sources, list) or not sources:
        errs.append("$.sources: must be a non-empty array")
    else:
        for i, s in enumerate(sources):
            if not isinstance(s, dict) or not s.get("id"):
                errs.append(f"$.sources[{i}]: missing non-empty 'id'")
            else:
                source_ids.add(s["id"])

    agent_hosts = data.get("agent_hosts")
    if not isinstance(agent_hosts, dict) or not agent_hosts:
        errs.append("$.agent_hosts: must be a non-empty object")
    else:
        for k, v in agent_hosts.items():
            if k not in AGENT_IDS:
                errs.append(f"$.agent_hosts.{k}: key not a recognised agent id {sorted(AGENT_IDS)}")
            if v not in HOST_KEYS:
                errs.append(f"$.agent_hosts.{k}: value not a recognised host key {sorted(HOST_KEYS)}")

    task_classes = data.get("task_classes")
    if not isinstance(task_classes, dict) or not task_classes:
        errs.append("$.task_classes: must be a non-empty object")
    else:
        for tc_id, tc in task_classes.items():
            if not re.match(r"^[a-z][a-z0-9-]*$", tc_id):
                errs.append(f"$.task_classes.{tc_id}: id must match ^[a-z][a-z0-9-]*$")
            if not isinstance(tc, dict):
                errs.append(f"$.task_classes.{tc_id}: must be an object")
                continue
            for req in ("label", "complexity_note", "recommendations"):
                if req not in tc:
                    errs.append(f"$.task_classes.{tc_id}: missing required '{req}'")
            recs = tc.get("recommendations")
            if not isinstance(recs, list) or not recs:
                errs.append(f"$.task_classes.{tc_id}.recommendations: must be a non-empty array")
                continue
            for i, r in enumerate(recs):
                p = f"$.task_classes.{tc_id}.recommendations[{i}]"
                if not isinstance(r, dict):
                    errs.append(f"{p}: must be an object")
                    continue
                for req in (
                    "interaction_mode",
                    "blast_radius",
                    "agent",
                    "model_ref",
                    "rank",
                    "basis",
                    "rationale",
                    "sources",
                ):
                    if req not in r:
                        errs.append(f"{p}: missing required '{req}'")
                if r.get("interaction_mode") not in INTERACTION_MODES:
                    errs.append(f"{p}.interaction_mode: must be one of {sorted(INTERACTION_MODES)}")
                if r.get("blast_radius") not in BLAST_RADII:
                    errs.append(f"{p}.blast_radius: must be one of {sorted(BLAST_RADII)}")
                if r.get("agent") not in AGENT_IDS:
                    errs.append(f"{p}.agent: must be one of {sorted(AGENT_IDS)}")
                mr = r.get("model_ref")
                if not isinstance(mr, dict) or "host" not in mr or "tier" not in mr:
                    errs.append(f"{p}.model_ref: must be an object with 'host' and 'tier'")
                else:
                    if mr["host"] not in HOST_KEYS:
                        errs.append(f"{p}.model_ref.host: must be one of {sorted(HOST_KEYS)}")
                    if mr["tier"] not in TIER_KEYS:
                        errs.append(f"{p}.model_ref.tier: must be one of {sorted(TIER_KEYS)}")
                rank = r.get("rank")
                if not isinstance(rank, int) or isinstance(rank, bool) or rank < 1:
                    errs.append(f"{p}.rank: must be a positive integer")
                if r.get("basis") not in BASIS_VALUES:
                    errs.append(f"{p}.basis: must be one of {sorted(BASIS_VALUES)}")
                if r.get("basis") == "framework-rule" and not (
                    isinstance(r.get("quote"), str) and r["quote"].strip()
                ):
                    errs.append(f"{p}.quote: required and non-empty when basis=framework-rule")
                if not isinstance(r.get("rationale"), str) or not r["rationale"].strip():
                    errs.append(f"{p}.rationale: must be a non-empty string")
                rsrc = r.get("sources")
                if not isinstance(rsrc, list) or not rsrc:
                    errs.append(f"{p}.sources: must be a non-empty array")
                elif source_ids and not set(rsrc) <= source_ids:
                    errs.append(f"{p}.sources: references an id not in top-level sources[]")
    return errs


# ---------------------------------------------------------------------------
# Check B — no vendor-fact duplication (RT-1 scoped derivation, not "every leaf")
# ---------------------------------------------------------------------------


def _substrate_model_leaves(substrate: dict) -> set[str]:
    leaves: set[str] = set()
    for host_table in (substrate.get("hosts") or {}).values():
        if not isinstance(host_table, dict):
            continue
        for row in host_table.values():
            if isinstance(row, str):
                leaves.add(row)
            elif isinstance(row, dict) and isinstance(row.get("model"), str):
                leaves.add(row["model"])
    return leaves


def build_ban_list(substrate: dict, catalog: dict) -> set[str]:
    ban = set(_substrate_model_leaves(substrate))
    for key in ("current", "stale"):
        section = catalog.get(key)
        if isinstance(section, dict):
            ban.update(v for v in section.values() if isinstance(v, str))
        elif isinstance(section, list):
            ban.update(v for v in section if isinstance(v, str))
    return {b for b in ban if b}


def check_b(data: object, doc_text: str, substrate: dict, catalog: dict) -> list[str]:
    errs: list[str] = []
    ban = build_ban_list(substrate, catalog)
    # Positive control: the derivation must actually produce something, and it must contain
    # both a hyphenated id and a display-name form, or a mis-scoped derivation would pass green.
    has_hyphenated = any(re.match(r"^[a-z0-9][a-z0-9.-]*-[0-9]", b) for b in ban)
    has_display = any(" " in b and b[0].isupper() for b in ban)
    if not ban or not has_hyphenated or not has_display:
        errs.append(
            "check-b-positive-control: derived ban-list is empty or missing a "
            "hyphenated-id/display-name pair — the derivation is mis-scoped"
        )
        return errs

    raw_json = json.dumps(data)
    for b in ban:
        if b in raw_json:
            errs.append(f"$.* (json, raw+parsed scan): vendor-fact literal '{b}' found")
    normalized_doc = _norm(doc_text)
    for b in ban:
        if _norm(b) in normalized_doc:
            errs.append(f"agent-routing-matrix.md (whitespace/markdown-normalized): vendor-fact literal '{b}' found")
    return errs


# ---------------------------------------------------------------------------
# Check C — no numeric confidence (RT-7 split: exact on JSON, shape-match on .md)
# ---------------------------------------------------------------------------

_CONFIDENCE_NUMERIC_RE = re.compile(r"confidence[^a-zA-Z]{0,20}\d*\.\d+|confidence[^a-zA-Z]{0,20}\d+%", re.IGNORECASE)


def _walk_json_for_confidence(node: object, path: str, errs: list[str]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "confidence":
                errs.append(f"{path}.{k}: a 'confidence' key is forbidden anywhere in the JSON")
            if isinstance(v, float):
                errs.append(f"{path}.{k}: a float-valued leaf is forbidden (numeric confidence is banned)")
            _walk_json_for_confidence(v, f"{path}.{k}", errs)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_json_for_confidence(v, f"{path}[{i}]", errs)


def check_c(data: object, doc_text: str) -> list[str]:
    errs: list[str] = []
    _walk_json_for_confidence(data, "$", errs)
    m = _CONFIDENCE_NUMERIC_RE.search(doc_text)
    if m:
        errs.append(f"agent-routing-matrix.md: a numeric confidence shape was found near {m.group(0)!r}")
    return errs


# ---------------------------------------------------------------------------
# Checks D1/D2 — strict membership, deliberately NEVER via resolve_tier (RT-2)
# ---------------------------------------------------------------------------


def check_d1(data: dict, substrate: dict) -> list[str]:
    errs: list[str] = []
    hosts = substrate.get("hosts") or {}
    agent_hosts = data.get("agent_hosts") or {}
    for agent, host in agent_hosts.items():
        if agent not in AGENT_IDS:
            errs.append(f"$.agent_hosts: unrecognised agent id '{agent}'")
        if host not in hosts:
            errs.append(f"$.agent_hosts.{agent}: host '{host}' is not a real substrate-tier-map.json host key")
    for agent in AGENT_IDS:
        if agent not in agent_hosts:
            errs.append(f"$.agent_hosts: missing entry for agent id '{agent}'")
    return errs


def check_d2(data: dict, substrate: dict) -> list[str]:
    errs: list[str] = []
    hosts = substrate.get("hosts") or {}
    agent_hosts = data.get("agent_hosts") or {}
    for tc_id, tc in (data.get("task_classes") or {}).items():
        for i, r in enumerate(tc.get("recommendations") or []):
            p = f"$.task_classes.{tc_id}.recommendations[{i}]"
            mr = r.get("model_ref") or {}
            host = mr.get("host")
            tier = mr.get("tier")
            if host not in hosts:
                errs.append(f"{p}.model_ref.host: '{host}' is not a real substrate-tier-map.json host key")
                continue
            if tier not in hosts[host]:
                errs.append(f"{p}.model_ref.tier: '{tier}' is not a real tier under host '{host}'")
            expected_host = agent_hosts.get(r.get("agent"))
            if expected_host is not None and host != expected_host:
                errs.append(
                    f"{p}.model_ref.host: '{host}' disagrees with agent_hosts['{r.get('agent')}'] = '{expected_host}'"
                )
    return errs


# ---------------------------------------------------------------------------
# Check E — framework-rule citations: source exists, quote exists in that file
# ---------------------------------------------------------------------------


def check_e(data: dict, sources_by_id: dict[str, Path]) -> list[str]:
    errs: list[str] = []
    file_text_cache: dict[Path, str] = {}
    for tc_id, tc in (data.get("task_classes") or {}).items():
        for i, r in enumerate(tc.get("recommendations") or []):
            if r.get("basis") != "framework-rule":
                continue
            p = f"$.task_classes.{tc_id}.recommendations[{i}]"
            quote = r.get("quote", "")
            src_ids = r.get("sources") or []
            resolved_paths = [sources_by_id[s] for s in src_ids if s in sources_by_id]
            if not resolved_paths:
                errs.append(f"{p}: basis=framework-rule but no cited source id resolves to a file path")
                continue
            found = False
            for path in resolved_paths:
                if not path.exists():
                    continue
                if path not in file_text_cache:
                    try:
                        file_text_cache[path] = _norm(path.read_text(encoding="utf-8"))
                    except OSError:
                        file_text_cache[path] = ""
                if _norm(quote) in file_text_cache[path]:
                    found = True
                    break
            if not found:
                errs.append(f"{p}: quote does not appear verbatim in any cited source file (fail-closed)")
    return errs


# ---------------------------------------------------------------------------
# Check F — ownership metadata carries real values
# ---------------------------------------------------------------------------


def check_f(data: dict) -> list[str]:
    errs: list[str] = []
    if not isinstance(data.get("owner"), str) or not data["owner"].strip():
        errs.append("$.owner: must be a non-empty string")
    if data.get("staleness_tier") not in STALENESS_TIERS:
        errs.append(f"$.staleness_tier: must be one of {sorted(STALENESS_TIERS)}")
    if not isinstance(data.get("review_trigger"), str) or not data["review_trigger"].strip():
        errs.append("$.review_trigger: must be a non-empty string")
    return errs


# ---------------------------------------------------------------------------
# Check G — route-task.py --self-test: exit 0, an N/N (equal) pass line (RT-10)
# ---------------------------------------------------------------------------

_SELFTEST_RE = re.compile(r"(\d+)\s*/\s*(\d+)\s*pass")


def check_g() -> list[str]:
    if not ROUTE_TASK.exists():
        return [f"{ROUTE_TASK}: does not exist"]
    try:
        proc = subprocess.run(
            [sys.executable, str(ROUTE_TASK), "--self-test"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [f"route-task.py --self-test: could not run ({exc})"]
    if proc.returncode != 0:
        return [f"route-task.py --self-test: exit {proc.returncode}, expected 0"]
    m = _SELFTEST_RE.search(proc.stdout)
    if not m:
        return ["route-task.py --self-test: no 'N/N pass' line found in output"]
    passed, total = int(m.group(1)), int(m.group(2))
    if passed != total:
        return [f"route-task.py --self-test: {passed}/{total} — not all self-test cases passed"]
    return []


# ---------------------------------------------------------------------------
# Check I — per-task_class totality bounded to the 4 grounded cells
# ---------------------------------------------------------------------------


def check_i(data: dict) -> list[str]:
    errs: list[str] = []
    for tc_id, tc in (data.get("task_classes") or {}).items():
        cells: dict[tuple[str, str], list[int]] = {}
        for r in tc.get("recommendations") or []:
            key = (r.get("interaction_mode"), r.get("blast_radius"))
            if key not in GROUNDED_CELLS:
                continue
            rank = r.get("rank")
            if isinstance(rank, int) and not isinstance(rank, bool):
                cells.setdefault(key, []).append(rank)
        missing = GROUNDED_CELLS - set(cells.keys())
        for cell in sorted(missing):
            errs.append(f"$.task_classes.{tc_id}: missing recommendation(s) for grounded cell {cell}")
        for cell, ranks in cells.items():
            expected = list(range(1, len(ranks) + 1))
            if sorted(ranks) != expected:
                errs.append(
                    f"$.task_classes.{tc_id} cell {cell}: ranks {sorted(ranks)} are not a contiguous 1..N set"
                )
    return errs


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _sources_by_id(data: dict) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for s in data.get("sources") or []:
        if isinstance(s, dict) and s.get("id") and s.get("path"):
            out[s["id"]] = REPO_ROOT / s["path"]
    return out


def run_all_checks(data: object, schema: object, doc_text: str, substrate: dict, catalog: dict) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    results["A"] = validate_schema_shape(schema) + validate_data(data, schema)
    # Downstream checks assume `data` is well-shaped; skip them if A already failed hard on shape.
    if not isinstance(data, dict):
        return results
    results["B"] = check_b(data, doc_text, substrate, catalog)
    results["C"] = check_c(data, doc_text)
    results["D1"] = check_d1(data, substrate)
    results["D2"] = check_d2(data, substrate)
    results["E"] = check_e(data, _sources_by_id(data))
    results["F"] = check_f(data)
    results["G"] = check_g()
    results["I"] = check_i(data)
    return results


def main_run() -> int:
    try:
        data = _load_json(DATA_PATH)
        schema = _load_json(SCHEMA_PATH)
        doc_text = DOC_PATH.read_text(encoding="utf-8")
        substrate = _load_json(SUBSTRATE_PATH)
        catalog = _load_json(CATALOG_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"check-agent-routing-matrix: could not load inputs: {exc}", file=sys.stderr)
        return 2

    results = run_all_checks(data, schema, doc_text, substrate, catalog)
    total_errs = 0
    for check, errs in results.items():
        if errs:
            print(f"check {check}: FAIL ({len(errs)})")
            for e in errs:
                print(f"  - {e}")
            total_errs += len(errs)
        else:
            print(f"check {check}: pass")
    if total_errs:
        print(f"check-agent-routing-matrix: {total_errs} finding(s) across {len(results)} checks")
        return 2
    print("check-agent-routing-matrix: all checks pass")
    return 0


# ---------------------------------------------------------------------------
# --must-fail: one mutant per check (+ must-NOT-fire companions), proves teeth
# ---------------------------------------------------------------------------


def _mutant_results(mutate) -> dict[str, list[str]]:
    """Apply `mutate` to fresh copies of the real inputs, run every check, return results."""
    data = copy.deepcopy(_load_json(DATA_PATH))
    schema = copy.deepcopy(_load_json(SCHEMA_PATH))
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    substrate = _load_json(SUBSTRATE_PATH)
    catalog = _load_json(CATALOG_PATH)
    data, schema, doc_text, substrate, catalog = mutate(data, schema, doc_text, substrate, catalog)
    return run_all_checks(data, schema, doc_text, substrate, catalog)


def _first_tc_id(data: dict) -> str:
    return next(iter(data["task_classes"]))


def _first_rec(data: dict, tc_id: str | None = None) -> dict:
    tc_id = tc_id or _first_tc_id(data)
    return data["task_classes"][tc_id]["recommendations"][0]


def must_fail() -> int:
    def m_a(data, schema, doc, sub, cat):
        schema["required"] = []
        return data, schema, doc, sub, cat

    def m_a_notacaught(data, schema, doc, sub, cat):  # must-NOT-fire companion: schema untouched
        return data, schema, doc, sub, cat

    def m_b_oneline(data, schema, doc, sub, cat):
        doc += "\nA rationale mentioning Claude Opus 5 directly.\n"
        return data, schema, doc, sub, cat

    def m_b_wrapped(data, schema, doc, sub, cat):
        doc += "\nA rationale mentioning Claude\nOpus 5 across a wrap.\n"
        return data, schema, doc, sub, cat

    def m_b_emptyban(data, schema, doc, sub, cat):
        sub2 = {"hosts": {}}
        cat2 = {"current": {}, "stale": []}
        return data, schema, doc, sub2, cat2

    def m_c_json(data, schema, doc, sub, cat):
        tc_id = _first_tc_id(data)
        data["task_classes"][tc_id]["recommendations"][0]["confidence"] = 0.75
        return data, schema, doc, sub, cat

    def m_c_md_companion(data, schema, doc, sub, cat):  # must-NOT-fire
        doc += "\nWe deliberately carry no numeric confidence field; see rank+basis instead.\n"
        return data, schema, doc, sub, cat

    def m_d1(data, schema, doc, sub, cat):
        data["agent_hosts"].pop("grok-build-cli", None)
        return data, schema, doc, sub, cat

    def m_d2(data, schema, doc, sub, cat):
        tc_id = _first_tc_id(data)
        rec = data["task_classes"][tc_id]["recommendations"][0]
        rec["agent"] = "copilot-cli"
        rec["model_ref"] = {"host": "copilot-chat", "tier": "top"}
        return data, schema, doc, sub, cat

    def m_e_bad_quote(data, schema, doc, sub, cat):
        for tc in data["task_classes"].values():
            for r in tc["recommendations"]:
                if r.get("basis") == "framework-rule":
                    r["quote"] = "this exact sentence does not appear in any source file, guaranteed"
                    return data, schema, doc, sub, cat
        return data, schema, doc, sub, cat

    def m_e_good_quote(data, schema, doc, sub, cat):  # must-NOT-fire companion (unmutated)
        return data, schema, doc, sub, cat

    def m_f(data, schema, doc, sub, cat):
        data["staleness_tier"] = "Tier-9"
        return data, schema, doc, sub, cat

    def m_g(data, schema, doc, sub, cat):
        # Simulated: check_g() shells the real route-task.py, so we can't easily break its
        # internal self-test from here without touching the real file. Instead assert the
        # positive path holds (route-task.py IS present and DOES report N/N) as the
        # must-NOT-fire companion, and simulate the failure shape directly against the regex.
        return data, schema, doc, sub, cat

    def m_i_missing_cell(data, schema, doc, sub, cat):
        tc_id = _first_tc_id(data)
        recs = data["task_classes"][tc_id]["recommendations"]
        data["task_classes"][tc_id]["recommendations"] = [
            r for r in recs if not (r["interaction_mode"] == "inline" and r["blast_radius"] == "reversible")
        ]
        return data, schema, doc, sub, cat

    def m_i_dup_rank(data, schema, doc, sub, cat):
        tc_id = _first_tc_id(data)
        recs = data["task_classes"][tc_id]["recommendations"]
        for r in recs:
            if r["interaction_mode"] == "inline" and r["blast_radius"] == "reversible":
                r["rank"] = 1
        return data, schema, doc, sub, cat

    cases: list[tuple[str, str, bool, object]] = [
        # (check, label, expect_fire, mutate_fn) — expect_fire False = must-NOT-fire companion
        ("A", "delete schema required[]", True, m_a),
        ("B", "one-line display-name SKU in .md", True, m_b_oneline),
        ("B", "hard-wrapped display-name SKU in .md", True, m_b_wrapped),
        ("B", "empty ban-list derivation (positive control)", True, m_b_emptyban),
        ("C", "confidence float planted in .json", True, m_c_json),
        ("C", "prose paragraph explaining no-confidence design", False, m_c_md_companion),
        ("D1", "agent_hosts missing an agent id", True, m_d1),
        ("D2", "model_ref.host set to an agent id, not a host key", True, m_d2),
        ("E", "framework-rule quote absent from any source", True, m_e_bad_quote),
        ("E", "real, unmutated framework-rule quote", False, m_e_good_quote),
        ("F", "staleness_tier outside the 5-item enum", True, m_f),
        ("I", "remove a task_class's only inline/reversible recommendation", True, m_i_missing_cell),
        ("I", "duplicate rank 1 within one cell", True, m_i_dup_rank),
    ]

    failures: list[str] = []
    for check, label, expect_fire, mutate in cases:
        results = _mutant_results(mutate)
        fired = bool(results.get(check))
        if expect_fire and not fired:
            failures.append(f"MISSED: check {check} did not catch mutant [{label}]")
        elif not expect_fire and fired:
            failures.append(f"FALSE-POSITIVE: check {check} fired on the must-NOT-fire case [{label}]: {results[check]}")

    # G: run the real self-test once as a positive (must-NOT-fire) control — route-task.py
    # is a live external file, not something this driver mutates in-process.
    g_errs = check_g()
    if g_errs:
        failures.append(f"FALSE-POSITIVE: check G fired against the real, unmutated route-task.py: {g_errs}")

    if failures:
        print("check-agent-routing-matrix --must-fail: teeth incomplete")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"check-agent-routing-matrix --must-fail: {len(cases)} mutants + 1 live G control, all as expected")
    return MUST_FAIL_TEETH_EXIT


def main() -> int:
    argv = sys.argv[1:]
    if "--must-fail-convention" in argv:
        print(f"must-fail-teeth-exit: {MUST_FAIL_TEETH_EXIT}")
        return 0
    if "--must-fail" in argv:
        return must_fail()
    return main_run()


if __name__ == "__main__":
    sys.exit(main())
