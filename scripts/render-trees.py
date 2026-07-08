#!/usr/bin/env python3
"""render-trees.py — pre-render every '## Decision Tree:' Mermaid block to a
themed, inlinable static SVG for the dashboard's Guidance tab.

Sibling of render-concepts.py (same offline-first rationale: the dashboard is
byte-deterministic and must work on a static host / file://, so we inline a
pre-rendered SVG rather than ship the 3.3MB mermaid runtime). The tree inventory
+ stable ids come from generate-dashboards.py's _decision_trees_inventory() — the
single source of truth, so the generator and this renderer never disagree on ids.

Speed: all fences are rendered in ONE mermaid-cli launch (a markdown file with N
```mermaid blocks → out-1.svg … out-N.svg), so 158 diagrams cost one Chromium
startup, not 158. Each SVG is then normalized to the dashboard's token system and
written as <id>.svg.

CI never needs Chromium: rendering writes a source-hash manifest; `--check`
re-derives hashes from the tree sources and diffs them against the committed
SVGs, so a tree edited without a re-render fails CI without launching a browser.
Only whoever edits a tree diagram needs mermaid-cli locally.

Usage:
    render-trees.py [--root DIR]          # render every tree's SVG
    render-trees.py --check [--root DIR]  # verify committed SVGs match source
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
import importlib.util as _ilu

# Pin the renderer so committed SVGs stay reproducible across machines/time.
MMDC_VERSION = "11.15.0"
# Bump when the normalizer logic below changes (invalidates every committed SVG).
NORMALIZER_VERSION = 2

VISUALS_DIR = "plugins/ravenclaude-core/knowledge/tree-visuals"
MANIFEST_NAME = ".render-manifest.json"

_PUPPETEER_CFG = '{"args":["--no-sandbox","--disable-setuid-sandbox"]}'
_BG_WHITE_RE = re.compile(r"background-color:\s*white;?", re.IGNORECASE)


def _load_inventory(root: Path) -> list[dict]:
    """Import generate-dashboards.py and call its tree inventory (single source of
    truth for ids + mermaid source). PLUGINS_DIR/REPO_ROOT there resolve from the
    script location, which is this same repo — so --root is informational here."""
    spec = _ilu.spec_from_file_location(
        "_gd_trees", str(Path(__file__).resolve().parent / "generate-dashboards.py")
    )
    gd = _ilu.module_from_spec(spec)
    spec.loader.exec_module(gd)  # type: ignore[union-attr]
    return [t for t in gd._decision_trees_inventory() if t.get("mermaid")]


def _theme_style(svg_id: str) -> str:
    """Override <style> remapping raw-Mermaid colors onto dashboard tokens (same
    approach as render-concepts.py). `!important` + id prefix beat Mermaid's own
    per-id rules; CSS vars let the dashboard's light-mode block flip the SVG.

    Each var() carries a concrete LIGHT fallback so the SVG also renders correctly
    when loaded as an external `<img>`/`<object>` (the lazy-load path on the plugin
    detail pages + the Guidance tab) — where the page's CSS custom properties do
    NOT cascade in. Inline use is unchanged: the page defines the vars, so the
    fallback is ignored and the diagram stays fully theme-reactive (incl. the dark
    toggle). The fallback palette gives nodes a bordered light fill + dark text, so
    an img-loaded tree stays legible on either a light or dark page background."""
    s = f"#{svg_id}"
    return (
        "<style>"
        f"{s} .nodeLabel,{s} .edgeLabel,{s} text,{s} span,{s} p,{s} div"
        "{fill:var(--text,#1f2937)!important;color:var(--text,#1f2937)!important;background:transparent!important}"
        f"{s} .node rect,{s} .node polygon,{s} .node circle,{s} .node path,{s} .label-container"
        "{fill:var(--surface-2,#eef2f7)!important;stroke:var(--border,#94a3b8)!important;stroke-width:1.5px!important}"
        f"{s} .cluster rect{{fill:var(--surface,#f1f5f9)!important;stroke:var(--border,#94a3b8)!important}}"
        f"{s} .edgePath .path,{s} .edgePath path,{s} path.flowchart-link,{s} .flowchart-link"
        "{stroke:var(--muted,#64748b)!important;stroke-width:1.5px!important;fill:none!important}"
        f"{s} marker path,{s} .arrowMarkerPath,{s} #arrowhead path"
        "{fill:var(--muted,#64748b)!important;stroke:none!important}"
        f"{s} .edgeLabel rect,{s} .edgeLabel .labelBkg,{s} .label-container.edgeLabel"
        "{fill:var(--bg,#ffffff)!important;opacity:1!important}"
        f"{s} .edgeLabel text,{s} .edgeLabel span{{fill:var(--muted,#64748b)!important;color:var(--muted,#64748b)!important}}"
        f"{s} .node:hover rect,{s} .node:hover polygon,{s} .node:hover circle,{s} .node:hover path"
        "{stroke:var(--accent,#0d9488)!important;stroke-width:2.5px!important;cursor:default}"
        "</style>"
    )


def _normalize(svg: str, svg_id: str) -> str:
    """Rewrite raw mmdc SVG: unique id prefix, transparent bg, theme override.
    Pure string ops → deterministic."""
    svg = svg.replace("my-svg", svg_id)
    svg = _BG_WHITE_RE.sub("", svg)
    m = re.match(r"<svg\b([^>]*)>", svg)
    if not m:
        return svg
    attrs = m.group(1)
    if 'class="' in attrs:
        attrs = attrs.replace('class="', 'class="rc-tree-diagram ', 1)
    else:
        attrs = ' class="rc-tree-diagram"' + attrs
    return f"<svg{attrs}>" + _theme_style(svg_id) + svg[m.end():]


def _source_hash(tree: dict) -> str:
    h = hashlib.sha256()
    payload = json.dumps(
        {
            "mermaid": tree["mermaid"],
            "mmdc": MMDC_VERSION,
            "normalizer": NORMALIZER_VERSION,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    h.update(payload.encode("utf-8"))
    return h.hexdigest()


def _svg_id(tree_id: str) -> str:
    return f"t-{tree_id}"


def _render_all(trees: list[dict], tmp: Path) -> dict[str, str]:
    """Render EVERY tree's mermaid in a single mermaid-cli launch (markdown with N
    fences → out-N.svg). Returns {tree_id: normalized_svg}. Fence order is the
    inventory order, which is how mmdc numbers its outputs."""
    md_path = tmp / "trees.md"
    out_path = tmp / "out.svg"  # mmdc writes out-1.svg, out-2.svg, … for markdown
    cfg_path = tmp / "pp.json"
    cfg_path.write_text(_PUPPETEER_CFG, encoding="utf-8")
    # One ```mermaid block per tree, separated so mmdc counts them distinctly.
    # Defense-in-depth: a literal ``` inside a tree's source would prematurely
    # close its fence and SHIFT every subsequent out-N.svg by one — a mis-map the
    # count check below can't catch (the total count still matches). Fail loudly
    # at write time with an actionable message instead.
    blocks = []
    for t in trees:
        if "```" in t["mermaid"]:
            raise RuntimeError(
                f"tree {t['id']!r} mermaid source contains a literal '```' fence — "
                "it would break the concatenated-markdown fence numbering and mis-map "
                "rendered SVGs to the wrong tree ids. Remove the backtick fence."
            )
        blocks.append(f"```mermaid\n{t['mermaid']}\n```")
    md_path.write_text("\n\n---\n\n".join(blocks) + "\n", encoding="utf-8")
    cmd = [
        "npx", "--yes", f"@mermaid-js/mermaid-cli@{MMDC_VERSION}",
        "-i", str(md_path), "-o", str(out_path),
        "-p", str(cfg_path), "-b", "transparent",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        raise RuntimeError(f"mermaid-cli failed:\n{proc.stderr.strip()[-1500:]}")
    result: dict[str, str] = {}
    for i, t in enumerate(trees, start=1):
        svg_file = tmp / f"out-{i}.svg"
        if not svg_file.exists():
            raise RuntimeError(
                f"expected {svg_file.name} for tree {t['id']!r} — mmdc rendered "
                f"{len(list(tmp.glob('out-*.svg')))} of {len(trees)} fences"
            )
        result[t["id"]] = _normalize(svg_file.read_text(encoding="utf-8"), _svg_id(t["id"]))
    return result


def _check(root: Path, trees: list[dict]) -> int:
    vis = root / VISUALS_DIR
    manifest_path = vis / MANIFEST_NAME
    if not manifest_path.exists():
        print(f"tree render manifest missing ({VISUALS_DIR}/{MANIFEST_NAME}) — run: scripts/render-trees.py")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    recorded = manifest.get("trees", {})
    problems: list[str] = []
    for t in trees:
        tid = t["id"]
        want = _source_hash(t)
        if recorded.get(tid) != want:
            problems.append(f"  ✗ {tid}: tree diagram changed since last render — re-run scripts/render-trees.py")
            continue
        if not (vis / f"{tid}.svg").exists():
            problems.append(f"  ✗ {tid}: {tid}.svg missing")
    stale = set(recorded) - {t["id"] for t in trees}
    for tid in sorted(stale):
        problems.append(f"  ✗ {tid}: orphaned in manifest (tree removed) — re-run scripts/render-trees.py")
    if problems:
        print("Decision-tree SVG freshness gate FAILED:")
        print("\n".join(problems))
        return 1
    print(f"Decision-tree SVGs OK — {len(trees)} tree(s) match their diagram source.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--check", action="store_true", help="verify committed SVGs match source (no render)")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    trees = _load_inventory(root)

    if args.check:
        return _check(root, trees)

    vis = root / VISUALS_DIR
    vis.mkdir(parents=True, exist_ok=True)
    # Clear stale SVGs so a removed tree doesn't leave an orphan file behind.
    for old in vis.glob("*.svg"):
        old.unlink()
    manifest = {"mmdc_version": MMDC_VERSION, "normalizer_version": NORMALIZER_VERSION, "trees": {}}
    with tempfile.TemporaryDirectory() as td:
        rendered = _render_all(trees, Path(td))
    for t in trees:
        tid = t["id"]
        (vis / f"{tid}.svg").write_text(rendered[tid], encoding="utf-8")
        manifest["trees"][tid] = _source_hash(t)
    (vis / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Rendered {len(trees)} decision-tree SVG(s) → {VISUALS_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
