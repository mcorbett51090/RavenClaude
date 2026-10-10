#!/usr/bin/env python3
"""claim_grounding_scan.py — single-process scan for claim-grounding-lint.sh.

WHY THIS EXISTS (SH-F9). The PostToolUse hook used to walk every markdown line
with a while-read loop that forked `echo | grep` / `sed` per check. On a large
doc (`docs/concepts.md`, ~3.7k lines) that was ~14–20 s of fork storm — still
advisory, but expensive enough to make the nudge unusable on the files that
matter most. This module ports the same three checks into ONE interpreter start.

DIVISION OF LABOUR (unchanged from the hook header):
  • This scanner owns SCOPE: frontmatter / fence / blockquote / heading skips,
    the check-1/2 regexes, and check-3's outcome/diagnostic/evidence/meta/
    prescriptive prefilters.
  • `classify_claim.py` owns TYPING for check 3 (the five grammatical families).
    Candidates that survive the prefilters are typed in-process via
    `classify_claim.families()` — never re-implemented here — so the planted
    canary / fixtures / must-fail battery stay the single source of "inference".

OUTPUT (stdout, one finding per line; stderr unused):
    c1<TAB>lineno<TAB>trimmed
    c2<TAB>lineno<TAB>trimmed
    c3<TAB>lineno<TAB>trimmed

Exit 0 always on a successful scan (including zero findings). Non-zero only when
the file cannot be read or the classifier import fails so hard we cannot type —
the hook treats any non-zero as fail-safe silence (checks 1–2 must not die
because check 3's module is missing).

Gate 224 C1 teeth neuter EVIDENCE / META / PRESCRIPTIVE via
CLAIM_GROUNDING_NEUTER_C3_SUPPRESSIONS=1 (a temp-file sed cannot safely rewrite
the multi-line assignments). Keep those three names as top-level
`NAME = (...)` so the fixture can assert they still exist.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path

# ── Check 1: unhedged absolute ───────────────────────────────────────────────
PHRASE = (
    r"(you can'?t|it'?s impossible|impossible to|there'?s no way|"
    r"there is no way|cannot be done|isn'?t possible|is not possible|"
    r"not possible to|never works)"
)
CONDITIONAL = r"\b(if|when|whenever|unless|because|since|until)\b"
C1_PROVENANCE = r"\[unverified|verified this session|verified against"

# ── Check 2: contract provenance ─────────────────────────────────────────────
CONTRACT = (
    r"(does not|doesn'?t|do not|don'?t) support|"
    r"(is|are|was|were) (not )?supported|"
    r"ha(s|ve) no (native|public|documented|official|supported)"
)
PROVENANCE = (
    r"\[docs-verified|\[verify-at-|\[unverified|\bverified\b|"
    r"20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]"
)
CONTRACT_SENSE = r"supported by"
CONTRACT_ELIDED = r"support(ed)?\s*[.,;:]*$"

# ── Check 3: inference-as-observation prefilters ─────────────────────────────
OUTCOME = (
    r"fail(s|ed|ing|ure|ures)?|break(s|ing)?|broke(n)?|bug|regress|error|"
    r"crash|hang|flake|flaky|leak|outage|timed out|timeout|denied|blocked|"
    r"stale|red|green|pass(es|ed|ing)?|work(s|ing)?|correct|incorrect|wrong|"
    r"missing|slow|down|exit\s+[0-9]|\b[45][0-9][0-9]\b"
)
DIAGNOSTIC = (
    r"caused\s+(by|the|it|this|that)|causing|"
    r"root\s+cause\s*(is|was|of|:|=)|"
    r"due\s+to|owing\s+to|led\s+to|"
    r"leads\s+to|resulted\s+in|"
    r"result(s|ing)\s+from|stems\s+from|"
    r"that\s+is\s+why|"
    r"the\s+reason\s+(is|was|for|why)|"
    r"therefore|hence|thus|consequently|as\s+a\s+result|"
    r"which\s+means|mean(s|ing)\s+that|"
    r"it\s+follows\s+that|attributable\s+to|"
    r"to\s+blame|at\s+fault|the\s+culprit"
)
# Gate 224 C1 sed-rewrites these three assignments — keep the names + shape.
EVIDENCE = (
    r"\[docs-verified|\[verify-at-|\[unverified|verified this session|"
    r"verified against|\bverified\b|\bmeasured\b|\breproduced\b|\bcontrol:|"
    r"20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]|"
    r"[A-Za-z0-9_./-]+\.(sh|py|mjs|js|ts|json|ya?ml|md|toml|txt):[0-9]+|"
    r"(->|=>|→)"
)
META = (
    r"anti-?pattern|for example|for instance|\be\.g\.|example:|counter-?example|"
    r"(do not|don'?t|never)\s+(write|say|claim|assert|state)|"
    r"would (be )?(get )?flagged|"
    r"this (hook|lint|check|gate|nudge|rule)|"
    r"\binference\b|\binferences\b|\bobservation\b|\bobservations\b|"
    r"\bhypothes|hypothetical|\bsuppose\b|imagine|"
    r'"[^"]*"|“[^”]*”'
)
PRESCRIPTIVE = (
    r"\b(must|should|shall|needs?\s+to|ought\s+to|"
    r"have\s+to|has\s+to|plan\s+to|"
    r"going\s+to)\b"
)

ESCAPE = "claim-lint-ok"
FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^\s*#{1,6}\s")
BLOCKQUOTE_RE = re.compile(r"^\s*>")

# Gate 224 C1 teeth: prove EVIDENCE/META/PRESCRIPTIVE are load-bearing by
# neutering them via env (a temp-file sed cannot rewrite the multi-line
# assignments without breaking Python syntax). When set, the describing-doc
# fixture MUST fire — same contract as the old bash `grep -qiE "$evidence"` sed.
if os.environ.get("CLAIM_GROUNDING_NEUTER_C3_SUPPRESSIONS") == "1":
    EVIDENCE = r"zzzNEVERMATCHzzz"
    META = r"zzzNEVERMATCHzzz"
    PRESCRIPTIVE = r"zzzNEVERMATCHzzz"


def _compile(pattern: str) -> re.Pattern[str]:
    # Bash patterns used grep -E POSIX [[:space:]]; Python re has no POSIX
    # classes, so the ported patterns use \s. re.IGNORECASE matches grep -i.
    return re.compile(pattern, re.IGNORECASE)


def _load_classify_claim():
    """Import the classifier without requiring a package install.

    Prefer the sibling of this file; fall back to $CLAUDE_PLUGIN_ROOT/scripts
    so a Gate-224 teeth mutant living in $TMP still finds the real module.
    """

    candidates = [Path(__file__).resolve().parent / "classify_claim.py"]
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if root:
        candidates.append(Path(root) / "scripts" / "classify_claim.py")
    path = next((c for c in candidates if c.is_file()), None)
    if path is None:
        return None
    spec = importlib.util.spec_from_file_location("classify_claim", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan(path: Path) -> list[tuple[str, int, str]]:
    """Return findings as (check, lineno, trimmed) for c1/c2/c3."""
    phrase = _compile(PHRASE)
    conditional = _compile(CONDITIONAL)
    c1_prov = _compile(C1_PROVENANCE)
    contract = _compile(CONTRACT)
    provenance = _compile(PROVENANCE)
    contract_sense = _compile(CONTRACT_SENSE)
    contract_elided = _compile(CONTRACT_ELIDED)
    outcome = _compile(OUTCOME)
    diagnostic = _compile(DIAGNOSTIC)
    evidence = _compile(EVIDENCE)
    meta = _compile(META)
    prescriptive = _compile(PRESCRIPTIVE)

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    findings: list[tuple[str, int, str]] = []
    c3_candidates: list[tuple[int, str]] = []
    in_fence = False
    in_frontmatter = False
    first_nonblank_seen = False

    for lineno, line in enumerate(lines, start=1):
        if not first_nonblank_seen and line.strip():
            first_nonblank_seen = True
            if line == "---":
                in_frontmatter = True
                continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            continue

        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if BLOCKQUOTE_RE.match(line):
            continue
        if HEADING_RE.match(line):
            continue
        if ESCAPE in line.lower():
            continue

        # Check 3 candidates FIRST — same order as the bash hook, so checks 1–2
        # keep their continue-skips-the-rest-of-the-line semantics below.
        if outcome.search(line) and diagnostic.search(line):
            if (
                not evidence.search(line)
                and not meta.search(line)
                and not prescriptive.search(line)
            ):
                c3_candidates.append((lineno, line))

        # Check 1 — unhedged absolute. A conditional / provenance continue skips
        # check 2 on this line (byte-identical to the original bash `continue`).
        if phrase.search(line):
            if conditional.search(line):
                continue
            if c1_prov.search(line):
                continue
            findings.append(("c1", lineno, line.strip()))

        # Check 2 — contract provenance (independent of check 1 when check 1
        # did not `continue`).
        if contract.search(line):
            if conditional.search(line):
                continue
            if provenance.search(line):
                continue
            if contract_sense.search(line):
                continue
            if contract_elided.search(line):
                continue
            findings.append(("c2", lineno, line.strip()))

    if c3_candidates:
        cc = _load_classify_claim()
        if cc is not None and hasattr(cc, "families"):
            for lineno, line in c3_candidates:
                try:
                    hits = cc.families(line)
                except (TypeError, AttributeError):
                    continue
                if "causal" not in hits:
                    continue
                # classify_claim types any family hit as inference; we only keep
                # the causal family (same as the bash hook's *,causal,* case).
                findings.append(("c3", lineno, line.strip()))

    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", required=True, help="markdown path to scan")
    args = ap.parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        return 0
    try:
        findings = scan(path)
    except OSError:
        return 0
    for check, lineno, trimmed in findings:
        # TSV: check / lineno / trimmed. Tabs in the line would break the
        # consumer — replace with spaces (markdown prose almost never has them).
        safe = trimmed.replace("\t", " ")
        sys.stdout.write("%s\t%d\t%s\n" % (check, lineno, safe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
