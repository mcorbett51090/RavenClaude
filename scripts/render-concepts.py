#!/usr/bin/env python3
"""render-concepts.py — pre-render concept Mermaid diagrams to themed static SVG.

Each Learn-tab concept (see concepts.py) carries its diagram as Mermaid *source*.
This script renders that source to a static, inlinable SVG at build time with
mermaid-cli, then NORMALIZES it to the dashboard's dark-teal token system so the
committed SVGs look designed (not raw-Mermaid) and theme-react in light mode.

Why build-time render (not a runtime Mermaid lib): the dashboard is offline-first
and byte-deterministic. Inlining the 3.3MB mermaid.min.js would 8x dashboard.html
and a tooltip can't run a live render pass. Pre-rendered SVG sidesteps both.

CI never needs Chromium: rendering writes a source-hash manifest, and `--check`
re-derives the hashes from the concept sources and diffs them against the
committed SVGs — so a diagram edited without a re-render is caught in CI without
launching a browser. Only whoever edits a diagram needs mermaid-cli locally.

Usage:
    render-concepts.py [--root DIR]          # render every concept's SVG(s)
    render-concepts.py --check [--root DIR]  # verify committed SVGs match source
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concepts as concepts_mod  # noqa: E402

# Pin the renderer so committed SVGs stay reproducible across machines/time.
MMDC_VERSION = "11.15.0"
# Bump when the normalizer logic below changes (invalidates every committed SVG).
NORMALIZER_VERSION = 4

VISUALS_DIR = "plugins/ravenclaude-core/knowledge/concepts/visuals"
MANIFEST_NAME = ".render-manifest.json"

_PUPPETEER_CFG = '{"args":["--no-sandbox","--disable-setuid-sandbox"]}'
_BG_WHITE_RE = re.compile(r"background-color:\s*white;?", re.IGNORECASE)

# ── Chrome resolution ────────────────────────────────────────────────────────
# mermaid-cli drives puppeteer-core, which resolves its own browser out of the
# Puppeteer cache. That resolution CAN FAIL even when the browser is correctly
# installed: observed 2026-07-28 on macOS/arm64 with Chrome 148.0.7778.97 present
# and complete (353 MB), mermaid-cli still died with
#   Error: Could not find Chrome (ver. 148.0.7778.97).
# Passing PUPPETEER_EXECUTABLE_PATH explicitly is puppeteer's documented escape
# hatch, and it is what actually renders. We therefore discover a cache-managed
# browser ourselves and hand it over.
#
# DELIBERATELY puppeteer-cache-only — no `shutil.which("google-chrome")` fallback.
# A system Chrome is an arbitrary version, and this renderer's whole contract is
# byte-reproducible committed SVGs (text metrics move with the browser). Better to
# fail loudly with an install hint than to silently render against a different
# engine and churn every committed SVG.
_CHROME_RELATIVE_CANDIDATES = {
    "darwin": (
        "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        "chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        "chrome-headless-shell-mac-arm64/chrome-headless-shell",
        "chrome-headless-shell-mac-x64/chrome-headless-shell",
    ),
    "linux": (
        "chrome-linux64/chrome",
        "chrome-headless-shell-linux64/chrome-headless-shell",
    ),
    "win32": (
        "chrome-win64/chrome.exe",
        "chrome-headless-shell-win64/chrome-headless-shell.exe",
    ),
}


def _puppeteer_cache_root() -> Path:
    """Where puppeteer keeps managed browsers (honors its own env override)."""
    override = os.environ.get("PUPPETEER_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".cache" / "puppeteer"


def _looks_complete(exe: Path) -> bool:
    """Reject a TRUNCATED browser download that still carries an executable stub.

    Observed 2026-07-28: a 448 KB Chrome 148 cache entry kept a plausible 68 KB
    launcher at `Contents/MacOS/Google Chrome for Testing` but was missing
    `Contents/Frameworks` entirely — so `is_file()` and `os.access(X_OK)` BOTH passed
    while every launch died with "Could not find Chrome". A complete macOS bundle is
    ~350 MB with its payload under Contents/Frameworks; on other platforms (and for
    chrome-headless-shell) the executable IS the payload, so a sub-megabyte file is
    the same tell. This is what stops us handing puppeteer a path we know is broken.
    """
    if exe.parent.name == "MacOS" and exe.parent.parent.name == "Contents":
        return (exe.parent.parent / "Frameworks").is_dir()
    try:
        return exe.stat().st_size > 1_000_000
    except OSError:
        return False


@functools.lru_cache(maxsize=1)
def _discover_chrome() -> str | None:
    """Return a Puppeteer-managed Chrome executable path, or None if none is usable.

    Version directories are walked NEWEST-FIRST and the choice is deterministic for a
    given cache, so repeat runs on one machine pick the same engine and the committed
    SVG bytes stay stable. Installing a newer Chrome CAN therefore change the chosen
    engine — which is why the caller logs the pick.
    """
    plat = "linux"
    if sys.platform.startswith("darwin"):
        plat = "darwin"
    elif sys.platform.startswith("win"):
        plat = "win32"
    relatives = _CHROME_RELATIVE_CANDIDATES[plat]

    root = _puppeteer_cache_root()
    for product in ("chrome", "chrome-headless-shell"):
        product_dir = root / product
        if not product_dir.is_dir():
            continue
        # Newest-first by directory name (e.g. mac_arm-151.0… before mac_arm-148.0…).
        for version_dir in sorted(product_dir.iterdir(), key=lambda p: p.name, reverse=True):
            if not version_dir.is_dir():
                continue
            for rel in relatives:
                exe = version_dir / rel
                if exe.is_file() and os.access(exe, os.X_OK) and _looks_complete(exe):
                    return str(exe)
    return None


# Set once, the first time puppeteer's own resolution is proven broken this run, so
# the remaining diagrams don't each pay a doomed first attempt.
_FALLBACK_EXE: str | None = None


def _render_env(exe: str | None) -> dict | None:
    """None ⇒ inherit os.environ untouched (puppeteer resolves the browser itself)."""
    if exe is None:
        return None
    env = os.environ.copy()
    env["PUPPETEER_EXECUTABLE_PATH"] = exe
    return env


def _chrome_hint() -> str:
    """An actionable hint for the two failure modes seen in the wild."""
    root = _puppeteer_cache_root()
    found = _discover_chrome()
    if found:
        return (
            f"\n\nHINT: handed puppeteer PUPPETEER_EXECUTABLE_PATH={found!r} and it still failed. "
            "If that directory is small (a complete Chrome is ~350 MB), it is a TRUNCATED download: "
            "`puppeteer browsers install` SILENTLY NO-OPS when the version directory already exists, "
            "so move it aside and reinstall:\n"
            "    mv <that version dir> /tmp/chrome-broken\n"
            "    npx --yes puppeteer browsers install chrome"
        )
    return (
        f"\n\nHINT: no Puppeteer-managed Chrome found under {root}. Install one:\n"
        "    npx --yes puppeteer browsers install chrome\n"
        "(mermaid-cli needs full **chrome**; chrome-headless-shell alone is not enough.)"
    )


def _theme_style(svg_id: str) -> str:
    """An override <style> that remaps raw-Mermaid colors onto dashboard tokens.
    `!important` + the id prefix beat Mermaid's own injected per-id rules. Uses
    CSS vars so the dashboard's prefers-color-scheme:light block flips the SVG."""
    s = f"#{svg_id}"
    return (
        "<style>"
        f"{s} .nodeLabel,{s} .edgeLabel,{s} text,{s} span,{s} p,{s} div"
        # theme the text COLOR only — never the font-family: Mermaid baked node
        # widths using its own font at render time, so forcing a wider font here
        # would overflow the shapes (clipped labels).
        "{fill:var(--text)!important;color:var(--text)!important;background:transparent!important}"
        f"{s} .node rect,{s} .node polygon,{s} .node circle,{s} .node path,{s} .label-container"
        "{fill:var(--surface-2)!important;stroke:var(--border)!important;stroke-width:1.5px!important}"
        f"{s} .cluster rect{{fill:var(--surface)!important;stroke:var(--border)!important}}"
        f"{s} .edgePath .path,{s} .edgePath path,{s} path.flowchart-link,{s} .flowchart-link"
        "{stroke:var(--muted)!important;stroke-width:1.5px!important;fill:none!important}"
        f"{s} marker path,{s} .arrowMarkerPath,{s} #arrowhead path"
        "{fill:var(--muted)!important;stroke:none!important}"
        f"{s} .edgeLabel rect,{s} .edgeLabel .labelBkg,{s} .label-container.edgeLabel"
        "{fill:var(--bg)!important;opacity:1!important}"
        f"{s} .edgeLabel text,{s} .edgeLabel span{{fill:var(--muted)!important;color:var(--muted)!important}}"
        # fact-vs-built coloring, driven by `class X,Y fact|built` in the Mermaid source
        f"{s} .node.fact rect,{s} .node.fact polygon,{s} .node.fact path,{s} .node.fact circle"
        "{stroke:var(--muted)!important}"
        f"{s} .node.built rect,{s} .node.built polygon,{s} .node.built path,{s} .node.built circle"
        "{fill:var(--surface)!important;stroke:var(--accent)!important}"
        # hover/focus highlight — the :hover pseudo-class out-specifies the base
        # node rule above, so the inlined diagram feels live without extra JS
        f"{s} .node:hover rect,{s} .node:hover polygon,{s} .node:hover circle,{s} .node:hover path"
        "{stroke:var(--accent)!important;stroke-width:2.5px!important;cursor:default}"
        "</style>"
    )


def _normalize(svg: str, svg_id: str) -> str:
    """Rewrite the raw mmdc SVG: unique id prefix, transparent bg, theme override.
    Pure string ops → deterministic."""
    # mmdc emits id="my-svg" and prefixes every internal id/url-ref with it; a
    # global rename makes the SVG safe to inline alongside others on one page.
    svg = svg.replace("my-svg", svg_id)
    svg = _BG_WHITE_RE.sub("", svg)
    # tag the root (merge into Mermaid's existing class — never add a 2nd attr)
    m = re.match(r"<svg\b([^>]*)>", svg)
    if not m:
        # mermaid-cli can emit a leading <?xml?>/comment before <svg>; if the root
        # isn't at offset 0 there's nothing to retag — return unchanged (mirrors
        # render-trees.py's guard).
        return svg
    attrs = m.group(1)
    if 'class="' in attrs:
        attrs = attrs.replace('class="', 'class="rc-concept-diagram ', 1)
    else:
        attrs = ' class="rc-concept-diagram"' + attrs
    return f"<svg{attrs}>" + _theme_style(svg_id) + svg[m.end():]


def _source_hash(concept: dict) -> str:
    h = hashlib.sha256()
    payload = {
        "diagram": concept["diagram"],
        "diagram_mini": concept["diagram_mini"],
        "mmdc": MMDC_VERSION,
        "normalizer": NORMALIZER_VERSION,
    }
    # Add steps to the hash ONLY when a concept has them, so the 18 step-less
    # concepts keep byte-identical hashes (their committed SVGs stay valid; no
    # NORMALIZER_VERSION bump needed).
    if concept.get("steps"):
        payload["steps"] = [s["diagram"] for s in concept["steps"]]
    h.update(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()


def _render_one(mermaid_src: str, svg_id: str, tmp: Path) -> str:
    """Render one Mermaid string to a normalized SVG via mermaid-cli."""
    in_path = tmp / "in.mmd"
    out_path = tmp / "out.svg"
    cfg_path = tmp / "pp.json"
    in_path.write_text(mermaid_src + "\n", encoding="utf-8")
    cfg_path.write_text(_PUPPETEER_CFG, encoding="utf-8")
    cmd = [
        "npx", "--yes", f"@mermaid-js/mermaid-cli@{MMDC_VERSION}",
        "-i", str(in_path), "-o", str(out_path),
        "-p", str(cfg_path), "-b", "transparent",
    ]
    global _FALLBACK_EXE

    def _run(exe: str | None):
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=180, env=_render_env(exe)
        )

    # ATTEMPT 1 — puppeteer's OWN resolution: byte-for-byte the historical path.
    # Deliberately tried first, and skipped only once a fallback has already proven
    # necessary this run. Rationale: committed SVGs are byte-compared, and text
    # metrics move with the browser build — so on any host where resolution already
    # works we must NOT substitute a different Chrome and silently churn every SVG.
    # The fallback is a repair for hosts that would otherwise render nothing at all.
    if _FALLBACK_EXE is None:
        proc = _run(None)
        if proc.returncode == 0 and out_path.exists():
            return _normalize(out_path.read_text(encoding="utf-8"), svg_id)
        # Resolution failed. An operator-set path already lost, so don't second-guess it.
        if os.environ.get("PUPPETEER_EXECUTABLE_PATH"):
            raise RuntimeError(
                f"mermaid-cli failed for {svg_id} with an explicit "
                f"PUPPETEER_EXECUTABLE_PATH:\n{proc.stderr.strip()[-800:]}{_chrome_hint()}"
            )
        found = _discover_chrome()
        if not found:
            raise RuntimeError(
                f"mermaid-cli failed for {svg_id}:\n{proc.stderr.strip()[-800:]}{_chrome_hint()}"
            )
        _FALLBACK_EXE = found
        print(
            "[render-concepts] puppeteer could not resolve its own browser; falling back to "
            f"PUPPETEER_EXECUTABLE_PATH={found}",
            file=sys.stderr,
        )

    # ATTEMPT 2 — explicit executable (also the direct path for every later diagram).
    proc = _run(_FALLBACK_EXE)
    if proc.returncode != 0 or not out_path.exists():
        raise RuntimeError(
            f"mermaid-cli failed for {svg_id}:\n{proc.stderr.strip()[-800:]}{_chrome_hint()}"
        )
    return _normalize(out_path.read_text(encoding="utf-8"), svg_id)


def _check(root: Path, concepts: list[dict]) -> int:
    vis = root / VISUALS_DIR
    manifest_path = vis / MANIFEST_NAME
    if not manifest_path.exists():
        print(f"render manifest missing ({VISUALS_DIR}/{MANIFEST_NAME}) — run: scripts/render-concepts.py")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    recorded = manifest.get("concepts", {})
    problems: list[str] = []
    diagramless = 0
    for c in concepts:
        cid = c["id"]
        # ⛔ DIAGRAMS ARE OPT-IN FOR INVENTORY ENTRIES (R2 corollary, plan P6.2).
        # concepts.py stopped requiring a ```mermaid block on entry_class:
        # inventory; this loop is the OTHER HALF of that change and was missing.
        # Without it, 12 diagram-less entries each reported "diagram source changed
        # since last render" and the only way to clear the gate would have been to
        # render 12 diagrams nobody asked for — one npx + Chromium process each,
        # with an all-or-nothing revert that continues green on failure. That is
        # the single most dangerous line in either panel plan, arriving through the
        # back door of a freshness check.
        if not c.get("diagram"):
            diagramless += 1
            continue
        want = _source_hash(c)
        if recorded.get(cid) != want:
            problems.append(f"  ✗ {cid}: diagram source changed since last render — re-run scripts/render-concepts.py")
            continue
        if not (vis / f"{cid}.svg").exists():
            problems.append(f"  ✗ {cid}: {cid}.svg missing")
        if c["diagram_mini"] and not (vis / f"{cid}.mini.svg").exists():
            problems.append(f"  ✗ {cid}: {cid}.mini.svg missing")
        for idx in range(1, len(c.get("steps", [])) + 1):
            if not (vis / f"{cid}.step-{idx}.svg").exists():
                problems.append(f"  ✗ {cid}: {cid}.step-{idx}.svg missing")
    # An orphan is a manifest entry for a concept that no longer has a diagram OR
    # no longer exists. Both need a re-render to clean up.
    stale = set(recorded) - {c["id"] for c in concepts if c.get("diagram")}
    for cid in sorted(stale):
        problems.append(f"  ✗ {cid}: orphaned in manifest (concept removed) — re-run scripts/render-concepts.py")
    if problems:
        print("Concept SVG freshness gate FAILED:")
        print("\n".join(problems))
        return 1
    print(
        f"Concept SVGs OK — {len(concepts) - diagramless} concept(s) match their "
        f"diagram source; {diagramless} carry no diagram (opt-in, and a skip is "
        "reported rather than counted as a pass)."
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--check", action="store_true", help="verify committed SVGs match source (no render)")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    try:
        concepts = concepts_mod.load_concepts(root)
    except concepts_mod.ConceptError as exc:
        print(f"Cannot render — concept schema invalid:\n  ✗ {exc}")
        return 1

    if args.check:
        return _check(root, concepts)

    vis = root / VISUALS_DIR
    vis.mkdir(parents=True, exist_ok=True)

    # ── Render to a STAGING dir, then swap. Never delete before you can replace. ──
    #
    # This used to unlink every *.svg in visuals/ and only then start calling mmdc.
    # If mmdc was missing or a single diagram failed, the run aborted having already
    # destroyed all 186 committed SVGs, leaving an empty directory and git as the
    # only recovery. That happened on 2026-07-21.
    #
    # The stale-orphan problem the original delete solved is real — a concept that
    # drops a step leaves `<cid>.step-N.svg` behind forever, and the manifest-keyed
    # --check only catches a whole removed concept. So the delete still happens; it
    # just happens AFTER every render has succeeded, when there is something to put
    # back. Same end state, no window in which the repo is worse off than when the
    # command started.
    manifest = {"mmdc_version": MMDC_VERSION, "normalizer_version": NORMALIZER_VERSION, "concepts": {}}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        staged = tmp / "_staged"
        staged.mkdir()
        for c in concepts:
            cid = c["id"]
            (staged / f"{cid}.svg").write_text(_render_one(c["diagram"], f"c-{cid}", tmp), encoding="utf-8")
            if c["diagram_mini"]:
                (staged / f"{cid}.mini.svg").write_text(
                    _render_one(c["diagram_mini"], f"c-{cid}-mini", tmp), encoding="utf-8"
                )
            for idx, st in enumerate(c.get("steps", []), start=1):
                (staged / f"{cid}.step-{idx}.svg").write_text(
                    _render_one(st["diagram"], f"c-{cid}-step{idx}", tmp), encoding="utf-8"
                )
            manifest["concepts"][cid] = _source_hash(c)
            extras = []
            if c["diagram_mini"]:
                extras.append("+mini")
            if c.get("steps"):
                extras.append(f"+{len(c['steps'])} steps")
            print(f"  rendered {cid}" + (f"  ({', '.join(extras)})" if extras else ""))

        # Every render succeeded. NOW it is safe to clear the old set and swap the
        # staged one in — this is the only point at which the repo's committed SVGs
        # are removed, and there is a complete replacement in hand when it happens.
        for old_svg in vis.glob("*.svg"):
            old_svg.unlink()
        for new_svg in sorted(staged.glob("*.svg")):
            shutil.move(str(new_svg), str(vis / new_svg.name))

    (vis / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Rendered {len(concepts)} concept(s) → {VISUALS_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
