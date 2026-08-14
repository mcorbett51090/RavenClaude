#!/usr/bin/env python3
"""Gate 193 driver — the static schema extractor + fetch hardening + brand.css emit
sanitization (P2). Property-based (NO .json byte-golden — the prettier-vs-json.dumps
trap), file fixtures only (NO port bind / no http.server). Proves, and proves the TEETH
of, six things with per-collector must-fail mutants:

  1. REGULAR fixture  → spacing.base_unit==8, type_scale.ratio≈1.25, 3 ordered shadows,
     2 breakpoints, components has button/card/nav, every dimension capture_method=="static",
     and design-schema.json validates via check-design-schema.py.
  2. IRREGULAR fixture → PER-DIMENSION null (spacing.base_unit is None AND type_scale.ratio
     is None AND grid degrades), type_scale.sizes still non-empty (honest degrade, not a wipe).
  3. hostile-fetch     → _fetch REFUSES a file:// and a metadata-range sub-resource BEFORE any
     network (their bytes never reach design-schema.json / brand.json); the refusals are noted.
  4. hostile-custom-prop → the url() beacon is ABSENT from brand.css (whole declaration dropped).
  5. REGRESSION        → brand.json / report-template.html / brand-summary.md are byte-identical
     to the pre-P2 (git HEAD) extractor on a benign fixture (timestamp masked). brand.css is
     deliberately excluded — the emit sanitization is a security fix on that one writer.
  6. TEETH             → 7 must-fail mutants (≥ per-collector): a spacing collector hardcoding
     base_unit, _derive_type_scale→empty, a _fetch that keeps FileHandler, a neutered emit
     sanitizer, and empty shadows/breakpoints/components collectors — each MUST break its
     assertion, or the gate is toothless.

macOS/bash-agnostic: pure Python (the bash wrapper only exec's this). No network.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
ROOT = SKILL.parents[3]  # .../skills/brand-extraction -> repo root
EXTRACT = SKILL / "extract_brand.py"
REL_EXTRACT = "plugins/ravenclaude-core/skills/brand-extraction/extract_brand.py"
CHECK = SKILL.parents[1] / "scripts" / "check-design-schema.py"
FX = ROOT / "tests" / "fixtures" / "design-schema" / "reference-site"

_TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_fails = 0


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def bad(msg: str) -> None:
    global _fails
    _fails += 1
    print(f"  ✗ {msg}")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_extract(mod, fixture: str, out_dir: Path) -> tuple[dict, str]:
    """Run mod.extract on a local fixture; return (design_schema, brand_css_text)."""
    html = (FX / fixture).read_text(encoding="utf-8")
    mod.extract(
        "http://ref.example.test/",
        str(out_dir),
        max_stylesheets=8,
        download=False,
        timeout=5,
        entry_html=html,
    )
    schema = json.loads((out_dir / "design-schema.json").read_text(encoding="utf-8"))
    css = (out_dir / "brand.css").read_text(encoding="utf-8")
    return schema, css


# --------------------------------------------------------------------------- #
# Property checks (used both for the real assertions AND as the mutant oracles)
# --------------------------------------------------------------------------- #


def chk_spacing8(schema: dict) -> bool:
    return schema["spacing"]["base_unit"] == 8


def chk_spacing_null(schema: dict) -> bool:
    return schema["spacing"]["base_unit"] is None


def chk_ratio125(schema: dict) -> bool:
    r = schema["type_scale"]["ratio"]
    return r is not None and abs(r - 1.25) <= 0.05


def chk_ratio_null(schema: dict) -> bool:
    return schema["type_scale"]["ratio"] is None


def chk_sizes_nonempty(schema: dict) -> bool:
    return len(schema["type_scale"]["sizes"]) > 0


def chk_shadows3_ordered(schema: dict) -> bool:
    sh = schema["elevation"]["shadows"]
    if len(sh) != 3:
        return False
    # already ranked ascending by the collector; confirm blur weight is non-decreasing
    weights = [_first_blur(s) for s in sh]
    return weights == sorted(weights)


def _first_blur(shadow: str) -> float:
    nums = re.findall(r"(-?\d*\.?\d+)px", shadow.split(",")[0])
    return float(nums[2]) if len(nums) >= 3 else 0.0


def chk_breakpoints2(schema: dict) -> bool:
    return len(schema["grid"]["breakpoints"]) == 2


def chk_grid_null(schema: dict) -> bool:
    g = schema["grid"]
    return g["columns"] is None and g["container_max"] is None and g["breakpoints"] == []


def chk_components_bcn(schema: dict) -> bool:
    names = {c["name"] for c in schema["components"]}
    return {"button", "card", "nav"}.issubset(names)


def chk_all_static(schema: dict) -> bool:
    if schema.get("capture_method") != "static":
        return False
    return all(schema[d]["capture_method"] == "static" for d in ("spacing", "type_scale", "grid", "elevation"))


def chk_no_beacon(css: str) -> bool:
    low = css.lower()
    return "url(" not in low and "beacon" not in low and "attacker" not in low


# --------------------------------------------------------------------------- #
# 1) REGULAR fixture — positive property assertions
# --------------------------------------------------------------------------- #


def test_regular(tmp: Path, real) -> None:
    schema, _ = run_extract(real, "regular.html", tmp / "regular")
    for label, fn in (
        ("spacing.base_unit == 8", chk_spacing8),
        ("type_scale.ratio within tolerance of ~1.25", chk_ratio125),
        ("type_scale.sizes non-empty", chk_sizes_nonempty),
        ("elevation.shadows: 3 entries, ordered ascending", chk_shadows3_ordered),
        ("grid.breakpoints: 2", chk_breakpoints2),
        ("components has button/card/nav", chk_components_bcn),
        ("every dimension capture_method == 'static'", chk_all_static),
    ):
        (ok if fn(schema) else bad)(f"regular: {label}")
    # validates against the P1 conformance checker
    rc = subprocess.run(
        [sys.executable, str(CHECK), str(tmp / "regular" / "design-schema.json")],
        capture_output=True,
    ).returncode
    (ok if rc == 0 else bad)("regular: design-schema.json validates via check-design-schema.py")


# --------------------------------------------------------------------------- #
# 2) IRREGULAR fixture — per-dimension null (NOT "no crash")
# --------------------------------------------------------------------------- #


def test_irregular(tmp: Path, real) -> None:
    schema, _ = run_extract(real, "irregular.html", tmp / "irregular")
    for label, fn in (
        ("spacing.base_unit is None (no clean base-unit fit)", chk_spacing_null),
        ("type_scale.ratio is None (no ratio within tolerance)", chk_ratio_null),
        ("type_scale.sizes still non-empty (honest degrade, not a wipe)", chk_sizes_nonempty),
        ("grid degrades to null (columns/container_max None, breakpoints [])", chk_grid_null),
    ):
        (ok if fn(schema) else bad)(f"irregular: {label}")
    rc = subprocess.run(
        [sys.executable, str(CHECK), str(tmp / "irregular" / "design-schema.json")],
        capture_output=True,
    ).returncode
    (ok if rc == 0 else bad)("irregular: design-schema.json still validates (null-degraded)")
    if schema["confidence_notes"]:
        ok("irregular: confidence_notes explain the null degrade")
    else:
        bad("irregular: null degrade carried NO confidence_notes")


# --------------------------------------------------------------------------- #
# 3) hostile-fetch — file:// + metadata sub-resources REFUSED (bytes never land)
# --------------------------------------------------------------------------- #


def test_hostile_fetch(tmp: Path, real) -> None:
    # unit: the guard refuses BEFORE any socket (literal IP / scheme — no network)
    for url, must_in in (
        ("file:///etc/passwd", "scheme"),
        ("http://169.254.169.254/latest/meta-data/", "blocked address"),
        ("http://127.0.0.1/", "blocked address"),
        ("http://10.0.0.1/", "blocked address"),
        ("ftp://example.com/x", "scheme"),
    ):
        body, _, err = real._fetch(url, 5, max_bytes=1000)
        refused = body is None and err is not None and "refused" in err and must_in in err
        (ok if refused else bad)(f"_fetch refuses {url} ({err!r})")
    # e2e: the extractor completes, records the refusals, and no hostile bytes reach the outputs
    schema, _ = run_extract(real, "hostile-fetch.html", tmp / "hostile-fetch")
    brand = json.loads((tmp / "hostile-fetch" / "brand.json").read_text(encoding="utf-8"))
    notes = " ".join(brand["confidence_notes"])
    if "file:///etc/passwd" in notes and "169.254.169.254" in notes and "refused" in notes:
        ok("hostile-fetch: both refusals recorded in confidence_notes")
    else:
        bad("hostile-fetch: refusals NOT recorded")
    blob = json.dumps(schema)
    if "root:" not in blob and "/bin/bash" not in blob and "meta-data" not in blob:
        ok("hostile-fetch: no fetched sub-resource content reached design-schema.json")
    else:
        bad("hostile-fetch: hostile sub-resource content LEAKED into design-schema.json")


# --------------------------------------------------------------------------- #
# 4) hostile-custom-prop — the url() beacon is ABSENT from brand.css
# --------------------------------------------------------------------------- #


def test_hostile_custom_prop(tmp: Path, real) -> None:
    _, css = run_extract(real, "hostile-custom-prop.html", tmp / "hostile-cp")
    (ok if chk_no_beacon(css) else bad)(
        "hostile-custom-prop: url() beacon absent from brand.css (whole declaration dropped)"
    )
    # the benign color-valued custom property still survives (not a drop-everything wipe)
    if "--brand-teal: #009688;" in css:
        ok("hostile-custom-prop: the benign --brand-teal color survives (no over-drop)")
    else:
        bad("hostile-custom-prop: a benign custom property was wrongly dropped")


# --------------------------------------------------------------------------- #
# 5) REGRESSION — brand.json / report / summary byte-identical to pre-P2 HEAD
# --------------------------------------------------------------------------- #


def test_regression(tmp: Path) -> None:
    head_src = subprocess.run(
        ["git", "show", f"HEAD:{REL_EXTRACT}"], cwd=str(ROOT), capture_output=True, text=True
    )
    if head_src.returncode != 0 or not head_src.stdout.strip():
        print("  ! REGRESSION SKIPPED — no git HEAD baseline available (THIS IS NOT A PASS)")
        return
    head_py = tmp / "head_extract.py"
    head_py.write_text(head_src.stdout, encoding="utf-8")
    # Both the pre-P2 baseline and the working extractor consume the SAME data: URL (the
    # baseline predates --html-file), so the entry HTML is identical on both sides.
    import base64

    html_bytes = (FX / "regular.html").read_bytes()
    data_url = "data:text/html;base64," + base64.b64encode(html_bytes).decode()
    for name, script in (("before", head_py), ("after", EXTRACT)):
        rc = subprocess.run(
            [sys.executable, str(script), data_url, "--out", str(tmp / name), "--no-download"],
            capture_output=True,
        ).returncode
        if rc != 0:
            bad(f"regression: extractor run '{name}' failed to execute")
            return
    all_same = True
    for f in ("brand.json", "report-template.html", "brand-summary.md"):
        b = _TS_RE.sub("<TS>", (tmp / "before" / f).read_text(encoding="utf-8"))
        a = _TS_RE.sub("<TS>", (tmp / "after" / f).read_text(encoding="utf-8"))
        same = a == b
        all_same = all_same and same
        (ok if same else bad)(f"regression: {f} byte-identical to pre-P2 HEAD (timestamp masked)")
    if all_same:
        ok("regression: existing brand kit writers unchanged by P2")


# --------------------------------------------------------------------------- #
# 6) TEETH — must-fail mutants (>= per-collector), each MUST break its assertion
# --------------------------------------------------------------------------- #

# (label, [(old, new), ...], mode) where mode is either a fixture+oracle tuple or "fetch".
_FETCH_GUARD_OLD = (
    "    _guard_err = _fetch_scheme_host_guard(url)\n"
    "    if _guard_err is not None:\n"
    "        return None, None, _guard_err\n"
    "    try:\n"
    '        req = Request(url, headers={"User-Agent": _UA, "Accept": "*/*"})\n'
    "        with _get_http_opener().open(req, timeout=timeout) as resp:"
)
_FETCH_GUARD_NEW = (
    "    try:\n"
    "        import urllib.request as _mut_ur\n"
    '        req = Request(url, headers={"User-Agent": _UA, "Accept": "*/*"})\n'
    "        with _mut_ur.urlopen(req, timeout=timeout) as resp:"
)

MUTANTS = [
    {
        "label": "spacing collector hardcodes base_unit → irregular null assert catches it",
        "repls": [("    best_base = None", "    best_base = 8  # MUTANT hardcode")],
        "fixture": "irregular.html",
        "oracle": chk_spacing_null,  # real: True (null). mutant: 8 → False → caught
    },
    {
        "label": "_derive_type_scale → empty sizes → 'sizes non-empty' catches it",
        "repls": [
            ("    s = sorted(sizes)\n    if not s:", "    s = sorted(sizes)\n    return None, None, [], None  # MUTANT\n    if not s:")
        ],
        "fixture": "regular.html",
        "oracle": chk_sizes_nonempty,
    },
    {
        "label": "_collect_shadows → [] → '3 shadows' catches it",
        "repls": [
            ("    out: list[str] = []\n    for decl in _BOX_SHADOW_DECL_RE.findall(css_text):", "    out: list[str] = []\n    return []  # MUTANT\n    for decl in _BOX_SHADOW_DECL_RE.findall(css_text):")
        ],
        "fixture": "regular.html",
        "oracle": chk_shadows3_ordered,
    },
    {
        "label": "_collect_breakpoints → [] → '2 breakpoints' catches it",
        "repls": [
            ("    out: list[str] = []\n    for val in _MEDIA_WIDTH_RE.findall(css_text):", "    out: list[str] = []\n    return []  # MUTANT\n    for val in _MEDIA_WIDTH_RE.findall(css_text):")
        ],
        "fixture": "regular.html",
        "oracle": chk_breakpoints2,
    },
    {
        "label": "_collect_component_hints → [] → 'button/card/nav' catches it",
        "repls": [
            ("    found: dict[str, dict] = {}\n    for selector, decls in _RULE_RE.findall(css_text):", "    found: dict[str, dict] = {}\n    return []  # MUTANT\n    for selector, decls in _RULE_RE.findall(css_text):")
        ],
        "fixture": "regular.html",
        "oracle": chk_components_bcn,
    },
    {
        "label": "emit sanitizer neutered (passthrough) → hostile beacon catches it",
        "repls": [
            ("    for fn in (_san_color, _san_length, _san_number, _san_shadow):\n        out = fn(value)", "    return str(value)  # MUTANT passthrough\n    for fn in (_san_color, _san_length, _san_number, _san_shadow):\n        out = fn(value)")
        ],
        "fixture": "hostile-custom-prop.html",
        "oracle": chk_no_beacon,
        "css": True,
    },
]


def _apply_mutant(src: str, repls: list[tuple[str, str]]) -> str | None:
    out = src
    for old, new in repls:
        if old not in out:
            return None  # anchor drifted
        out = out.replace(old, new, 1)
    return out


def test_mutants(tmp: Path, real) -> None:
    src = EXTRACT.read_text(encoding="utf-8")
    for i, m in enumerate(MUTANTS):
        mutated = _apply_mutant(src, m["repls"])
        if mutated is None:
            bad(f"teeth m{i}: anchor drifted (update the Gate 193 mutant) — {m['label']}")
            continue
        mpath = tmp / f"mutant_{i}.py"
        mpath.write_text(mutated, encoding="utf-8")
        try:
            mod = load_module(mpath, f"eb_mut_{i}")
            schema, css = run_extract(mod, m["fixture"], tmp / f"mut_out_{i}")
            passes = m["oracle"](css if m.get("css") else schema)
        except Exception as exc:  # a mutant that crashes is also "caught"
            passes = False
            _ = exc
        # mutant is CAUGHT iff the oracle now FAILS (returns False)
        (ok if not passes else bad)(f"teeth m{i}: {m['label']}")

    # the fetch mutant needs a direct _fetch call, not an extract run
    mutated = _apply_mutant(src, [(_FETCH_GUARD_OLD, _FETCH_GUARD_NEW)])
    if mutated is None:
        bad("teeth m6: _fetch guard anchor drifted (update the Gate 193 mutant)")
    else:
        mpath = tmp / "mutant_fetch.py"
        mpath.write_text(mutated, encoding="utf-8")
        mod = load_module(mpath, "eb_mut_fetch")
        existing = str((FX / "regular.html").resolve())
        # A generous cap so the (small) fixture is returned whole — the FileHandler-keeping
        # mutant READS the local file (body not None); the real, guarded _fetch REFUSES the
        # file:// scheme up front and returns None regardless of cap.
        body, _, _ = mod._fetch("file://" + existing, 5, max_bytes=1_000_000)
        real_body, _, real_err = real._fetch("file://" + existing, 5, max_bytes=1_000_000)
        caught = body is not None and real_body is None and "refused" in (real_err or "")
        (ok if caught else bad)(
            "teeth m6: a _fetch that keeps FileHandler READS the file (real _fetch refuses it)"
        )


def main() -> int:
    real = load_module(EXTRACT, "extract_brand_real")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        print("Gate 193 — static schema extractor + fetch hardening + brand.css emit sanitization")
        test_regular(tmp, real)
        test_irregular(tmp, real)
        test_hostile_fetch(tmp, real)
        test_hostile_custom_prop(tmp, real)
        test_regression(tmp)
        test_mutants(tmp, real)
    print()
    if _fails == 0:
        print("Gate 193 — ALL PASS")
        return 0
    print(f"Gate 193 — {_fails} assertion(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
