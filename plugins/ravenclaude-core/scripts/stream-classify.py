#!/usr/bin/env python3
"""stream-classify.py — deterministic, stdlib-only prompt classifier for Agentic Work-Streams.

A *pure* library (no side effects, no I/O beyond what a caller passes in) that turns a
prompt's text into DERIVED features and scores it against a set of stream centroids using
TF-IDF / cosine similarity. This is P0 of the Agentic Work-Streams feature.

WHY DETERMINISTIC + STDLIB-ONLY
  The classifier must be reproducible across hosts (Claude Code, Copilot CLI, a bare
  terminal) and add NO new dependencies (house rule). TF-IDF + cosine over a bag of
  stemmed terms is the smallest thing that does the job. The optional `claude -p`
  LLM-assist is a SEPARATE, off-by-default posture toggle handled elsewhere — this file
  never calls a model.

THE LOAD-BEARING PRIVACY INVARIANT (no-egress)
  The prompt text is read here to COMPUTE features, but this module NEVER returns, stores,
  or logs a raw prompt substring. `derive_features()` returns only:
    - terms:       a sorted, de-duplicated, length-capped list of stemmed *tokens*
                   (each token is a single normalized word; stop-words removed) — these
                   are derived labels, not free-form prompt text. They are intentionally
                   single tokens so no phrase/sentence from the prompt can reconstruct.
    - word_count:  an integer
    - label:       a short slug derived from the TOP terms (single tokens joined by `-`)
  A caller that persists the result to the per-stream history.jsonl therefore persists
  derived labels only. The no-egress gate (Gate 110) greps a stored history for a
  distinctive multi-word prompt phrase and asserts it is ABSENT. Single-token terms can
  never reconstruct a phrase, so the invariant holds by construction.

DETERMINISM RULES (so the gate can assert byte-stable output)
  - tokenization is fixed (lowercase, [a-z0-9]+ on a casefolded string)
  - the stop-word set is a fixed literal
  - the light stemmer is a fixed suffix-strip
  - term lists are sorted; ties in scoring break on the stream id (sorted)
  - no wall-clock, no randomness, no locale-dependent ops
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable

# ── Fixed lexical config (all literals — no env, no locale) ────────────────────

# A compact, fixed English stop-word set. Intentionally small + literal so the
# output is byte-stable and the gate can pin it. Not meant to be exhaustive.
_STOP_WORDS = frozenset(
    """
    a an and are as at be been being but by can could did do does doing done for
    from get got had has have having he her him his how i if in into is it its
    just me my no nor not of off on once only or our out over own re so some such
    than that the their them then there these they this those through to too up us
    use used using very was we were what when where which while who why will with
    would you your please make made let lets need needs want wants
    """.split()
)

# Tokens shorter than this (after stemming) are dropped as low-signal noise.
_MIN_TOKEN_LEN = 2

# Cap the number of terms returned so a long prompt can't blow up the history line.
# (Also bounds memory; the label is built from the top of this list.)
_MAX_TERMS = 40

# How many top terms feed the human-readable label slug.
_LABEL_TERM_COUNT = 4

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _stem(token: str) -> str:
    """A tiny, deterministic suffix-stripper.

    Not a real Porter stemmer — just enough to collapse the most common inflections
    so "deploying"/"deployed"/"deploys" land near "deploy". Fixed rules, applied
    longest-suffix-first, with a length floor so we never stem a word to nothing.
    """
    t = token
    for suffix in ("ing", "edly", "ied", "ies", "ed", "es", "ly", "s"):
        if t.endswith(suffix) and len(t) - len(suffix) >= 3:
            base = t[: -len(suffix)]
            # "ies" -> "y" (e.g. "queries" -> "query")
            if suffix == "ies":
                return base + "y"
            return base
    return t


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics, drop stop-words, stem, drop short tokens.

    Deterministic. Returns tokens in ORIGINAL ORDER (term-frequency callers want the
    multiset; `derive_features` sorts for the stored label). Pure tokens — single words.
    """
    if not text:
        return []
    out: list[str] = []
    for raw in _TOKEN_RE.findall(text.casefold()):
        if raw in _STOP_WORDS:
            continue
        stemmed = _stem(raw)
        if len(stemmed) < _MIN_TOKEN_LEN or stemmed in _STOP_WORDS:
            continue
        out.append(stemmed)
    return out


def term_freq(tokens: Iterable[str]) -> dict[str, float]:
    """Raw term-frequency map from a token stream."""
    tf: dict[str, float] = {}
    for tok in tokens:
        tf[tok] = tf.get(tok, 0.0) + 1.0
    return tf


def _label_from_terms(terms: list[str]) -> str:
    """Build a short, filesystem-safe slug from the top terms.

    Top terms are the alphabetically-first N of the sorted unique term list (sorting
    keeps it deterministic; we are not ranking by importance here — the label is a hint,
    not a claim). Joined by `-`. Single tokens only, so no prompt phrase leaks.
    """
    head = terms[:_LABEL_TERM_COUNT]
    slug = "-".join(head)
    # Defensive: keep only the slug charset (tokens are already [a-z0-9], but be explicit).
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug or "misc"


def derive_features(text: str) -> dict:
    """Turn a prompt into DERIVED features — the only thing a caller may persist.

    Returns a dict with:
      - terms:      sorted, de-duplicated, length-capped list of stemmed tokens
      - word_count: int (count of raw whitespace-split words in the original text)
      - label:      short slug from the top terms (single tokens joined by '-')

    NEVER returns a raw prompt substring. See the module docstring's no-egress note.
    """
    tokens = tokenize(text)
    unique_sorted = sorted(set(tokens))[:_MAX_TERMS]
    # word_count is over the ORIGINAL text (a true length signal), independent of tokenization.
    word_count = len(text.split()) if text else 0
    return {
        "terms": unique_sorted,
        "word_count": word_count,
        "label": _label_from_terms(unique_sorted),
    }


# ── TF-IDF / cosine scoring against stream centroids ───────────────────────────


def _idf(doc_term_sets: list[set[str]]) -> dict[str, float]:
    """Smoothed inverse-document-frequency over a corpus of term-sets.

    idf(t) = ln( (1 + N) / (1 + df(t)) ) + 1   (the sklearn-style smoothed form)
    Deterministic; N is the number of documents (centroids + the query).
    """
    n = len(doc_term_sets)
    df: dict[str, float] = {}
    for s in doc_term_sets:
        for t in s:
            df[t] = df.get(t, 0.0) + 1.0
    return {t: math.log((1.0 + n) / (1.0 + d)) + 1.0 for t, d in df.items()}


def _tfidf_vec(tf: dict[str, float], idf: dict[str, float]) -> dict[str, float]:
    return {t: f * idf.get(t, 0.0) for t, f in tf.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    # iterate the smaller dict
    if len(a) > len(b):
        a, b = b, a
    dot = sum(v * b.get(t, 0.0) for t, v in a.items())
    if dot == 0.0:
        return 0.0
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def classify(
    text: str,
    centroids: dict[str, dict[str, float]],
    *,
    threshold: float = 0.18,
) -> dict:
    """Score a prompt against per-stream term centroids; return the best match + scores.

    Args:
      text:      the prompt text (read to derive features; never echoed back).
      centroids: {stream_id: {term: weight}} — each stream's accumulated term profile.
                 An empty centroid map means "no streams yet" -> best_stream is None.
      threshold: minimum cosine for a confident match. Below it, `confident` is False
                 and the caller should treat the prompt as a NEW-stream candidate (or,
                 under the sticky rule, inherit the active stream — that decision is the
                 caller's, not the classifier's).

    Returns:
      {
        "best_stream":  str | None,        # highest-scoring stream id (None if no centroids)
        "best_score":   float,             # its cosine score (0.0 if none)
        "confident":    bool,              # best_score >= threshold
        "scores":       {stream_id: cosine},  # all scores, for transparency
        "features":     {...},             # derive_features(text) — derived-only
      }

    Determinism: ties in best_score break on the LOWEST stream id (sorted), so the
    result is byte-stable for identical inputs.
    """
    features = derive_features(text)
    query_tf = term_freq(tokenize(text))

    if not centroids:
        return {
            "best_stream": None,
            "best_score": 0.0,
            "confident": False,
            "scores": {},
            "features": features,
        }

    # Build the IDF over query + all centroids (centroids are already term->weight maps;
    # their key-set is the "document" for IDF).
    doc_term_sets = [set(query_tf.keys())] + [set(c.keys()) for c in centroids.values()]
    idf = _idf(doc_term_sets)

    query_vec = _tfidf_vec(query_tf, idf)

    scores: dict[str, float] = {}
    for sid in sorted(centroids.keys()):
        cvec = _tfidf_vec(centroids[sid], idf)
        scores[sid] = _cosine(query_vec, cvec)

    # Best by score, tie-break on lowest sorted id (sorted() below orders the iteration,
    # and we only replace on a STRICT increase, so the first-seen max — lowest id — wins).
    best_stream = None
    best_score = 0.0
    for sid in sorted(scores.keys()):
        if scores[sid] > best_score:
            best_score = scores[sid]
            best_stream = sid

    return {
        "best_stream": best_stream,
        "best_score": best_score,
        "confident": best_stream is not None and best_score >= threshold,
        "scores": scores,
        "features": features,
    }


def update_centroid(
    centroid: dict[str, float],
    text: str,
    *,
    alpha: float = 0.30,
) -> dict[str, float]:
    """Fold a prompt's term-frequencies into a stream centroid via EMA (red-team mitigation
    #4: centroid poisoning -> small-alpha exponential moving average so one off-topic prompt
    can't yank the profile).

    new_weight(t) = (1 - alpha) * old_weight(t) + alpha * tf(t)

    Terms present in only one side are blended against an implicit 0 on the other side.
    Returns a NEW dict (does not mutate the input). Deterministic.
    """
    tf = term_freq(tokenize(text))
    keys = set(centroid.keys()) | set(tf.keys())
    out: dict[str, float] = {}
    for t in sorted(keys):
        old = centroid.get(t, 0.0)
        new = tf.get(t, 0.0)
        blended = (1.0 - alpha) * old + alpha * new
        if blended > 1e-9:
            out[t] = blended
    return out


# ── CLI shim (for the gate + manual inspection; emits JSON, reads no files by default) ──

if __name__ == "__main__":
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(
        description="Derive features / classify a prompt (stdlib, deterministic)."
    )
    ap.add_argument("--text", help="prompt text (or read from stdin if omitted)")
    ap.add_argument(
        "--centroids",
        help="path to a JSON file mapping {stream_id: {term: weight}} (optional)",
    )
    ap.add_argument("--threshold", type=float, default=0.18)
    ap.add_argument(
        "--features-only",
        action="store_true",
        help="emit only derive_features(text) (no classification)",
    )
    args = ap.parse_args()

    text = args.text if args.text is not None else sys.stdin.read()

    if args.features_only:
        print(json.dumps(derive_features(text), sort_keys=True))
        sys.exit(0)

    centroids = {}
    if args.centroids:
        with open(args.centroids, encoding="utf-8") as fh:
            centroids = json.load(fh)

    print(json.dumps(classify(text, centroids, threshold=args.threshold), sort_keys=True))
