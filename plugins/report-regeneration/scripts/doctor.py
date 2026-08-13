#!/usr/bin/env python3
"""
report-regeneration — environment doctor (Phase 0, gate G0-d).

Probes every external tool the pipeline can use, on THIS host, and emits a
capability receipt. Stdlib-only. Fail-CLOSED by contract: a missing tool maps
to a degradation mode and the affected QA leg reports PARTIAL / not_captured —
never a silent PASS (accuracy-near-guarantee W5: "a probe error is never a pass";
"A SKIP IS NOT A PASS").

Run:  python3 plugins/report-regeneration/scripts/doctor.py [--json]
Exit: 0 always (this is a probe, not a gate). The `verdict` field carries the
      PASS / PARTIAL / FAIL signal that downstream gates consume.
"""
from __future__ import annotations

import importlib.util
import json
import platform
import shutil
import subprocess
import sys

# Tier-A = Python stdlib, always available. The ML-free harness legs
# (V2 frozen-complement diff, V4 taint egress, V6 coverage, period-coherence)
# stand on exactly these — so the load-bearing checks never depend on a pip install.
TIER_A_STDLIB = [
    "json", "re", "zipfile", "xml.etree.ElementTree",
    "html.parser", "hashlib", "difflib", "base64", "urllib.request",
]

# (name, kind, probe, tier, powers, degrade_mode)
#   kind: "py" = import name | "cli" = executable on PATH
TOOLS = [
    ("lxml",        "py",  "lxml",        "B", "HTML/XML structural parse",             "fall back to stdlib html.parser (lower fidelity on malformed HTML)"),
    ("selectolax",  "py",  "selectolax",  "B", "fast HTML parse",                       "use lxml, else stdlib html.parser"),
    ("jinja2",      "py",  "jinja2",      "B", "HTML template rebind",                  "REQUIRED for the HTML lane (v0.1.0) — that lane blocks until installed"),
    ("python-docx", "py",  "docx",        "B", "Office (.docx) structural read/write",  "Office lane (v0.2.0) unavailable"),
    ("docxtpl",     "py",  "docxtpl",     "B", "Office narrative regenerate",           "use python-docx direct manipulation (more code)"),
    ("playwright",  "py",  "playwright",  "B", "HTML render referee + PBI screenshot",  "V5 render referee -> not_captured; PBI screenshot -> user-provided image only"),
    ("weasyprint",  "py",  "weasyprint",  "B", "accessible PDF/UA emit",                "PDF/UA emit unavailable; ship HTML only + flag manual PDF step"),
    ("docling",     "py",  "docling",     "B", "layout inference on rendered inputs",   "native-parse (Tier-0) inference only; rendered-only inputs unsupported"),
    ("soffice",     "cli", "soffice",     "B", "LibreOffice docx->PDF export",          "Office PDF export unavailable; emit .docx only"),
    ("verapdf",     "cli", "verapdf",     "B", "PDF/UA accessibility validation",       "PDF a11y leg -> not_captured (PARTIAL, never PASS)"),
    ("node",        "cli", "node",        "B", "axe-core a11y runner host",             "HTML a11y (axe) leg -> not_captured"),
    ("pyadomd",     "py",  "pyadomd",     "B", "native XMLA client (Windows/.NET only)", "EXPECTED-ABSENT on macOS -> use Power BI REST executeQueries (DAX) instead"),
]


def probe_py(mod: str):
    try:
        spec = importlib.util.find_spec(mod)
    except (ImportError, ValueError, ModuleNotFoundError):
        return None
    if spec is None:
        return None
    try:
        m = __import__(mod)
        return getattr(m, "__version__", "") or "(present)"
    except Exception:
        return "(present, version unknown)"


def probe_cli(exe: str):
    if not shutil.which(exe):
        return None
    for flag in ("--version", "-version", "version", "--help"):
        try:
            out = subprocess.run([exe, flag], capture_output=True, text=True, timeout=10)
            text = (out.stdout or out.stderr).strip()
            if text:
                return text.splitlines()[0][:120]
        except Exception:
            continue
    return "(present)"


def main() -> int:
    as_json = "--json" in sys.argv
    results = []
    for name, kind, probe, tier, powers, degrade in TOOLS:
        ver = probe_py(probe) if kind == "py" else probe_cli(probe)
        present = ver is not None
        results.append({
            "tool": name, "kind": kind, "tier": tier, "present": present,
            "version": ver if present else None, "powers": powers,
            "degrade_mode": None if present else degrade,
        })

    tier_a_ok = all(
        importlib.util.find_spec(m.split(".")[0]) is not None for m in TIER_A_STDLIB
    )
    missing_b = [r["tool"] for r in results if not r["present"]]
    # fail-CLOSED: any missing Tier-B tool -> PARTIAL, never PASS. Broken stdlib -> FAIL.
    verdict = "PASS" if (tier_a_ok and not missing_b) else ("PARTIAL" if tier_a_ok else "FAIL")

    receipt = {
        "schema": "report-regeneration/doctor@1",
        "host": {"platform": platform.platform(), "python": platform.python_version()},
        "tier_a_stdlib_ok": tier_a_ok,
        "verdict": verdict,
        "missing": missing_b,
        "tools": results,
        "note": "A SKIP IS NOT A PASS: a missing tool degrades its QA leg to PARTIAL/not_captured, never a silent pass.",
    }

    if as_json:
        print(json.dumps(receipt, indent=2))
        return 0

    print(f"report-regeneration doctor — verdict: {verdict}")
    print(f"  host: {receipt['host']['platform']} / python {receipt['host']['python']}")
    print(f"  tier-A stdlib legs (taint / diff / manifest / period-coherence / V6): "
          f"{'OK' if tier_a_ok else 'BROKEN — hard FAIL'}")
    print("  external tools:")
    for r in results:
        mark = "OK  " if r["present"] else "--  "
        ver = f"  ({r['version']})" if r["present"] and r["version"] else ""
        print(f"    [{mark}] {r['tool']:<12} tier-{r['tier']}  {r['powers']}{ver}")
        if not r["present"]:
            print(f"             -> {r['degrade_mode']}")
    if missing_b:
        print(f"\n  {len(missing_b)} tool(s) absent -> verdict PARTIAL "
              f"(fail-closed; affected legs report not_captured, never PASS).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
