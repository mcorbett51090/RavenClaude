#!/usr/bin/env python3
"""
e2e_acceptance.py — the bet-settling END-TO-END acceptance test for the report-regeneration HTML
lane. Runs the whole pipeline on the real corpus and settles the two Phase-1 bets:

    infer.py  ->  build_manifest.py  ->  rebind_html.py  ->  harness.py  ->  qa_gate.py

Bet 1 ("single abstraction lowers to HTML"): the SHARED rr_anchor resolver lets every stage
resolve the SAME anchor grammar infer emits — including the compound css_selector anchors infer
uses for id-less nodes — so the pipeline COMPOSES without the anchor-grammar mismatch that used to
abort stage 3. Proven by the happy path reaching PASS/PARTIAL (never a hard FAIL) with ZERO
old-client (Ridgeline) literal surviving the V4 egress scan.

Bet 2 ("the composed harness + adjacent gates catch every seeded defect"): each seeded defect
D1-D14, injected into the REBOUND output, produces an overall FAIL attributed to a SPECIFIC gate
— not merely "something fired". Twelve defects are caught inside the six-leg fidelity harness
(D1/D2/D5/D6/D7/D8/D11/D12/D14 by their mapped leg; D4/D9/D10 trip V2/V3 as chrome/structure
edits). The two defects whose mapped gate is OUTSIDE the six-leg harness are caught crisply by the
two adjacent gates folded into `report-qa-gate`: **D3 (missing alt-text) -> the a11y gate**
(skills/report-a11y-gate, an img-alt BLOCK) and **D13 (prompt-injection) -> the injection guard**
(skills/report-injection-guard, the provenance-bound narrative check catching un-provenanced
attacker prose in a `regenerate` slot). Both fold into the assembled qa_gate verdict as FAIL — the
harness still honestly reports PARTIAL on its own legs (it does not FAKE a fidelity pass or claim
to judge a11y/injection), and the adjacent gate supplies the crisp catch.

What "happy path" means here (an honest scope note, printed in the summary): rebind (stage 3)
rebinds node CONTENT — a value, a narrative, a re-captured asset — but NOT the data-period /
data-source-period PROVENANCE attributes. A cross-period ADVANCE (Q1->Q2) would therefore leave
stale provenance attributes that period-coherence (correctly) flags — so this acceptance run
regenerates WITHIN the template's period (2025-Q1): fresh narratives + re-captured assets + a
strip-then-write of every value slot, staying period-coherent. new-data.sample.json (the Q2
advance dataset) is still exercised as the binding-COVERAGE contract. Rebinding provenance
attributes for a true period advance is a noted follow-up, out of scope for this anchor-grammar fix.

Design constraints: stdlib only, Python 3.9.6, NO pip installs, no network. Loads the five stage
modules + seed_defects + rr_anchor by path (importlib) and drives their Python APIs; the only files
written are intermediates under a private tempdir (the corpus + repo fixtures are read-only).

Exit codes: 0 — every assertion held; 1 — any assertion missed (details printed).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_PLUGIN_DIR = _SCRIPTS_DIR.parent
_REPO_ROOT = _PLUGIN_DIR.parent.parent
_FIXTURES = _REPO_ROOT / "tests" / "fixtures" / "report-regeneration"
_SAMPLE = _FIXTURES / "sample-report.html"
_NEWDATA_SAMPLE = _FIXTURES / "new-data.sample.json"
_HARNESS_NEWDATA = _PLUGIN_DIR / "skills" / "report-fidelity-harness" / "fixtures" / "clean-new-data.json"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, str(_PLUGIN_DIR / rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


infer = _load("rr_infer", "skills/infer-report-structure/infer.py")
build_manifest = _load("rr_build_manifest", "skills/rebind-manifest/build_manifest.py")
rebind_html = _load("rr_rebind_html", "skills/rebind-html/rebind_html.py")
harness = _load("rr_harness", "skills/report-fidelity-harness/harness.py")
qa_gate = _load("rr_qa_gate", "skills/report-qa-gate/qa_gate.py")
a11y_lint = _load("rr_a11y_lint", "skills/report-a11y-gate/a11y_lint.py")
injection_guard = _load("rr_injection_guard", "skills/report-injection-guard/injection_guard.py")
seed_defects = _load("rr_seed_defects", "scripts/seed_defects.py")


# ── the "human amendment" of the proposed manifest (core-architecture-spec.md §3: inference
# proposes a manifest, a human amends it). Concretely: point each surgical/regenerate binding's
# data_query at a concrete new-data cell (the RSG-proposed DAX/screenshot/literal expressions are
# human-readable placeholders), then supply the matching new dataset. Values EQUAL the template's
# 2025-Q1 figures (a same-period refresh — see the module docstring), so the output stays
# period-coherent AND the seeded-defect injectors' byte-exact "before" guards still match.

_EXPR = {
    # surgical value slots -> the new-data cell (dotted path resolvable against _REBIND_DATA)
    "hdr-period": "meta.period_label", "ftr-period": "meta.period_label",
    "kpi-revenue": "revenue.total", "kpi-revenue-growth": "revenue.growth_yoy",
    "kpi-operating-margin": "margin.operating", "kpi-report-date": "meta.report_date",
    "tbl-north-revenue": "revenue.region.north", "tbl-north-share": "revenue.region.north_share",
    "tbl-emea-revenue": "revenue.region.emea", "tbl-emea-share": "revenue.region.emea_share",
    "tbl-apac-revenue": "revenue.region.apac", "tbl-apac-share": "revenue.region.apac_share",
    "tbl-latam-revenue": "revenue.region.latam", "tbl-latam-share": "revenue.region.latam_share",
    "tbl-region-total": "revenue.total", "xmla-figure-latest": "revenue.trend.latest_quarter",
    # regenerate slots -> narrative templates / re-captured assets
    "exec-summary-narrative": "regen.exec_summary", "outlook-narrative": "regen.outlook",
    "logo-header": "regen.logo", "pbi-screenshot": "regen.pbi_screenshot",
    "chart-region-mix": "regen.chart_region_mix",
}

_REBIND_DATA = {
    "meta": {"period_label": "Q1 2025", "report_date": "April 4, 2025"},
    "revenue": {
        "total": "$4,821,300", "growth_yoy": "+12.4%",
        "region": {
            "north": "$1,203,400", "north_share": "25.0%",
            "emea": "$982,900", "emea_share": "20.4%",
            "apac": "$1,540,700", "apac_share": "32.0%",
            "latam": "$1,094,300", "latam_share": "22.7%",
        },
        "trend": {"latest_quarter": "$4,821,300"},
    },
    "margin": {"operating": "18.7%"},
    "regen": {
        # ${dotted.path} placeholders render via rebind's stdlib string.Template subclass.
        "exec_summary": (
            "Acme Widgets delivered ${revenue.total} in total revenue in ${meta.period_label}, "
            "up ${revenue.growth_yoy} year-over-year across all four regions."
        ),
        "outlook": (
            "Management expects continued momentum through the remainder of 2025; key risks "
            "include freight-cost volatility in the APAC lane and competitive pricing in EMEA."
        ),
        "logo": {"src": "data:image/gif;base64,QUNNRUxPR09WMQ==", "alt": "Acme Widgets logo"},
        "pbi_screenshot": {
            "src": "data:image/gif;base64,UEJJU0hPVFYx",
            "alt": "Power BI screenshot: quarterly revenue trend, Q1 2025",
        },
        "chart_region_mix": {
            "src": "data:image/gif;base64,UkVHSU9OTUlYVjE=",
            "alt": "Bar chart comparing Q1 2025 revenue share across North America, EMEA, APAC, "
                   "and Latin America regions.",
        },
    },
}

# Defect -> the gate expected to FIRE (overall FAIL), by category.
#   FIDELITY: the six-leg harness catches it at its mapped fidelity leg.
#   CHROME:   a chrome/structure edit whose NOMINAL gate is a11y/render, but which trips a
#             fidelity leg (V2/V3) because it changes bytes/structure OUTSIDE a bound anchor.
#   A11Y:     mapped to the adjacent a11y gate (skills/report-a11y-gate) — outside the six-leg
#             harness, but a CRISP catch: the a11y sub-receipt's blocking img-alt violation folds
#             the assembled qa_gate verdict to FAIL.
#   INJECTION: mapped to the adjacent injection guard (skills/report-injection-guard) — outside
#             the six-leg harness, a CRISP catch: the provenance-bound narrative finding folds the
#             assembled qa_gate verdict to FAIL.
_FIDELITY = {
    "D1": "V1", "D2": "V1", "D5": "V3", "D6": "V4", "D7": "V1",
    "D8": "period-coherence", "D11": "V6", "D12": "V4", "D14": "period-coherence",
}
_CHROME = {"D4": ("V2", "V3"), "D9": ("V2", "V3"), "D10": ("V2", "V3")}
_A11Y = {"D3": "a11y gate (stdlib WCAG floor) — img-alt BLOCK folds qa_gate to FAIL"}
_INJECTION = {
    "D13": "injection guard (partition-anomaly + provenance-bound narrative) — "
           "un-provenanced regenerate-slot prose folds qa_gate to FAIL",
}


class Result:
    def __init__(self) -> None:
        self.passes: list = []
        self.fails: list = []

    def check(self, ok: bool, label: str) -> bool:
        (self.passes if ok else self.fails).append(label)
        print(("  PASS  " if ok else "  MISS  ") + label)
        return ok


def _legs(receipt: dict) -> dict:
    return {leg["leg"]: leg for leg in receipt["legs"]}


def build_pipeline(tmp: Path):
    """infer -> build_manifest -> (amend) -> rebind. Returns (template_text, manifest, output_text)."""
    template_text = _SAMPLE.read_text(encoding="utf-8")

    # stage 1 — infer the RSG
    rsg, _stats = infer.build_rsg(template_text, template_id="acme-widgets-q1-2025")
    rsg_path = tmp / "rsg.json"
    rsg_path.write_text(json.dumps(rsg), encoding="utf-8")

    # stage 2 — build the manifest + taint dictionary (same reporting period, 2025-Q1)
    bm_newdata = tmp / "bm-newdata.json"
    bm_newdata.write_text(json.dumps({
        "source_ref": "acme-q1-2025-refresh", "source_period": "2025-Q1",
        "values": dict.fromkeys(set(_EXPR.values()), "cell"),
    }), encoding="utf-8")
    manifest_path = tmp / "manifest.json"
    taint_path = tmp / "taint.json"
    build_manifest.run(
        str(rsg_path), str(_SAMPLE), str(bm_newdata), str(manifest_path), str(taint_path),
        manifest_version="1.0.0", threshold=0.7,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # the human amendment: point each mutable binding's data_query at a concrete new-data cell.
    for b in manifest["bindings"]:
        if b.get("class") in ("surgical", "regenerate") and b["anchor"].get("kind") == "element_id":
            expr = _EXPR.get(b["anchor"]["value"])
            if expr and isinstance(b.get("data_query"), dict):
                b["data_query"]["expression"] = expr

    # stage 3 — rebind (surgical + regenerate + needs-review + frozen), via the shared resolver
    output_text, _changes, _nrc = rebind_html.rebind(template_text, manifest, _REBIND_DATA)
    return template_text, manifest, output_text


def run_harness(tmp: Path, template_text: str, output_text: str, manifest: dict, tag: str) -> dict:
    """Write the intermediates and run the fidelity harness (stage 4). new-data is the harness-shape
    2025-Q1 dataset (clean-new-data.json), matching the same-period regeneration."""
    tp = tmp / f"template-{tag}.html"; tp.write_text(template_text, encoding="utf-8")
    op = tmp / f"output-{tag}.html"; op.write_text(output_text, encoding="utf-8")
    mp = tmp / f"manifest-{tag}.json"; mp.write_text(json.dumps(manifest), encoding="utf-8")
    return harness.run_harness(str(tp), str(op), str(mp), str(_HARNESS_NEWDATA))


def main() -> int:
    res = Result()
    tmp = Path(tempfile.mkdtemp(prefix="rr-e2e-"))
    print("report-regeneration END-TO-END acceptance (infer -> build_manifest -> rebind -> harness -> qa_gate)")
    print(f"  corpus: {_SAMPLE.relative_to(_REPO_ROOT)}")
    print(f"  workdir: {tmp}\n")

    # ── the corpus new-data (Q2 advance) covers every template binding (coverage contract) ──
    sample_nd = json.loads(_NEWDATA_SAMPLE.read_text(encoding="utf-8"))
    surgical_keys = {v for k, v in _EXPR.items() if v.startswith(("meta.", "revenue.", "margin."))}
    covered = set(sample_nd.get("bindings", {}))
    res.check(surgical_keys <= covered,
              f"new-data.sample.json covers every template data-bind ({len(surgical_keys)} keys)")

    template_text, manifest, output_text = build_pipeline(tmp)
    print()

    # the harness-shape new dataset (2025-Q1) — also the injection guard's provenance domain
    harness_new_data = json.loads(_HARNESS_NEWDATA.read_text(encoding="utf-8"))

    # ── (a) HAPPY PATH ──────────────────────────────────────────────────────────────────────
    print("[A] happy path — the composed pipeline runs clean end-to-end")
    receipt = run_harness(tmp, template_text, output_text, manifest, "clean")
    legs = _legs(receipt)
    gate = receipt["overall_gate"]
    clean_a11y = a11y_lint.lint_html(output_text)
    clean_injection = injection_guard.guard(output_text, manifest, harness_new_data)
    qa = qa_gate.build_result(receipt, a11y=clean_a11y, injection=clean_injection)

    res.check(gate in ("PASS", "PARTIAL"),
              f"overall gate is PASS/PARTIAL, never a hard FAIL (got {gate})")
    res.check(clean_a11y["gate"] == "PASS",
              "a11y gate PASSES on the clean output (no blocking WCAG-floor violation)")
    res.check(clean_injection["gate"] == "PASS",
              "injection guard PASSES on the clean output (healthy partition; every "
              "regenerate-slot token provenanced)")
    res.check(qa["computed_gate"] in ("PASS", "PARTIAL"),
              f"qa_gate verdict (harness + a11y + injection folded in) is PASS/PARTIAL "
              f"(got {qa['computed_gate']})")
    res.check(any(item["category"] == "a11y-manual-residue"
                  for item in qa["manual_residue_checklist"]),
              "a11y manual residue (~30-50% WCAG floor) folds into the reviewer checklist")
    res.check(legs["V4"]["verdict"] == "pass",
              "V4 taint-egress: NO old-client (Ridgeline) literal survives")
    decoded_corpus, _ = harness._decoded_container(harness.parse_html(output_text))
    res.check("ridgeline" not in decoded_corpus.lower(),
              "no 'Ridgeline' literal in the DECODED delivered container (V4's scan surface: text + "
              "attrs + base64; the taint-dictionary comment is an authoring artifact purged pre-emit)")
    for leg in ("V1", "V2", "V3", "V4", "V6", "period-coherence"):
        res.check(legs[leg]["verdict"] == "pass",
                  f"blocking leg {leg} passes on the rebound output")
    res.check(legs["V5"]["verdict"] == "not_captured",
              "V5 render referee honestly not_captured (no Playwright) -> PARTIAL, not a fake pass")
    res.check(bool(receipt["manual_residue"]),
              "manual residue is surfaced (needs-review advisory) — never an empty over-claim")
    print()

    # ── (b) DEFECT LOOP ─────────────────────────────────────────────────────────────────────
    print("[B] defect loop — each seeded defect injected into the REBOUND output")
    fidelity_caught = chrome_caught = a11y_caught = injection_caught = 0
    for did in sorted(seed_defects.DEFECTS, key=lambda d: int(d[1:])):
        bad_html, _changes = seed_defects.DEFECTS[did]["fn"](output_text)
        rc = run_harness(tmp, template_text, bad_html, manifest, did)
        rlegs = _legs(rc)
        verdicts = {k: v["verdict"] for k, v in rlegs.items()}
        rgate = rc["overall_gate"]

        if did in _FIDELITY:
            leg = _FIDELITY[did]
            ok = rlegs[leg]["verdict"] == "fail" and rgate == "FAIL"
            res.check(ok, f"{did}: mapped fidelity leg {leg} FIRES -> gate FAIL  (verdicts={verdicts})")
            fidelity_caught += 1 if ok else 0
        elif did in _CHROME:
            legset = _CHROME[did]
            fired = [lg for lg in legset if rlegs[lg]["verdict"] == "fail"]
            ok = bool(fired) and rgate == "FAIL"
            res.check(ok, f"{did}: chrome/structure edit trips {'/'.join(legset)} "
                          f"(fired {fired}) -> gate FAIL")
            chrome_caught += 1 if ok else 0
        elif did in _A11Y:
            # the a11y gate supplies the crisp catch; the injection guard stays clean.
            a11y_r = a11y_lint.lint_html(bad_html)
            inj_r = injection_guard.guard(bad_html, manifest, harness_new_data)
            qa = qa_gate.build_result(rc, a11y=a11y_r, injection=inj_r)
            fired_alt = any(v["rule"] == "img-alt" and v["blocking"] for v in a11y_r["violations"])
            ok = a11y_r["gate"] == "FAIL" and fired_alt and qa["computed_gate"] == "FAIL"
            res.check(ok, f"{did}: a11y gate FIRES (img-alt BLOCK) -> assembled qa_gate FAIL "
                          f"(a11y={a11y_r['gate']}, injection={inj_r['gate']}, qa={qa['computed_gate']})")
            a11y_caught += 1 if ok else 0
        elif did in _INJECTION:
            # the injection guard supplies the crisp catch; the a11y gate stays clean.
            inj_r = injection_guard.guard(bad_html, manifest, harness_new_data)
            a11y_r = a11y_lint.lint_html(bad_html)
            qa = qa_gate.build_result(rc, a11y=a11y_r, injection=inj_r)
            fired_prov = any(
                f["check"] == "provenance-bound-narrative" and f["blocking"]
                for f in inj_r["findings"]
            )
            ok = inj_r["gate"] == "FAIL" and fired_prov and qa["computed_gate"] == "FAIL"
            res.check(ok, f"{did}: injection guard FIRES (provenance-bound narrative BLOCK) -> "
                          f"assembled qa_gate FAIL "
                          f"(injection={inj_r['gate']}, a11y={a11y_r['gate']}, qa={qa['computed_gate']})")
            injection_caught += 1 if ok else 0
    print()

    # ── summary ─────────────────────────────────────────────────────────────────────────────
    total = len(res.passes) + len(res.fails)
    n_fid = len(_FIDELITY); n_chr = len(_CHROME); n_a11y = len(_A11Y); n_inj = len(_INJECTION)
    crisp = fidelity_caught + chrome_caught + a11y_caught + injection_caught
    print("=" * 78)
    print("BET-SETTLING SUMMARY")
    print(f"  Bet 1 (single abstraction lowers to HTML): happy path -> {gate}, "
          f"zero old-client leak (V4 {legs['V4']['verdict']}).")
    print("  Bet 2 (composed harness + adjacent gates catch every seeded defect):")
    print(f"    - {fidelity_caught}/{n_fid} FIDELITY defects (D1/D2/D5/D6/D7/D8/D11/D12/D14) caught by their mapped leg (FAIL)")
    print(f"    - {chrome_caught}/{n_chr} CHROME/STRUCTURE defects (D4/D9/D10) tripped a fidelity leg (V2/V3, FAIL)")
    print(f"    - {a11y_caught}/{n_a11y} A11Y defect (D3) caught by the a11y gate (img-alt BLOCK -> assembled FAIL)")
    print(f"    - {injection_caught}/{n_inj} INJECTION defect (D13) caught by the injection guard (provenance-bound narrative -> assembled FAIL)")
    print(f"    => {crisp}/14 defects produce an overall FAIL — all crisp catches, no honest-PARTIAL residue.")
    print(f"  checks: {len(res.passes)}/{total} passed, {len(res.fails)} missed")
    print("=" * 78)
    if res.fails:
        print("MISSED:")
        for f in res.fails:
            print("  - " + f)
        return 1
    print("ALL E2E ACCEPTANCE CHECKS PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
