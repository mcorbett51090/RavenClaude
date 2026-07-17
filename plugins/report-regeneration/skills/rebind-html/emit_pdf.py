#!/usr/bin/env python3
"""
emit_pdf.py — STANDALONE, OPTIONAL-DEPENDENCY HTML→PDF/UA emitter for report-regeneration
(the `rebind-html` skill's enhanced-fidelity module).

NOT wired into rebind_html.py (rebind_html.py is not edited by this module — it stays a genuinely
standalone unit a future orchestrator step wires into the pipeline). Given a regenerated HTML
output (rebind_html.py's own output, or any HTML file), this emits a **tagged/accessible PDF**
(PDF/UA-1, ISO 14289-1) via WeasyPrint when WeasyPrint is importable AND its native rendering
stack (Pango/Cairo/GDK-Pixbuf/GObject, which WeasyPrint's `text/ffi.py` `dlopen()`s at IMPORT
time via cffi) actually loads in this interpreter. Absent either, this is a clean SKIP — never a
fake emit, never a fabricated PDF path, never an unhandled exception. Same discipline as this
plugin's fidelity harness (`../report-fidelity-harness/harness.py`'s `leg_v5()`: "PROBE_ERROR !=
pass … a render/parse crash never reads as fidelity OK") and its standalone sibling
`../report-fidelity-harness/render_referee.py`.

Why a broad `except Exception` around the WeasyPrint import (not just `except ImportError`):
`importlib.util.find_spec("weasyprint")` only proves the wheel is unpacked on disk — it does NOT
prove the module actually imports. WeasyPrint's `weasyprint.text.ffi` module calls
`ffi.dlopen(...)` against the system's Pango/Cairo/GObject shared libraries the MOMENT
`import weasyprint` runs; if those native libraries are absent (common on a bare macOS host with
no Homebrew GTK stack, or a minimal Linux container), the import raises `OSError`, not
`ImportError`. `weasyprint_capability()` performs the REAL import and reports whatever actually
happened — the "package is on disk but doesn't import here" case is real and this plugin's own
Phase-0 environment hits it (verified this session: `pip list` shows weasyprint installed in the
provided venv, yet `import weasyprint` there raises `OSError: cannot load library
'libgobject-2.0-0'` because no Homebrew/system GTK stack is present on this host — the venv having
the PYTHON PACKAGE does not by itself guarantee the NATIVE capability).

Public API:

    weasyprint_capability() -> dict
        {"available": bool, "present_on_disk": bool, "reason": str|None, "note": str|None,
        "version": str|None}. `available=False` covers BOTH "not installed" and "installed but
        failed to import" — callers do not need to distinguish.

    emit_pdf(html_path, out_path, *, base_url=None, pdf_variant="pdf/ua-1") -> dict
        {"schema", "ok", "verdict" ("pass"|"fail"|"skip"), "pdf_path", "pdf_variant", "tagged",
        "capability", "note"}. `verdict="skip"` = the optional dependency is unusable here (never
        an error, never an exception). `verdict="fail"` = WeasyPrint WAS usable but the emit
        itself failed for some other reason (bad input HTML, disk-full, etc — a REAL, actionable
        problem, distinct from a clean absence). `verdict="pass"` = a real, verified (magic-header
        checked) tagged PDF/UA-1 file was written.

Usage (CLI):
    python3 emit_pdf.py --html tests/fixtures/report-regeneration/sample-report.html \
        --out    tests/fixtures/report-regeneration/_out/sample-report.pdf
    python3 emit_pdf.py --html <relative path> --out <relative path> --pdf-variant pdf/ua-1 --pretty

Exit codes: `0` — verdict `pass` OR `skip` (a skip is not an error: the optional capability is
simply unavailable, mirrors scripts/powerbi_probe.py's "a probe error is never treated as a hard
failure" framing applied to an optional-dependency gap); `1` — verdict `fail` (WeasyPrint was
usable but the emit itself failed — a real, actionable problem worth a non-zero exit); `2` —
usage / path-guard error (message on stderr + a best-effort JSON error object on stdout, mirrors
`../rebind-html/rebind_html.py`'s `_emit_error`).

Constraints (binding, matches every other script in this plugin): Python 3.9.6-safe (`from
__future__ import annotations`; `X | Y` / `dict[str, T]` appear only in annotation position, which
the future-import defers to a string, never evaluated at runtime — safe on 3.9, exactly as
harness.py/rebind_html.py already do throughout). Optional-import guarded: importing this module
under stdlib python3 (no WeasyPrint, or a WeasyPrint whose native libs are absent) never raises.
No network, no subprocess. Path-guarded: `--html`/`--out` mirror `../rebind-html/rebind_html.py`'s
`_repo_root()`/`_guard_path()` convention exactly (relative paths only, no `..` traversal, must
resolve inside the repo root) — this file is that skill's direct sibling.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path

SCHEMA = "report-regeneration/emit-pdf@1"
PDF_MAGIC = b"%PDF-"

INSTALL_NOTE = (
    "WeasyPrint (+ the native Pango/Cairo/GDK-Pixbuf/GObject stack it dlopen()s via cffi at "
    "IMPORT time) is not usable in this interpreter. Install path: `pip install weasyprint` "
    "PLUS the native libraries -- macOS: `brew install pango` (pulls in cairo/gdk-pixbuf/glib "
    "transitively); Debian/Ubuntu: `apt install libpango-1.0-0 libpangocairo-1.0-0 "
    "libgdk-pixbuf2.0-0 libcairo2 libffi-dev`; see "
    "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation."
)


class EmitPdfError(Exception):
    """Raised for path-guard / usage failures (surfaced as CLI exit 2). NEVER raised for an
    absent/broken optional dependency -- that is always a clean `skip` verdict, never an
    exception (mirrors rebind_html.py's RebindError convention: this exception means "abort",
    not "degrade")."""


# ── path safety (mirrors ../rebind-html/rebind_html.py's _repo_root()/_guard_path() convention
# exactly -- this file is that skill's direct sibling and inherits the same contract) ──


def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    root = here
    for _ in range(10):
        if (root / ".repo-layout.json").is_file() or (root / "AGENTS.md").is_file():
            return root
        if root.parent == root:
            break
        root = root.parent
    # Fallback: this file lives at plugins/report-regeneration/skills/rebind-html/emit_pdf.py
    return (here / ".." / ".." / ".." / "..").resolve()


def _guard_path(raw: str, *, must_exist: bool) -> Path:
    """Resolve `raw` and reject traversal / absolute-escape. Never touches the filesystem
    outside the repo root. Raises EmitPdfError (never a bare OSError) on any violation."""
    if not raw:
        raise EmitPdfError("empty path")
    p = Path(raw)
    if p.is_absolute():
        raise EmitPdfError(f"absolute paths are not allowed: {raw!r}")
    if ".." in p.parts:
        raise EmitPdfError(f"path traversal ('..') is not allowed: {raw!r}")
    repo_root = _repo_root().resolve()
    resolved = (Path.cwd() / p).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise EmitPdfError(f"path escapes the repo root: {resolved}") from exc
    if must_exist and not resolved.is_file():
        raise EmitPdfError(f"input file not found: {raw!r} (resolved {resolved})")
    return resolved


# ── capability detection (two-tier: cheap find_spec() gate, then a REAL import attempt --
# see module docstring for why find_spec alone cannot be trusted here) ──


def weasyprint_capability() -> dict:
    """Never raises. See module docstring for the exact return shape and why `available=False`
    covers both "not installed" and "installed but native libs absent"."""
    present_on_disk = False
    try:
        present_on_disk = importlib.util.find_spec("weasyprint") is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        present_on_disk = False
    if not present_on_disk:
        return {
            "available": False, "present_on_disk": False,
            "reason": "weasyprint is not installed in this interpreter",
            "note": INSTALL_NOTE, "version": None,
        }
    try:
        # WeasyPrint's own weasyprint/text/ffi.py `_dlopen()` helper does an unconditional
        # `print(...)` straight to real stdout on a native-library load failure, right before
        # re-raising -- redirect stdout during the probe so that banner never leaks into a
        # caller's stdout-is-JSON contract (this module's CLI prints exactly one JSON object to
        # stdout; see main()). The captured text is folded into `reason` below so nothing is lost.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            import weasyprint  # noqa: F401  -- broad except below: a native dlopen() failure
                                # inside this import raises OSError, not ImportError (see docstring)
    except Exception as exc:  # pragma: no cover - exercised whenever the native stack is absent
        noise = buf.getvalue().strip()
        reason = f"{type(exc).__name__}: {exc}"
        if noise:
            reason += f" (WeasyPrint also printed: {noise!r})"
        return {
            "available": False, "present_on_disk": True,
            "reason": reason, "note": INSTALL_NOTE, "version": None,
        }
    return {
        "available": True, "present_on_disk": True, "reason": None, "note": None,
        "version": getattr(weasyprint, "__version__", None),
    }


def _capability_reason(cap: dict) -> str:
    if cap["reason"]:
        return f"{cap['reason']} — {cap['note']}"
    return cap["note"] or "weasyprint unavailable"


def _skip_receipt(cap: dict) -> dict:
    return {
        "schema": SCHEMA, "ok": False, "verdict": "skip",
        "pdf_path": None, "pdf_variant": None, "tagged": False,
        "capability": cap, "note": _capability_reason(cap),
    }


# ── the emitter ──


def emit_pdf(html_path: str, out_path: str, *, base_url: str | None = None,
             pdf_variant: str = "pdf/ua-1") -> dict:
    """
    Render `html_path` to a tagged/accessible PDF at `out_path` via WeasyPrint.
    `html_path`/`out_path` are repo-root-relative paths, guarded the same way
    `../rebind-html/rebind_html.py` guards `--template`/`--out`.

    NEVER raises. Three outcomes, all returned as a receipt dict (see module docstring):
      - `verdict="skip"`   — WeasyPrint unusable in this interpreter (absent, or native libs
                             missing). The clean, expected outcome under stdlib python3.
      - `verdict="fail"`   — WeasyPrint WAS usable but the emit failed for some other real
                             reason (bad --html path, malformed HTML WeasyPrint chokes on, an
                             internal WeasyPrint exception, a zero-byte or non-PDF output file).
      - `verdict="pass"`   — a real PDF/UA-1 file was written and magic-header verified.
    """
    cap = weasyprint_capability()
    if not cap["available"]:
        return _skip_receipt(cap)

    receipt = {
        "schema": SCHEMA, "ok": False, "verdict": "fail",
        "pdf_path": None, "pdf_variant": pdf_variant, "tagged": False,
        "capability": cap, "note": None,
    }

    try:
        resolved_html = _guard_path(html_path, must_exist=True)
        resolved_out = _guard_path(out_path, must_exist=False)
    except EmitPdfError as exc:
        receipt["note"] = f"input error: {exc}"
        return receipt

    try:
        import weasyprint
        html_doc = weasyprint.HTML(
            filename=str(resolved_html), base_url=base_url or str(resolved_html.parent)
        )
        resolved_out.parent.mkdir(parents=True, exist_ok=True)
        # pdf_variant='pdf/ua-1' sets pdf_tags=True internally (WeasyPrint's own
        # weasyprint/pdf/pdfua.py VARIANTS mapping) -- this IS what makes the output a real
        # tagged/accessible PDF, not merely a plain one with a PDF/UA label slapped on.
        html_doc.write_pdf(target=str(resolved_out), pdf_variant=pdf_variant)
    except Exception as exc:  # never let a WeasyPrint-internal failure propagate uncaught --
                              # this is the "fail, never a crash" half of the module's contract
        receipt["note"] = f"WeasyPrint emit failed: {type(exc).__name__}: {exc}"
        return receipt

    if not resolved_out.is_file() or resolved_out.stat().st_size == 0:
        receipt["note"] = "WeasyPrint reported no exception but wrote no non-empty PDF file"
        return receipt

    header = resolved_out.read_bytes()[:5]
    if header != PDF_MAGIC:
        receipt["note"] = f"output file does not carry a PDF magic header (got {header!r})"
        return receipt

    receipt.update({
        "ok": True, "verdict": "pass", "pdf_path": str(resolved_out), "tagged": True,
        "note": f"emitted a tagged {pdf_variant} document via WeasyPrint {cap['version']}",
    })
    return receipt


# ── CLI ──


def _emit_error(message: str) -> None:
    print(json.dumps({"schema": SCHEMA, "ok": False, "error": message}), file=sys.stdout)
    print(f"[error] {message}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="emit_pdf.py",
        description="Standalone, optional-dependency HTML->PDF/UA emitter (WeasyPrint) for "
                    "report-regeneration.",
    )
    p.add_argument("--html", required=True, metavar="PATH", help="input HTML, relative path")
    p.add_argument("--out", required=True, metavar="PATH", help="output PDF path, relative path")
    p.add_argument("--base-url", default=None, dest="base_url",
                   help="base URL for resolving relative asset URLs (default: the HTML file's dir)")
    p.add_argument("--pdf-variant", default="pdf/ua-1", dest="pdf_variant",
                   choices=["pdf/ua-1", "pdf/ua-2", "pdf/a-1b", "pdf/a-2b", "pdf/a-3b"],
                   help="WeasyPrint PDF variant (default: pdf/ua-1, tagged/accessible)")
    p.add_argument("--pretty", action="store_true", help="pretty-print the JSON receipt")
    return p


def main(argv: list) -> int:
    args = build_parser().parse_args(argv)

    try:
        # CLI-level guard BEFORE calling emit_pdf() so a bad --html/--out is reported as a
        # usage error (exit 2), not folded into emit_pdf()'s own "fail" verdict -- mirrors
        # rebind_html.py's main() doing its own _guard_path() pass ahead of the pure engine call.
        _guard_path(args.html, must_exist=True)
        _guard_path(args.out, must_exist=False)
    except EmitPdfError as exc:
        _emit_error(str(exc))
        return 2

    receipt = emit_pdf(args.html, args.out, base_url=args.base_url, pdf_variant=args.pdf_variant)
    print(json.dumps(receipt, indent=2 if args.pretty else None))
    return 1 if receipt["verdict"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
