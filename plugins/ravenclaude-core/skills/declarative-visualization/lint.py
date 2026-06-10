#!/usr/bin/env python3
"""
declarative-visualization security linter (Gate 101).

Checks a Vega-Lite/Vega/SVG spec or template for network-access vectors and
script-injection vectors.  Stdlib-only, no network, exit-coded for CI.

Exit codes:
  0 — clean (no violations)
  1 — one or more security violations found
  2 — I/O, parse, or path-rejection error (purity failure: '..' in path,
      path outside the repo root, or file not found/unreadable)

The six forbidden patterns (all → exit 1):
  JSON specs:
    (a) data.url — top-level or nested — any object with a "url" key that is a
        sibling of "name" in a data source, or any top-level data.url string
    (b) transform.lookup with a from.data that has a "url" key
    (c) any "loader" key anywhere in the spec
    (d) a "$schema" value whose host is NOT vega.github.io (non-official origin)

  SVG files (.svg or JSON string containing '<svg'):
    (e) <script> element
    (f) on* attribute (onclick, onload, onmouseover, …)
    (g) <foreignObject> element (XSS-escalation vector)
    (h) href or xlink:href whose value starts with http://, https://, or
        javascript: (network call + potential JS); safe local fragment refs
        like href="#id" are allowed

Usage:
  python3 lint.py <spec.json|template.json|file.svg> [--debug]
  python3 lint.py --list-checks
"""

import json
import os
import re
import sys

CHECKS = [
    ("data-url",           "data.url present (SSRF vector) — use data.name instead"),
    ("transform-lookup",   "transform.lookup with remote from.data.url — use data.name + host-side join"),
    ("loader-override",    "'loader' key present — custom loader can redirect all URL resolution"),
    ("schema-remote",      "$schema references a non-vega.github.io host — only the official origin is allowed"),
    ("svg-script",         "<script> element in SVG — script injection vector"),
    ("svg-on-attr",        "on* attribute in SVG — inline JS event handler vector"),
    ("svg-foreign-object", "<foreignObject> element in SVG — XSS-escalation vector"),
    ("svg-remote-href",    "remote or javascript: href/xlink:href in SVG — network call + potential JS"),
]

VEGA_SCHEMA_ALLOWED_HOST = "vega.github.io"


def list_checks() -> None:
    print("Gate 101 — declarative-visualization linter checks:")
    for key, desc in CHECKS:
        print(f"  [{key}] {desc}")


# ── path safety ──────────────────────────────────────────────────────────────

def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(10):
        if os.path.isfile(os.path.join(root, ".repo-layout.json")) or \
           os.path.isfile(os.path.join(root, "AGENTS.md")):
            return root
        parent = os.path.dirname(root)
        if parent == root:
            break
        root = parent
    return os.path.abspath(os.path.join(here, "../../../.."))


def _safe_path(raw: str) -> str:
    """Resolve and validate path; exit 2 on traversal or escape."""
    if ".." in raw:
        print(f"[error] path contains '..': {raw!r}", file=sys.stderr)
        sys.exit(2)
    repo = _repo_root()
    abs_path = os.path.realpath(os.path.join(os.getcwd(), raw))
    if not abs_path.startswith(os.path.realpath(repo)):
        print(f"[error] path escapes repo root: {abs_path!r}", file=sys.stderr)
        sys.exit(2)
    return abs_path


# ── JSON traversal ────────────────────────────────────────────────────────────

def _walk(obj, violations: list, path: str = "$") -> None:
    """Recursively walk a parsed JSON object, collecting violations."""
    if isinstance(obj, dict):
        # (c) loader key anywhere
        if "loader" in obj:
            violations.append(("loader-override", path + ".loader"))

        # (d) $schema non-official host
        schema_val = obj.get("$schema")
        if isinstance(schema_val, str) and schema_val.startswith("http"):
            host = schema_val.split("/")[2] if schema_val.count("/") >= 2 else ""
            if host and host != VEGA_SCHEMA_ALLOWED_HOST:
                violations.append(("schema-remote", f"{path}.$schema = {schema_val!r}"))

        # (a) data.url — object has a "url" key and is acting as a data source
        # A data source is an object with a "url" key (and optionally "format",
        # "name", etc.).  We match any dict that has "url" at a data-source
        # position (i.e., it is the value of a "data" key, or inside "datasets",
        # or inside a "from.data" of a transform).
        # We check for "url" as a string value (the network-fetch case).
        if "url" in obj and isinstance(obj["url"], str):
            # only flag if this looks like a data source (has "url" but also
            # optional data-source keys, or is clearly nested under data)
            _flag_url_if_data_source(obj, violations, path)

        # (b) transform.lookup with from.data.url
        transforms = obj.get("transform", [])
        if isinstance(transforms, list):
            for i, t in enumerate(transforms):
                if isinstance(t, dict) and t.get("lookup") is not None:
                    from_data = t.get("from", {}).get("data", {})
                    if isinstance(from_data, dict) and "url" in from_data:
                        violations.append((
                            "transform-lookup",
                            f"{path}.transform[{i}].from.data.url"
                        ))

        # recurse into all values
        for k, v in obj.items():
            _walk(v, violations, f"{path}.{k}")

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk(v, violations, f"{path}[{i}]")


def _flag_url_if_data_source(obj: dict, violations: list, path: str) -> None:
    """
    Flag obj.url if this dict looks like a Vega data source (not, e.g., a
    hyperlink in a tooltip title).  Heuristic: a data source at minimum has
    "url" and typically has "format" or "name" as siblings, or it is bare
    {"url": "..."}. We flag if "url" is a non-empty string and is not clearly
    a pure UI annotation (e.g., embedded in a tooltip or href field name).
    """
    url_val = obj.get("url")
    if not isinstance(url_val, str) or not url_val:
        return
    # Definitely a data source if it also has "format" or "csv"/"json" hint
    data_source_keys = {"format", "name", "csv", "json", "sequence", "sphere", "graticule"}
    if data_source_keys.intersection(obj.keys()) or set(obj.keys()) == {"url"}:
        violations.append(("data-url", f"{path}.url = {url_val!r}"))
    # Also flag top-level data: {url: ...} even if only "url" is present
    elif "url" in obj and len(obj) <= 3:
        violations.append(("data-url", f"{path}.url = {url_val!r}"))


# ── SVG checks ────────────────────────────────────────────────────────────────

_RE_SCRIPT_TAG      = re.compile(r"<script[\s/>]", re.IGNORECASE)
_RE_ON_ATTR         = re.compile(r"\bon\w+\s*=", re.IGNORECASE)
_RE_FOREIGN_OBJECT  = re.compile(r"<foreignObject[\s/>]", re.IGNORECASE)
# Match href or xlink:href whose value begins with a remote scheme or javascript:.
# Safe local fragment refs (href="#id") do NOT start with http/https/javascript,
# so they are intentionally excluded from this pattern.
_RE_REMOTE_HREF     = re.compile(
    r"""(?:xlink:)?href\s*=\s*['"]?\s*(?:https?://|javascript:)""",
    re.IGNORECASE,
)


def _check_svg(content: str, violations: list) -> None:
    if _RE_SCRIPT_TAG.search(content):
        violations.append(("svg-script", "<script> element found in SVG"))
    if _RE_ON_ATTR.search(content):
        violations.append(("svg-on-attr", "on* attribute found in SVG"))
    if _RE_FOREIGN_OBJECT.search(content):
        violations.append(("svg-foreign-object", "<foreignObject> element found in SVG"))
    if _RE_REMOTE_HREF.search(content):
        violations.append(("svg-remote-href", "remote or javascript: href/xlink:href found in SVG"))


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    args = sys.argv[1:]
    debug = "--debug" in args
    args = [a for a in args if a != "--debug"]

    if "--list-checks" in args:
        list_checks()
        return 0

    if not args:
        print("usage: lint.py <spec.json|file.svg> [--debug]", file=sys.stderr)
        return 2

    raw_path = args[0]
    abs_path = _safe_path(raw_path)

    if not os.path.isfile(abs_path):
        print(f"[error] file not found: {abs_path!r}", file=sys.stderr)
        return 2

    try:
        content = open(abs_path, encoding="utf-8").read()
    except OSError as exc:
        print(f"[error] cannot read file: {exc}", file=sys.stderr)
        return 2

    violations: list = []

    is_svg = abs_path.lower().endswith(".svg") or content.lstrip().startswith("<svg")

    if is_svg:
        _check_svg(content, violations)
    else:
        # JSON path
        try:
            obj = json.loads(content)
        except json.JSONDecodeError as exc:
            print(f"[error] JSON parse error: {exc}", file=sys.stderr)
            return 2
        _walk(obj, violations)
        # Also check if the JSON embeds an SVG string (SVG-in-DAX pattern)
        if "<svg" in content.lower():
            _check_svg(content, violations)

    if debug:
        print(f"[debug] path={abs_path!r}, is_svg={is_svg}, violations={violations}")

    if not violations:
        print(f"[lint] PASS — {raw_path}")
        return 0

    print(f"[lint] FAIL — {raw_path} ({len(violations)} violation(s)):")
    for key, detail in violations:
        print(f"  [{key}] {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
