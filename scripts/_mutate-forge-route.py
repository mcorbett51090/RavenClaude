#!/usr/bin/env python3
"""Write a MUTANT copy of forge-route.py with the layout-detector fix reverted.

Gate 222's must-fail half. The mutant restores the pre-fix behaviour — a bare
substring match on `.repo-layout.json` / `allowed_globs`, with no edit-verb
requirement and no negation suppression — so the two negative fixtures in
`forge-route.py`'s own `_FIXTURES` must redden.

⛔ WHY THIS EXISTS AS ITS OWN FILE. The gate needs to prove its fixtures can
FAIL. Without that, "9 fixtures OK" is a sentence, not evidence: a detector that
had gone blind (matching nothing at all) would also print it. This repo's own
record is full of gates that reported green while measuring nothing, and the
half that catches that is always the mutant.

⛔ IT MUST FAIL LOUDLY IF THE MUTATION DOES NOT APPLY. If `forge-route.py` is
refactored so the anchor text below no longer matches, this exits non-zero
rather than writing an unmutated copy — because an unmutated copy would pass its
own self-test and the gate would report teeth it does not have. That is the
exact failure mode the mutant is here to prevent, so it must not be able to
happen to the mutant itself.

Python 3.9-safe (stock macOS): no PEP-604 unions, no match statements.
"""

from __future__ import annotations

import pathlib
import sys

# The two guard clauses the fix added to `_layout_edit_fires`. Removing them
# collapses the predicate back to "the line mentions the token" — the defect.
_ANCHOR = (
    "        if not _LAYOUT_EDIT_VERB.search(line):\n"
    "            continue\n"
    "        if _LAYOUT_NEGATION.search(line):\n"
    "            continue\n"
)

_SRC = pathlib.Path("plugins/ravenclaude-core/scripts/forge-route.py")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: _mutate-forge-route.py <out-path>", file=sys.stderr)
        return 2
    try:
        src = _SRC.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read {_SRC}: {exc}", file=sys.stderr)
        return 2

    mutant = src.replace(_ANCHOR, "", 1)
    if mutant == src:
        print(
            "MUTATION DID NOT APPLY — the anchor text in _mutate-forge-route.py no "
            "longer matches forge-route.py. Gate 222's teeth are measuring NOTHING "
            "until this is re-synced. Refusing to write an unmutated copy.",
            file=sys.stderr,
        )
        return 1

    try:
        pathlib.Path(sys.argv[1]).write_text(mutant, encoding="utf-8")
    except OSError as exc:
        print(f"cannot write mutant: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
