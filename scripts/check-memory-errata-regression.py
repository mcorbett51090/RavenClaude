#!/usr/bin/env python3
"""check-memory-errata-regression.py — keep the 12 debunked memory claims out of the tree.

The `memory-engineering` plugin is authored from a source thread that carried twelve
verified-false claims (fabricated institution attributions, a mis-read energy
spread, two customers' testimonials generalized into a property of the technique,
an invented Agent SDK surface, ...). The plugin ships a `## Corrections` errata
block that states each falsehood *and* its correction, precisely so a future author
meeting the same source thread does not reintroduce it in good faith.

That errata block is the only place those formulations may appear. This gate is the
mechanical control that keeps it that way. It replaces a hand-run shell sweep that
was authored as `grep -E` with a PCRE lookbehind — a dead check that errors (exit 2,
zero files scanned) on BSD/ugrep and, on GNU grep, warns to stderr and matches
nothing, so a clean run looks like a pass. Python sidesteps the whole
GNU-vs-BSD-vs-ugrep class (see plugins/ravenclaude-core/CLAUDE.md v0.196.0) and is
the only dialect in which the two negative conditions below are expressible at all.

HOW IT TELLS A REGRESSION FROM THE ERRATA BLOCK (the crux)
----------------------------------------------------------
The errata block is identified by LOCATION, not by content:

    ERRATA REGION = the lines from the `## Corrections` heading to the next `^## `
                    heading, in knowledge/memory-engineering-paradigms.md

The region is not "exempted" — it is where the claims are REQUIRED to be. Four
assertions, and the shape of them is what makes the check self-testing:

  A1 REGRESSION  Outside the region, every match is a violation, unless the line
                 carries a per-claim `guard` (a token that makes the mention
                 correctly qualified, e.g. `97%` on a line that also says
                 `Rakuten`) or the explicit inline marker `<!-- errata-quote -->`.

  A2 LIVENESS    Inside the region, ALL twelve patterns must match. Zero hits means
                 the PATTERN is broken, not that the tree is clean — the exact
                 silent-green failure that killed the shell version. A pattern that
                 stops matching fails the build instead of passing quietly.

  A3 PAIRING     EVERY in-region occurrence must sit within +/-4 lines of a
                 refutation token — not merely one of them. The "at least one"
                 reading let a correct errata entry inoculate every additional bare
                 occurrence of the same claim inside the region. HONEST SCOPE: this
                 proves a refutation word is adjacent; it does not prove the
                 refutation is correct. A bare comma-separated list of the twelve
                 phrasings with the corrections stripped out fails A3.

  A3b COMMENTS   Inside the region, no HTML comment line may carry a banned
                 phrasing. A3's adjacency rule structurally cannot see the
                 withdrawn `<!-- grep-targets: ... -->` shape: a one-line target
                 list sits beside a real correction, so it is always "paired".
                 A3b catches it by shape instead.

Because the checker's own regexes contain the banned strings, it deliberately lives
at scripts/ — OUTSIDE the scanned tree — so it can never flag itself.

NOT-APPLICABLE IS NOT A FAILURE: if the plugin (or its errata file) does not exist,
the gate exits 0 with a notice, so it is safe to land before the plugin does.

Exit 0 = clean (or not applicable). Exit 1 = at least one assertion failed.
Exit 2 = bad usage.

Precedent: scripts/check-lineup-citations.py (a plugin-specific, conservative gate
living at repo scripts/ and invoked as its own validate-marketplace.yml step).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile

# ---------------------------------------------------------------------------
# Scan scope
# ---------------------------------------------------------------------------

PLUGIN = "memory-engineering"
ERRATA_RELPATH = os.path.join("knowledge", "memory-engineering-paradigms.md")
ERRATA_HEADING = "## Corrections"
TEXT_SUFFIXES = (".md", ".markdown", ".txt", ".py", ".sh", ".json", ".yaml", ".yml")

# An explicit, greppable, human-visible escape for a deliberate quotation outside
# the errata block. Chosen over a fuzzy "is there a correction nearby" heuristic:
# a fuzzy heuristic is what a reviewer waves through.
QUOTE_MARKER = "errata-quote"

# A3's vocabulary. Deliberately small and literal.
REFUTATION = re.compile(
    r"(?i)(\bfalse\b|\bwrong\b|\bnot\b|\bnever\b|\bno such\b|\bopposite\b"
    r"|\bcorrect(?:ed|ion)?\b|\binstead\b|\bin fact\b|\bactually\b|->|→|≠)"
)
PAIR_WINDOW = 4


class Claim:
    """One banned formulation, its qualifiers, and a canonical example of each."""

    def __init__(self, cid, label, pattern, guards, example, correction):
        self.cid = cid
        self.label = label
        self.pattern = re.compile(pattern)
        self.guards = [re.compile(g) for g in guards]
        self.example = example
        self.correction = correction

    def guarded(self, line):
        return any(g.search(line) for g in self.guards)


# The twelve, sourced verbatim from claims-table-a.md
# section "What must NOT be repeated".
CLAIMS = [
    Claim(
        "C01-47x-energy-spread",
        '"Two systems with identical accuracy differ by 47x in energy."',
        # The trailing \b is deliberately absent: it cannot fire after the Unicode
        # multiplication sign, and house style is the glyph ~2:1 over ASCII `x`.
        r"(?i)\b47\s*[x×]",
        [
            r"(?i)best[-\s]vs[-\s]worst",
            r"(?i)very different accuracy",
            r"(?i)differing accurac",
            r"(?i)\b20\.0\s*%",
            r"(?i)\bnot\b|\bnever\b|\bfalse\b",
        ],
        "Two systems with identical accuracy differ by 47x in energy.",
        "False - 47x is the best-vs-worst spread across systems with very "
        "different accuracy (47.0% vs 20.0%); the similar-accuracy figure is ~10x.",
    ),
    Claim(
        "C02-nvidia-lens",
        '"There is an NVIDIA lens." (MEMENTO results misattributed to NVIDIA)',
        # Attribution-shaped only. A bare vendor mention ("TensorRT (NVIDIA)")
        # is not a claim; "the NVIDIA lens" / "NVIDIA's results" is.
        r"(?i)(\bnvidia\b[^\n]{0,60}\b(lens|results?|published|paper|study|measured"
        r"|benchmark|found|reported|showed|built|figures?|numbers?)\b"
        r"|\b(lens|results?|paper|study|benchmark|figures?|numbers?)\b[^\n]{0,40}\bnvidia\b"
        r"|\bnvidia'?s\b)",
        [
            r"(?i)\bB200\b",
            r"(?i)GPU vendor",
            r"(?i)\bnot\b|\bnever\b|published nothing",
        ],
        "The NVIDIA lens gives 4,290 vs 2,447 tok/s.",
        "There is no NVIDIA lens - those are Microsoft's MEMENTO results measured "
        "on a single NVIDIA B200; NVIDIA appears only as the GPU vendor.",
    ),
    Claim(
        "C03-plugmem-fewer-tokens",
        '"PlugMem beat purpose-built designs while spending fewer tokens."',
        r"(?i)(plugmem[^\n]{0,80}fewer\s+tokens|fewer\s+tokens[^\n]{0,80}plugmem)",
        [
            r"(?i)same order of magnitude",
            r"(?i)\bcomparable\b",
            r"(?i)injected[-\s]context",
            r"(?i)information density",
            r"(?i)\bnot\b|\bnever\b|\bfalse\b",
        ],
        "PlugMem beat purpose-built designs while spending fewer tokens.",
        "The paper says the opposite about total tokens: comparable, within the "
        "same order of magnitude. The real claims are information density and "
        "injected-context tokens.",
    ),
    Claim(
        "C04-msr-built-plugmem",
        '"Microsoft Research built PlugMem."',
        r"(?i)(microsoft\s+research[^\n]{0,60}\b(built|created|developed|authored|made)\b"
        r"[^\n]{0,60}plugmem|plugmem[^\n]{0,60}\b(built|created|developed|authored)\b"
        r"[^\n]{0,60}microsoft\s+research)",
        [
            r"(?i)\bUIUC\b",
            r"(?i)\bTsinghua\b",
            r"(?i)co-authors?\b",
            r"(?i)\bnot\b|\bnever\b|\bfalse\b",
        ],
        "Microsoft Research built PlugMem.",
        "UIUC-led (Yang, He, Jiang, Han, Zhai) with Tsinghua and three MSR "
        "co-authors (Galley, Wang, Gao).",
    ),
    Claim(
        "C05-97-percent-first-pass",
        '"Memory cuts first-pass errors by 97%." (a customer testimonial, generalized)',
        r"\b97\s*%",
        [
            r"(?i)\bRakuten\b",
            r"(?i)\bWisedocs\b",
            r"(?i)testimonial",
            r"(?i)vendor[-\s]published|unaudited",
            r"(?i)\bnot\b|\bnever\b|attribute it or drop it",
        ],
        "Memory cuts first-pass errors by 97% and speeds verification by a third.",
        "Two different customers' vendor-published, unaudited testimonials "
        "(Rakuten 97%, Wisedocs 30%). Attribute it or drop it; never present it "
        "as an expected outcome.",
    ),
    Claim(
        "C06-anthropic-memory-is-files",
        '"Anthropic\'s memory is files on a filesystem."',
        r"(?i)(anthropic'?s?\s+memory[^\n]{0,60}files?\s+on\s+(?:a|the)\s+file\s?system"
        r"|memory\s+is\s+(?:just\s+)?files?\s+on\s+(?:a|the)\s+file\s?system)",
        [
            r"(?i)managed agents",
            r"(?i)client[-\s]side",
            r"(?i)only true of",
            r"(?i)/memories",
            r"(?i)\bnot\b|\bnever\b|\bfalse\b",
        ],
        "Anthropic's memory is files on a filesystem.",
        "True only of Managed Agents memory stores (public beta). The GA memory "
        "tool is client-side - /memories is a prefix your handler maps onto "
        "storage you own.",
    ),
    Claim(
        "C07-agent-sdk-memory-api",
        '"Anthropic ships an Agent SDK memory API."',
        r"(?i)(agent\s+sdk[^\n]{0,60}memory\s+api|memory\s+api[^\n]{0,60}agent\s+sdk)",
        [
            r"(?i)no such",
            r"(?i)does\s?n'?o?t?\s+exist|doesn'?t exist",
            r"(?i)do not invent",
            r"(?i)\bnot\b|\bnever\b|\bfalse\b",
        ],
        "Anthropic ships an Agent SDK memory API.",
        "No such documented surface exists. Do not invent one.",
    ),
    Claim(
        "C08-memento-without-arxiv-id",
        '"Memento" written without an arXiv ID (two unrelated papers share the name)',
        r"(?i)\bmementos?\b",
        [
            r"2604\.09852",
            r"2508\.16153",
            r"(?i)arxiv",
        ],
        "Memento manages its own context.",
        "Two unrelated agent-memory papers carry the name: Microsoft's "
        "context-management MEMENTO (2604.09852) and the case-based-reasoning "
        "agent Memento (2508.16153). Always disambiguate by arXiv ID.",
    ),
    Claim(
        "C09-quadratic-per-token",
        '"Attention is quadratic, so long context costs quadratically per token."',
        r"(?i)(quadratic[^\n]{0,60}per\s+token"
        r"|long[-\s]context[^\n]{0,40}costs?\s+quadratic"
        r"|attention\s+is\s+quadratic[^\n]{0,60}\bso\b)",
        [
            r"(?i)\bprefill\b",
            r"(?i)O\(n\)",
            r"(?i)kv[-\s]?cach",
            r"(?i)\bHBM\b",
            r"(?i)\bdecode\b",
            r"(?i)\bnot\b|\bnever\b|\bfalse\b",
        ],
        "Attention is quadratic, so long context costs quadratically per token.",
        "Prefill is O(n^2); KV-cached decode is O(n) per token. The real "
        "production constraint is KV bytes in HBM.",
    ),
    Claim(
        "C10-prefix-cache-is-memory",
        '"Prefix caching gives you cross-session memory."',
        r"(?i)prefix\s+cach\w*[^\n]{0,60}"
        r"(cross[-\s]session|persistence|persistent|durable)",
        [
            r"≠|!=",
            r"(?i)\bnot\b|\bnever\b|isn'?t",
            r"(?i)opportunistic",
            r"(?i)replica[-\s]local",
            r"(?i)\bevict|LRU\b",
        ],
        "Prefix caching gives you cross-session memory.",
        "vLLM evicts refcount-0 blocks LRU. It is opportunistic, replica-local, "
        "and not durable.",
    ),
    Claim(
        "C11-claude-md-controls",
        '"CLAUDE.md controls what the agent does."',
        # Predicate-shaped only: CLAUDE.md must be the SUBJECT doing the
        # controlling. A nearby "admission control" / "control additional
        # services" is not a claim about CLAUDE.md.
        r"(?i)(claude\.md\b[^\n]{0,30}\b(controls?|enforces?|dictates?|governs?)\s+"
        r"(?:what|how|which|the\s+agent|agent|behaviou?r)"
        r"|claude\.md\b[^\n]{0,30}\bis\b[^\n]{0,30}"
        r"\b(enforced\s+configuration|enforcement|a\s+control)\b)",
        [
            r"(?i)context,?\s+not\s+enforce",
            r"(?i)not\s+enforced",
            r"(?i)PreToolUse",
            r"(?i)\bnot\b|\bnever\b|\bfalse\b",
        ],
        "CLAUDE.md controls what the agent does.",
        "Anthropic's own docs: CLAUDE.md and auto memory are context, not "
        "enforced configuration - use a PreToolUse hook to actually block an "
        "action.",
    ),
    Claim(
        "C12-2606-published-or-stanfords",
        'arXiv 2606.06448 called "published", "peer-reviewed", or simply "Stanford\'s"',
        # The apostrophe class is widened to ['’]: `Stanford’s` with U+2019 is
        # literally the falsehood this claim exists to catch and went unmatched.
        r"(?i)(2606\.06448[^\n]{0,80}\b(published|peer[-\s]reviewed)\b"
        r"|\b(published|peer[-\s]reviewed)\b[^\n]{0,80}2606\.06448"
        r"|\bstanford['’]?s\b[^\n]{0,60}(2606\.06448|paper|study)"
        r"|2606\.06448[^\n]{0,60}\bstanford['’]?s\b)",
        [
            r"(?i)preprint",
            r"(?i)no venue",
            r"(?i)multi[-\s]institution",
            r"(?i)stanford[-\s]led",
            r"(?i)\bnot\b|\bnever\b|\bfalse\b",
        ],
        "The published, peer-reviewed 2606.06448 is Stanford's paper.",
        "June 2026 preprint, no venue, Stanford-led but multi-institution "
        "(incl. KU Leuven). Never call it published or peer-reviewed.",
    ),
]


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------


def _iter_text_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules"))
        for name in sorted(filenames):
            if name.endswith(TEXT_SUFFIXES):
                out.append(os.path.join(dirpath, name))
    return out


def _read_lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


def _errata_region(lines):
    """Return (start, end) line indexes of the `## Corrections` section, or None."""
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith(ERRATA_HEADING):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j]
        if s.startswith("## ") and not s.strip().startswith(ERRATA_HEADING):
            end = j
            break
    return (start, end)


def check_tree(root, verbose=False):
    """Run A1/A2/A3/A3b over one plugin tree. Returns (exit_code, report_lines)."""
    report = []
    if not os.path.isdir(root):
        return 0, ["not applicable: %s does not exist yet" % root]

    errata_path = os.path.join(root, ERRATA_RELPATH)
    if not os.path.isfile(errata_path):
        return 0, ["not applicable: %s does not exist yet" % errata_path]

    errata_lines = _read_lines(errata_path)
    region = _errata_region(errata_lines)
    if region is None:
        return 1, [
            "A2 FAIL: %s has no `%s` section - the errata block is the only "
            "sanctioned home for the twelve claims, and it is missing."
            % (os.path.relpath(errata_path, root), ERRATA_HEADING)
        ]
    r_start, r_end = region

    # ---- A1: regressions outside the errata region ------------------------
    violations = []
    qualified = []
    for path in _iter_text_files(root):
        lines = _read_lines(path)
        is_errata_file = os.path.abspath(path) == os.path.abspath(errata_path)
        for n, line in enumerate(lines):
            if is_errata_file and r_start <= n < r_end:
                continue  # A2/A3 own this region
            if QUOTE_MARKER in line:
                continue
            for claim in CLAIMS:
                if not claim.pattern.search(line):
                    continue
                rec = (os.path.relpath(path, root), n + 1, claim, line.strip())
                if claim.guarded(line):
                    qualified.append(rec)
                else:
                    violations.append(rec)

    # ---- A2: liveness inside the errata region ----------------------------
    region_text_lines = errata_lines[r_start:r_end]
    missing = []
    hits_by_claim = {}
    for claim in CLAIMS:
        hits = [i for i, ln in enumerate(region_text_lines) if claim.pattern.search(ln)]
        hits_by_claim[claim.cid] = hits
        if not hits:
            missing.append(claim)

    # ---- A3: refutation adjacency inside the region -----------------------
    # EVERY occurrence must be paired, not merely one of them: the "at least
    # one" reading let a correct errata entry inoculate every additional bare
    # occurrence of the same claim inside the region.
    unpaired = []
    for claim in CLAIMS:
        hits = hits_by_claim[claim.cid]
        if not hits:
            continue
        paired = True
        for i in hits:
            lo = max(0, i - PAIR_WINDOW)
            hi = min(len(region_text_lines), i + PAIR_WINDOW + 1)
            if not any(REFUTATION.search(region_text_lines[k]) for k in range(lo, hi)):
                paired = False
                break
        if not paired:
            unpaired.append(claim)

    # ---- A3b: no machine-readable target list hiding in an HTML comment ---
    # An HTML comment is invisible when rendered and fully visible to
    # grep/Read/chunked retrieval. Inside the errata region that is precisely
    # the withdrawn `<!-- grep-targets: ... -->` shape: the twelve falsehoods
    # with every correction stripped, in the file's most-retrieved chunk.
    # The +/-4-line adjacency rule cannot see it, because a one-line list sits
    # next to a real correction.
    comment_lists = []
    for i, ln in enumerate(region_text_lines):
        if "<!--" not in ln:
            continue
        cids = [c.cid for c in CLAIMS if c.pattern.search(ln)]
        if cids:
            comment_lists.append((r_start + i + 1, cids))

    # ---- report ------------------------------------------------------------
    rc = 0
    if violations:
        rc = 1
        report.append(
            "A1 FAIL - %d debunked claim(s) outside the `%s` block:"
            % (len(violations), ERRATA_HEADING)
        )
        for rel, ln, claim, text in violations:
            report.append("  %s:%d [%s]" % (rel, ln, claim.cid))
            report.append("      %s" % claim.label)
            report.append("      > %s" % text[:160])
        report.append(
            "  Fix: state the correction on the same line, move it into the "
            "`%s` block, or - if the quote is deliberate - mark the line with "
            "<!-- %s -->." % (ERRATA_HEADING, QUOTE_MARKER)
        )
    if missing:
        rc = 1
        report.append(
            "A2 FAIL - %d pattern(s) matched NOTHING in the errata block. "
            "Zero hits means the PATTERN is broken, not that the tree is clean:"
            % len(missing)
        )
        for claim in missing:
            report.append("  [%s] %s" % (claim.cid, claim.label))
    if unpaired:
        rc = 1
        report.append(
            "A3 FAIL - %d claim(s) appear in the errata block with no refutation "
            "within %d lines (a bare list of the phrasings, corrections stripped, "
            "is worse than no errata block):" % (len(unpaired), PAIR_WINDOW)
        )
        for claim in unpaired:
            report.append("  [%s] %s" % (claim.cid, claim.label))
    if comment_lists:
        rc = 1
        report.append(
            "A3 FAIL - %d HTML comment(s) inside the `%s` block carry a banned "
            "phrasing. A comment is invisible when rendered and fully visible to "
            "grep/Read/chunked retrieval - that is the corrections-stripped "
            "target list, not a sync aid:" % (len(comment_lists), ERRATA_HEADING)
        )
        for ln, cids in comment_lists:
            report.append("  %s:%d [%s]" % (ERRATA_RELPATH, ln, ", ".join(cids)))

    if rc == 0:
        report.append(
            "errata regression check passed: 0 unqualified claims outside the "
            "errata block; 12/12 patterns live inside it; 12/12 paired with a "
            "refutation."
        )
    if verbose and qualified:
        report.append(
            "  (%d correctly-qualified mention(s) outside the block, allowed:)"
            % len(qualified)
        )
        for rel, ln, claim, text in qualified:
            report.append("    %s:%d [%s] %s" % (rel, ln, claim.cid, text[:120]))
    return rc, report


# ---------------------------------------------------------------------------
# Self-test (the must-fail half)
# ---------------------------------------------------------------------------


def _write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _errata_body():
    out = ["**Last verified:** 2026-08-06", "", ERRATA_HEADING, ""]
    for i, claim in enumerate(CLAIMS, 1):
        out.append('%d. **"%s"**' % (i, claim.example))
        out.append("   Correction: %s" % claim.correction)
        out.append("")
    out.append("## Paradigms I-IV")
    out.append("")
    out.append("Body prose starts here.")
    return "\n".join(out) + "\n"


def _make_good(root):
    _write(os.path.join(root, ERRATA_RELPATH), _errata_body())
    # A correctly-qualified mention outside the block: guard tokens present.
    _write(
        os.path.join(root, "knowledge", "memory-surfaces-2026.md"),
        "**Last verified:** 2026-08-06\n\n"
        "# Surfaces\n\n"
        "The 47x figure is a best-vs-worst spread across systems with very "
        "different accuracy, not an identical-accuracy comparison.\n"
        "NVIDIA appears only as the B200 GPU vendor.\n"
        "Rakuten's vendor-published 97% is one customer's unaudited testimonial.\n"
        "MEMENTO (arXiv 2604.09852) is not the same paper as Memento "
        "(arXiv 2508.16153).\n"
        "Prefix caching is opportunistic and replica-local, so it is not "
        "persistence.\n"
        "CLAUDE.md is context, not enforced configuration - it does not control "
        "what the agent does; a PreToolUse hook does.\n",
    )
    # An explicitly-marked deliberate quote.
    _write(
        os.path.join(root, "best-practices", "README.md"),
        "# Index\n\nSee the errata block. <!-- errata-quote --> "
        "Microsoft Research built PlugMem.\n",
    )


def _make_bad(root):
    _make_good(root)
    _write(
        os.path.join(root, "skills", "choose-memory-paradigm", "SKILL.md"),
        "---\nname: choose-memory-paradigm\n---\n\n"
        "Two systems with identical accuracy differ by 47x in energy, so pick "
        "the cheaper one.\n",
    )


def _make_stripped_errata(root):
    """The RT-7 shape: the twelve phrasings with every correction removed."""
    lines = ["**Last verified:** 2026-08-06", "", ERRATA_HEADING, ""]
    for claim in CLAIMS:
        lines.append("- %s" % claim.example)
    lines += ["", "## Paradigms I-IV", "", "Body."]
    _write(os.path.join(root, ERRATA_RELPATH), "\n".join(lines) + "\n")


def _make_grep_targets_comment(root):
    """The RT-7 shape TB-5 actually proposed: a one-line machine-readable target
    list, as an HTML comment, immediately under the `## Corrections` heading.
    The +/-4-line adjacency rule cannot catch it - it sits beside a real
    correction - so A3b catches it by shape."""
    lines = _errata_body().split("\n")
    h = lines.index(ERRATA_HEADING)
    lines.insert(
        h + 1, "<!-- grep-targets: " + ", ".join(c.example for c in CLAIMS) + " -->"
    )
    _write(os.path.join(root, ERRATA_RELPATH), "\n".join(lines) + "\n")


def self_test():
    failures = []

    # 0. Every regex matches its own canonical banned formulation, and no guard
    #    fires on it. Without this the whole gate could be twelve dead patterns.
    for claim in CLAIMS:
        if not claim.pattern.search(claim.example):
            failures.append("regex dead: %s does not match its own example" % claim.cid)
        if claim.guarded(claim.example):
            failures.append(
                "guard too broad: %s's guard fires on the bare banned form" % claim.cid
            )

    tmp = tempfile.mkdtemp(prefix="errata-selftest-")
    try:
        good = os.path.join(tmp, "good", PLUGIN)
        _make_good(good)
        rc, rep = check_tree(good)
        if rc != 0:
            failures.append("KNOWN-GOOD tree was flagged (exit %d):\n    %s"
                            % (rc, "\n    ".join(rep)))

        bad = os.path.join(tmp, "bad", PLUGIN)
        _make_bad(bad)
        rc, rep = check_tree(bad)
        if rc == 0:
            failures.append("KNOWN-BAD tree passed - the A1 regression check has no teeth")
        elif not any("A1 FAIL" in ln for ln in rep):
            failures.append("KNOWN-BAD tree failed for the wrong reason: %s" % rep[:1])

        stripped = os.path.join(tmp, "stripped", PLUGIN)
        _make_good(stripped)
        _make_stripped_errata(stripped)
        rc, rep = check_tree(stripped)
        if rc == 0 or not any("A3 FAIL" in ln for ln in rep):
            failures.append(
                "CORRECTIONS-STRIPPED errata block passed A3 - the pairing check "
                "has no teeth"
            )

        targets = os.path.join(tmp, "targets", PLUGIN)
        _make_good(targets)
        _make_grep_targets_comment(targets)
        rc, rep = check_tree(targets)
        if rc == 0 or not any("A3 FAIL" in ln for ln in rep):
            failures.append(
                "GREP-TARGETS comment inside the errata block passed - A3b has "
                "no teeth (this is the exact mechanism TB-5 proposed and RT-7 "
                "withdrew)"
            )

        absent = os.path.join(tmp, "absent", PLUGIN)
        rc, rep = check_tree(absent)
        if rc != 0:
            failures.append("ABSENT plugin should be not-applicable, got exit %d" % rc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for f in failures:
            print("  - %s" % f, file=sys.stderr)
        return 1
    print(
        "self-test passed: 12/12 regexes match their own banned form and no guard "
        "over-fires; known-good clean; known-bad caught by A1; corrections-stripped "
        "errata caught by A3; grep-targets comment caught by A3b; absent plugin is "
        "not-applicable."
    )
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".", help="Repo root to scan (default: cwd).")
    ap.add_argument("--plugin", default=PLUGIN, help="Plugin directory name.")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="List correctly-qualified mentions that were allowed.")
    ap.add_argument("--self-test", dest="selftest", action="store_true",
                    help="Run the known-good / known-bad fixtures.")
    ap.add_argument("--must-fail", dest="selftest", action="store_true",
                    help="Alias for --self-test (audit-gates.sh teeth convention).")
    args = ap.parse_args(argv)

    if args.selftest:
        return self_test()

    root = os.path.join(args.root, "plugins", args.plugin)
    rc, report = check_tree(root, verbose=args.verbose)
    stream = sys.stderr if rc else sys.stdout
    for line in report:
        print(line, file=stream)
    return rc


if __name__ == "__main__":
    sys.exit(main())
