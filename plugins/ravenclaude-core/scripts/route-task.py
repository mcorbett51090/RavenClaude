#!/usr/bin/env python3
"""route-task.py — decide whether a task goes to the CHEAP lane (Grok) or stays
on Claude. Deterministic, model-free, stdlib-only, no network.

    route-task.py --task "<text>"        -> {"lane":"cheap"|"claude", ...}
    route-task.py --task-file <path>
    route-task.py --self-test

⛔ THE DEFAULT IS CLAUDE, AND THAT ASYMMETRY IS THE WHOLE DESIGN.
A task wrongly sent to Grok can produce a confidently wrong multi-file change that
costs more to unwind than it saved. A task wrongly kept on Claude costs only money.
So an unmatched task, an ambiguous task, and a task matching BOTH lanes all resolve
to `claude`. Cheap-lane routing is opt-in per rule, never a fallback.

⛔ THIS IS A TEXT CLASSIFIER OVER A TASK DESCRIPTION. It cannot read the repo, so
it cannot know that "fix the typo in auth.py" touches a security boundary. The
escalation rules are therefore deliberately BROAD and the cheap rules NARROW — a
false escalation is invisible, a false delegation is expensive.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time

# ── ESCALATE: broad by design. Any hit forces Claude, and beats every cheap rule.
_ESCALATE = [
    (
        "multi-file",
        r"\b(across|multiple|several|every|all)\s+(the\s+)?(file|module|package|service|caller|call site|surface)s?\b",
    ),
    # ⛔ Gaps between a verb and its object are BOUNDED (.{0,200}), never `.*`:
    # an unbounded gap rescans to the end of the text for every occurrence of
    # the verb, so a long paste of repeated trigger words took tens of seconds.
    (
        "multi-file",
        r"\b(refactor|migrate|rename)\b.{0,200}\b(codebase|repo|repository|project|everywhere)\b",
    ),
    (
        "architecture",
        r"\b(architect|architecture|design (the|a|an)|redesign|restructure|trade[- ]?off|should we|which approach)\b",
    ),
    # ⛔ Stems end in \w*, not a bare \b: `diagnos\b` matched only the stem
    # itself, so "diagnose", "credentials", "permissions", "secrets" and
    # "authentication" never escalated and routed to the cheap lane.
    (
        "debugging",
        r"\b(debug|root[- ]cause|why (is|does|did|are)|diagnos\w*|investigat\w*|figure out why|reproduce)\b",
    ),
    (
        "security",
        r"\b(security|auth\w*|credential\w*|secret\w*|token\w*|permission\w*|password\w*|passwd|(?:en|de)?crypt\w*|ssh|api[_ -]?key\w*|jwt|oauth|sandbox\w*|escalat\w*|vulnerab\w*|injection|csrf|xss)\b",
    ),
    (
        "guardrail-substrate",
        r"(hooks?/|tribunal|thing-orchestrator|audit-gates|guard-|comfort-posture|premise-gate)",
    ),
    ("ambiguous", r"\b(figure out|decide|not sure|unclear|somehow|best way|what should)\b"),
    (
        "irreversible",
        r"\b(deploy|publish|release|migrat\w*|drop (table|column)|delete|force[- ]push|prod(uction)?)\b",
    ),
]

# ── CHEAP: narrow by design. Only well-defined, single-surface, verifiable work.
_CHEAP = [
    (
        "single-file-edit",
        r"\b(in|to|for) (the )?(file )?[\w./-]+\.(py|sh|js|ts|tsx|jsx|md|json|ya?ml|css|html|rs|go|java|rb)\b",
    ),
    ("test-writing", r"\b(write|add|generate)\b.{0,200}\b(unit )?tests?\b"),
    (
        "summarize",
        r"\b(summari[sz]e|tl;?dr|condense|extract|list (the|all)|what does this (file|function|script) do)\b",
    ),
    (
        "reformat",
        r"\b(reformat|prettify|format|indent|sort (the )?(imports|list|keys)|convert .{0,200} to (json|yaml|csv|markdown))\b",
    ),
    (
        "mechanical-refactor",
        r"\b(rename|extract (a )?(function|method|variable)|inline|dedupe|remove unused)\b",
    ),
    ("boilerplate", r"\b(scaffold|boilerplate|stub out|template|skeleton)\b"),
    (
        "docstring",
        r"\b(docstring|doc ?comment|jsdoc|add comments?|document (the|this) (function|class|module))\b",
    ),
    ("one-liner", r"\b(one[- ]?liner|regex|sed|awk|jq) (that|to|for)\b"),
]

# Tier within the cheap lane. Everything defaults to `fast`; a cheap task that is
# still non-trivial gets `balanced`. `top` is never auto-assigned — if a task
# needs Grok's best model it is close enough to the escalation line to warrant a
# human choosing it explicitly.
_CHEAP_BALANCED = re.compile(r"\b(test|refactor|extract|scaffold|generate)\b", re.I)

# A task description this long is not a well-defined single-surface job, and the
# bounded-gap rules still cost O(len x gap) per call. Route it to claude without
# scanning — the safe direction of the routing asymmetry.
MAX_TASK_CHARS = 16000


def route(task: str) -> dict:
    t = (task or "").strip()
    if not t:
        return {
            "lane": "claude",
            "tier": "top",
            "rule": "empty",
            "reason": "empty task — default is claude",
        }
    if len(t) > MAX_TASK_CHARS:
        return {
            "lane": "claude",
            "tier": "top",
            "rule": "oversize",
            "reason": "task longer than %d chars — default is claude" % MAX_TASK_CHARS,
            "escalations": [],
            "cheap_signals": [],
        }

    esc = [name for name, pat in _ESCALATE if re.search(pat, t, re.I)]
    cheap = [name for name, pat in _CHEAP if re.search(pat, t, re.I)]

    if esc:
        return {
            "lane": "claude",
            "tier": "top",
            "rule": esc[0],
            "reason": "escalation rule matched: " + ", ".join(sorted(set(esc))),
            "escalations": sorted(set(esc)),
            "cheap_signals": sorted(set(cheap)),
        }
    if cheap:
        tier = "balanced" if _CHEAP_BALANCED.search(t) else "fast"
        return {
            "lane": "cheap",
            "tier": tier,
            "rule": cheap[0],
            "reason": "cheap-lane rule matched: " + ", ".join(sorted(set(cheap))),
            "escalations": [],
            "cheap_signals": sorted(set(cheap)),
        }
    return {
        "lane": "claude",
        "tier": "top",
        "rule": "unmatched",
        "reason": "no cheap-lane rule matched — default is claude",
        "escalations": [],
        "cheap_signals": [],
    }


# ── self-test ────────────────────────────────────────────────────────────────
_CASES = [
    # (task, expected_lane, why-this-case-exists)
    ("Write unit tests for parse_config in config.py", "cheap", "canonical cheap"),
    ("Summarize what this script does", "cheap", "summarization"),
    ("Rename the variable `foo` to `bar`", "cheap", "mechanical refactor"),
    ("Add docstrings to the functions in utils.py", "cheap", "docstring"),
    ("Write a regex that matches an ISO date", "cheap", "one-liner"),
    ("Reformat this JSON", "cheap", "reformat"),
    # escalations — each must beat any cheap signal present
    ("Debug why the tests fail in config.py", "claude", "debug beats single-file"),
    ("Write unit tests for the auth token validator", "claude", "security beats test-writing"),
    ("Rename this across every module in the repo", "claude", "multi-file beats rename"),
    ("Design the retry architecture", "claude", "architecture"),
    ("Summarize why the deploy broke", "claude", "debug+irreversible beats summarize"),
    ("Add comments to hooks/guard-destructive.sh", "claude", "guardrail substrate beats docstring"),
    ("Figure out the best way to structure this", "claude", "ambiguity"),
    # plural / derived security and debugging forms — each once routed cheap
    ("Write unit tests for the credentials loader in creds.py", "claude", "plural: credentials"),
    (
        "Add unit tests for the authentication middleware in mw.py",
        "claude",
        "derived: authentication",
    ),
    ("Write unit tests for the permissions checker in perms.py", "claude", "plural: permissions"),
    ("Write unit tests for the secrets handling in vault.py", "claude", "plural: secrets"),
    ("Write unit tests for the tokens table in db.py", "claude", "plural: tokens"),
    ("Write unit tests for the password hashing function in users.py", "claude", "password"),
    ("Summarize ~/.ssh/config", "claude", "ssh"),
    ("Rename the variable api_key to key in settings.py", "claude", "api_key"),
    ("Write unit tests for the jwt verifier in jwt.py", "claude", "jwt"),
    ("Write unit tests for the encryption helper in enc.py", "claude", "derived: encryption"),
    ("Please diagnose the failing test in a.py", "claude", "derived: diagnose"),
    ("Investigate the crash in a.py", "claude", "derived: investigate"),
    ("Write a script to migrate the users in a.py", "claude", "derived: migrate"),
    # defaults
    ("", "claude", "empty defaults to claude"),
    ("Make it better", "claude", "unmatched defaults to claude"),
]


def self_test() -> int:
    bad = 0
    for task, want, why in _CASES:
        got = route(task)["lane"]
        ok = got == want
        if not ok:
            bad += 1
        print(
            "  %s %-58s want=%-6s got=%-6s (%s)"
            % ("✓" if ok else "✗", ('"%s"' % task)[:58], want, got, why)
        )
    # ⛔ TEETH: prove the escalation rules are what produce the claude verdicts —
    # a router that returned "claude" unconditionally would pass every case above.
    forced = route("Write unit tests for parse_config in config.py")
    if forced["lane"] != "cheap":
        print("  ✗ TEETH: no task reaches the cheap lane — the router is a constant")
        bad += 1
    else:
        print("  ✓ teeth: at least one task DOES reach the cheap lane (not a constant)")
    # ⛔ BOUNDED COST: a long paste of repeated trigger words must not rescan to
    # the end of the text per occurrence (an unbounded `.*` took ~18 s at 100 KB).
    # Checked just under the oversize cap (exercises the bounded regexes) and
    # well over it (the cap short-circuit).
    slow = []
    for word in ("rename ", "write ", "add ", "convert "):
        for size in (MAX_TASK_CHARS - 16, 100_000):
            s = word * (size // len(word))
            t0 = time.perf_counter()
            route(s)
            dt = time.perf_counter() - t0
            if dt >= 0.1:
                slow.append("%r x %d chars %.3fs" % (word, len(s), dt))
    if slow:
        bad += 1
        print("  ✗ bounded cost: slow routes (want < 0.1s): " + "; ".join(slow))
    else:
        print("  ✓ bounded cost: repeated-trigger tasks up to 100 KB route in < 100 ms")
    # ⛔ TEETH: escalation must dominate, not merely co-occur.
    both = route("Write unit tests for the auth token validator")
    if both["lane"] != "claude" or not both["escalations"] or not both["cheap_signals"]:
        print("  ✗ TEETH: a task matching BOTH lanes did not resolve to claude-with-both-signals")
        bad += 1
    else:
        print("  ✓ teeth: a both-lanes task resolves to claude, and both signal sets are reported")
    print("\n  %d/%d pass" % (len(_CASES) + 3 - bad, len(_CASES) + 3))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task")
    ap.add_argument("--task-file")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    task = a.task or ""
    if a.task_file:
        try:
            task = open(a.task_file, encoding="utf-8").read()
        except OSError as exc:
            print(
                json.dumps(
                    {
                        "lane": "claude",
                        "tier": "top",
                        "rule": "unreadable",
                        "reason": "task-file unreadable: %s" % exc,
                    }
                )
            )
            return 0  # fail-safe: still routable, just to claude
    print(json.dumps(route(task), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
