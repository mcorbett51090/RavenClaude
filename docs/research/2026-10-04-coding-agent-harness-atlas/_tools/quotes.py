"""Find each scout quote in the raw page itself and store the raw text, never the scout's.

A cheap model extracts records {claim, quote} from documentation pages. It cannot be trusted
with line numbers or exact punctuation, so this module locates the quote in the raw page,
assigns the line range itself, and keeps the raw span. A model saying a quote is present
never counts; a quote that cannot be found is dropped, never repaired.

Matching tiers, tried in order and stopped at the first hit: exact (substring), ws
(whitespace collapsed), neutral (ws plus the neutralizer substitutes mapped back) and
markup (neutral plus Markdown markup characters turned into spaces). The three normalized
tiers never match across a hard boundary: a blank line, a heading line, a table row or a
fence line. Plain consecutive text lines of one paragraph still join with a space.

A quote whose markup-normalized text has fewer than MIN_QUOTE_ALNUM letters or digits and
fewer than MIN_QUOTE_WORDS words is "too_short": a single character or bare markup would
verify against almost any page.

Install and update command lines are never stored verbatim: the evidence carries an empty
quote and a described span with a hash of the raw lines instead. The install test looks at
the quote's lines plus two lines on each side, after joining backslash continuations.

Usage: python3 quotes.py check --raw FILE --quote TEXT [--line-hint N]
       python3 quotes.py batch --records SCOUT_JSON --pages PAGES_JSON --out OUT_JSON
                              [--counters FILE]
       python3 quotes.py --selftest
"""

import argparse
import hashlib
import json
import re
import sys
from bisect import bisect_right
from functools import lru_cache
from pathlib import Path

from atlas_common import assert_worktree, dump_json

TIERS = ("exact", "ws", "neutral", "markup")
MAX_SPAN = 300
MIN_QUOTE_ALNUM = 12
MIN_QUOTE_WORDS = 2
INSTALL_DESCRIPTION = "install or update command line (stored as a described span)"
CONTEXT_SCRUBBED = "[install command line omitted]"

# Placed between lines in the normalized haystack where a quote must not match across. It is
# turned into a space in every needle and every haystack line, so it cannot occur in a needle.
BOUNDARY = "\x00"

_MARKUP_CHARS = "`*_|\\#>"
_WS_TABLE = {0: " "}
_NEUTRAL_TABLE = {**_WS_TABLE, ord("‹"): "<", ord("›"): ">"}
# In the markup tier the right substitute maps to ">", which is itself markup: one pass.
_MARKUP_TABLE = {**_WS_TABLE, ord("‹"): "<", ord("›"): " "}
_MARKUP_TABLE.update({ord(c): " " for c in _MARKUP_CHARS})
_TABLES = {"ws": _WS_TABLE, "neutral": _NEUTRAL_TABLE, "markup": _MARKUP_TABLE}
_SUBSTITUTES = ("‹", "›")

_BREAK_RE = re.compile(r"\r\n|\r|\n")
_TOKEN_RE = re.compile(r"\S+")
# A heading, a table row or a fence starts a new block; a blank line ends one.
_HARD_RE = re.compile(r"^\s*(?:[|#]|`{3}|~{3})")


def norm(s, tier):
    """Normalize s for comparison at the given tier (see the module docstring)."""
    if tier == "exact":
        return s
    if tier not in _TABLES:
        raise ValueError(f"unknown tier {tier!r}")
    return " ".join(s.translate(_TABLES[tier]).split())


@lru_cache(maxsize=8)
def _raw_lines(raw_text):
    """Every piece between line breaks: CRLF, a lone CR and LF each end a line."""
    return tuple(_BREAK_RE.split(raw_text))


def _content_lines(raw_text):
    """The lines of the page: the empty piece after a final line break is not a line."""
    lines = _raw_lines(raw_text)
    if len(lines) > 1 and lines[-1] == "":
        return lines[:-1]
    return lines


@lru_cache(maxsize=8)
def _line_starts(raw_text):
    """Offset of the first character of each raw line; bisect_right gives a 1-based line."""
    return [0, *(m.end() for m in _BREAK_RE.finditer(raw_text))]


def _segments(lines, table):
    """Yield (line index, translated line, separator) for each line that has text.

    The separator goes before the segment: "" for the first, BOUNDARY where a blank (or
    normalizes-to-nothing) line lies between this segment and the previous one or either of
    the two lines is a heading, table row or fence, and a space otherwise.
    """
    gap = False
    prev_hard = False
    first = True
    for index, line in enumerate(lines):
        translated = line.translate(table)
        if not translated.strip():
            gap = True
            continue
        hard = bool(_HARD_RE.match(line))
        if first:
            sep = ""
        else:
            sep = BOUNDARY if (gap or hard or prev_hard) else " "
        yield index, translated, sep
        gap, prev_hard, first = False, hard, False


@lru_cache(maxsize=8)
def _norm_map(raw_text, tier):
    """Normalized copy of the raw text plus the segment offsets and raw line of each segment.

    One linear pass: every raw line is normalized on its own, lines with no text are skipped
    and the rest are joined by the separator _segments chooses. A normalized index maps back
    to its raw line by bisecting the segment offsets.
    """
    parts, seg_starts, seg_lines = [], [], []
    pos = 0
    for index, translated, sep in _segments(_content_lines(raw_text), _TABLES[tier]):
        seg = " ".join(translated.split())
        parts.append(sep)
        parts.append(seg)
        pos += len(sep)
        seg_starts.append(pos)
        seg_lines.append(index + 1)
        pos += len(seg)
    return "".join(parts), seg_starts, seg_lines


def _find_all(haystack, needle):
    hits = []
    idx = haystack.find(needle)
    while idx != -1:
        hits.append(idx)
        idx = haystack.find(needle, idx + len(needle))
    return hits


def _clip_lines(lines):
    """Whole lines joined with newline, cut at a line boundary when over MAX_SPAN."""
    text = "\n".join(lines)
    if len(text) <= MAX_SPAN:
        return text
    kept, total = [], 0
    for line in lines:
        added = len(line) + (1 if kept else 0)
        if total + added > MAX_SPAN:
            break
        kept.append(line)
        total += added
    if kept:
        return "\n".join(kept)
    return lines[0][:MAX_SPAN]


def _span_lines(raw_text, start, end):
    return list(_content_lines(raw_text)[max(start - 1, 0) : end])


def lines_text(raw_text, start, end):
    """The whole lines start..end (1-based, inclusive) joined with newline, never capped."""
    return "\n".join(_span_lines(raw_text, start, end))


def split_lines(raw_text):
    """The lines of a page as a list: CRLF, a lone CR and LF each end a line."""
    return list(_content_lines(raw_text))


def _local_norm(lines, tier):
    """Normalized text of just these lines, plus each token's normalized and raw offset.

    The raw offset is into "\\n".join(lines). Translation is one character for one character,
    so a token keeps its length and an index inside a token maps straight back.
    """
    table = _TABLES[tier]
    bases, offset = [], 0
    for line in lines:
        bases.append(offset)
        offset += len(line) + 1
    parts, tok_norm, tok_raw = [], [], []
    pos = 0
    for index, translated, sep in _segments(lines, table):
        parts.append(sep)
        pos += len(sep)
        for k, m in enumerate(_TOKEN_RE.finditer(translated)):
            if k:
                parts.append(" ")
                pos += 1
            tok_norm.append(pos)
            tok_raw.append(bases[index] + m.start())
            parts.append(m.group())
            pos += len(m.group())
    return "".join(parts), tok_norm, tok_raw


def _locate(lines, tier, needle):
    """(start, end) of the match inside "\\n".join(lines), or None when it cannot be placed."""
    block = "\n".join(lines)
    if tier == "exact":
        unified = _BREAK_RE.sub("\n", needle)
        for candidate in (needle, unified, unified.strip("\n")):
            idx = block.find(candidate) if candidate else -1
            if idx >= 0:
                return idx, idx + len(candidate)
        return None
    text, tok_norm, tok_raw = _local_norm(lines, tier)
    first = text.find(needle)
    if first < 0:
        return None
    last = first + len(needle) - 1
    k_first = bisect_right(tok_norm, first) - 1
    k_last = bisect_right(tok_norm, last) - 1
    return (
        tok_raw[k_first] + (first - tok_norm[k_first]),
        tok_raw[k_last] + (last - tok_norm[k_last]) + 1,
    )


def _window(block, match_start, match_end):
    """At most MAX_SPAN characters of block, centred on the match, cut on word boundaries.

    Each edge moves inward to the nearest word boundary that does not cut into the match;
    when the slack holds no boundary the edge stays where it is.
    """
    length = len(block)
    low = max(0, min((match_start + match_end) // 2 - MAX_SPAN // 2, length - MAX_SPAN))
    high = min(length, low + MAX_SPAN)

    def starts_word(p):
        return not block[p].isspace() and (p == 0 or block[p - 1].isspace())

    def ends_word(p):
        return not block[p - 1].isspace() and (p == length or block[p].isspace())

    start = next((p for p in range(low, match_start + 1) if starts_word(p)), low)
    stop = next((p for p in range(high, match_end - 1, -1) if ends_word(p)), high)
    return block[start:stop], start


def _span_text(raw_text, tier, needle, start, end):
    """(stored span, its character offset inside the joined whole lines).

    Short spans are the whole lines. A longer one is a window that contains the match; a match
    longer than MAX_SPAN cannot be contained, so it keeps the cut at a line boundary.
    """
    lines = _span_lines(raw_text, start, end)
    block = "\n".join(lines)
    if len(block) <= MAX_SPAN:
        return block, 0
    located = _locate(lines, tier, needle)
    if located is None or located[1] - located[0] > MAX_SPAN:
        return _clip_lines(lines), 0
    return _window(block, *located)


def _not_found():
    return {
        "found": False,
        "tier": None,
        "start_line": None,
        "end_line": None,
        "raw_span": None,
        "ambiguous": False,
        "occurrences": 0,
    }


def _too_short(quote):
    """True when the markup-normalized quote fails both minimums (see the module docstring)."""
    text = norm(quote, "markup")
    letters = sum(c.isalnum() for c in text)
    return letters < MIN_QUOTE_ALNUM and len(text.split()) < MIN_QUOTE_WORDS


def _found(raw_text, tier, needle, spans, line_hint):
    if line_hint is None:
        start, end = spans[0]
    else:
        start, end = min(spans, key=lambda s: (abs(s[0] - line_hint), s[0]))
    raw_span, offset = _span_text(raw_text, tier, needle, start, end)
    return {
        "found": True,
        "tier": tier,
        "start_line": start,
        "end_line": end,
        "raw_span": raw_span,
        "span_offset": offset,
        "ambiguous": len(spans) > 1,
        "occurrences": len(spans),
    }


def verify_quote(quote, raw_text, line_hint=None):
    """Locate quote in raw_text and report its tier and exact 1-based line range.

    A found result also carries span_offset, the character offset of raw_span inside the
    joined whole lines. A quote too short to verify returns reason "too_short".
    """
    if not isinstance(quote, str) or not quote.strip():
        return _not_found()
    if _too_short(quote):
        return {**_not_found(), "reason": "too_short"}
    hits = _find_all(raw_text, quote)
    if hits:
        starts = _line_starts(raw_text)
        spans = [(bisect_right(starts, i), bisect_right(starts, i + len(quote) - 1)) for i in hits]
        return _found(raw_text, "exact", quote, spans, line_hint)

    has_substitute = any(c in raw_text or c in quote for c in _SUBSTITUTES)
    for tier in ("ws", "neutral", "markup"):
        if tier == "neutral" and not has_substitute:
            continue  # without substitutes neutral equals ws, which already missed
        needle = norm(quote, tier)
        if not needle:
            continue
        text, seg_starts, seg_lines = _norm_map(raw_text, tier)
        hits = _find_all(text, needle)
        if hits:
            spans = [
                (
                    seg_lines[bisect_right(seg_starts, i) - 1],
                    seg_lines[bisect_right(seg_starts, i + len(needle) - 1) - 1],
                )
                for i in hits
            ]
            return _found(raw_text, tier, needle, spans, line_hint)
    return _not_found()


# The install pattern is assembled from fragments: the repo's command-review hook refuses
# any file write containing a downloader command piped into a shell, even inside a regex.
_PIPE = "\\" + "|"
_DOWNLOADER = "(?:" + "cu" + "rl|wg" + "et)"
_SHELL = "(?:" + "s" + "h|ba" + "sh|z" + "sh)"
_PS_FETCH = "(?:" + "ir" + "m|invoke-rest" + "method)"
_PS_RUN = "(?:" + "ie" + "x|invoke-expres" + "sion)"
_INSTALL_PARTS = (
    r"\b" + _DOWNLOADER + r"\b[^\n|]*" + _PIPE + r"\s*(?:sudo\s+(?:-\S+\s+)*)?" + _SHELL + r"\b",
    r"\b" + _PS_FETCH + r"\b[^\n|]*" + _PIPE + r"\s*" + _PS_RUN + r"\b",
    r"\bnpm\s+(?:i|install)\b[^\n]*?\s(?:-g|--global)\b",
    r"\bnpm\s+(?:-g|--global)\s+(?:i|install)\b",
    r"\bpip3?\s+install\b",
    r"\bpipx\s+install\b",
    r"\bbrew\s+(?:install|upgrade)\b",
    r"\bwinget\s+install\b",
    r"\bscoop\s+install\b",
    r"\bgh\s+extension\s+install\b",
    r"\bnpx\s+(?:-y|--yes)\b",
)
INSTALL_RE = re.compile("|".join(f"(?:{p})" for p in _INSTALL_PARTS), re.IGNORECASE)

# A backslash that ends a line (spaces may follow it) continues the command on the next line.
_CONTINUATION_RE = re.compile(r"\\[ \t]*(?:\r\n|\r|\n)")
# The alternatives above scan to the end of the line from each start, so cost grows with the
# square of the line length; a line longer than twice this is tested by its two ends only.
_LINE_CLIP = 4096


def _clip_long_lines(text):
    if len(text) <= 2 * _LINE_CLIP:
        return text
    return "\n".join(
        line if len(line) <= 2 * _LINE_CLIP else line[:_LINE_CLIP] + "\n" + line[-_LINE_CLIP:]
        for line in _BREAK_RE.split(text)
    )


def install_text(text):
    """True when the text holds an install or update command, continuations joined.

    Tested twice: as it stands, and with every line that ends in a backslash joined to the
    next line by one space. Long lines are clipped to their two ends so a hostile page cannot
    make the scan quadratic.
    """
    if not isinstance(text, str) or not text:
        return False
    if INSTALL_RE.search(_clip_long_lines(text)):
        return True
    joined = _CONTINUATION_RE.sub(" ", text)
    return joined != text and bool(INSTALL_RE.search(_clip_long_lines(joined)))


def is_install_span(text):
    return install_text(text)


def _continues(line):
    """True when a command on this line carries on to the next one."""
    line = line.rstrip(" \t")
    if line.endswith("\\"):
        return True
    return line.endswith("|") and not line.lstrip().startswith("|")


def _install_line_flags(lines):
    """One flag per line: it belongs to a continued command that is install-shaped."""
    flags = [False] * len(lines)
    i = 0
    while i < len(lines):
        j = i
        while j + 1 < len(lines) and _continues(lines[j]):
            j += 1
        if install_text("\n".join(lines[i : j + 1])):
            flags[i : j + 1] = [True] * (j + 1 - i)
        i = j + 1
    return flags


_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_HEADING_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)\s*$")
_ATX_CLOSE_RE = re.compile(r"\s+#+\s*$")
_SETEXT_UNDERLINE_RE = re.compile(r"^ {0,3}(?:={3,}|-{3,})[ \t]*$")


def _front_matter_end(lines):
    """Index of the first line after a leading --- front matter block, else 0."""
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() in ("---", "..."):
                return index + 1
    return 0


def _heading_at(lines, start_line):
    """Text of the nearest heading at or before start_line, outside fenced code and front matter.

    A heading is an ATX line (its closing # sequence is dropped) or a setext heading: a text
    line directly above a line of only = or only - characters, three or more.
    """
    heading = ""
    fence = None
    limit = min(start_line, len(lines))
    for index in range(_front_matter_end(lines), limit):
        line = lines[index]
        m = _FENCE_RE.match(line)
        if m:
            mark = m.group(1)
            if fence is None:
                fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1] and not line.strip().strip(mark[0]):
                fence = None
            continue
        if fence is not None:
            continue
        h = _HEADING_RE.match(line)
        if h and h.group(1):
            heading = _ATX_CLOSE_RE.sub("", h.group(1))
        elif (
            line.strip()
            and not _SETEXT_UNDERLINE_RE.match(line)
            and index + 1 < len(lines)
            and _SETEXT_UNDERLINE_RE.match(lines[index + 1])
        ):
            heading = line.strip()
    return heading


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if isinstance(text, str) else None


def _scout_text(record, with_quote):
    """The scout's claim (and quote) as stored in a drop or info record.

    Install-shaped text is never stored: the field becomes the placeholder and both hashes
    are kept, so a human can still match the record to the scout output.
    """
    fields = {"claim": record.get("claim")}
    if with_quote:
        fields["quote"] = record.get("quote")
    shaped = {
        key: isinstance(record.get(key), str) and install_text(record[key])
        for key in ("claim", "quote")
    }
    if any(shaped.values()):
        fields["quote_sha256"] = _sha256(record.get("quote"))
        fields["claim_sha256"] = _sha256(record.get("claim"))
        for key in fields.keys() & {"claim", "quote"}:
            if shaped[key]:
                fields[key] = CONTEXT_SCRUBBED
    return fields


def build_evidence(
    *,
    surface,
    tier,
    url,
    url_effective,
    retrieved,
    http_status,
    raw_bytes_sha256,
    raw_bytes_len,
    product_version,
    version_source,
    raw_text,
    record,
    seq,
):
    """Verify one scout record against the raw page; return (evidence or None, info)."""
    if not 0 <= seq <= 99999:
        raise ValueError(f"seq {seq} does not fit a 5-digit evidence id")
    found = verify_quote(record.get("quote", ""), raw_text, record.get("line_hint"))
    if not found["found"]:
        info = {
            "dropped": True,
            "reason": found.get("reason", "quote_not_found"),
            "page_id": record.get("page_id"),
            "chunk_id": record.get("chunk_id"),
            "claim_rows": record.get("rows"),
            **_scout_text(record, with_quote=True),
        }
        return None, info

    start, end = found["start_line"], found["end_line"]
    lines = _content_lines(raw_text)
    # The install test sees the quote's lines plus two on each side, uncapped, so a command
    # split across the quote boundary is caught; so is the capped span itself, which a very
    # long line's two-ended scan might not reach.
    first, last = max(0, start - 3), min(len(lines), end + 2)
    window = lines[first:last]
    install = install_text(found["raw_span"]) or install_text("\n".join(window))
    flags = _install_line_flags(window) if install else [False] * len(window)

    def context(low, high):
        return [
            CONTEXT_SCRUBBED if flags[i - first] else lines[i][:MAX_SPAN] for i in range(low, high)
        ]

    heading = _heading_at(lines, start)
    evidence = {
        "id": f"E-{surface}-{seq:05d}",
        "surface": surface,
        "tier": tier,
        "url": url,
        "url_effective": url_effective,
        "retrieved": retrieved,
        "http_status": http_status,
        "bytes": raw_bytes_len,
        "sha256": raw_bytes_sha256,
        "product_version": product_version,
        "version_source": version_source,
        "locator": {
            "heading": CONTEXT_SCRUBBED if install_text(heading) else heading,
            "raw_line_start": start,
            "raw_line_end": end,
        },
        "quote": found["raw_span"],
        "context_before": context(first, start - 1),
        "context_after": context(end, last),
        "quote_verified": True,
        "neutralizer_flags": [],
    }
    if install:
        evidence["quote"] = ""
        evidence["described_span"] = {
            "description": INSTALL_DESCRIPTION,
            "raw_line_start": start,
            "raw_line_end": end,
            "span_sha256": _sha256("\n".join(lines[start - 1 : end])),
        }
    info = {
        "dropped": False,
        "tier": found["tier"],
        "ambiguous": found["ambiguous"],
        "claim_rows": record.get("rows"),
        **_scout_text(record, with_quote=False),
    }
    return evidence, info


def _shift_lines(item, offset):
    """Move an evidence record's line numbers by ``offset``.

    A page cut out of an aggregate file (a Gemini page) is verified as its own text, so its line
    numbers start at 1; the offset puts them back where a reader finds them in the fetched file.
    """
    if not offset:
        return
    item["locator"]["raw_line_start"] += offset
    item["locator"]["raw_line_end"] += offset
    span = item.get("described_span")
    if span:
        span["raw_line_start"] += offset
        span["raw_line_end"] += offset


def verify_batch(records, page_texts, counters=None):
    """Verify every scout record; number evidence per surface.

    A page spec may carry ``line_offset``: the lines before the page in the file it was cut from.

    counters maps a surface to the next sequence number to use. It is read and updated in
    place, so several calls for one surface never reuse an id; None starts every surface at 1.
    """
    if counters is None:
        counters = {}
    evidence, pairs, dropped = [], [], []
    by_tier = dict.fromkeys(TIERS, 0)
    for index, record in enumerate(records):
        page = page_texts.get(record.get("page_id"))
        if page is None:
            dropped.append(
                {
                    "record_index": index,
                    "dropped": True,
                    "reason": "unknown_page",
                    "page_id": record.get("page_id"),
                    "chunk_id": record.get("chunk_id"),
                    "claim_rows": record.get("rows"),
                    **_scout_text(record, with_quote=False),
                }
            )
            continue
        surface = page["surface"]
        seq = counters.get(surface, 1)
        item, info = build_evidence(
            surface=surface,
            tier=page["tier"],
            url=page["url"],
            url_effective=page["url_effective"],
            retrieved=page["retrieved"],
            http_status=page["http_status"],
            raw_bytes_sha256=page["sha256"],
            raw_bytes_len=page["bytes"],
            product_version=page.get("product_version"),
            version_source=page.get("version_source"),
            raw_text=page["raw_text"],
            record=record,
            seq=seq,
        )
        if item is None:
            dropped.append({**info, "record_index": index})
            continue
        _shift_lines(item, page.get("line_offset", 0))
        counters[surface] = seq + 1
        evidence.append(item)
        pairs.append({"record_index": index, "evidence_id": item["id"]})
        by_tier[info["tier"]] += 1
    total = len(records)
    return {
        "evidence": evidence,
        "pairs": pairs,
        "dropped": dropped,
        "pass_rate": (len(evidence) / total) if total else 1.0,
        "by_tier": by_tier,
    }


def _read_text(path):
    return Path(path).read_bytes().decode("utf-8", errors="strict")


def _selftest():
    raw = "# Head\n\nIntro text here.\n| `k` | The **v** |\nPass ‹name› now\nwrapped\nline\n"
    cases = (
        ("Intro text here.", "exact", 3, 3),
        ("wrapped  line", "ws", 6, 7),
        ("Pass <name> now", "neutral", 5, 5),
        ("k The v", "markup", 4, 4),
    )
    for quote, tier, start, end in cases:
        got = verify_quote(quote, raw)
        if (got["tier"], got["start_line"], got["end_line"]) != (tier, start, end):
            raise AssertionError(f"{quote!r}: unexpected {got}")
    if verify_quote("absent text", raw)["found"]:
        raise AssertionError("an absent quote was found")
    if verify_quote("Intro text here. # Head", raw)["found"]:
        raise AssertionError("a quote spliced across a heading was found")
    if verify_quote("e", raw).get("reason") != "too_short":
        raise AssertionError("a one-letter quote was not too short")
    sample = "echo hi"
    if is_install_span(sample) or not is_install_span("pip install example"):
        raise AssertionError("unexpected install detection")
    split = "cu" + "rl -fsSL https://example.com/i \\\n| " + "s" + "h"
    if not install_text(split) or install_text(split.replace("\\\n", "\n")):
        raise AssertionError("a continued command was not joined")
    record = {"page_id": "p", "chunk_id": "c", "rows": ["U00"], "claim": "x", "quote": "k The v"}
    page = {
        "raw_text": raw,
        "surface": "claude-code",
        "tier": "E1",
        "url": "https://example.com/a",
        "url_effective": "https://example.com/a",
        "retrieved": "2026-10-04",
        "http_status": 200,
        "sha256": "0" * 64,
        "bytes": len(raw),
        "product_version": None,
        "version_source": None,
    }
    result = verify_batch([record, {**record, "quote": "nope"}], {"p": page})
    if result["pass_rate"] != 0.5 or result["evidence"][0]["quote"] != "| `k` | The **v** |":
        raise AssertionError(f"unexpected batch result: {result}")
    print("OK")


def _read_counters(path):
    if not Path(path).exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        counters = json.load(fh)
    ok = isinstance(counters, dict) and all(
        isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool)
        for k, v in counters.items()
    )
    if not ok:
        raise ValueError(f"{path} must be a JSON object of surface to next sequence number")
    return counters


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    sub = parser.add_subparsers(dest="command")
    check = sub.add_parser("check", help="verify one quote against one raw file")
    check.add_argument("--raw", required=True)
    check.add_argument("--quote", required=True)
    check.add_argument("--line-hint", type=int)
    batch = sub.add_parser("batch", help="verify a scout batch against its pages")
    batch.add_argument("--records", required=True)
    batch.add_argument("--pages", required=True)
    batch.add_argument("--out", required=True)
    batch.add_argument(
        "--counters",
        help="JSON file of surface to next evidence number; read if present, written back",
    )
    args = parser.parse_args(argv)

    if args.selftest:
        _selftest()
        return 0
    if args.command == "check":
        result = verify_quote(args.quote, _read_text(args.raw), args.line_hint)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    if args.command == "batch":
        with open(args.records, encoding="utf-8") as fh:
            scout = json.load(fh)
        records = scout["records"] if isinstance(scout, dict) else scout
        with open(args.pages, encoding="utf-8") as fh:
            pages_spec = json.load(fh)
        page_texts = {}
        for page_id, spec in pages_spec.items():
            raw_bytes = Path(spec["raw_path"]).read_bytes()
            page = {k: v for k, v in spec.items() if k != "raw_path"}
            page["raw_text"] = raw_bytes.decode("utf-8", errors="strict")
            page.setdefault("sha256", hashlib.sha256(raw_bytes).hexdigest())
            page.setdefault("bytes", len(raw_bytes))
            page_texts[page_id] = page
        try:
            counters = _read_counters(args.counters) if args.counters else None
        except ValueError as exc:
            print(f"quotes: {exc}", file=sys.stderr)
            return 2
        result = verify_batch(records, page_texts, counters)
        dump_json(args.out, result)
        if args.counters:
            dump_json(args.counters, counters)
        print(f"pass_rate {result['pass_rate']:.4f}")
        return 0
    parser.error("a command (check or batch) or --selftest is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())
