# Phase 11 — rollout runbook

The measured-rollout half of `verify-before-assert`. Everything here is gated on
evidence that does not exist yet, so this file states the conditions rather than
declaring them met.

---

## 0. What shipped, and what it is worth today

| phase | state | gate |
|---|---|---|
| 0, 2, 3 | shipped earlier (#989, #991, #1006) | 232 / 233 / 235 |
| 2's missing SSOT | `knowledge/cause-taxonomy.md`, 34/34 parity | `--check-doc` |
| 1 | replay corpus + rule measurement | 244 |
| 4 | pre-flight review, one measured rule | 244 |
| 5 | remediation gate — the primary D1 surface | 245 |
| 6 | closure gate | 246 |
| 7 | cross-host projection, honest cells | 247 |
| 8 | portable text floor | 248 |
| 9 | outcome eval | 249 |
| 10 | anti-rot | 250 |

All four knobs ship at **`warn`**. Nothing blocks.

---

## 1. Posture seeding — the CE-6 fix, and why it was needed

Every hook no-ops entirely when its posture key is missing. Both design panels
planned a consumer rollout with **no step that writes those keys**, which would
have shipped a mechanism that is off by default in exactly the repos where the
complaint is newest.

control: before this phase, `grep -cE 'cause_(triage|preflight|remediation|closure)'`
returned **0** against both this repo's own `.ravenclaude/comfort-posture.yaml`
and `templates/comfort-posture-balanced.yaml`; after seeding it returns 4 for
each. The mechanism was inert, and the count is the difference.

⛔ **Seeding alone was not enough.** `emitYaml()` rebuilds the whole posture from
the dashboard's in-memory state, so a top-level key with no state slot is
silently deleted on the next Save & apply — the v0.61.0 data-loss class that has
already eaten `runaway`, `decision_review`, `definition_of_done`,
`stream_classify` and `context_handoff` in turn. The four `cause_*` knobs are
therefore modelled in the serializer (state + hydrate + emit, no DOM control),
and so is **`probe_validity`**, which was already live in this repo's posture and
already exposed to exactly that loss.
control: Gate 35 Test 7 asserts all five survive emit/hydrate; stripping the emit
block from a copy of the dashboard turns it red (exit 1) while the real one exits 0.

---

## 2. The `block` flips — conditions, none of which are met

`cause_remediation: block` and `cause_closure: block` may be set only when **all**
of the following hold. They are listed so the decision is checkable rather than
remembered.

1. **Phase 9's DBR gate passed** — with-hook DBR ≥ **0.8122** (frozen baseline
   0.6622 + the 0.15 delta), measured over ≥500 Bash envelopes with a
   *with-hook / without-hook* arm alternating by session.
2. **Live fire count is single-digit per active repo.**
3. **Hand-classified false-positive rate ≤ 10%** for the knob being flipped
   (the stricter bar, because this path can block).
4. **No session shows a `blind` event without a paired advisory.**

⛔ **This prohibition is mechanized, not exhorted.**
`check-cause-eval.py --check` reads the seeded postures and FAILS if either
blockable knob is set to `block` while the with-hook arm is `[unverified]`. Its
`--must-fail` half drives a temp posture set to `block` and requires the finding,
and an all-`warn` temp posture and requires silence — so a red verdict is not
ambiguous.

### Why the arm does not exist yet

control: a search for a two-arm artifact returned only substring false positives
(`dbre-*`, `extend-with-hooks`) while the same search located `corpus.jsonl`, so
the probe could return something. And until this phase the live posture set **no**
`cause_*` key at all, so an off-vs-warn alternation would have read the same
default on both arms and measured nothing. Seeding is what makes the arm
*possible*; it does not make it *done*.

---

## 3. ⛔ The ship gate was unsatisfiable as written, and that is now pinned

The plan's gate is `DBR(with-hook) ≥ DBR(without-hook) + 0.15`. It never says what
counts as "a discriminating probe", and the gate's satisfiability turns entirely
on that unspecified choice:

| definition | baseline | +0.15 reachable |
|---|---|---|
| any read verb (the natural reading) | 0.9757 | **no — needs 1.1257** |
| control-shaped (pinned) | 0.6751 | yes |
| explicit control markers only | 0.0334 | yes, but ~always 0 |

control: one corpus, one remediate predicate, only the discriminate predicate
varied — so the spread is the definition and not a different sample.
`check-cause-eval.py --baseline` regenerates the first two rows, so this table can
be checked rather than trusted.

Agents overwhelmingly *do* read again before remediating, so under the natural
reading the metric is saturated and no hook could move it. A gate nobody can pass
is not a high bar — it is a mechanism permanently stuck at `warn`.

---

## 4. Re-measure live; do not tune

Phase 1's corpus was produced by the **un-instrumented** agent. Its fire rates are
**pre-registration thresholds, not predictions** — the agent adapts to the hook,
and adaptation is the point.

⛔ A rule exceeding its false-positive ceiling on live data is **removed, not
tuned**. The precedent is `guard-probe-validity.sh`, where two sibling rules were
measured and rejected rather than softened.

---

## 5. Decommission criterion

If after two review cycles the DBR delta (with-hook minus without-hook) is below
**+0.15**, the mechanism is not changing behaviour. The correct response is to
narrow it further or remove it — **never to make it louder**. A guard nobody reads
is a guard that gets switched off, so this plan carries its own off-ramp in a
metric it can actually measure.

---

## 6. Still owed

- **A version bump.** The plugin cache is keyed on the `version` string, never a
  content hash, so none of Phases 1–11 reaches an installed session without a
  bump + `sync-plugin-versions.py` + `generate-copilot-plugin.py`.
- **The owner ruling the plan asks for:** default-on vs opt-in for consumer repos.
  What shipped is the conservative reading — seeded at `warn` in this repo and in
  the balanced template, inert where neither is present.
- **`check-durable-predicate-parity.py`**, declared as a follow-up rather than
  claimed: the durable predicate inside `guard-premise.sh` is not an extractable
  list, so a byte-parity check across the two shapes would likely pass vacuously.
  The honest form is behavioural parity over a shared path fixture.
- **The three new hooks have never fired in the live substrate.** The fired-count
  audit reports a GAP: `triage-outcome.sh` 2,670 fires against 0 for each of the
  three, in the same window. That is expected — they are registered in this branch
  while the running session uses the installed cache — and it is exactly what the
  version bump above resolves.
