#!/usr/bin/env python3
"""visual_pack.py — the one place that knows how the pre-rendered diagram SVGs are packed.

Why this exists: the repo carried 1,019 generated SVG files (799 decision trees + 220 concept
diagrams). The Claude Code Directory stops validating a repo at 10,000 files, and these two sets
were the only block big enough to close the gap without deleting a diagram. Packing is lossless:
the same bytes, in a handful of files.

    knowledge/tree-visuals/pack-NN.js        decision trees, grouped by owning plugin (<= 40 shards).
                                             `window.__rcTreePack&&window.__rcTreePack({"<id>": "<svg>"});`
                                             A <script src> loads on file:// where fetch() would not, and the
                                             file is pure ASCII so the page's charset can never corrupt it.
    knowledge/concepts/visuals/visuals.pack.json
                                             concept diagrams, {"<name>.svg": "<svg>"}. Read at generation
                                             time only (the dashboard inlines them), so a plain JSON file.

Both renderers (render-trees.py, render-concepts.py), both generators (generate-dashboards.py,
generate-index-dashboard.py), concepts.py and the audit gates import THIS module, so the format cannot
drift between writer and reader. One member per line: a diagram change is a one-line diff.

    python3 scripts/visual_pack.py --self-test     # round trip, determinism, shard stability, loader JS
    python3 scripts/visual_pack.py --verify        # every manifest entry has its SVG in a pack, no strays

Stdlib only; Python 3.9-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TREE_DIR_REL = "plugins/ravenclaude-core/knowledge/tree-visuals"
CONCEPT_DIR_REL = "plugins/ravenclaude-core/knowledge/concepts/visuals"
MANIFEST_NAME = ".render-manifest.json"
CONCEPT_PACK_NAME = "visuals.pack.json"

# Decision trees are 28.8 MB over 116 owning plugins. 40 shards keep the lazy fetch near 0.7 MB and the
# repo ~95 files under the Directory's 10,000-file limit. Changing this reshuffles every shard, so it is a
# constant, not a knob: new owners fill the lightest shard instead (see assign_shards).
N_TREE_SHARDS = 40

_TREE_HEAD = "window.__rcTreePack&&window.__rcTreePack("
_TREE_TAIL = ");\n"
_TREE_PACK_RE = re.compile(r"^pack-(\d{2})\.js$")


class PackError(ValueError):
    """A pack file is malformed, or a member the manifest promises is missing."""


# ── trees ────────────────────────────────────────────────────────────────────────────────────────
def tree_owner(tree_id: str) -> str:
    """`power-platform--some-tree` -> `power-platform` (every committed id is `<plugin>--<slug>`)."""
    return tree_id.split("--", 1)[0]


def shard_name(n: int) -> str:
    return f"pack-{n:02d}"


def dump_tree_shard(members: dict) -> str:
    """One member per line, sorted by id, pure ASCII (non-ASCII escaped), so output is byte-deterministic."""
    lines = [
        f"{json.dumps(k)}: {json.dumps(members[k], ensure_ascii=True)}" for k in sorted(members)
    ]
    return _TREE_HEAD + "{\n" + ",\n".join(lines) + "\n}" + _TREE_TAIL


def load_tree_shard(text: str) -> dict:
    if not (text.startswith(_TREE_HEAD) and text.endswith(_TREE_TAIL)):
        raise PackError("tree shard does not have the expected wrapper")
    body = text[len(_TREE_HEAD) : -len(_TREE_TAIL)]
    try:
        obj = json.loads(body)
    except ValueError as exc:
        raise PackError(f"tree shard body is not JSON: {exc}")
    if not isinstance(obj, dict) or not all(isinstance(v, str) for v in obj.values()):
        raise PackError("tree shard must map id -> svg string")
    return obj


def assign_shards(owner_bytes: dict, previous: dict = None, n: int = N_TREE_SHARDS) -> dict:
    """owner -> shard number (1..n). Owners already placed in `previous` keep their shard (so adding a tree
    never reshuffles the others); each new owner goes to the currently lightest shard, largest first."""
    keep = {o: s for o, s in (previous or {}).items() if o in owner_bytes and 1 <= int(s) <= n}
    load = dict.fromkeys(range(1, n + 1), 0)
    for o, s in keep.items():
        load[int(s)] += owner_bytes[o]
    out = {o: int(s) for o, s in keep.items()}
    for o in sorted((o for o in owner_bytes if o not in out), key=lambda o: (-owner_bytes[o], o)):
        s = min(load, key=lambda i: (load[i], i))
        out[o] = s
        load[s] += owner_bytes[o]
    return out


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with open(str(tmp), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(str(tmp), str(path))


def write_tree_packs(vis: Path, svgs: dict, previous_owner_shards: dict = None) -> dict:
    """Write every shard for `svgs` ({tree_id: svg}) into `vis`; delete shards that are no longer needed.
    Returns the owner -> shard mapping to record in the manifest."""
    vis.mkdir(parents=True, exist_ok=True)
    sizes: dict = {}
    for tid, svg in svgs.items():
        sizes[tree_owner(tid)] = sizes.get(tree_owner(tid), 0) + len(svg.encode("utf-8"))
    owner_shards = assign_shards(sizes, previous_owner_shards)
    per_shard: dict = {}
    for tid, svg in svgs.items():
        per_shard.setdefault(owner_shards[tree_owner(tid)], {})[tid] = svg
    written = set()
    for n, members in sorted(per_shard.items()):
        _atomic_write(vis / (shard_name(n) + ".js"), dump_tree_shard(members))
        written.add(shard_name(n) + ".js")
    for old in vis.iterdir():
        if _TREE_PACK_RE.match(old.name) and old.name not in written:
            old.unlink()
    return owner_shards


def read_tree_manifest(vis: Path) -> dict:
    p = vis / MANIFEST_NAME
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def tree_shard_for(manifest: dict, tree_id: str):
    """`pack-07` for a rendered tree, or None (not rendered yet). Needs only the manifest, not the packs."""
    n = (manifest.get("owner_shards") or {}).get(tree_owner(tree_id))
    if n and tree_id in (manifest.get("trees") or {}):
        return shard_name(int(n))
    return None


def read_tree_svgs(vis: Path) -> dict:
    """Every packed tree SVG, {id: svg}. A member present in two shards is an error."""
    out: dict = {}
    for p in sorted(vis.iterdir()):
        if not _TREE_PACK_RE.match(p.name):
            continue
        for k, v in load_tree_shard(p.read_text(encoding="utf-8")).items():
            if k in out:
                raise PackError(f"tree {k!r} appears in more than one shard")
            out[k] = v
    return out


# ── concepts ─────────────────────────────────────────────────────────────────────────────────────
def dump_concept_pack(members: dict) -> str:
    lines = [
        f"{json.dumps(k)}: {json.dumps(members[k], ensure_ascii=False)}" for k in sorted(members)
    ]
    return "{\n" + ",\n".join(lines) + "\n}\n"


def load_concept_pack(text: str) -> dict:
    try:
        obj = json.loads(text)
    except ValueError as exc:
        raise PackError(f"concept pack is not JSON: {exc}")
    if not isinstance(obj, dict) or not all(isinstance(v, str) for v in obj.values()):
        raise PackError("concept pack must map name -> svg string")
    return obj


def write_concept_pack(vis: Path, members: dict) -> None:
    vis.mkdir(parents=True, exist_ok=True)
    _atomic_write(vis / CONCEPT_PACK_NAME, dump_concept_pack(members))
    _CONCEPT_CACHE.pop(str(vis / CONCEPT_PACK_NAME), None)


_CONCEPT_CACHE: dict = {}


def read_concept_pack(vis: Path) -> dict:
    key = str(vis / CONCEPT_PACK_NAME)
    if key not in _CONCEPT_CACHE:
        p = vis / CONCEPT_PACK_NAME
        _CONCEPT_CACHE[key] = (
            load_concept_pack(p.read_text(encoding="utf-8")) if p.is_file() else {}
        )
    return _CONCEPT_CACHE[key]


def concept_svg(plugin_dir: Path, rel: str) -> str:
    """The stripped SVG for a `concepts.json` path such as `knowledge/concepts/visuals/<name>.svg`
    ('' if absent). The path stays a stable KEY: only its last segment selects the pack member."""
    if not rel:
        return ""
    vis = plugin_dir / "knowledge" / "concepts" / "visuals"
    return read_concept_pack(vis).get(rel.rsplit("/", 1)[-1], "").strip()


# ── the page-side loader, shared by dashboard.html and index.html ───────────────────────────────
# Opening a <details> that holds an <img data-pack=URL data-tree=ID> loads the shard once (a <script>,
# which works on file://) and gives the <img> a data: URI. The pack's SVG is byte-identical to the old
# file; an <img> does not inherit page CSS vars either way, so theming is unchanged.
CLIENT_JS = r"""
/* rc-tree-loader: lazy-load pre-rendered decision-tree SVGs from packed shards (scripts/visual_pack.py). */
(function () {
  if (window.__rcTreeLoader) return;
  window.__rcTreeLoader = true;
  var store = (window.__rcTreeStore = window.__rcTreeStore || {});
  var state = {};
  var waiting = {};
  window.__rcTreePack = function (members) {
    for (var id in members) {
      if (Object.prototype.hasOwnProperty.call(members, id)) store[id] = members[id];
    }
  };
  var style = document.createElement("style");
  style.textContent = "img[data-pack]:not([src]){visibility:hidden;min-height:2em}";
  (document.head || document.documentElement).appendChild(style);
  function show(img) {
    var svg = store[img.getAttribute("data-tree")];
    if (typeof svg !== "string") {
      img.setAttribute("data-state", "missing");
      return;
    }
    img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    img.setAttribute("data-state", "ready");
  }
  function load(img) {
    if (img.getAttribute("data-state") || img.getAttribute("src")) return;
    var url = img.getAttribute("data-pack");
    if (!url) return;
    img.setAttribute("data-state", "loading");
    if (state[url] === "done") {
      show(img);
      return;
    }
    if (waiting[url]) {
      waiting[url].push(img);
      return;
    }
    waiting[url] = [img];
    var s = document.createElement("script");
    s.async = true;
    s.onload = function () {
      state[url] = "done";
      var q = waiting[url];
      delete waiting[url];
      for (var i = 0; i < q.length; i++) show(q[i]);
    };
    s.onerror = function () {
      var q = waiting[url];
      delete waiting[url];
      for (var i = 0; i < q.length; i++) {
        q[i].removeAttribute("data-state");
        q[i].title = "Diagram failed to load - close and reopen to retry";
      }
    };
    s.src = url;
    (document.head || document.documentElement).appendChild(s);
  }
  document.addEventListener(
    "toggle",
    function (ev) {
      var d = ev.target;
      if (!d || !d.open || !d.querySelectorAll) return;
      var imgs = d.querySelectorAll("img[data-pack]");
      for (var i = 0; i < imgs.length; i++) {
        // Only this <details>' OWN diagram: opening a plugin group must not load every diagram nested in it.
        if (imgs[i].closest && imgs[i].closest("details") !== d) continue;
        load(imgs[i]);
      }
    },
    true
  );
})();
"""

# A minimal DOM, enough to drive CLIENT_JS under node (self-test only).
_NODE_HARNESS = r"""
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
const packsByUrl = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const appended = [];
let listener = null;
let listeners = 0;
function el(tag) {
  const a = {};
  return {
    tag, attrs: a, children: [],
    getAttribute(k) { return Object.prototype.hasOwnProperty.call(a, k) ? a[k] : null; },
    setAttribute(k, v) { a[k] = String(v); },
    removeAttribute(k) { delete a[k]; },
    set src(v) { a.src = v; }, get src() { return a.src; },
    querySelectorAll() { return this.children; },
    open: true,
  };
}
global.window = global;
global.document = {
  head: { appendChild(n) { appended.push(n); if (n.tag === "script") setTimeout(() => {
    const rec = packsByUrl[n.src];
    if (rec === "ERROR") { n.onerror(); return; }
    if (rec) window.__rcTreePack(rec);
    n.onload();
  }, 0); } },
  createElement: el,
  addEventListener(name, fn, cap) { if (name === "toggle" && cap === true) { listener = fn; listeners++; } },
};
eval(src);
eval(src); // idempotent: the second load must not register a second listener or loader
const out = {};
function img(id, pack) { const e = el("img"); e.setAttribute("data-tree", id); e.setAttribute("data-pack", pack); return e; }
const d1 = el("details"); d1.children = [img("a--one", "p1.js"), img("a--two", "p1.js")];
const d2 = el("details"); d2.children = [img("a--one", "p1.js"), img("zz--ghost", "p1.js")];
const d3 = el("details"); d3.children = [img("b--bad", "bad.js")];
const closed = el("details"); closed.open = false; closed.children = [img("a--one", "never.js")];
const outer = el("details"), inner = el("details");
const nested = img("a--one", "nested.js");
outer.children = [nested];
for (const holder of [d1, d2, d3, closed]) for (const c of holder.children) c.closest = () => holder;
nested.closest = () => inner;
listener({ target: outer });
listener({ target: d1 });
listener({ target: closed });
listener({ target: d3 });
setTimeout(() => {
  listener({ target: d2 });
  out.listeners = listeners;
  out.scripts = appended.filter((n) => n.tag === "script").map((n) => n.src);
  out.d1 = d1.children.map((i) => [i.getAttribute("data-state"), (i.src || "").slice(0, 40)]);
  out.d2 = d2.children.map((i) => i.getAttribute("data-state"));
  out.d3 = d3.children.map((i) => [i.getAttribute("data-state"), i.title || ""]);
  out.closed = closed.children.map((i) => i.getAttribute("data-state"));
  out.nested = nested.getAttribute("data-state");
  out.decoded = decodeURIComponent(d1.children[0].src.split(",").slice(1).join(","));
  console.log(JSON.stringify(out));
}, 30);
"""


# ── checks ───────────────────────────────────────────────────────────────────────────────────────
def verify_trees(vis: Path, manifest: dict = None) -> list:
    """Problems with the tree packs vs the manifest (empty list = consistent)."""
    manifest = manifest if manifest is not None else read_tree_manifest(vis)
    try:
        shards = {}
        for p in sorted(vis.iterdir()):
            if _TREE_PACK_RE.match(p.name):
                shards[p.name[: -len(".js")]] = load_tree_shard(p.read_text(encoding="utf-8"))
    except PackError as exc:
        return [f"  ✗ tree packs unreadable: {exc}"]
    problems = []
    recorded = set(manifest.get("trees") or {})
    seen = {}
    for name, members in shards.items():
        for tid in members:
            if tid in seen:
                problems.append(f"  ✗ {tid}: appears in more than one shard ({seen[tid]}, {name})")
            seen[tid] = name
    for tid in sorted(recorded):
        want = tree_shard_for(manifest, tid)
        if want is None:
            problems.append(f"  ✗ {tid}: no shard recorded for its owner in the manifest")
        elif tid not in shards.get(want, {}):
            where = f" (found in {seen[tid]})" if tid in seen else ""
            problems.append(f"  ✗ {tid}: expected in {want}.js but it is not there{where}")
    for tid in sorted(set(seen) - recorded):
        problems.append(f"  ✗ {tid}: packed but absent from the manifest (stray member)")
    return problems


# ── self-test ────────────────────────────────────────────────────────────────────────────────────
def self_test() -> int:
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(("  ✓ " if ok else "  ✗ ") + name + ((" - " + detail) if (detail and not ok) else ""))
        if not ok:
            failures.append(name)

    nasty = "a \"quoted\" <svg x='1'>\n\ttab \\ back — dash ✓ \U0001f600 </svg>"
    members = {"b--two": nasty, "a--one": "<svg/>", "a--three": "x"}
    text = dump_tree_shard(members)
    check(
        "tree shard round-trips exactly (quotes, newlines, non-ASCII, astral)",
        load_tree_shard(text) == members,
    )
    check("tree shard is pure ASCII", all(ord(c) < 128 for c in text))
    check(
        "tree shard is deterministic and order-independent",
        dump_tree_shard(dict(reversed(list(members.items())))) == text,
    )
    check(
        "tree shard has one member per line",
        text.count("\n") == len(members) + 2,
        str(text.count("\n")),
    )
    for bad_name, bad in (
        ("wrapper removed", text[len(_TREE_HEAD) :]),
        ("trailing garbage", text + "x"),
        ("not JSON", _TREE_HEAD + "{nope" + _TREE_TAIL),
        ("non-string member", _TREE_HEAD + '{"a": 1}' + _TREE_TAIL),
    ):
        try:
            load_tree_shard(bad)
            check("tree shard rejects: " + bad_name, False)
        except PackError:
            check("tree shard rejects: " + bad_name, True)

    ctext = dump_concept_pack({"z.svg": nasty, "a.svg": "<svg/>"})
    check(
        "concept pack round-trips exactly",
        load_concept_pack(ctext) == {"z.svg": nasty, "a.svg": "<svg/>"},
    )
    check(
        "concept pack is deterministic",
        dump_concept_pack({"a.svg": "<svg/>", "z.svg": nasty}) == ctext,
    )

    sizes = {"alpha": 900, "beta": 800, "gamma": 100, "delta": 100}
    first = assign_shards(sizes, None, n=3)
    check(
        "assign_shards places every owner in 1..n",
        sorted(first) == sorted(sizes) and all(1 <= s <= 3 for s in first.values()),
    )
    check(
        "assign_shards balances (largest owners land in different shards)",
        first["alpha"] != first["beta"],
    )
    check("assign_shards is deterministic", assign_shards(sizes, None, n=3) == first)
    grown = assign_shards(dict(sizes, epsilon=5000, alpha=9999), first, n=3)
    check(
        "assign_shards keeps existing owners where they were",
        all(grown[o] == first[o] for o in sizes),
    )
    lightest = min(range(1, 4), key=lambda i: (sum(sizes[o] for o in sizes if first[o] == i), i))
    check(
        "assign_shards puts a NEW owner in the lightest shard",
        grown["epsilon"] == lightest,
        f"{grown['epsilon']} vs {lightest}",
    )
    check(
        "assign_shards drops owners that disappeared",
        "gamma" not in assign_shards({"alpha": 1}, first, n=3),
    )

    with tempfile.TemporaryDirectory() as td:
        vis = Path(td) / "tree-visuals"
        svgs = {f"{o}--t{i}": f"<svg>{o}{i}✓</svg>" for o in ("p", "q", "r") for i in range(3)}
        mapping = write_tree_packs(vis, svgs)
        files = sorted(x.name for x in vis.iterdir())
        check(
            "write_tree_packs writes one file per used shard, no temp files",
            len(files) == len(set(mapping.values())) and not any(f.endswith(".tmp") for f in files),
            str(files),
        )
        check("read_tree_svgs returns exactly what was written", read_tree_svgs(vis) == svgs)
        manifest = {"trees": dict.fromkeys(svgs, "h"), "owner_shards": mapping}
        (vis / MANIFEST_NAME).write_text(json.dumps(manifest))
        check(
            "verify_trees is clean on a consistent pack",
            verify_trees(vis) == [],
            str(verify_trees(vis)),
        )
        check(
            "tree_shard_for answers from the manifest alone",
            tree_shard_for(manifest, "p--t0") == shard_name(mapping["p"])
            and tree_shard_for(manifest, "p--nope") is None,
        )
        stale = vis / "pack-39.js"
        stale.write_text(dump_tree_shard({"old--x": "<svg/>"}))
        write_tree_packs(vis, svgs, mapping)
        check("write_tree_packs removes a shard that is no longer needed", not stale.exists())
        bad = dict(manifest, trees=dict(manifest["trees"], **{"p--ghost": "h"}))
        check(
            "verify_trees catches a manifest entry with no packed SVG",
            any("p--ghost" in x for x in verify_trees(vis, bad)),
        )
        shard = vis / (shard_name(mapping["p"]) + ".js")
        members_p = load_tree_shard(shard.read_text(encoding="utf-8"))
        members_p["p--stray"] = "<svg/>"
        shard.write_text(dump_tree_shard(members_p), encoding="utf-8")
        check(
            "verify_trees catches a stray packed member",
            any("p--stray" in x for x in verify_trees(vis, manifest)),
        )
        plug_dir = Path(td) / "plugin"
        write_concept_pack(
            plug_dir / "knowledge" / "concepts" / "visuals",
            {"x.svg": "  <svg/>\n", "x.step-1.svg": "<svg>1</svg>"},
        )
        check(
            "concept_svg looks a path up by its last segment and strips it",
            concept_svg(plug_dir, "knowledge/concepts/visuals/x.svg") == "<svg/>"
            and concept_svg(plug_dir, "knowledge/concepts/visuals/x.step-1.svg") == "<svg>1</svg>"
            and concept_svg(plug_dir, "knowledge/concepts/visuals/nope.svg") == ""
            and concept_svg(plug_dir, "") == "",
        )

    check("CLIENT_JS never contains a script terminator", "</script" not in CLIENT_JS.lower())
    check(
        "CLIENT_JS parens/braces balance",
        CLIENT_JS.count("{") == CLIENT_JS.count("}")
        and CLIENT_JS.count("(") == CLIENT_JS.count(")"),
    )
    node = shutil.which("node")
    if not node:
        print("  - CLIENT_JS behaviour under node: NOT RUN (node not on PATH) - this is not a pass")
    else:
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            (t / "h.js").write_text(_NODE_HARNESS)
            (t / "loader.js").write_text(CLIENT_JS)
            (t / "packs.json").write_text(
                json.dumps(
                    {
                        "p1.js": {"a--one": "<svg>one ✓</svg>", "a--two": "<svg>two</svg>"},
                        "bad.js": "ERROR",
                    }
                )
            )
            proc = subprocess.run(
                [node, str(t / "h.js"), str(t / "loader.js"), str(t / "packs.json")],
                capture_output=True,
                text=True,
                timeout=30,
            )
            try:
                got = json.loads(proc.stdout.strip().splitlines()[-1])
            except Exception:  # noqa: BLE001 - report the raw output instead
                got = None
            check("CLIENT_JS runs under node", got is not None, (proc.stderr or proc.stdout)[-300:])
            if got is not None:
                check(
                    "loading it twice registers one toggle listener",
                    got["listeners"] == 1,
                    str(got["listeners"]),
                )
                check(
                    "loader fetches each shard once, even for several images",
                    got["scripts"] == ["p1.js", "bad.js"],
                    str(got["scripts"]),
                )
                check(
                    "images get a data: URI and state ready",
                    got["d1"][0][0] == "ready"
                    and got["d1"][0][1].startswith("data:image/svg+xml;charset=utf-8,"),
                    str(got["d1"]),
                )
                check(
                    "the data: URI decodes to the packed SVG bytes",
                    got["decoded"] == "<svg>one ✓</svg>",
                )
                check(
                    "a second <details> reuses the loaded shard; an unknown id is 'missing'",
                    got["d2"] == ["ready", "missing"],
                    str(got["d2"]),
                )
                check(
                    "a failed shard load leaves the image retryable with a hint",
                    got["d3"][0][0] is None and "retry" in got["d3"][0][1],
                    str(got["d3"]),
                )
                check(
                    "a closed <details> loads nothing", got["closed"] == [None], str(got["closed"])
                )
                check(
                    "opening an OUTER <details> does not load diagrams nested in an inner one",
                    got["nested"] is None,
                    str(got["nested"]),
                )

    if failures:
        print("visual_pack self-test FAILED: " + ", ".join(failures))
        return 1
    print("visual_pack self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument(
        "--verify", action="store_true", help="check the committed packs against their manifests"
    )
    ap.add_argument("--root", default=".", help="repo root")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.verify:
        root = Path(args.root).resolve()
        problems = verify_trees(root / TREE_DIR_REL)
        if problems:
            print("Tree packs inconsistent with their manifest:")
            print("\n".join(problems))
            return 1
        m = read_tree_manifest(root / TREE_DIR_REL)
        print(
            f"Tree packs OK - {len(m.get('trees', {}))} tree(s) in {len(set((m.get('owner_shards') or {}).values()))} shard(s)."
        )
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
