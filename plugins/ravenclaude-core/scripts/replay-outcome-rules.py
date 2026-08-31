#!/usr/bin/env python3
"""replay-outcome-rules.py — Phase 1 of verify-before-assert.

Measures each CANDIDATE pre-flight rule against the offline corpus BEFORE it is
written into a hook, and prints a random sample of its fires for hand
classification.

⛔ THE POINT OF THIS SCRIPT IS TO DELETE RULES. Phase 4 caps the pre-flight hook
at five rules, each individually droppable, and sets a hard rule: any rule over
20% hand-classified false positives is dropped before a line of hook code is
written, and the combined fire rate across survivors must stay under 2% of
evidence-bearing commands. Membership is decided by MEASUREMENT, never by how
good the rule sounds.

⛔ THE CORPUS IS NON-STATIONARY. It was produced by the un-instrumented agent, so
these are PRE-REGISTRATION THRESHOLDS, not predictions. Phase 11 re-measures
live, and a rule over its ceiling there is REMOVED, not tuned.

Usage
-----
    python3 replay-outcome-rules.py --corpus <dir> [--rule R-1] [--sample 40]
    python3 replay-outcome-rules.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys

COMBINED_CEILING = 0.02

# ── C15 defence: argv tokens only, never a quoted or heredoc body ────────────
# `worktree-guard.sh:_wg_bash_is_mutating` substring-matches the RAW command
# string, so PROSE DESCRIBING a command is classified as the command — verified
# still live 2026-08-25, and reproduced in-session when a heredoc of
# documentation was blocked. Any rule here that reads path-shaped tokens must
# strip quoted and heredoc bodies FIRST or it inherits that defect.
# control: `strip_bodies` on a heredoc containing an absolute path must return
# text with no absolute path, while a real argv path must survive. Both
# directions are asserted in --self-test.
_HEREDOC_RE = re.compile(r"<<-?\s*'?\"?(\w+)'?\"?.*?^\1", re.S | re.M)
_SQ_RE = re.compile(r"'[^']*'")
_DQ_RE = re.compile(r'"[^"]*"')


def strip_bodies(cmd: str) -> str:
    cmd = _HEREDOC_RE.sub(" ", cmd)
    cmd = _SQ_RE.sub(" ", cmd)
    cmd = _DQ_RE.sub(" ", cmd)
    return cmd


_LAST_LIMIT_RE = re.compile(r"\|\s*(head|tail)\b[^|]*$")
_ABS_PATH_RE = re.compile(r"(?:^|\s)(/[A-Za-z0-9._/-]{4,}|~/[A-Za-z0-9._/-]{2,})")
# ⛔ A COLLECTION endpoint ends AT the collection segment -- followed by `?`, a
# quote, or end-of-token. `/runs/<id>` is a SINGLE RESOURCE and pagination is
# meaningless there. MEASURED 2026-08-25: without the terminator this matched
# `/runs/31659533954/jobs`, `/commits/v4.2.2` and `/actions/jobs/<id>/logs`, and a
# hand classification of 12 fires read ~11 as false positives.
_COLLECTION_RE = re.compile(
    r"gh\s+api\s+['\"]?[^\s|'\"]*/(repos|issues|pulls|runs|jobs|workflows|commits|"
    r"branches|releases|artifacts|members|teams|packages)(?=[?'\"\s]|$)"
)

# Deliberate bounding: the author already decided how much they wanted. A rule
# that fires on an explicit bound is telling the author something they knew.
_BOUNDED_RE = re.compile(
    r"--limit\b|per_page=1\b|\[0\]|\bfor\s+\w+\s+in\b|--paginate|\bhead\s+-\d"
)
_PROSE_SCAN_RE = re.compile(r"--include=\*\.\{?md|\*\.md|\.md['\"]?\s")
_SEARCH_FAMILIES = frozenset({"grep", "find", "git"})

# The three idioms in which an EMPTY result is expected rather than misread.
# Derived from a hand classification of R-1's fires, not from taste.
_HANDLED_EMPTY_RE = re.compile(
    r"\|\|"                       # an explicit fallback: || echo / || true
    r"|(^|;|&&|\|\|)\s*(until|while)\b"   # a polling loop, where empty IS the condition
    r"|(^|;|&&)\s*(rm|pkill|kill|mkdir|touch|mv|cp)\b"  # mutating cleanup: no claim made
)


def _worktree_root(path: str) -> str:
    """Cheap textual stand-in for the tree a path belongs to.

    Offline we cannot run `git rev-parse`, so a path is attributed to its
    top-level project directory under $HOME. This is deliberately coarse: it is
    used to MEASURE a rule's fire rate, not to decide a live verdict.
    """
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 3 and parts[0] == "Users":
        return "/".join(parts[:3])
    return "/".join(parts[:2])


# ── Candidate rules ──────────────────────────────────────────────────────────
# Each returns True when the rule FIRES on the envelope.
def rule_r1(e):
    """2>/dev/null on an evidence-bearing read whose result then came back empty.

    The hazard is manufacturing a positive control: the redirect converts "I
    could not ask" into "there is nothing there" (member G2). Narrowed to the
    empty case because a suppressed-stderr command that still produced output
    did not mislead anyone.

    ⛔ NARROWED ON MEASUREMENT, 2026-08-25. As first written this fired 487 times
    (1.43%), and a hand classification of 14 random fires read 11 as false
    positives (79%, ceiling 20%). The FPs were not noise -- they were three
    idioms in which an empty result is EXPECTED rather than misread:
      * an explicit fallback (`... 2>/dev/null || echo "not running"`), where the
        author already handled the empty case;
      * a polling construct (`until grep -q ... 2>/dev/null; do sleep`), where
        empty is the loop condition;
      * mutating cleanup (`rm -r dist 2>/dev/null`), where there is no claim.
    control: the narrowed predicate must still fire on a bare suppressed read,
    which is asserted in --self-test alongside all three exclusions.
    """
    s = e["shape"]
    if not (s["is_evidence_bearing"] and s["has_2devnull"]
            and not s["has_stderr_merge"] and e["stdout_empty"]):
        return False
    return not _HANDLED_EMPTY_RE.search(e["cmd"])


def rule_r2(e):
    """An output limit is the LAST stage and the result was absence-shaped.

    This is the G-x rule: the answer was produced and correct, and the harness
    discarded the part that mattered. Narrowed to search-family commands whose
    limited output is not piped onward, because piping build or test output
    through `tail` for readability is pervasive ordinary practice here.
    """
    s = e["shape"]
    return (
        s["is_evidence_bearing"]
        and s["has_output_limit"]
        and s["tool_family"] in _SEARCH_FAMILIES
        and bool(_LAST_LIMIT_RE.search(e["cmd"]))
        and e["stdout_empty"]
    )


def rule_r3(e):
    """A collection endpoint read with the default page still in place.

    Measured precedent: a `/user/repos?per_page=100` read returned 98 rows and
    was taken for the whole set; `--paginate` returned 246.
    """
    cmd = e["cmd"]
    return (
        e["shape"]["is_evidence_bearing"]
        and bool(_COLLECTION_RE.search(cmd))
        and not _BOUNDED_RE.search(cmd)
    )


def rule_r4(e):
    """An argv path resolving outside the tree the command ran in.

    F2: searching the primary checkout from a linked worktree, or the plugin
    cache instead of the repo. Quoted and heredoc bodies are stripped first --
    the C15 anti-requirement.
    """
    if not e["shape"]["is_evidence_bearing"]:
        return False
    cwd = e.get("cwd") or ""
    if not cwd:
        return False
    home_root = _worktree_root(cwd)
    body = strip_bodies(e["cmd"])
    for m in _ABS_PATH_RE.finditer(body):
        tok = m.group(1)
        if tok.startswith("~"):
            tok = os.path.expanduser(tok)
        if not tok.startswith("/Users/"):
            continue
        if _worktree_root(tok) != home_root:
            return True
    return False


def rule_r5(e):
    """A search whose pattern would be satisfied by PROSE describing the thing.

    The source-scan-gate shape: one call spanning `*.md` and code, so a gate is
    satisfied by its own documentation.
    """
    s = e["shape"]
    return (
        s["is_evidence_bearing"]
        and s["tool_family"] == "grep"
        and bool(_PROSE_SCAN_RE.search(e["cmd"]))
    )


# ⛔ ONE RULE SURVIVED, and that is the intended shape of this file's output.
# Phase 4 caps the pre-flight hook at five rules and requires each to clear a
# measured fire-rate ceiling AND a hand-classified false-positive bar. Four did
# not. The survivors ship; the rest are recorded below, not deleted.
RULES = {
    "R-3": (rule_r3, 0.01, "collection endpoint read without --paginate"),
}

# ⛔ REJECTED RULES — recorded, not deleted, and asserted ABSENT by --self-test.
# A rule that was measured and rejected must not quietly reappear in a later edit
# because it still sounds good. This mirrors the treatment of `$?`-after-a-pipe,
# which measured 13 fires at 85% FP and is permanently out.
REJECTED = {
    "R-1": (
        "2>/dev/null on an evidence-bearing read",
        "⛔ THE PREDICATE IS NOT EVALUABLE AT PRE-FLIGHT. The hazard is a "
        "suppressed-stderr read whose result then came BACK EMPTY -- but a "
        "PreToolUse hook runs BEFORE the command, so `stdout_empty` does not "
        "exist yet. Measured lexically (the only form the hook can see): 8.28% "
        "of evidence-bearing commands, 4x the 2% combined ceiling, and a hand "
        "classification read nearly all as idiomatic glob-noise suppression. "
        "ITS VALUE IS ALREADY DELIVERED POST-HOC: triage-outcome.sh ranks member "
        "G2 first for exactly this shape, at the moment the result IS known. "
        "Re-adding it here would duplicate a working rule at 100x the noise.",
    ),
    "R-2": (
        "output limit is the last stage, absence-shaped result",
        "Same pre-flight evaluability problem as R-1, and over ceiling even "
        "post-hoc: 1.03% against a 1% bar at its narrowest. The G-x hazard is "
        "real and is covered by taxonomy member G7, which triage-outcome ranks "
        "post-hoc where the count is actually comparable.",
    ),
    "R-4": (
        "argv path resolving outside the tree the command ran in",
        "5.69% of evidence-bearing commands against a 2% ceiling. Working across "
        "trees is ordinary practice in this repo (worktrees are the sanctioned "
        "workflow), so the shape does not discriminate a defect from the house "
        "convention.",
    ),
    "R-5": (
        "search spanning .md and code in one call",
        "660 fires (1.94%); hand-classified 14/14 as false positives (100%, "
        "ceiling 20%). Every fire was an ordinary multi-extension search for a "
        "gate number or identifier, not a gate satisfied by its own prose. The "
        "hazard is real but is not separable lexically at this corpus size.",
    ),
    "$?-after-a-pipe": (
        "reading $? after a pipeline",
        "13 fires at 85% hand-classified FP. A channel that is wrong 85% of the "
        "time is how an agent learns to stop reading the channel.",
    ),
}

MIN_FIRES_TO_KEEP = 5


def load_corpus(corpus_dir):
    path = os.path.join(corpus_dir, "corpus.jsonl")
    if not os.path.isfile(path):
        print(f"SHORT: no corpus at {path} — run build-outcome-corpus.py first")
        return None
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def measure(envelopes, which=None, sample=0, seed=20260825):
    ev = [e for e in envelopes if e["shape"]["is_evidence_bearing"]]
    n = len(ev)
    if not n:
        print("SHORT: no evidence-bearing envelopes — the derivation is blind")
        return 2
    print(f"evidence-bearing envelopes: {n} of {len(envelopes)} ({n / len(envelopes):.1%})")
    print(f"combined ceiling: {COMBINED_CEILING:.0%} of evidence-bearing\n")
    rnd = random.Random(seed)
    survivors = []
    total_fire = set()
    for rid, (fn, ceiling, blurb) in sorted(RULES.items()):
        if which and rid != which:
            continue
        hits = [e for e in ev if fn(e)]
        rate = len(hits) / n
        over = rate > ceiling
        thin = len(hits) < MIN_FIRES_TO_KEEP
        if over:
            verdict = "OVER CEILING — narrow or drop"
        elif thin:
            verdict = f"TOO THIN (<{MIN_FIRES_TO_KEEP}) — drop rather than widen"
        else:
            verdict = "candidate — needs hand-classified FP <= 20%"
            survivors.append(rid)
            total_fire.update(id(e) for e in hits)
        print(f"{rid}  {blurb}")
        print(f"      fires {len(hits):>6}   rate {rate:7.2%}   ceiling {ceiling:.0%}   {verdict}")
        if sample and hits:
            take = rnd.sample(hits, min(sample, len(hits)))
            print(f"      --- {len(take)} random fires for hand classification ---")
            for e in take:
                cmd = e["cmd"].replace("\n", " ")[:150]
                print(f"        [{e['verdict']:<12}] {cmd}")
        print()
    if not which:
        combined = len(total_fire) / n
        ok = combined <= COMBINED_CEILING
        print(f"SURVIVORS: {', '.join(survivors) if survivors else '(none)'}")
        print(f"COMBINED fire rate across survivors: {combined:.2%} "
              f"({'within' if ok else 'OVER'} the {COMBINED_CEILING:.0%} ceiling)")
        if not ok:
            print("⛔ Over the combined ceiling — ship the lowest-FP rule only.")
            return 1
    return 0


def run_self_test() -> int:
    failures = []

    # ⛔ C15, both directions. A heredoc documenting a path must not fire R-4;
    # a real argv path in another tree must.
    doc = {
        "cwd": "/Users/x/RepoA",
        "cmd": "cat <<'EOF' > notes.md\nsee /Users/x/RepoB/src for the old copy\nEOF",
        "shape": {"is_evidence_bearing": True},
    }
    if rule_r4(doc):
        failures.append("R-4 fired on a heredoc BODY describing a path (the C15 trap)")
    real = {
        "cwd": "/Users/x/RepoA",
        "cmd": "grep -rn foo /Users/x/RepoB/src",
        "shape": {"is_evidence_bearing": True},
    }
    if not rule_r4(real):
        failures.append("R-4 is blind: it did not fire on a real cross-tree argv path")
    same = {
        "cwd": "/Users/x/RepoA",
        "cmd": "grep -rn foo /Users/x/RepoA/src",
        "shape": {"is_evidence_bearing": True},
    }
    if rule_r4(same):
        failures.append("R-4 fired on a path inside the SAME tree")

    # strip_bodies must remove a quoted path but keep a bare one
    if "/Users/x/RepoB" in strip_bodies("echo '/Users/x/RepoB'"):
        failures.append("strip_bodies left a single-quoted path in place")
    if "/Users/x/RepoB" not in strip_bodies("grep -rn foo /Users/x/RepoB"):
        failures.append("strip_bodies removed a bare argv path")

    # R-1 needs the empty result; a suppressed-stderr command that produced
    # output misled nobody.
    base = {"shape": {"is_evidence_bearing": True, "has_2devnull": True,
                      "has_stderr_merge": False, "has_output_limit": False,
                      "tool_family": "grep"}, "cmd": "grep -rn x . 2>/dev/null"}
    if not rule_r1({**base, "stdout_empty": True}):
        failures.append("R-1 did not fire on its own true positive")
    if rule_r1({**base, "stdout_empty": False}):
        failures.append("R-1 fired on a command that produced output")

    # R-2 must ignore a build log piped through tail
    b = {"shape": {"is_evidence_bearing": True, "has_output_limit": True,
                   "tool_family": "build", "has_2devnull": False,
                   "has_stderr_merge": False},
         "cmd": "npm run build | tail -20", "stdout_empty": True}
    if rule_r2(b):
        failures.append("R-2 fired on a build log piped through tail")

    # ⛔ R-1's three measured exclusions, each individually. A regression here
    # returns the rule to a 79% false-positive rate.
    for cmd, why in (
        ('grep -rn x . 2>/dev/null || echo "none"', "an explicit || fallback"),
        ("until grep -q done log 2>/dev/null; do sleep 2; done", "a polling loop"),
        ("rm -r dist 2>/dev/null; ls -d dist", "mutating cleanup"),
    ):
        if rule_r1({**base, "cmd": cmd, "stdout_empty": True}):
            failures.append(f"R-1 fired on {why}: {cmd!r}")

    # ⛔ A measured-and-rejected rule must stay rejected.
    for rid in REJECTED:
        if rid in RULES:
            failures.append(f"rejected rule {rid} has reappeared in the active set")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\nself-test FAILED — {len(failures)} finding(s)")
        return 1
    print("PASS: 12 checks — C15 both directions, strip_bodies both directions,")
    print("      R-1 requires an empty result and skips all three handled-empty idioms,")
    print("      R-2 ignores a piped build log, rejected rules stay rejected")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="replay candidate pre-flight rules")
    ap.add_argument("--corpus", default=os.path.expanduser(
        "~/RavenClaude/.ravenclaude/runs/forge/vba-impl/corpus"))
    ap.add_argument("--rule")
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return run_self_test()
    if args.rule and args.rule not in RULES:
        ap.error(f"unknown rule {args.rule!r}; known: {', '.join(sorted(RULES))}")
    envelopes = load_corpus(args.corpus)
    if envelopes is None:
        return 2
    return measure(envelopes, which=args.rule, sample=args.sample)


if __name__ == "__main__":
    sys.exit(main())
