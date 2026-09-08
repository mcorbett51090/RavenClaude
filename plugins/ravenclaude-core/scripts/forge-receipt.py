#!/usr/bin/env python3
"""forge-receipt.py — the FORGE Sága run-record recorder + completeness verifier.

Deterministic; no model judgment. Two subcommands:

  append <gate> --receipt <file.json> --run-dir <dir>
      Append ONE receipt line to <run-dir>/run-log.jsonl, immediately after the
      gate returns — NOT batched at the end of the run.

  verify --run-dir <dir> --depth <micro|quick|standard|deep>
      Assert every gate the resolved depth requires has a pass/waived receipt.

⛔ CE-1 — WHY THE TIMING MATTERS, and why this script exists at all.
Two independent review panels proposed a write-time validating recorder, both
assuming the Saga record was appended per gate. It was not: `commands/forge.md`
Step 5 was a single TERMINAL write, after every gate had already advanced. A
validator built on that timing runs AFTER every advance decision it is meant to
gate, so its "fail-closed" claim is aspirational rather than mechanical. The fix
is half prose (move the append into Step 4's gate loop) and half this script
(make the append itself refuse a lie). Neither half works alone.

⛔ CE-2 — WHY THE STORED PATH IS RELATIVE. FORGE provisions a worktree (§0.5),
so a run's artifacts can be split across the primary checkout and a worktree
with no reconciliation — confirmed live in a landed run whose G2-G8 artifacts
existed ONLY inside a worktree. If that worktree is ever pruned, an absolute
path in the ledger points at nothing and the record cannot even say what it lost.
Every artifact path is therefore rewritten RELATIVE TO --run-dir before it is
appended, so the ledger survives the run-dir being moved or a worktree being
pruned. SKILL.md §0.5's absolute-primary-checkout-path rule fixes the SPLIT at
the cause; this fixes the LEDGER's durability. Both are needed — a relative path
does not help if two receipts were written into two different directories to
begin with.

⛔ BYTES ARE RECOMPUTED FROM DISK, NEVER TRUSTED. Measured over 44 real run
directories: 25 of 73 `bytes` fields disagreed with the real file size, and 26 of
153 receipts named an artifact that does not exist on disk. A self-reported size
is the claim under audit; it cannot also be the evidence.

EXIT CODES ARE A CONTRACT (mirrors premise-gate.py's 0/1/2 exactly — reusing a
shape this repo has already hardened rather than inventing a new one):
  0  clean    — appended, or every required gate is accounted for, or disabled
  2  refused  — fail-closed: a `pass` receipt whose artifact is missing/empty, or
                a required gate with no pass/waived receipt
  1  COULD NOT RUN — malformed/absent inputs, unreadable run-dir or run-log.
     NEVER conflate with clean: "I looked and found nothing" and "I could not
     look" are indistinguishable afterward, which is exactly how a green gate
     ends up protecting nothing.

Kill switch (mirrors forge-worktree.sh's FORGE_WORKTREE / `forge_worktree: off`
shape): `FORGE_RECEIPT=off` in the env, or `forge_receipt: off` in
`.ravenclaude/comfort-posture.yaml`. Either makes both subcommands exit 0
immediately with a `"status":"disabled"` result, so a new mechanism can never
wedge a run. Absent => ON (the default).

Python 3.9 compatible (stock macOS ships 3.9.6). Stdlib only — no PyYAML.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import tempfile

# The ladder order, used to decide which gates come AFTER a short-circuit point.
GATE_ORDER = ["G0", "G1", "G2", "G3", "G3b", "G4a", "G4b", "G5", "G6", "G7", "G8"]

# SKILL.md §1's depth ladder. `deep` runs the SAME gate set as `standard` — depth
# changes cadence/checkpointing (no conflict cap, a 2nd red-team, resume), not
# WHICH gates run. Deriving it from standard rather than re-listing it keeps a
# future editor from "fixing the duplication" by inventing a deep-only gate.
DEPTH_GATES = {
    "micro": ["G0", "G6", "G7", "G8"],
    "quick": ["G0", "G1", "G2", "G3", "G3b", "G6", "G7", "G8"],
    "standard": ["G0", "G1", "G2", "G3", "G3b", "G4a", "G4b", "G5", "G6", "G7", "G8"],
}
DEPTH_GATES["deep"] = list(DEPTH_GATES["standard"])

VALID_STATUS = ("pass", "fail", "waived")

# ⛔ RED-TEAM #2 — a legitimately short-circuited run must not fail `verify`.
# A run that BLOCKs at G1 or takes a `reject` route at G7 never reaches the later
# gates BY DESIGN. A naive "does every gate in the depth ladder have a receipt?"
# check would hard-fail every such run — a false-positive denial that trains users
# to bypass `verify` rather than trust it. This repo has already recorded that
# outcome twice (srm.force-push, sce.curl-pipe-shell): an untunable guard gets
# turned off, and a guard that is off protects nothing.
SHORT_CIRCUIT_GATES = ("G1", "G7")
_REJECT_RE = re.compile(r"\b(reject|rejected|block|blocked|blocking)\b", re.I)

# Self-test teeth knob. --must-fail flips it and asserts the self-test CATCHES the
# planted defect; a self-test that still passes with the defect applied has none.
_NEUTER_ARTIFACT_CHECK = False


# -- kill switch --------------------------------------------------------------


def _posture_path(start):
    """First `.ravenclaude/comfort-posture.yaml` at or above `start`. '' if none."""
    try:
        cur = os.path.abspath(start)
    except Exception:
        return ""
    for _ in range(64):
        cand = os.path.join(cur, ".ravenclaude", "comfort-posture.yaml")
        if os.path.isfile(cand):
            return cand
        parent = os.path.dirname(cur)
        if parent == cur:
            return ""
        cur = parent
    return ""


def is_disabled(start=""):
    """True when the kill switch is engaged. Fail-safe: any read error => enabled.

    Precedence mirrors forge-worktree.sh's `_worktree_mode`:
    FORGE_RECEIPT env > comfort-posture > on.
    """
    if os.environ.get("FORGE_RECEIPT", "").strip().lower() == "off":
        return True
    roots = []
    if start:
        roots.append(start)
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if proj:
        roots.append(proj)
    roots.append(os.getcwd())
    for root in roots:
        path = _posture_path(root)
        if not path:
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                body = fh.read(65536)
        except Exception:
            continue
        # Minimal scalar read — no PyYAML. Match a top-level `forge_receipt: off`.
        if re.search(r"(?m)^[ \t]*forge_receipt:[ \t]*off[ \t]*(?:#.*)?$", body):
            return True
    return False


def _disabled_result(sub):
    return {"status": "disabled", "subcommand": sub,
            "reason": "FORGE_RECEIPT=off or forge_receipt: off"}


# -- helpers ------------------------------------------------------------------


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_artifact(artifact, run_dir):
    """Absolute filesystem path for a receipt's artifact reference."""
    if os.path.isabs(artifact):
        return os.path.normpath(artifact)
    return os.path.normpath(os.path.join(run_dir, artifact))


def _relativize(abs_path, run_dir):
    """(relative-path, escapes_run_dir). A relative path survives a move/prune."""
    try:
        rel = os.path.relpath(abs_path, run_dir)
    except Exception:
        return abs_path, True
    return rel, rel.startswith("..")


# -- append -------------------------------------------------------------------


def append(gate, receipt_path, run_dir):
    """Return (exit_code, result_dict). See the module docstring's exit contract."""
    if not gate or not str(gate).strip():
        return 1, {"error": "gate is required and must be non-empty"}
    gate = str(gate).strip()

    if not os.path.isdir(run_dir):
        return 1, {"error": "run-dir does not exist or is not a directory: %s" % run_dir}
    if not os.access(run_dir, os.W_OK):
        return 1, {"error": "run-dir is not writable: %s" % run_dir}

    try:
        with open(receipt_path, encoding="utf-8") as fh:
            rec = json.load(fh)
    except FileNotFoundError:
        return 1, {"error": "receipt not found: %s" % receipt_path}
    except (OSError, ValueError) as exc:
        return 1, {"error": "receipt unreadable/malformed: %s" % exc}
    if not isinstance(rec, dict):
        return 1, {"error": "receipt is not a JSON object"}

    rec_gate = rec.get("gate")
    if rec_gate is not None and str(rec_gate).strip() and str(rec_gate).strip() != gate:
        # The two inputs disagree about WHICH gate this is. We cannot tell which
        # is right, so this is could-not-run, never a silent pick-one.
        return 1, {"error": "gate mismatch: CLI says %r, receipt says %r" % (gate, rec_gate)}
    rec["gate"] = gate

    status = str(rec.get("status", "")).strip().lower()
    if status not in VALID_STATUS:
        return 1, {"error": "status must be one of %s (got %r)"
                            % ("|".join(VALID_STATUS), rec.get("status"))}
    rec["status"] = status

    artifact = rec.get("artifact")
    artifact = str(artifact).strip() if isinstance(artifact, str) else ""

    if status == "pass":
        # ⛔ FAIL-CLOSED. A `pass` whose artifact is missing or empty is the exact
        # defect measured in the corpus (26/153 named a nonexistent file). Warning
        # and continuing would reproduce it — the whole point is to make the
        # artifact contract's stated advance criterion real.
        if not artifact and not _NEUTER_ARTIFACT_CHECK:
            return 2, {"error": "refused: status=pass with no artifact named", "gate": gate}
        abs_path = _resolve_artifact(artifact, run_dir) if artifact else ""
        # ⛔ isfile() FIRST, and it is load-bearing — not defensive padding.
        # os.path.getsize() on a DIRECTORY returns its inode size (384, 416, ...),
        # which is > 0, so a size-only check ACCEPTS a directory as a valid
        # artifact. Found by a live smoke test against a real FORGE run dir where
        # a harness bug passed the run dir itself as the artifact: all 11 gates
        # appended "clean" with bytes 384-416 and artifact ".". A recorder that
        # accepts a directory as proof of a written artifact is the same
        # green-while-checking-nothing defect this script exists to close.
        why = ""
        if not abs_path:
            size = -1
        elif os.path.isdir(abs_path):
            size, why = -1, "a directory, not a file"
        elif not os.path.isfile(abs_path):
            size, why = -1, "missing or not a regular file"
        else:
            try:
                size = os.path.getsize(abs_path)
            except OSError:
                size = -1
        if size <= 0 and not _NEUTER_ARTIFACT_CHECK:
            if not why:
                why = "missing" if size < 0 else "empty"
            return 2, {"error": "refused: status=pass but artifact is %s: %s" % (why, artifact),
                       "gate": gate, "artifact": artifact}
        rec["bytes"] = max(size, 0)
        rec["bytes_verified"] = size > 0
        rel, escapes = _relativize(abs_path, run_dir) if abs_path else ("", False)
        rec["artifact"] = rel
        if escapes:
            rec["artifact_outside_run_dir"] = True
    else:
        # fail / waived: append as-is. No existence check — a gate that FAILED may
        # legitimately have produced nothing, and refusing to record a failure is
        # how a ledger ends up describing only the happy path.
        if artifact:
            abs_path = _resolve_artifact(artifact, run_dir)
            try:
                size = os.path.getsize(abs_path)
            except OSError:
                size = -1
            rel, escapes = _relativize(abs_path, run_dir)
            rec["artifact"] = rel
            if escapes:
                rec["artifact_outside_run_dir"] = True
            if size >= 0:
                rec["bytes"] = size
                rec["bytes_verified"] = True
            else:
                rec["bytes_verified"] = False
        else:
            rec["bytes_verified"] = False

    rec.setdefault("ts", _now())

    log = os.path.join(run_dir, "run-log.jsonl")
    try:
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    except OSError as exc:
        return 1, {"error": "could not append to run-log.jsonl: %s" % exc}

    return 0, {"status": "appended", "gate": gate, "receipt_status": status,
               "artifact": rec.get("artifact", ""), "bytes": rec.get("bytes"),
               "log": log}


# -- verify -------------------------------------------------------------------


def _short_circuits(rec):
    """True when this record is a documented short-circuit exit point."""
    if str(rec.get("status", "")).lower() != "fail":
        return False
    if str(rec.get("gate", "")) in SHORT_CIRCUIT_GATES:
        return True
    if str(rec.get("outcome", "")).strip().lower() in ("reject", "rejected"):
        return True
    blockers = rec.get("blockers") or []
    if isinstance(blockers, (list, tuple)):
        blob = " ".join(str(b) for b in blockers)
    else:
        blob = str(blockers)
    return bool(_REJECT_RE.search(blob))


def verify(run_dir, depth):
    """Return (exit_code, result_dict)."""
    depth = str(depth or "").strip().lower()
    if depth not in DEPTH_GATES:
        return 1, {"error": "unknown depth %r (expected %s)"
                            % (depth, "|".join(sorted(DEPTH_GATES)))}
    if not os.path.isdir(run_dir):
        return 1, {"error": "run-dir does not exist or is not a directory: %s" % run_dir}

    log = os.path.join(run_dir, "run-log.jsonl")
    if not os.path.isfile(log):
        return 1, {"error": "run-log.jsonl not found in %s — a record that was never "
                            "written cannot be reported clean" % run_dir}
    try:
        with open(log, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        return 1, {"error": "run-log.jsonl unreadable: %s" % exc}

    records = []
    for lineno, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except ValueError as exc:
            return 1, {"error": "run-log.jsonl line %d is malformed JSON: %s" % (lineno, exc)}
        if not isinstance(obj, dict):
            return 1, {"error": "run-log.jsonl line %d is not a JSON object" % lineno}
        records.append(obj)

    if not records:
        return 1, {"error": "run-log.jsonl is empty — no gate was ever recorded"}

    required = DEPTH_GATES[depth]

    # Earliest short-circuit point, by ladder position.
    sc_gate, sc_idx = None, None
    for rec in records:
        if not _short_circuits(rec):
            continue
        g = str(rec.get("gate", ""))
        if g not in GATE_ORDER:
            continue
        idx = GATE_ORDER.index(g)
        if sc_idx is None or idx < sc_idx:
            sc_gate, sc_idx = g, idx

    accounted, failed = set(), set()
    for rec in records:
        g = str(rec.get("gate", ""))
        st = str(rec.get("status", "")).lower()
        if st in ("pass", "waived"):
            accounted.add(g)
        elif st == "fail":
            failed.add(g)

    missing, failing, after_short_circuit = [], [], []
    for g in required:
        if g in accounted:
            continue
        gidx = GATE_ORDER.index(g) if g in GATE_ORDER else None
        if sc_idx is not None and gidx is not None and gidx > sc_idx:
            after_short_circuit.append(g)
            continue
        if sc_idx is not None and g == sc_gate:
            continue  # the terminating gate itself: its fail receipt IS the record
        if g in failed:
            failing.append(g)
        else:
            missing.append(g)

    result = {
        "depth": depth,
        "required": required,
        "accounted": sorted(accounted),
        "missing": missing,
        "failing": failing,
        "short_circuit_gate": sc_gate,
        "after_short_circuit": after_short_circuit,
        "records": len(records),
    }
    if missing or failing:
        return 2, result
    return 0, result


# -- self-test ----------------------------------------------------------------


def _write(path, body):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def _receipt_file(tmp, name, obj):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    return path


def _log_lines(run_dir):
    with open(os.path.join(run_dir, "run-log.jsonl"), encoding="utf-8") as fh:
        return [json.loads(ln) for ln in fh if ln.strip()]


def _seed_log(run_dir, entries):
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "run-log.jsonl"), "w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")
    return run_dir


def self_test(broken=False):
    global _NEUTER_ARTIFACT_CHECK
    _NEUTER_ARTIFACT_CHECK = broken
    ok = True

    def chk(name, got, want):
        nonlocal ok
        if got == want:
            print("  OK   %s" % name)
        else:
            ok = False
            print("  FAIL %s (got %r, want %r)" % (name, got, want))

    # The kill switch must not silently swallow the whole self-test.
    prior_kill = os.environ.pop("FORGE_RECEIPT", None)

    try:
        with tempfile.TemporaryDirectory() as tmp:
            # (a) append refuses a `pass` receipt whose artifact is missing.
            rd = os.path.join(tmp, "a")
            os.makedirs(rd)
            r = _receipt_file(tmp, "a.json",
                              {"gate": "G2", "status": "pass", "artifact": "plan-A.md",
                               "bytes": 9999, "digest": [], "blockers": [], "confidence": 0.9})
            code, _ = append("G2", r, rd)
            chk("(a) pass receipt naming a MISSING artifact is refused (2)", code, 2)
            chk("(a) the refusal wrote NO ledger line",
                os.path.exists(os.path.join(rd, "run-log.jsonl")), False)

            # (a2) an artifact that exists but is EMPTY is the same refusal.
            _write(os.path.join(rd, "plan-A.md"), "")
            code, _ = append("G2", r, rd)
            chk("(a2) pass receipt naming an EMPTY artifact is refused (2)", code, 2)

            # (a3) ⛔ REGRESSION GUARD — a DIRECTORY is not an artifact.
            # os.path.getsize() on a directory returns 384/416/..., i.e. > 0, so a
            # size-only check accepts it. Caught by a live smoke test against a real
            # run dir; without this assertion the isfile() guard can be removed and
            # every other fixture still passes.
            r_dir = _receipt_file(tmp, "adir.json",
                                  {"gate": "G2", "status": "pass", "artifact": rd})
            code, res = append("G2", r_dir, rd)
            chk("(a3) pass receipt naming a DIRECTORY is refused (2)", code, 2)
            chk("(a3) and the refusal says WHY it is not an artifact",
                "directory" in res.get("error", ""), True)

            # (b) append succeeds, recomputes bytes from disk, stores a relative path.
            rd_b = os.path.join(tmp, "b")
            os.makedirs(rd_b)
            body = "# plan A\nreal content on disk\n"
            art_abs = _write(os.path.join(rd_b, "plan-A.md"), body)
            r_b = _receipt_file(tmp, "b.json",
                                {"gate": "G2", "status": "pass", "artifact": art_abs,
                                 "bytes": 1, "digest": ["x"], "blockers": [], "confidence": 0.8})
            code, _ = append("G2", r_b, rd_b)
            chk("(b) a real artifact appends clean (0)", code, 0)
            lines = _log_lines(rd_b)
            chk("(b) exactly one ledger line", len(lines), 1)
            chk("(b) bytes RECOMPUTED from disk, not the receipt's self-report",
                lines[0]["bytes"], len(body.encode("utf-8")))
            chk("(b) an ABSOLUTE artifact path is stored run-dir-RELATIVE",
                lines[0]["artifact"], "plan-A.md")

            # (c) malformed / unreadable inputs are could-not-run (1), never clean.
            code, _ = append("G2", os.path.join(tmp, "nope.json"), rd_b)
            chk("(c1) a missing receipt file is could-not-run (1)", code, 1)
            bad = _write(os.path.join(tmp, "bad.json"), "{not json at all")
            code, _ = append("G2", bad, rd_b)
            chk("(c2) a malformed receipt is could-not-run (1)", code, 1)
            code, _ = append("G2", r_b, os.path.join(tmp, "no-such-run-dir"))
            chk("(c3) an unreadable run-dir is could-not-run (1)", code, 1)
            bad_status = _receipt_file(tmp, "bs.json",
                                       {"gate": "G2", "status": "greenish", "artifact": art_abs})
            code, _ = append("G2", bad_status, rd_b)
            chk("(c4) an out-of-contract status is could-not-run (1)", code, 1)
            mismatch = _receipt_file(tmp, "mm.json",
                                     {"gate": "G5", "status": "pass", "artifact": art_abs})
            code, _ = append("G2", mismatch, rd_b)
            chk("(c5) a CLI/receipt gate mismatch is could-not-run (1), never pick-one", code, 1)

            # (c6) a FAILED gate records as-is — no artifact existence check.
            rd_f = os.path.join(tmp, "f")
            os.makedirs(rd_f)
            r_f = _receipt_file(tmp, "f.json",
                                {"gate": "G1", "status": "fail", "artifact": "claims-table.md",
                                 "blockers": ["unsourced third-party claim"]})
            code, _ = append("G1", r_f, rd_f)
            chk("(c6) a FAIL receipt with no artifact on disk still records (0)", code, 0)
            chk("(c6) and is honest that its size was not verifiable",
                _log_lines(rd_f)[0]["bytes_verified"], False)

            # (d) verify passes when every required gate for the depth is present.
            rd_d = _seed_log(os.path.join(tmp, "d"),
                             [{"gate": g, "status": "pass"} for g in DEPTH_GATES["quick"]])
            code, res = verify(rd_d, "quick")
            chk("(d) quick with every required gate present is clean (0)", code, 0)
            chk("(d) and nothing is reported missing", res["missing"], [])
            rd_d2 = _seed_log(os.path.join(tmp, "d2"),
                              [{"gate": g, "status": "pass"} for g in DEPTH_GATES["standard"]])
            code, _ = verify(rd_d2, "standard")
            chk("(d2) standard with its full set is clean (0)", code, 0)
            code, _ = verify(rd_d2, "deep")
            chk("(d3) deep requires the SAME set as standard", code, 0)
            rd_d3 = _seed_log(os.path.join(tmp, "d3"),
                              [{"gate": g, "status": ("waived" if g == "G3b" else "pass")}
                               for g in DEPTH_GATES["quick"]])
            code, _ = verify(rd_d3, "quick")
            chk("(d4) a WAIVED gate counts as accounted for", code, 0)

            # (e) verify refuses and NAMES the gap when a gate is missing with no
            #     short-circuit to explain it. G3b is the measured CE-6 skip.
            rd_e = _seed_log(os.path.join(tmp, "e"),
                             [{"gate": g, "status": "pass"}
                              for g in DEPTH_GATES["quick"] if g != "G3b"])
            code, res = verify(rd_e, "quick")
            chk("(e) a silently-skipped required gate is refused (2)", code, 2)
            chk("(e) and the gap is NAMED, not just counted", res["missing"], ["G3b"])

            # (f) RED-TEAM #2: a legitimately short-circuited run must NOT fail verify.
            rd_f1 = _seed_log(os.path.join(tmp, "f1"), [
                {"gate": "G0", "status": "pass"},
                {"gate": "G1", "status": "fail", "blockers": ["BLOCK: unsourced claim"]},
            ])
            code, res = verify(rd_f1, "quick")
            chk("(f1) a G1-BLOCK short circuit is clean (0), not a false denial", code, 0)
            chk("(f1) the gates after it are correctly ABSENT, not missing",
                res["after_short_circuit"], ["G2", "G3", "G3b", "G6", "G7", "G8"])
            rd_f2 = _seed_log(os.path.join(tmp, "f2"),
                              [{"gate": g, "status": "pass"}
                               for g in ["G0", "G1", "G2", "G3", "G3b", "G6"]]
                              + [{"gate": "G7", "status": "fail", "outcome": "reject"}])
            code, _ = verify(rd_f2, "quick")
            chk("(f2) a G7 `reject` short circuit is clean (0)", code, 0)
            # ...but a short circuit does not excuse gates BEFORE it.
            rd_f3 = _seed_log(os.path.join(tmp, "f3"),
                              [{"gate": "G1", "status": "fail", "blockers": ["BLOCK"]}])
            code, res = verify(rd_f3, "quick")
            chk("(f3) a short circuit does NOT excuse an EARLIER missing gate (2)", code, 2)
            chk("(f3) and names it", res["missing"], ["G0"])

            # (g) verify on an unreadable/absent run-log is could-not-run (1).
            rd_g = os.path.join(tmp, "g")
            os.makedirs(rd_g)
            code, _ = verify(rd_g, "quick")
            chk("(g1) a run dir with NO run-log is could-not-run (1), never clean", code, 1)
            _write(os.path.join(rd_g, "run-log.jsonl"), "{broken\n")
            code, _ = verify(rd_g, "quick")
            chk("(g2) a malformed run-log line is could-not-run (1)", code, 1)
            _write(os.path.join(rd_g, "run-log.jsonl"), "")
            code, _ = verify(rd_g, "quick")
            chk("(g3) an EMPTY run-log is could-not-run (1)", code, 1)
            code, _ = verify(os.path.join(tmp, "no-such-dir"), "quick")
            chk("(g4) a missing run dir is could-not-run (1)", code, 1)
            code, _ = verify(rd_d, "enormous")
            chk("(g5) an unknown depth is could-not-run (1)", code, 1)

            # (h) the kill switch: both subcommands exit 0 immediately, and append
            #     writes nothing. A new mechanism must never be able to wedge a run.
            os.environ["FORGE_RECEIPT"] = "off"
            try:
                chk("(h) is_disabled honours the env kill switch", is_disabled(), True)
                rd_h = os.path.join(tmp, "h")
                os.makedirs(rd_h)
                rc_h = main(["append", "G2", "--receipt", r, "--run-dir", rd_h])
                chk("(h) append exits 0 when disabled", rc_h, 0)
                chk("(h) and wrote no ledger line",
                    os.path.exists(os.path.join(rd_h, "run-log.jsonl")), False)
                rc_h = main(["verify", "--run-dir", os.path.join(tmp, "no-such"),
                             "--depth", "quick"])
                chk("(h) verify exits 0 when disabled, even on a bad run-dir", rc_h, 0)
            finally:
                os.environ.pop("FORGE_RECEIPT", None)

            # (h2) the posture kill switch, read without PyYAML.
            proj = os.path.join(tmp, "proj")
            os.makedirs(os.path.join(proj, ".ravenclaude"))
            posture = os.path.join(proj, ".ravenclaude", "comfort-posture.yaml")
            _write(posture, "design_checkins: true\nforge_receipt: off\n")
            chk("(h2) `forge_receipt: off` in comfort-posture disables",
                is_disabled(proj), True)
            _write(posture, "design_checkins: true\nforge_receipt: on\n")
            chk("(h2) `forge_receipt: on` does NOT disable", is_disabled(proj), False)
    finally:
        if prior_kill is not None:
            os.environ["FORGE_RECEIPT"] = prior_kill

    print()
    print("  forge-receipt self-test: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="FORGE Saga run-record recorder + verifier")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true",
                    help="neuter the fail-closed artifact check and assert the "
                         "self-test CATCHES it; exits 0 only when the teeth bite")
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd")

    p_app = sub.add_parser("append", help="append one gate receipt to run-log.jsonl")
    p_app.add_argument("gate")
    p_app.add_argument("--receipt", required=True)
    p_app.add_argument("--run-dir", required=True)

    p_ver = sub.add_parser("verify",
                           help="assert the depth's required gate set is accounted for")
    p_ver.add_argument("--run-dir", required=True)
    p_ver.add_argument("--depth", required=True)

    args = ap.parse_args(argv)

    if args.must_fail:
        rc = self_test(broken=True)
        if rc == 0:
            print("  TEETH FAILED: a neutered recorder still passed the self-test")
            return 1
        print("  teeth OK: the planted defect was caught")
        return 0
    if args.self_test:
        return self_test()

    if not args.cmd:
        ap.error("a subcommand is required (append | verify), or use --self-test / --must-fail")

    # ⛔ The kill switch is checked BEFORE any work, so a disabled recorder can
    # never block, refuse, or write. Exit 0 with an honest `disabled` status.
    if is_disabled(getattr(args, "run_dir", "") or ""):
        res = _disabled_result(args.cmd)
        print(json.dumps(res) if args.json else "forge-receipt: DISABLED (%s)" % res["reason"])
        return 0

    if args.cmd == "append":
        code, res = append(args.gate, args.receipt, args.run_dir)
        if args.json:
            print(json.dumps(res, indent=2, sort_keys=True))
        elif code == 0:
            print("forge-receipt: appended %s (%s) -> %s [%s bytes]"
                  % (res["gate"], res["receipt_status"], res["artifact"] or "-", res["bytes"]))
        elif code == 2:
            print("forge-receipt: REFUSED — %s" % res["error"])
            print("⛔ A `pass` receipt must name an artifact that exists and is non-empty. "
                  "Write the artifact, then re-append.")
        else:
            print("forge-receipt: COULD NOT RUN — %s" % res["error"])
            print("⛔ This is NOT a pass. A recorder that cannot run must not report clean.")
        return code

    code, res = verify(args.run_dir, args.depth)
    if args.json:
        print(json.dumps(res, indent=2, sort_keys=True))
    elif code == 0:
        note = ""
        if res.get("short_circuit_gate"):
            note = " (short-circuited at %s; %d later gate(s) correctly absent)" % (
                res["short_circuit_gate"], len(res["after_short_circuit"]))
        print("forge-receipt: COMPLETE — depth=%s, %d/%d required gates accounted for "
              "across %d record(s)%s"
              % (res["depth"],
                 len(res["required"]) - len(res["missing"]) - len(res["failing"]),
                 len(res["required"]), res["records"], note))
    elif code == 2:
        print("forge-receipt: INCOMPLETE — depth=%s" % res["depth"])
        if res["missing"]:
            print("  missing (no receipt at all): %s" % ", ".join(res["missing"]))
        if res["failing"]:
            print("  failed with no pass/waiver:  %s" % ", ".join(res["failing"]))
        print("⛔ G8 must not report a clean exit while a required gate is unaccounted for.")
    else:
        print("forge-receipt: COULD NOT RUN — %s" % res["error"])
        print("⛔ This is NOT a pass. A verifier that cannot see must not report clean.")
    return code


if __name__ == "__main__":
    sys.exit(main())
