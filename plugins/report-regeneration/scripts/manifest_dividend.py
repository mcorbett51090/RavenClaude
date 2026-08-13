#!/usr/bin/env python3
"""
manifest_dividend.py — Phase-1 manifest-dividend measurement (plan §5-P1, binding — RT2-F7).

The plan's core value hypothesis (§2, "Addressing layer"): the Binding Manifest — NOT per-run
inference — is the product. A recurring template's manifest is proposed once, a human amends it,
and every later run of that SAME template just re-points the amended manifest's bindings at a NEW
period's data. If that is true, run 2 of a recurring template should require far less human
attention than run 1. This script simulates exactly that A/B and counts a human-touch PROXY for
each run:

    RUN 1 (cold start on a template never seen before):
        infer.py builds an RSG -> build_manifest.py proposes a manifest against period A's data.
        Every binding the pipeline classed `needs-review`, or whose confidence sits below the
        classification threshold, is a HUMAN TOUCH — it must be resolved before the draft can ship
        (the plugin's guarantee #2, honest-guarantee.md / plan §1). We then simulate that human
        resolving each one (`human_amend_binding`) — assigning it a final class + query — producing
        the CACHED, amended manifest a recurring template would keep on file.

    RUN 2 (a later run of the SAME template, new period B):
        The cached run-1 manifest is REUSED AS-IS — no fresh infer.py call, no fresh
        build_manifest.py classification walk. We only (a) re-point each binding's query at period
        B's data and (b) re-run the two MECHANICAL, per-period safety checks the plan requires even
        on a reused manifest: the earned-frozen new-domain-collision re-check (plan §2 — a `frozen`
        binding is only safe if it also carries "no member of the NEW dataset's value domains", and
        that is a per-period fact, not a template fact) and a dataset-coverage check for every
        already-discovered bind key. Anything either check re-flags is a run-2 human touch.

Emits a JSON report: run1_human_touches, run2_human_touches, dividend_ratio, and a break-even
statement (default bound: run-2 human touches < 20% of run-1's, per the plan's own illustrative
bound in §5-P1 — tune with --break-even-ratio).

━━ HONESTY LABEL (read this before citing a number from this script anywhere) ━━━━━━━━━━━━━━━━━━━
This is a PROXY MEASUREMENT ON ONE SYNTHETIC FIXTURE (tests/fixtures/report-regeneration/
sample-report.html — a fabricated company, fabricated figures, no real client data). It counts
MECHANICAL human-touch bindings (needs-review / sub-threshold-confidence), not wall-clock human
review minutes, and involves no real human reviewer. It is NOT a validated human-time study, and it
is NOT the plan's real calibration signal — that is the client's actual downstream peer-review
feedback, instrumented per plan §5 Phase-0 gate G0-d. This script exists only to settle, cheaply and
honestly, whether the manifest-reuse premise is even directionally plausible before Phase 2 commits
to productionizing the harness around it. Every JSON report this script emits repeats this label
verbatim in its `honesty_label` field — never cite a bare number from it without that context.

Usage:
    python3 manifest_dividend.py
    python3 manifest_dividend.py --format text
    python3 manifest_dividend.py --out /tmp/dividend.json --pretty
    python3 manifest_dividend.py --break-even-ratio 0.25 --strict

Exit codes:
    0 — measurement completed (this is a measurement tool, not a gate — see doctor.py's identical
        "probe, not a gate" convention; the `dividend.holds` field carries the real pass/fail signal)
    1 — measurement completed but the break-even bound did NOT hold, AND --strict was passed (opt-in;
        "surface it at the bet gate" per plan §5-P1)
    2 — usage / path-guard / pipeline error (message on stderr; a best-effort JSON error object on
        stdout so a caller parsing stdout never gets truncated/ambiguous JSON)

Design constraints (binding, mirrors this plugin's other scripts/*.py):
    - Stdlib only: argparse, copy, importlib, json, sys, tempfile, pathlib, typing. No third-party
      imports, no pip installs, no network, no subprocess. Runs on Python 3.9.6.
    - `from __future__ import annotations`; no PEP-604 `X | Y`, no `match` statement.
    - Path-guarded: the optional --out rejects any '..' traversal component (mirrors
      build_manifest.py's `_guard_path` — absolute paths are allowed, since this is a user-facing
      CLI, not a repo-internal fixture tool; traversal is never accepted).
    - Does NOT edit any existing file. The only files this script writes are (a) private tempdir
      intermediates for the infer/build_manifest pipeline calls, and (b) the optional --out report.
    - The pipeline modules are loaded by path (mirrors scripts/e2e_acceptance.py's `_load`) so this
      script never needs a package `__init__.py` or an installed distribution.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA = "report-regeneration/manifest-dividend@1"
DEFAULT_BREAK_EVEN_RATIO = 0.20  # plan §5-P1's own illustrative bound: "run-2 human time < 20%"
DEFAULT_CONFIDENCE_THRESHOLD = 0.7  # matches build_manifest.py's CLI default

_SCRIPTS_DIR = Path(__file__).resolve().parent
_PLUGIN_DIR = _SCRIPTS_DIR.parent
_REPO_ROOT = _PLUGIN_DIR.parent.parent
_FIXTURES = _REPO_ROOT / "tests" / "fixtures" / "report-regeneration"
_SAMPLE = _FIXTURES / "sample-report.html"
_NEWDATA_A = _FIXTURES / "new-data.sample.json"

# A binding whose class a human resolved to `surgical` but for which no discoverable data-bind key
# exists in the template (the node has a data-shaped literal but no `data-bind` attribute to point
# at) — the human authors a bespoke query. NOT a generic dotted-path lookup, so run 2's dataset-
# coverage re-check deliberately does not treat it as a coverage gap (see reuse_manifest_for_new_period).
_HUMAN_AUTHORED_PLACEHOLDER = "<human-authored binding - no automatic bind key>"

# ── period B — a SECOND, hand-authored synthetic reporting period for run 2 ────────────────────
# Advances new-data.sample.json's Q2 2025 figures by one more quarter with plausible, hand-picked
# growth. Deliberately kept IN THIS FILE (never a new corpus fixture file — the task constraint is
# NEW file only, and this script is that one new file). Every figure is fabricated, same as the
# corpus it advances.
_PERIOD_B = {
    "source_ref": "acme-q3-2025-refresh",
    "source_period": "2025-Q3",
    "bindings": {
        "meta.period_label": "Q3 2025",
        "meta.report_date": "October 8, 2025",
        "revenue.total": "$5,398,900",
        "revenue.growth_yoy": "+8.1%",
        "margin.operating": "19.6%",
        "revenue.region.north": "$1,376,300",
        "revenue.region.north_share": "25.5%",
        "revenue.region.emea": "$1,079,800",
        "revenue.region.emea_share": "20.0%",
        "revenue.region.apac": "$1,755,900",
        "revenue.region.apac_share": "32.5%",
        "revenue.region.latam": "$1,186,900",
        "revenue.region.latam_share": "22.0%",
        "revenue.trend.latest_quarter": "$5,398,900",
    },
}


class ManifestDividendError(Exception):
    """Raised for any path-guard / pipeline / usage failure (exit 2)."""


# ── path safety (mirrors build_manifest.py's _guard_path — a user-facing CLI, absolute paths
# allowed, traversal never accepted) ────────────────────────────────────────────────────────────

def _guard_path(raw: str, *, must_exist: bool) -> Path:
    if not raw:
        raise ManifestDividendError("empty path")
    p = Path(raw)
    if ".." in p.parts:
        raise ManifestDividendError(f"path traversal ('..') is not allowed: {raw!r}")
    resolved = p if p.is_absolute() else (Path.cwd() / p)
    resolved = resolved.resolve()
    if must_exist and not resolved.is_file():
        raise ManifestDividendError(f"file not found: {raw!r} (resolved {resolved})")
    return resolved


# ── load the pipeline stages by path (mirrors scripts/e2e_acceptance.py's `_load`) ─────────────

def _load_module(name: str, rel: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, str(_PLUGIN_DIR / rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _load_pipeline() -> tuple[Any, Any, Any]:
    infer = _load_module("rr_infer_mdiv", "skills/infer-report-structure/infer.py")
    build_manifest = _load_module("rr_build_manifest_mdiv", "skills/rebind-manifest/build_manifest.py")
    rr_anchor = _load_module("rr_anchor_mdiv", "scripts/rr_anchor.py")
    return infer, build_manifest, rr_anchor


# ── RSG helpers ──────────────────────────────────────────────────────────────────────────────

def _index_rsg_nodes(root: dict) -> dict[str, dict]:
    """node_id -> RSG node, flattened over the whole tree (pre-order)."""
    out: dict[str, dict] = {}

    def walk(n: dict) -> None:
        out[n["id"]] = n
        for c in n.get("children", []):
            walk(c)

    walk(root)
    return out


def _is_human_touch(binding: dict, threshold: float) -> bool:
    """A binding a human must resolve before the draft can ship: needs-review OR sub-threshold
    confidence (the two conditions the plan's guarantee #2 makes mechanical — plan §1)."""
    return binding["class"] == "needs-review" or binding["confidence"] < threshold


# ── RUN 1 — cold start: fresh infer -> fresh manifest proposal against period A ────────────────

def run_stage1(
    build_manifest: Any, infer: Any, template_text: str, template_path: Path,
    new_data_a: dict, tmp: Path, threshold: float,
) -> tuple[dict, dict, list[dict]]:
    rsg, _stats = infer.build_rsg(template_text, template_id="acme-widgets-q1-2025")
    rsg_path = tmp / "rsg-run1.json"
    rsg_path.write_text(json.dumps(rsg), encoding="utf-8")

    nd_path = tmp / "newdata-a.json"
    nd_path.write_text(
        json.dumps({
            "source_ref": new_data_a["source_ref"],
            "source_period": new_data_a["source_period"],
            "values": new_data_a["bindings"],
        }),
        encoding="utf-8",
    )

    manifest_path = tmp / "manifest-run1.json"
    taint_path = tmp / "taint-run1.json"
    result = build_manifest.run(
        str(rsg_path), str(template_path), str(nd_path), str(manifest_path), str(taint_path),
        manifest_version="1.0.0", threshold=threshold,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return rsg, manifest, result["decisions"]


# ── the "human amends the proposed manifest" step (core-architecture-spec.md §3) ───────────────

def human_amend_binding(
    binding: dict, rsg_index: dict[str, dict], template_text: str, rr_anchor: Any,
    template_id: str, source_ref: str, source_period: str,
) -> dict:
    """Simulate a human resolving ONE needs-review binding. Uses only generically-available
    signals (a real `data-bind` attribute on the anchored element; the RSG's own inferred `role`;
    the RSG's own `data_shaped_literal` flag) — never fixture-specific string matching — so the
    heuristic generalizes past this one corpus. Returns the amended binding (never needs-review)."""
    node = rsg_index.get(binding["node_id"], {})
    role = node.get("role", "unknown")
    bind_key = ""
    if rr_anchor.exists(template_text, binding["anchor"]):
        try:
            bind_key = rr_anchor.resolve(template_text, binding["anchor"]).attrs.get("data-bind", "")
        except rr_anchor.AnchorError:
            bind_key = ""

    if bind_key:
        # a genuine, already-annotated data binding the classifier merely under-trusted.
        final_class = "surgical"
        query: Any = {"kind": "file-cell", "expression": bind_key, "source_ref": source_ref}
    elif role in ("chart", "image"):
        final_class = "regenerate"
        query = {
            "kind": "screenshot-capture",
            "expression": "human-confirmed regenerate slot (fresh capture, never transplanted)",
            "source_ref": source_ref,
        }
    elif role == "narrative":
        final_class = "regenerate"
        query = {
            "kind": "literal-from-new-source",
            "expression": "human-confirmed regenerate slot",
            "source_ref": source_ref,
        }
    elif node.get("data_shaped_literal"):
        # a value-shaped token with no discoverable bind key — the expensive residual case: the
        # human hand-authors a new binding (V6's coverage gap, made concrete).
        final_class = "surgical"
        query = {"kind": "file-cell", "expression": _HUMAN_AUTHORED_PLACEHOLDER, "source_ref": source_ref}
    else:
        # no data-bind signal, no generative role, no data-shaped literal -> genuinely static
        # chrome; the human confirms frozen.
        final_class = "frozen"
        query = None

    amended = copy.deepcopy(binding)
    amended["class"] = final_class
    amended["confidence"] = 1.0  # human sign-off
    if final_class == "frozen":
        amended["provenance"] = {"source": template_id, "source_period": None}
        amended["data_query"] = None
    else:
        amended["provenance"] = {"source": source_ref, "source_period": source_period}
        amended["data_query"] = query
    return amended


def amend_manifest(
    manifest: dict, rsg_index: dict[str, dict], template_text: str, rr_anchor: Any,
    source_ref: str, source_period: str,
) -> tuple[dict, list[dict]]:
    """Resolve every needs-review binding in `manifest`. Returns the amended (cached) manifest plus
    a log of what the simulated human decided — this cached manifest is what run 2 reuses."""
    amended = copy.deepcopy(manifest)
    log: list[dict] = []
    for i, b in enumerate(amended["bindings"]):
        if b["class"] == "needs-review":
            new_b = human_amend_binding(
                b, rsg_index, template_text, rr_anchor, manifest["template_id"], source_ref, source_period
            )
            log.append({
                "node_id": b["node_id"],
                "resolved_class": new_b["class"],
                "resolution": "one-time human amendment in run 1; cached into the manifest thereafter",
            })
            amended["bindings"][i] = new_b
    return amended, log


# ── RUN 2 — REUSE the cached manifest; only re-point at period B + re-run the two mechanical
# per-period safety checks (NO fresh infer, NO fresh classification walk) ──────────────────────

def reuse_manifest_for_new_period(
    amended_manifest: dict, template_text: str, build_manifest: Any, rr_anchor: Any,
    new_data_b: dict, threshold: float,
) -> tuple[dict, list[dict]]:
    """The manifest-reuse step (plan §2: "a cached prior manifest for a recurring template"). The
    binding CLASS decisions from run 1 carry over untouched. Only two MECHANICAL, per-period checks
    re-run (neither is a re-inference / re-classification pass):

      1. earned-frozen new-domain collision (plan §2 hard rule: frozen requires no data-shaped
         literal AND no member of the NEW dataset's value domains — the domain is period-specific,
         so this genuinely must be re-checked every period even though the template never changes).
      2. dataset coverage for every already-discovered `file-cell` bind key (does period B's data
         actually carry a value for a key run 1 already resolved?).

    Anything either check flags is a run-2 human touch. Returns (reused_manifest, touches[])."""
    reused = copy.deepcopy(amended_manifest)
    domain_norm_b = [
        build_manifest._norm(v) for v in new_data_b["bindings"].values() if len(build_manifest._norm(v)) >= 2
    ]
    bindings_b = new_data_b["bindings"]
    touches: list[dict] = []

    for b in reused["bindings"]:
        if b["class"] == "needs-review":
            touches.append({
                "node_id": b["node_id"],
                "reason": "residual needs-review carried over from the cached manifest",
            })
            continue

        if b["class"] == "frozen":
            try:
                text = rr_anchor.read_inner(template_text, b["anchor"])
            except rr_anchor.AnchorError:
                text = ""
            hit = build_manifest._contains_domain_value(build_manifest._norm(text), domain_norm_b)
            if hit:
                b["class"] = "needs-review"
                b["data_query"] = {
                    "kind": "none",
                    "expression": "pending human sign-off; no binding proposed until reviewed",
                }
                touches.append({
                    "node_id": b["node_id"],
                    "reason": f"new-period value {hit!r} newly collides with this frozen node's text "
                              "(earned-frozen re-check, NOT re-inference)",
                })
            continue

        # surgical / regenerate: only a discovered `file-cell` bind key is checked against period
        # B's dataset (dax/screenshot-capture/literal-from-new-source/the human-authored placeholder
        # resolve through their own live mechanism at run time — out of scope for this classification
        # + coverage dividend proxy).
        query = b.get("data_query") or {}
        if query.get("kind") == "file-cell" and query.get("expression") != _HUMAN_AUTHORED_PLACEHOLDER:
            expr = query.get("expression", "")
            if expr not in bindings_b:
                touches.append({
                    "node_id": b["node_id"],
                    "reason": f"period B's dataset has no value for known key {expr!r} "
                              "(data-pipeline coverage gap, not a classification gap)",
                })

    return reused, touches


# ── the measurement itself ──────────────────────────────────────────────────────────────────────

def measure(threshold: float, break_even_ratio: float) -> dict:
    infer, build_manifest, rr_anchor = _load_pipeline()

    if not _SAMPLE.is_file():
        raise ManifestDividendError(f"corpus template not found: {_SAMPLE}")
    if not _NEWDATA_A.is_file():
        raise ManifestDividendError(f"corpus new-data fixture not found: {_NEWDATA_A}")

    template_text = _SAMPLE.read_text(encoding="utf-8")
    raw_a = json.loads(_NEWDATA_A.read_text(encoding="utf-8"))
    new_data_a = {
        "source_ref": "acme-q2-2025-refresh",
        "source_period": raw_a["source_period"],
        "bindings": raw_a["bindings"],
    }

    with tempfile.TemporaryDirectory(prefix="rr-manifest-dividend-") as tmp_s:
        tmp = Path(tmp_s)

        rsg, manifest_run1, _decisions = run_stage1(
            build_manifest, infer, template_text, _SAMPLE, new_data_a, tmp, threshold
        )
        rsg_index = _index_rsg_nodes(rsg["root"])

        run1_touches = [
            {"node_id": b["node_id"], "class": b["class"], "confidence": b["confidence"]}
            for b in manifest_run1["bindings"]
            if _is_human_touch(b, threshold)
        ]

        amended_manifest, amendment_log = amend_manifest(
            manifest_run1, rsg_index, template_text, rr_anchor,
            new_data_a["source_ref"], new_data_a["source_period"],
        )
        residual_after_amendment = sum(
            1 for b in amended_manifest["bindings"] if b["class"] == "needs-review"
        )
        if residual_after_amendment:
            raise ManifestDividendError(
                f"human_amend_binding left {residual_after_amendment} binding(s) still "
                "needs-review — the amendment heuristic has a bug"
            )

        reused_manifest, run2_touches = reuse_manifest_for_new_period(
            amended_manifest, template_text, build_manifest, rr_anchor, _PERIOD_B, threshold
        )

    run1_count = len(run1_touches)
    run2_count = len(run2_touches)
    dividend_ratio = (run2_count / run1_count) if run1_count else 0.0
    holds = True if run1_count == 0 else dividend_ratio < break_even_ratio

    if run1_count == 0:
        break_even_statement = (
            "run 1 had zero human-touch bindings on this fixture, so no reuse dividend applies "
            "(nothing to amortize) — the premise is vacuously untested here."
        )
    else:
        break_even_statement = (
            "run-2 human touches ({}) {} {:.0f}% of run-1's ({}) -> {}".format(
                run2_count,
                "<" if holds else ">=",
                break_even_ratio * 100,
                run1_count,
                "HOLDS"
                if holds
                else "DOES NOT HOLD -- the manifest-reuse premise did not settle cheaply on this "
                "proxy; surface at the Phase-1 bet gate (plan §5-P1)",
            )
        )

    return {
        "schema": SCHEMA,
        "honesty_label": (
            "SYNTHETIC PROXY on ONE fixture "
            "(tests/fixtures/report-regeneration/sample-report.html) -- NOT a validated human-time "
            "study. Counts a MECHANICAL human-touch proxy (needs-review + sub-threshold-confidence "
            "bindings a human must resolve), not wall-clock review minutes, and involves no real "
            "human reviewer. It is a stand-in for the plan's real calibration signal (plan §5 "
            "Phase-0 gate G0-d: instrumenting the client's ACTUAL peer-review feedback), used only "
            "to settle whether the manifest-reuse premise is directionally plausible before Phase 2."
        ),
        "corpus": {
            "template": str(_SAMPLE.relative_to(_REPO_ROOT)),
            "confidence_threshold": threshold,
            "period_a": {
                "source_ref": new_data_a["source_ref"],
                "source_period": new_data_a["source_period"],
                "note": "tests/fixtures/report-regeneration/new-data.sample.json (existing fixture)",
            },
            "period_b": {
                "source_ref": _PERIOD_B["source_ref"],
                "source_period": _PERIOD_B["source_period"],
                "note": "hand-authored synthetic third period, embedded in THIS script only "
                "(no new corpus fixture file added)",
            },
        },
        "run1": {
            "description": "cold start on this template: fresh infer.py -> fresh build_manifest.py "
            "proposal against period A. Every needs-review / sub-threshold-confidence binding is a "
            "human touch that must be resolved before the draft can ship.",
            "total_bindings": len(manifest_run1["bindings"]),
            "human_touches": run1_count,
            "touch_detail": run1_touches,
            "amendment_log": amendment_log,
        },
        "run2": {
            "description": "recurring run on the SAME template, period B: REUSE the run-1 "
            "human-amended manifest as-is (no fresh infer.py call, no fresh build_manifest.py "
            "classification walk); only re-point bindings at period B and re-run the two "
            "mechanical per-period safety checks (earned-frozen new-domain collision; dataset "
            "coverage for known bind keys).",
            "total_bindings": len(reused_manifest["bindings"]),
            "human_touches": run2_count,
            "touch_detail": run2_touches,
            "residual_needs_review_after_run1_amendment": residual_after_amendment,
        },
        "dividend": {
            "run1_human_touches": run1_count,
            "run2_human_touches": run2_count,
            "dividend_ratio": round(dividend_ratio, 4),
            "break_even_threshold": break_even_ratio,
            "break_even_statement": break_even_statement,
            "holds": holds,
        },
    }


# ── CLI ──────────────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="manifest_dividend.py",
        description="Phase-1 manifest-dividend measurement: human-touch proxy on run 1 (cold "
        "start) vs run 2 (cached-manifest reuse) of the same report template — SYNTHETIC PROXY, "
        "not a validated human-time study.",
    )
    p.add_argument("--out", metavar="PATH", default=None, help="write the JSON report here (optional)")
    p.add_argument("--format", dest="fmt", choices=["json", "text"], default="json",
                    help="stdout format (default json)")
    p.add_argument("--pretty", action="store_true", help="pretty-print the JSON report")
    p.add_argument("--confidence-threshold", dest="threshold", type=float,
                    default=DEFAULT_CONFIDENCE_THRESHOLD,
                    help="sub-threshold confidence counts as a human touch (default %(default)s)")
    p.add_argument("--break-even-ratio", dest="break_even_ratio", type=float,
                    default=DEFAULT_BREAK_EVEN_RATIO,
                    help="run-2 touches must be below this fraction of run-1's to HOLD "
                    "(default %(default)s, per plan §5-P1's own illustrative bound)")
    p.add_argument("--strict", action="store_true",
                    help="exit 1 if the break-even bound does NOT hold (default: always exit 0, a "
                    "measurement tool, not a gate)")
    return p


def _emit_error(message: str) -> None:
    print(json.dumps({"schema": SCHEMA, "ok": False, "error": message}))
    print(f"[error] {message}", file=sys.stderr)


def main(argv: Any = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        out_path = _guard_path(args.out, must_exist=False) if args.out else None
    except ManifestDividendError as exc:
        _emit_error(str(exc))
        return 2

    try:
        report = measure(args.threshold, args.break_even_ratio)
    except ManifestDividendError as exc:
        _emit_error(str(exc))
        return 2
    except (OSError, ValueError, KeyError) as exc:
        _emit_error(f"{type(exc).__name__}: {exc}")
        return 2

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.fmt == "text":
        d = report["dividend"]
        print("manifest-dividend measurement -- SYNTHETIC PROXY (see report['honesty_label'])")
        print(f"  run-1 human touches: {d['run1_human_touches']} / {report['run1']['total_bindings']} bindings")
        print(f"  run-2 human touches: {d['run2_human_touches']} / {report['run2']['total_bindings']} bindings")
        print(f"  dividend_ratio: {d['dividend_ratio']}")
        print(f"  {d['break_even_statement']}")
        if out_path is not None:
            print(f"  report written: {out_path}")
    else:
        print(json.dumps(report, indent=2 if args.pretty else None))

    if args.strict and not report["dividend"]["holds"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
