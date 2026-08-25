#!/usr/bin/env python3
"""check-portable-floor.py — Phase 8 of verify-before-assert.

The portable text floor is the ONLY form the cause discipline takes on a host
that runs no hooks. R1 is layered: deterministic hooks where they fire, protocol
text as the floor. This asserts the floor actually reaches each projection, says
the same thing in each, and does not overclaim what it is.

⛔ THE ANTI-OVERCLAIM ASSERTION IS THE POINT, NOT DECORATION.
A projection that reads as though the rule is ENFORCED on that host is worse than
no projection: it manufactures the false sense of coverage that R7 exists to
prevent, in prose, on the hosts least able to check it. Aider reads nothing
automatically, Copilot Chat's hooks are `supported: false`, and neither carries
the model's chat text on any event. The floor is a behavioural rule; the honest
limit paragraph is what keeps it honest, and it is required verbatim.

Usage:
    check-portable-floor.py --check
    check-portable-floor.py --must-fail
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AGENTS = os.path.join(_REPO, "AGENTS.md")
_HEADER = "## Naming a cause (the portable floor)"

_RITUAL = (
    "list the classes that could produce",
    "Name the ONE discriminating probe that splits the top two",
    "write the cause as a hypothesis, not a fact",
)

_HONEST_LIMIT = (
    "No hook on any host carries the model's chat text, so the place the "
    "confident inference is most often spoken is structurally out of reach."
)

# ⛔ The verbs the plan names. A form like "enforced sliver" or "not the rule's
# enforcement" is deliberately NOT matched: both appear only inside the honest
# limit paragraph, where they are a DISCLAIMER of enforcement rather than a claim
# of it. Matching them would make the mandatory honest paragraph unshippable —
# a check that forbids its own required text.
_OVERCLAIM = re.compile(r"\b(blocks|prevents|enforces)\b", re.I)


def _section(text: str, header: str) -> str:
    lines = text.split("\n")
    try:
        start = lines.index(header)
    except ValueError:
        return ""
    out = [lines[start]]
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)


def _projection(cmd) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=_REPO)
    except Exception:
        return ""
    return p.stdout if p.returncode == 0 else ""


def check() -> int:
    fails = []

    try:
        with open(_AGENTS, encoding="utf-8") as fh:
            agents = fh.read()
    except OSError as exc:
        print(f"FAIL: cannot read AGENTS.md: {exc}")
        return 2

    source = _section(agents, _HEADER)
    if not source.strip():
        fails.append(f"AGENTS.md has no section {_HEADER!r} — the floor has no source")

    surfaces = [("AGENTS.md (source)", source)]

    aider = _projection([sys.executable, "scripts/generate-aider-conventions.py"])
    if not aider:
        fails.append("the aider projector produced nothing")
    else:
        surfaces.append(("CONVENTIONS.md (aider)", _section(aider, _HEADER)))

    copilot = ""
    cop_path = os.path.join(_REPO, "plugins", "ravenclaude-core", "copilot", "AGENTS.md")
    if os.path.exists(cop_path):
        with open(cop_path, encoding="utf-8") as fh:
            copilot = fh.read()
        surfaces.append(("copilot/AGENTS.md", _section(copilot, _HEADER)))
    else:
        fails.append("copilot/AGENTS.md is absent — the Copilot Chat lane has no floor")

    for name, body in surfaces:
        if not body.strip():
            fails.append(f"{name}: the floor section is missing entirely")
            continue

        # 1. The ritual's three steps, in every projection.
        for step in _RITUAL:
            if step not in body:
                fails.append(f"{name}: ritual step missing — {step!r}")

        # 2. All five class letters, so step 1 has something to enumerate against.
        for letter in ("E", "F", "G", "H", "I"):
            if not re.search(r"\*\*%s\*\*" % letter, body):
                fails.append(f"{name}: class letter {letter} is not present")

        # 3. ⛔ Anti-overclaim.
        hit = _OVERCLAIM.search(body)
        if hit:
            fails.append(
                f"{name}: contains the enforcement verb {hit.group(0)!r} — this floor "
                "is a behavioural rule on hosts that run no hooks, and claiming "
                "enforcement there manufactures coverage that does not exist"
            )

        # 4. The honest limit, verbatim.
        if _HONEST_LIMIT not in body:
            fails.append(f"{name}: the honest-limit paragraph is missing or altered")

    # 5. ⛔ HEADER-RENAME CANARY. The aider projector must RAISE on a missing
    #    header rather than shipping a CONVENTIONS.md with a hole in it.
    #    control: the unmodified tree returns rc=0 above, so a non-zero here is
    #    the rename and not a broken projector.
    with tempfile.TemporaryDirectory() as tmp:
        backup = os.path.join(tmp, "AGENTS.md")
        shutil.copy(_AGENTS, backup)
        try:
            renamed = agents.replace(_HEADER, "## Renamed Header Canary")
            with open(_AGENTS, "w", encoding="utf-8") as fh:
                fh.write(renamed)
            p = subprocess.run(
                [sys.executable, "scripts/generate-aider-conventions.py"],
                capture_output=True, text=True, timeout=120, cwd=_REPO,
            )
            if p.returncode == 0:
                fails.append(
                    "HEADER-RENAME CANARY: the aider projector exited 0 with the "
                    "section renamed away — it would ship a floor-shaped hole"
                )
        finally:
            shutil.copy(backup, _AGENTS)

    for f in fails:
        print(f"FAIL: {f}")
    if fails:
        print(f"\nportable floor FAILED — {len(fails)} finding(s)")
        return 2
    print(
        f"PASS: floor present in {len(surfaces)} surface(s) — ritual x3, five classes, "
        "honest limit verbatim, no enforcement verb, rename canary raises"
    )
    return 0


def must_fail() -> int:
    """An overclaiming floor must be caught.

    ⛔ Teeth for the assertion that actually protects the reader. A floor that
    says the rule is enforced on a host with no hooks is the failure mode; if
    this passes, the anti-overclaim check is not measuring anything.
    """
    try:
        with open(_AGENTS, encoding="utf-8") as fh:
            agents = fh.read()
    except OSError:
        print("MUST-FAIL SETUP FAILED: cannot read AGENTS.md")
        return 1
    body = _section(agents, _HEADER)
    if not body.strip():
        print("MUST-FAIL SETUP FAILED: no floor section to mutate")
        return 1
    poisoned = body + "\n\nThis rule blocks the write on every host.\n"
    if not _OVERCLAIM.search(poisoned):
        print("MUST-FAIL VIOLATED: an overclaiming line was not caught")
        return 1
    if _OVERCLAIM.search(body):
        print("MUST-FAIL VIOLATED: the UNMODIFIED floor already trips the check, so a "
              "pass would be indistinguishable from the poisoned case")
        return 1
    # ⛔ AND THE VERDICT MUST COME FROM check() ITSELF (P1-3). Everything above
    # exercises the _OVERCLAIM regex — a HELPER. A check() blinded so it can
    # report nothing satisfies it, leaving --check AND --must-fail both at rc=0,
    # which is the shape this gate exists to detect. Assert the ENTRY POINT.
    #
    # ⛔ The poisoned tree is a TEMP COPY, never the real AGENTS.md. check()
    # mutates-and-restores that file in place (P2-5), so driving the mutant over
    # the real path would leave a poisoned AGENTS.md behind if this process died
    # between the write and the restore. The rc asserted is MEASURED: unmutated
    # scores 0 and a planted enforcement claim drives check() to 2 (2026-08-25).
    import contextlib as _ctx
    import hashlib as _hash
    import io as _io
    import tempfile as _tf

    def _digest(path):
        with open(path, "rb") as fh:
            return _hash.sha256(fh.read()).hexdigest()

    before = _digest(_AGENTS)
    with _ctx.redirect_stdout(_io.StringIO()):
        real_rc = check()
    if real_rc != 0:
        print(f"MUST-FAIL SETUP FAILED: the unmutated floor already fails check() "
              f"(rc={real_rc}), so a red result below would be ambiguous")
        return 1

    saved_agents = _AGENTS
    try:
        with _tf.TemporaryDirectory() as tmp:
            fake = os.path.join(tmp, "AGENTS.md")
            with open(fake, "w", encoding="utf-8") as fh:
                fh.write(agents.replace(body, poisoned, 1))
            globals()["_AGENTS"] = fake
            with _ctx.redirect_stdout(_io.StringIO()):
                bad_rc = check()
    finally:
        globals()["_AGENTS"] = saved_agents

    if bad_rc != 2:
        print(f"MUST-FAIL VIOLATED: check() returned {bad_rc} on a floor carrying a "
              "planted enforcement claim — the overclaim assertion is not reaching "
              "the entry point's verdict")
        return 1
    if _digest(_AGENTS) != before:
        print("MUST-FAIL VIOLATED: the real AGENTS.md changed while running the "
              "teeth — check()'s mutate-and-restore did not restore (P2-5)")
        return 1

    print("PASS (--must-fail): a planted enforcement claim is caught, it drives "
          "check() to 2 while the real floor scores 0, and AGENTS.md is byte-identical")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="portable text floor")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    if args.must_fail:
        return must_fail()
    return check()


if __name__ == "__main__":
    sys.exit(main())
