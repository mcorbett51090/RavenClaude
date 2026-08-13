#!/usr/bin/env python3
"""
powerbi_ingest.py — report-regeneration `powerbi-ingest` skill: a PIPELINE-facing
adapter over the Phase-0 `powerbi_probe.py` probe. Where the probe answers "can we
reach Power BI at all" (a one-shot CLI receipt), this adapter answers the pipeline's
actual question: "given a Binding Manifest, produce the artifact the next stage
needs" — either a new-data fragment (`data` mode) or an embedded screenshot for a
`regenerate`-class node (`shot` mode).

Two pipeline-facing modes (per core-architecture-spec.md sec 3/sec 4/sec 5 and
knowledge/powerbi-ingest-contract.md sec 3/sec 4):

  data  — run every `dax`-kind binding in a Binding Manifest via the SAME REST
          `executeQueries` mechanics the probe uses (service-principal/token from
          ENV ONLY), and assemble a data.json-shaped FRAGMENT
          (`dataset_id`/`period`/`values`, keyed by each binding's
          `data_query.expression` — the exact key report-fidelity-harness's V1 leg
          indexes new-data by, see harness.py leg_v1()) with `source_period`
          stamped on the top-level `period` AND on every value. This is what makes
          a PBI-sourced figure a genuinely independent V1 recompute source: a fresh
          HTTP round-trip per binding, never a cached result from manifest-build
          time (contract sec 3).

  shot  — capture a fresh Power BI report image via `powerbi_probe.probe_shot()`
          (ExportToFile primary, Playwright fallback — unchanged mechanics), then
          package it as the embedded image for a `regenerate`-class PBI node:
          node_id + path + `source_period` stamped, so the fidelity harness's
          period-coherence leg can catch a stale screenshot under a fresh period
          header (contract sec 4 / core-architecture-spec.md sec 5 "+period-coherence").
          `period_coherence_checked` is always false on a successful capture — this
          adapter proves capture feasibility + period ATTRIBUTION, never period
          CORRECTNESS; that check is report-fidelity-harness's job.

Fail-closed contract (binding, inherited from the probe verbatim — see
scripts/powerbi_probe.py's own module docstring for the full rationale):
  - No creds / no route / no resolvable source_period => `verdict: "not_captured"`,
    NEVER a fabricated PASS, NEVER a guessed period. `data` mode names the
    manual-figure-labeled-unverified fallback (contract sec 3); `shot` mode names
    the user-provided-image fallback (contract sec 4/5) — same vocabulary as the
    probe's own `shot` receipt.
  - Tokens are read from env vars ONLY (POWERBI_ACCESS_TOKEN / POWERBI_WORKSPACE_ID
    / POWERBI_DATASET_ID, same as the probe) and are NEVER printed, logged, or
    embedded in any returned/written structure — only `"present": true/false`.
  - No network call happens on `import powerbi_ingest` — every network-capable
    branch is inside a subcommand function, invoked only from `main()`. This
    script does NOT auto-run.
  - A DAX result that is NULL, or a query that returns more than one row (this
    adapter only extracts a single scalar per binding, per the
    `EVALUATE ROW("value", [Measure])` convention `rebind-manifest` proposes), is
    a FAILURE for that binding, never a silently-picked first row — ambiguity
    fails closed, it is never resolved by guessing.

What this adapter deliberately does NOT do (documented, not left implicit):
  - It does not validate the manifest against `binding-manifest.schema.json`
    (rebind-manifest's job — this stage trusts an already-valid manifest and only
    duck-types the shape it needs: `bindings[].data_query.kind/expression` and
    `bindings[].provenance.source_period`).
  - It does not run the period-coherence check itself (report-fidelity-harness's
    job) — `shot` mode only guarantees the embed carries an attributed period to
    check AGAINST; it proves attribution, not correctness.
  - It supports exactly ONE target semantic model per invocation
    (POWERBI_WORKSPACE_ID/POWERBI_DATASET_ID), mirroring the probe's own
    single-dataset design. A manifest whose dax-kind bindings' `data_query.source_ref`
    disagrees with the env dataset is not an error (source_ref may be a label, not
    a literal GUID) but is surfaced under `source_ref_mismatches` for a human to
    check — see "what breaks next" in SKILL.md.

Run:
  python3 powerbi_ingest.py data --manifest <manifest.json> [--source-period Q1] \
      [--out <data-fragment.json>] [--receipt-out <receipt.json>] [--format json|text] [--pretty]
  python3 powerbi_ingest.py shot --manifest <manifest.json> --node-id <id> \
      [--source-period Q1] [--out <capture-out-path-hint>] [--receipt-out <receipt.json>] \
      [--format json|text] [--pretty]

Exit codes: `0` — ran to completion (`verdict` field carries PASS / PARTIAL /
not_captured — mirrors powerbi_probe.py's own "always exit 0, verdict carries the
signal" contract, since both are fundamentally network-dependent and fail-closed
by design); `2` — usage / path-guard / manifest-parse / bad-`--node-id` error (a
caller bug, not a network condition).

Constraints (binding, per the plugin constitution): stdlib only (argparse / json /
os / re / sys / pathlib). No pip, no third-party imports beyond the sibling
`powerbi_probe` module. Runs on Python 3.9.6 (`from __future__ import annotations`;
no `X | Y` runtime types, no match statement). Path-guarded (rejects `..`
traversal). No network at import.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# The sibling probe (scripts/powerbi_probe.py) — shared HTTP mechanics
# (execute_dax_query) and the unchanged shot capture (probe_shot). Mirrors
# report-fidelity-harness/harness.py's own sys.path pattern for reaching
# ../../scripts from a skill directory.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import powerbi_probe as pb  # noqa: E402

SCHEMA_DATA_FRAGMENT = "report-regeneration/powerbi-ingest-data@1"
SCHEMA_SHOT_EMBED = "report-regeneration/powerbi-ingest-shot@1"

_DATA_FALLBACK_MSG = (
    "no live Power BI data route -- per knowledge/powerbi-ingest-contract.md sec 3, a human "
    "either supplies the figure(s) manually (labeled unverified) or the route is restored "
    "(set POWERBI_ACCESS_TOKEN / POWERBI_WORKSPACE_ID / POWERBI_DATASET_ID); V1 degrades from "
    "value-accuracy to binding-correctness-only for the affected node(s), never a fake PASS"
)

_SHOT_FALLBACK_MSG = (
    "user-provided image (always-available fallback per core-architecture-spec.md sec 4/sec 6 "
    "step 4 -- a human supplies the screenshot; it is classed regenerate exactly like an "
    "auto-captured one and MUST still pass the identical period-coherence gate)"
)


class IngestError(Exception):
    """Raised for path-guard / parse / usage failures (exit 2, never a fake pass)."""


# ── path safety (mirrors skills/rebind-manifest/build_manifest.py's guard) ──

def _guard_path(raw: str, *, must_exist: bool) -> Path:
    if not raw:
        raise IngestError("empty path")
    p = Path(raw)
    if ".." in p.parts:
        raise IngestError(f"path traversal ('..') is not allowed: {raw!r}")
    resolved = p if p.is_absolute() else (Path.cwd() / p)
    resolved = resolved.resolve()
    if must_exist and not resolved.is_file():
        raise IngestError(f"input file not found: {raw!r} (resolved {resolved})")
    return resolved


def _load_manifest(path: Path) -> dict:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise IngestError(f"could not read/parse manifest {str(path)!r}: {type(exc).__name__}: {exc}") from exc
    if not isinstance(doc, dict):
        raise IngestError(f"manifest {str(path)!r} must be a JSON object")
    bindings = doc.get("bindings")
    if not isinstance(bindings, list):
        raise IngestError(f"manifest {str(path)!r} has no 'bindings' array (not a valid Binding Manifest)")
    return doc


# ── `data` mode — run manifest dax-kind bindings, assemble a new-data fragment ──

_RE_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[T ].*)?$")
_RE_PERIOD_YQ = re.compile(r"^\d{4}-Q[1-4]$", re.I)
_RE_PERIOD_QY = re.compile(r"^Q[1-4]\s?\d{4}$", re.I)


def _format_number(n: Any) -> str:
    """Render a numeric DAX result as a canon_number()-parseable string (see
    report-fidelity-harness/harness.py canon_number: strips $ , % then float()s)."""
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        return str(int(n)) if n.is_integer() else repr(n)
    return str(n)


def infer_type_and_value(raw: Any) -> tuple:
    """
    Infer a harness-compatible (type, value-as-string) pair from a raw DAX JSON
    scalar. Deliberately CONSERVATIVE: only date/period are pattern-detected from
    an actual string shape; every numeric result is labeled 'number' (never
    guessed as 'currency' or 'percent' from magnitude/column-name heuristics --
    see SKILL.md "what breaks next" for the percent-fraction caveat this does
    NOT attempt to auto-correct). report-fidelity-harness's canon_number()
    normalizes currency/percent/number identically once symbols are stripped, so
    a plain numeric string composes correctly PROVIDED the underlying magnitude
    already matches what the regenerate stage will render.
    """
    if isinstance(raw, bool):
        return "string", str(raw)
    if isinstance(raw, (int, float)):
        return "number", _format_number(raw)
    if isinstance(raw, str):
        s = raw.strip()
        if _RE_ISO_DATE.match(s):
            return "date", s[:10]
        if _RE_PERIOD_YQ.match(s):
            return "period", s
        if _RE_PERIOD_QY.match(s):
            return "period", s.upper()
        return "string", s
    return "string", str(raw)


def _dax_bindings(bindings: list) -> list:
    out = []
    for b in bindings:
        if not isinstance(b, dict):
            continue
        dq = b.get("data_query")
        if isinstance(dq, dict) and dq.get("kind") == "dax" and dq.get("expression"):
            out.append(b)
    return out


def _modal_period(bindings: list) -> str | None:
    """The first non-null provenance.source_period in document (list) order --
    mirrors report-fidelity-harness/harness.py leg_period()'s own fallback
    ("the modal provenance period declared in the manifest") EXACTLY, so this
    adapter's default agrees with what the harness would fall back to anyway."""
    for b in bindings:
        p = (b.get("provenance") or {}).get("source_period")
        if p:
            return p
    return None


def ingest_data(manifest_path: Path, *, source_period: str | None = None,
                 out_path: Path | None = None) -> dict:
    """
    Run every `dax`-kind binding in `manifest_path` via powerbi_probe.execute_dax_query()
    (REST executeQueries, service-principal/token from ENV ONLY) and assemble a
    data.json-shaped fragment: {"dataset_id", "period", "values": {expression:
    {"value","type","period"}}}. Never raises for a network/credentials condition
    (fail-closed => `verdict: "not_captured"` in the returned receipt); raises
    IngestError only for a bad manifest (a caller bug, exit 2 at the CLI).
    """
    manifest = _load_manifest(manifest_path)
    bindings = manifest["bindings"]

    receipt: dict[str, Any] = {
        "schema": SCHEMA_DATA_FRAGMENT,
        "verdict": "not_captured",
        "reason": None,
        "fallback": None,
        "manifest": str(manifest_path),
        "env": {
            "POWERBI_ACCESS_TOKEN": {"present": pb._env_present("POWERBI_ACCESS_TOKEN")},
            "POWERBI_WORKSPACE_ID": {"present": bool(pb._env("POWERBI_WORKSPACE_ID"))},
            "POWERBI_DATASET_ID": {"present": bool(pb._env("POWERBI_DATASET_ID"))},
        },
        "bindings_total": len(bindings),
        "bindings_dax": 0,
        "succeeded": [],
        "failed": [],
        "source_ref_mismatches": [],
        "fragment": None,
        "fragment_path": None,
    }

    dax_bindings = _dax_bindings(bindings)
    receipt["bindings_dax"] = len(dax_bindings)
    if not dax_bindings:
        receipt["reason"] = "manifest has no dax-kind bindings -- nothing to ingest from Power BI for this run"
        return receipt

    canonical_period = source_period or _modal_period(dax_bindings)
    if not canonical_period:
        receipt["reason"] = (
            "no source_period resolvable (neither --source-period nor any dax-kind binding's "
            "provenance.source_period) -- refusing to stamp an unattributed value; "
            "period-coherence cannot be honestly asserted without one"
        )
        receipt["fallback"] = _DATA_FALLBACK_MSG
        return receipt

    workspace_id = pb._env("POWERBI_WORKSPACE_ID")
    dataset_id = pb._env("POWERBI_DATASET_ID")
    token_present = pb._env_present("POWERBI_ACCESS_TOKEN")
    missing = [
        name for name, present in (
            ("POWERBI_ACCESS_TOKEN", token_present),
            ("POWERBI_WORKSPACE_ID", bool(workspace_id)),
            ("POWERBI_DATASET_ID", bool(dataset_id)),
        )
        if not present
    ]
    if missing:
        receipt["reason"] = f"missing required env var(s): {', '.join(missing)}"
        receipt["fallback"] = _DATA_FALLBACK_MSG
        return receipt

    values: dict[str, dict] = {}
    for b in dax_bindings:
        node_id = b.get("node_id", "<unknown>")
        dq = b["data_query"]
        expr = dq["expression"]
        source_ref = dq.get("source_ref")
        if source_ref and source_ref != dataset_id:
            receipt["source_ref_mismatches"].append(
                {"node_id": node_id, "data_query_source_ref": source_ref, "used_dataset_id": dataset_id}
            )
        period = source_period or (b.get("provenance") or {}).get("source_period") or canonical_period
        entry: dict[str, Any] = {"node_id": node_id, "expression": expr}

        outcome = pb.execute_dax_query(expr, workspace_id=workspace_id, dataset_id=dataset_id,
                                        token=pb._env("POWERBI_ACCESS_TOKEN"))
        if not outcome["ok"]:
            entry["reason"] = outcome["reason"]
            receipt["failed"].append(entry)
            continue

        row_count = outcome["row_count"] or 0
        if row_count == 0:
            entry["reason"] = "DAX query returned zero rows"
            receipt["failed"].append(entry)
            continue
        if row_count > 1:
            entry["reason"] = (
                f"DAX query returned {row_count} rows; scalar extraction expects exactly 1 -- "
                "refusing to silently pick the first"
            )
            receipt["failed"].append(entry)
            continue

        first_row = outcome["first_row"]
        if not first_row:
            entry["reason"] = "DAX query's single row had no columns to extract"
            receipt["failed"].append(entry)
            continue
        raw = first_row[next(iter(first_row))]
        if raw is None:
            entry["reason"] = "DAX query returned NULL"
            receipt["failed"].append(entry)
            continue

        vtype, vstr = infer_type_and_value(raw)
        if expr in values and values[expr] != {"value": vstr, "type": vtype, "period": period}:
            entry["reason"] = (
                f"expression {expr!r} already ingested with a different value/type/period from "
                "another binding -- refusing to silently overwrite"
            )
            receipt["failed"].append(entry)
            continue

        values[expr] = {"value": vstr, "type": vtype, "period": period}
        entry.update({
            "value": vstr, "type": vtype, "period": period,
            "http_status": outcome["http_status"], "elapsed_ms": outcome["elapsed_ms"],
        })
        receipt["succeeded"].append(entry)

    if not values:
        receipt["reason"] = "every dax-kind binding failed (see `failed`); no live V1 source produced"
        receipt["fallback"] = _DATA_FALLBACK_MSG
        return receipt

    fragment = {"dataset_id": dataset_id, "period": canonical_period, "values": values}
    receipt["fragment"] = fragment
    receipt["verdict"] = "PASS" if not receipt["failed"] else "PARTIAL"
    if receipt["failed"]:
        receipt["reason"] = (
            f"{len(receipt['failed'])} of {len(dax_bindings)} dax-kind binding(s) did not "
            "produce a value (see `failed`); V1 degrades to binding-correctness-only for those nodes"
        )

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(fragment, indent=2) + "\n", encoding="utf-8")
        receipt["fragment_path"] = str(out_path)

    return receipt


# ── `shot` mode — capture + package as a regenerate-node embed ──

def ingest_shot(node_id: str, manifest_path: Path, *, source_period: str | None = None,
                 out_path_hint: str | None = None) -> dict:
    """
    Look up `node_id` in the Binding Manifest, resolve a source_period (CLI
    override, else the binding's own provenance.source_period), then capture a
    fresh Power BI report image via powerbi_probe.probe_shot() (UNCHANGED
    mechanics — ExportToFile primary, Playwright fallback, same env-var
    contract). Packages the result as the embedded image for a
    `regenerate`-class PBI node. Raises IngestError only if `node_id` is not
    found in the manifest (a caller bug, exit 2); every network/credentials/
    capture condition fails closed into the returned receipt's `verdict`.
    """
    manifest = _load_manifest(manifest_path)
    bindings = manifest["bindings"]
    binding = next((b for b in bindings if isinstance(b, dict) and b.get("node_id") == node_id), None)
    if binding is None:
        raise IngestError(f"node_id {node_id!r} not found in manifest {str(manifest_path)!r}")

    receipt: dict[str, Any] = {
        "schema": SCHEMA_SHOT_EMBED,
        "verdict": "not_captured",
        "node_id": node_id,
        "class": "regenerate",
        "route": None,
        "path": None,
        "source_period": None,
        "period_coherence_checked": False,
        "reason": None,
        "fallback": None,
        "warnings": [],
        "probe": None,
    }

    prov = binding.get("provenance") or {}
    if binding.get("class") != "regenerate" or prov.get("pbi_route") != "screenshot":
        receipt["warnings"].append(
            f"binding {node_id!r} is class={binding.get('class')!r} pbi_route={prov.get('pbi_route')!r} "
            "-- expected class='regenerate' pbi_route='screenshot' for a PBI screenshot node "
            "(core-architecture-spec.md sec 4 construction rule); proceeding anyway, this adapter "
            "does not own manifest-classification correctness"
        )

    resolved_period = source_period or prov.get("source_period")
    if not resolved_period:
        receipt["reason"] = (
            "no source_period resolvable (neither --source-period nor the manifest binding's "
            "provenance.source_period) -- refusing to produce an unstamped screenshot embed; the "
            "stale-screenshot period-coherence guard requires it (knowledge/powerbi-ingest-contract.md sec 4)"
        )
        receipt["fallback"] = _SHOT_FALLBACK_MSG
        return receipt
    receipt["source_period"] = resolved_period

    restore_env: str | None = None
    had_env = "POWERBI_SHOT_OUT_PATH" in os.environ
    if out_path_hint is not None:
        restore_env = os.environ.get("POWERBI_SHOT_OUT_PATH")
        os.environ["POWERBI_SHOT_OUT_PATH"] = out_path_hint
    try:
        probe_receipt = pb.probe_shot()
    finally:
        if out_path_hint is not None:
            if had_env:
                os.environ["POWERBI_SHOT_OUT_PATH"] = restore_env  # type: ignore[assignment]
            else:
                os.environ.pop("POWERBI_SHOT_OUT_PATH", None)

    receipt["probe"] = probe_receipt  # already token-free; kept whole for observability
    if probe_receipt["verdict"] == "PASS":
        receipt.update({
            "verdict": "PASS",
            "route": probe_receipt["route"],
            "path": probe_receipt["path"],
            "reason": None,
            "fallback": None,
        })
    else:
        receipt["reason"] = probe_receipt["reason"]
        receipt["fallback"] = probe_receipt.get("fallback") or _SHOT_FALLBACK_MSG
    return receipt


# ── CLI ──

def _print_human_data(receipt: dict) -> None:
    print(f"powerbi_ingest [data] — verdict: {receipt['verdict']}")
    print(f"  manifest: {receipt['manifest']}")
    print(f"  dax bindings: {receipt['bindings_dax']} of {receipt['bindings_total']} total "
          f"(succeeded {len(receipt['succeeded'])}, failed {len(receipt['failed'])})")
    if receipt["fragment"]:
        print(f"  period: {receipt['fragment']['period']}  dataset_id: {receipt['fragment']['dataset_id']}")
    if receipt["fragment_path"]:
        print(f"  fragment written: {receipt['fragment_path']}")
    if receipt["reason"]:
        print(f"  reason: {receipt['reason']}")
    if receipt["fallback"]:
        print(f"  fallback: {receipt['fallback']}")
    for m in receipt["source_ref_mismatches"]:
        print(f"  ! source_ref mismatch: {m}")


def _print_human_shot(receipt: dict) -> None:
    print(f"powerbi_ingest [shot] — verdict: {receipt['verdict']}")
    print(f"  node_id: {receipt['node_id']}  class: {receipt['class']}")
    print(f"  route: {receipt['route']}  path: {receipt['path']}")
    print(f"  source_period: {receipt['source_period']}  "
          f"period_coherence_checked: {receipt['period_coherence_checked']}")
    if receipt["reason"]:
        print(f"  reason: {receipt['reason']}")
    if receipt["fallback"]:
        print(f"  fallback: {receipt['fallback']}")
    for w in receipt["warnings"]:
        print(f"  ! {w}")


def _write_receipt_out(receipt: dict, raw: str | None) -> Path | None:
    if raw is None:
        return None
    out = _guard_path(raw, must_exist=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="powerbi_ingest.py",
        description="report-regeneration powerbi-ingest: pipeline-facing Power BI adapter -- "
                    "data (manifest dax bindings -> new-data fragment) and shot (ExportToFile "
                    "capture -> regenerate-node embed), both source_period-stamped.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_data = sub.add_parser("data", help="Run manifest dax-kind bindings; emit a new-data fragment.")
    p_data.add_argument("--manifest", required=True, metavar="PATH", help="Binding Manifest JSON")
    p_data.add_argument("--source-period", dest="source_period", metavar="PERIOD",
                        help="override the stamped period (default: modal provenance.source_period "
                             "across the manifest's dax-kind bindings)")
    p_data.add_argument("--out", metavar="PATH", help="write the data.json-shaped fragment here")
    p_data.add_argument("--receipt-out", dest="receipt_out", metavar="PATH",
                        help="also write the full receipt (fragment + per-binding detail) here")
    p_data.add_argument("--format", choices=["json", "text"], default="json")
    p_data.add_argument("--pretty", action="store_true")

    p_shot = sub.add_parser("shot", help="Capture a fresh PBI report image; emit a regenerate-node embed.")
    p_shot.add_argument("--manifest", required=True, metavar="PATH", help="Binding Manifest JSON")
    p_shot.add_argument("--node-id", dest="node_id", required=True, metavar="ID",
                        help="the manifest binding node_id this capture is for")
    p_shot.add_argument("--source-period", dest="source_period", metavar="PERIOD",
                        help="override the stamped period (default: the binding's own "
                             "provenance.source_period)")
    p_shot.add_argument("--out", metavar="PATH", help="capture output path hint "
                        "(forwarded as POWERBI_SHOT_OUT_PATH to the underlying probe)")
    p_shot.add_argument("--receipt-out", dest="receipt_out", metavar="PATH",
                        help="also write the full receipt here")
    p_shot.add_argument("--format", choices=["json", "text"], default="json")
    p_shot.add_argument("--pretty", action="store_true")

    return p


def _emit_error(message: str) -> None:
    print(json.dumps({"schema": "report-regeneration/powerbi-ingest-error@1", "ok": False, "error": message}))
    print(f"[error] {message}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        manifest_path = _guard_path(args.manifest, must_exist=True)
    except IngestError as exc:
        _emit_error(str(exc))
        return 2

    try:
        if args.command == "data":
            out_path = _guard_path(args.out, must_exist=False) if args.out else None
            receipt = ingest_data(manifest_path, source_period=args.source_period, out_path=out_path)
        else:
            receipt = ingest_shot(args.node_id, manifest_path, source_period=args.source_period,
                                  out_path_hint=args.out)
    except IngestError as exc:
        _emit_error(str(exc))
        return 2

    _write_receipt_out(receipt, getattr(args, "receipt_out", None))

    if args.format == "text":
        if args.command == "data":
            _print_human_data(receipt)
        else:
            _print_human_shot(receipt)
    else:
        print(json.dumps(receipt, indent=2 if args.pretty else None))

    return 0  # verdict field carries PASS/PARTIAL/not_captured -- mirrors the probe's own contract


if __name__ == "__main__":
    sys.exit(main())
