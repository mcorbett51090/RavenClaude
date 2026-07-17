#!/usr/bin/env python3
"""
render_referee.py — STANDALONE, OPTIONAL-DEPENDENCY V5 render-referee for
report-regeneration (enhanced-fidelity module).

This is NOT wired into harness.py (harness.py is not edited by this module — see
core-architecture-spec.md §5's V5 row and harness.py's own `leg_v5()`/`_renderer_available()`,
which this file deliberately MIRRORS rather than imports, so it stays a genuinely standalone,
optional-dependency unit a future orchestrator step can wire in). Where harness.py's stdlib-only
`leg_v5()` can only ever report `pass` (trivially, "a renderer is importable") or `not_captured`,
this module does the REAL work when Playwright is importable: launches headless chromium, navigates
to the HTML file under test, collects console errors + uncaught page exceptions, runs a non-ML
in-page layout heuristic (invisible-but-non-empty text nodes; pairwise bounding-rect overlap among
visible leaf text nodes), and captures a screenshot. Absent Playwright, it degrades to
`not_captured` — NEVER a fake pass (the same W5 discipline harness.py's own docstring states
verbatim: "PROBE_ERROR != pass"; a render/parse crash never reads as "fidelity OK").

Two public entry points:

    render_referee(html_path, ...) -> dict
        Render ONE HTML file and return a fidelity-receipt `legReceipt`-shaped verdict
        (../../knowledge/fidelity-receipt.schema.json `$defs.legReceipt`) for leg "V5":
        {leg, verdict, label, inference_independent, blocking, repeat_count, judge_fingerprint,
        evidence} plus a `diagnostics` key. NOTE: `diagnostics` is NOT part of the schema's
        `legReceipt` (`additionalProperties: false`) — a future wiring step that lifts this dict
        verbatim into a `fidelity-receipt`'s `legs[]` array MUST pop `diagnostics` first. It is
        kept here, outside the strict fields, because this module is read standalone (CLI/tests)
        and the extra detail (screenshot path, the actual console errors, the actual layout
        issues) is exactly what a human debugging a V5 `fail` needs.

    render_diff(template_html, output_html, ...) -> dict
        A frozen-region VISUAL sanity check: render both HTML documents (content strings, mirroring
        harness.py's own `template_text`/`output_text` naming), optionally scoped to specific CSS
        selectors (e.g. the manifest's `frozen` anchors), and compare screenshots. With Pillow
        importable (present in the same optional venv as Playwright in this plugin's Phase-0
        environment) this is a genuine tolerant per-pixel diff; with Pillow absent but Playwright
        present it degrades to an exact-byte compare (still real, just blunter — documented in the
        result's `mode` field). With Playwright absent: `not_captured`.

Both functions NEVER raise for an absent/broken optional dependency — that is always a clean
`not_captured` verdict (mirrors harness.py's `leg_v5()` contract exactly). A genuine crash MID-run
(Playwright present but the browser/page interaction itself throws) is reported as `PROBE_ERROR`,
distinct from a clean absence — same PROBE_ERROR-vs-not_captured distinction the fidelity-receipt
schema itself draws.

Capability detection: `importlib.util.find_spec("playwright")` is the cheap first gate (mirrors
harness.py's `_renderer_available()`); this module additionally performs a REAL `import
playwright.sync_api` before use, because `find_spec` only proves the package is on disk, not that
it actually imports cleanly in this interpreter (see `emit_pdf.py`'s sibling `weasyprint_capability()`
for the same two-tier pattern, needed there because WeasyPrint's native cffi bindings can be present
on disk yet fail to `dlopen()` a missing system library).

Usage (CLI):
    python3 render_referee.py referee --html report.html [--screenshot out.png] [--repeat 1]
    python3 render_referee.py diff --template t.html --output o.html \
        [--frozen-selector "#logo-header" --frozen-selector "#sec-appendix"] [--tolerance 0.02]

Exit: this is a probe for a NON-BLOCKING leg (fidelity-receipt.schema.json: V5's `blocking` is
always `false`), not a gate — mirrors scripts/powerbi_probe.py's "Exit: always 0" convention EXCEPT
that a `fail` verdict (a REAL captured defect, not an absence) exits 1 so a caller can branch on
it without re-parsing JSON; `not_captured`/`PROBE_ERROR`/`pass` all exit 0. Usage/path-guard errors
exit 2.

Constraints (binding, matches every other script in this plugin): Python 3.9.6-safe
(`from __future__ import annotations`; `X | Y` / `dict[str, T]` appear only in annotation position,
which the future-import defers to a string — never evaluated at runtime, so this is safe on 3.9,
exactly as harness.py/rebind_html.py already do throughout). Optional-import guarded: importing
this module under stdlib python3 (no Playwright) never raises. No network — Playwright only ever
navigates to a local `file://` URI this script itself wrote/read; no subprocess is spawned directly
by this module's own code (Playwright manages its own browser subprocess internally, inherent to
using it at all). Read-only + path-guarded against the two file inputs (`--html` / `--template` /
`--output`); the only writes are the screenshot PNG(s) this module is explicitly asked to produce
and its own scratch temp files (always cleaned up).
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import sys
import tempfile
from pathlib import Path

INSTALL_NOTE = (
    "Playwright is not usable in this interpreter. Install path: "
    "`pip install playwright && python3 -m playwright install chromium` "
    "(add `--with-deps` on Linux for the OS-level codec/font libraries chromium needs)."
)

# Non-ML in-page layout heuristic: (a) a leaf text node with non-whitespace content that is NOT
# intentionally hidden (display:none / visibility:hidden / opacity:0) but renders at zero size is
# "invisible-content" (a likely CSS/layout bug); (b) two such visible leaf text nodes (neither an
# ancestor of the other) whose bounding rects overlap more than 50% of the smaller one's area is
# "overlap" (a likely layout collision). Capped at 300 candidate leaf nodes for O(n^2) safety on a
# large report. Deliberately scoped ("basic layout-overlap/visibility") — this is a heuristic, not
# a CSS layout engine re-implementation, and it says so in every evidence string it emits.
_MAX_LAYOUT_CANDIDATES = 300
_LAYOUT_CHECK_JS = """
(maxCandidates) => {
  function describe(el) {
    if (el.id) return el.tagName.toLowerCase() + '#' + el.id;
    const cls = (el.className && typeof el.className === 'string')
      ? '.' + el.className.trim().split(/\\s+/).filter(Boolean).join('.') : '';
    return el.tagName.toLowerCase() + cls;
  }
  const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'HEAD', 'TITLE', 'META', 'LINK', 'NOSCRIPT']);
  const candidates = Array.from(document.querySelectorAll('body *')).filter((el) => {
    if (SKIP_TAGS.has(el.tagName)) return false;
    if (el.children.length !== 0) return false;
    const text = (el.textContent || '').trim();
    return text.length > 0;
  }).slice(0, maxCandidates);

  const issues = [];
  const visible = [];
  for (const el of candidates) {
    const style = getComputedStyle(el);
    const hidden = style.display === 'none' || style.visibility === 'hidden'
      || parseFloat(style.opacity || '1') === 0;
    if (hidden) continue;
    const rect = el.getBoundingClientRect();
    const text = (el.textContent || '').trim().slice(0, 80);
    if (rect.width === 0 || rect.height === 0) {
      issues.push({type: 'invisible-content', selector: describe(el), text: text});
      continue;
    }
    visible.push({el: el, rect: rect, selector: describe(el)});
  }
  for (let i = 0; i < visible.length; i++) {
    for (let j = i + 1; j < visible.length; j++) {
      const a = visible[i], b = visible[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const overlapX = Math.max(0, Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left));
      const overlapY = Math.max(0, Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top));
      const overlapArea = overlapX * overlapY;
      const minArea = Math.min(a.rect.width * a.rect.height, b.rect.width * b.rect.height);
      if (minArea > 0 && (overlapArea / minArea) > 0.5) {
        issues.push({type: 'overlap', a: a.selector, b: b.selector});
      }
    }
  }
  return issues;
}
"""


class RenderRefereeError(Exception):
    """Raised for path-guard / usage failures (surfaced as CLI exit 2). NEVER raised for an
    absent/broken optional dependency — that is always a `not_captured` verdict, never an
    exception (mirrors harness.py's HarnessError / rebind_html.py's RebindError convention:
    this exception means "abort", not "degrade")."""


# ─────────────────────────────────────────────────────────────────────────────
# Path guard — mirrors harness.py's safe_read_path() exactly (this module lives in the same
# skill dir and inherits the same "read-only verifier" contract), reimplemented standalone so
# this file has zero import-time coupling to harness.py.
# ─────────────────────────────────────────────────────────────────────────────

def safe_read_path(raw: str) -> Path:
    if not raw or "\x00" in raw:
        raise RenderRefereeError("empty or NUL-bearing path")
    try:
        resolved = Path(raw).resolve()
    except (OSError, RuntimeError) as exc:
        raise RenderRefereeError(f"cannot resolve path {raw!r}: {exc}") from exc
    if not resolved.exists():
        raise RenderRefereeError(f"input file not found: {raw!r} (resolved {resolved})")
    if not resolved.is_file():
        raise RenderRefereeError(f"not a regular file: {raw!r} (resolved {resolved})")
    return resolved


# ─────────────────────────────────────────────────────────────────────────────
# Capability detection — two-tier: cheap find_spec() gate, then a REAL import attempt (never
# trust find_spec alone for the "usable" claim; see module docstring).
# ─────────────────────────────────────────────────────────────────────────────

def playwright_capability() -> dict:
    """Never raises. Returns {"available": bool, "present_on_disk": bool, "reason": str|None,
    "note": str|None}. `available=False` covers BOTH "not installed" and "installed but failed
    to import in this interpreter" — the caller does not need to care which."""
    present_on_disk = False
    try:
        present_on_disk = importlib.util.find_spec("playwright") is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        present_on_disk = False
    if not present_on_disk:
        return {
            "available": False, "present_on_disk": False,
            "reason": "playwright is not installed in this interpreter", "note": INSTALL_NOTE,
        }
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except Exception as exc:  # pragma: no cover - exercised only when the wheel is broken
        return {
            "available": False, "present_on_disk": True,
            "reason": f"{type(exc).__name__}: {exc}", "note": INSTALL_NOTE,
        }
    return {"available": True, "present_on_disk": True, "reason": None, "note": None}


def _capability_reason(cap: dict) -> str:
    if cap["reason"]:
        return f"{cap['reason']} — {cap['note']}"
    return cap["note"] or "playwright unavailable"


def _not_captured(reason: str) -> dict:
    return {
        "leg": "V5", "verdict": "not_captured", "label": "judged",
        "inference_independent": False, "blocking": False,
        "evidence": reason,
    }


def _probe_error(reason: str) -> dict:
    return {
        "leg": "V5", "verdict": "PROBE_ERROR", "label": "judged",
        "inference_independent": False, "blocking": False,
        "evidence": reason,
    }


# ─────────────────────────────────────────────────────────────────────────────
# render_referee() — the real V5 leg
# ─────────────────────────────────────────────────────────────────────────────

def _render_once(browser, html_path: Path, screenshot_path: str | None, timeout_ms: int) -> dict:
    console_errors: list = []
    page_errors: list = []
    page = browser.new_page()
    tmp_shot: str | None = None
    try:
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(html_path.as_uri(), timeout=timeout_ms, wait_until="load")
        page.wait_for_timeout(150)  # let any deferred console/pageerror events flush
        layout_issues = page.evaluate(_LAYOUT_CHECK_JS, _MAX_LAYOUT_CANDIDATES)
        if screenshot_path:
            page.screenshot(path=screenshot_path, full_page=True)
            shot = screenshot_path
        else:
            fd, tmp_shot = tempfile.mkstemp(suffix=".png", prefix="render-referee-")
            os.close(fd)
            page.screenshot(path=tmp_shot, full_page=True)
            shot = tmp_shot
    finally:
        page.close()
    return {
        "console_errors": console_errors + [f"uncaught exception: {e}" for e in page_errors],
        "layout_issues": layout_issues,
        "screenshot_path": shot,
    }


def render_referee(html_path: str, *, screenshot_path: str | None = None, repeat: int = 1,
                   timeout_ms: int = 15000) -> dict:
    """Render `html_path` (a real file on disk) with headless chromium `repeat` time(s) and
    return a leg="V5" `legReceipt`-shaped dict (see module docstring for the `diagnostics` caveat).
    NEVER raises: absent/broken Playwright -> `not_captured`; a genuine crash mid-capture ->
    `PROBE_ERROR`; a bad `html_path` -> `not_captured` (the input never got a real render, so it
    is honestly "not captured", not a harness-crash PROBE_ERROR)."""
    cap = playwright_capability()
    if not cap["available"]:
        receipt = _not_captured(_capability_reason(cap))
        receipt["diagnostics"] = {"capability": cap}
        return receipt

    try:
        resolved = safe_read_path(html_path)
    except RenderRefereeError as exc:
        receipt = _not_captured(f"input error (never a fake pass): {exc}")
        receipt["diagnostics"] = {"capability": cap}
        return receipt

    repeat_n = max(1, int(repeat))
    runs: list = []
    browser_version = None
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                browser_version = browser.version
                for i in range(repeat_n):
                    per_run_shot = None
                    if screenshot_path:
                        per_run_shot = screenshot_path if repeat_n == 1 else f"{screenshot_path}.run{i + 1}.png"
                    runs.append(_render_once(browser, resolved, per_run_shot, timeout_ms))
            finally:
                browser.close()
    except Exception as exc:  # a genuine crash mid-capture -- PROBE_ERROR, never a fake pass
        receipt = _probe_error(
            f"render referee crashed during a real Playwright/chromium capture of "
            f"{resolved.name}: {type(exc).__name__}: {exc}"
        )
        receipt["diagnostics"] = {"capability": cap}
        return receipt

    all_console_errors: list = []
    all_layout_issues: list = []
    last_shot = None
    for run in runs:
        all_console_errors.extend(run["console_errors"])
        all_layout_issues.extend(run["layout_issues"])
        if run["screenshot_path"]:
            last_shot = run["screenshot_path"]

    dirty = bool(all_console_errors) or bool(all_layout_issues)
    verdict = "fail" if dirty else "pass"
    evidence = (
        f"{len(runs)} real Playwright/chromium run(s) of {resolved.name}: "
        f"{len(all_console_errors)} console error(s)/uncaught exception(s), "
        f"{len(all_layout_issues)} layout issue(s) (non-ML overlap/invisible-content heuristic, "
        f"leaf text nodes only)"
    )

    return {
        "leg": "V5",
        "verdict": verdict,
        "label": "judged",
        "inference_independent": False,
        "blocking": False,
        "repeat_count": len(runs),
        "judge_fingerprint": f"render-referee/playwright-chromium@{browser_version}",
        "evidence": evidence,
        # Informational, NOT part of the strict fidelity-receipt legReceipt
        # (additionalProperties: false) -- pop this key before inserting into legs[].
        "diagnostics": {
            "capability": cap,
            "screenshot_path": last_shot,
            "console_errors": all_console_errors,
            "layout_issues": all_layout_issues,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# render_diff() — frozen-region visual sanity check
# ─────────────────────────────────────────────────────────────────────────────

def _capture_regions(browser, html_text: str, selectors: list | None,
                     timeout_ms: int) -> tuple:
    fd, tmp_path = tempfile.mkstemp(suffix=".html", prefix="render-diff-")
    os.close(fd)
    path = Path(tmp_path)
    try:
        path.write_text(html_text, encoding="utf-8")
        page = browser.new_page()
        try:
            page.goto(path.as_uri(), timeout=timeout_ms, wait_until="load")
            shots: dict = {}
            missing: list = []
            if selectors:
                for sel in selectors:
                    el = page.query_selector(sel)
                    if el is None:
                        missing.append(sel)
                        continue
                    shots[sel] = el.screenshot()
            else:
                shots["__full_page__"] = page.screenshot(full_page=True)
            return shots, missing
        finally:
            page.close()
    finally:
        try:
            path.unlink(missing_ok=True)
        except OSError:  # pragma: no cover - best-effort scratch cleanup
            pass


def _pixel_diff_ratio(a_bytes: bytes, b_bytes: bytes, *, channel_threshold: int = 12):
    """Pillow-backed tolerant pixel diff: fraction of pixels whose grayscale absolute difference
    exceeds `channel_threshold` (0-255). Returns None if the two images differ in dimensions
    (not comparable — the caller reports that as its own mismatch, distinct from a real diff
    ratio). Import is local/lazy: only reached when PIL is confirmed importable by the caller."""
    from PIL import Image, ImageChops
    a = Image.open(io.BytesIO(a_bytes)).convert("RGB")
    b = Image.open(io.BytesIO(b_bytes)).convert("RGB")
    if a.size != b.size:
        return None
    diff = ImageChops.difference(a, b).convert("L")
    hist = diff.histogram()
    total_pixels = a.size[0] * a.size[1]
    if total_pixels == 0:
        return 0.0
    differing = sum(hist[channel_threshold + 1:])
    return differing / total_pixels


def render_diff(template_html: str, output_html: str, *, frozen_selectors=None,
                pixel_tolerance: float = 0.02, timeout_ms: int = 15000) -> dict:
    """Render `template_html` and `output_html` (HTML CONTENT strings, mirroring harness.py's own
    `template_text`/`output_text` convention — not file paths) with headless chromium and compare
    screenshots. With `frozen_selectors` given, each selector's element is crop-compared
    independently (the intended use: pass the manifest's `frozen`-class anchors so a caller can
    sanity-check that the regions the fidelity harness's V2 already proved byte-identical ALSO
    render visually identical — a genuinely different failure mode than V2's AST diff, e.g. a CSS
    regression that changes layout without changing any DOM byte). Without `frozen_selectors`,
    compares the full page. NEVER raises: absent/broken Playwright -> `not_captured`; a genuine
    crash mid-capture -> `PROBE_ERROR`."""
    cap = playwright_capability()
    if not cap["available"]:
        return {
            "check": "render-diff", "verdict": "not_captured", "mode": None,
            "regions_checked": 0, "pixel_tolerance": pixel_tolerance, "mismatches": [],
            "evidence": _capability_reason(cap),
        }

    selectors = list(frozen_selectors) if frozen_selectors else None
    try:
        pil_available = importlib.util.find_spec("PIL") is not None
    except (ImportError, ValueError, ModuleNotFoundError):  # pragma: no cover - defensive
        pil_available = False

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                tmpl_shots, tmpl_missing = _capture_regions(browser, template_html, selectors, timeout_ms)
                out_shots, out_missing = _capture_regions(browser, output_html, selectors, timeout_ms)
            finally:
                browser.close()
    except Exception as exc:
        return {
            "check": "render-diff", "verdict": "PROBE_ERROR", "mode": None,
            "regions_checked": 0, "pixel_tolerance": pixel_tolerance, "mismatches": [],
            "evidence": f"render_diff crashed during a real Playwright/chromium capture: "
                        f"{type(exc).__name__}: {exc}",
        }

    mismatches: list = []
    for label in tmpl_missing:
        mismatches.append(f"{label!r}: selector never resolved against the TEMPLATE render")
    for label in out_missing:
        mismatches.append(f"{label!r}: selector never resolved against the OUTPUT render")

    checked = 0
    for label, t_bytes in tmpl_shots.items():
        if label not in out_shots:
            continue  # already reported via out_missing above
        checked += 1
        o_bytes = out_shots[label]
        if t_bytes == o_bytes:
            continue
        if pil_available:
            ratio = _pixel_diff_ratio(t_bytes, o_bytes)
            if ratio is None:
                mismatches.append(f"{label!r}: template/output render dimensions differ")
            elif ratio > pixel_tolerance:
                mismatches.append(
                    f"{label!r}: {ratio:.2%} of pixels differ (tolerance {pixel_tolerance:.2%})"
                )
        else:
            mismatches.append(
                f"{label!r}: screenshot bytes differ (coarse mode -- Pillow unavailable for a "
                f"tolerant pixel diff in this interpreter; any byte difference is reported)"
            )

    verdict = "fail" if mismatches else "pass"
    region_desc = ("selector-scoped: " + ", ".join(selectors)) if selectors else "full page"
    return {
        "check": "render-diff",
        "verdict": verdict,
        "mode": "pixel-tolerant" if pil_available else "coarse-byte-exact",
        "regions_checked": checked,
        "pixel_tolerance": pixel_tolerance,
        "mismatches": mismatches,
        "evidence": f"{checked} region(s) compared ({region_desc}); {len(mismatches)} mismatch(es)",
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="render_referee.py",
        description="Standalone, optional-dependency V5 render-referee (Playwright/chromium) for "
                    "report-regeneration.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_referee = sub.add_parser("referee", help="Render one HTML file, return a V5 leg-shaped receipt.")
    p_referee.add_argument("--html", required=True, metavar="PATH", help="HTML file to render")
    p_referee.add_argument("--screenshot", default=None, metavar="PATH", help="where to write the screenshot PNG")
    p_referee.add_argument("--repeat", type=int, default=1, help="N repeated renders (W5 N-agreement)")
    p_referee.add_argument("--timeout-ms", type=int, default=15000, dest="timeout_ms")
    p_referee.add_argument("--pretty", action="store_true")

    p_diff = sub.add_parser("diff", help="Frozen-region visual sanity check between two HTML files.")
    p_diff.add_argument("--template", required=True, metavar="PATH")
    p_diff.add_argument("--output", required=True, metavar="PATH")
    p_diff.add_argument("--frozen-selector", dest="frozen_selectors", action="append", default=[],
                        metavar="SELECTOR", help="repeatable; omit for a full-page compare")
    p_diff.add_argument("--tolerance", type=float, default=0.02)
    p_diff.add_argument("--timeout-ms", type=int, default=15000, dest="timeout_ms")
    p_diff.add_argument("--pretty", action="store_true")

    return p


def _emit_error(message: str) -> None:
    print(json.dumps({"ok": False, "error": message}))
    print(f"[error] {message}", file=sys.stderr)


def main(argv: list) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "referee":
        try:
            safe_read_path(args.html)
        except RenderRefereeError as exc:
            _emit_error(str(exc))
            return 2
        receipt = render_referee(
            args.html, screenshot_path=args.screenshot, repeat=args.repeat, timeout_ms=args.timeout_ms
        )
        print(json.dumps(receipt, indent=2 if args.pretty else None))
        # V5 is a NON-BLOCKING leg by schema (blocking: false) -- this CLI is a probe, not a
        # gate (mirrors scripts/powerbi_probe.py's "always 0" convention), except a REAL captured
        # `fail` (not an absence) exits 1 so a caller can branch without re-parsing JSON.
        return 1 if receipt["verdict"] == "fail" else 0

    try:
        template_path = safe_read_path(args.template)
        output_path = safe_read_path(args.output)
    except RenderRefereeError as exc:
        _emit_error(str(exc))
        return 2
    template_html = template_path.read_text(encoding="utf-8")
    output_html = output_path.read_text(encoding="utf-8")
    result = render_diff(
        template_html, output_html,
        frozen_selectors=args.frozen_selectors or None,
        pixel_tolerance=args.tolerance, timeout_ms=args.timeout_ms,
    )
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 1 if result["verdict"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
