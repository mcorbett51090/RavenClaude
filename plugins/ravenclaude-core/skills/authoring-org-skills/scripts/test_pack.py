#!/usr/bin/env python3
"""Acceptance battery for pack / verify (plan Phase 4).

Run: python3 scripts/test_pack.py
     python3 scripts/test_pack.py --must-fail-zp09     # prove the extract-and-relint bites
     python3 scripts/test_pack.py --must-fail-harness  # prove the harness has teeth

⛔ THE ROUND-TRIP FIXTURE IS THE POINT OF THIS FILE (gap-delta D4). A source tree that
lints CLEAN can still ship a broken bundle — the link resolves on disk and not in the
archive. Nothing upstream of `verify` can see that, because everything upstream reads the
disk. ZP08 and ZP09 read the archive.

⛔ `verify` IS EXERCISED AGAINST AN ARCHIVE THE PACKER NEVER TOUCHED, in a fresh process,
built by `zip(1)`. A verifier that only ever sees its own packer's output is testing that
the packer is self-consistent, which it is by construction even when it is wrong.

Stdlib only. Python 3.9-safe.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packer  # noqa: E402
from orgskill import load_rules  # noqa: E402

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RULES = os.path.join(_HERE, "schemas", "org-skill-rules.json")
_CLI = os.path.join(_HERE, "scripts", "orgskill.py")
_EVIDENCE = os.path.join(_HERE, "reference", "platform-constraints.md")

GOOD_SKILL = """---
name: processing-invoices
description: Extracts totals and line items from supplier invoices. Use when the user \
asks to read an invoice or reconcile a bill.
---

# processing-invoices

Read the invoice, extract the totals, and reconcile against the bill.
See [the field guide](reference/fields.md).
"""


def _tree(tmp: str, name: str = "processing-invoices", with_ref: bool = True) -> str:
    d = os.path.join(tmp, name)
    os.makedirs(os.path.join(d, "reference"), exist_ok=True)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        # FM09 requires name == directory name, so the fixture must substitute it.
        # Not doing so made the round-trip fixture fail on FM09 — i.e. it would have
        # "passed" for the wrong reason, which is what its precondition assertion is
        # there to catch, and did.
        fh.write(GOOD_SKILL.replace("processing-invoices", name))
    if with_ref:
        with open(os.path.join(d, "reference", "fields.md"), "w", encoding="utf-8") as fh:
            fh.write("# Fields\n\ntotal, subtotal, tax.\n")
    return d


def wrap_no_skill(tmp: str) -> str:
    """An archive with no SKILL.md under any casing — ZP01 must still fire."""
    p = os.path.join(tmp, "noskill.zip")
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("processing-invoices/README.md", "# nothing here\n")
    return p


def main(argv: list[str]) -> int:
    must_fail_zp09 = "--must-fail-zp09" in argv
    must_fail_harness = "--must-fail-harness" in argv

    rules_path = os.path.join(tempfile.mkdtemp(), "gone.json") if must_fail_harness else _RULES
    try:
        table = load_rules(rules_path)
    except Exception as exc:  # noqa: BLE001
        print("HARNESS ERROR: cannot load the rule table: %s" % exc)
        print("\nsuite: RED (harness could not run — this is NOT a pass)")
        return 0 if must_fail_harness else 1

    if must_fail_zp09:
        # Neuter the extract-and-relint clause. The round-trip fixture MUST redden,
        # or that assertion is decoration.
        _orig = packer.verify

        def _blind(archive_path, tbl, zp02_evidence=None, markers=None):
            f, n = _orig(archive_path, tbl, zp02_evidence, markers)
            return [x for x in f if x["rule_id"] not in ("ZP08", "ZP09")], n
        packer.verify = _blind

    ok = 0
    bad: list[str] = []

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        if cond:
            ok += 1
            print("  OK    %s" % label)
        else:
            bad.append(label)
            print("  FAIL  %s%s" % (label, ("  — " + str(detail)) if detail else ""))

    def ids(findings):
        return {f["rule_id"] for f in findings}

    tmp = tempfile.mkdtemp(prefix="orgskill-pack-")
    try:
        # ── a clean tree packs and verifies ──────────────────────────────────
        src = _tree(tmp)
        good_zip = os.path.join(tmp, "good.zip")
        res = packer.pack(src, good_zip, table, [], layout="A")
        check("pack writes an archive from a clean tree", os.path.isfile(good_zip))
        check("pack roots every entry under <name>/",
              all(e.startswith("processing-invoices/") for e in res["entries"]),
              "entries=%s" % res["entries"][:4])
        f, notes = packer.verify(good_zip, table, _EVIDENCE, [])
        check("verify passes a well-formed archive (no FAIL)",
              not [x for x in f if x["tier"] == "fail"],
              "findings=%s" % [(x["rule_id"], x["message"][:50]) for x in f])
        check("verify notes that ZP02 is unsettled rather than guessing",
              any("unsettled" in n for n in notes), "notes=%s" % notes)

        # ── AT5: pack refuses on a live FAIL, and NAMES the rule ─────────────
        seeded = [{"rule_id": "R2", "tier": "fail", "span": "SKILL.md:1", "message": "x"}]
        try:
            packer.pack(src, os.path.join(tmp, "nope.zip"), table, seeded)
            check("pack refuses while a FAIL finding is live", False, "it packed anyway")
        except packer.PackRefused as exc:
            check("pack refuses while a FAIL finding is live", True)
            check("        …and the refusal names the rule id", "R2" in str(exc), str(exc))
        check("        …and no archive was written", not os.path.exists(os.path.join(tmp, "nope.zip")))

        # ── AT1: five seeded malformed archives, each by its own rule id ─────
        # 1. wrapper directory  2. bare SKILL.md at root  3. Finder zip
        # 4. ../ member         5. symlink member
        wrap = os.path.join(tmp, "wrapper.zip")
        with zipfile.ZipFile(wrap, "w") as zf:
            zf.writestr("wrapper/processing-invoices/SKILL.md", GOOD_SKILL)
            zf.writestr("README.txt", "stray")
        f, _ = packer.verify(wrap, table, _EVIDENCE, [])
        check("malformed 1/5 — wrapper dir + stray root entry caught by ZP05",
              "ZP05" in ids(f), "ids=%s" % ids(f))

        flat = os.path.join(tmp, "flat.zip")
        with zipfile.ZipFile(flat, "w") as zf:
            zf.writestr("SKILL.md", GOOD_SKILL)
            zf.writestr("reference/fields.md", "# Fields\n")
        f, notes = packer.verify(flat, table, _EVIDENCE, [])
        check("malformed 2/5 — bare SKILL.md at root is NOT a FAIL while ZP02 is unsettled",
              not [x for x in f if x["rule_id"] == "ZP02" and x["tier"] == "fail"],
              "ZP02 blocked on an unsettled question: %s" % ids(f))
        check("        …and ZP05 does NOT hard-fail a layout-B archive (SKILL.md + "
              "reference/ are separate top-level entries there BY DEFINITION)",
              "ZP05" not in ids(f), "ids=%s" % ids(f))

        # ── ZP05 must not contradict Layout B, which `pack(..., layout="B")` ITSELF
        # produces. Regression fixture: ZP05 used to require exactly one top-level zip
        # entry unconditionally, so this exact archive — built by the packer's own
        # documented B path — hard-failed its own verifier. ZP05 is the Layout-A
        # invariant only; it must gate on the observed layout the same way ZP02 does.
        src_b = _tree(tmp, "reviewing-timesheets", with_ref=True)
        layout_b_zip = os.path.join(tmp, "layout-b.zip")
        res_b = packer.pack(src_b, layout_b_zip, table, [], layout="B")
        check("pack(layout=\"B\") writes SKILL.md and reference/ as SEPARATE top-level "
              "entries (the shape ZP05 must accept)",
              sorted(res_b["entries"]) == ["SKILL.md", "reference/fields.md"],
              "entries=%s" % res_b["entries"])
        f, _ = packer.verify(layout_b_zip, table, _EVIDENCE, [])
        check("verify(pack(..., layout=\"B\")) has NO fail findings at all",
              not [x for x in f if x["tier"] == "fail"],
              "a layout-B archive the packer itself produced was hard-rejected: %s"
              % [(x["rule_id"], x["tier"]) for x in f])
        check("        …specifically, ZP05 does not fire on it",
              "ZP05" not in ids(f), "ids=%s" % ids(f))

        finder = os.path.join(tmp, "finder.zip")
        with zipfile.ZipFile(finder, "w") as zf:
            zf.writestr("processing-invoices/SKILL.md", GOOD_SKILL)
            zf.writestr("processing-invoices/reference/fields.md", "# Fields\n")
            zf.writestr("__MACOSX/._SKILL.md", "resource fork")
            zf.writestr("processing-invoices/.DS_Store", "\x00\x01")
        f, _ = packer.verify(finder, table, _EVIDENCE, [])
        check("malformed 3/5 — Finder artifacts caught by ZP07", "ZP07" in ids(f),
              "ids=%s" % ids(f))

        trav = os.path.join(tmp, "traverse.zip")
        with zipfile.ZipFile(trav, "w") as zf:
            zf.writestr("processing-invoices/SKILL.md", GOOD_SKILL)
            zf.writestr("processing-invoices/../escape.md", "outside")
        f, _ = packer.verify(trav, table, _EVIDENCE, [])
        check("malformed 4/5 — ../ member caught by ZP03", "ZP03" in ids(f), "ids=%s" % ids(f))
        check("        …and verify did NOT extract an unsafe archive",
              any("extraction skipped" in n for n in packer.verify(trav, table, _EVIDENCE, [])[1]))

        sym = os.path.join(tmp, "symlink.zip")
        with zipfile.ZipFile(sym, "w") as zf:
            zf.writestr("processing-invoices/SKILL.md", GOOD_SKILL)
            info = zipfile.ZipInfo("processing-invoices/link.md")
            info.external_attr = (0o120777 << 16)      # S_IFLNK | 0777
            zf.writestr(info, "../../../etc/passwd")
        f, _ = packer.verify(sym, table, _EVIDENCE, [])
        check("malformed 5/5 — symlink member caught by ZP03", "ZP03" in ids(f), "ids=%s" % ids(f))

        # ── AT2: THE ROUND-TRIP — source lints clean, archive is missing the file ──
        src2 = _tree(tmp, "reconciling-bills", with_ref=True)
        broken = os.path.join(tmp, "broken.zip")
        with zipfile.ZipFile(broken, "w") as zf:
            # Everything except reference/fields.md — the link resolves on DISK.
            zf.writestr("reconciling-bills/SKILL.md",
                        GOOD_SKILL.replace("processing-invoices", "reconciling-bills"))
        import lint_rules
        disk_f, disk_amb = lint_rules.lint_skill(src2, table, [])
        check("round-trip precondition: the SOURCE tree has no FAIL",
              not [x for x in disk_f if x["tier"] == "fail"] and not disk_amb,
              "the fixture proves nothing if the source is already broken: %s"
              % [(x["rule_id"], x["tier"]) for x in disk_f])
        f, _ = packer.verify(broken, table, _EVIDENCE, [])
        check("round-trip: clean source + archive missing a bundled ref -> ZP08/ZP09",
              bool({"ZP08", "ZP09"} & ids(f)),
              "the archive-only defect was invisible: ids=%s" % ids(f))

        # ── ZP04: the report must never travel ───────────────────────────────
        src3 = _tree(tmp, "auditing-permissions")
        with open(os.path.join(src3, "orgskill-report.json"), "w", encoding="utf-8") as fh:
            fh.write('{"fail_count": 0}')
        rep_zip = os.path.join(tmp, "withreport.zip")
        packer.pack(src3, rep_zip, table, [], layout="A")
        with zipfile.ZipFile(rep_zip) as zf:
            check("pack excludes the validation report by construction",
                  not any(os.path.basename(n) in packer.REPORT_NAMES for n in zf.namelist()),
                  zf.namelist())
        planted = os.path.join(tmp, "planted.zip")
        with zipfile.ZipFile(planted, "w") as zf:
            zf.writestr("auditing-permissions/SKILL.md",
                        GOOD_SKILL.replace("processing-invoices", "auditing-permissions"))
            zf.writestr("auditing-permissions/reference/fields.md", "# Fields\n")
            zf.writestr("auditing-permissions/orgskill-report.json", '{"fail_count": 0}')
        f, _ = packer.verify(planted, table, _EVIDENCE, [])
        check("verify catches a report planted into the archive (ZP04)", "ZP04" in ids(f),
              "ids=%s" % ids(f))

        # ── ZP10: filename case is a WARN, because the vendor contradicts itself ──
        # ⛔ This fixture is a regression record. verify() used to hard-REJECT an archive
        # whose SKILL.md was spelled the way Anthropic's own worked example spells it
        # (article 12512198 writes lowercase throughout and never the uppercase form),
        # reporting "contains 0 SKILL.md entries" on a perfectly good bundle. Rejecting on
        # a point where the vendor disagrees with itself is not ground truth.
        lower = os.path.join(tmp, "lowercase.zip")
        with zipfile.ZipFile(lower, "w") as zf:
            zf.writestr("processing-invoices/skill.md", GOOD_SKILL)
            zf.writestr("processing-invoices/reference/fields.md", "# Fields\n")
        f, _ = packer.verify(lower, table, _EVIDENCE, [])
        check("ZP10 lowercase skill.md is a WARN, not a FAIL",
              not [x for x in f if x["tier"] == "fail"] and "ZP10" in ids(f),
              [(x["rule_id"], x["tier"]) for x in f])
        upper = os.path.join(tmp, "uppercase.zip")
        with zipfile.ZipFile(upper, "w") as zf:
            zf.writestr("processing-invoices/SKILL.md", GOOD_SKILL)
            zf.writestr("processing-invoices/reference/fields.md", "# Fields\n")
        f, _ = packer.verify(upper, table, _EVIDENCE, [])
        check("        …and canonical SKILL.md raises no ZP10 at all", "ZP10" not in ids(f),
              "a warn that fires on the correct spelling is noise")
        check("        …and ZP01 still catches a genuinely absent SKILL.md",
              "ZP01" in ids(packer.verify(wrap_no_skill(tmp), table, _EVIDENCE, [])[0]),
              "case-insensitivity must not blind the presence check")

        # ── AT3: verify in a FRESH PROCESS against a zip(1)-built archive ────
        if shutil.which("zip") is None:
            check("AT3 fresh-process verify against zip(1) — SKIPPED (no zip binary)",
                  False, "a skip is not a pass; install zip or run on a host that has it")
        else:
            _tree(tmp, "summarizing-meetings")   # side effect: the dir zip(1) archives
            ext = os.path.join(tmp, "external.zip")
            r = subprocess.run(["zip", "-q", "-r", ext, "summarizing-meetings"],
                               cwd=tmp, capture_output=True, text=True)
            check("zip(1) built an archive the packer never touched",
                  r.returncode == 0 and os.path.isfile(ext), r.stderr[:120])
            proc = subprocess.run([sys.executable, _CLI, "verify", ext],
                                  capture_output=True, text=True)
            check("AT3 fresh-process verify accepts a zip(1) archive",
                  proc.returncode == 0,
                  "rc=%s out=%s" % (proc.returncode, (proc.stdout + proc.stderr)[:200]))
            # …and the same fresh process rejects a bad one, so acceptance means something.
            proc = subprocess.run([sys.executable, _CLI, "verify", finder],
                                  capture_output=True, text=True)
            check("        …and rejects the Finder archive (exit 2)",
                  proc.returncode == 2 and "ZP07" in proc.stdout,
                  "rc=%s out=%s" % (proc.returncode, proc.stdout[:160]))

        # ── AT4: both probe fixtures exist, and the report names their paths ─
        fx = os.path.join(tmp, "fixtures")
        paths = packer.write_probe_fixtures(fx)
        check("AT4 both zip-root probe fixtures are written",
              len(paths) == 2 and all(os.path.isfile(p) for p in paths), paths)
        roots = []
        for p in paths:
            with zipfile.ZipFile(p) as zf:
                roots.append(sorted(zf.namelist()))
        check("        …and they differ ONLY in the root layout",
              roots[0] == ["zip-root-probe/SKILL.md"] and roots[1] == ["SKILL.md"],
              "a probe that changes two variables settles nothing: %s" % roots)
        proc = subprocess.run([sys.executable, _CLI, "fixtures", "--out",
                               os.path.join(tmp, "fx2")], capture_output=True, text=True)
        check("        …and the CLI names their paths for the owner's upload check",
              proc.returncode == 0 and "rootA-folder.zip" in proc.stdout
              and "rootB-flat.zip" in proc.stdout and "platform-constraints.md" in proc.stdout,
              proc.stdout[:200])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── ZP02's tier is derived from the evidence file, not hand-set ──────────
    check("ZP02 tier is WARN while the evidence file records no settlement",
          packer.derive_zp02_tier(_EVIDENCE) == ("warn", None),
          str(packer.derive_zp02_tier(_EVIDENCE)))
    check("ZP02 tier is derived, not read from the rule table",
          "tier_derivation" in {r["id"]: r for r in table["rules"]}["ZP02"])
    d = tempfile.mkdtemp()
    settled = os.path.join(d, "e.md")
    with open(settled, "w", encoding="utf-8") as fh:
        fh.write("settled: yes\naccepted_layout: B\n")
    check("        …and a settled file promotes it to FAIL with the layout",
          packer.derive_zp02_tier(settled) == ("fail", "B"))
    with open(settled, "w", encoding="utf-8") as fh:
        fh.write("settled: yes\n")
    check("        …while a half-filled record does NOT promote it",
          packer.derive_zp02_tier(settled) == ("warn", None),
          "settled:yes with no accepted_layout is not a settlement")

    # ── research vs upload-verified: two evidences, never collapsed ─────────
    # ⛔ The case that matters is the LAST one. If research could outrank an observed
    # upload, a doc-derived conclusion would start blocking real archives — the
    # confident-inference-from-a-true-observation failure, wired into a linter.
    for label, body, want in (
        ("nothing recorded", "settled: no\n", ("A", "fallback")),
        ("research A", "settled: no\nresearch_indicates: A\nresearch_confidence: moderate\n",
         ("A", "research")),
        ("research B", "settled: no\nresearch_indicates: B\nresearch_confidence: weak\n",
         ("B", "research")),
        ("research unresolved", "settled: no\nresearch_indicates: unresolved\n", ("A", "fallback")),
        ("upload OUTRANKS research",
         "settled: yes\naccepted_layout: B\nresearch_indicates: A\n", ("B", "upload-verified")),
    ):
        ep = os.path.join(d, "ev.md")
        with open(ep, "w", encoding="utf-8") as fh:
            fh.write(body)
        got = packer.derive_default_layout(ep)[:2]
        check("default layout: %-24s -> %s" % (label, want[0] + "/" + want[1]), got == want, str(got))
    check("        …and research NEVER promotes ZP02's tier",
          packer.derive_zp02_tier(ep) == ("fail", "B")
          and packer.derive_zp02_tier(os.path.join(d, "ev.md")) == ("fail", "B"),
          "upload set this one; the research-only cases above must stay warn")
    with open(os.path.join(d, "r.md"), "w", encoding="utf-8") as fh:
        fh.write("settled: no\nresearch_indicates: B\nresearch_confidence: strong\n")
    check("        …even at research_confidence: strong",
          packer.derive_zp02_tier(os.path.join(d, "r.md")) == ("warn", None)
          and packer.derive_default_layout(os.path.join(d, "r.md"))[0] == "B",
          "strong research moved the DEFAULT to B but must leave the TIER at warn")

    total = ok + len(bad)
    print("\norgskill pack/verify suite: %s (%d/%d)"
          % ("PASS" if not bad else "FAIL", ok, total))
    if bad:
        print("failed:")
        for b in bad:
            print("   -", b)
    if must_fail_zp09:
        print("\n--must-fail-zp09: suite went %s (RED is the pass)"
              % ("RED" if bad else "GREEN"))
        return 0 if bad else 1
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
