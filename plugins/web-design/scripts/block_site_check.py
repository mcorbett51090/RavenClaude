#!/usr/bin/env python3
"""block_site_check.py: the block-site contract, checked. Stdlib only, Python 3.9+.

A block site stays pixel-perfect and upgradeable only while every block keeps
its contract and every manifest stays inside it. This turns the contract in
templates/block-site/ into exit codes.

  catalog CATALOG                lint every block contract against
                                 block.schema.json and the rules a schema cannot
                                 state (closed props, bounded strings and lists,
                                 no styling props, level-1 blocks first, paths
                                 that resolve, unique ids). CATALOG is either a
                                 catalog.json ({"blocks": [...]}, as the kit
                                 ships) or a directory of <id>/block.json files
  manifest FILE --catalog CATALOG
                                 resolve a site manifest against the catalog:
                                 unknown blocks or variants, props outside the
                                 block's schema, the single-h1 order, maxPerPage,
                                 adjacency, two dark bands in a row, locked tones,
                                 placeholder text, asset and link references,
                                 and image sizes too small for their slot
  tokens FILE                    check every colour-role pairing in tokens.css,
                                 light and dark, against WCAG AA (text 4.5:1,
                                 focus ring 3:1), reading the values from the
                                 file itself so there is no second copy to drift
  fixtures CATALOG --out FILE    write a stress manifest from the catalog's own
                                 bounds: every block at its minimum, its maximum,
                                 one unbreakable word at full length, and RTL
                                 text. Render it, then run device_matrix.mjs on it.
  --self-test                    break each rule in a copy of the starter kit and
                                 require it to be reported; require the kit
                                 itself (catalog, example manifest, fixtures) to
                                 pass.

Exit: 0 clean (warnings may print), 1 problems, 2 usage.
"""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, "..", "templates", "block-site"))

# ─── a JSON Schema validator for the subset the contracts use ────────────────

TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
}


def _is_type(value, t):
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, TYPES[t])


def validate(schema, value, root=None, path="$"):
    """Return a list of 'path: message' strings. Supports: type, properties,
    required, additionalProperties (bool or schema), propertyNames, enum, const,
    minLength, maxLength, pattern, items, minItems, maxItems, uniqueItems,
    minimum, maximum, $ref (#/$defs/...). format is not enforced."""
    root = root if root is not None else schema
    errs = []
    if "$ref" in schema:
        ref = schema["$ref"]
        m = re.match(r"^#/\$defs/(.+)$", ref)
        if not m:
            return [f"{path}: unsupported $ref {ref}"]
        return validate(root["$defs"][m.group(1)], value, root, path)
    t = schema.get("type")
    if t is not None and not _is_type(value, t):
        return [f"{path}: expected {t}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {json.dumps(value)} is not one of {json.dumps(schema['enum'])}")
    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: must be {json.dumps(schema['const'])}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errs.append(f"{path}: shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errs.append(f"{path}: {len(value)} characters, more than {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{path}: {json.dumps(value)} does not match {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}: below {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{path}: above {schema['maximum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errs.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errs.append(f"{path}: {len(value)} items, more than {schema['maxItems']}")
        if schema.get("uniqueItems"):
            seen = [json.dumps(v, sort_keys=True) for v in value]
            if len(seen) != len(set(seen)):
                errs.append(f"{path}: items must be unique")
        if isinstance(schema.get("items"), dict):
            for i, v in enumerate(value):
                errs += validate(schema["items"], v, root, f"{path}[{i}]")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing required {k!r}")
        if "propertyNames" in schema:
            for k in value:
                errs += validate(schema["propertyNames"], k, root, f"{path} key {k!r}")
        extra = schema.get("additionalProperties", True)
        for k, v in value.items():
            if k in props:
                errs += validate(props[k], v, root, f"{path}.{k}")
            elif extra is False:
                errs.append(f"{path}: unknown property {k!r}")
            elif isinstance(extra, dict):
                errs += validate(extra, v, root, f"{path}.{k}")
    return errs


# ─── catalog ──────────────────────────────────────────────────────────────────

# Props that would let a manifest restyle a block: styling belongs to tokens and
# variants, never to content.
STYLE_NAME = re.compile(
    r"^(style|styles|class|classes|classname|css|theme|colou?r|background|bg|font|fontsize|fontfamily|fontweight|"
    r"padding|margin|gap|width|height|align|textalign|justify|radius|shadow|opacity|zindex)$|"
    r"(colou?r|classname|css|style|fontsize|padding|margin|radius|shadow)$",
    re.IGNORECASE,
)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_blocks(catalog):
    """Read a catalog in either form. Returns (problems, [(where, block, dir_id)]).

    A file is a bundle, {"blocks": [...]}. A directory holds one <id>/block.json
    per block, and there dir_id is the directory name the block's id must match.
    """
    if os.path.isfile(catalog):
        bundle = load_json(catalog)
        if not isinstance(bundle, dict) or not isinstance(bundle.get("blocks"), list):
            return [f'{catalog}: a catalog file is an object with a "blocks" list'], []
        extra = sorted(set(bundle) - {"$schema", "description", "blocks"})
        problems = [f"{catalog}: unknown top-level key(s) {extra}"] if extra else []
        out = []
        for i, b in enumerate(bundle["blocks"]):
            bid = b.get("id") if isinstance(b, dict) else None
            out.append((f"blocks[{i}]" + (f" ({bid})" if isinstance(bid, str) else ""), b, None))
        return problems, out
    out = []
    for dirpath, _dirs, files in sorted(os.walk(catalog)):
        if "block.json" in files:
            p = os.path.join(dirpath, "block.json")
            out.append((os.path.relpath(p, catalog), load_json(p), os.path.basename(dirpath)))
    return [], out


def walk_props(schema, path="props"):
    """Yield (path, node) for every node of a props schema."""
    yield path, schema
    for k, v in (schema.get("properties") or {}).items():
        yield from walk_props(v, f"{path}.{k}")
    if isinstance(schema.get("items"), dict):
        yield from walk_props(schema["items"], f"{path}[]")


def prop_paths(schema, path=""):
    """Every addressable prop path, in the assetProps notation (a.b, list[].c)."""
    out = set()
    for k, v in (schema.get("properties") or {}).items():
        p = f"{path}.{k}" if path else k
        out.add(p)
        out |= prop_paths(v, p)
        if isinstance(v.get("items"), dict):
            out.add(f"{p}[]")
            out |= prop_paths(v["items"], f"{p}[]")
    return out


def check_catalog(catalog, block_schema):
    if not os.path.exists(catalog):
        return [f"{catalog}: no such catalog file or directory"], {}
    problems, blocks = find_blocks(catalog)
    if not blocks:
        return problems or [f"{catalog}: no block contracts found"], {}
    by_id = {}
    for where, b, dir_id in blocks:
        for e in validate(block_schema, b):
            problems.append(f"{where}: {e}")
        if not isinstance(b, dict) or "id" not in b:
            continue
        if b["id"] in by_id:
            problems.append(f"{where}: id {b['id']!r} appears more than once in the catalog")
        by_id[b["id"]] = b
        if dir_id is not None and dir_id != b["id"]:
            problems.append(f"{where}: id {b['id']!r} does not match its directory {dir_id!r}")
        props = b.get("props") or {}
        if props.get("type") != "object":
            problems.append(f"{where}: props must be an object schema")
        for p, node in walk_props(props):
            t = node.get("type")
            if t == "object" or "properties" in node:
                if node.get("additionalProperties") is not False:
                    problems.append(f"{where}: {p} is an open object (set additionalProperties: false, so a manifest cannot add props the block never renders)")
                for name in node.get("properties") or {}:
                    if name != "variant" and STYLE_NAME.search(name):
                        problems.append(f"{where}: {p}.{name} looks like a styling prop; styling comes from tokens and variants, never from content")
            if t == "string" and not any(k in node for k in ("maxLength", "enum", "const")):
                problems.append(f"{where}: {p} is an unbounded string (give it maxLength): an unbounded string has no worst case to test, so no width can be proven to fit it")
            if t == "array" and "maxItems" not in node:
                problems.append(f"{where}: {p} is an unbounded list (give it maxItems)")
            if "enum" in node and not node.get("enum"):
                problems.append(f"{where}: {p} has an empty enum")
        variants = b.get("variants") or []
        venum = ((props.get("properties") or {}).get("variant") or {}).get("enum")
        if variants and venum is not None and list(venum) != list(variants):
            problems.append(f"{where}: props.variant enum {venum} must equal variants {variants}")
        if variants and venum is None:
            problems.append(f"{where}: declares variants {variants} but props has no variant enum")
        if b.get("headingLevel") == 1 and (b.get("placement") or {}).get("position") != "first":
            problems.append(f"{where}: a level-1 block renders the page's h1, so placement.position must be 'first'")
        tone = b.get("tone") or {}
        if tone.get("allowed") and tone.get("default") not in tone["allowed"]:
            problems.append(f"{where}: tone.default {tone.get('default')!r} is not in tone.allowed")
        paths = prop_paths(props)
        for key in ("assetProps", "linkProps"):
            for ref in b.get(key) or []:
                if ref not in paths:
                    problems.append(f"{where}: {key} names {ref!r}, which is not a prop")
        for m in b.get("media") or []:
            if m.get("prop") not in paths:
                problems.append(f"{where}: media names prop {m.get('prop')!r}, which is not a prop")
            elif m.get("prop") not in (b.get("assetProps") or []):
                problems.append(f"{where}: media prop {m.get('prop')!r} must also be listed in assetProps")
    for bid, b in by_id.items():
        for other in (b.get("placement") or {}).get("notAdjacentTo") or []:
            if other not in by_id:
                problems.append(f"{bid}: placement.notAdjacentTo names unknown block {other!r}")
    return problems, by_id


# ─── manifest ────────────────────────────────────────────────────────────────

PLACEHOLDER = re.compile(r"\b(TODO|TBD|TBC|XXX|FIXME)\b|lorem ipsum|\{\{[^}]*\}\}", re.IGNORECASE)
PLACEHOLDER_CASED = re.compile(r"\b(TODO|TBD|TBC|XXX|FIXME)\b")  # upper-case words only: 'Todos Santos' is a place
DARK = {"inverse", "media"}
# The widest a slot draws at 2x, in source pixels: below this the image is upscaled
# somewhere on the device matrix. Full-bleed is capped at 2560 (a QHD desktop at 1x).
SLOT_MIN_SRC = {"full": 2560, "wide": 2880, "content": 2304, "half-content": 1152, "third-content": 768}


def _get(props, path):
    """Values at an assetProps-style path (list[] fans out)."""
    cur = [props]
    for part in path.split("."):
        nxt = []
        is_list = part.endswith("[]")
        key = part[:-2] if is_list else part
        for c in cur:
            if isinstance(c, dict) and key in c:
                v = c[key]
                if is_list and isinstance(v, list):
                    nxt.extend(v)
                elif not is_list:
                    nxt.append(v)
        cur = nxt
    return cur


def _strings(value, path):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _strings(v, f"{path}[{i}]")


def check_manifest(manifest, blocks, manifest_schema):
    problems, warnings = [], []
    for e in validate(manifest_schema, manifest):
        problems.append(f"manifest {e}")
    if problems:
        return problems, warnings
    assets = manifest.get("assets", {})
    paths = [p["path"] for p in manifest["pages"]]
    for dup in sorted({p for p in paths if paths.count(p) > 1}):
        problems.append(f"page path {dup} appears more than once")
    decorative_ok = set()
    content_use = set()
    for page in manifest["pages"]:
        where = f"page {page['path']}"
        seq = page["blocks"]
        level1 = [i for i, bl in enumerate(seq) if blocks.get(bl["type"], {}).get("headingLevel") == 1]
        for i, bl in enumerate(seq):
            b = blocks.get(bl["type"])
            at = f"{where} block {i + 1} ({bl['type']})"
            if b is None:
                problems.append(f"{at}: no such block in the catalog")
                continue
            place = b.get("placement") or {}
            if place.get("position") == "first" and i != 0:
                problems.append(f"{at}: must be the first block on the page")
            if place.get("position") == "last" and i != len(seq) - 1:
                problems.append(f"{at}: must be the last block on the page")
            variants = b.get("variants") or []
            if "variant" in bl and bl["variant"] not in variants:
                problems.append(f"{at}: variant {bl['variant']!r} is not one of {variants}")
            if "variant" in bl and (bl.get("props") or {}).get("variant", bl["variant"]) != bl["variant"]:
                problems.append(f"{at}: variant and props.variant disagree")
            tone = b.get("tone") or {}
            if "tone" in bl:
                if tone.get("locked") and bl["tone"] != tone.get("default"):
                    problems.append(f"{at}: tone is locked to {tone.get('default')!r}")
                elif tone.get("allowed") and bl["tone"] not in tone["allowed"]:
                    problems.append(f"{at}: tone {bl['tone']!r} is not one of {tone['allowed']}")
            for e in validate(b["props"], bl["props"], b["props"], "props"):
                problems.append(f"{at}: {e}")
            for spath, s in _strings(bl["props"], "props"):
                if PLACEHOLDER_CASED.search(s) or re.search(r"lorem ipsum|\{\{[^}]*\}\}", s, re.IGNORECASE):
                    problems.append(f"{at}: {spath} holds placeholder text {s[:40]!r}: an unknown fact goes in ownerTodos, never in a rendered field")
            for ap in b.get("assetProps") or []:
                for key in _get(bl["props"], ap):
                    if key not in assets:
                        problems.append(f"{at}: {ap} names asset {key!r}, which the manifest does not have")
            media = {m["prop"]: m for m in b.get("media") or []}
            for mprop, m in media.items():
                for key in _get(bl["props"], mprop):
                    a = assets.get(key)
                    if not a:
                        continue
                    if m["slot"] == "full":
                        decorative_ok.add(key)
                    else:
                        content_use.add(key)
                    need = SLOT_MIN_SRC.get(m["slot"])
                    if need and a["width"] < need:
                        warnings.append(f"{at}: asset {key!r} is {a['width']}px wide; a {m['slot']} slot draws up to {need}px at 2x, so it will be upscaled (blurry) on large screens")
                    num, den = (int(x) for x in m["ratio"].split(" / "))
                    frame, src = num / den, a["width"] / a["height"]
                    kept = min(frame, src) / max(frame, src)
                    if kept < 0.6:
                        warnings.append(f"{at}: asset {key!r} ({a['width']}×{a['height']}) loses {round((1 - kept) * 100)}% of its area in a {m['ratio']} frame; set its focal point or use a better-shaped crop")
            for lp in b.get("linkProps") or []:
                for href in _get(bl["props"], lp):
                    if isinstance(href, str) and href.startswith("/") and not href.startswith("//"):
                        target = href.split("#")[0].split("?")[0]
                        if target and target not in paths:
                            problems.append(f"{at}: {lp} links to {href}, which is not a page in this manifest")
            if i > 0:
                prev = seq[i - 1]
                pb = blocks.get(prev["type"])
                if pb is not None:
                    na = set(place.get("notAdjacentTo") or []) | {
                        x for x in ((pb.get("placement") or {}).get("notAdjacentTo") or []) if x == bl["type"]
                    }
                    if prev["type"] in na or bl["type"] in ((pb.get("placement") or {}).get("notAdjacentTo") or []):
                        problems.append(f"{at}: may not sit directly after {prev['type']}")
                    tone_here = bl.get("tone", tone.get("default"))
                    tone_prev = prev.get("tone", (pb.get("tone") or {}).get("default"))
                    if tone_here in DARK and tone_prev in DARK:
                        problems.append(f"{at}: two dark bands back to back ({tone_prev} then {tone_here}) read as one; put a light block between them")
        if not seq or not level1 or level1[0] != 0:
            problems.append(f"{where}: the first block must be the page's level-1 block (it renders the only h1)")
        if len(level1) > 1:
            problems.append(f"{where}: {len(level1)} level-1 blocks; a page has exactly one h1")
        counts = {}
        for bl in seq:
            counts[bl["type"]] = counts.get(bl["type"], 0) + 1
        for t, n in counts.items():
            mx = (blocks.get(t, {}).get("placement") or {}).get("maxPerPage")
            if mx and n > mx:
                problems.append(f"{where}: {n} × {t}, more than its maxPerPage {mx}")
    for key in sorted(content_use):
        if assets[key]["alt"] == "":
            problems.append(f"asset {key!r} has empty alt but is shown as content; write the alt while looking at the image (\"\" is only for a decorative backdrop)")
    for key, a in assets.items():
        if PLACEHOLDER_CASED.search(a.get("alt", "")):
            problems.append(f"asset {key!r}: alt holds placeholder text")
    unused = set(assets) - decorative_ok - content_use - {
        k for page in manifest["pages"] for bl in page["blocks"] for ap in (blocks.get(bl["type"], {}).get("assetProps") or []) for k in _get(bl["props"], ap)
    }
    for key in sorted(unused):
        warnings.append(f"asset {key!r} is not used by any block")
    return problems, warnings


# ─── tokens ──────────────────────────────────────────────────────────────────

# (foreground role, background role, minimum ratio, why). Every pair a block can
# put on screen through layout.css's tones.
ROLE_PAIRS = [
    ("ink", "canvas", 4.5, "body text on the page"),
    ("ink", "surface", 4.5, "body text on a surface band or card"),
    ("ink-muted", "canvas", 4.5, "secondary text on the page"),
    ("ink-muted", "surface", 4.5, "secondary text on a surface"),
    ("accent", "canvas", 4.5, "links on the page"),
    ("accent", "surface", 4.5, "links on a surface"),
    ("on-accent", "accent", 4.5, "button labels"),
    ("on-inverse", "inverse", 4.5, "text on an inverse band"),
    ("on-inverse-muted", "inverse", 4.5, "secondary text on an inverse band"),
    ("inverse", "on-inverse", 4.5, "a button label on an inverse band (the accent pair flips there)"),
    ("focus", "canvas", 3.0, "focus ring on the page (SC 1.4.11)"),
    ("focus", "surface", 3.0, "focus ring on a surface (SC 1.4.11)"),
    ("on-inverse", "inverse", 3.0, "focus ring on an inverse band (SC 1.4.11)"),
]


def _roles(block):
    return {m.group(1): m.group(2) for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{3,8})\s*;", block)}


def token_themes(css):
    """{'light': roles, 'dark': roles}: the first :root block in @layer tokens, then
    the dark overrides laid over it."""
    code = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    light_m = re.search(r":root\s*\{([^}]*)\}", code)
    dark_m = re.search(r':root\[data-theme="dark"\]\s*\{([^}]*)\}', code)
    light = _roles(light_m.group(1)) if light_m else {}
    dark = dict(light, **_roles(dark_m.group(1))) if dark_m else {}
    return {"light": light, "dark": dark}


def check_tokens(css):
    sys.path.insert(0, HERE)
    from contrast_ratio import contrast_ratio  # same math as the plugin's contrast checker

    problems, rows = [], []
    themes = token_themes(css)
    if not themes["light"]:
        return ["no colour roles found in a :root block"], rows
    code = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    media_m = re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*:root[^{]*\{([^}]*)\}", code)
    attr_m = re.search(r':root\[data-theme="dark"\]\s*\{([^}]*)\}', code)
    if media_m and attr_m and _roles(media_m.group(1)) != _roles(attr_m.group(1)):
        problems.append("dark: the prefers-color-scheme block and the [data-theme=\"dark\"] block disagree; they are one theme written twice and must match")
    for theme, roles in themes.items():
        if not roles:
            problems.append(f"{theme}: no [data-theme=\"dark\"] roles found (a site that supports dark mode needs them)")
            continue
        for fg, bg, need, why in ROLE_PAIRS:
            if fg not in roles or bg not in roles:
                problems.append(f"{theme}: --{fg} or --{bg} is missing")
                continue
            r = contrast_ratio(roles[fg], roles[bg])
            rows.append((theme, fg, bg, r, need, why))
            if r < need:
                problems.append(f"{theme}: --{fg} {roles[fg]} on --{bg} {roles[bg]} is {r:.2f}:1, needs {need}:1 ({why})")
    return problems, rows


# ─── fixtures ────────────────────────────────────────────────────────────────

WORDS = "breakfast counter biscuits coffee morning griddle neighbours table window kitchen recipe Saturday harbour bakery orchard".split()
LONG = "Donaudampfschifffahrtsgesellschaftskapitänswitwe"
RTL = "جاءت المنضدة مع المبنى وما زالت بطاقات الوصفات في العلبة نفسها"


def _text(n, mode):
    if n <= 0:
        return ""
    if mode == "long" and n >= 12:
        return (LONG * (n // len(LONG) + 1))[:n]
    if mode == "rtl":
        return (RTL + " ") * (n // (len(RTL) + 1) + 1)
    out, i = [], 0
    while len(" ".join(out)) < n:
        out.append(WORDS[i % len(WORDS)])
        i += 1
    s = " ".join(out)[:n].rstrip()
    return s[0].upper() + s[1:] if s else s


def gen(schema, mode, path, block):
    t = schema.get("type")
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0 if mode == "min" else -1]
    if path in (block.get("assetProps") or []):
        return "stress-photo"
    if path in (block.get("linkProps") or []):
        return "#top"
    if t == "object":
        out = {}
        req = set(schema.get("required", []))
        for k, v in (schema.get("properties") or {}).items():
            if mode == "min" and k not in req:
                continue
            if k == "variant":
                continue
            out[k] = gen(v, mode, f"{path}.{k}" if path else k, block)
        return out
    if t == "array":
        n = schema.get("minItems", 1) if mode == "min" else schema.get("maxItems", 3)
        item_path = f"{path}[]"
        return [gen(schema.get("items", {"type": "string", "maxLength": 20}), mode, item_path, block) for _ in range(max(n, 0))]
    if t == "string":
        if "pattern" in schema:
            if "%" in schema["pattern"]:
                return "50% 50%"
            return "stress-photo" if "a-z" in schema["pattern"] else ""
        lo, hi = schema.get("minLength", 1), schema.get("maxLength", 40)
        s = _text(lo if mode == "min" else hi, mode)
        return s[:hi] if len(s) > hi else s.ljust(lo, "x")
    if t in ("integer", "number"):
        return schema.get("minimum", 0) if mode == "min" else schema.get("maximum", 100)
    if t == "boolean":
        return mode != "min"
    return None


def _may_follow(blocks, first, second):
    """True when `second` may sit directly after `first` (both directions of notAdjacentTo, and tone)."""
    a, b = blocks[first], blocks[second]
    if second in ((a.get("placement") or {}).get("notAdjacentTo") or []):
        return False
    if first in ((b.get("placement") or {}).get("notAdjacentTo") or []):
        return False
    return not ((a.get("tone") or {}).get("default") in DARK and (b.get("tone") or {}).get("default") in DARK)


def make_fixtures(blocks):
    pages = []
    for bid, b in sorted(blocks.items()):
        for mode in ("min", "max", "long", "rtl"):
            blk = {"type": bid, "props": gen(b["props"], mode, "", b)}
            if b.get("variants"):
                blk["variant"] = b["variants"][0 if mode == "min" else -1]
                if "variant" in (b["props"].get("properties") or {}):
                    blk["props"]["variant"] = blk["variant"]
            seq = [blk]
            if b.get("headingLevel") != 1:
                lead = next((x for x, xb in sorted(blocks.items()) if xb.get("headingLevel") == 1), None)
                if lead:
                    seq.insert(0, {"type": lead, "props": gen(blocks[lead]["props"], "min", "", blocks[lead])})
                    if not _may_follow(blocks, lead, bid):
                        spacer = next(
                            (x for x in sorted(blocks) if blocks[x].get("headingLevel") != 1 and x != bid and _may_follow(blocks, lead, x) and _may_follow(blocks, x, bid)),
                            None,
                        )
                        if spacer:
                            seq.insert(1, {"type": spacer, "props": gen(blocks[spacer]["props"], "min", "", blocks[spacer])})
            pages.append(
                {
                    "path": f"/stress/{bid}/{mode}/",
                    "title": f"Stress: {bid} at {mode}",
                    "description": f"The {bid} block rendered at its {mode} content, for the device matrix and visual baselines.",
                    "blocks": seq,
                }
            )
    return {
        "siteId": "stress-fixtures",
        "lang": "en",
        "business": {"name": "Stress fixtures", "schemaType": "LocalBusiness"},
        "assets": {"stress-photo": {"src": "stress-photo.jpg", "alt": "A test photograph", "width": 2560, "height": 1600, "provenance": "generated"}},
        "pages": pages,
    }


# ─── self-test ───────────────────────────────────────────────────────────────


def self_test():
    failed = 0

    def row(ok, label, detail=""):
        nonlocal failed
        if not ok:
            failed += 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}{f' — {detail}' if detail else ''}")

    bschema = load_json(os.path.join(KIT, "block.schema.json"))
    mschema = load_json(os.path.join(KIT, "site-manifest.schema.json"))
    kit_catalog = os.path.join(KIT, "catalog.json")
    probs, blocks = check_catalog(kit_catalog, bschema)
    row(not probs and len(blocks) >= 5, f"positive: the starter catalog passes ({len(blocks)} blocks)", "; ".join(probs[:2]))
    example = load_json(os.path.join(KIT, "example.manifest.json"))
    mp, mw = check_manifest(example, blocks, mschema)
    row(not mp, "positive: the example manifest passes", "; ".join(mp[:2]))
    fx = make_fixtures(blocks)
    fp, _ = check_manifest(fx, blocks, mschema)
    row(not fp and len(fx["pages"]) == 4 * len(blocks), f"positive: generated stress fixtures pass ({len(fx['pages'])} pages)", "; ".join(fp[:2]))
    hero_max = next(p for p in fx["pages"] if p["path"] == "/stress/hero-full/max/")["blocks"][0]["props"]
    row(len(hero_max["title"]) == 60 and len(hero_max["actions"]) == 2, "fixtures: max mode fills strings to maxLength and lists to maxItems", json.dumps(hero_max)[:80])
    hero_long = next(p for p in fx["pages"] if p["path"] == "/stress/hero-full/long/")["blocks"][0]["props"]
    row(" " not in hero_long["title"], "fixtures: long mode puts one unbreakable word in each string")

    with open(os.path.join(KIT, "tokens.css"), encoding="utf-8") as f:
        css = f.read()
    tp, trows = check_tokens(css)
    row(not tp and len(trows) == 2 * len(ROLE_PAIRS), f"positive: tokens.css passes every role pairing, light and dark ({len(trows)} pairs)", "; ".join(tp[:2]))
    bad, _ = check_tokens(css.replace("--ink-muted: #55565e;", "--ink-muted: #9a9aa0;", 1))
    row(any("--ink-muted" in b and "light" in b for b in bad), "must fail (tokens): a muted ink too light for the canvas")
    bad, _ = check_tokens(css.replace("--focus: #9db9ff;\n  }", "--focus: #2a2b33;\n  }"))
    row(any("dark: --focus" in b for b in bad), "must fail (tokens): a dark-theme focus ring that vanishes on the dark canvas")
    bad, _ = check_tokens(css.replace("--accent: #8fb0ff;", "--accent: #8fb1ff;", 1))
    row(any("disagree" in b for b in bad), "must fail (tokens): the two copies of the dark theme drifted apart")

    tmp = tempfile.mkdtemp(prefix="block-site-check-")
    try:

        kit_bundle = load_json(kit_catalog)

        def write_dir_form(d, rename=None):
            """The same contracts as a directory of <id>/block.json, optionally misfiled."""
            for b in kit_bundle["blocks"]:
                sub = os.path.join(d, (rename or {}).get(b["id"], b["id"]))
                os.makedirs(sub)
                with open(os.path.join(sub, "block.json"), "w", encoding="utf-8") as f:
                    json.dump(b, f)

        d = os.path.join(tmp, "dir-form")
        write_dir_form(d)
        got, dblocks = check_catalog(d, bschema)
        row(not got and set(dblocks) == set(blocks), f"positive: the same catalog as a directory of <id>/block.json passes ({len(dblocks)} blocks)", "; ".join(got[:2]))
        d = os.path.join(tmp, "dir-misfiled")
        write_dir_form(d, rename={"cta-banner": "cta"})
        got, _ = check_catalog(d, bschema)
        row(any("does not match its directory" in g for g in got), "must fail (catalog): id does not match its directory")

        def catalog_case(label, mutate, want):
            bundle = copy.deepcopy(kit_bundle)
            mutate(bundle)
            p = os.path.join(tmp, re.sub(r"\W+", "-", label) + ".json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(bundle, f)
            got, _ = check_catalog(p, bschema)
            hit = any(want in g for g in got)
            row(hit, f"must fail (catalog): {label}", "" if hit else f"expected {want!r}, got {got[:2] or 'nothing'}")

        def edit(bid, fn):
            return lambda bundle: fn(next(b for b in bundle["blocks"] if b["id"] == bid))

        catalog_case("a catalog file with no blocks list", lambda c: c.pop("blocks"), '"blocks" list')
        catalog_case("the same id twice", lambda c: c["blocks"].append(copy.deepcopy(c["blocks"][-1])), "appears more than once")
        catalog_case("schema shape (summary missing)", edit("cta-banner", lambda b: b.pop("summary")), "missing required 'summary'")
        catalog_case("open props object", edit("cta-banner", lambda b: b["props"]["properties"]["action"].pop("additionalProperties")), "open object")
        catalog_case("unbounded string", edit("cta-banner", lambda b: b["props"]["properties"]["heading"].pop("maxLength")), "unbounded string")
        catalog_case("unbounded list", edit("features-grid", lambda b: b["props"]["properties"]["items"].pop("maxItems")), "unbounded list")
        catalog_case("a styling prop", edit("cta-banner", lambda b: b["props"]["properties"].update(textColor={"type": "string", "maxLength": 9})), "styling prop")
        catalog_case("variant enum differs from variants", edit("cta-banner", lambda b: b["props"]["properties"]["variant"].update(enum=["book"])), "must equal variants")
        catalog_case("level-1 block not placed first", edit("hero-full", lambda b: b["placement"].update(position="any")), "must be 'first'")
        catalog_case("assetProps names no prop", edit("story-split", lambda b: b.update(assetProps=["photo"])), "which is not a prop")
        catalog_case("media prop not in assetProps", edit("story-split", lambda b: b.update(assetProps=[])), "must also be listed in assetProps")
        catalog_case("tone default not allowed", edit("features-grid", lambda b: b["tone"].update(default="inverse")), "is not in tone.allowed")
        catalog_case("notAdjacentTo names an unknown block", edit("cta-banner", lambda b: b["placement"].update(notAdjacentTo=["hero-giant"])), "unknown block")
        catalog_case("more than three variants", edit("cta-banner", lambda b: b.update(variants=["a", "b", "c", "d"])), "more than 3")

        def manifest_case(label, mutate, want, catalog_mutate=None):
            bl = copy.deepcopy(blocks)
            if catalog_mutate:
                catalog_mutate(bl)
            m = copy.deepcopy(example)
            mutate(m)
            got, _ = check_manifest(m, bl, mschema)
            hit = any(want in g for g in got)
            row(hit, f"must fail (manifest): {label}", "" if hit else f"expected {want!r}, got {got[:2] or 'nothing'}")

        B = lambda m: m["pages"][0]["blocks"]  # noqa: E731
        manifest_case("schema shape (lang missing)", lambda m: m.pop("lang"), "missing required 'lang'")
        manifest_case("unknown block", lambda m: B(m).append({"type": "carousel", "props": {}}), "no such block")
        manifest_case("first block is not level 1", lambda m: B(m).insert(0, B(m).pop(1)), "must be the first block")
        manifest_case("two level-1 blocks", lambda m: B(m).insert(2, copy.deepcopy(B(m)[0])), "level-1 blocks")
        manifest_case("maxPerPage", lambda m: B(m).insert(3, copy.deepcopy(B(m)[3])), "more than its maxPerPage")
        manifest_case("notAdjacentTo", lambda m: B(m).insert(1, copy.deepcopy(B(m)[-1])), "may not sit directly after")
        manifest_case(
            "two dark bands in a row",
            lambda m: B(m).insert(4, {"type": "features-grid", "tone": "inverse", "props": B(m)[1]["props"]}),
            "two dark bands",
            catalog_mutate=lambda bl: bl["features-grid"]["tone"].update(allowed=["canvas", "surface", "inverse"]),
        )
        manifest_case("variant not in the catalog", lambda m: B(m)[0].update(variant="carousel"), "is not one of")
        manifest_case("locked tone changed", lambda m: B(m)[0].update(tone="canvas"), "tone is locked")
        manifest_case("tone not allowed", lambda m: B(m)[1].update(tone="media"), "is not one of")
        manifest_case("prop over its maxLength", lambda m: B(m)[0]["props"].update(title="x" * 61), "more than 60")
        manifest_case("unknown prop", lambda m: B(m)[0]["props"].update(subtitle="Extra"), "unknown property 'subtitle'")
        manifest_case("too many items", lambda m: B(m)[1]["props"].update(items=B(m)[1]["props"]["items"] * 3), "more than 6")
        manifest_case("placeholder text", lambda m: B(m)[1]["props"]["items"][0].update(body="TODO write this card"), "placeholder text")
        manifest_case("unknown asset", lambda m: B(m)[2]["props"].update(image="kitchen"), "does not have")
        manifest_case("empty alt on a content image", lambda m: m["assets"]["counter"].update(alt=""), "empty alt")
        manifest_case("internal link to a missing page", lambda m: B(m)[0]["props"]["actions"][0].update(href="/specials/"), "not a page in this manifest")
        manifest_case("duplicate page path", lambda m: m["pages"].append(copy.deepcopy(m["pages"][0])), "appears more than once")
        mm = copy.deepcopy(example)
        mm["assets"]["counter"]["width"] = 640
        _, w = check_manifest(mm, blocks, mschema)
        row(any("will be upscaled" in x for x in w), "warns: an image too small for its slot at 2x")
        mm = copy.deepcopy(example)
        mm["assets"]["counter"].update(width=600, height=1600)
        _, w = check_manifest(mm, blocks, mschema)
        row(any("loses" in x for x in w), "warns: a crop that loses most of the image")
        tidy = copy.deepcopy(example)
        B(tidy)[1]["props"]["items"][0]["body"] = "Todos Santos is a town, not a placeholder."
        p2, _ = check_manifest(tidy, blocks, mschema)
        row(not any("placeholder" in x for x in p2), "placeholder check is case-aware: 'Todos Santos' is real copy")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"block_site_check --self-test: {'FAILED (%d row(s))' % failed if failed else 'OK'}")
    return 1 if failed else 0


# ─── cli ─────────────────────────────────────────────────────────────────────


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[0]
    bschema = load_json(os.path.join(KIT, "block.schema.json"))
    mschema = load_json(os.path.join(KIT, "site-manifest.schema.json"))
    if cmd == "catalog" and len(argv) == 2:
        probs, blocks = check_catalog(argv[1], bschema)
        for p in probs:
            print(f"  ✗ {p}")
        print(f"block_site_check catalog: {'FAILED, %d problem(s)' % len(probs) if probs else 'OK, %d block(s)' % len(blocks)}")
        return 1 if probs else 0
    if cmd == "manifest" and len(argv) == 4 and argv[2] == "--catalog":
        cprobs, blocks = check_catalog(argv[3], bschema)
        if cprobs:
            for p in cprobs:
                print(f"  ✗ catalog: {p}")
            print("block_site_check manifest: the catalog itself fails; fix it first")
            return 1
        probs, warns = check_manifest(load_json(argv[1]), blocks, mschema)
        for w in warns:
            print(f"  ! {w}")
        for p in probs:
            print(f"  ✗ {p}")
        print(f"block_site_check manifest: {'FAILED, %d problem(s)' % len(probs) if probs else 'OK'}{', %d warning(s)' % len(warns) if warns else ''}")
        return 1 if probs else 0
    if cmd == "tokens" and len(argv) == 2:
        with open(argv[1], encoding="utf-8") as f:
            probs, rows = check_tokens(f.read())
        for theme, fg, bg, r, need, why in rows:
            print(f"  {'ok' if r >= need else '✗ '} {theme:5} --{fg} on --{bg}: {r:.2f}:1 (needs {need}:1, {why})")
        for p in probs:
            print(f"  ✗ {p}")
        print(f"block_site_check tokens: {'FAILED, %d problem(s)' % len(probs) if probs else 'OK, %d pairs' % len(rows)}")
        return 1 if probs else 0
    if cmd == "fixtures" and len(argv) == 4 and argv[2] == "--out":
        cprobs, blocks = check_catalog(argv[1], bschema)
        if cprobs:
            print("block_site_check fixtures: the catalog fails its own check; run `catalog` first")
            return 1
        fx = make_fixtures(blocks)
        with open(argv[3], "w", encoding="utf-8") as f:
            json.dump(fx, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"block_site_check fixtures: wrote {len(fx['pages'])} stress pages to {argv[3]} (render them, then run device_matrix.mjs)")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
