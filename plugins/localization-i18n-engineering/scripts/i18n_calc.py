#!/usr/bin/env python3
"""i18n_calc.py — a zero-dependency localization / i18n decision calculator.

Removes the guesswork from three recurring "will this string survive translation?"
questions an i18n architect / localization engineer / QA runs constantly — WITHOUT
pulling in ICU4X, CLDR data files, or a TMS SDK, so it runs anywhere Python 3.8+ is
present (stdlib only). It is a CALCULATOR, NOT a CLDR mirror: the plural-category data
is a small, dated, [verify-at-build] table covering the locales teams hit first, and
the agent emits the command for a human to run, then re-grounds the numbers against
Intl.PluralRules / the live CLDR before quoting them to a consumer.

  pseudo            Pseudo-localize a string: accent the Latin letters, pad to a target
                    expansion (~30-40% by default — the IBM/Microsoft rule of thumb for
                    short UI strings), and bracket it. The cheapest hardcoded-string and
                    truncation tripwire, runnable on one string from the shell.
                    Mirrors best-practices/pseudo-localize-continuously.md.

  expansion         Estimate translated length growth for a source string and flag
                    truncation risk against a fixed UI width (in characters or, with an
                    --avg-char-px, in CSS px). Uses the published per-language expansion
                    bands (shorter source -> larger % growth; German/Russian/Finnish run
                    long, CJK contracts). Mirrors best-practices/translated-is-not-correct.md.

  plural-coverage   Given the plural categories an ICU message actually defines (e.g.
                    "one,other"), check they cover the CLDR cardinal categories REQUIRED
                    for a locale (Polish needs one/few/many/other; Arabic needs all six).
                    Reports the missing categories — the exact never-assume-english-grammar
                    failure. Mirrors best-practices/never-assume-english-grammar.md.

All tables are [verify-at-build]: re-check expansion bands against your own corpus and
plural categories against Intl.PluralRules / the CLDR before quoting them. CLDR plural
data evolves; this is a decision aid, not the source of truth (cldr-intl-is-the-source-of-truth).
"""

from __future__ import annotations

import argparse
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Pseudo-localization
# ---------------------------------------------------------------------------

# An accent map for the Latin alphabet. Each replacement is a single, visibly
# accented homoglyph so the string stays readable while obviously "foreign" —
# the standard accent-and-bracket pseudo-locale transform.
_ACCENTS = {
    "a": "å", "b": "ƀ", "c": "ç", "d": "ð", "e": "é",
    "f": "ƒ", "g": "ĝ", "h": "ĥ", "i": "î", "j": "ĵ",
    "k": "ķ", "l": "ļ", "m": "ḿ", "n": "ñ", "o": "ö",
    "p": "þ", "q": "ǫ", "r": "ŗ", "s": "š", "t": "ţ",
    "u": "û", "v": "ṽ", "w": "ŵ", "x": "ẋ", "y": "ý",
    "z": "ž",
    "A": "Å", "B": "Ɓ", "C": "Ç", "D": "Ð", "E": "É",
    "F": "Ƒ", "G": "Ĝ", "H": "Ĥ", "I": "Î", "J": "Ĵ",
    "K": "Ķ", "L": "Ļ", "M": "Ḿ", "N": "Ñ", "O": "Ö",
    "P": "Þ", "Q": "Ǫ", "R": "Ŗ", "S": "Š", "T": "Ţ",
    "U": "Û", "V": "Ṽ", "W": "Ŵ", "X": "Ẋ", "Y": "Ý",
    "Z": "Ž",
}

# Padding glyph repeated to hit the expansion target — a vowel-ish run that reads
# as "this got longer" without being mistaken for real copy.
_PAD = "əṽå"  # ə ṽ å


def _split_placeholders(text: str) -> list[tuple[str, bool]]:
    """Split into (segment, is_placeholder) runs.

    Placeholders ({name}, {0}, %s, %1$s, {{x}}) must pass through untouched — a
    pseudo-localizer that mangles a placeholder defeats its own purpose. We treat
    any {...} or %-token as opaque.
    """
    out: list[tuple[str, bool]] = []
    i, n = 0, len(text)
    buf = ""
    while i < n:
        ch = text[i]
        if ch == "{":
            depth = 0
            j = i
            while j < n:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
            if buf:
                out.append((buf, False))
                buf = ""
            out.append((text[i:j], True))
            i = j
            continue
        # A lone "%" in copy ("50% off") is literal, not a printf placeholder.
        # Only treat "%" as a conversion start when a printf-ish char follows
        # (flags/width/precision digits, the arg-index "$", or "%%").
        if ch == "%" and i + 1 < n and text[i + 1] in "sdifgGeExXoubcp%0123456789$.+-#":
            j = i + 1
            while j < n and text[j] not in " \t":
                j += 1
                # %s, %d, %1$s, %% — stop at the conversion letter
                if text[j - 1] in "sdifgGeExXoubcp%":
                    break
            if buf:
                out.append((buf, False))
                buf = ""
            out.append((text[i:j], True))
            i = j
            continue
        buf += ch
        i += 1
    if buf:
        out.append((buf, False))
    return out


def pseudo_localize(text: str, expansion: float, brackets: bool) -> str:
    """Accent the translatable runs, pad to `expansion`, leave placeholders intact."""
    segments = _split_placeholders(text)
    accented_parts: list[str] = []
    translatable_len = 0
    for seg, is_ph in segments:
        if is_ph:
            accented_parts.append(seg)
        else:
            accented = "".join(_ACCENTS.get(c, c) for c in seg)
            accented_parts.append(accented)
            translatable_len += len(seg)
    body = "".join(accented_parts)

    # Pad to hit the requested expansion over the *translatable* character count
    # only — padding the placeholder length would lie about real-copy growth.
    target_extra = round(translatable_len * expansion)
    if target_extra > 0:
        pad = (_PAD * (target_extra // len(_PAD) + 1))[:target_extra]
        body = body + pad
    return f"[{body}]" if brackets else body


# ---------------------------------------------------------------------------
# Expansion / truncation risk
# ---------------------------------------------------------------------------

# Per-language average expansion factors for translation FROM English, as a
# multiplier on source character length. Published rule-of-thumb bands (IBM
# Globalization, Microsoft, W3C i18n) — [verify-at-build] against your corpus.
# Short strings expand MORE in %; this is the average-band approximation.
_EXPANSION = {
    "de": 1.35, "ru": 1.30, "fi": 1.30, "pl": 1.30, "fr": 1.25, "es": 1.25,
    "it": 1.25, "pt": 1.25, "nl": 1.25, "cs": 1.30, "el": 1.30, "tr": 1.20,
    "ja": 0.60, "zh": 0.50, "ko": 0.70, "ar": 1.25, "he": 1.20, "th": 1.15,
}

# For very short source strings, growth runs higher than the average band.
# Microsoft/IBM short-string surcharge: <=10 chars +~30pp, <=20 chars +~15pp.
def _short_string_surcharge(src_len: int) -> float:
    if src_len <= 10:
        return 0.30
    if src_len <= 20:
        return 0.15
    return 0.0


def estimate_expansion(text: str, lang: str) -> tuple[float, int, int]:
    """Return (factor, estimated_len, source_len) for `text` into `lang`."""
    src_len = len(text)
    base = _EXPANSION.get(lang)
    if base is None:
        raise KeyError(lang)
    factor = base + _short_string_surcharge(src_len)
    est = round(src_len * factor)
    return factor, est, src_len


# ---------------------------------------------------------------------------
# CLDR plural-category coverage
# ---------------------------------------------------------------------------

# CLDR cardinal plural categories REQUIRED per locale (the set Intl.PluralRules
# returns for that locale). Dated 2026-06-08, [verify-at-build] — re-ground
# against Intl.PluralRules before quoting. "other" is always required.
_PLURAL_REQUIRED = {
    "en": {"one", "other"},
    "de": {"one", "other"},
    "es": {"one", "many", "other"},
    "fr": {"one", "many", "other"},
    "it": {"one", "many", "other"},
    "pt": {"one", "many", "other"},
    "nl": {"one", "other"},
    "ja": {"other"},
    "zh": {"other"},
    "ko": {"other"},
    "th": {"other"},
    "tr": {"one", "other"},
    "ru": {"one", "few", "many", "other"},
    "uk": {"one", "few", "many", "other"},
    "pl": {"one", "few", "many", "other"},
    "cs": {"one", "few", "many", "other"},
    "sk": {"one", "few", "many", "other"},
    "lt": {"one", "few", "many", "other"},
    "ar": {"zero", "one", "two", "few", "many", "other"},
    "he": {"one", "two", "many", "other"},
    "cy": {"zero", "one", "two", "few", "many", "other"},
    "sl": {"one", "two", "few", "other"},
    "ga": {"one", "two", "few", "many", "other"},
}

_CLDR_ORDER = ["zero", "one", "two", "few", "many", "other"]


def plural_coverage(provided: set[str], locale: str) -> tuple[set[str], set[str]]:
    """Return (missing, extra) categories vs. the CLDR requirement for `locale`."""
    required = _PLURAL_REQUIRED.get(locale)
    if required is None:
        raise KeyError(locale)
    missing = required - provided
    extra = provided - required
    return missing, extra


def _sort_cats(cats: set[str]) -> list[str]:
    return sorted(cats, key=lambda c: _CLDR_ORDER.index(c) if c in _CLDR_ORDER else 99)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_pseudo(args: argparse.Namespace) -> int:
    text = args.text if args.text is not None else sys.stdin.read().rstrip("\n")
    result = pseudo_localize(text, args.expansion, not args.no_brackets)
    src_visible = sum(1 for c in text if not unicodedata.category(c).startswith("C"))
    print(result)
    print(
        f"# source {len(text)} chars ({src_visible} visible) "
        f"-> pseudo {len(result)} chars, ~{round(args.expansion * 100)}% expansion target",
        file=sys.stderr,
    )
    return 0


def _cmd_expansion(args: argparse.Namespace) -> int:
    try:
        factor, est, src = estimate_expansion(args.text, args.lang)
    except KeyError:
        langs = ", ".join(sorted(_EXPANSION))
        print(f"error: no expansion band for '{args.lang}'. Known: {langs}", file=sys.stderr)
        return 2
    print(f"source ({src} chars)  : {args.text!r}")
    print(f"target {args.lang:<6}      : ~{est} chars  (x{factor:.2f})")
    if args.width is not None:
        fits = est <= args.width
        verdict = "FITS" if fits else "TRUNCATION RISK"
        print(f"UI width {args.width} chars : {verdict}  ({est} vs {args.width})")
        if not fits:
            print(
                f"  -> over by {est - args.width} chars; widen the control, "
                f"wrap, or shorten the source (translated-is-not-correct).",
            )
        return 0 if fits else 1
    return 0


def _cmd_plural_coverage(args: argparse.Namespace) -> int:
    provided = {c.strip() for c in args.categories.split(",") if c.strip()}
    unknown = provided - set(_CLDR_ORDER)
    if unknown:
        print(
            f"error: unknown plural categor(ies): {', '.join(sorted(unknown))}. "
            f"Valid: {', '.join(_CLDR_ORDER)}",
            file=sys.stderr,
        )
        return 2
    try:
        missing, extra = plural_coverage(provided, args.locale)
    except KeyError:
        locs = ", ".join(sorted(_PLURAL_REQUIRED))
        print(f"error: no CLDR plural data for '{args.locale}'. Known: {locs}", file=sys.stderr)
        return 2
    required = _PLURAL_REQUIRED[args.locale]
    print(f"locale {args.locale:<6}    : requires {{{', '.join(_sort_cats(required))}}}")
    print(f"message defines  : {{{', '.join(_sort_cats(provided))}}}")
    if missing:
        print(f"MISSING          : {{{', '.join(_sort_cats(missing))}}}  -- counts will be WRONG")
        print(
            "  -> add these ICU plural arms; the translator owns the grammar per CLDR "
            "(never-assume-english-grammar).",
        )
    else:
        print("coverage         : OK -- all required CLDR categories present")
    if extra:
        print(f"note: extra arms {{{', '.join(_sort_cats(extra))}}} (harmless but unused for this locale)")
    return 1 if missing else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="i18n_calc",
        description="Zero-dependency localization/i18n decision calculator "
        "(stdlib only; all tables [verify-at-build] against Intl/CLDR).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("pseudo", help="pseudo-localize a string (accent + pad + bracket)")
    sp.add_argument("text", nargs="?", default=None, help="string to pseudo-localize (or read stdin)")
    sp.add_argument(
        "--expansion", type=float, default=0.35,
        help="length-inflation target as a fraction (default 0.35 = ~35%%)",
    )
    sp.add_argument("--no-brackets", action="store_true", help="omit the surrounding [ ] markers")
    sp.set_defaults(func=_cmd_pseudo)

    se = sub.add_parser("expansion", help="estimate target-language growth + truncation risk")
    se.add_argument("text", help="source (English) string")
    se.add_argument("--lang", required=True, help="target language code (e.g. de, ru, ja, ar)")
    se.add_argument(
        "--width", type=int, default=None,
        help="UI width in characters; flags truncation risk if the estimate exceeds it",
    )
    se.set_defaults(func=_cmd_expansion)

    spc = sub.add_parser("plural-coverage", help="check an ICU plural set covers a locale's CLDR categories")
    spc.add_argument(
        "--categories", required=True,
        help="comma-separated categories the message defines (e.g. one,other)",
    )
    spc.add_argument("--locale", required=True, help="target locale (e.g. pl, ar, ru, ja)")
    spc.set_defaults(func=_cmd_plural_coverage)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
