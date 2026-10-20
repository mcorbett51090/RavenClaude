#!/usr/bin/env python3
"""
test_harness.py — TDD acceptance suite for the report-fidelity-harness against the seeded-defect
corpus (tests/fixtures/report-regeneration + scripts/seed_defects.py).

Contract proven here (per core-architecture-spec.md §5 + the corpus README):
  1. CLEAN CONTROL PASSES — a genuine, leak-free REBIND of the template (fixtures/clean-output.html,
     produced by the real rebind_html.rebind() engine against fixtures/clean-manifest.json +
     fixtures/clean-new-data.json — NOT the raw template fed back as its own "output", which still
     carries the template's own TAINT-DICTIONARY documentation comment and would spuriously trip
     V4) passes every BLOCKING leg (V1, V2, V3, V4, V6, period-coherence); V5 is honestly
     not_captured, so the overall gate is PARTIAL (never a fake PASS, never a FAIL).
  2. EACH DEFECT IS CAUGHT BY ITS MAPPED LEG — leg-to-defect attribution, not merely "something
     fired": D1/D2 -> V1, D5 -> V3, D6/D12 -> V4, D7 -> V1 cross-slot, D8/D14 -> period-coherence,
     D11 -> V6.
  3. MUST-FAIL HALVES PROVE THE DISABLE KNOB CAN'T GREEN-LIGHT A DEFECT — for each ML-free leg
     (V2, V4, V6, period-coherence): with the leg enabled the seeded defect is caught (verdict
     "fail", gate FAIL). Neutering the SAME leg via the test-only --disable-leg mutant knob
     (RR_HARNESS_ENABLE_DISABLE_LEG=1, set below) never reports a fake "pass" — the neutered leg
     reports verdict "disabled", and because every one of these legs is BLOCKING, compute_gate
     forces the overall gate to FAIL (never PARTIAL, never PASS). A leg that could be switched off
     to a silent "pass" would be a false-teeth bug; this is the stronger check that it cannot be.
     Per-leg catching teeth (attribution) is proven separately by the positive test_*_catches_*
     tests above.
  4. RECEIPTS ARE SCHEMA-VALID and the ML-free legs are labeled inference_independent.

Stdlib-only. Runnable directly (`python3 test_harness.py`) or under pytest.
"""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from pathlib import Path

# The --disable-leg mutant knob is a TEST-ONLY footgun (harness.py P1 #5): honored only under this
# env flag, so a neutered leg can never silently green-light a production run. This suite's
# must-fail-half tests (section 3 below) are exactly the sanctioned use of that footgun — they
# deliberately disable a leg to prove the knob itself can't be used to fake a "pass".
os.environ.setdefault("RR_HARNESS_ENABLE_DISABLE_LEG", "1")

_SKILL_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _SKILL_DIR.parents[3]
_SAMPLE = _REPO_ROOT / "tests" / "fixtures" / "report-regeneration" / "sample-report.html"
_SEED = _REPO_ROOT / "plugins" / "report-regeneration" / "scripts" / "seed_defects.py"
_MANIFEST = _SKILL_DIR / "fixtures" / "clean-manifest.json"
_NEW_DATA = _SKILL_DIR / "fixtures" / "clean-new-data.json"
# The genuine, leak-free rebind of _SAMPLE (produced by the real rebind_html.rebind() engine
# against _MANIFEST + _NEW_DATA; see fixtures/README or the generation note in this file's
# docstring) — the actual "clean control" output. Feeding _SAMPLE back as its own "output" is NOT
# a legitimate clean control: the raw template still carries its own TAINT-DICTIONARY documentation
# comment (see sample-report.html's header comment), and a real output would have had that comment
# purged pre-emit (rebind_html._strip_old_client_comments, spec §6.6) — feeding it back unpurged
# spuriously trips V4's raw-byte backstop.
_CLEAN_OUTPUT = _SKILL_DIR / "fixtures" / "clean-output.html"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


harness = _load("harness_under_test", _SKILL_DIR / "harness.py")
seed = _load("seed_defects_under_test", _SEED)

_TMP = Path(tempfile.mkdtemp(prefix="fidelity-harness-tests-"))
_TEMPLATE_TEXT = _SAMPLE.read_text(encoding="utf-8")


def _write_defect_output(defect_id: str) -> Path:
    """Inject exactly one seeded defect via the corpus injector; write the bad output to a temp
    file and return its path. The template is opened read-only; only the temp output is written."""
    mutated, _changes = seed.DEFECTS[defect_id]["fn"](_TEMPLATE_TEXT)
    out = _TMP / (f"bad-{defect_id}.html")
    out.write_text(mutated, encoding="utf-8")
    return out


def _run(output_path: Path, disabled=()) -> dict:
    return harness.run_harness(
        str(_SAMPLE), str(output_path), str(_MANIFEST), str(_NEW_DATA), disabled_legs=disabled
    )


def _legs(receipt: dict) -> dict:
    return {leg["leg"]: leg for leg in receipt["legs"]}


def _run_defect(defect_id: str, disabled=()) -> dict:
    return _run(_write_defect_output(defect_id), disabled=disabled)


# ── 1. clean control passes ───────────────────────────────────────────────────

def test_clean_control_passes_every_blocking_leg():
    # _CLEAN_OUTPUT is a genuine rebind() output (see the constant's docstring above) — NOT the
    # raw template fed back as its own "output". Feeding the template to itself would still carry
    # its own TAINT-DICTIONARY comment and spuriously fail V4; a real clean output has had that
    # comment purged pre-emit, exactly as _CLEAN_OUTPUT was generated.
    receipt = _run(_CLEAN_OUTPUT)
    legs = _legs(receipt)
    blocking = [lg for lg in receipt["legs"] if lg["blocking"]]
    assert blocking, "expected blocking legs to exist"
    for lg in blocking:
        assert lg["verdict"] == "pass", (
            "clean control: blocking leg {} did not pass: {}".format(lg["leg"], lg["evidence"])
        )
    # V5 render referee is honestly not_captured in a headless stdlib env → PARTIAL, never PASS,
    # never FAIL. (An empty manual_residue on a shipped report would itself be an over-claim.)
    assert legs["V5"]["verdict"] == "not_captured"
    assert receipt["overall_gate"] == "PARTIAL"
    assert receipt["manual_residue"], "clean control must surface the adversarial advisory residue"


def test_clean_receipt_is_schema_valid():
    receipt = _run(_CLEAN_OUTPUT)
    assert harness.validate_receipt(receipt) == []


def test_ml_free_legs_are_labeled_inference_independent():
    legs = _legs(_run(_CLEAN_OUTPUT))
    for name in ("V2", "V4", "V6", "period-coherence"):
        assert legs[name]["inference_independent"] is True, name
    # V1 (recompute path) and V3 (fine isomorphism) are inference-adjacent as a whole.
    assert legs["V1"]["inference_independent"] is False
    assert legs["V3"]["inference_independent"] is False


# ── 2. each seeded defect caught by its mapped leg ─────────────────────────────

def _assert_leg_fires(defect_id: str, leg_name: str, must_contain=None):
    receipt = _run_defect(defect_id)
    legs = _legs(receipt)
    assert legs[leg_name]["verdict"] == "fail", (
        "{}: expected leg {} to FIRE; receipt={}".format(
            defect_id, leg_name, json.dumps({k: v["verdict"] for k, v in legs.items()})
        )
    )
    if leg_name in ("V1", "V2", "V3", "V4", "V6", "period-coherence"):
        assert receipt["overall_gate"] == "FAIL", (
            f"{defect_id}: a blocking leg fired but overall_gate != FAIL"
        )
    if must_contain:
        assert must_contain in legs[leg_name]["evidence"], (
            "{}: evidence missing {!r}: {}".format(defect_id, must_contain, legs[leg_name]["evidence"])
        )


def test_D1_wrong_value_fires_V1():
    _assert_leg_fires("D1", "V1")


def test_D2_stale_value_fires_V1():
    _assert_leg_fires("D2", "V1")


def test_D5_dropped_section_fires_V3():
    _assert_leg_fires("D5", "V3", must_contain="section")


def test_D6_old_client_literal_fires_V4():
    _assert_leg_fires("D6", "V4", must_contain="Ridgeline")


def test_D7_cross_slot_inconsistency_fires_V1_crossslot():
    # D7 changes the headline KPI but not the table total it summarizes → V1's cross-slot half.
    _assert_leg_fires("D7", "V1", must_contain="cross-slot")


def test_D8_wrong_period_label_fires_period_coherence():
    _assert_leg_fires("D8", "period-coherence")


def test_D11_frozen_misclassified_fires_V6():
    _assert_leg_fires("D11", "V6", must_contain="kpi-report-date")


def test_D12_embedded_cache_leak_fires_V4():
    # The leak lives in <meta> attrs + a hidden <script> cache — invisible to a visible-text scan,
    # present in the decoded container.
    _assert_leg_fires("D12", "V4")


def test_D14_stale_pbi_period_fires_period_coherence():
    _assert_leg_fires("D14", "period-coherence")


# ── 3. must-fail halves — disabling a blocking leg can never green-light a defect ─────

def _assert_leg_has_teeth(defect_id: str, leg_name: str):
    """Enabled: the leg catches the defect (verdict "fail") and the gate FAILs — the precondition
    that this leg is the one doing the catching. Disabled (the test-only --disable-leg mutant
    knob, RR_HARNESS_ENABLE_DISABLE_LEG=1, set at module import above): the leg can NEVER neuter
    itself into a fake "pass" — it reports verdict "disabled", and because V2/V4/V6/period-coherence
    are all BLOCKING legs, harness.compute_gate forces the overall gate to FAIL (never PARTIAL,
    never PASS) on any disabled leg. This is the *stronger* teeth check: it is not enough for a
    leg to catch its defect when switched on — the mutant knob itself must be provably incapable
    of turning a real defect green. (Per-leg catching/attribution is proven separately by the
    positive test_*_catches_*/test_D*_fires_* tests above; this section proves the disable knob's
    own safety invariant, not leg attribution.)"""
    enabled = _legs(_run_defect(defect_id))
    assert enabled[leg_name]["verdict"] == "fail", (
        f"precondition: {defect_id} did not fire {leg_name} when the leg is enabled"
    )

    neutered_receipt = _run_defect(defect_id, disabled=(leg_name,))
    neutered = _legs(neutered_receipt)
    assert neutered[leg_name]["verdict"] == "disabled", (
        f"{defect_id}: a neutered {leg_name} must report verdict 'disabled', never 'pass' "
        f"(got {neutered[leg_name]['verdict']!r}) — a leg that can be switched off to a silent "
        f"pass is a false-teeth bug"
    )
    assert neutered_receipt["overall_gate"] != "PASS", (
        "{}: disabling BLOCKING leg {} must never green-light the overall gate to PASS "
        "(got {!r})".format(defect_id, leg_name, neutered_receipt["overall_gate"])
    )
    assert neutered_receipt["overall_gate"] == "FAIL", (
        "{}: {} is a BLOCKING leg, so a disabled/neutered verdict must force a hard FAIL "
        "(got {!r}, expected 'FAIL')".format(defect_id, leg_name, neutered_receipt["overall_gate"])
    )


def test_V2_must_fail_half_chrome_edit_slips_when_disabled():
    # D4 edits a FROZEN node (#tagline-text, inline style) — a chrome change outside any bound
    # anchor, caught by V2 when enabled. Disabling V2 must not slip it to a fake pass: V2 reports
    # 'disabled' and the gate is forced to FAIL.
    _assert_leg_has_teeth("D4", "V2")


def test_V4_must_fail_half_leak_slips_when_disabled():
    # D6 leaks the old client's name into a regenerate narrative, caught by V4 when enabled.
    # Disabling V4 must not slip it to a fake pass: V4 reports 'disabled' and the gate is forced
    # to FAIL.
    _assert_leg_has_teeth("D6", "V4")


def test_V6_must_fail_half_frozen_misclass_slips_when_disabled():
    # D11 hides a real dataset value in a manifest-surgical slot the output froze — caught by V6
    # when enabled (the date value is still correct, so V1 stays green). Disabling V6 must not
    # slip it to a fake pass: V6 reports 'disabled' and the gate is forced to FAIL.
    _assert_leg_has_teeth("D11", "V6")


def test_period_coherence_must_fail_half_stale_pbi_slips_when_disabled():
    # D14 moves the PBI screenshot/XMLA provenance to a stale quarter without touching any value —
    # caught by period-coherence when enabled. Disabling it must not slip it to a fake pass:
    # period-coherence reports 'disabled' and the gate is forced to FAIL.
    _assert_leg_has_teeth("D14", "period-coherence")


# ── 4. every emitted receipt validates against the frozen schema ───────────────

def test_every_defect_receipt_is_schema_valid():
    for defect_id in ("D1", "D2", "D5", "D6", "D7", "D8", "D11", "D12", "D14"):
        receipt = _run_defect(defect_id)
        assert harness.validate_receipt(receipt) == [], (
            f"{defect_id}: receipt failed schema validation"
        )
        # PROBE_ERROR != pass and a fired blocking leg forbids overall PASS.
        assert receipt["overall_gate"] in ("FAIL", "PARTIAL")


def test_schema_validator_rejects_a_bad_receipt():
    # Prove the validator has teeth too: a PASS gate carrying a failing leg violates the schema
    # allOf and must be rejected.
    good = _run(_SAMPLE)
    bad = json.loads(json.dumps(good))
    bad["overall_gate"] = "PASS"  # but V5 is not_captured → schema allOf forbids this
    assert harness.validate_receipt(bad) != []


def test_v2_checks_a_needs_review_node_apart_from_its_rebind_badge():
    # B-2 binds more nodes as needs-review; V2 must still see an edit inside one (the D4 class),
    # while rebind's own badge + data-rebind-* flag attributes stay licensed.
    rh = _load("rebind_html_under_test", _SKILL_DIR.parent / "rebind-html" / "rebind_html.py")

    def nr(anchor_id):
        return {"node_id": anchor_id, "anchor": {"kind": "element_id", "value": anchor_id},
                "class": "needs-review", "confidence": 0.6,
                "provenance": {"source": "t", "source_period": None},
                "data_query": {"kind": "none", "expression": "pending"}}

    template = ('<html><body><p id="tag">100% Committed since 1998</p>'
                '<img id="pic" src="a.png" alt="x"><p>chrome</p></body></html>')
    manifest = {"manifest_version": "1", "rsg_schema_version": "1", "template_id": "t",
                "format": "html", "bindings": [nr("tag"), nr("pic")]}
    output, _changes, _n = rh.rebind(template, manifest, {})
    t_root = harness.parse_html(template)
    leg = harness.leg_v2(t_root, harness.parse_html(output), manifest, template)
    assert leg["verdict"] == "pass", leg["evidence"]
    for bad in (output.replace('id="tag"', 'id="tag" style="color: rgb(250,250,250);"'),
                output.replace("100% Committed", "100% Totally Committed")):
        leg = harness.leg_v2(t_root, harness.parse_html(bad), manifest, template)
        assert leg["verdict"] == "fail", "V2 missed an edit inside a needs-review node"


def test_v4_html_catches_a_raw_ungrouped_taint_number():
    # B-3: a taint figure written raw (no $ / no grouping) survived V4 in every hidden channel.
    taint = {"old_revenue_total": "$3,102,450"}
    leaks = {
        "data- attribute": '<html><body><div data-value="3102450">chart</div></body></html>',
        "script JSON": '<html><body><script>var d={"rev":[3102450,2900000]};</script></body></html>',
        "plain text": "<html><body><p>Revenue 3102450</p></body></html>",
        "3102450.00": "<html><body><p>Revenue 3102450.00</p></body></html>",
        "formatted visible (control)": "<html><body><p>Revenue $3,102,450</p></body></html>",
    }
    for name, text in leaks.items():
        leg = harness.leg_v4(harness.parse_html(text), taint, text)
        assert leg["verdict"] == "fail", f"V4 missed the raw taint figure in the {name}"
    clean = '<html><body><p>Revenue $4,821,300</p><style>p{color:rgb(30,30,30)}</style></body></html>'
    assert harness.leg_v4(harness.parse_html(clean), taint, clean)["verdict"] == "pass"


def test_bad_input_encoding_or_json_is_exit_2_with_a_json_error_not_a_traceback():
    # B-19: a crash used to exit 1 with no stdout, indistinguishable from a gate FAIL.
    import subprocess
    import sys

    latin = _TMP / "latin1-template.html"
    latin.write_bytes("<html><body><p>Caf\u00e9 report</p></body></html>".encode("cp1252"))
    bad_manifest = _TMP / "malformed-manifest.json"
    bad_manifest.write_text("{not json", encoding="utf-8")
    for template, manifest in ((latin, _MANIFEST), (_CLEAN_OUTPUT, bad_manifest)):
        proc = subprocess.run(
            [sys.executable, str(_SKILL_DIR / "harness.py"), "--template", str(template),
             "--output", str(_CLEAN_OUTPUT), "--manifest", str(manifest), "--new-data", str(_NEW_DATA)],
            capture_output=True, text=True,
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr[-300:])
        assert json.loads(proc.stdout)["ok"] is False
        assert "Traceback" not in proc.stderr


def test_taint_flag_accepts_the_build_manifest_taint_dict():
    # B-4: build_manifest --taint-out writes taint-dict@1; feeding it to --taint crashed V4.
    import subprocess
    import sys

    bm = _load("build_manifest_under_test", _SKILL_DIR.parent / "rebind-manifest" / "build_manifest.py")
    taint_path = _TMP / "taint-dict.json"
    taint_path.write_text(json.dumps(bm.build_taint_dictionary(_SAMPLE)), encoding="utf-8")
    bad_path = _TMP / "bad-taint-dict.json"
    bad_path.write_text(json.dumps({"schema": "report-regeneration/taint-dict@1", "values": [1]}),
                        encoding="utf-8")

    def run(taint_file):
        return subprocess.run(
            [sys.executable, str(_SKILL_DIR / "harness.py"), "--template", str(_SAMPLE),
             "--output", str(_CLEAN_OUTPUT), "--manifest", str(_MANIFEST), "--new-data", str(_NEW_DATA),
             "--taint", str(taint_file)],
            capture_output=True, text=True,
        )

    proc = run(taint_path)
    v4 = _legs(json.loads(proc.stdout))["V4"]
    assert v4["verdict"] in ("pass", "fail"), v4["evidence"]  # V4 ran: no PROBE_ERROR
    proc = run(bad_path)
    assert proc.returncode == 2
    assert "taint-dict@1" in json.loads(proc.stdout)["error"]


def test_render_referee_leaves_no_scratch_screenshot_behind():
    # B-22: every Playwright run left a full-page PNG of the report in the temp dir. Stubbed page.
    referee = _load("render_referee_under_test", _SKILL_DIR / "render_referee.py")
    written = []

    class Page:
        def on(self, *_a):
            pass

        def goto(self, *_a, **_k):
            pass

        def wait_for_timeout(self, *_a):
            pass

        def evaluate(self, *_a):
            return []

        def screenshot(self, path, **_k):
            Path(path).write_bytes(b"\x89PNG report pixels")
            written.append(path)

        def close(self):
            pass

    class Browser:
        def new_page(self):
            return Page()

    run = referee._render_once(Browser(), _CLEAN_OUTPUT, None, 1000)
    assert written and not any(Path(p).exists() for p in written), "scratch screenshot left behind"
    assert run["screenshot_path"] is None
    kept = _TMP / "asked-for.png"
    run = referee._render_once(Browser(), _CLEAN_OUTPUT, str(kept), 1000)
    assert kept.exists() and run["screenshot_path"] == str(kept), "an asked-for screenshot is kept"


# ── standalone runner (no pytest required) ─────────────────────────────────────

def _main() -> int:
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {name}\n      {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {name}\n      {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    import sys
    sys.exit(_main())
