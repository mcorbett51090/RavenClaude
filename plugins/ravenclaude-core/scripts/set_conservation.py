#!/usr/bin/env python3
"""set_conservation.py — the Set-Conservation Primitive (SCP).

THE SHARED PRIMITIVE, AND WHY IT IS ONE FILE
────────────────────────────────────────────
Two FORGE runs need the same thing: emit a set of ids in a form a later reader
can *re-derive and disagree with*, then compare a CLAIMED set against an ACTUAL
one and return a verdict that cannot quietly be "fine".

  * `task-ledger`          — `set_kind="open_items"`, the ledger's open set.
  * `verify-before-assert` — `set_kind="causes"`, that run's enumerated causes.

This module is the SSOT for both (plan.md §14.1, ruling M). The second caller is
a CALLER, never a second implementation. To add a third set kind, add ONE row to
`SET_KINDS` below — never a parallel module, and never a caller-supplied id
pattern, because a pattern that lives in the caller cannot be re-checked by
`verify` and the block stops being self-describing.

THE THREE-VALUED VERDICT — the whole point (ruling A)
─────────────────────────────────────────────────────
`diff` returns PASS / FAIL / **UNKNOWN**, and UNKNOWN BLOCKS with the same force
as FAIL. The defect this exists to prevent is measured and specific: with an
EMPTY actual set, `A \\ C` and `C \\ A` are both empty and a two-valued gate
reports GREEN — inert exactly when it is most needed. So `diff` REQUIRES a
positive control (`--parsed-records N`, the count of records the caller actually
read to build the actual set). Absent or zero => UNKNOWN. An empty result needs a
positive control or it is a broken probe, not a pass.

DIGEST
──────
    digest = "sha256:" + sha256(f"{scp_version}\\n{set_kind}\\n" + "\\n".join(ids))[:12]

`ids` are sorted and deduped BEFORE the digest, so the digest is stable under
input reordering — asserted by the self-test, not assumed.

EXIT CODES (this tool's own convention — check every tool's, they differ)
────────────────────────────────────────────────────────────────────────
    build        0 ok · 1 invalid input
    verify       0 valid · 1 an invariant is broken (FAIL) · 2 unreadable (UNKNOWN)
    diff         0 PASS · 1 FAIL · 2 UNKNOWN
    --self-test  0 pass · 1 fail
    --must-fail  0 when the TEETH BIT (a planted defect was caught) · 1 otherwise

⛔ `--must-fail` exits **0** on success here, matching `premise-gate.py`.
`scripts/sync-plugin-versions.py` uses the OPPOSITE convention (it expects 2).
There is no repo-wide convention; a caller must read the tool it is calling.

Usage:
    set_conservation.py build --set-kind open_items --basis 'ledger:x@abc' \\
        --id rc-0123456789ab --computed-at 2026-08-20T09:44:12.771Z
    set_conservation.py verify --block open-set.json
    set_conservation.py diff --claimed claimed.json --actual actual.json --parsed-records 42
    set_conservation.py --self-test
    set_conservation.py --must-fail
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from typing import Any, Dict, List, NamedTuple, Optional

SCP_VERSION = 1

# Volatile fields — excluded from a SEMANTIC comparison of two blocks, because a
# byte compare of a block containing `computed_at` is RED on 100% of runs forever
# (plan.md §11.3 bug A-1). The digest carries the load a byte compare cannot.
VOLATILE_FIELDS = ("computed_at", "coverage", "basis")

REQUIRED_KEYS = (
    "scp_version",
    "set_kind",
    "count",
    "ids",
    "digest",
    "basis",
    "truncated",
    "computed_at",
)
OPTIONAL_KEYS = ("coverage",)
ALLOWED_KEYS = REQUIRED_KEYS + OPTIONAL_KEYS

_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")


class SetKindSpec(NamedTuple):
    id_pattern: str
    owner: str
    description: str


# ⛔ ONE TABLE. A new set kind is a row here. A caller that needs a different id
# shape edits this row — it does not pass a pattern in, because a caller-supplied
# pattern makes `verify` unable to re-check the block on its own.
SET_KINDS: Dict[str, SetKindSpec] = {
    "open_items": SetKindSpec(
        id_pattern=r"^rc-[0-9a-f]{12}$",
        owner="task-ledger",
        description="the ledger's open item set (plan.md §8.1)",
    ),
    "causes": SetKindSpec(
        id_pattern=r"^rc-[0-9a-f]{12}$",
        owner="verify-before-assert",
        description="an enumerated cause set (plan.md §14.1, acceptance C38)",
    ),
}


class ScpError(Exception):
    """A determinate invariant violation — maps to FAIL, never to UNKNOWN."""


class ScpUnknown(Exception):
    """The block could not be read or parsed — maps to UNKNOWN, never to PASS."""


# ── build ────────────────────────────────────────────────────────────────────


def compute_digest(set_kind: str, ids: List[str], scp_version: int = SCP_VERSION) -> str:
    """Digest over the SORTED, DEDUPED id set. Stable under input reordering."""
    canonical = sorted(set(ids))
    payload = "{0}\n{1}\n{2}".format(scp_version, set_kind, "\n".join(canonical))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def build_block(
    set_kind: str,
    ids: List[str],
    basis: str,
    computed_at: str,
    coverage: Optional[Dict[str, int]] = None,
    truncated: bool = False,
) -> Dict[str, Any]:
    if set_kind not in SET_KINDS:
        raise ScpError(
            "unknown set_kind {0!r} — known: {1}".format(set_kind, ", ".join(sorted(SET_KINDS)))
        )
    if not basis:
        raise ScpError("basis is required — a set with no stated origin cannot be re-derived")
    pattern = re.compile(SET_KINDS[set_kind].id_pattern)
    bad = [i for i in ids if not isinstance(i, str) or not pattern.match(i)]
    if bad:
        raise ScpError(
            "ids do not match {0}'s pattern {1}: {2}".format(
                set_kind, SET_KINDS[set_kind].id_pattern, ", ".join(map(repr, sorted(bad)[:5]))
            )
        )
    canonical = sorted(set(ids))
    block: Dict[str, Any] = {
        "scp_version": SCP_VERSION,
        "set_kind": set_kind,
        "count": len(canonical),
        "ids": canonical,
        "digest": compute_digest(set_kind, canonical),
        "basis": basis,
        "truncated": bool(truncated),
        "computed_at": computed_at,
    }
    if coverage is not None:
        block["coverage"] = coverage
    return block


# ── verify ───────────────────────────────────────────────────────────────────


def verify_block(block: Any) -> List[str]:
    """Return the list of broken invariants. An empty list means valid."""
    problems: List[str] = []
    if not isinstance(block, dict):
        return ["block is not a JSON object"]

    unknown = sorted(set(block) - set(ALLOWED_KEYS))
    if unknown:
        problems.append("unknown key(s): {0}".format(", ".join(unknown)))
    missing = [k for k in REQUIRED_KEYS if k not in block]
    if missing:
        problems.append("missing required key(s): {0}".format(", ".join(missing)))
        return problems

    if block["scp_version"] != SCP_VERSION:
        problems.append("scp_version {0!r} != {1}".format(block["scp_version"], SCP_VERSION))

    set_kind = block["set_kind"]
    if set_kind not in SET_KINDS:
        problems.append("unknown set_kind {0!r}".format(set_kind))
        return problems

    ids = block["ids"]
    if not isinstance(ids, list) or any(not isinstance(i, str) for i in ids):
        problems.append("ids is not a list of strings")
        return problems

    pattern = re.compile(SET_KINDS[set_kind].id_pattern)
    bad = [i for i in ids if not pattern.match(i)]
    if bad:
        problems.append(
            "id(s) fail {0}: {1}".format(
                SET_KINDS[set_kind].id_pattern, ", ".join(map(repr, sorted(bad)[:5]))
            )
        )
    if ids != sorted(ids):
        problems.append("ids are not sorted lexicographically")
    if len(set(ids)) != len(ids):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        problems.append("duplicate id(s): {0}".format(", ".join(dupes[:5])))
    if block["count"] != len(ids):
        problems.append("count {0} != len(ids) {1}".format(block["count"], len(ids)))

    expected = compute_digest(set_kind, ids)
    if block["digest"] != expected:
        problems.append(
            "digest {0} does not recompute (expected {1})".format(block["digest"], expected)
        )

    if not isinstance(block["basis"], str) or not block["basis"]:
        problems.append("basis is empty — the set's origin is unstated and cannot be re-derived")
    if not isinstance(block["truncated"], bool):
        problems.append("truncated must be a boolean")
    if not isinstance(block["computed_at"], str) or not _TS_RE.match(block["computed_at"]):
        problems.append(
            "computed_at {0!r} is not an ISO-8601 instant".format(block.get("computed_at"))
        )

    cov = block.get("coverage")
    if cov is not None:
        if not isinstance(cov, dict):
            problems.append("coverage must be an object")
        else:
            for key, value in sorted(cov.items()):
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    problems.append("coverage.{0} must be a non-negative integer".format(key))
    return problems


def load_block(path: str) -> Any:
    """Read a block. Any read/parse failure is UNKNOWN — never an empty set."""
    try:
        if path == "-":
            raw = sys.stdin.read()
        else:
            with open(path, encoding="utf-8") as handle:
                raw = handle.read()
    except OSError as exc:
        raise ScpUnknown("basis_unreadable: cannot read {0}: {1}".format(path, exc))
    try:
        return json.loads(raw)
    except ValueError as exc:
        raise ScpUnknown("block_unparseable: {0}: {1}".format(path, exc))


# ── diff (the three-valued gate) ─────────────────────────────────────────────


class Verdict(NamedTuple):
    verdict: str  # PASS | FAIL | UNKNOWN
    exit_code: int
    reasons: List[str]
    missing: List[str]  # in ACTUAL, absent from CLAIMED — under-enumeration
    extra: List[str]  # in CLAIMED, absent from ACTUAL — over-enumeration

    def as_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict,
            "exit_code": self.exit_code,
            "reasons": list(self.reasons),
            "missing": list(self.missing),
            "extra": list(self.extra),
        }


def diff_blocks(claimed: Any, actual: Any, parsed_records: Optional[int]) -> Verdict:
    """Three-valued conservation check.

    `parsed_records` is the POSITIVE CONTROL: how many records the caller
    actually parsed to construct `actual`. `None` (never supplied) or `0` =>
    UNKNOWN. Without it, an empty ledger and a perfectly-conserved one are the
    same two empty sets, and the gate is inert exactly when it matters.
    """
    reasons: List[str] = []

    if parsed_records is None:
        return Verdict(
            "UNKNOWN",
            2,
            [
                "no_positive_control: --parsed-records was not supplied, so an empty actual "
                "set is indistinguishable from an unread basis"
            ],
            [],
            [],
        )
    if parsed_records < 0:
        return Verdict("UNKNOWN", 2, ["no_positive_control: --parsed-records is negative"], [], [])
    if parsed_records == 0:
        return Verdict(
            "UNKNOWN",
            2,
            ["ledger_empty: 0 records parsed for the actual set — UNKNOWN, never '0 open'"],
            [],
            [],
        )

    claimed_problems = verify_block(claimed)
    actual_problems = verify_block(actual)
    if actual_problems:
        reasons += ["actual block invalid: " + p for p in actual_problems]
    if claimed_problems:
        reasons += ["claimed block invalid: " + p for p in claimed_problems]
    if reasons:
        return Verdict("FAIL", 1, reasons, [], [])

    if claimed["set_kind"] != actual["set_kind"]:
        return Verdict(
            "FAIL",
            1,
            [
                "set_kind mismatch: claimed {0!r} vs actual {1!r}".format(
                    claimed["set_kind"], actual["set_kind"]
                )
            ],
            [],
            [],
        )

    claimed_ids = set(claimed["ids"])
    actual_ids = set(actual["ids"])
    missing = sorted(actual_ids - claimed_ids)
    extra = sorted(claimed_ids - actual_ids)

    if missing:
        reasons.append(
            "under-enumeration: {0} id(s) present in the actual set and absent from the "
            "claim: {1}".format(len(missing), ", ".join(missing))
        )
    if extra:
        reasons.append(
            "over-enumeration: {0} claimed id(s) the basis does not contain (fabricated or "
            "stale — both unexplained): {1}".format(len(extra), ", ".join(extra))
        )
    if not missing and not extra and claimed["digest"] != actual["digest"]:
        reasons.append(
            "digest mismatch while the id sets agree — one of the blocks is corrupt "
            "(claimed {0}, actual {1})".format(claimed["digest"], actual["digest"])
        )

    if reasons:
        return Verdict("FAIL", 1, reasons, missing, extra)
    return Verdict(
        "PASS",
        0,
        [
            "conserved: {0} id(s), digest {1}, {2} record(s) parsed".format(
                actual["count"], actual["digest"], parsed_records
            )
        ],
        [],
        [],
    )


def semantic_equal(left: Any, right: Any) -> bool:
    """Compare two blocks with the volatile fields excluded (bug A-1's fix)."""

    def strip(block: Any) -> Any:
        if not isinstance(block, dict):
            return block
        return {k: v for k, v in block.items() if k not in VOLATILE_FIELDS}

    return strip(left) == strip(right)


# ── self-test ────────────────────────────────────────────────────────────────

_IDS = ["rc-1f0c9a3b2d41", "rc-77b04e19a8c2", "rc-a3f8c1d2e4b7", "rc-e40d2288ff10"]
_NOW = "2026-08-20T09:44:12.771Z"


def _self_test(broken: bool = False) -> int:
    """Prove every finding class DISTINGUISHES.

    `broken=True` neuters the digest function so it agrees with everything; the
    run must then FAIL. That is exactly what `--must-fail` asserts.
    """
    global compute_digest
    original = compute_digest
    if broken:
        def compute_digest(set_kind, ids, scp_version=SCP_VERSION):  # type: ignore[misc]
            return "sha256:000000000000"

    failures: List[str] = []

    def check(label: str, condition: bool) -> None:
        if condition:
            print("  ok   {0}".format(label))
        else:
            print("  FAIL {0}".format(label))
            failures.append(label)

    try:
        good = build_block("open_items", _IDS, "ledger:test@abcdef", _NOW)
        check("build produces a block that verifies", verify_block(good) == [])
        check("count == len(ids)", good["count"] == len(_IDS))
        check("ids are sorted", good["ids"] == sorted(_IDS))

        # Digest stability under input reordering — asserted, not assumed.
        shuffled = build_block("open_items", list(reversed(_IDS)), "ledger:test@abcdef", _NOW)
        check("digest is stable under input reordering", shuffled["digest"] == good["digest"])
        check(
            "a shuffled build is byte-identical",
            json.dumps(shuffled, sort_keys=True) == json.dumps(good, sort_keys=True),
        )

        # C38 — the SAME code path serves verify-before-assert.
        causes = build_block("causes", _IDS, "cause-triage:scope-x@abcdef", _NOW)
        check("set_kind='causes' returns the same shape (C38)", verify_block(causes) == [])
        check("set_kind is load-bearing in the digest", causes["digest"] != good["digest"])

        # FOUR SEPARATE NEGATIVE CONTROLS (plan.md A2.8).
        n1 = dict(good, count=3)
        check("neg 1/4: count != len(ids) is caught", any("count" in p for p in verify_block(n1)))
        n2 = dict(good, ids=good["ids"] + [good["ids"][0]], count=len(good["ids"]) + 1)
        check("neg 2/4: a duplicate id is caught", any("duplicate" in p for p in verify_block(n2)))
        n3 = dict(good, ids=list(reversed(good["ids"])))
        check("neg 3/4: unsorted ids are caught", any("sorted" in p for p in verify_block(n3)))
        n4 = dict(good, digest="sha256:deadbeefcafe")
        check("neg 4/4: a mutated digest is caught", any("recompute" in p for p in verify_block(n4)))

        n5 = dict(good, confidence=0.9)
        check(
            "an unknown key (e.g. the REFUSED `confidence`) is rejected",
            any("unknown key" in p for p in verify_block(n5)),
        )

        # ── the three-valued gate ────────────────────────────────────────────
        empty = build_block("open_items", [], "ledger:test@abcdef", _NOW)
        v = diff_blocks(empty, empty, parsed_records=0)
        check(
            "EMPTY basis (0 records parsed) => UNKNOWN, exit 2, NEVER pass",
            v.verdict == "UNKNOWN" and v.exit_code == 2,
        )
        v = diff_blocks(empty, empty, parsed_records=None)
        check(
            "no positive control at all => UNKNOWN, exit 2",
            v.verdict == "UNKNOWN" and v.exit_code == 2,
        )
        v = diff_blocks(empty, empty, parsed_records=7)
        check(
            "a genuinely empty set WITH a positive control => PASS",
            v.verdict == "PASS" and v.exit_code == 0,
        )

        v = diff_blocks(good, good, parsed_records=12)
        check("conserved sets => PASS, exit 0", v.verdict == "PASS" and v.exit_code == 0)

        short = build_block("open_items", _IDS[:3], "ledger:test@abcdef", _NOW)
        v = diff_blocks(short, good, parsed_records=12)
        check(
            "under-enumeration => FAIL, exit 1, names the missing id",
            v.verdict == "FAIL" and v.exit_code == 1 and v.missing == [_IDS[3]],
        )

        longer = build_block("open_items", _IDS + ["rc-ffffffffffff"], "ledger:test@abcdef", _NOW)
        v = diff_blocks(longer, good, parsed_records=12)
        check(
            "over-enumeration => FAIL, exit 1, names the extra id",
            v.verdict == "FAIL" and v.exit_code == 1 and v.extra == ["rc-ffffffffffff"],
        )

        corrupt = dict(good, digest="sha256:000000000001")
        v = diff_blocks(corrupt, good, parsed_records=12)
        check(
            "a corrupt claimed block => FAIL, never UNKNOWN",
            v.verdict == "FAIL" and v.exit_code == 1,
        )

        v = diff_blocks(good, build_block("causes", _IDS, "b:1", _NOW), parsed_records=12)
        check("set_kind mismatch => FAIL", v.verdict == "FAIL")

        # Semantic compare excludes the volatile fields (bug A-1), BOTH directions.
        later = build_block("open_items", _IDS, "ledger:test@fedcba", "2026-08-20T09:49:12.771Z")
        check("semantic_equal ignores computed_at/basis (A-1)", semantic_equal(good, later))
        mutated = build_block(
            "open_items", _IDS[:3] + ["rc-000000000000"], "ledger:test@abcdef", _NOW
        )
        check(
            "semantic_equal still catches a mutated id (A-1 negative control)",
            not semantic_equal(good, mutated),
        )

        # A sequential id is refused at build time (plan.md §4.3, claims 13/2).
        try:
            build_block("open_items", ["T001"], "b:1", _NOW)
            check("a sequential id (T001) is refused", False)
        except ScpError:
            check("a sequential id (T001) is refused", True)
    finally:
        compute_digest = original

    print()
    if failures:
        print("set_conservation self-test FAILED ({0})".format(len(failures)))
        return 1
    print("set_conservation self-test PASS")
    return 0


def _must_fail() -> int:
    """Plant a defect (a digest function that agrees with everything) and assert
    the self-test CATCHES it. Exits 0 only when the teeth bite."""
    print("-- --must-fail: the self-test below is MEANT to redden --")
    rc = _self_test(broken=True)
    if rc == 0:
        print("TEETH FAILED: a neutered digest still passed the self-test", file=sys.stderr)
        return 1
    print("teeth ok: the planted digest defect was caught (self-test exited {0})".format(rc))
    return 0


# ── CLI ──────────────────────────────────────────────────────────────────────


def _parse_coverage(pairs: List[str]) -> Optional[Dict[str, int]]:
    if not pairs:
        return None
    coverage: Dict[str, int] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ScpError("--coverage expects key=int, got {0!r}".format(pair))
        key, _, value = pair.partition("=")
        try:
            coverage[key] = int(value)
        except ValueError:
            raise ScpError("--coverage value for {0!r} is not an integer".format(key))
    return coverage


def _collect_ids(args: argparse.Namespace) -> List[str]:
    ids: List[str] = list(args.id or [])
    if args.ids_file:
        try:
            with open(args.ids_file, encoding="utf-8") as handle:
                ids += [line.strip() for line in handle if line.strip()]
        except OSError as exc:
            raise ScpUnknown("ids_file unreadable: {0}".format(exc))
    return ids


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="set_conservation.py",
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "exit codes — build: 0 ok/1 invalid · verify: 0 valid/1 FAIL/2 UNKNOWN · "
            "diff: 0 PASS/1 FAIL/2 UNKNOWN · --must-fail: 0 when the teeth BIT "
            "(premise-gate.py's convention, NOT sync-plugin-versions.py's)"
        ),
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--must-fail",
        action="store_true",
        help="plant a defect and assert the self-test catches it; exits 0 only when the "
        "teeth bite",
    )
    sub = parser.add_subparsers(dest="command")

    p_build = sub.add_parser("build", help="emit an SCP block")
    p_build.add_argument("--set-kind", required=True, choices=sorted(SET_KINDS))
    p_build.add_argument("--basis", required=True)
    p_build.add_argument("--id", action="append", default=[])
    p_build.add_argument("--ids-file")
    p_build.add_argument("--coverage", action="append", default=[], metavar="KEY=INT")
    p_build.add_argument("--truncated", action="store_true")
    p_build.add_argument(
        "--computed-at",
        required=True,
        help="ISO-8601 instant; REQUIRED and explicit so the block is a pure function of "
        "its inputs (no hidden wall-clock input)",
    )
    p_build.add_argument("--out")

    p_verify = sub.add_parser("verify", help="check an SCP block's invariants")
    p_verify.add_argument("--block", required=True, help="path, or - for stdin")

    p_diff = sub.add_parser("diff", help="three-valued conservation check")
    p_diff.add_argument("--claimed", required=True)
    p_diff.add_argument("--actual", required=True)
    p_diff.add_argument(
        "--parsed-records",
        type=int,
        default=None,
        help="POSITIVE CONTROL: records parsed to build the actual set. Absent or 0 => "
        "UNKNOWN (exit 2).",
    )
    p_diff.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.must_fail:
        return _must_fail()
    if args.self_test:
        return _self_test()

    try:
        if args.command == "build":
            block = build_block(
                args.set_kind,
                _collect_ids(args),
                args.basis,
                args.computed_at,
                coverage=_parse_coverage(args.coverage),
                truncated=args.truncated,
            )
            text = json.dumps(block, indent=2, sort_keys=True) + "\n"
            if args.out:
                with open(args.out, "w", encoding="utf-8") as handle:
                    handle.write(text)
            else:
                sys.stdout.write(text)
            return 0

        if args.command == "verify":
            problems = verify_block(load_block(args.block))
            if problems:
                print("SCP INVALID ({0} problem(s)):".format(len(problems)), file=sys.stderr)
                for problem in problems:
                    print("  - " + problem, file=sys.stderr)
                return 1
            print("SCP valid")
            return 0

        if args.command == "diff":
            claimed = load_block(args.claimed)
            actual = load_block(args.actual)
            verdict = diff_blocks(claimed, actual, args.parsed_records)
            if args.json:
                print(json.dumps(verdict.as_dict(), indent=2, sort_keys=True))
            else:
                stream = sys.stdout if verdict.verdict == "PASS" else sys.stderr
                print("{0} (exit {1})".format(verdict.verdict, verdict.exit_code), file=stream)
                for reason in verdict.reasons:
                    print("  - " + reason, file=stream)
                if verdict.verdict == "UNKNOWN":
                    print("  UNKNOWN BLOCKS. It is never downgraded to PASS.", file=stream)
            return verdict.exit_code
    except ScpUnknown as exc:
        print("UNKNOWN (exit 2): {0}".format(exc), file=sys.stderr)
        return 2
    except ScpError as exc:
        print("FAIL (exit 1): {0}".format(exc), file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
