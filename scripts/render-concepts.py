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
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concepts as concepts_mod  # noqa: E402

# Pin the renderer so committed SVGs stay reproducible across machines/time.
MMDC_VERSION = "11.15.0"
# Bump when the normalizer logic below changes (invalidates every committed SVG).
NORMALIZER_VERSION = 2

VISUALS_DIR = "plugins/ravenclaude-core/knowledge/concepts/visuals"
MANIFEST_NAME = ".render-manifest.json"

_PUPPETEER_CFG = '{"args":["--no-sandbox","--disable-setuid-sandbox"]}'
_BG_WHITE_RE = re.compile(r"background-color:\s*white;?", re.IGNORECASE)


def _theme_style(svg_id: str) -> str:
    """An override <style> that remaps raw-Mermaid colors onto dashboard tokens.
    `!important` + the id prefix beat Mermaid's own injected per-id rules. Uses
    CSS vars so the dashboard's prefers-color-scheme:light block flips the SVG."""
    s = f"#{svg_id}"
    return (
        "<style>"
        f"{s} .nodeLabel,{s} .edgeLabel,{s} text,{s} span,{s} p,{s} div"
        "{fill:var(--text)!important;color:var(--text)!important;"
        "font-family:var(--font-mono)!important;background:transparent!important}"
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
    attrs = m.group(1)
    if 'class="' in attrs:
        attrs = attrs.replace('class="', 'class="rc-concept-diagram ', 1)
    else:
        attrs = ' class="rc-concept-diagram"' + attrs
    return f"<svg{attrs}>" + _theme_style(svg_id) + svg[m.end():]


def _source_hash(concept: dict) -> str:
    h = hashlib.sha256()
    payload = json.dumps(
        {
            "diagram": concept["diagram"],
            "diagram_mini": concept["diagram_mini"],
            "mmdc": MMDC_VERSION,
            "normalizer": NORMALIZER_VERSION,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    h.update(payload.encode("utf-8"))
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
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0 or not out_path.exists():
        raise RuntimeError(f"mermaid-cli failed for {svg_id}:\n{proc.stderr.strip()[-800:]}")
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
    for c in concepts:
        cid = c["id"]
        want = _source_hash(c)
        if recorded.get(cid) != want:
            problems.append(f"  ✗ {cid}: diagram source changed since last render — re-run scripts/render-concepts.py")
            continue
        if not (vis / f"{cid}.svg").exists():
            problems.append(f"  ✗ {cid}: {cid}.svg missing")
        if c["diagram_mini"] and not (vis / f"{cid}.mini.svg").exists():
            problems.append(f"  ✗ {cid}: {cid}.mini.svg missing")
    stale = set(recorded) - {c["id"] for c in concepts}
    for cid in sorted(stale):
        problems.append(f"  ✗ {cid}: orphaned in manifest (concept removed) — re-run scripts/render-concepts.py")
    if problems:
        print("Concept SVG freshness gate FAILED:")
        print("\n".join(problems))
        return 1
    print(f"Concept SVGs OK — {len(concepts)} concept(s) match their diagram source.")
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
    manifest = {"mmdc_version": MMDC_VERSION, "normalizer_version": NORMALIZER_VERSION, "concepts": {}}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for c in concepts:
            cid = c["id"]
            (vis / f"{cid}.svg").write_text(_render_one(c["diagram"], f"c-{cid}", tmp), encoding="utf-8")
            if c["diagram_mini"]:
                (vis / f"{cid}.mini.svg").write_text(
                    _render_one(c["diagram_mini"], f"c-{cid}-mini", tmp), encoding="utf-8"
                )
            manifest["concepts"][cid] = _source_hash(c)
            print(f"  rendered {cid}" + ("  (+mini)" if c["diagram_mini"] else ""))
    (vis / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Rendered {len(concepts)} concept(s) → {VISUALS_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
