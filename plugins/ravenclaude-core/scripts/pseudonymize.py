#!/usr/bin/env python3
"""pseudonymize.py — reversible NAME/ENTITY pseudonymizer for text going to a model.

A user-facing companion to `pseudonymize-brief.py` (the orchestrator's structured-PII
egress guard). Where the brief tool catches only reliably-SHAPED PII (email/SSN/card/
IBAN/phone), this tool adds the piece a controller actually asked for: **names and
entities**. It is a *generalize-on-top-of*, not an edit — it imports the brief tool's
audited pattern table + token machinery and leaves that file byte-stable.

Subcommands (a SUPERSET of the brief tool's CLI — same encode/decode/--map-file shape):
  encode  — read text from stdin, replace (a) every KNOWN entity you list in
            --entities-file, (b) structured PII (reused from the brief tool), and
            (optionally, --ner) unknown names via a lazily-imported NER model, each
            with a stable opaque token. Writes the token->original map (JSON, 0600)
            to --map-file and prints the tokenized text to stdout. The map NEVER
            egresses.
  decode  — read text from stdin (e.g. the model's reply), restore tokens to their
            originals via --map-file, tolerant of wrap/markdown mangling.
  scan    — residual-leak review aid: fuzzy-match your listed entities against text
            and re-run the structured patterns, emitting a COVERAGE ENVELOPE and
            REVIEW ITEMS. It never emits a "safe" verdict.
  self-test — built-in fixtures.

═══════════════════════════════════════════════════════════════════════════════════
HONEST LIMITS — read before trusting this (printed by `scan` and in the skill):
  • This PSEUDONYMIZES (reversible, key retained). It does NOT anonymize. The mapping
    is re-identifiable and remains personal data.
  • The DENYLIST is reliable for the exact terms you list — 100% of *listed* terms,
    and the completeness of that list is entirely on you. Any UNLISTED name, variant,
    abbreviation, or spelling LEAKS.
  • The optional NER layer is BEST-EFFORT: it misses rare names, common-word names,
    typos, lowercase, and names inside IDs/emails. Never treat it as complete.
  • Masking names is NOT sufficient — quasi-identifier COMBINATIONS (rare role + city
    + salary; org chart; rare condition) re-identify even with perfect name masking.
  • The VAULT (--map-file) is the crown jewel: in reversible mode the whole guarantee
    collapses to that one file staying secret. Vault compromise = total, instant
    de-anonymization of everything ever tokenized. Keep it 0600, out of git, out of
    any model prompt.
  • There is deliberately NO "safe"/"redacted" badge. A clean scan means "found
    nothing among the things I already know to look for" — read the actual text.

Stdlib-only on the default path (NER is imported ONLY when --ner is passed). Fail-safe:
on any ENCODE error, writes NOTHING to stdout and exits nonzero (fail closed) — a caller
capturing stdout without checking the exit code can never receive un-tokenized text.
"""

import argparse
import difflib
import importlib.util
import json
import os
import re
import sys
import unicodedata

# ── Reuse the brief tool's audited structured-PII table + token machinery ───────────
# The filename is hyphenated, so import it by path rather than `import`.
_HERE = os.path.dirname(os.path.abspath(__file__))
_BRIEF_PATH = os.path.join(_HERE, "pseudonymize-brief.py")


def _load_brief():
    spec = importlib.util.spec_from_file_location("pseudonymize_brief", _BRIEF_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # defines functions/patterns; __main__ guard prevents CLI
    return mod


_brief = _load_brief()
_BUILTIN = _brief._BUILTIN  # [(label, compiled_regex, validator|None), ...]
_token = _brief._token  # (label, n, nonce) -> "__PII_{label}_{nonce}_{n}__"
_load_extra = _brief._load_extra  # consumer --patterns-file loader


class NerUnavailable(Exception):
    """--ner was requested but no NER backend is installed. Distinct, non-suppressible."""


# ── Homoglyph fold (FM3) ────────────────────────────────────────────────────────────
# A curated, 1:1-character map of the most common cross-script look-alikes to their
# Latin equivalent, so "Аcme" (Cyrillic А) matches a denylist entry "Acme". The 1:1 (length-preserving) property that keeps match offsets valid against the
# ORIGINAL text is ENFORCED by _fold_char (it never expands a char).
# HONEST LIMIT: this is a curated subset, NOT a full Unicode confusables table — an
# exotic look-alike can still bypass it. Stated in the coverage report + the skill.
_CONFUSABLES = {
    # Cyrillic -> Latin
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O",
    "Р": "P", "С": "C", "Т": "T", "Х": "X", "а": "a", "е": "e", "о": "o",
    "с": "c", "р": "p", "х": "x", "у": "y", "ѕ": "s", "і": "i", "ј": "j",
    # Greek -> Latin
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I", "Κ": "K",
    "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T", "Υ": "Y", "Χ": "X",
    "ο": "o", "ν": "v",
    # dotted capital I (Turkish) — folds 1:1 after the _fold_char length guard
    "İ": "I",
}


def _fold_char(ch):
    ch = _CONFUSABLES.get(ch, ch)
    low = ch.lower()
    # 1:1 alignment is load-bearing: match offsets on the fold slice the ORIGINAL text.
    # Some chars expand when lower-cased (U+0130 'İ' -> 'i' + U+0307). Never expand —
    # returning the original (a COVERAGE miss) is fail-safe; an offset shift LEAKS.
    return low if len(low) == 1 else ch


def _fold_view(text):
    """A 1:1 (offset-aligned) case+homoglyph-folded view of text, for matching only."""
    return "".join(_fold_char(c) for c in text)


# ── Denylist (FM1, FM2) ─────────────────────────────────────────────────────────────
_POSS = r"(?:['’]s)?"  # optional possessive: Acme's / Acme’s


def _entity_regex(entity):
    """Word-boundary-anchored, whitespace-flexible, possessive-tolerant pattern for one
    entity, built against the FOLDED view (so `entity` is pre-folded by the caller)."""
    words = entity.split()
    body = r"\s+".join(re.escape(w) for w in words)
    # (?<!\w)…(?!\w) prevents "Al" matching inside "Alabama" (FM2).
    return re.compile(r"(?<!\w)" + body + _POSS + r"(?!\w)")


def _load_entities(entities_file):
    """One entity per line. Blank/`#` ignored. Optional `entity | LABEL` (default NAME).
    1-char entities are REJECTED with a warning (FM2 over-match guard). Returns a list of
    (entity_original, folded, label), sorted longest-folded-first so multi-word beats
    its prefix. Raises OSError if the file itself is unreadable (caller fails closed)."""
    out = []
    with open(entities_file, encoding="utf-8") as fh:  # OSError -> caller fails closed
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                ent, _, label = line.rpartition("|")
                ent, label = ent.strip(), label.strip().upper() or "NAME"
            else:
                ent, label = line, "NAME"
            if len(ent) < 2:
                sys.stderr.write(
                    f"pseudonymize: SKIPPING 1-char denylist entry {ent!r} "
                    "(would over-match inside other words).\n"
                )
                continue
            if not re.fullmatch(r"[A-Za-z]+", label):
                label = "NAME"
            out.append((ent, _fold_view(ent), label))
    out.sort(key=lambda t: len(t[1]), reverse=True)
    return out


# ── NER adapter (FM7) — imported ONLY here, ONLY when --ner is passed ────────────────
def _ner_spans(text):
    """Yield (start, end, label, value) for PERSON/ORG/GPE via spaCy, if installed.
    Raises NerUnavailable (never silently returns nothing) when the backend is absent."""
    try:
        import spacy  # noqa: F401  (lazy — never imported on the default path)
    except ImportError as exc:
        raise NerUnavailable(
            "spaCy is not installed. Install a NER backend "
            "(`pip install spacy && python -m spacy download en_core_web_lg`) "
            "or run without --ner (denylist + structured only)."
        ) from exc
    try:
        nlp = spacy.load("en_core_web_lg")
    except OSError as exc:
        raise NerUnavailable(
            "spaCy is installed but no English model is present. "
            "Run `python -m spacy download en_core_web_lg`."
        ) from exc
    keep = {"PERSON": "NAME", "ORG": "ORG", "GPE": "GPE", "LOC": "LOC"}
    for ent in nlp(text).ents:
        if ent.label_ in keep:
            yield (ent.start_char, ent.end_char, keep[ent.label_], ent.text)


# ── Realistic surrogates (optional; FM4) ────────────────────────────────────────────
# Clearly-fictional pool, disjoint from real-name space, keyed deterministically by a
# salted hash of the value. Collisions vs the denylist/input are re-drawn. When used,
# the substitution manifest is printed to stderr so a reviewer can still tell a
# surrogate from an un-replaced real name (overclaim #2).
_FAKE_NAMES = [
    "Quillon Vasp", "Marent Dolo", "Sable Krenn", "Ovid Marne", "Tessa Vane",
    "Doran Fick", "Lira Osk", "Bram Teel", "Neve Calder", "Ivo Renn",
    "Sasha Wold", "Piety Lund", "Orin Vex", "Mira Sol", "Kane Ferro",
]
_FAKE_ORGS = [
    "Vantridge Systems", "Okra Dynamics", "Perrell & Voss", "Nimbus Fell Co",
    "Trellon Group", "Yarrow Labs", "Castle Peak Holdings", "Draymoor Inc",
]


def _surrogate(value, label, salt, taken, banned):
    pool = _FAKE_ORGS if label in ("ORG",) else _FAKE_NAMES
    h = int(__import__("hashlib").sha256((salt + "\x00" + value).encode()).hexdigest(), 16)
    for i in range(len(pool)):
        cand = pool[(h + i) % len(pool)]
        if cand not in taken and cand.lower() not in banned:
            return cand
    # Pool exhausted / all collide -> fall back to an opaque marker (never a real name).
    return None


# ── encode ──────────────────────────────────────────────────────────────────────────
def _overlaps(s, e, claimed):
    for cs, ce in claimed:
        if s < ce and cs < e:
            return True
    return False


def encode(
    text,
    map_file,
    entities_file=None,
    patterns_file=None,
    use_ner=False,
    surrogates="opaque",
):
    """Return (tokenized_text, coverage_dict). Raises on any error so the CLI can fail
    closed. `text` is NFKC-normalized first (compatibility folding); denylist matching
    additionally uses a case+homoglyph fold."""
    text = unicodedata.normalize("NFKC", text)
    fold = _fold_view(text)
    # Load-bearing: the fold must be offset-aligned 1:1 with text (denylist slices the
    # original by fold offsets). If a future fold change ever expands, fail CLOSED here.
    if len(fold) != len(text):  # pragma: no cover — guarded by _fold_char
        raise ValueError("fold view is not 1:1 offset-aligned with the input")
    claimed = []
    spans = []  # (start, end, label, original_value)

    # 1) DENYLIST — highest priority (your explicit known list; 100% of *listed* terms).
    n_denylist = 0
    if entities_file:
        for _ent, folded, label in _load_entities(entities_file):
            rx = _entity_regex(folded)
            for m in rx.finditer(fold):
                s, e = m.start(), m.end()
                if _overlaps(s, e, claimed):
                    continue
                claimed.append((s, e))
                spans.append((s, e, label, text[s:e]))  # value = ORIGINAL slice
                n_denylist += 1

    # 2) STRUCTURED — reused, deterministic (match on the original text).
    n_struct = 0
    for label, rx, validator in _BUILTIN + _load_extra(patterns_file):
        for m in rx.finditer(text):
            s, e = m.start(), m.end()
            val = m.group(0)
            if validator and not validator(val):
                continue
            if _overlaps(s, e, claimed):
                continue
            claimed.append((s, e))
            spans.append((s, e, label, val))
            n_struct += 1

    # 3) NER — optional, lowest priority, best-effort. Required-but-absent RAISES (FM7).
    n_ner = 0
    if use_ner:
        for s, e, label, val in _ner_spans(text):  # NerUnavailable propagates -> fail closed
            if _overlaps(s, e, claimed):
                continue
            claimed.append((s, e))
            spans.append((s, e, label, val))
            n_ner += 1

    # Build stable tokens (same value -> same token), replace RIGHT-TO-LEFT.
    salt = os.urandom(8).hex()
    nonce = os.urandom(4).hex()
    value_to_token = {}
    counter = {}
    taken_surrogates = set()
    banned = set(fold.split())  # surrogate must not equal any input word (FM4)
    out = text
    for s, e, label, val in sorted(spans, key=lambda t: t[0], reverse=True):
        tok = value_to_token.get(val)
        if tok is None:
            n = counter.get(label, 0)
            counter[label] = n + 1
            if surrogates == "realistic":
                sur = _surrogate(val, label, salt, taken_surrogates, banned)
                if sur is not None:
                    taken_surrogates.add(sur)
                    tok = sur
                else:
                    tok = _token(label, n, nonce)  # fallback: opaque, never a real name
            else:
                tok = _token(label, n, nonce)
            value_to_token[val] = tok
        out = out[:s] + tok + out[e:]

    # token->value must be 1:1 (FM5 — no token maps to two values).
    token_to_value = {}
    for v, t in value_to_token.items():
        if t in token_to_value:
            raise ValueError(f"surrogate collision on token {t!r}")
        token_to_value[t] = v

    # Write the vault 0600 from creation; it holds cleartext PII and never egresses.
    fd = os.open(map_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(token_to_value, fh)

    coverage = {
        "denylist_hits": n_denylist,
        "structured_hits": n_struct,
        "ner_hits": n_ner,
        "ner": "on" if use_ner else "OFF",
        "surrogates": surrogates,
    }
    return out, coverage


# ── decode (FM9, FM5) ───────────────────────────────────────────────────────────────
# Tolerant token pattern: matches __PII_LABEL_NONCE_N__ even if the model wrapped it in
# markdown, split it across a line wrap (whitespace inserted), or drifted its case.
_TOK_RE = re.compile(
    r"_\s*_\s*PII\s*_\s*([A-Za-z]+)\s*_\s*([0-9a-fA-F]+)\s*_\s*(\d+)\s*_\s*_"
)


def decode(text, map_file):
    """Restore tokens -> originals. Returns (restored_text, undecoded_count)."""
    try:
        with open(map_file, encoding="utf-8") as fh:
            token_to_value = json.load(fh)
    except (OSError, ValueError):
        return text, 0  # local restore only; nothing to restore -> unchanged

    # Pass 1: exact, longest-first (a token is never a prefix of another).
    for tok in sorted(token_to_value, key=len, reverse=True):
        text = text.replace(tok, token_to_value[tok])

    # Pass 2: tolerant — reconstruct the canonical token from a mangled match and retry.
    undecoded = 0

    def _sub(m):
        nonlocal undecoded
        canon = f"__PII_{m.group(1).upper()}_{m.group(2).lower()}_{m.group(3)}__"
        if canon in token_to_value:
            return token_to_value[canon]
        undecoded += 1
        return m.group(0)  # leave visible so a garbled token never ships silently

    text = _TOK_RE.sub(_sub, text)
    return text, undecoded


# ── scan (residual-leak review aid; overclaims 1 & 3, FM1) ──────────────────────────
# Common words that shouldn't count as an entity's "distinctive" word.
_STOP = {
    "corp", "corporation", "inc", "incorporated", "llc", "ltd", "limited", "company",
    "co", "group", "holdings", "the", "and", "of", "systems", "labs", "partners",
}


def scan(text, entities_file=None, patterns_file=None, threshold=0.78):
    """Return a review report: near-misses of listed entities (fuzzy n-gram + a
    distinctive-word check that catches abbreviations/partials) + any structured PII
    still present + the honest COVERAGE ENVELOPE. Never a binary 'safe'.

    Intended to run on the text you are ABOUT to send (i.e. AFTER encode) — a listed
    entity's own word remaining in that text means a variant/abbreviation leaked."""
    text_norm = unicodedata.normalize("NFKC", text)
    fold = _fold_view(text_norm)
    words = re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", fold)
    word_set = set(words)
    review = []

    n_listed = 0
    if entities_file:
        entities = _load_entities(entities_file)
        n_listed = len(entities)
        for ent, folded, _label in entities:
            ent_words = folded.split()
            span = len(ent_words)
            grams = [" ".join(words[i : i + span]) for i in range(len(words) - span + 1)]
            flagged_here = False
            for g in grams:
                if folded == g:
                    continue  # an exact match should already be tokenized upstream
                r = difflib.SequenceMatcher(None, folded, g).ratio()
                if r >= threshold:
                    review.append(
                        f"NEAR-MISS: listed {ent!r} ~ {g!r} in text "
                        f"(similarity {r:.2f}) — a variant/abbreviation may be leaking."
                    )
                    flagged_here = True
            # Distinctive-word check: a rare word of the entity present on its own
            # (catches "Acme Corp"/"Acme" when only "Acme Corporation" is listed).
            if not flagged_here:
                for w in ent_words:
                    if len(w) >= 4 and w not in _STOP and w in word_set:
                        review.append(
                            f"PARTIAL: a distinctive word of listed {ent!r} "
                            f"(word {w!r}) is present — an abbreviation may be leaking."
                        )
                        break

    n_pat = 0
    for label, rx, validator in _BUILTIN + _load_extra(patterns_file):
        n_pat += 1
        for m in rx.finditer(text_norm):
            if validator and not validator(m.group(0)):
                continue
            review.append(f"STRUCTURED PII STILL PRESENT: {label} {m.group(0)!r}")

    envelope = (
        f"COVERAGE: checked {n_listed} listed entities (fuzzy) + {n_pat} structured "
        "patterns. FREE-TEXT names NOT on your list are NOT covered by this scan. "
        "Read the ACTUAL text you are about to send — a clean scan is NOT a safe verdict."
    )
    return {"review_items": review, "coverage": envelope}


# ── self-test ───────────────────────────────────────────────────────────────────────
def _self_test():
    import tempfile

    d = tempfile.mkdtemp()
    ents = os.path.join(d, "ents.txt")
    with open(ents, "w", encoding="utf-8") as fh:
        fh.write("# known entities\nAcme Corporation | ORG\nJane Doe\nAl\n")  # 'Al' rejected

    src = "Jane Doe at Acme Corporation emailed jane@acme.com about Alabama."
    mp = os.path.join(d, "map.json")
    enc, cov = encode(src, mp, entities_file=ents)
    assert "Jane Doe" not in enc, "name leaked"
    assert "Acme Corporation" not in enc, "org leaked"
    assert "jane@acme.com" not in enc, "email leaked"
    assert "Alabama" in enc, "FM2: 'Al' over-matched inside Alabama"  # 1-char rejected
    assert cov["denylist_hits"] == 2 and cov["structured_hits"] == 1
    dec, undec = decode(enc, mp)
    assert dec == unicodedata.normalize("NFKC", src), "round-trip mismatch"
    assert undec == 0

    # FM3: homoglyph 'Аcme' (Cyrillic А) still matches the denylist entry.
    src2 = "Аcme Corporation shipped."
    mp2 = os.path.join(d, "m2.json")
    enc2, _ = encode(src2, mp2, entities_file=ents)
    assert "Аcme Corporation" not in enc2, "FM3: homoglyph bypassed the denylist"

    # FM9: model mangled the token (backticks + case drift) still decodes.
    tok = next(iter(json.load(open(mp))))
    mangled = f"The `{tok.lower()}` value is here."
    dec2, undec2 = decode(mangled, mp)
    assert "`" in dec2 and undec2 == 0, "FM9: mangled token not tolerated"

    # no-egress: the cleartext never appears in stdout form (it's only in the map).
    assert "jane@acme.com" not in enc

    # scan never says "safe" and always prints the coverage envelope.
    rep = scan(src, entities_file=ents)
    assert "safe verdict" in rep["coverage"].lower()

    # FM3/U+0130: a denylist match near 'İ' (which lower-cases to 2 chars) must NOT
    # shift offsets and leak the name (the security-review blocker).
    src3 = "İ Jane Doe is the patient."
    enc3, _ = encode(src3, os.path.join(d, "m3.json"), entities_file=ents)
    assert "Jane Doe" not in enc3 and "ane Doe" not in enc3, "FM3/U+0130 leaked the name"
    assert len(_fold_view(src3)) == len(src3), "fold not 1:1 over U+0130"

    # FM1: scanning about-to-send text that leaks an abbreviation flags it.
    rep2 = scan("Acme Corp shipped it.", entities_file=ents)
    assert any("Acme Corporation" in r for r in rep2["review_items"]), "FM1 abbrev not flagged"

    print("pseudonymize self-test: OK")
    return 0


# ── CLI (superset of the brief tool: encode/decode + --map-file preserved) ──────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="Reversible name/entity pseudonymizer.")
    sub = ap.add_subparsers(dest="cmd")

    pe = sub.add_parser("encode")
    pe.add_argument("--map-file", required=True)
    pe.add_argument("--entities-file", default=None, help="known names/orgs, one per line")
    pe.add_argument("--patterns-file", default=None, help="extra structured-PII regexes")
    pe.add_argument("--ner", action="store_true", help="REQUIRE a NER backend for unknown names")
    pe.add_argument("--surrogates", choices=["opaque", "realistic"], default="opaque")

    pd = sub.add_parser("decode")
    pd.add_argument("--map-file", required=True)

    ps = sub.add_parser("scan")
    ps.add_argument("--entities-file", default=None)
    ps.add_argument("--patterns-file", default=None)

    sub.add_parser("self-test")
    args = ap.parse_args(argv)

    if args.cmd == "self-test":
        return _self_test()

    if args.cmd == "encode":
        text = sys.stdin.read()
        try:
            out, cov = encode(
                text,
                args.map_file,
                entities_file=args.entities_file,
                patterns_file=args.patterns_file,
                use_ner=args.ner,
                surrogates=args.surrogates,
            )
        except NerUnavailable as exc:
            # FM7: requested-but-absent NER is a DISTINCT, non-suppressible failure.
            # Fail closed (write NOTHING) with a distinct exit code.
            sys.stderr.write(f"pseudonymize: NER UNAVAILABLE — {exc}\n")
            return 10
        except Exception as exc:  # FM8: any encode error fails CLOSED (nothing to stdout)
            sys.stderr.write(f"pseudonymize encode failed (nothing egressed): {exc}\n")
            return 1
        sys.stdout.write(out)
        _vault_warn(args.map_file)
        sys.stderr.write(
            "pseudonymize coverage: "
            f"denylist={cov['denylist_hits']} structured={cov['structured_hits']} "
            f"ner={cov['ner']}({cov['ner_hits']}) surrogates={cov['surrogates']}. "
            "Free-text names beyond your denylist are NOT scrubbed unless --ner. "
            "This pseudonymizes; it does not anonymize.\n"
        )
        return 0

    if args.cmd == "decode":
        text = sys.stdin.read()
        try:
            out, undec = decode(text, args.map_file)
        except Exception as exc:
            sys.stderr.write(f"pseudonymize decode failed: {exc}\n")
            sys.stdout.write(text)
            return 1
        sys.stdout.write(out)
        if undec:
            sys.stderr.write(
                f"pseudonymize: WARNING {undec} token(s) could not be decoded "
                "(the model may have altered them) — check the output.\n"
            )
        return 0

    if args.cmd == "scan":
        text = sys.stdin.read()
        rep = scan(text, entities_file=args.entities_file, patterns_file=args.patterns_file)
        for item in rep["review_items"]:
            sys.stderr.write(f"REVIEW: {item}\n")
        sys.stderr.write(rep["coverage"] + "\n")
        if not rep["review_items"]:
            sys.stderr.write(
                "No near-misses or structured PII found among the checked items — "
                "this is NOT a safe verdict; read the text yourself.\n"
            )
        return 0

    ap.print_help()
    return 2


def _vault_warn(map_file):
    """FM6: warn if the vault lands inside a git working tree."""
    p = os.path.dirname(os.path.abspath(map_file)) or "."
    cur = p
    while True:
        if os.path.isdir(os.path.join(cur, ".git")):
            sys.stderr.write(
                f"pseudonymize: WARNING the vault {map_file!r} is inside a git repo — "
                "keep it OUT of version control (add to .gitignore) and never paste it "
                "into a model. It holds the cleartext mapping.\n"
            )
            return
        parent = os.path.dirname(cur)
        if parent == cur:
            return
        cur = parent


if __name__ == "__main__":
    raise SystemExit(main())
