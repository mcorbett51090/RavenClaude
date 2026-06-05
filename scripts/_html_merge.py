#!/usr/bin/env python3
"""Helpers for folding the dashboard sub-app natively into index.html.

The dashboard (`plugins/ravenclaude-core/dashboard.html` via
`generate-dashboards.py`) was authored as a *whole-document* app: its CSS uses
bare element selectors (`body`, `html`, `main`, `*`, `a`, `code`) and its JS
queries the DOM globally. To mount it as a native section inside the single
`index.html` shell — instead of in an iframe — its CSS must be **scoped** under
a container element so its rules can't bleed across the page. (The repo-guide
sub-app was retired; its catalog content is now rendered natively by the shell
from JSON, so it no longer needs scoping.)

`scope_css(css, prefix)` rewrites a stylesheet so every rule only applies
within `prefix` (e.g. `#dash-root`). It is comment-aware, handles nested
`@media`/`@supports`/`@container`/`@layer` blocks by recursion, leaves
`@keyframes`/`@font-face`/`@page`/`@import`/`@charset` untouched, keeps `:root`
custom-property blocks global, and maps leading `html`/`body`/`:host` selectors
onto the container itself.

No third-party deps; pure string processing. Self-test: `python3 scripts/_html_merge.py`.
"""

from __future__ import annotations

import re

# At-rules whose body is itself a list of style rules → recurse into the block.
_NESTED_ATRULES = ("@media", "@supports", "@container", "@layer")
# At-rules whose body must pass through verbatim (selectors are not element
# selectors: keyframe stops, font descriptors, page boxes…).
_VERBATIM_ATRULES = ("@keyframes", "@-webkit-keyframes", "@font-face", "@page", "@property", "@counter-style", "@font-feature-values")


def _strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def _split_top_level_commas(selector_list: str) -> list[str]:
    """Split a selector list on commas that are not inside () or []."""
    out: list[str] = []
    depth = 0
    buf: list[str] = []
    for ch in selector_list:
        if ch in "([":
            depth += 1
            buf.append(ch)
        elif ch in ")]":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return [s.strip() for s in out if s.strip()]


def _prefix_one(selector: str, prefix: str) -> str:
    """Scope a single (comma-free) selector under `prefix`."""
    s = selector.strip()
    if not s:
        return s
    # Keep custom-property roots global — CSS variables cascade everywhere and
    # the values are identical to the shell's, so duplicating them is harmless.
    if s == ":root" or s.startswith(":root"):
        return s
    # Map whole-document anchors onto the container itself.
    for anchor in ("html", "body", ":host"):
        if s == anchor:
            return prefix
        if s.startswith(anchor + " ") or s.startswith(anchor + ">") or s.startswith(anchor + "."):
            return prefix + s[len(anchor):]
        if s.startswith(anchor + ":"):  # body:hover, html:focus-within…
            return prefix + s[len(anchor):]
    # Everything else: nest under the container.
    return prefix + " " + s


def _prefix_selector_list(selector_list: str, prefix: str) -> str:
    return ", ".join(_prefix_one(s, prefix) for s in _split_top_level_commas(selector_list))


def scope_css(css: str, prefix: str) -> str:
    """Return `css` rewritten so every rule applies only within `prefix`."""
    css = _strip_comments(css)
    out: list[str] = []
    i, n = 0, len(css)
    while i < n:
        ch = css[i]
        if ch in " \t\r\n":
            i += 1
            continue
        # At-rules.
        if ch == "@":
            # Read up to the first '{' or ';' to learn the at-rule prelude.
            j = i
            while j < n and css[j] not in "{;":
                j += 1
            prelude = css[i:j].strip()
            keyword = prelude.split(None, 1)[0].lower() if prelude else ""
            if j < n and css[j] == ";":  # @import / @charset — no block
                out.append(prelude + ";\n")
                i = j + 1
                continue
            # has a block — find its matching close brace
            block_start = j
            depth = 0
            k = block_start
            while k < n:
                if css[k] == "{":
                    depth += 1
                elif css[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            inner = css[block_start + 1:k]
            if keyword in _NESTED_ATRULES:
                out.append(prelude + " {\n" + scope_css(inner, prefix) + "}\n")
            else:  # keyframes / font-face / page / property … pass through
                out.append(prelude + " {" + inner + "}\n")
            i = k + 1
            continue
        # Normal rule: selector-list up to '{', then a brace-balanced body.
        j = i
        while j < n and css[j] != "{":
            j += 1
        selectors = css[i:j]
        depth = 0
        k = j
        while k < n:
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        body = css[j + 1:k]
        scoped_sel = _prefix_selector_list(selectors, prefix)
        if scoped_sel:
            out.append(scoped_sel + " {" + body + "}\n")
        i = k + 1
    return "".join(out)


def iife_wrap(js: str, expose: str = "") -> str:
    """Wrap a sub-app's JS in an IIFE so its top-level helpers (`svg`, `toast`,
    `esc`…) can't collide with the shell's. `expose` is appended inside the
    closure (e.g. `window.__dashApp = {...};`)."""
    tail = ("\n" + expose) if expose else ""
    return "(function(){\n" + js + tail + "\n})();"


if __name__ == "__main__":
    # ── Self-test: mechanical guarantees the merge relies on ──────────────────
    sample = """
    /* a comment with { braces } and ; semicolons */
    :root { --x: 1; }
    * { box-sizing: border-box; }
    html, body { margin: 0; background: var(--bg); }
    body.dark { color: white; }
    a:hover { color: teal; }
    main { max-width: 1280px; }
    .card, .btn { padding: 4px; }
    @media (max-width: 720px) {
      body { font-size: 14px; }
      .card { padding: 2px; }
    }
    @keyframes spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }
    .x:not(.y, .z) { color: red; }
    """
    scoped = scope_css(sample, "#dash-root")
    assert scoped.count("{") == scoped.count("}"), "brace balance broken"
    # Bare leaky selectors must be gone (outside @keyframes).
    body_no_kf = re.sub(r"@(?:-webkit-)?keyframes[^{]*\{.*?\n\}", "", scoped, flags=re.DOTALL)
    for leak in ("\nbody ", "\nbody{", "\nhtml ", "\nmain ", "\n* {", "\na:hover"):
        assert leak not in ("\n" + scoped.replace(" {", "{")), f"leaky selector survived: {leak!r}"
    assert "#dash-root.dark" in scoped, "body.dark not mapped to container"
    assert "#dash-root *" in scoped, "* not scoped"
    assert ":root { --x: 1; }" in scoped, ":root must stay global"
    assert "@keyframes spin {" in scoped and "from {" in scoped, "keyframes must pass through"
    assert "#dash-root .card" in scoped and "#dash-root .btn" in scoped, "selector list not scoped"
    assert "#dash-root .x:not(.y, .z)" in scoped, ":not() comma split mishandled"
    # nested media rules scoped
    assert "@media (max-width: 720px) {" in scoped
    assert scoped.count("#dash-root .card") == 2, "media-nested .card not scoped"
    print("scope_css self-test: PASS")
    print(scoped)
