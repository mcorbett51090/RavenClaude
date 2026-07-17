---
name: report-gold-standard-rubric
description: "The Phase-5 iterate-to-gold-standard loop contract for report-regeneration — score a review-ready draft against 4 dimensions (Accurate HARD FLOOR / Dynamic / Inclusive / Polished), each anchored to a deterministic harness leg with an honest judged residue. Owns the loop mechanics: stop = PASS or plateau(2) or cap(6), monotonic ratchet (revert on any regression), per-node edit budget, N=3 median for judged dims, and the do-no-harm zero-diff fixture. Also owns feedback-instrumentation: classify the client's real peer-review edits substantive-vs-mechanical and feed that back to tune the bars. Use after report-fidelity-harness emits a receipt and before a draft is handed to the human peer reviewer."
---

# Skill: report-gold-standard-rubric

You are running the **Phase 5 — iterate-to-gold-standard** loop (FORGE plan
§6a, binding TB-4a / RT2-F6) for a `report-regeneration` review-ready draft.
This skill turns a `report-fidelity-harness` receipt into a per-dimension
verdict, decides whether the draft needs another revision pass, and — when
it does — enforces the guardrails that keep the loop honest: a hard floor
that is never traded, a ratchet that reverts regressions, a budget that
freezes a stuck node instead of grinding forever, and a cap that always
terminates.

**This skill never claims "the report is correct."** It reproduces the
plugin's honest guarantee (`CLAUDE.md` §1): auto-QA proves *the checked
surfaces*; a PASS here means every checked dimension cleared its bar, not
that a human peer reviewer has nothing left to do. The manual residue this
skill surfaces (`escalate_to_human`, judged-stub dimensions, plateau
escalation) is exactly the mechanism that keeps that claim honest.

## The four dimensions

Each dimension has a **deterministic anchor** (a harness leg or a scanner —
proven, machine-checked) and, for three of the four, a **judged residue**
(behavioral, N=3-median-scored by a model judge). The anchor is a
**necessary condition**: a judged score can never rescue a red anchor.

| Dimension | Bar | Deterministic anchor | Judged residue |
|---|---|---|---|
| **Accurate — HARD FLOOR** (never iterated, never traded) | V1-V6 + period-coherence ALL green | the WHOLE `report-fidelity-harness` receipt | **none.** Fails CLOSED to `"unverified"` — **never** `"pass"` — when V1 is in binding-correctness mode (RT1-F12: no live Power BI data route, so V1 degraded from value-accuracy to binding-correctness). |
| **Dynamic** | zero static fossils; every manifest slot demonstrably rebound; variance narrative direction matches data direction (says "up" iff Δ>0) | V1 leg pass + a sign-consistency check | narrative fluency |
| **Inclusive** | per-format a11y gate green (axe-core HTML / veraPDF Office-PDF); reading order sane; alt-text present *and specific* | axe-core / veraPDF | alt-text *quality*, plain-language — LLM-judged, advisory |
| **Polished** | layout lint clean; render referee pass (Playwright HTML / LibreOffice Office — local for both formats); number/date formats consistent; no orphans (`NaN`, `{{`, empty nodes) | V5 leg (both formats) + a format-consistency scanner | typographic taste, visual hierarchy |

**Why Accurate is categorically different, in code as well as in prose:**
every other dimension collapses to a `[0,1]` judged score once its anchor is
green; Accurate never does — `rubric.score_accurate()` returns exactly one
of `"pass" | "fail" | "unverified"`, and `"unverified"` is reachable **only**
from the anchor, never from a judge. There is no code path in `rubric.py`
that lets a judged score turn Accurate green. See `rubric.py`'s own
docstring on `score_accurate()` for the exact precedence between a genuine
other-leg failure (reports `"fail"` — a proven leak outranks an honest "we
couldn't verify") and the V1-degrade case (reports `"unverified"`).

## Reading a `report-fidelity-harness` receipt

`rubric.py` consumes the receipt shape defined by
[`../../knowledge/fidelity-receipt.schema.json`](../../knowledge/fidelity-receipt.schema.json)
(see also [`../../knowledge/core-architecture-spec.md`](../../knowledge/core-architecture-spec.md)
§5). It reads `receipt["legs"]` (each `{leg, verdict, label, ...}`) and
`receipt["overall_gate"]`. It does **not** call the harness itself — that is
`report-fidelity-harness`'s job; this skill is downstream of it.

Three signals the rubric needs for Dynamic/Inclusive/Polished are **not**
part of `fidelity-receipt.schema.json` (that schema only carries the six
V-legs + period-coherence): the sign-consistency check, the two a11y gates,
and the format-consistency scanner. `rubric.py`'s scoring functions accept
these as **explicit optional keyword arguments** — a bare receipt with none
of them supplied still scores Accurate correctly, and the other three
dimensions degrade honestly (their anchor reports `False`, never a silent
pass) rather than assuming a signal that was never actually run.

```python
from rubric import score_all, passes_bar

scores = score_all(
    receipt,
    sign_consistency_pass=True,       # Dynamic anchor's second half
    a11y_axe_pass=True,                # Inclusive anchor (HTML)
    a11y_verapdf_pass=True,             # Inclusive anchor (Office PDF)
    format_consistency_pass=True,      # Polished anchor's second half
    dynamic_judged=0.91,               # N=3 median, already computed
    inclusive_judged=0.88,
    polished_judged=0.93,
)
if passes_bar(scores):
    ...  # PASS — every dimension's status == "pass"
```

## Loop mechanics

```
score_all(receipt, ...) → per-dimension {status, anchor_pass, judged_score, judged_stub}
                        → terminate(iterations)
                             ├─ PASS      : every dimension status == "pass" (checked FIRST, at
                             │              any iteration count — a cap/plateau that coincides
                             │              with a clean pass is still reported PASS)
                             ├─ cap       : len(iterations) >= 6
                             ├─ plateau   : the last 2 iterations both show "improved" == False
                             └─ otherwise : keep iterating — apply accept_revision() to the next
                                            candidate revision, respecting the per-node edit budget
```

### Stop condition (binding — TB-4a)

**PASS ∨ plateau(2 consecutive no-improvement) ∨ cap(6), whichever fires
first.** `rubric.terminate(iterations)` is the pure, model-free predicate —
see its docstring for the exact precedence. `STATUS_PASS = "PASS"`,
`STATUS_PLATEAU = "plateau"`, `STATUS_CAP = "cap"` are the fixed vocabulary;
plateau and cap both set `escalate_to_human = True` and route the residual to
`architect` — non-convergence is never silently swallowed, and genuine
human-only substantive residue is flagged, never faked as a pass.

### Monotonic ratchet (binding — RT2-F6)

`rubric.accept_revision(prev_scores, new_scores, target_dim)` — accept a
revision **only if** its target dimension improves **and no other dimension
drops**; otherwise revert. Accurate is additionally **never** allowed to
regress from `"pass"`, regardless of which dimension the revision targeted —
a revision that lifts Polished but silently corrupts a verified value node is
rejected outright, not traded.

### Per-node edit budget (binding)

`rubric.node_edit_budget_exceeded(edit_counts, node_id, budget=2)` — any
node revised twice without reaching the bar is **frozen** and flagged to the
human reviewer. That residue is theirs by the draft+QA model (`CLAUDE.md`
§1) — the loop does not grind on a single stuck node past its budget.

### N=3 median for judged dimensions (binding — RT2-F6, noisy-judge robustness)

Every judged dimension (Dynamic/Inclusive/Polished, once their anchor is
green) is scored by **3 independent judge calls**, reduced with
`rubric.judged_median(scores)`; the judge is fingerprinted in the receipt
(per `fidelity-receipt.schema.json`'s `judge_fingerprint` field) for
reproducibility. `rubric.judged_sample_insufficient(scores)` is the teeth:
a caller that tries to trust a median computed from fewer than 3 samples
must check this first — the N=3 rule is not just a docstring, it is a
checkable predicate.

### Do-no-harm zero-diff fixture (binding — RT2-F6, required acceptance test)

**An input already at the bar must exit at iteration 1 with ZERO content
diffs.** This is the loop's do-no-harm invariant: a report that is already
gold-standard is never edited "for the sake of iterating." Concretely — call
`terminate([iteration_1])` where `iteration_1["scores"]` already satisfies
`passes_bar()` and `iteration_1["content_diff_count"] == 0`; the loop must
stop with `STATUS_PASS` at `iterations == 1`, and the caller must never have
applied a revision to reach that state. `tests/test_rubric.py`'s
`TestZeroDiffFixture` is exactly this test, run against `rubric.py` directly.

### Advisory dimensions are not iterated to convergence

The judged residues (narrative fluency; alt-text quality/plain-language;
typographic taste/visual hierarchy) are **advisory** — the loop has no
obligation to grind them to a perfect score once the dimension's own bar is
cleared. Only a red anchor or a below-bar judged median keeps a dimension
`"fail"`; once `"pass"`, further polish on that dimension is out of scope for
this loop (a human reviewer's taste call, not a re-iteration trigger).

## Feedback instrumentation (G0-d — the calibration signal)

Peer review is a **downstream human step**; the plugin emits a review-ready
draft only (`CLAUDE.md` §1, §4 Scope). There is no in-plugin secured human
grader — instead, **the client's real peer-review feedback, over successive
real reports, is the calibration signal that tunes this rubric's bars.**

The contract (FORGE plan §5-P0 G0-d):

1. **Capture** the reviewer's demanded edits per shipped report — every
   change the human peer reviewer requested before the report went out.
2. **Classify each edit substantive vs. mechanical/QA:**
   - **Mechanical/QA** — a wrong value, a stale label, a broken layout, a
     missed alt-text, an inconsistent number format: exactly the class of
     defect one of the four dimensions' deterministic anchors is *supposed*
     to catch. A mechanical edit surfacing in real peer review is a
     **miss** — the anchor should have caught it, or the bar is set too low.
   - **Substantive** — a judgment call about framing, emphasis, narrative
     interpretation, or a domain fact no automated check could verify: this
     is genuine human-only residue, exactly what `manual_residue` on the
     fidelity receipt is honestly enumerating (`CLAUDE.md` §1: "does NOT
     guarantee a human-free-correct report").
3. **Feed the classification back** into the Binding Manifest + this
   rubric: a recurring *mechanical* miss on a given dimension is evidence
   that dimension's bar, anchor coverage, or judged-residue weighting needs
   tightening; a *substantive*-only pattern is evidence the harness + rubric
   are doing their job and the residual is correctly human-owned.
4. **The measured question, over successive real reports:** does auto-QA
   leave the reviewer giving **only substantive** feedback? That trend line
   — not any single report — is the calibration signal. It replaces the
   pre-secured human-grader gate the original G0-d design called for
   (struck per rev. 2 scope change — RT2-F1/critic-P0).

**This is an ongoing calibration instrument, not a hard pre-build blocker.**
It does not gate any release; it tunes the rubric's bars (`DEFAULT_BAR` in
`rubric.py`, the anchor thresholds, which judged dimensions get weight) over
time as real feedback accumulates. Implementation note: the classifier
itself (substantive vs. mechanical) is a downstream, report-regeneration-
specific instrument that consumes real reviewer edits — it is out of scope
for `rubric.py` (which is a pure, receipt-scoring + loop-termination module
with no I/O beyond its own CLI); wire it as a separate script that reads the
shipped-report + reviewer-diff pair and writes its classification alongside
the run's fidelity receipt under `.ravenclaude/runs/`, per the plugin's Run
Artifacts convention.

## Files

| file | role |
|---|---|
| `rubric.py` | pure, stdlib-only, Python 3.9-compatible: `score_accurate` / `score_dynamic` / `score_inclusive` / `score_polished` / `score_all`, `passes_bar`, `judged_median` / `judged_sample_insufficient`, `dimension_score`, `accept_revision` (monotonic ratchet), `node_edit_budget_exceeded`, and `terminate` (the PASS/plateau/cap stop predicate) — plus a CLI (`--receipt` to score, `--iterations` to run `terminate()`). |
| `tests/test_rubric.py` | `unittest`, stdlib-only. Covers the three required acceptance tests (zero-diff fixture exits at iteration 1 unchanged; a rigged never-improving scorer triggers plateau at 2; the Accurate floor fails closed to `"unverified"` on a V1-binding-correctness-mode receipt) plus the monotonic ratchet, the per-node edit budget, the cap stop, and the N=3 median helper. |

## Reuse ledger (no duplication)

- **`refine-to-rubric` / `converge.py`** (`ravenclaude-core`) is the
  domain-neutral Convergence Engine this skill's loop mechanics are modeled
  on (plateau/cap/keep-best, model-free `terminate()`, N-agreement judging,
  never-claim-perfect vocabulary) — **not imported or wrapped**, because the
  two rubrics are shaped differently: `converge.py` grades one weighted
  score across freely-tradeable dimensions; this skill grades four
  independently-gated dimensions, one of which (Accurate) is a hard floor
  that can **never** be traded for gains elsewhere. Anyone extending this
  skill should read `converge.py`'s docstring first — the anti-failure-mode
  reasoning (objective-first, cross-model judge, model-free stop authority)
  applies verbatim here.
- **`agent-quality-rubric`** (`ravenclaude-core`) is the sibling pattern for
  an anchored, multi-dimension scorecard with remediation guidance — read
  for the "quote, don't vibe-grade" review discipline when a human is
  grading the judged residues by hand.
- **`report-fidelity-harness`** (this plugin, Phase 2) owns V1-V6 +
  period-coherence themselves; this skill only *reads* the receipt they
  emit. Do not re-implement any harness leg here.
- **`report-qa-gate`** (this plugin) is the downstream consumer that
  assembles the per-format tiered report + manual-residue checklist a human
  reviewer sees; it calls this skill's `score_all` to get the four
  dimension verdicts and this skill's `terminate` to decide whether another
  revision pass is warranted before handing the draft off.

## Acceptance tests (binding — RT2-F6)

- A seeded-mediocre regeneration reaches the bar within the cap (6
  iterations) — drive `terminate()` with a monotonically-improving
  iteration history and assert `STATUS_PASS` before `iterations` hits 6.
- A rigged never-improving scorer triggers the plateau escape (must-fail
  half) — `tests/test_rubric.py::TestPlateauEscape`.
- The zero-diff fixture exits at iteration 1 untouched —
  `tests/test_rubric.py::TestZeroDiffFixture`.
- The Accurate floor fails closed to `"unverified"` when V1 is in
  binding-correctness mode — `tests/test_rubric.py::TestAccurateHardFloor`.

Run: `python3 plugins/report-regeneration/skills/report-gold-standard-rubric/tests/test_rubric.py`
