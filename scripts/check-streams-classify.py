#!/usr/bin/env python3
"""check-streams-classify.py — Gate 110 engine for Agentic Work-Streams (P0).

Proves three properties of the pure store + classifier libs, all stdlib-only / CI-safe:

  1. DETERMINISM       — derive_features() + classify() are byte-stable across runs.
  2. NO-EGRESS         — a distinctive multi-word prompt phrase routed through
                         derive_features -> append_event NEVER appears in the stored
                         history.jsonl (the load-bearing privacy tripwire), AND
                         append_event REFUSES a raw-content field (`prompt`/`text`/...).
  3. CLASSIFY-ACCURACY — on a labeled fixture, the TF-IDF/cosine classifier routes every
                         held-out eval prompt to its expected stream (confident).

Modes (so audit-gates.sh can drive both halves of the bidirectional gate):
  (default)            run the real assertions; exit 0 on all-pass, nonzero on any failure.
  --must-fail-egress   re-run the no-egress check with the tripwire DISABLED (the real
                       ops._validate_event_fields monkeypatched to a no-op) and drive the
                       REAL ops.append_event with a raw-content field; the phrase MUST then
                       leak -> this mode exits 0 ONLY IF the leak is detected (proving the
                       gate has teeth). audit-gates runs it must_pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLASSIFY = REPO / "plugins/ravenclaude-core/scripts/stream-classify.py"
OPS = REPO / "plugins/ravenclaude-core/scripts/stream-ops.py"
FIXTURE = REPO / "tests/fixtures/streams/classify-fixture.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build_centroids(clf, train: dict) -> dict:
    centroids = {}
    for sid, docs in train.items():
        c = {}
        for doc in docs:
            c = clf.update_centroid(c, doc)
        centroids[sid] = c
    return centroids


def check_determinism(clf) -> list[str]:
    errs = []
    text = "Deploy the billing service to production with a canary rollout and a refund"
    f1 = json.dumps(clf.derive_features(text), sort_keys=True)
    f2 = json.dumps(clf.derive_features(text), sort_keys=True)
    if f1 != f2:
        errs.append("derive_features not deterministic")
    # classify determinism (with a small centroid set)
    centroids = {
        "a": clf.update_centroid({}, "billing invoice payment"),
        "b": clf.update_centroid({}, "auth login token"),
    }
    r1 = json.dumps(clf.classify(text, centroids), sort_keys=True)
    r2 = json.dumps(clf.classify(text, centroids), sort_keys=True)
    if r1 != r2:
        errs.append("classify not deterministic")
    # tie-break determinism: identical centroids -> lowest id wins, stable
    eq = clf.update_centroid({}, "shared term here")
    rt = clf.classify("shared term here", {"zzz": dict(eq), "aaa": dict(eq)})
    if rt["best_stream"] != "aaa":
        errs.append(f"tie-break not lowest-id (got {rt['best_stream']!r})")
    return errs


def check_no_egress(clf, ops, fixture: dict) -> list[str]:
    """Route the distinctive phrase through the REAL path; assert it never lands in history."""
    errs = []
    phrase = fixture["egress_phrase"]
    with tempfile.TemporaryDirectory() as d:
        ops.create_stream(d, "Privacy Probe", ts="2026-06-23T00:00:00Z")
        sid = ops.slugify("Privacy Probe")
        # derive features from the phrase (the supported path), then persist DERIVED-only.
        feats = clf.derive_features(phrase)
        ops.append_event(
            d,
            sid,
            label=feats["label"],
            terms=feats["terms"],
            word_count=feats["word_count"],
            session_id="sess-x",
            ts="2026-06-23T00:01:00Z",
        )
        hist_path = Path(d) / ".ravenclaude" / "streams" / sid / "history.jsonl"
        hist = hist_path.read_text(encoding="utf-8")
        if phrase in hist:
            errs.append("NO-EGRESS VIOLATION: prompt phrase found in history.jsonl")
        # any 4+ word window of the phrase must also be absent (phrase reconstruction)
        words = phrase.split()
        for i in range(len(words) - 3):
            window = " ".join(words[i : i + 4])
            if window in hist:
                errs.append(f"NO-EGRESS VIOLATION: 4-word window {window!r} in history")
                break
        # the tripwire: a raw-content field must be REFUSED
        for bad_key in ("prompt", "text", "content", "command"):
            try:
                ops.append_event(d, sid, extra={bad_key: phrase})
                errs.append(f"tripwire did not reject forbidden key {bad_key!r}")
            except ValueError:
                pass
    return errs


def check_accuracy(clf, fixture: dict) -> list[str]:
    errs = []
    centroids = _build_centroids(clf, fixture["train"])
    for item in fixture["eval"]:
        r = clf.classify(item["text"], centroids)
        # Put best_score inside the f-string; the old trailing `% r["best_score"]`
        # applied %-formatting to an already-materialized f-string, so any literal
        # '%' in the eval text (via !r) became a stray conversion spec and crashed
        # the diagnostic with a formatting error (2026-07 review).
        if r["best_stream"] != item["expect"]:
            errs.append(
                f"misroute: {item['text'][:40]!r} -> {r['best_stream']!r} "
                f"(expected {item['expect']!r}, score={r['best_score']:.3f})"
            )
        elif not r["confident"]:
            errs.append(
                f"low-confidence on expected match: {item['text'][:40]!r} "
                f"-> {r['best_stream']!r} score={r['best_score']:.3f}"
            )
    return errs


def must_fail_egress(clf, ops, fixture: dict) -> int:
    """Route the phrase through the REAL write path with the guard DISABLED; assert it leaks.

    Monkeypatches the real no-egress tripwire (``ops._validate_event_fields``, stream-ops.py)
    to a no-op, then drives the REAL ``ops.append_event`` with a raw-content field
    (``extra={"prompt": phrase}``). The phrase MUST then land in history.jsonl — proving the
    guard removed from production code is exactly what suppresses the leak. Exit 0 iff it
    leaks. This mirrors must_fail_sticky's pattern of exercising real functions along the
    broken path, rather than hand-writing a leaky line that runs zero production code.
    """
    phrase = fixture["egress_phrase"]
    with tempfile.TemporaryDirectory() as d:
        ops.create_stream(d, "Leaky Probe", ts="2026-06-23T00:00:00Z")
        sid = ops.slugify("Leaky Probe")
        # Neutralize the REAL tripwire, then drive the REAL append_event with a
        # forbidden raw-content field. append_event's internal calls to
        # _validate_event_fields resolve through the module global, so patching it on
        # the module disables the guard inside the real write path.
        original = ops._validate_event_fields
        ops._validate_event_fields = lambda fields: None
        try:
            ops.append_event(d, sid, extra={"prompt": phrase}, ts="2026-06-23T00:01:00Z")
        finally:
            ops._validate_event_fields = original
        hist = (Path(d) / ".ravenclaude" / "streams" / sid / "history.jsonl").read_text(
            encoding="utf-8"
        )
        if phrase in hist:
            print(
                "  must-fail-egress: leak DETECTED via real append_event with the guard "
                "disabled (gate has teeth)"
            )
            return 0
        print(
            "  must-fail-egress: ERROR — leak NOT detected even with the guard disabled",
            file=sys.stderr,
        )
        return 1


def main(argv: list[str]) -> int:
    clf = _load(CLASSIFY, "stream_classify")
    ops = _load(OPS, "stream_ops")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    if "--must-fail-egress" in argv:
        return must_fail_egress(clf, ops, fixture)

    all_errs: list[str] = []
    all_errs += check_determinism(clf)
    all_errs += check_no_egress(clf, ops, fixture)
    all_errs += check_accuracy(clf, fixture)

    if all_errs:
        print("Gate 110 FAILURES:", file=sys.stderr)
        for e in all_errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(
        "  determinism OK | no-egress OK | classify-accuracy OK (%d eval prompts)"
        % len(fixture["eval"])
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
