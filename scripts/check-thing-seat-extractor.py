#!/usr/bin/env python3
"""Gate 136 — thing-seat.sh JSON-verdict extractor (P1, red-team FM1).

The seat's inline Python extractor (thing-seat.sh) is the ONLY code that turns a
model's raw text into a votable verdict, and NO other gate exercises it (Gate 33 is
engine-only via thing-decision.py; the mock gates short-circuit before it). This gate
extracts the REAL inline extractor from thing-seat.sh and drives it with fixtures.

The load-bearing property (FM1): a verdict salvaged from NEAR-JSON (attempt 2) may
only ever TIGHTEN — a repaired "allow" must resolve to "abstain", NEVER a votable
allow. A lenient parse that manufactures an allow from garbage is a security
regression worse than the bug it fixes (it converts the KB's abstain-pair into a
unanimous allow, bypassing the 2-abstain fail-closed floor).

Usage: python3 scripts/check-thing-seat-extractor.py            (exit 0 clean)
       python3 scripts/check-thing-seat-extractor.py --must-fail (exit 0 iff a
         mutated extractor is correctly caught — proves the teeth)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEAT = ROOT / "plugins" / "ravenclaude-core" / "scripts" / "thing-seat.sh"


def extract_py(src: str) -> str:
    """Pull the real `python3 -c '...'` extractor block out of thing-seat.sh."""
    m = re.search(r"python3 -c '\n(.*?)\n' 2>/dev/null", src, re.DOTALL)
    if not m:
        raise SystemExit("could not locate the extractor block in thing-seat.sh")
    return m.group(1)


def run(py: str, stdin: str) -> str:
    r = subprocess.run(
        [sys.executable, "-c", py], input=stdin, capture_output=True, text=True
    )
    return r.stdout.strip()


def verdict_of(out: str):
    if not out:
        return None
    try:
        return json.loads(out).get("verdict")
    except (ValueError, json.JSONDecodeError):
        return "<unparseable-output>"


# (name, raw model text, expected_verdict_or_None, byte_identical_expected_output|None)
CASES = [
    # 1. bare valid JSON -> parsed, byte-identical (happy path, attempt 1)
    ("bare-json", '{"verdict":"allow","confidence":0.9}', "allow",
     '{"verdict":"allow","confidence":0.9}'),
    # 2. fenced valid JSON -> salvaged by attempt 1 (fences aren't `{`) — regression guard
    ("fenced", '```json\n{"verdict":"deny","confidence":0.8}\n```', "deny", None),
    # 3. near-JSON deny (single quotes + trailing comma + Python literal) -> deny honored
    ("loose-deny", "{'verdict':'deny','injection_detected':True,'confidence':0.7,}", "deny", None),
    # 4. near-JSON ALLOW -> MUST resolve to abstain, NEVER allow (FM1 teeth)
    ("loose-allow", "{'verdict':'allow','confidence':0.9,}", "abstain", None),
    # 5. prose, no JSON -> empty output (the seat then exits 6, honest abstain)
    ("prose", "I think this command looks fine to me.", None, ""),
    # 6. valid JSON whose reasoning contains a brace -> correct object (must-fix #9 regression)
    ("brace-in-reason", '{"verdict":"deny","reasoning":"blocks the } char here"}', "deny", None),
]


def check(py: str) -> list:
    fails = []
    for name, raw, exp_v, exp_out in CASES:
        out = run(py, raw)
        v = verdict_of(out)
        if v != exp_v:
            fails.append(f"{name}: verdict {v!r} != expected {exp_v!r} (out={out!r})")
        if exp_out is not None and out != exp_out:
            fails.append(f"{name}: output {out!r} != byte-expected {exp_out!r}")
    return fails


def main() -> int:
    py = extract_py(SEAT.read_text(encoding="utf-8"))
    fails = check(py)
    if fails:
        print("Gate 136 FAILED — extractor fixtures:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("Gate 136 OK — bare-JSON byte-identical; near-JSON deny salvaged; "
          "near-JSON allow -> abstain (FM1); no-JSON empty; brace-in-reason correct.")
    return 0


def must_fail() -> int:
    """Prove the teeth: two mutants of the real extractor must be caught.
    (a) delete the monotonic downgrade -> loose-allow votes allow.
    (b) delete attempt-2 entirely       -> loose-deny yields nothing."""
    py = extract_py(SEAT.read_text(encoding="utf-8"))
    # mutant (a): strip the FM1 downgrade line
    mut_a = re.sub(r'\n\s*if obj\.get\("verdict"\) == "allow":\n\s*obj\["verdict"\] = "abstain"',
                   "", py)
    caught_a = mut_a != py and verdict_of(run(mut_a, "{'verdict':'allow','confidence':0.9,}")) == "allow"
    # mutant (b): cut everything from the attempt-2 marker onward
    idx = py.find("# Attempt 2")
    mut_b = py[:idx] if idx > 0 else py
    caught_b = idx > 0 and run(mut_b, "{'verdict':'deny',}") == ""
    if caught_a and caught_b:
        print("Gate 136 --must-fail OK: monotonic-strip -> allow (caught); "
              "attempt2-strip -> deny lost (caught).")
        return 0
    print(f"Gate 136 --must-fail FAILED: caught_a={caught_a} caught_b={caught_b} "
          "(a mutant was NOT detected — the fixtures lack teeth)")
    return 1


if __name__ == "__main__":
    sys.exit(must_fail() if (len(sys.argv) > 1 and sys.argv[1] == "--must-fail") else main())
