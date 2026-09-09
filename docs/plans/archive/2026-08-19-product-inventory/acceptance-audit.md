# Acceptance audit — every phase's own criteria, with a verdict each

**Plan:** [`plan.md`](plan.md). Built in PR #1002 on top of Phase 0 (#998, #1000).

⛔ **A phase is not done because its code shipped. It is done when its own
acceptance list is satisfied, or the gap is named.** Three criteria below are
**NOT met**, and each says why in its own row rather than being quietly dropped.

**Suite state:** 915 gate assertions pass, 0 fail — locally and in CI, including
the macOS stock-toolchain run. Gates 236–243, each registered in the `--check`
dispatcher **and** the main sequence **and** the `Supported:` string, each with a
must-fail half, all eight confirmed in the suite output **by literal name**.

---

## P1 — Empirical spikes

| # | Criterion | Verdict |
|---|---|---|
| 1 | Four-row verdict table, command + literal output class each | ✅ [`p1-spike-verdicts.md`](p1-spike-verdicts.md) |
| 2 | S1 includes a file that **should** deny and does | ✅ `S1-C0` = DENY, asserted first |
| 3 | Line-offset rule + template recorded | ✅ [`inventory-authoring.md`](../../best-practices/inventory-authoring.md) |
| 4 | Apostrophe rule enforced mechanically | ✅ `audit-prose-rendering-path.py`, 199 shell files |
| 5 | **S2 dispatched in CI** | ⛔ **NOT MET — deliberately.** The workflow is authored and unrunnable-by-me: a dispatch is the owner's to trigger. Marked PENDING rather than inferred from a local `command -v claude`, which is evidence about this laptop. |

## P2 — Self-heal contract + collect-all

| # | Criterion | Verdict |
|---|---|---|
| 1 | S3's verdict reproduced, then shown fixed | ✅ `covers-digest-drift` FATAL → CONTINUE |
| 2 | Self-heal completes when the new check fails | ✅ Gate 236 runs the **workflow's own extracted block** |
| 3 | Collect-all proven with a dual-violation fixture | ✅ both classes + both markers |
| 4 | Registered in both, greped by literal name | ✅ |

## P3 — Staleness, both escapes

| # | Criterion | Verdict |
|---|---|---|
| 1 | Aged `ravenclaude-built` entry **warns** on PR, **fails** the sweep | ✅ + a control proving the two modes differ |
| 2 | Absent `last_verified` **fails** on PR | ✅ |
| 3 | Mutated covered artifact fails; `--restamp-cosmetic` clears the digest without moving the date | ✅ dated fixture proves the date did not move |
| 4 | 58 existing concepts still validate; registry additive | ✅ restated correctly — see the note below |

⛔ **Criterion 4 was mis-encoded and is now fixed.** It shipped as
`git diff --quiet -- concepts.json`, which is a true statement about **git**, not
about the schema: it measures *"is the working tree committed"* and goes red on
any mid-work run. It is now the real property — **a concept opting into none of
the new fields carries none of them in the registry** — which holds regardless of
what else the corpus contains.

## P4 — Path-keyed harness

| # | Criterion | Verdict |
|---|---|---|
| 1 | Resolver reproduces GT13's two findings + its negative control | ⛔ **NOT MET, AND UNMEETABLE.** GT13 does not reproduce: **0 of 2**. One target exists; the other is a backticked prose mention of a deliberately-removed file. Building a resolver to find two would be tuning a detector to a predetermined number. [`p4-harness-findings.md`](p4-harness-findings.md) §1 |
| 2 | Every class ships its control and it **demonstrably fires** | ✅ 7/7 via `--capping-table` |
| 3 | Neutering one runner's assertion makes the sweep fail | ✅ neutered `agent-static` on a copy → its control stops firing → `--capping-table` non-zero |
| 4 | Three counts from the independent census; a dropped concept does not move both | ✅ census 321 / enumerated 321, unmoved across drop and restore |
| 5 | The permanently-red canary is red | ✅ |
| 6 | Planted-secret `--must-fail` proves the scrubber bites | ✅ closed label vocabulary |
| 7 | Runners apostrophe-clean, mechanically greped | ✅ |

## P5 — Schema delta

All four met (Gate 239): corpus validates; a missing `nuance` fails with a
field-naming message; a pasted-output block is rejected by
`check-inventory-evidence.py`; **the R12 badge is asserted in the generated HTML**,
never in the generator source — a source scan is satisfied by the string being
*described* in a comment.

## P6 — Surfacing + budgets

| # | Criterion | Verdict |
|---|---|---|
| 1 | A synthetic +200-concept payload **fails** the ceiling; pristine passes | ✅ measured 30,993 vs ceiling 31,500; +200 entries → 37,793 = EXCEEDS. Headroom today: 507 elements ≈ 14 entries |
| 2 | A synthetic +5 MB dashboard fails the byte ratchet | ✅ teeth push the ceiling below measured in **both** dimensions |
| 3 | A deliberately-broken render **fails** the changed-concepts gate | ✅ broke `agent-harness-loop`'s diagram in a throwaway clone → exit 1, never a warning |
| 4 | All four strength badges render in a fixture set | ✅ |

## P7 — Nuance gate

Floor accepts **12/12** measured positives and rejects **12/12** negatives; the
per-negative disposition is printed honestly (rejected-by-F1 / caught-only-by-B2 /
passed-uncaught). `--must-fail-convention` is compared against the observed exit by
a shared auditor helper. `coverage --check` blocks a missing sample and a 60%
batch, and passes a 100% one.

⛔ **Criterion 2 is met in the honest direction:** one adversarial negative
(`adv-token-dense-truism`) **passes the floor uncaught** and is **named on every
run**. That is the measured gameability of a cheap floor, reported rather than
tuned away — if that list ever reads empty, the floor has been fitted to its own
fixtures, which is the fake metric R7 forbids.

## P8 — Inception ratchet + merge-time re-measure

All five met, including the PR #991 shape reconstructed deliberately in a scratch
repo (a foreign SHA fails, an absent SHA fails as UNKNOWN, a correctly-stamped one
passes) and the `paths:`-filter assertion — which is scoped to the
**`pull_request`** trigger only, after its first version produced two false
positives (a deliberate `push:` filter, and a comment *saying* the words).

## P9 — Wave 1

| # | Criterion | Verdict |
|---|---|---|
| 1 | All entries pass `--check` and the nuance floor | ✅ 12 |
| 2 | `verify.tier != none`, or a written rationale | ✅ 10 + 2 rationales |
| 3 | The judge labels ≥18/20 as `nuance` | ⛔ **NOT MET — cannot run.** The judge reports `judge-uncalibrated` here and therefore emits **no verdicts**. That is the designed behaviour, not a pass. |
| 4 | Sampled review ≥80%, verdicts in the committed ledger | ⛔ **OPEN BY DESIGN — the one human step.** See below. |
| 5 | Render with no hand edit to `dashboard.html`/`concepts.json` | ✅ both regenerated |
| 6 | 3-skill transferability test recorded with a literal verdict | ✅ **2 of 3 transfer** — [`p9-wave1-record.md`](p9-wave1-record.md) §3 |

⛔ **12 entries, not ~20.** Twelve are what this session actually measured to the
N1/N2/N3 bar. Authoring eight more would have meant writing to a number instead of
to evidence — the exact failure the project exists to prevent. The ratchet makes
twelve a legitimate stopping point rather than an abandonment.

## P10 / P11

All met. The sweep is unrequirable **by construction** (no `pull_request` trigger,
asserted structurally with a control fixture that *does* carry one), the health
card is asserted in the generated page, and claim 5 is re-measured at **47 hooks**
with the counting rule written into the script — the rule being the deliverable,
the number being downstream of it.

---

## ⛔ The three open items, in one place

1. **S2 CI dispatch** (P1) — owner-triggered. Either answer activates a lane; no
   phase is cancelled.
2. **The calibrated judge** (P9) — reports `judge-uncalibrated`, emits no verdicts.
   Gated on S2's answer via the §7.4 substitute ladder.
3. **The fresh-context sampled review** (P9) — **the only one that blocks
   anything**, and it blocks batch **N+1**, not this batch. Grade the three
   sampled entries in `tests/fixtures/inventory-review-ledger.json`; ≥80% opens
   the gate.

None of the three is a defect. Each is a place where the plan says a human or a
model call is required, and the mechanism reports that requirement rather than
papering over it — which is the whole thesis.
