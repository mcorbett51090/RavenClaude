#!/usr/bin/env python3
"""check-memory-engineering-reachability.py — the memory-security lane must be reachable.

TB-1 shipped memory security as a SKILL (`memory-poisoning-review`) rather than a
fourth agent, and conditioned that ruling on the skill being demonstrably reachable:
"If any of the four is dropped during the build, the skill is undiscoverable and this
ruling's premise is false - that is exactly the condition worth failing on."

Nothing in the repo checked the routes. `check-md-links.py` proves a link RESOLVES
once written; no gate proves it was WRITTEN, and `check-frontmatter.py` validates a
`description`'s TYPE and LENGTH but never its CONTENT (see its `_violations()` -
strict-YAML parse, non-empty description, <=300 chars, tools allowlist, scenario
schema, cross-plugin name uniqueness; no content assertion exists at any line).

This gate is the missing presence half. It pairs with `check-md-links.py`, which is
already PR-blocking: this file asserts the route EXISTS, that one asserts its target
RESOLVES. Neither alone is sufficient and both are cheap.

Deliberately a flat, declarative ROUTES table: the point is that a human reviewing
this PR can read the four routes in fifteen seconds and see one is missing.

NOT-APPLICABLE IS NOT A FAILURE: routes whose owning file does not exist yet are
reported as `n/a` and do not fail, so this can land before the plugin does. Once the
file exists, its routes are hard requirements.

Exit 0 = every applicable route present. Exit 1 = at least one route missing.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

PLUGIN_PATH = os.path.join("plugins", "memory-engineering")
CORE_PATH = os.path.join("plugins", "ravenclaude-core")

# (route id, file relative to repo root, human description, [required regexes])
ROUTES = [
    (
        "R1",
        os.path.join(CORE_PATH, "agents", "security-reviewer.md"),
        "core security-reviewer carries an inline prior linking the skill "
        "(a markdown LINK, never a backticked path - check-md-links.py strips "
        "inline code spans, so a backticked path is never validated on any host)",
        [
            r"\]\(\.\./\.\./memory-engineering/skills/memory-poisoning-review/SKILL\.md\)",
        ],
    ),
    (
        "R2",
        os.path.join(PLUGIN_PATH, "agents", "memory-architect-lead.md"),
        "the in-plugin routing keyword: the literal token `poisoning` in the "
        "agent `description` - the only route that survives a consumer disabling "
        "ravenclaude-core to reclaim agent-description budget",
        [
            # Anchored to the frontmatter `description:` scalar, not the body.
            r"(?ms)^---\n.*?^description:[^\n]*\bpoisoning\b",
        ],
    ),
    (
        "R3",
        os.path.join(PLUGIN_PATH, "knowledge", "memory-security-and-privacy.md"),
        "the in-PR half of the ai-red-teaming seam: this plugin names their ASI06 "
        "row (the reciprocal edit is a follow-on PR against ai-red-teaming, so it "
        "is NOT gated here - gating a file this PR may not touch is what made the "
        "original R3 unsatisfiable)",
        [
            r"\]\(\.\./\.\./ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree\.md\)",
            r"\bASI06\b",
        ],
    ),
    (
        "R4",
        os.path.join(PLUGIN_PATH, "CLAUDE.md"),
        "the in-plugin skills index lists the skill with a resolving link "
        "(the `## N. Skills in this plugin` section - the shape 89 of 179 plugin "
        "constitutions already use, including both AI-cluster seam siblings)",
        [
            r"(?m)^##\s*\d*\.?\s*Skills in this plugin\b",
            r"\]\(skills/memory-poisoning-review/SKILL\.md\)",
        ],
    ),
]


def check(root):
    # The whole question only exists once the plugin does. Before it lands,
    # every route is vacuously n/a - including R1, whose file (core's
    # security-reviewer.md) already exists and must NOT red main today.
    if not os.path.isdir(os.path.join(root, PLUGIN_PATH)):
        return [(rid, "n/a", rel, desc, "memory-engineering does not exist yet")
                for rid, rel, desc, _ in ROUTES]
    results = []
    for rid, rel, desc, patterns in ROUTES:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            # The plugin exists, so every route's owning file is required by
            # TB-5's manifest. A deleted file must not launder into `n/a`.
            results.append((rid, "FAIL", rel, desc, "route file is missing"))
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        missing = [p for p in patterns if not re.search(p, text)]
        if missing:
            results.append((rid, "FAIL", rel, desc, "missing: " + " | ".join(missing)))
        else:
            results.append((rid, "ok", rel, desc, ""))
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".", help="Repo root (default: cwd).")
    ap.add_argument("--must-fail", action="store_true",
                    help="Teeth: assert a tree with the routes removed is caught.")
    args = ap.parse_args(argv)

    if args.must_fail:
        import shutil
        import tempfile
        tmp = tempfile.mkdtemp(prefix="reach-teeth-")
        try:
            # Known-good: synthesize every route.
            for rid, rel, _desc, _patterns in ROUTES:
                p = os.path.join(tmp, "good", rel)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                body = {
                    "R1": "- [`memory-poisoning-review`]"
                          "(../../memory-engineering/skills/memory-poisoning-review/SKILL.md)\n",
                    "R2": "---\nname: memory-architect-lead\n"
                          "description: Owns memory-system design: paradigm, surface, "
                          "write-path trust boundary and poisoning exposure.\ntools: Read\n---\n",
                    "R3": "ASI06 is owned by "
                          "[the taxonomy row]"
                          "(../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md).\n",
                    "R4": "## 5. Skills in this plugin\n\n"
                          "| [`memory-poisoning-review`]"
                          "(skills/memory-poisoning-review/SKILL.md) | ASI06 review |\n",
                }[rid]
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(body)
            good = check(os.path.join(tmp, "good"))
            if any(s == "FAIL" for _, s, _, _, _ in good):
                print("TEETH FAIL: synthesized known-good tree was flagged", file=sys.stderr)
                for r in good:
                    print("  %s" % (r,), file=sys.stderr)
                return 1
            if any(s == "n/a" for _, s, _, _, _ in good):
                print("TEETH FAIL: known-good tree left a route n/a", file=sys.stderr)
                return 1
            # Known-bad: same tree, every required token stripped.
            for _rid, rel, _desc, _patterns in ROUTES:
                dst = os.path.join(tmp, "bad", rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "w", encoding="utf-8") as fh:
                    fh.write("placeholder with none of the required tokens\n")
            bad = check(os.path.join(tmp, "bad"))
            failed = [r for r in bad if r[1] == "FAIL"]
            if len(failed) != len(ROUTES):
                print("TEETH FAIL: a stripped tree was not caught on every route",
                      file=sys.stderr)
                for r in bad:
                    print("  %s" % (r,), file=sys.stderr)
                return 1
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        print("teeth passed: synthesized known-good clean; every route caught when stripped.")
        return 0

    results = check(args.root)
    bad = [r for r in results if r[1] == "FAIL"]
    stream = sys.stderr if bad else sys.stdout
    for rid, status, rel, desc, note in results:
        print("  [%-3s] %-4s %s" % (rid, status, rel), file=stream)
        if status != "ok":
            print("         %s" % desc, file=stream)
            if note:
                print("         %s" % note, file=stream)
    if bad:
        print(
            "\nmemory-security lane reachability FAILED on %d route(s). TB-1 conditioned "
            "the skill-not-agent ruling on these routes; a missing one falsifies the "
            "ruling's premise." % len(bad),
            file=sys.stderr,
        )
        return 1
    live = sum(1 for r in results if r[1] == "ok")
    print("reachability OK: %d/%d routes present (%d not yet applicable)."
          % (live, len(ROUTES), len(ROUTES) - live))
    return 0


if __name__ == "__main__":
    sys.exit(main())
