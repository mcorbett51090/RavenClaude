"""Drift checks for a finished atlas: quotes, page additions and changelog entries.

presence   re-check stored evidence against a fresh fetch: unchanged page, quote still
           present, quote drifted, install span unchanged or changed, or page gone
addition   compare the set of mirrored URLs against a baseline
changelog  list changelog entries newer than a date that mention any of the given terms

Usage: python3 reverify.py presence --evidence FILE --pages FILE
       python3 reverify.py addition --baseline FILE --current FILE
       python3 reverify.py changelog --raw FILE --since YYYY-MM-DD --term REGEX [--term REGEX ...]
       python3 reverify.py --selftest
"""

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

from atlas_common import assert_worktree
from quotes import lines_text, split_lines, verify_quote

STATUSES = (
    "ok",
    "quote_present",
    "span_unchanged",
    "span_changed",
    "drifted",
    "page_missing",
)
_DRIFT_STATUSES = ("drifted", "span_changed")


def check_quote_presence(evidence, pages):
    """Classify each evidence record against a fresh fetch of its page.

    pages maps URL to {"raw_text", "sha256"}. drifted_ids lists records a human must
    re-check: a quote that is gone ("drifted") and an install span whose lines changed
    ("span_changed").
    """
    counts = dict.fromkeys(STATUSES, 0)
    status_by_id = {}
    drifted_ids, missing_ids = [], []
    for ev in evidence:
        page = pages.get(ev["url"])
        if page is None:
            status = "page_missing"
        elif page["sha256"] == ev["sha256"]:
            status = "ok"
        elif ev.get("described_span"):
            span = ev["described_span"]
            # The hash covers the whole lines of the range, never a capped span, so a change
            # anywhere in a long install line is seen.
            current = lines_text(page["raw_text"], span["raw_line_start"], span["raw_line_end"])
            same = hashlib.sha256(current.encode("utf-8")).hexdigest() == span["span_sha256"]
            status = "span_unchanged" if same else "span_changed"
        elif verify_quote(ev.get("quote", ""), page["raw_text"])["found"]:
            status = "quote_present"
        else:
            status = "drifted"
        counts[status] += 1
        status_by_id[ev["id"]] = status
        if status in _DRIFT_STATUSES:
            drifted_ids.append(ev["id"])
        elif status == "page_missing":
            missing_ids.append(ev["id"])
    return {
        "counts": counts,
        "drifted_ids": drifted_ids,
        "page_missing_ids": missing_ids,
        "status_by_id": status_by_id,
    }


def _url_digest(urls):
    return hashlib.sha256("\n".join(urls).encode("utf-8")).hexdigest()


def addition_drift(baseline_urls, current_urls):
    """Added and removed URLs; each digest is over the sorted, de-duplicated list."""
    baseline, current = sorted(set(baseline_urls)), sorted(set(current_urls))
    return {
        "added": sorted(set(current) - set(baseline)),
        "removed": sorted(set(baseline) - set(current)),
        "baseline_sha256": _url_digest(baseline),
        "current_sha256": _url_digest(current),
    }


_MONTH_WORDS = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?"
    r"|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
_MONTH_NUMBER = {
    m: i
    for i, m in enumerate(
        ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1
    )
}
_ISO_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_MDY_RE = re.compile(
    r"\b(" + _MONTH_WORDS + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", re.IGNORECASE
)
_DMY_RE = re.compile(
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + _MONTH_WORDS + r")\.?,?\s+(\d{4})\b", re.IGNORECASE
)
_HEADING_LINE_RE = re.compile(r"^\s*#{1,6}\s")
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_LEAD_MARKUP = " \t*_|`>[(~"
# A version token may sit between the bullet marker and the date: "v1.2.3 - 2026-09-01".
_VERSION_LEAD_RE = re.compile(
    r"v?\d+(?:\.\d+)+(?:[-+.][0-9a-z.]+)*\s*[-\u2013\u2014:]?", re.IGNORECASE
)


def _valid(year, month, day):
    try:
        return datetime.date(int(year), month, int(day))
    except ValueError:
        return None


def _first_date(line):
    """(start offset, date) of the leftmost valid date in the line, or None."""
    found = []
    for rx, order in ((_ISO_RE, "ymd"), (_MDY_RE, "mdy"), (_DMY_RE, "dmy")):
        for m in rx.finditer(line):
            a, b, c = m.groups()
            if order == "ymd":
                parts = (a, int(b), c)
            elif order == "mdy":
                parts = (c, _MONTH_NUMBER[a[:3].lower()], b)
            else:
                parts = (c, _MONTH_NUMBER[b[:3].lower()], a)
            d = _valid(*parts)
            if d is not None:
                found.append((m.start(), d))
                break
    return min(found) if found else None


def _entry_start(line):
    """The entry date when this line starts an entry, else None.

    A heading containing a date anywhere starts an entry. Any other line starts one only when
    the date leads it: directly after a bullet marker if there is one, then after Markdown
    emphasis, table markup or a version token (a bullet, a bare date line or a table row).
    A bullet that merely mentions a date does not.
    """
    hit = _first_date(line)
    if hit is None:
        return None
    start, date = hit
    if _HEADING_LINE_RE.match(line):
        return date
    bullet = _BULLET_RE.match(line)
    lead = line[bullet.end() if bullet else 0 : start].strip(_LEAD_MARKUP)
    if not lead or _VERSION_LEAD_RE.fullmatch(lead):
        return date
    return None


def scan_changelog(raw_text, since_date, terms):
    """Entries dated strictly after since_date whose text matches at least one term."""
    since = datetime.date.fromisoformat(since_date)
    try:
        term_res = [(t, re.compile(t, re.IGNORECASE)) for t in terms]
    except re.error as exc:
        raise ValueError(f"invalid regular expression in terms: {exc}") from exc
    lines = split_lines(raw_text)
    starts = []
    for number, line in enumerate(lines, 1):
        date = _entry_start(line)
        if date is not None:
            starts.append((number, date))
    entries = []
    for i, (number, date) in enumerate(starts):
        end = starts[i + 1][0] - 1 if i + 1 < len(starts) else len(lines)
        if date <= since:
            continue
        text = "\n".join(lines[number - 1 : end])
        matched = [t for t, rx in term_res if rx.search(text)]
        if matched:
            entries.append(
                {
                    "date": date.isoformat(),
                    "start_line": number,
                    "end_line": end,
                    "matched_terms": matched,
                    "first_line": lines[number - 1].strip()[:300],
                }
            )
    return entries


def _selftest():
    rec = {
        "id": "E-cursor-00001",
        "url": "https://example.com/a",
        "sha256": "1" * 64,
        "quote": "kept line",
    }
    pages = {"https://example.com/a": {"raw_text": "x\nkept line\n", "sha256": "2" * 64}}
    got = check_quote_presence([rec], pages)
    if got["counts"]["quote_present"] != 1 or got["drifted_ids"]:
        raise AssertionError(f"unexpected presence result: {got}")
    gone = check_quote_presence([rec], {"https://example.com/a": {"raw_text": "y", "sha256": "3"}})
    if gone["drifted_ids"] != ["E-cursor-00001"]:
        raise AssertionError(f"unexpected drift result: {gone}")
    drift = addition_drift(["https://a", "https://b"], ["https://b", "https://c"])
    if drift["added"] != ["https://c"] or drift["removed"] != ["https://a"]:
        raise AssertionError(f"unexpected addition drift: {drift}")
    log = "## 1.0.0 (2026-01-01)\nold sandbox change\n## 1.1.0 (2026-03-02)\nnew sandbox change\n"
    found = scan_changelog(log, "2026-01-01", ["sandbox"])
    if [(e["date"], e["start_line"], e["end_line"]) for e in found] != [("2026-03-02", 3, 4)]:
        raise AssertionError(f"unexpected changelog entries: {found}")
    print("OK")


def _load_pages(path):
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    pages = {}
    for url, item in spec.items():
        if "raw_text" in item:
            raw_bytes = item["raw_text"].encode("utf-8")
        else:
            raw_bytes = Path(item["raw_path"]).read_bytes()
        pages[url] = {
            "raw_text": raw_bytes.decode("utf-8", errors="strict"),
            "sha256": item.get("sha256") or hashlib.sha256(raw_bytes).hexdigest(),
        }
    return pages


def _read_urls(path):
    text = Path(path).read_bytes().decode("utf-8", errors="strict")
    return [line.strip() for line in text.splitlines() if line.strip()]


def _print(obj):
    print(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False))


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    sub = parser.add_subparsers(dest="command")
    presence = sub.add_parser("presence")
    presence.add_argument("--evidence", required=True)
    presence.add_argument("--pages", required=True)
    addition = sub.add_parser("addition")
    addition.add_argument("--baseline", required=True)
    addition.add_argument("--current", required=True)
    changelog = sub.add_parser("changelog")
    changelog.add_argument("--raw", required=True)
    changelog.add_argument("--since", required=True)
    changelog.add_argument("--term", action="append", required=True)
    args = parser.parse_args(argv)

    if args.selftest:
        _selftest()
        return 0
    if args.command == "presence":
        with open(args.evidence, encoding="utf-8") as fh:
            evidence = json.load(fh)
        if isinstance(evidence, dict):
            evidence = evidence["evidence"]
        _print(check_quote_presence(evidence, _load_pages(args.pages)))
        return 0
    if args.command == "addition":
        _print(addition_drift(_read_urls(args.baseline), _read_urls(args.current)))
        return 0
    if args.command == "changelog":
        raw = Path(args.raw).read_bytes().decode("utf-8", errors="strict")
        try:
            _print(scan_changelog(raw, args.since, args.term))
        except ValueError as exc:
            print(f"reverify: {exc}", file=sys.stderr)
            return 2
        return 0
    parser.error("a command (presence, addition or changelog) or --selftest is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())
