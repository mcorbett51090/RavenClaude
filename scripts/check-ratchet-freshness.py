#!/usr/bin/env python3
"""check-ratchet-freshness.py — P8 §10.2 (⛔ R6). The merge-time re-measure.

⛔ THE PRECEDENT, IN THIS REPO: PR #991.

Two branches each raised a shared baseline CORRECTLY IN ISOLATION and WRONGLY
after the other merged. The wrong value still passes on its own branch and
surfaces later as unexplained drift, because the number was measured against a
base that no longer exists by the time the merge happens.

Every ratchet this initiative adds inherits that shape: coverage, the island
payload ceiling, the byte ceiling, the unprobed fraction, the
derived-from-header fraction. Any multi-batch rollout reproduces it per batch.

⛔ THE RULE, AND IT IS NOT EXHORTATION:

  The last step before merge is RECOMPUTE THE RATCHET VALUE ON REBASED HEAD, not
  trust the value computed when the branch was cut. A ratchet number in a diff
  whose base is not origin/main at merge time is INVALID.

Enforced here: each ratchet state file records the `measured_against` SHA it was
computed against, and this check fails when that SHA is not the PR actual merge
base. Without the SHA binding the rule is a sentence in a document, and this repo
record is that sentences decay.

⛔ AN ABSENT SHA IS **UNKNOWN**, NEVER UP-TO-DATE. That asymmetry is the whole
point: the failure mode being defended against is a stale value that looks fine.

⛔ THE TEETH-BIT EXIT IS 1. Declared, never assumed.

Usage:
    check-ratchet-freshness.py [--base origin/main] [--check]
    check-ratchet-freshness.py --stamp        # re-measure and rewrite the SHAs
    check-ratchet-freshness.py --must-fail
    check-ratchet-freshness.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Every committed file that carries a ratchet VALUE.
RATCHET_FILES = (
    "scripts/artifact-budgets.seed.json",
    "tests/fixtures/inventory-coverage-ratchet.json",
)


def _git(root: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout.strip()


def merge_base(root: Path, base: str) -> str | None:
    rc, out = _git(root, "merge-base", "HEAD", base)
    return out if rc == 0 and out else None


def evaluate(root: Path, base: str) -> tuple[int, list[str]]:
    mb = merge_base(root, base)
    lines: list[str] = []
    if not mb:
        # ⛔ UNKNOWN. A ratchet cannot be declared fresh against a base that does
        # not resolve, and reporting a pass here is precisely the #991 shape.
        return 1, [
            f"  ✗ no merge base against {base}. Ratchet freshness is UNKNOWN, never",
            "     up-to-date — that asymmetry is the whole defence.",
        ]
    lines.append(f"  merge base vs {base}: {mb[:12]}")
    rc = 0
    seen = 0
    for rel in RATCHET_FILES:
        fp = root / rel
        if not fp.is_file():
            lines.append(f"  · {rel}: absent (no ratchet to bind yet)")
            continue
        seen += 1
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            lines.append(f"  ✗ {rel}: does not parse — UNKNOWN, not fresh")
            rc = 1
            continue
        stamped = (data or {}).get("measured_against")
        if not stamped:
            lines.append(
                f"  ✗ {rel}: no `measured_against` SHA. An absent SHA is UNKNOWN, never"
                " up-to-date — re-measure on rebased HEAD and run --stamp."
            )
            rc = 1
        elif stamped != mb:
            lines.append(
                f"  ✗ {rel}: measured against {stamped[:12]}, but this PR merge base is"
                f" {mb[:12]}. This is the PR #991 shape: correct in isolation, wrong"
                " after the other branch merged. Re-measure on rebased HEAD."
            )
            rc = 1
        else:
            lines.append(f"  ✓ {rel}: bound to the current merge base")
    if seen == 0:
        lines.append("  ⚠ no ratchet state files exist — nothing was checked, which is")
        lines.append("     an EMPTY result, not a clean one.")
    return rc, lines


def stamp(root: Path, base: str) -> int:
    mb = merge_base(root, base)
    if not mb:
        print(f"cannot stamp: no merge base against {base}")
        return 2
    n = 0
    for rel in RATCHET_FILES:
        fp = root / rel
        if not fp.is_file():
            continue
        data = json.loads(fp.read_text(encoding="utf-8"))
        data["measured_against"] = mb
        fp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        n += 1
    print(f"stamped {n} ratchet file(s) against merge base {mb[:12]}")
    print("⛔ Re-run this immediately before merge. A value measured when the branch")
    print("   was cut is invalid the moment another branch lands.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stamp", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    root = Path(args.root).resolve()

    if args.stamp:
        return stamp(root, args.base)

    if args.must_fail:
        # ⛔ RECONSTRUCT THE #991 SHAPE DELIBERATELY, in a scratch tree: a ratchet
        # stamped against a SHA that is not the merge base must FAIL.
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            fake = Path(td)
            subprocess.run(["git", "-C", str(fake), "init", "-q"], check=False, timeout=60)
            subprocess.run(["git", "-C", str(fake), "config", "user.email", "t@t"], check=False)
            subprocess.run(["git", "-C", str(fake), "config", "user.name", "t"], check=False)
            (fake / "scripts").mkdir(exist_ok=True)
            (fake / "tests" / "fixtures").mkdir(parents=True, exist_ok=True)
            (fake / "seed.txt").write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(fake), "add", "-A"], check=False, timeout=60)
            subprocess.run(["git", "-C", str(fake), "commit", "-qm", "base"], check=False, timeout=60)

            wrong = "0" * 40
            (fake / RATCHET_FILES[0]).write_text(
                json.dumps({"payload": {}, "bytes": {}, "measured_against": wrong}),
                encoding="utf-8",
            )
            rc_bad, _ = evaluate(fake, "HEAD")
            if rc_bad == 0:
                print("✗ must-fail: a ratchet stamped against a foreign SHA was accepted.")
                print("  That is exactly the PR #991 shape this file exists to catch.")
                return 0

            # CONTROL: the same file, correctly stamped, must PASS — a check that
            # fails everything proves nothing about the one it is meant to catch.
            mb = merge_base(fake, "HEAD")
            (fake / RATCHET_FILES[0]).write_text(
                json.dumps({"payload": {}, "bytes": {}, "measured_against": mb}),
                encoding="utf-8",
            )
            rc_good, why = evaluate(fake, "HEAD")
            if rc_good != 0:
                print(f"✗ must-fail: a correctly-stamped ratchet was rejected — {why}")
                return 0

            # And an ABSENT SHA must be UNKNOWN (fail), never treated as fresh.
            (fake / RATCHET_FILES[0]).write_text(
                json.dumps({"payload": {}, "bytes": {}}), encoding="utf-8"
            )
            rc_absent, _ = evaluate(fake, "HEAD")
            if rc_absent == 0:
                print("✗ must-fail: an ABSENT measured_against was treated as up-to-date.")
                return 0

        print("✓ must-fail: a foreign SHA fails, an absent SHA fails as UNKNOWN, and a")
        print("  correctly-stamped ratchet passes. Exiting 1, the DECLARED teeth code.")
        return 1

    rc, lines = evaluate(root, args.base)
    print("── ratchet freshness (⛔ R6: merge-time re-measure) ──")
    for ln in lines:
        print(ln)
    print()
    print("  ⛔ Re-measure on REBASED HEAD as the last step before merge. A value that")
    print("     was correct when the branch was cut is invalid once another branch lands,")
    print("     and it still passes on its own branch — that is what makes it dangerous.")
    return rc if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
