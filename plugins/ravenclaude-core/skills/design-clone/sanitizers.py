#!/usr/bin/env python3
"""sanitizers.py — the allowlist primitives the design-clone apply path routes every
reference-derived value through before it can reach a generated stylesheet.

TWO FAMILIES:

  1. PORTED FROM wireframe_lint.py — keep in sync. `html_text`, `uri_scheme`, and
     `css_value` are copied verbatim from
     plugins/ravenclaude-core/skills/wireframe/wireframe_lint.py (the `_scrub.sh` /
     `thing-seat.sh` duplicate-until-a-third-caller precedent — no cross-skill Python
     import in this repo). `css_value` is COLOR-ONLY by design (its docstring says so):
     it validates a safe CSS color and nothing else. That is exactly why the design
     schema's STRUCTURAL payload (lengths, shadows, grid numbers) needs the second
     family below — routing `8px` / `0 2px 8px rgba(0,0,0,0.1)` / `1200px` through
     `css_value` returns None and would ship an EMPTY stylesheet (the CE-3 trap).

  2. NEW STRICT ALLOWLISTS — `css_length`, `css_number`, `css_shadow`. Reject-on-unknown,
     NO partial salvage: an unknown token anywhere in a compound value drops the WHOLE
     value (never the clean remainder). Every widened sanitizer unconditionally rejects
     the CSS-injection metacharacters (`;` `{` `}` `/*` `\\` `<` `>`, `@import`,
     `expression(`, `var(`, whitespace-injection / control chars) and rejects `(`/`)`
     except inside a matched color function. Regexes are LINEAR (no nested quantifiers)
     — no catastrophic backtracking over a large `css_text` (ReDoS).

The apply path (apply_schema.py) is the sole caller; Gate 194 proves both directions:
hostile input neutralized to ABSENT, legit input surviving VERBATIM.
"""

from __future__ import annotations

import re

# ── ported from wireframe_lint.py — keep in sync ──────────────────────────────
_HTML_ESCAPES = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}
_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_FUNC_COLOR_RE = re.compile(r"^(?:rgb|rgba|hsl|hsla)\([0-9.,%\s/]+\)$")
_KEYWORD_RE = re.compile(r"^[a-zA-Z][a-zA-Z-]{0,31}$")
_ALLOWED_URI_SCHEMES = ("http://", "https://", "mailto:", "tel:")


def html_text(s: str) -> str:
    """Escape the five HTML metacharacters for a text/attribute context.

    ported from wireframe_lint.py — keep in sync.
    """
    return "".join(_HTML_ESCAPES.get(c, c) for c in str(s))


def css_value(s: str) -> str | None:
    """Return the value iff it is a safe CSS color, else None.

    ported from wireframe_lint.py — keep in sync. COLOR-ONLY: allows #hex,
    rgb()/rgba()/hsl()/hsla(), or a plain keyword. Rejects anything that could carry
    url(), a declaration break (`;`/`}`), or a comment — which is how a raw brand color
    reaching <style> becomes an external fetch / CSP break. It does NOT accept a length,
    a shadow, or a number — that is what css_length / css_shadow / css_number are for.
    """
    v = str(s).strip()
    if _HEX_RE.match(v) or _FUNC_COLOR_RE.match(v) or _KEYWORD_RE.match(v):
        return v
    return None


def uri_scheme(s: str) -> str | None:
    """Return the URI iff its scheme is allowlisted (or it is relative/anchor).

    ported from wireframe_lint.py — keep in sync.
    """
    v = str(s).strip()
    low = v.lower()
    if low.startswith(("javascript:", "data:", "vbscript:", "file:")):
        return None
    if low.startswith(_ALLOWED_URI_SCHEMES):
        return v
    # relative path, anchor, or query — no scheme, so no scheme-based injection
    if v.startswith(("/", "#", "?", "./", "../")) or ":" not in v.split("/", 1)[0]:
        return v
    return None


# ── NEW strict structural allowlists (reject-on-unknown, no partial salvage) ───

# A single CSS length: an optionally-signed number with an allowlisted unit, OR literal
# 0. LINEAR — the alternation branches start on disjoint characters (digit vs `.`), so
# there is no ambiguous overlap and no catastrophic backtracking (ReDoS).
_CSS_LENGTH_RE = re.compile(r"^-?(?:\d+\.?\d*|\.\d+)(?:px|rem|em|%|vw|vh|ch|ex)$")
# A bare non-negative CSS number (e.g. a grid column count, a unitless line-height).
_CSS_NUMBER_RE = re.compile(r"^\d+(?:\.\d+)?$")

# Substrings that are NEVER allowed in a widened sanitizer's input — a declaration break,
# a block, a comment, an escape, an angle bracket, an @-rule, a CSS expression(), or a
# var() reference (an untrusted var() can resolve to anything, so it is refused here; the
# apply path emits its OWN trusted var(--brand-*) tokens, which never pass through this).
_FORBIDDEN_SUBSTR = (
    ";",
    "{",
    "}",
    "/*",
    "*/",
    "\\",
    "<",
    ">",
    "@import",
    "expression(",
    "var(",
)

_MAX_LAYERS = 8  # ≤N comma-separated shadow layers
_MAX_LENGTHS_PER_LAYER = 4  # box-shadow: offset-x offset-y blur spread


def _has_forbidden(v: str) -> bool:
    """True iff `v` carries a CSS-injection metacharacter or any control char.

    Control chars include tab/newline/CR/formfeed/vertical-tab — the whitespace-injection
    vectors that can smuggle a declaration break past a naive length check. A plain ASCII
    space (0x20) is NOT a control char and is allowed (shadows separate tokens with it).
    """
    low = v.lower()
    for tok in _FORBIDDEN_SUBSTR:
        if tok in low:
            return True
    for ch in v:
        o = ord(ch)
        if o < 0x20 or o == 0x7F:
            return True
    return False


def css_length(value: str) -> str | None:
    """Return the value iff it is a single safe CSS length (`^-?num(unit)$` or `0`), else
    None. Rejects ( ) unconditionally and every _FORBIDDEN_SUBSTR / control char."""
    v = str(value).strip()
    if not v or _has_forbidden(v):
        return None
    if "(" in v or ")" in v:
        return None
    if v == "0":
        return "0"
    if _CSS_LENGTH_RE.match(v):
        return v
    return None


def css_number(value: str) -> str | None:
    """Return the value iff it is a bare non-negative CSS number, else None. Rejects ( )
    unconditionally and every _FORBIDDEN_SUBSTR / control char."""
    v = str(value).strip()
    if not v or _has_forbidden(v):
        return None
    if "(" in v or ")" in v:
        return None
    if _CSS_NUMBER_RE.match(v):
        return v
    return None


def split_top_level(s: str, sep_chars: str) -> list[str] | None:
    """Split `s` on any char in `sep_chars` that sits at parenthesis-depth 0 (so a comma
    or space inside `rgba( … )` is preserved as part of that token). Returns the parts, or
    None if the parentheses are unbalanced. Single linear pass — O(len(s)), no backtracking.
    """
    out: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in s:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return None
            buf.append(ch)
        elif depth == 0 and ch in sep_chars:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if depth != 0:
        return None
    out.append("".join(buf))
    return out


def _validate_shadow_layer(layer: str) -> bool:
    """A shadow layer is valid iff EVERY whitespace-separated token is a css_length, a
    css_value(matched color), or the literal `inset`, with ≤4 length tokens. Any unknown
    token invalidates the layer (the caller then drops the whole value — no salvage)."""
    toks = split_top_level(layer, " ")
    if toks is None:
        return False
    toks = [t.strip() for t in toks if t.strip()]
    if not toks:
        return False
    lengths = 0
    for tok in toks:
        if tok == "inset":
            continue
        if css_length(tok) is not None:
            lengths += 1
            if lengths > _MAX_LENGTHS_PER_LAYER:
                return False
            continue
        if css_value(tok) is not None:
            continue
        return False
    return True


def css_shadow(value: str) -> str | None:
    """Return the value iff it is a safe box-shadow (bounded compound), else None.

    Tokenizes on top-level whitespace/comma; every token must be a css_length OR a
    css_value(matched color) OR literal `inset`; ≤4 length tokens per layer, ≤8 layers.
    ANY unknown token ⇒ return None for the ENTIRE value — NEVER keep the clean remainder
    (no partial salvage). ( ) are permitted only inside a matched color function; any
    other paren use fails a token and drops the whole value.
    """
    v = str(value).strip()
    if not v or _has_forbidden(v):
        return None
    layers = split_top_level(v, ",")
    if layers is None:
        return None
    layers = [layer.strip() for layer in layers]
    if not layers or len(layers) > _MAX_LAYERS:
        return None
    for layer in layers:
        if not layer or not _validate_shadow_layer(layer):
            return None
    return v
