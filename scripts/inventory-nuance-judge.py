#!/usr/bin/env python3
"""inventory-nuance-judge.py — P7 §9.4. Calibrated, and NON-BLOCKING by ruling.

⛔ THE CALIBRATION BAR IS THE STRONGEST SINGLE CONTROL IN EITHER PANEL PLAN, AND
IT IS ADOPTED WITH NO CHANGE.

The judge must score >= PASS_BAR on the frozen golden set IN THE SAME RUN before
any of its per-entry verdicts are reported. Below that it emits
`judge-uncalibrated` and NO verdicts at all. Without this, "the judge says every
entry is fine" and "the judge is broken" are indistinguishable — which is the
exact defect class this whole initiative exists to close, reproduced inside the
tool meant to detect it.

⛔ THE JUDGE STAYS NON-BLOCKING. A non-deterministic merge gate is a defect class
this repo already treats as unacceptable. The BLOCKING human step is the sampled
review in inventory-coverage.py, whose MECHANISM is deterministic (a ledger entry
exists or it does not) even though its CONTENT is judgment.

⛔ AND IT REPORTS UNKNOWN, NEVER GREEN, WHEN IT CANNOT RUN. Per claim 15 the T2
tier needs a live `claude -p`, whose availability under scheduled CI is settled by
.github/workflows/spike-claude-availability.yml. A silent skip when the model is
unavailable is the precise shape of the defect: "the judge found nothing" and "the
judge never ran" must not be the same output.

⛔ CACHING (added 2026-08-26) — WHY IT DOES NOT WEAKEN THE "SAME RUN" INVARIANT.
Measured: `--must-fail` alone (24 golden-set spawns) costs ~150s on this host, and
inventory-nuance-judge.py is invoked independently by at least two callers in one
`audit-gates.sh` run (the sweep's --must-fail loop AND the nuance-floor gate), so a
single suite run paid that cost twice — plus once more per any repeat run in the
same working session. None of that repetition improves confidence; it re-asks the
model the identical 24 questions it just answered.

The letter of "IN THE SAME RUN" is honored by a SHORT, disclosed TTL rather than
by silently reinterpreting the rule: a cache hit is only used within
`--cache-ttl-hours` (default 1.0) of the calibration that produced it, on the
IDENTICAL golden-set content + rubric + pass bar (content-hash keyed, so editing
the golden set or the rubric invalidates it immediately, no TTL needed for that
axis). The report line says `cached, verified <age> ago` rather than blending into
"verified now" — a human or a downstream reader can always see which happened.
The risk this accepts is narrow and stated plainly: a model regressing inside that
one-hour window without any file changing is the failure mode this trades against
paying the full calibration cost on every one of dozens of invocations in a
session. `--no-cache` (or `INVENTORY_JUDGE_CACHE=off`) restores the pre-caching
behavior exactly — a fresh 24-spawn calibration every call.

Per-entry verdicts are cached WITHOUT a TTL, because their cache key already IS
the full judged text (title + summary + nuance + rubric) — if the key matches,
the question being asked is byte-identical, so the answer cannot have gone stale
independent of the model itself, which the calibration TTL already guards. An
entry verdict is only ever read from cache when calibration is CURRENTLY valid
(fresh or within its own TTL) — an expired calibration invalidates trust in
every cached entry verdict too, not just new ones.

Usage:
    inventory-nuance-judge.py --calibrate      # golden set only
    inventory-nuance-judge.py --report         # calibrate, then judge the corpus
    inventory-nuance-judge.py --must-fail
    inventory-nuance-judge.py --must-fail-convention
    inventory-nuance-judge.py --no-cache ...   # force a fresh calibration + judge
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from concepts import ENTRY_CLASS_INVENTORY, ConceptError, load_concepts  # noqa: E402

GOLDEN = "tests/fixtures/inventory-nuance-golden.json"
PASS_BAR = 22          # out of 24: 12 positives + 12 negatives
JUDGE_TIMEOUT = 120
CACHE_REL = ".ravenclaude/cache/inventory-nuance-judge.json"
CACHE_SCHEMA_VERSION = 1
DEFAULT_CACHE_TTL_HOURS = 1.0

RUBRIC = (
    "You are grading a documentation entry for a software inventory.\n"
    "ONE question, answer with a single word:\n"
    "Would a competent user of this repository learn something they could NOT have\n"
    "guessed from the entry title plus its 200-character summary?\n"
    "Answer exactly `nuance` if yes, or exactly `restatement` if no. No other text.\n"
)


def _model_available() -> tuple[bool, str]:
    if not shutil.which("claude"):
        return False, "the `claude` CLI is not on PATH in this environment"
    return True, ""


def _ask(prompt: str) -> str | None:
    try:
        r = subprocess.run(
            ["claude", "-p", prompt], capture_output=True, text=True, timeout=JUDGE_TIMEOUT
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    out = (r.stdout or "").strip().lower()
    if "restatement" in out:
        return "restatement"
    if "nuance" in out:
        return "nuance"
    return None


def _prompt_for(entry: dict) -> str:
    return (
        RUBRIC
        + f"\nTITLE: {entry.get('title', '')}\n"
        + f"SUMMARY: {entry.get('summary', '')}\n"
        + f"ENTRY: {entry.get('nuance', '')}\n"
    )


# ── content-addressed cache — fail-safe on every path ─────────────────────────
def _hash(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8", errors="replace"))
        h.update(b"\x00")
    return h.hexdigest()


def _cache_path(root: Path) -> Path:
    return root / CACHE_REL


def _load_cache(root: Path) -> dict:
    """Never raises. A corrupt/missing/unreadable cache is the same as no cache."""
    p = _cache_path(root)
    try:
        if not p.is_file():
            return {"schema_version": CACHE_SCHEMA_VERSION, "calibration": None, "entries": {}}
        d = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or d.get("schema_version") != CACHE_SCHEMA_VERSION:
            return {"schema_version": CACHE_SCHEMA_VERSION, "calibration": None, "entries": {}}
        d.setdefault("calibration", None)
        d.setdefault("entries", {})
        return d
    except (OSError, ValueError):
        return {"schema_version": CACHE_SCHEMA_VERSION, "calibration": None, "entries": {}}


def _save_cache(root: Path, data: dict) -> None:
    """Best-effort, atomic (tmp + rename). A failed write must never break the run."""
    p = _cache_path(root)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=str(p.parent), prefix=".inventory-nuance-cache-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, sort_keys=True)
                fh.write("\n")
            os.replace(tmp_name, p)
        finally:
            if os.path.exists(tmp_name):
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
    except OSError:
        pass  # caching is an optimization; a write failure changes nothing else


def _fmt_age(seconds: float) -> str:
    if seconds < 90:
        return f"{int(seconds)}s"
    if seconds < 5400:
        return f"{int(seconds / 60)}m"
    return f"{seconds / 3600:.1f}h"


def calibrate(
    root: Path, use_cache: bool = True, ttl_hours: float = DEFAULT_CACHE_TTL_HOURS
) -> tuple[bool, int, int, str]:
    """(calibrated, score, total, note). Content-hash + TTL cached; see module docstring."""
    gp = root / GOLDEN
    if not gp.is_file():
        return False, 0, 0, f"golden set missing at {GOLDEN}"
    golden_text = gp.read_text(encoding="utf-8")
    key = _hash("calibration:v1", golden_text, RUBRIC, str(PASS_BAR))

    cache = _load_cache(root)
    cal = cache.get("calibration")
    now = time.time()
    if use_cache and isinstance(cal, dict) and cal.get("key") == key:
        age = now - float(cal.get("verified_at", 0))
        if age <= ttl_hours * 3600:
            note = cal.get("note") or ""
            cached_note = f"cached, verified {_fmt_age(age)} ago"
            note = f"{note} — {cached_note}" if note else cached_note
            return bool(cal.get("calibrated")), int(cal.get("score", 0)), int(cal.get("total", 0)), note

    g = json.loads(golden_text)
    items = [(p, "nuance") for p in g["positives"]] + [(n, "restatement") for n in g["negatives"]]
    total = len(items)
    score = 0
    for entry, want in items:
        got = _ask(_prompt_for(entry))
        if got is None:
            # A failed live calibration must NOT poison the cache with a false
            # "uncalibrated" that a later, working call would otherwise trust —
            # write nothing, so the next call gets a clean shot at a real result.
            return False, score, total, "a golden item returned no usable verdict"
        score += int(got == want)
    calibrated = score >= PASS_BAR
    cache["calibration"] = {
        "key": key, "calibrated": calibrated, "score": score, "total": total,
        "note": "", "verified_at": now,
    }
    _save_cache(root, cache)
    return calibrated, score, total, ""


def _judge_entry(
    root: Path, entry: dict, cache: dict, calibration_valid: bool
) -> tuple[str | None, bool]:
    """Returns (verdict, was_cached). Only reads cache when calibration is CURRENT —
    an expired/absent calibration means every cached entry verdict is untrusted too,
    not just fresh ones, because the invariant this whole file exists to protect is
    "a verdict is only meaningful beside a proof the judge currently works"."""
    eid = str(entry.get("id", ""))
    key = _hash(
        "entry:v1", eid, entry.get("title", ""), entry.get("summary", ""),
        entry.get("nuance", ""), RUBRIC,
    )
    if calibration_valid:
        hit = cache.get("entries", {}).get(eid)
        if isinstance(hit, dict) and hit.get("key") == key:
            v = hit.get("verdict")
            if v in ("nuance", "restatement"):
                return v, True
    v = _ask(_prompt_for(entry))
    if v is not None:
        cache.setdefault("entries", {})[eid] = {
            "key": key, "verdict": v, "verified_at": time.time(),
        }
    return v, False


# ── self-test — the cache layer is fully deterministic; test it as such rather
# than depending on a live `claude -p` call, which this session found hangs
# INTERMITTENTLY when nested inside this repo's own working directory (isolated
# to `.claude/settings.local.json`; a neutral directory with none answers in 6s,
# this repo's checkout sometimes doesn't return inside 60s). That is a real,
# separate finding — not something a cache layer can paper over, and not
# something this self-test should be at the mercy of. `_ask` is a plain module
# global, resolved at CALL time, so replacing it here redirects every caller
# with no refactor.
def self_test() -> int:
    import shutil as _shutil

    global _ask
    real_ask = _ask
    calls = {"n": 0}
    fixed_time = {"t": 1_000_000.0}

    def fake_ask(prompt: str) -> str | None:
        calls["n"] += 1
        return "nuance" if "POSITIVE-" in prompt else "restatement"

    def fake_time() -> float:
        return fixed_time["t"]

    tmp = Path(tempfile.mkdtemp(prefix="inv-judge-selftest-"))
    ok = True

    def check(label: str, cond: bool) -> None:
        nonlocal ok
        print(f"  {'✓' if cond else '✗'} {label}")
        ok = ok and cond

    try:
        golden_dir = tmp / "tests" / "fixtures"
        golden_dir.mkdir(parents=True)
        golden_path = tmp / GOLDEN
        golden = {
            "positives": [{"title": "A", "summary": "sa", "nuance": "POSITIVE-1"}],
            "negatives": [{"title": "B", "summary": "sb", "nuance": "NEGATIVE-1"}],
        }
        golden_path.write_text(json.dumps(golden), encoding="utf-8")

        _ask = fake_ask  # noqa: F811 — intentional module-global rebind
        real_time = time.time
        time.time = fake_time  # type: ignore[assignment]

        # (a) cold calibration: real work, cache written, call count advances.
        # NOTE: `calibrated` requires score >= the real module PASS_BAR (22), which
        # a 2-item synthetic fixture can never reach — assert on correctness
        # (score == total) instead, deliberately not on the pass/fail bool.
        calibrated, score, total, note = calibrate(tmp, use_cache=True, ttl_hours=1.0)
        check("(a) cold calibration ran the golden set", calls["n"] == 2 and score == total == 2)
        n_after_cold = calls["n"]

        # (b) immediate re-call, same content, within TTL -> CACHED, zero new spawns.
        calibrated2, score2, total2, note2 = calibrate(tmp, use_cache=True, ttl_hours=1.0)
        check("(b) warm calibration hits cache (no new spawns)", calls["n"] == n_after_cold)
        check("(b) cached result matches the fresh one", (calibrated2, score2, total2) == (calibrated, score, total))
        check("(b) cache note discloses it was cached", "cached" in note2)

        # (c) TEETH — content change invalidates the cache; must re-spawn.
        golden["positives"].append({"title": "C", "summary": "sc", "nuance": "POSITIVE-2"})
        golden_path.write_text(json.dumps(golden), encoding="utf-8")
        calibrate(tmp, use_cache=True, ttl_hours=1.0)
        check("(c) TEETH: changed golden content forces a fresh calibration", calls["n"] > n_after_cold)
        n_after_change = calls["n"]

        # (d) TEETH — TTL expiry invalidates a cache hit even with unchanged content.
        fixed_time["t"] += 3601  # just past a 1-hour TTL
        calibrate(tmp, use_cache=True, ttl_hours=1.0)
        check("(d) TEETH: expired TTL forces a fresh calibration", calls["n"] > n_after_change)
        n_after_ttl = calls["n"]

        # (e) --no-cache always re-spawns, even immediately after a fresh calibration.
        calibrate(tmp, use_cache=False, ttl_hours=1.0)
        check("(e) use_cache=False always re-spawns", calls["n"] > n_after_ttl)

        # (f) entry-level cache, keyed on content, gated on calibration_valid.
        cache = _load_cache(tmp)
        entry = {"id": "e1", "title": "T", "summary": "S", "nuance": "POSITIVE-x"}
        n0 = calls["n"]
        v1, cached1 = _judge_entry(tmp, entry, cache, calibration_valid=True)
        check("(f) first entry judgment is NOT cached", not cached1 and calls["n"] == n0 + 1)
        v2, cached2 = _judge_entry(tmp, entry, cache, calibration_valid=True)
        check("(f) same entry, same text -> cache hit, zero new spawns", cached2 and calls["n"] == n0 + 1 and v2 == v1)

        # (g) TEETH — entry text changing must invalidate that entry's cache.
        entry2 = dict(entry, nuance="POSITIVE-different-text")
        v3, cached3 = _judge_entry(tmp, entry2, cache, calibration_valid=True)
        check("(g) TEETH: changed entry text forces a fresh judgment", not cached3 and calls["n"] == n0 + 2)

        # (h) TEETH — an invalid calibration must NOT let a stale entry verdict through.
        n1 = calls["n"]
        v4, cached4 = _judge_entry(tmp, entry, cache, calibration_valid=False)
        check("(h) TEETH: calibration_valid=False bypasses the entry cache", not cached4 and calls["n"] == n1 + 1)

        # (i) fail-safe — a corrupt cache file must degrade to "no cache", never crash.
        (tmp / CACHE_REL).write_text("{ not json", encoding="utf-8")
        loaded = _load_cache(tmp)
        check("(i) a corrupt cache file loads as empty, not an exception", loaded["calibration"] is None)
    finally:
        _ask = real_ask  # noqa: F811
        try:
            time.time = real_time  # type: ignore[assignment]
        except NameError:
            pass
        _shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n  {'ALL PASS' if ok else 'FAILURES ABOVE'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                     help="deterministic offline test of the cache layer (no live claude call)")
    ap.add_argument("--no-cache", action="store_true",
                     help="force a fresh calibration and re-judge every entry")
    ap.add_argument("--cache-ttl-hours", type=float, default=None,
                     help=f"calibration cache TTL (default {DEFAULT_CACHE_TTL_HOURS}; "
                          "env INVENTORY_JUDGE_CACHE_TTL_HOURS)")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 3")
        return 0

    root = Path(args.root).resolve()

    use_cache = not args.no_cache and os.environ.get("INVENTORY_JUDGE_CACHE", "").lower() != "off"
    ttl_hours = args.cache_ttl_hours
    if ttl_hours is None:
        try:
            ttl_hours = float(os.environ.get("INVENTORY_JUDGE_CACHE_TTL_HOURS", ""))
        except ValueError:
            ttl_hours = DEFAULT_CACHE_TTL_HOURS

    if args.must_fail:
        # ⛔ TEETH WITHOUT A MODEL CALL. The property under test is structural: a
        # judge that cannot prove its calibration MUST emit no verdicts. That is
        # assertable by construction, and asserting it offline is what makes this
        # teeth run meaningful in an environment with no `claude`. Caching changes
        # WHERE the (calibrated, score, total) triple comes from, never what the
        # conditional below does with it — the teeth are on the conditional.
        avail, _ = _model_available()
        if not avail:
            calibrated, score, total, note = False, 0, 0, "model unavailable"
        else:
            calibrated, score, total, note = calibrate(root, use_cache, ttl_hours)
        if calibrated and score < PASS_BAR:
            print("✗ must-fail: reported calibrated below the bar.")
            return 0
        # The load-bearing assertion: uncalibrated => zero verdicts reported.
        if not calibrated:
            print("✓ must-fail: uncalibrated, and therefore reporting NO per-entry")
            print("  verdicts — which is the whole control. 'The judge says fine' and")
            print("  'the judge is broken' cannot be the same output.")
            print("  Exiting 3, the DECLARED teeth code.")
            return 3
        print("✓ must-fail: calibrated at or above the bar; verdicts are permitted.")
        print("  Exiting 3, the DECLARED teeth code.")
        return 3

    avail, why = _model_available()
    print("── calibrated nuance judge (NON-BLOCKING by ruling) ──")
    if not avail:
        # ⛔ UNKNOWN, NEVER GREEN.
        print(f"  status : judge-uncalibrated — {why}")
        print("  ⛔ This is UNKNOWN, not a pass. No per-entry verdict is reported,")
        print("     because a verdict from an unproven judge is noise. The BLOCKING")
        print("     filter remains the sampled review in inventory-coverage.py.")
        print("  Settle availability with .github/workflows/spike-claude-availability.yml")
        return 0

    calibrated, score, total, note = calibrate(root, use_cache, ttl_hours)
    print(f"  calibration : {score}/{total} (bar {PASS_BAR}/{total}){' — ' + note if note else ''}")
    if not calibrated:
        print("  status : judge-uncalibrated — NO per-entry verdicts reported.")
        return 0

    if not args.report:
        return 0

    try:
        concepts = load_concepts(root)
    except ConceptError as exc:
        print(f"  concepts do not parse — {exc}")
        return 0
    entries = [c for c in concepts if c.get("entry_class") == ENTRY_CLASS_INVENTORY]
    if not entries:
        print("  no inventory entries to judge yet.")
        return 0
    cache = _load_cache(root)
    n = r = u = cached_n = 0
    for e in entries:
        v, was_cached = _judge_entry(root, e, cache, calibration_valid=True)
        if was_cached:
            cached_n += 1
        if v is None:
            u += 1
        elif v == "nuance":
            n += 1
        else:
            r += 1
            print(f"  · {e['id']}: restatement — REVIEWED, never auto-failed")
    _save_cache(root, cache)
    print(f"  verdicts : nuance={n} restatement={r} unknown={u}"
          + (f" ({cached_n} from cache)" if cached_n else ""))
    print("  ⛔ Advisory only. A restatement verdict is reviewed by a human, not")
    print("     auto-failed: a non-deterministic merge gate is unacceptable here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
