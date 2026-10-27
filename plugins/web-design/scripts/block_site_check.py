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
                                 facts a block requires, placeholder text, asset,
                                 link and anchor references, unsafe link schemes,
                                 overlapping hours, and photos too small for the
                                 box they are drawn in at 2x
  tokens FILE                    check every colour-role pairing in tokens.css,
                                 light and dark, against WCAG AA (text 4.5:1,
                                 control edges and focus rings 3:1), light copy
                                 over the photo scrim on a white pixel, the 2.5x
                                 type-scale bound and the font stack, reading the
                                 values from the file itself (hex, rgb(), hsl(),
                                 oklch(), oklab()) so there is no second copy
  fixtures CATALOG --out FILE    write a stress manifest from the catalog's own
                                 bounds: every block at its minimum, its maximum,
                                 one unbreakable word at full length, and RTL
                                 text, under the longest header the schema allows;
                                 and a near-white stress photo beside FILE. Render
                                 it (block_site_render.py), then run
                                 device_matrix.mjs on it.
  --self-test                    break each rule in a copy of the starter kit and
                                 require it to be reported; require the kit
                                 itself (catalog, example manifest, fixtures) to
                                 pass.

Exit: 0 clean (warnings may print), 1 problems, 2 usage.
"""

from __future__ import annotations

import copy
import datetime
import json
import math
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
    if isinstance(t, list):
        return any(_is_type(value, x) for x in t)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, TYPES[t])


def _same(a, b):
    """JSON equality: true is not 1, and 1 is not true (Python says both are)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (list, dict)) or isinstance(b, (list, dict)):
        return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    return a == b


_RX = {}


def _rx(pattern):
    """A JSON Schema pattern as Python should read it: ASCII classes (\\d is 0-9, not
    any script's digits) and a final $ that means the very end, not 'before a
    trailing newline'."""
    if pattern not in _RX:
        _RX[pattern] = re.compile(re.sub(r"(?<!\\)\$$", r"\\Z", pattern), re.ASCII)
    return _RX[pattern]


EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+\Z")


def validate(schema, value, root=None, path="$"):
    """Return a list of 'path: message' strings. Supports: type, properties,
    required, additionalProperties (bool or schema), propertyNames, enum, const,
    minLength, maxLength, pattern, items, minItems, maxItems, uniqueItems,
    minimum, maximum, $ref (#/$defs/...), format: email. Booleans never equal
    numbers, and patterns read ASCII to the true end of the string."""
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
    if "enum" in schema and not any(_same(value, e) for e in schema["enum"]):
        errs.append(f"{path}: {json.dumps(value)} is not one of {json.dumps(schema['enum'])}")
    if "const" in schema and not _same(value, schema["const"]):
        errs.append(f"{path}: must be {json.dumps(schema['const'])}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errs.append(f"{path}: shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errs.append(f"{path}: {len(value)} characters, more than {schema['maxLength']}")
        if "pattern" in schema and not _rx(schema["pattern"]).search(value):
            errs.append(f"{path}: {json.dumps(value)} does not match {schema['pattern']}")
        if schema.get("format") == "email" and not EMAIL.match(value):
            errs.append(f"{path}: {json.dumps(value)} is not an email address")
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
# variants, never to content. Tone and space belong on the block instance.
STYLE_NAME = re.compile(
    r"^(style|styles|class|classes|classname|css|theme|colou?r|background|bg|font|fontsize|fontfamily|fontweight|"
    r"padding|margin|gap|width|height|align|textalign|justify|radius|shadow|opacity|zindex|accent|columns|cols|"
    r"size|spacing|layout|fullwidth|maxwidth|minwidth|textsize|tone|space)$|"
    r"(colou?r|classname|css|style|fontsize|textsize|padding|margin|radius|shadow|spacing|maxwidth|minwidth)$",
    re.IGNORECASE,
)
# The JSON Schema a props contract may use. Anything else ($ref, anyOf, oneOf,
# allOf, not, if, patternProperties…) is a branch the checker would have to
# follow to prove the props closed and bounded, so it is refused instead.
PROPS_KEYWORDS = {
    "type", "properties", "required", "additionalProperties", "items", "minItems", "maxItems", "uniqueItems",
    "minLength", "maxLength", "pattern", "format", "enum", "const", "minimum", "maximum", "description", "title",
    "default", "examples",
}


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
    if not isinstance(schema, dict):
        return
    for k, v in (schema.get("properties") or {}).items():
        yield from walk_props(v, f"{path}.{k}")
    if isinstance(schema.get("items"), dict):
        yield from walk_props(schema["items"], f"{path}[]")


def prop_paths(schema, path=""):
    """Every addressable prop path, in the assetProps notation (a.b, list[].c)."""
    out = set()
    for k, v in (schema.get("properties") or {}).items():
        if not isinstance(v, dict):
            continue
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
        if "variant" in (props.get("properties") or {}):
            problems.append(f"{where}: props declares 'variant'; the variant lives on the block instance (variants), never in props")
        for p, node in walk_props(props):
            if not isinstance(node, dict):
                problems.append(f"{where}: {p} is not a schema object")
                continue
            unknown = sorted(set(node) - PROPS_KEYWORDS)
            if unknown:
                problems.append(f"{where}: {p} uses {', '.join(unknown)}, which this checker cannot follow, so it cannot prove the props closed and bounded; write the schema out in the supported subset")
            t = node.get("type")
            if isinstance(t, list):
                problems.append(f"{where}: {p} has a list of types {t}; give it one type (an optional prop is left out of required, never typed null)")
                continue
            if "items" in node and not isinstance(node["items"], dict):
                problems.append(f"{where}: {p}.items must be one schema")
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
        if b.get("headingLevel") == 1 and (b.get("placement") or {}).get("position") != "first":
            problems.append(f"{where}: a level-1 block renders the page's h1, so placement.position must be 'first'")
        tone = b.get("tone") or {}
        if tone.get("allowed") and tone.get("default") not in tone["allowed"]:
            problems.append(f"{where}: tone.default {tone.get('default')!r} is not in tone.allowed")
        paths = prop_paths(props)
        for v in b.get("variantLinks") or {}:
            if v not in (b.get("variants") or []):
                problems.append(f"{where}: variantLinks names {v!r}, which is not one of its variants")
        for key in ("assetProps", "linkProps", "endpointProps"):
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

PLACEHOLDER_CASED = re.compile(r"\b(TODO|TBD|TBC|XXX|FIXME)\b")  # upper-case words only: 'Todos Santos' is a place
PLACEHOLDER_ANY = re.compile(r"lorem ipsum|\{\{[^}]*\}\}", re.IGNORECASE)
DARK = {"inverse", "media"}
# How wide a frame on each grid line can be drawn, in CSS px, when its contract
# gives no maxWidth: full is capped at 1280 (2560 source pixels, a QHD desktop at
# 1x), the others are layout.css's line widths and halves of them.
SLOT_MAX_WIDTH = {"full": 1280, "wide": 1440, "content": 1152, "half-content": 576, "third-content": 384}
DENSITY = 2  # sources are sized for 2x; above 2x the eye cannot tell, and apple.com caps there too
PORTRAIT_MAX_WIDTH = 480  # the renderer serves a portrait crop at (max-width: 30em) and (orientation: portrait)
ENDPOINT = re.compile(r"^(https://[^\s#]+|/[^\s#]*)\Z")
SAFE_HREF = re.compile(r"^(/|#|https://|mailto:[^@\s]+@|tel:\+?[0-9][0-9 ()-]{3,})")
DAY_ORDER = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
EXTENSION = re.compile(r"\s*(?:ext\.?|x)\s*([0-9]{1,6})\Z", re.IGNORECASE)
# Primary language subtags written right to left; a script subtag (-Arab, -Latn…) wins.
RTL_LANGS = {"ar", "arc", "ckb", "dv", "fa", "he", "ks", "ps", "sd", "ug", "ur", "yi"}


def phone_parts(phone):
    """(number, extension) of a phone as printed: number keeps a leading + and its
    digits only, so tel: dials exactly it; extension is its digits or ''."""
    m = EXTENSION.search(phone)
    ext, main = (m.group(1), phone[: m.start()]) if m else ("", phone)
    digits = re.sub(r"[^0-9]", "", main)
    return ("+" if main.strip().startswith("+") else "") + digits, ext


def same_number(tel_href, phone):
    """True when a tel: link dials the business's number: the same digits, allowing
    one side to carry the country code the other leaves out."""
    a = re.sub(r"[^0-9]", "", re.split(r"[;,]", tel_href[4:], maxsplit=1)[0])
    b = re.sub(r"[^0-9]", "", phone_parts(phone)[0])
    return min(len(a), len(b)) >= 7 and (a.endswith(b) or b.endswith(a))


def text_direction(lang, explicit=None):
    """The dir a page gets: the manifest's own, else the language's script."""
    if explicit:
        return explicit
    parts = lang.split("-")
    scripts = {p.title() for p in parts[1:] if len(p) == 4}
    if scripts & {"Arab", "Hebr", "Thaa", "Syrc", "Nkoo", "Adlm", "Rohg"}:
        return "rtl"
    if scripts:
        return "ltr"
    return "rtl" if parts[0].lower() in RTL_LANGS else "ltr"


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


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def check_hours(business):
    """Weekly hours that cannot be rendered truthfully: an empty or overlapping window."""
    problems = []
    windows = {d: [] for d in DAY_ORDER}
    for i, h in enumerate(business.get("hours") or []):
        o, c = _minutes(h["opens"]), _minutes(h["closes"])
        if o == c:
            problems.append(
                f"business.hours[{i}]: opens and closes at the same time ({h['opens']}); leave a closed day out, "
                "or write open all day as 00:00 to 23:59"
            )
            continue
        for d in h["days"]:
            # A window past midnight runs to the end of its day, then on into the next.
            spans = [(d, o, c if c > o else 24 * 60)]
            if c < o:
                spans.append((DAY_ORDER[(DAY_ORDER.index(d) + 1) % 7], 0, c))
            for day, start, end in spans:
                for j, (o2, e2) in windows[day]:
                    if j != i and start < e2 and o2 < end:
                        problems.append(f"business.hours[{i}]: {day} overlaps business.hours[{j}]")
                windows[day].append((i, (start, end)))
    seen = set()
    for i, sp in enumerate(business.get("specialHours") or []):
        try:
            datetime.date.fromisoformat(sp["date"])
        except ValueError:
            problems.append(f"business.specialHours[{i}]: {sp['date']} is not a real date")
            continue
        if sp["date"] in seen:
            problems.append(f"business.specialHours[{i}]: {sp['date']} is listed twice")
        seen.add(sp["date"])
        timed = "opens" in sp or "closes" in sp
        if sp.get("closed") and timed:
            problems.append(f"business.specialHours[{i}]: closed and opening times at once")
        elif not sp.get("closed") and not ("opens" in sp and "closes" in sp):
            problems.append(f"business.specialHours[{i}]: give closed: true, or both opens and closes")
        elif timed and sp["opens"] == sp["closes"]:
            problems.append(f"business.specialHours[{i}]: opens and closes at the same time")
    return problems


def _need_scale(width, height, box_w, box_h):
    """How far a width×height source is enlarged to cover a box_w×box_h box at 2x."""
    return max(DENSITY * box_w / width, DENSITY * box_h / height)


def check_manifest(manifest, blocks, manifest_schema, today=None):
    problems, warnings = [], []
    for e in validate(manifest_schema, manifest):
        problems.append(f"manifest {e}")
    if problems:
        return problems, warnings
    today = today or datetime.date.today().isoformat()
    business = manifest["business"]
    assets = manifest.get("assets", {})
    paths = [p["path"] for p in manifest["pages"]]
    for dup in sorted({p for p in paths if paths.count(p) > 1}):
        problems.append(f"page path {dup} appears more than once")
    problems += check_hours(business)
    if business.get("phone"):
        number, _ext = phone_parts(business["phone"])
        if not 7 <= len(number.lstrip("+")) <= 15:
            problems.append(
                f"business.phone {business['phone']!r} has {len(number.lstrip('+'))} digits; a number has 7 to 15 "
                "(write a vanity number in digits, and an extension as 'ext. 12')"
            )
    for i, sp in enumerate(business.get("specialHours") or []):
        if sp["date"] < today:
            warnings.append(f"business.specialHours[{i}]: {sp['date']} ({sp['label']}) has passed; remove it")

    def check_href(at, where, href, anchors):
        if not isinstance(href, str):
            return
        if not SAFE_HREF.match(href):
            problems.append(f"{at}: {where} is {href[:60]!r}; a link is a path (/…), an in-page #anchor, https://, mailto: or a tel: number")
            return
        if href.startswith("tel:"):
            # One source for the number: a typed copy goes stale when the business's changes.
            if not business.get("phone"):
                problems.append(f"{at}: {where} calls {href}, but the business facts list no phone")
            elif not same_number(href, business["phone"]):
                problems.append(f"{at}: {where} calls {href}, not the business's phone {business['phone']!r}")
            return
        if href.startswith("/") and not href.startswith("//"):
            target = href.split("#")[0].split("?")[0]
            if target and target not in paths:
                problems.append(f"{at}: {where} links to {href}, which is not a page in this manifest")
            frag = href.split("#", 1)[1] if "#" in href else ""
            page = next((p for p in manifest["pages"] if p["path"] == target), None)
            if frag and page is not None and frag not in {"main"} | {bl.get("anchor") for bl in page["blocks"]}:
                problems.append(f"{at}: {where} links to {href}, but {target} has no anchor {frag!r}")
        elif href.startswith("#") and anchors is not None:
            if href[1:] not in anchors:
                problems.append(f"{at}: {where} links to {href}, which no block on this page has as its anchor (set the block's anchor, or link to #main)")
        elif href.startswith("#"):
            problems.append(f"{at}: {where} is an in-page link, but the header and footer are on every page; link to a path")

    chrome = manifest.get("chrome") or {}
    for key in ("nav", "footerNav"):
        for i, link in enumerate(chrome.get(key) or []):
            check_href("chrome", f"{key}[{i}].href", link["href"], None)
    if chrome.get("action"):
        check_href("chrome", "action.href", chrome["action"]["href"], None)
    if business.get("email") is None and any(
        str(link.get("href", "")).startswith("mailto:") for link in (chrome.get("nav") or []) + (chrome.get("footerNav") or [])
    ):
        warnings.append("chrome links to an email address the business facts do not list")

    for spath, s in _strings(chrome, "chrome"):
        if PLACEHOLDER_CASED.search(s) or PLACEHOLDER_ANY.search(s):
            problems.append(f"{spath} holds placeholder text {s[:40]!r}")
    decorative_ok = set()
    content_use = set()
    for page in manifest["pages"]:
        where = f"page {page['path']}"
        for key in ("title", "description"):
            if PLACEHOLDER_CASED.search(page[key]) or PLACEHOLDER_ANY.search(page[key]):
                problems.append(f"{where}: {key} holds placeholder text {page[key][:40]!r}")
        seq = page["blocks"]
        anchors = {bl["anchor"] for bl in seq if "anchor" in bl} | {"main"}
        names = [bl["anchor"] for bl in seq if "anchor" in bl]
        for dup in sorted({n for n in names if names.count(n) > 1}):
            problems.append(f"{where}: anchor {dup!r} is used more than once")
        if "main" in names:
            problems.append(f"{where}: anchor 'main' is reserved for the page's <main>")
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
            tone = b.get("tone") or {}
            if "tone" in bl:
                if tone.get("locked") and bl["tone"] != tone.get("default"):
                    problems.append(f"{at}: tone is locked to {tone.get('default')!r}")
                elif tone.get("allowed") and bl["tone"] not in tone["allowed"]:
                    problems.append(f"{at}: tone {bl['tone']!r} is not one of {tone['allowed']}")
            for fact in b.get("requires") or []:
                if not business.get(fact.split(".", 1)[1]):
                    problems.append(f"{at}: renders {fact}, which the manifest's business does not give")
            for e in validate(b["props"], bl["props"], b["props"], "props"):
                problems.append(f"{at}: {e}")
            for spath, s in _strings(bl["props"], "props"):
                if PLACEHOLDER_CASED.search(s) or PLACEHOLDER_ANY.search(s):
                    problems.append(f"{at}: {spath} holds placeholder text {s[:40]!r}: an unknown fact goes in ownerTodos, never in a rendered field")
            for ap in b.get("assetProps") or []:
                for key in _get(bl["props"], ap):
                    if key not in assets:
                        problems.append(f"{at}: {ap} names asset {key!r}, which the manifest does not have")
            for m in b.get("media") or []:
                num, den = (int(x) for x in m["ratio"].split(" / "))
                box_w = m.get("maxWidth") or SLOT_MAX_WIDTH.get(m["slot"], 1152)
                box_h = m.get("maxHeight") or box_w * den / num
                for key in _get(bl["props"], m["prop"]):
                    a = assets.get(key)
                    if not a:
                        continue
                    (decorative_ok if m["slot"] == "full" else content_use).add(key)
                    widest = max([a["width"]] + [x["width"] for x in a.get("sources") or []])
                    scale = _need_scale(widest, widest * a["height"] / a["width"], box_w, box_h)
                    if scale > 1.02:
                        warnings.append(
                            f"{at}: asset {key!r} is {a['width']}×{a['height']}; this frame is drawn up to {round(box_w)}×{round(box_h)} CSS px, "
                            f"so at 2x it is enlarged {scale:.2f}× (blurry). Supply at least {round(DENSITY * box_w)}×{round(DENSITY * box_h)} for this crop"
                        )
                    if not m.get("maxHeight"):
                        frame, src = num / den, a["width"] / a["height"]
                        kept = min(frame, src) / max(frame, src)
                        if kept < 0.6:
                            warnings.append(f"{at}: asset {key!r} ({a['width']}×{a['height']}) loses {round((1 - kept) * 100)}% of its area in a {m['ratio']} frame; set its focal point or use a better-shaped crop")
                    pk = a.get("portrait")
                    if pk:
                        pa = assets.get(pk)
                        if pa is None:
                            problems.append(f"asset {key!r}: portrait names asset {pk!r}, which the manifest does not have")
                        elif pa["height"] <= pa["width"]:
                            problems.append(f"asset {key!r}: its portrait crop {pk!r} is {pa['width']}×{pa['height']}, not portrait")
                        else:
                            (decorative_ok if m["slot"] == "full" else content_use).add(pk)
                            ps = _need_scale(pa["width"], pa["height"], PORTRAIT_MAX_WIDTH, box_h)
                            if ps > 1.02:
                                warnings.append(f"asset {pk!r}: the portrait crop is drawn up to {PORTRAIT_MAX_WIDTH}×{round(box_h)} CSS px, so at 2x it is enlarged {ps:.2f}×")
            for lp in b.get("linkProps") or []:
                for href in _get(bl["props"], lp):
                    check_href(at, lp, href, anchors)
            variant = bl.get("variant", (b.get("variants") or [None])[0])
            prefix = (b.get("variantLinks") or {}).get(variant)
            if prefix:
                for lp in b.get("linkProps") or []:
                    for href in _get(bl["props"], lp):
                        if isinstance(href, str) and not href.startswith(prefix):
                            problems.append(f"{at}: the {variant!r} variant's {lp} must be a {prefix} link, not {href[:60]!r}")
            for ep in b.get("endpointProps") or []:
                for url in _get(bl["props"], ep):
                    if isinstance(url, str) and not ENDPOINT.match(url):
                        problems.append(f"{at}: {ep} is {url[:60]!r}; a form posts to https:// or a path on this site, never an #anchor, mailto: or tel:")
            if i > 0:
                prev = seq[i - 1]
                pb = blocks.get(prev["type"])
                if pb is not None:
                    if prev["type"] in (place.get("notAdjacentTo") or []) or bl["type"] in ((pb.get("placement") or {}).get("notAdjacentTo") or []):
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
    for at, key in [("shareImage", manifest.get("shareImage"))] + [
        (f"page {p['path']}: shareImage", p.get("shareImage")) for p in manifest["pages"]
    ]:
        if not key:
            continue
        if key not in assets:
            problems.append(f"{at} names asset {key!r}, which the manifest does not have")
            continue
        content_use.add(key)
        if not manifest.get("origin"):
            problems.append(f"{at} needs origin: a link preview reads an absolute image URL")
        elif assets[key]["width"] < 1200:
            warnings.append(f"{at}: asset {key!r} is {assets[key]['width']}px wide; link previews ask for 1200px")
    for key in sorted(content_use):
        if assets[key]["alt"] == "":
            problems.append(f"asset {key!r} has empty alt but is shown as content; write the alt while looking at the image (\"\" is only for a decorative backdrop)")
    for key, a in assets.items():
        if PLACEHOLDER_CASED.search(a.get("alt", "")):
            problems.append(f"asset {key!r}: alt holds placeholder text")
        widths = [x["width"] for x in a.get("sources") or []]
        if len(widths) != len(set(widths)) or a["width"] in widths:
            problems.append(f"asset {key!r}: two srcset candidates share a width")
    for key in sorted(set(assets) - decorative_ok - content_use):
        warnings.append(f"asset {key!r} is not used by any block")
    for path, s in _strings(business, "business"):
        if PLACEHOLDER_CASED.search(s) or PLACEHOLDER_ANY.search(s):
            problems.append(f"{path} holds placeholder text {s[:40]!r}")
    return problems, warnings


# ─── tokens ──────────────────────────────────────────────────────────────────

# (foreground role, background role, minimum ratio, why). Every pair a block can
# put on screen through layout.css's tones; inverse and photo bands re-point the
# roles, so their pairs are here too.
ROLE_PAIRS = [
    ("ink", "canvas", 4.5, "body text on the page"),
    ("ink", "surface", 4.5, "body text on a surface band or card"),
    ("ink-muted", "canvas", 4.5, "secondary text on the page"),
    ("ink-muted", "surface", 4.5, "secondary text on a surface"),
    ("accent", "canvas", 4.5, "links on the page"),
    ("accent", "surface", 4.5, "links on a surface"),
    ("on-accent", "accent", 4.5, "button labels"),
    ("field-border", "canvas", 3.0, "a form control's edge on the page (SC 1.4.11)"),
    ("field-border", "surface", 3.0, "a form control's edge on a surface (SC 1.4.11)"),
    ("focus", "canvas", 3.0, "focus ring on the page (SC 1.4.11)"),
    ("focus", "surface", 3.0, "focus ring on a surface (SC 1.4.11)"),
    ("on-inverse", "inverse", 4.5, "text on an inverse band (and its focus ring)"),
    ("on-inverse-muted", "inverse", 4.5, "secondary text on an inverse band"),
    ("on-inverse", "inverse-surface", 4.5, "text in a card on an inverse band"),
    ("on-inverse-muted", "inverse-surface", 4.5, "secondary text, and a field's edge, in a card on an inverse band"),
    ("inverse", "on-inverse", 4.5, "a button label on an inverse band (the accent pair flips there)"),
]
SCRIM_INKS = [("on-inverse", 4.5, "copy on a photo"), ("on-inverse-muted", 4.5, "secondary copy on a photo")]
TYPE_SCALE_MAX = 2.5  # a step's max over its min; above this 200% zoom stops enlarging it (WCAG 1.4.4)


def _num(tok, scale=1.0):
    tok = tok.strip()
    if tok.endswith("%"):
        return float(tok[:-1]) / 100 * scale
    return float(tok)


def _oklab_to_srgb(L, a, b):
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )
    enc = lambda c: 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055  # noqa: E731
    return tuple(min(255.0, max(0.0, enc(min(1.0, max(0.0, c))) * 255)) for c in lin)


HUE_UNIT = {"deg": 1.0, "turn": 360.0, "grad": 0.9, "rad": 180 / math.pi, "": 1.0}


def _hue(tok):
    m = re.fullmatch(r"(-?[\d.]+)(deg|turn|grad|rad|)", tok.strip())
    if not m:
        raise ValueError(tok)
    return float(m.group(1)) * HUE_UNIT[m.group(2)]


def parse_color(value, roles=None, depth=0):
    """A CSS colour value to (r, g, b, alpha) in 0-255, or None if it is not one this reads.
    Reads #hex, rgb()/rgba(), hsl()/hsla(), oklch(), oklab() and var(--role), with any hue
    unit. Out-of-gamut oklch is clipped to sRGB, as a browser without a wide-gamut screen
    paints it."""
    try:
        return _parse_color(value, roles, depth)
    except (ValueError, IndexError, ZeroDivisionError):
        return None


def _parse_color(value, roles, depth):
    v = value.strip().lower()
    m = re.fullmatch(r"var\(--([a-z0-9-]+)\)", v)
    if m and roles is not None and depth < 8 and m.group(1) in roles:
        return parse_color(roles[m.group(1)], roles, depth + 1)
    m = re.fullmatch(r"#([0-9a-f]{3,8})", v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            return None
        alpha = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    m = re.fullmatch(r"(rgba?|hsla?|oklch|oklab)\((.*)\)", v)
    if not m:
        return None
    fn, args = m.group(1), m.group(2)
    alpha = 1.0
    if "/" in args:
        args, al = args.split("/", 1)
        alpha = _num(al)
    parts = [x for x in re.split(r"[\s,]+", args.strip()) if x]
    if fn.startswith("rgba") or fn == "rgb":
        if len(parts) == 4:
            alpha = _num(parts.pop())
        if len(parts) != 3:
            return None
        return tuple(_num(x, 255) for x in parts) + (alpha,)
    if fn.startswith("hsl"):
        if len(parts) == 4:
            alpha = _num(parts.pop())
        h, sat, light = _hue(parts[0]) % 360, _num(parts[1]), _num(parts[2])
        c = (1 - abs(2 * light - 1)) * sat
        x = c * (1 - abs((h / 60) % 2 - 1))
        r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h // 60) % 6]
        mm = light - c / 2
        return ((r + mm) * 255, (g + mm) * 255, (b + mm) * 255, alpha)
    if len(parts) != 3:
        return None
    L = _num(parts[0])
    if fn == "oklch":
        C, H = _num(parts[1], 0.4), _hue(parts[2])
        a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    else:
        a, b = _num(parts[1], 0.4), _num(parts[2], 0.4)
    return _oklab_to_srgb(L, a, b) + (alpha,)


def _hex(rgb):
    return "#" + "".join(f"{round(c):02x}" for c in rgb[:3])


def _roles(block):
    return {m.group(1): " ".join(m.group(2).split()) for m in re.finditer(r"--([a-z0-9-]+):\s*([^;]+);", block)}


def token_themes(css):
    """{'light': roles, 'dark': roles}: every plain :root block in file order (a later
    one overrides an earlier, as the cascade does), then every [data-theme="dark"]
    block laid over them. Values are raw text; parse_color reads colours."""
    code = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    light, dark = {}, {}
    for m in re.finditer(r"(?<![\w\])-]):root\s*\{([^}]*)\}", code):
        light.update(_roles(m.group(1)))
    for m in re.finditer(r':root\[data-theme="dark"\]\s*\{([^}]*)\}', code):
        dark.update(_roles(m.group(1)))
    return {"light": light, "dark": dict(light, **dark) if dark else {}}


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
    light = themes["light"]
    if not light.get("font-body"):
        problems.append("--font-body is missing: every page would render in the browser's default serif")
    for name, val in light.items():
        if not name.startswith("step-"):
            continue
        m = re.fullmatch(r"clamp\(\s*([\d.]+)(rem|px)\s*,.*,\s*([\d.]+)(rem|px)\s*\)", val)
        if not m:
            problems.append(f"--{name} is not a clamp(min, preferred, max) in rem or px, so its zoom range cannot be checked")
            continue
        lo = float(m.group(1)) * (16 if m.group(2) == "rem" else 1)
        hi = float(m.group(3)) * (16 if m.group(4) == "rem" else 1)
        if lo <= 0 or hi / lo > TYPE_SCALE_MAX:
            problems.append(f"--{name} grows {hi / lo:.2f}× from its min to its max; above {TYPE_SCALE_MAX}× text stops growing at 200% zoom (WCAG 1.4.4)")
    for theme, roles in themes.items():
        if not roles:
            problems.append(f"{theme}: no [data-theme=\"dark\"] roles found (a site that supports dark mode needs them)")
            continue

        def col(name, theme=theme, roles=roles):
            if name not in roles:
                problems.append(f"{theme}: --{name} is missing")
                return None
            c = parse_color(roles[name], roles)
            if c is None:
                problems.append(f"{theme}: --{name} is {roles[name]!r}, which this cannot read as a colour (use #hex, rgb(), hsl(), oklch() or oklab())")
            elif c[3] < 1:
                problems.append(f"{theme}: --{name} is translucent; a colour role must be opaque, or its contrast depends on what is under it")
                return None
            return c

        for fg, bg, need, why in ROLE_PAIRS:
            f, b = col(fg), col(bg)
            if f is None or b is None:
                continue
            r = contrast_ratio(_hex(f), _hex(b))
            rows.append((theme, fg, bg, r, need, why))
            if r < need:
                problems.append(f"{theme}: --{fg} {roles[fg]} on --{bg} {roles[bg]} is {r:.2f}:1, needs {need}:1 ({why})")
        scrim = col("scrim-color")
        weak = roles.get("scrim-weak")
        if scrim is None or not weak or not re.fullmatch(r"[\d.]+%", weak) or not roles.get("scrim-strong"):
            problems.append(f"{theme}: --scrim-color, --scrim-weak and --scrim-strong (a percentage) are what layout.css's photo band reads")
            continue
        a = float(weak[:-1]) / 100
        over_white = tuple(a * c + (1 - a) * 255 for c in scrim[:3])
        for ink, need, why in SCRIM_INKS:
            f = col(ink)
            if f is None:
                continue
            r = contrast_ratio(_hex(f), _hex(over_white))
            rows.append((theme, ink, f"scrim {weak} over white", r, need, why))
            if r < need:
                problems.append(f"{theme}: --{ink} over the scrim at --scrim-weak {weak} on a white photo pixel is {r:.2f}:1, needs {need}:1 ({why}); raise --scrim-weak")
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


FIXTURE_LINK = {"tel:": "tel:+12515550100", "https://": "https://example.com/", "/": "/", "mailto:": "mailto:hello@example.com"}


def gen(schema, mode, path, block, variant=None):
    t = schema.get("type")
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0 if mode == "min" else -1]
    if path in (block.get("assetProps") or []):
        return "stress-photo"
    if path in (block.get("endpointProps") or []):
        return "https://forms.example.com/stress"
    if path in (block.get("linkProps") or []):
        prefix = (block.get("variantLinks") or {}).get(variant)
        return FIXTURE_LINK.get(prefix, "#main")
    if t == "object":
        out = {}
        req = set(schema.get("required", []))
        for k, v in (schema.get("properties") or {}).items():
            if mode == "min" and k not in req:
                continue
            if k == "variant":
                continue
            out[k] = gen(v, mode, f"{path}.{k}" if path else k, block, variant)
        return out
    if t == "array":
        n = schema.get("minItems", 1) if mode == "min" else schema.get("maxItems", 3)
        item_path = f"{path}[]"
        return [gen(schema.get("items", {"type": "string", "maxLength": 20}), mode, item_path, block, variant) for _ in range(max(n, 0))]
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


def stress_business(today=None):
    """Business facts at their bounds: the longest name and street, every day its own
    row, a window past midnight, and special days ahead of today."""
    d0 = datetime.date.fromisoformat(today) if today else datetime.date.today()
    later = lambda n: (d0 + datetime.timedelta(days=n)).isoformat()  # noqa: E731
    times = [("06:30", "14:00"), ("07:00", "15:30"), ("06:00", "13:00"), ("08:00", "16:00"), ("06:30", "21:00"), ("18:00", "02:00"), ("07:30", "13:00")]
    return {
        "name": _text(80, "max"),
        "schemaType": "LocalBusiness",
        "phone": "+1 (251) 555-0100",
        "email": "reservations.and.private.events@example.com",
        "address": {"street": _text(120, "max"), "city": _text(40, "max"), "region": "AL", "postalCode": "36532-0000", "countryCode": "US"},
        "hours": [{"days": [d], "opens": o, "closes": c} for d, (o, c) in zip(DAY_ORDER, times)],
        "specialHours": [
            {"date": later(20), "label": _text(40, "max"), "closed": True},
            {"date": later(40), "label": "Christmas Eve", "opens": "07:00", "closes": "12:00"},
        ],
    }


def make_fixtures(blocks, today=None):
    pages = []
    for bid, b in sorted(blocks.items()):
        for mode in ("min", "max", "long", "rtl"):
            variant = b["variants"][0 if mode == "min" else -1] if b.get("variants") else None
            blk = {"type": bid, "props": gen(b["props"], mode, "", b, variant)}
            if variant:
                blk["variant"] = variant
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
            page = {
                "path": f"/stress/{bid}/{mode}/",
                "title": f"Stress: {bid} at {mode}",
                "description": f"The {bid} block rendered at its {mode} content, for the device matrix and visual baselines.",
                "noindex": True,
                "blocks": seq,
            }
            if mode == "rtl":
                page.update(lang="ar", dir="rtl")
            pages.append(page)
    paths = [p["path"] for p in pages]
    link = lambda i, n: {"label": _text(n, "max"), "href": paths[i % len(paths)]}  # noqa: E731
    return {
        "siteId": "stress-fixtures",
        "lang": "en",
        "business": stress_business(today),
        "chrome": {
            "nav": [link(i, 20) for i in range(6)],
            "action": {"label": _text(28, "max"), "href": "tel:+12515550100"},
            "footerNav": [link(i, 20) for i in range(8)],
        },
        "assets": {"stress-photo": copy.deepcopy(STRESS_PHOTO)},
        "pages": pages,
    }


# The worst photo for light copy: near white, with faint bands so it is not flat.
STRESS_PHOTO = {
    "src": "stress-photo.png",
    "alt": "A test photograph",
    "width": 2560,
    "height": 1600,
    "provenance": "generated",
    "sources": [{"src": "stress-photo-640.png", "width": 640}, {"src": "stress-photo-1280.png", "width": 1280}],
}


def write_png(path, width, height, row_color):
    """A truecolour PNG whose row y is one colour, row_color(y) -> (r, g, b). Stdlib only."""
    import struct
    import zlib

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = bytearray()
    cache = {}
    for y in range(height):
        c = row_color(y)
        if c not in cache:
            cache[c] = b"\x00" + bytes(c) * width
        raw += cache[c]
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 6)))
        f.write(chunk(b"IEND", b""))


def write_stress_photo(path):
    """The stress photo and its smaller srcset widths, beside path (the same crop)."""
    w, h = STRESS_PHOTO["width"], STRESS_PHOTO["height"]
    band = lambda scale: lambda y: (255, 255, 255) if (y // max(1, round(40 * scale))) % 2 else (236, 234, 229)  # noqa: E731
    write_png(path, w, h, band(1))
    for x in STRESS_PHOTO["sources"]:
        k = x["width"] / w
        write_png(os.path.join(os.path.dirname(path), x["src"]), x["width"], round(h * k), band(k))


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
    rtl = [p for p in fx["pages"] if p["path"].endswith("/rtl/")]
    row(rtl and all(p.get("dir") == "rtl" and p.get("lang") == "ar" for p in rtl), "fixtures: rtl pages are dir=rtl lang=ar, so mirroring is tested")
    row(len(fx["chrome"]["nav"]) == 6 and all(len(x["label"]) == 20 for x in fx["chrome"]["nav"]), "fixtures: the header carries its worst case (6 links of 20 characters)")
    hero_max = next(p for p in fx["pages"] if p["path"] == "/stress/hero-full/max/")["blocks"][0]["props"]
    row(len(hero_max["title"]) == 60 and len(hero_max["actions"]) == 2, "fixtures: max mode fills strings to maxLength and lists to maxItems", json.dumps(hero_max)[:80])
    hero_long = next(p for p in fx["pages"] if p["path"] == "/stress/hero-full/long/")["blocks"][0]["props"]
    row(" " not in hero_long["title"], "fixtures: long mode puts one unbreakable word in each string")

    with open(os.path.join(KIT, "tokens.css"), encoding="utf-8") as f:
        css = f.read()
    tp, trows = check_tokens(css)
    row(not tp and len(trows) == 2 * (len(ROLE_PAIRS) + len(SCRIM_INKS)), f"positive: tokens.css passes every role pairing and the scrim, light and dark ({len(trows)} pairs)", "; ".join(tp[:2]))
    ok_oklch, _ = check_tokens(css.replace("--accent: #2f5bd3;", "--accent: oklch(0.5 0.2 264);", 1))
    row(not ok_oklch, "tokens: an oklch() role is read and scored, not reported missing", "; ".join(ok_oklch[:2]))
    tcase = lambda label, old, new, want: row(  # noqa: E731
        any(want in x for x in check_tokens(css.replace(old, new, 1))[0]), f"must fail (tokens): {label}"
    )
    tcase("a field border too faint to see (SC 1.4.11)", "--field-border: #8a8b94;", "--field-border: #d0d0d4;", "--field-border")
    tcase("a card on an inverse band too light for its text", "--inverse-surface: #25262d;", "--inverse-surface: #9a9aa0;", "inverse-surface")
    tcase("a scrim too thin for light copy over a white pixel", "--scrim-weak: 74%;", "--scrim-weak: 40%;", "raise --scrim-weak")
    tcase("a type step that grows more than 2.5x", "--step-5: clamp(2.4883rem,", "--step-5: clamp(1rem,", "stops growing at 200% zoom")
    tcase("no font stack", "--font-body:", "--font-bodyx:", "--font-body is missing")
    tcase("a translucent colour role", "--surface: #ffffff;", "--surface: #ffffff80;", "translucent")
    bad, _ = check_tokens(css.replace("--ink-muted: #55565e;", "--ink-muted: #9a9aa0;", 1))
    row(any("--ink-muted" in b and "light" in b for b in bad), "must fail (tokens): a muted ink too light for the canvas")
    bad, _ = check_tokens(css.replace("--focus: #9db9ff;\n  }", "--focus: #2a2b33;\n  }"))
    row(any("dark: --focus" in b for b in bad), "must fail (tokens): a dark-theme focus ring that vanishes on the dark canvas")
    bad, _ = check_tokens(css.replace("--accent: #8fb0ff;", "--accent: #8fb1ff;", 1))
    row(any("disagree" in b for b in bad), "must fail (tokens): the two copies of the dark theme drifted apart")
    bad, _ = check_tokens(css + "\n:root { --field-border: #e2e2e6; --focus: #e9e9ee; }\n")
    row(any("--field-border" in b for b in bad) and any("--focus" in b for b in bad), "must fail (tokens): a later :root block that overrides a role (every :root is read, in order)")
    ok_turn, _ = check_tokens(css.replace("--accent: #2f5bd3;", "--accent: hsl(0.62turn 64% 50%);", 1))
    row(not any("cannot read" in b for b in ok_turn), "tokens: an hsl() hue in turn units is read, not a crash", "; ".join(ok_turn[:2]))
    row(parse_color("hsl(nonsense 1 2)") is None, "tokens: an unreadable colour is reported, not a crash")

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
        catalog_case("level-1 block not placed first", edit("hero-full", lambda b: b["placement"].update(position="any")), "must be 'first'")
        catalog_case("assetProps names no prop", edit("story-split", lambda b: b.update(assetProps=["photo"])), "which is not a prop")
        catalog_case("media prop not in assetProps", edit("story-split", lambda b: b.update(assetProps=[])), "must also be listed in assetProps")
        catalog_case("tone default not allowed", edit("features-grid", lambda b: b["tone"].update(default="inverse")), "is not in tone.allowed")
        catalog_case("notAdjacentTo names an unknown block", edit("cta-banner", lambda b: b["placement"].update(notAdjacentTo=["hero-giant"])), "unknown block")
        catalog_case("more than three variants", edit("cta-banner", lambda b: b.update(variants=["a", "b", "c", "d"])), "more than 3")
        catalog_case("a $ref the checker cannot follow", edit("cta-banner", lambda b: b["props"]["properties"].update(extra={"$ref": "#/$defs/anything"})), "cannot follow")
        catalog_case("anyOf in props", edit("cta-banner", lambda b: b["props"]["properties"]["heading"].update(anyOf=[{"type": "string"}])), "cannot follow")
        catalog_case("a list of types", edit("cta-banner", lambda b: b["props"]["properties"].update(note={"type": ["string", "null"], "maxLength": 9})), "list of types")
        catalog_case("variant repeated in props", edit("cta-banner", lambda b: b["props"]["properties"].update(variant={"enum": ["book", "call"]})), "lives on the block instance")
        catalog_case("a styling prop named accent", edit("features-grid", lambda b: b["props"]["properties"].update(accent={"enum": ["blue"]})), "styling prop")
        catalog_case("headingLevel true is not 1", edit("page-header", lambda b: b.update(headingLevel=True)), "is not one of [1, 2]")

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
            lambda m: B(m).insert(1, {"type": "features-grid", "tone": "inverse", "props": B(m)[1]["props"]}),
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
        manifest_case("a block's required fact is missing", lambda m: m["business"].pop("hours"), "does not give")
        manifest_case("an in-page link to no anchor", lambda m: B(m)[0]["props"]["actions"][0].update(href="#nowhere"), "has as its anchor")
        manifest_case("a link to an anchor another page lacks", lambda m: B(m)[0]["props"]["actions"][0].update(href="/visit/#nowhere"), "has no anchor")
        manifest_case("a nav link to a missing page", lambda m: m["chrome"]["nav"][0].update(href="/menu/"), "not a page")
        manifest_case("an in-page link in the header", lambda m: m["chrome"]["nav"][0].update(href="#visit"), "on every page")
        manifest_case("a javascript: link", lambda m: B(m)[0]["props"]["actions"][0].update(href="javascript:alert(1)"), "a link is a path")
        manifest_case("an anchor used twice", lambda m: B(m)[1].update(anchor="visit"), "used more than once")
        manifest_case("the reserved anchor main", lambda m: B(m)[1].update(anchor="main"), "reserved")
        manifest_case("a portrait crop that is landscape", lambda m: m["assets"]["dining-room-portrait"].update(width=2000, height=1000), "not portrait")
        manifest_case("a special day both closed and open", lambda m: m["business"]["specialHours"][0].update(opens="09:00", closes="12:00"), "closed and opening times")
        manifest_case("two windows on one day overlap", lambda m: m["business"]["hours"].append({"days": ["Mo"], "opens": "13:00", "closes": "15:00"}), "overlaps")
        manifest_case("a window that opens as it closes", lambda m: m["business"]["hours"][1].update(closes="07:30"), "same time")
        manifest_case("a quotation without permission", lambda m: B(m)[4]["props"].update(permission=False), "must be true")
        manifest_case("two srcset candidates of one width", lambda m: m["assets"]["counter"]["sources"].append({"src": "x.jpg", "width": 800}), "share a width")
        manifest_case("a path with a trailing newline", lambda m: m["pages"][1].update(path="/visit/\n"), "does not match")
        manifest_case("a date in another script's digits", lambda m: m["business"]["specialHours"][0].update(date="٢٠٢٦-١١-٢٦"), "does not match")
        manifest_case("a date that is not in the calendar", lambda m: m["business"]["specialHours"][0].update(date="2026-11-31"), "not a real date")
        manifest_case(
            "an overnight window that runs into the next day's",
            lambda m: m["business"].update(hours=[{"days": ["Fr"], "opens": "18:00", "closes": "02:00"}, {"days": ["Sa"], "opens": "00:30", "closes": "03:00"}]),
            "Sa overlaps",
        )
        manifest_case("a vanity phone number (tel: would dial its digits only)", lambda m: m["business"].update(phone="1-800-FLOWERS"), "does not match")
        manifest_case("a tel: link to a number that is not the business's", lambda m: m["business"].update(phone="(251) 555-0199"), "not the business's phone")
        manifest_case("a tel: link with no phone in the facts", lambda m: m["business"].pop("phone"), "list no phone")

        def call_to_page(m):
            cta = next(b for b in B(m) if b["type"] == "cta-banner")
            cta.update(variant="call")
            cta["props"]["action"] = {"label": "Call us now", "href": "/visit/"}

        manifest_case("a 'call' variant whose button opens a page", call_to_page, "must be a tel: link")

        def form_to_anchor(m):
            next(b for p in m["pages"] for b in p["blocks"] if b["type"] == "contact-form")["props"]["action"] = "#main"

        manifest_case("a form that posts to an in-page anchor", form_to_anchor, "a form posts to")
        manifest_case("placeholder text in a page title", lambda m: m["pages"][0].update(title="TODO home title"), "title holds placeholder")
        manifest_case("a share image with no origin (a preview needs an absolute URL)", lambda m: (m.pop("origin", None), m.update(shareImage="dining-room")), "needs origin")
        manifest_case("a share image that is not an asset", lambda m: m.update(origin="https://www.example.com", shareImage="nope"), "does not have")
        manifest_case("placeholder text in the chrome", lambda m: m["chrome"]["action"].update(label="XXX call"), "chrome.action.label holds placeholder")
        ok_ext, _ = check_manifest({**copy.deepcopy(example), "business": {**example["business"], "phone": "(251) 555-0100 ext. 12"}}, blocks, mschema)
        row(not ok_ext, "positive: a phone with an extension is a valid fact, and the tel: links still match it", "; ".join(ok_ext[:2]))
        mm = copy.deepcopy(example)
        mm["assets"]["counter"].update(width=1100, height=825)
        _, w = check_manifest(mm, blocks, mschema)
        row(any("enlarged" in x and "counter" in x for x in w), "warns: a photo that is sharp side by side but blurry when the split stacks (1100px for a 704px frame at 2x)")
        mm = copy.deepcopy(example)
        mm["assets"]["dining-room"].update(height=1000)
        _, w = check_manifest(mm, blocks, mschema)
        row(any("enlarged" in x and "dining-room" in x for x in w), "warns: a hero source too short for the band's 704px height at 2x")
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
        os.makedirs(os.path.dirname(os.path.abspath(argv[3])), exist_ok=True)
        with open(argv[3], "w", encoding="utf-8") as f:
            json.dump(fx, f, ensure_ascii=False, indent=2)
            f.write("\n")
        photo = os.path.join(os.path.dirname(os.path.abspath(argv[3])), STRESS_PHOTO["src"])
        write_stress_photo(photo)
        print(f"block_site_check fixtures: wrote {len(fx['pages'])} stress pages to {argv[3]} and the stress photo to {photo}")
        print("  next: block_site_render.py render <that file> --catalog <catalog> --out <dir>, then device_matrix.mjs --dir <dir> --manifest <that file>")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
