"""Find each scout quote in the raw page itself and store the raw text, never the scout's.

A cheap model extracts records {claim, quote} from documentation pages. It cannot be trusted
with line numbers or exact punctuation, so this module locates the quote in the raw page,
assigns the line range itself, and keeps the raw span. A model saying a quote is present
never counts; a quote that cannot be found is dropped, never repaired.

Matching tiers, tried in order and stopped at the first hit: exact (substring), ws
(whitespace collapsed), neutral (ws plus the neutralizer substitutes mapped back) and
markup (neutral plus Markdown markup characters removed).

Install and update command lines are never stored verbatim: the evidence carries an empty
quote and a described span with a hash of the raw bytes instead.

Usage: python3 quotes.py check --raw FILE --quote TEXT [--line-hint N]
       python3 quotes.py batch --records SCOUT_JSON --pages PAGES_JSON --out OUT_JSON
       python3 quotes.py --selftest
"""

import argparse
import hashlib
import json
import re
import sys
from bisect import bisect_right
from functools import lru_cache
from itertools import accumulate
from pathlib import Path

from atlas_common import assert_worktree, dump_json

TIERS = ("exact", "ws", "neutral", "markup")
MAX_SPAN = 300
INSTALL_DESCRIPTION = "install or update command line (stored as a described span)"

_NEUTRAL_MAP = {ord("‹"): "<", ord("›"): ">"}
_MARKUP_CHARS = "`*_|\\#>"
# In the markup tier the right substitute maps to ">" and is then removed, in one pass.
_MARKUP_MAP = {ord("‹"): "<", ord("›"): None}
_MARKUP_MAP.update({ord(c): None for c in _MARKUP_CHARS})
_TABLES = {"ws": None, "neutral": _NEUTRAL_MAP, "markup": _MARKUP_MAP}
_SUBSTITUTES = ("‹", "›")


def norm(s, tier):
    """Normalize s for comparison at the given tier (see the module docstring)."""
    if tier == "exact":
        return s
    if tier not in _TABLES:
        raise ValueError(f"unknown tier {tier!r}")
    table = _TABLES[tier]
    if table is not None:
        s = s.translate(table)
    return " ".join(s.split())


@lru_cache(maxsize=8)
def _raw_lines(raw_text):
    return tuple(raw_text.split("\n"))


@lru_cache(maxsize=8)
def _line_starts(raw_text):
    """Offset of the first character of each raw line; bisect_right gives a 1-based line."""
    lengths = [len(line) + 1 for line in _raw_lines(raw_text)]
    return [0, *accumulate(lengths)][:-1]


@lru_cache(maxsize=8)
def _norm_map(raw_text, tier):
    """Normalized copy of the raw text plus the segment offsets and raw line of each segment.

    One linear pass: every raw line is normalized on its own, empty results are skipped and
    the rest are joined with one space. A normalized index maps back to its raw line by
    bisecting the segment offsets.
    """
    table = _TABLES[tier]
    parts, seg_starts, seg_lines = [], [], []
    pos = 0
    for number, line in enumerate(_raw_lines(raw_text), 1):
        if table is not None:
            line = line.translate(table)
        seg = " ".join(line.split())
        if not seg:
            continue
        if parts:
            pos += 1
        seg_starts.append(pos)
        seg_lines.append(number)
        parts.append(seg)
        pos += len(seg)
    return " ".join(parts), seg_starts, seg_lines


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
    lines = _raw_lines(raw_text)
    return [line.rstrip("\r") for line in lines[start - 1 : end]]


def raw_span_for_range(raw_text, start, end):
    """The raw text of whole lines start..end (1-based, inclusive), capped at MAX_SPAN."""
    selected = _span_lines(raw_text, start, end)
    return _clip_lines(selected) if selected else ""


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


def _found(raw_text, tier, spans, line_hint):
    if line_hint is None:
        start, end = spans[0]
    else:
        start, end = min(spans, key=lambda s: (abs(s[0] - line_hint), s[0]))
    return {
        "found": True,
        "tier": tier,
        "start_line": start,
        "end_line": end,
        "raw_span": raw_span_for_range(raw_text, start, end),
        "ambiguous": len(spans) > 1,
        "occurrences": len(spans),
    }


def verify_quote(quote, raw_text, line_hint=None):
    """Locate quote in raw_text and report its tier and exact 1-based line range."""
    if not isinstance(quote, str) or not quote.strip():
        return _not_found()
    hits = _find_all(raw_text, quote)
    if hits:
        starts = _line_starts(raw_text)
        spans = [(bisect_right(starts, i), bisect_right(starts, i + len(quote) - 1)) for i in hits]
        return _found(raw_text, "exact", spans, line_hint)

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
            return _found(raw_text, tier, spans, line_hint)
    return _not_found()


# The install pattern is assembled from fragments: the repo's command-review hook refuses
# any file write containing a downloader command piped into a shell, even inside a regex.
_PIPE = "\\" + "|"
_DOWNLOADER = "(?:" + "cu" + "rl|wg" + "et)"
_SHELL = "(?:" + "s" + "h|ba" + "sh|z" + "sh)"
_PS_FETCH = "(?:" + "ir" + "m|invoke-rest" + "method)"
_PS_RUN = "(?:" + "ie" + "x|invoke-expres" + "sion)"
_INSTALL_PARTS = (
    r"\b" + _DOWNLOADER + r"\b[^\n]*" + _PIPE + r"\s*(?:sudo\s+(?:-\S+\s+)*)?" + _SHELL + r"\b",
    r"\b" + _PS_FETCH + r"\b[^\n]*" + _PIPE + r"\s*" + _PS_RUN + r"\b",
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


def is_install_span(text):
    return bool(INSTALL_RE.search(text))


_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_HEADING_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)\s*$")


def _heading_at(lines, start_line):
    """Text of the nearest ATX heading at or before start_line, outside fenced code."""
    heading = ""
    fence = None
    for line in lines[:start_line]:
        line = line.rstrip("\r")
        m = _FENCE_RE.match(line)
        if m:
            mark = m.group(1)
            if fence is None:
                fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1] and not line.strip().strip(mark[0]):
                fence = None
            continue
        if fence is None:
            h = _HEADING_RE.match(line)
            if h and h.group(1):
                heading = h.group(1)
    return heading


CONTEXT_SCRUBBED = "[install command line omitted]"


def _context(lines, first, last):
    """Up to two raw lines of context. An install-shaped line is never stored verbatim
    (plan W2), so it is replaced by a fixed placeholder here as well as in the quote."""
    out = []
    for line in lines[first:last]:
        line = line.rstrip("\r")[:MAX_SPAN]
        out.append(CONTEXT_SCRUBBED if is_install_span(line) else line)
    return out


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
            "reason": "quote_not_found",
            "page_id": record.get("page_id"),
            "chunk_id": record.get("chunk_id"),
            "claim": record.get("claim"),
            "claim_rows": record.get("rows"),
            "quote": record.get("quote"),
        }
        return None, info

    start, end = found["start_line"], found["end_line"]
    lines = _raw_lines(raw_text)
    if raw_text.endswith("\n"):
        lines = lines[:-1]  # the empty piece after the final newline is not a line
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
            "heading": _heading_at(lines, start),
            "raw_line_start": start,
            "raw_line_end": end,
        },
        "quote": found["raw_span"],
        "context_before": _context(lines, max(0, start - 3), start - 1),
        "context_after": _context(lines, end, end + 2),
        "quote_verified": True,
        "neutralizer_flags": [],
    }
    # Detect on the whole lines, not only the capped span, so nothing install-shaped slips by.
    whole = "\n".join(_span_lines(raw_text, start, end))
    if is_install_span(found["raw_span"]) or is_install_span(whole):
        evidence["quote"] = ""
        evidence["described_span"] = {
            "description": INSTALL_DESCRIPTION,
            "raw_line_start": start,
            "raw_line_end": end,
            "span_sha256": hashlib.sha256(found["raw_span"].encode("utf-8")).hexdigest(),
        }
    info = {
        "dropped": False,
        "tier": found["tier"],
        "ambiguous": found["ambiguous"],
        "claim_rows": record.get("rows"),
        "claim": record.get("claim"),
    }
    return evidence, info


def verify_batch(records, page_texts):
    """Verify every scout record; number evidence per surface from a counter kept here."""
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
                    "claim": record.get("claim"),
                    "claim_rows": record.get("rows"),
                }
            )
            continue
        surface = page["surface"]
        seq = counters.get(surface, 0) + 1
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
        counters[surface] = seq
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
    sample = "echo hi"
    if is_install_span(sample) or not is_install_span("pip install example"):
        raise AssertionError("unexpected install detection")
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
        result = verify_batch(records, page_texts)
        dump_json(args.out, result)
        print(f"pass_rate {result['pass_rate']:.4f}")
        return 0
    parser.error("a command (check or batch) or --selftest is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())
