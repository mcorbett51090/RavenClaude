#!/usr/bin/env python3
"""Derive DS02's trigger-clause marker list FROM the corpus, not from intuition.

Why this script exists (plan Phase 2, work item 4 / resolution 3): plan-A authored
DS02's marker list by hand. Measured against the real corpus, that list missed this
repo's own house idiom — "Reach for this ON a X question" — while containing "reach
for this WHEN". The result was a 47% false-positive rate on the hits it did produce.

A marker list written from intuition encodes the author's phrasing habits. A marker
list derived from the corpus encodes the population's. This script produces the
latter, and ships next to its output so anyone can re-run it and diff.

Method, stated plainly so its limits are visible:
  1. Read every SKILL.md description in the corpus.
  2. Split each into sentences.
  3. Keep sentences that look like a *trigger clause* — they mention a user/request/
     situation rather than only a capability.
  4. Frequency-rank the leading subordinator or imperative phrase of those sentences.
  5. Emit every idiom at or above a support threshold.

⛔ This does NOT prove the resulting list is complete. It proves the list covers the
idioms THIS corpus actually uses, at the support level shown. A phrasing nobody in
the corpus happens to use will be missed, and that is a known and accepted bound —
which is precisely why DS02 ships at WARN and not FAIL.

Stdlib only. Python 3.9-safe.
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

# A sentence is trigger-shaped if it references the situation or the asker rather
# than only describing a capability. Deliberately broad: this is the RECALL stage;
# ranking and the support threshold do the precision work.
_TRIGGER_CONTEXT = re.compile(
    r"\b(user|someone|anyone|you|request|asks?|asking|question|task|when|whenever|"
    r"before|after|during|situation|scenario|need|needs|wants?|trying|invoke|invoked|"
    r"trigger|triggers|load|loads|reach)\b",
    re.I,
)

# The leading idiom we rank: an optional imperative verb phrase followed by the
# subordinator, captured as written so the output is inspectable rather than
# normalised into something nobody typed.
_LEAD = re.compile(
    r"^\W*("
    r"use (?:this |it )?(?:skill )?(?:when|whenever|for|to|if|on)|"
    r"reach for (?:this|it)(?: when| on| for| if)?|"
    r"load (?:this )?(?:skill )?(?:when|if|before)|"
    r"invoke(?:d)? (?:this )?(?:when|for|on|if)|"
    r"triggers? on|"
    r"apply (?:this )?when|"
    r"call (?:this )?when|"
    r"when(?:ever)?(?: the| a| an| you| someone)?|"
    r"for (?:any|a|an|the)|"
    r"if (?:the|a|an|you|someone)|"
    r"before (?:any|a|the|you)|"
    r"after (?:any|a|the|you)"
    r")\b",
    re.I,
)

_SENT_SPLIT = re.compile(r"(?<=[.!?;])\s+|\s+—\s+|\s+--\s+")


def read_descriptions(patterns: list[str]) -> list[tuple[str, str]]:
    """Return [(source_path, description)] for every parseable SKILL.md."""
    out: list[tuple[str, str]] = []
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
            if not m:
                continue
            d = re.search(r"^description:\s*(.+(?:\n\s+.+)*)$", m.group(1), re.M)
            if not d:
                continue
            out.append((path, " ".join(d.group(1).split())))
    return out


def derive(descriptions: list[tuple[str, str]], min_support: int) -> dict[str, object]:
    counter: collections.Counter = collections.Counter()
    examples: dict[str, str] = {}
    trigger_bearing = 0

    for _path, desc in descriptions:
        has_trigger = False
        for sentence in _SENT_SPLIT.split(desc):
            s = sentence.strip()
            if not s or not _TRIGGER_CONTEXT.search(s):
                continue
            lead = _LEAD.match(s)
            if not lead:
                continue
            idiom = " ".join(lead.group(1).lower().split())
            counter[idiom] += 1
            examples.setdefault(idiom, s[:110])
            has_trigger = True
        if has_trigger:
            trigger_bearing += 1

    kept = [(i, n) for i, n in counter.most_common() if n >= min_support]
    dropped = [(i, n) for i, n in counter.most_common() if n < min_support]

    return {
        "derived_on": "corpus scan",
        "corpus_size": len(descriptions),
        "descriptions_with_a_trigger_clause": trigger_bearing,
        "min_support": min_support,
        "markers": [
            {"idiom": i, "support": n, "example": examples.get(i, "")} for i, n in kept
        ],
        "below_threshold": [{"idiom": i, "support": n} for i, n in dropped],
        "limits": (
            "Covers the idioms THIS corpus uses at support >= %d. A phrasing absent "
            "from the corpus is missed by construction. This bound is why DS02 ships "
            "at WARN." % min_support
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="derive_markers", description=__doc__.splitlines()[0])
    ap.add_argument("--corpus", nargs="+",
                    default=["plugins/*/skills/*/SKILL.md"],
                    help="glob(s) of SKILL.md files to scan")
    ap.add_argument("--min-support", type=int, default=3)
    ap.add_argument("--out", default=None, help="write JSON here instead of stdout")
    args = ap.parse_args(argv)

    descriptions = read_descriptions(args.corpus)
    if not descriptions:
        print("derive_markers: corpus is empty — refusing to emit a marker list "
              "derived from nothing", file=sys.stderr)
        return 2

    result = derive(descriptions, args.min_support)
    payload = json.dumps(result, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload + "\n")
        print("corpus: %d descriptions, %d carry a trigger clause"
              % (result["corpus_size"], result["descriptions_with_a_trigger_clause"]))
        print("markers kept (support >= %d): %d" % (args.min_support, len(result["markers"])))
        for m in result["markers"]:
            print("   %4d  %s" % (m["support"], m["idiom"]))
        print("\nwritten to %s" % args.out)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
