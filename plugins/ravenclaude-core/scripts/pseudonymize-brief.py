#!/usr/bin/env python3
"""pseudonymize-brief.py — structured-PII tokenizer for the relay-all egress path.

This is layer **A** of the orchestrator relay-all data-governance guard (the
deterministic egress floor in `claude-orchestrate.sh` is layer **C**). It is an
OPTIONAL defense-in-depth layer, never the sole guard: see
`plugins/ravenclaude-core/knowledge/orchestrator-data-egress.md`.

What it does:
  encode  — read text from stdin, replace each *structured* PII value with a
            stable opaque token, write a token->original map (JSON) to --map-file,
            print the tokenized text to stdout. The map NEVER leaves the local
            scratch dir; only the tokenized text egresses.
  decode  — read text from stdin, substitute tokens back to their originals using
            --map-file, print the restored text to stdout.

HONEST LIMITS (printed in the knowledge file and on the dashboard toggle):
  - Detects only RELIABLY-SHAPED PII: email, US SSN (dashed), Luhn-valid card
    numbers, IBAN, and clearly-formatted phone numbers, plus any consumer-supplied
    regexes via --patterns-file. It does NOT reliably catch free-text names,
    addresses, or bare account numbers — pattern detection cannot. A miss leaks the
    real value. This is exactly why layer C (the deterministic floor) sits beneath
    this layer and this layer is never the only guard.
  - Conservative by design: bare integers (amounts, years, IDs) are NOT tokenized,
    so the relayed brief stays useful. Over-tokenizing would gut the brief.

Stdlib-only. Fail-safe: on any internal error the encode path writes NOTHING to
stdout and exits non-zero — the caller (claude-orchestrate.sh) MUST treat a
non-zero exit from the pseudonymizer as "do not egress" (fail closed). Writing
nothing (rather than echoing the raw input) is deliberate: it guarantees a
tokenizer fault can never cause un-tokenized PII to reach stdout for a caller that
captures output without checking the exit code.
"""

import argparse
import json
import os
import re
import sys

# ── Built-in structured-PII patterns, in priority order ─────────────────────────
# Earlier entries win on overlap. Each entry: (label, compiled regex, validator|None).
# A validator(str)->bool lets a shape-match (e.g. 13-19 digits) be confirmed (Luhn)
# before it is treated as PII, cutting false positives.


def _luhn_ok(s: str) -> bool:
    digits = [int(c) for c in s if c.isdigit()]
    if not (13 <= len(digits) <= 19):
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


# Order matters: email and SSN before the card/phone numeric shapes so a dashed
# SSN is not eaten by a looser numeric matcher.
_BUILTIN = [
    (
        "EMAIL",
        re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
        None,
    ),
    (
        "SSN",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        None,
    ),
    (
        "IBAN",
        re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
        None,
    ),
    (
        # 13-19 digits, optionally separated by single spaces or hyphens; Luhn-gated.
        "CARD",
        re.compile(r"\b(?:\d[ \-]?){12,18}\d\b"),
        _luhn_ok,
    ),
    (
        # Clearly-formatted phone: optional +country, then a 3-3-4 group (parens or
        # separators). The 3-3-4 shape is phone-specific — it structurally cannot
        # match an SSN (3-2-4) or a card group (4-4-4-4), so those don't collide.
        # Bare runs of digits and other groupings are intentionally NOT matched.
        "PHONE",
        re.compile(
            r"(?<!\d)(?:\+\d{1,3}[ .\-]?)?(?:\(\d{3}\)[ .\-]?|\d{3}[ .\-])"
            r"\d{3}[ .\-]\d{4}(?!\d)"
        ),
        None,
    ),
]


def _load_extra(patterns_file):
    """Read consumer-supplied regexes (one per line, blank/# lines ignored)."""
    out = []
    if not patterns_file:
        return out
    try:
        with open(patterns_file, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln or ln.startswith("#"):
                    continue
                try:
                    out.append(("CUSTOM", re.compile(ln), None))
                except re.error:
                    # A bad consumer regex is skipped, not fatal.
                    continue
    except OSError:
        pass
    return out


def _find_spans(text, patterns):
    """Collect non-overlapping (start, end, label, value) spans by priority."""
    claimed = []  # list of (start, end)

    def overlaps(s, e):
        for cs, ce in claimed:
            if s < ce and cs < e:
                return True
        return False

    spans = []
    for label, rx, validator in patterns:
        for m in rx.finditer(text):
            s, e = m.start(), m.end()
            val = m.group(0)
            if validator and not validator(val):
                continue
            if overlaps(s, e):
                continue
            claimed.append((s, e))
            spans.append((s, e, label, val))
    spans.sort(key=lambda t: t[0])
    return spans


def _token(label, n, nonce):
    # Opaque, model-stable token. Underscored + nonce so it is unlikely to collide
    # with real text and survives being echoed back in the model's content.
    return f"__PII_{label}_{nonce}_{n}__"


def encode(text, map_file, patterns_file=None):
    patterns = _BUILTIN + _load_extra(patterns_file)
    spans = _find_spans(text, patterns)
    nonce = os.urandom(4).hex()
    value_to_token = {}
    counter = {}
    # Replace right-to-left so earlier offsets stay valid.
    out = text
    for s, e, label, val in sorted(spans, key=lambda t: t[0], reverse=True):
        tok = value_to_token.get(val)
        if tok is None:
            n = counter.get(label, 0)
            counter[label] = n + 1
            tok = _token(label, n, nonce)
            value_to_token[val] = tok
        out = out[:s] + tok + out[e:]
    token_to_value = {tok: val for val, tok in value_to_token.items()}
    # The token->value map is the one artifact holding cleartext PII — create it
    # 0600 from the start (not a post-write chmod) so it is never briefly world-readable.
    fd = os.open(map_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(token_to_value, fh)
    return out


def decode(text, map_file):
    try:
        with open(map_file, encoding="utf-8") as fh:
            token_to_value = json.load(fh)
    except (OSError, ValueError):
        # No map / unreadable map -> nothing to restore; return text unchanged.
        return text
    # Longest tokens first so no token is a prefix of another during replace.
    for tok in sorted(token_to_value, key=len, reverse=True):
        text = text.replace(tok, token_to_value[tok])
    return text


def _self_test():
    sample = (
        "Email jane.doe@acme.com, SSN 123-45-6789, card 4111 1111 1111 1111, "
        "call +1 (415) 555-2671. Amount 4200 in 2026 is not PII."
    )
    import tempfile

    d = tempfile.mkdtemp()
    mp = os.path.join(d, "map.json")
    enc = encode(sample, mp)
    assert "jane.doe@acme.com" not in enc, "email leaked"
    assert "123-45-6789" not in enc, "ssn leaked"
    assert "4111 1111 1111 1111" not in enc, "card leaked"
    assert "555-2671" not in enc, "phone leaked"
    # conservative: bare amounts/years preserved
    assert "4200" in enc, "amount over-tokenized"
    assert "2026" in enc, "year over-tokenized"
    # round-trip
    dec = decode(enc, mp)
    assert dec == sample, "round-trip mismatch:\n%r\n%r" % (dec, sample)
    # an invalid (non-Luhn) 16-digit run is NOT tokenized
    bad = encode("num 1234567890123456 here", os.path.join(d, "m2.json"))
    assert "1234567890123456" in bad, "non-Luhn number tokenized"
    print("pseudonymize-brief self-test: OK")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Structured-PII tokenizer (layer A).")
    sub = ap.add_subparsers(dest="cmd")
    pe = sub.add_parser("encode")
    pe.add_argument("--map-file", required=True)
    pe.add_argument("--patterns-file", default=None)
    pd = sub.add_parser("decode")
    pd.add_argument("--map-file", required=True)
    sub.add_parser("self-test")
    args = ap.parse_args(argv)

    if args.cmd == "self-test":
        return _self_test()
    if args.cmd == "encode":
        text = sys.stdin.read()
        try:
            sys.stdout.write(encode(text, args.map_file, args.patterns_file))
            return 0
        except Exception as exc:  # fail closed: caller must NOT egress on nonzero
            sys.stderr.write(f"pseudonymize-brief encode failed: {exc}\n")
            # Write NOTHING to stdout. The old behavior echoed the raw, untokenized
            # input here — so a caller capturing stdout without checking $? (e.g.
            # `out=$(... encode ...)` lacking `|| abort`) received raw PII and could
            # forward it. An empty relay brief is strictly safer and still signals
            # failure via the nonzero exit.
            return 1
    if args.cmd == "decode":
        text = sys.stdin.read()
        try:
            sys.stdout.write(decode(text, args.map_file))
            return 0
        except Exception as exc:
            sys.stderr.write(f"pseudonymize-brief decode failed: {exc}\n")
            sys.stdout.write(text)
            return 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
