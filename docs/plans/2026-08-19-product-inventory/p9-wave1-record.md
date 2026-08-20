# P9 — Wave 1: 12 mechanism entries, and the transferability verdict

**Phase 9 of** [`plan.md`](plan.md). `depends_on_claims: [6, 7, 8, 9, 10, 11]`

---

## 1. What shipped

**12 mechanism entries covering 69 of 319 artifacts (22%).** The unit is the
mechanism, not the file — the largest entry, `hook-message-channels`, lists **47
paths** in `covers[]` because the two-channel fact is true of every hook at once.
Writing it into 47 entries would write one fact 47 times.

| Entry | covers | verify |
|---|---|---|
| `hook-message-channels` | 47 | effect / executed |
| `must-fail-conventions-diverge` | 14 | effect / executed |
| `islanded-panel-costs-two` | 5 | effect / executed |
| `plugin-cache-is-version-keyed` | 3 | reachability / static |
| `selfheal-greps-a-sentence` | 3 | effect / executed |
| `census-must-be-independent` | 3 | effect / executed |
| `tprose-screens-edits-too` | 2 | effect / executed |
| `frontmatter-date-is-a-certainty-stamp` | 2 | effect / executed |
| `staleness-double-exemption` | 2 | effect / executed |
| `probing-a-script-runs-it` | 2 | effect / executed |
| `hook-emitter-collision` | 2 | **none** + rationale |
| `bash-tool-response-has-no-exit-code` | 1 | **none** + rationale |

Every nuance was **measured in this session**, and each carries the control that
would have come out differently had the claim been false. They are the same twelve
facts frozen in `tests/fixtures/inventory-nuance-golden.json`.

⛔ **12, not 20.** The plan budgeted ~20. Twelve are what this session actually
measured to the N1/N2/N3 bar. Authoring eight more would have meant writing to a
number instead of to evidence — which is the failure the project exists to
prevent. The ratchet makes twelve a legitimate stopping point rather than an
abandonment.

---

## 2. ⛔ The one gate that is RED, deliberately

`inventory-coverage.py --check` **BLOCKS**:

```
x batch wave-1: reviewer_context is not 'fresh' — a reviewer who authored
                the batch reviews their own summary
x batch wave-1: 3 sampled but only 0 graded
```

**This is the mechanism working, not a defect.** These entries were authored by
the same session that built the gate. Recording that session as a fresh-context
reviewer would be exactly the self-review the ledger exists to prevent, so
`reviewer_context` reads `not-fresh` and `verdicts` is empty.

The plan says this directly: *"It does not make the nuance bar machine-checkable
end to end… There is a required human/fresh-model step and it is the real gate."*

**To clear it:** a reviewer with no memory of the authoring session grades the
three sampled entries in `tests/fixtures/inventory-review-ledger.json` against the
one-question rubric, then sets `reviewer`, `reviewer_context: fresh`, and the three
verdicts. At or above 80% the gate opens.

⛔ This is not ceremony: `check-nuance-floor.py --golden` reports every run which
adversarial negatives cleared the deterministic floor **uncaught**. Those are
caught only here.

---

## 3. ⛔ The 3-skill transferability test — literal verdict

§11.4: *"Author 3 real entries for 3 skills before authoring 54… If a competent
author cannot produce a genuine counterfactual for 3 skills, the standard does not
transfer, and the plan should know that in week 1."*

**Verdict: 2 of 3 transfer. 1 does not.** Recorded per skill:

| Skill | Counterfactual (N1) available? | Verdict |
|---|---|---|
| `probe-kit` | **YES.** A reader assumes a `file` negative licenses *"it was never created"*. The discriminator is in the skill own table: a wrong cwd and a permission-denied traverse **read identically**, so the negative licenses only *"this process, this uid, this cwd could not stat this path"*. Consequence: an absence conclusion drawn from it is unlicensed. | **transfers** — N1/N2/N3 all present, and mechanism-bearing |
| `spec-reread-ritual` | **YES, but the evidence is external.** A reader assumes spec drift is occasional; the measured finding is **11/11 sessions, 0% format exact-match**. That is a genuine counterfactual, but it is a cited external study, not a mechanism observable in this repo. | **transfers as `verify.tier: none`** with a written rationale — honest, and weaker than an effect entry |
| `wall-handling` | **NO.** Its trigger thresholds (same tool+error 3+, one-attempt TS failure) are stated in its own 300-char description, so a nuance restating them is derivable from title + summary by construction. The underlying claim — agents push forward through impossible tasks — is a documented behavioural finding about agents, not a non-obvious mechanism of this artifact. | **does not transfer** — an honest summary entry at `verify.strength: static` is the correct outcome |

**What this means for the remaining 54 skills.** The bar was drawn from hooks —
the one artifact class with a machine-readable contract with a host process — and
generalised to four classes without test. It **partially** transfers: skills whose
value is a *measured constraint* (`probe-kit`) carry a real counterfactual; skills
whose value is a *behavioural discipline* (`wall-handling`) do not, and forcing one
would manufacture the restatement the project exists to prevent.

⛔ **This is a legitimate outcome, not a failure** — the plan says so in advance.
Those skills get honest summary entries at `verify.strength: static`, and the
`Findable` badge renders that limit to the reader rather than hiding it.

---

## 4. ⛔ A measured correction to risk X8

The plan X8 projected *"~90,000 elements injected into the DOM on one tab click"*
for 162 entries, derived from the Learn tab ~411 elements/concept.

**Measured: 34 payload elements per inventory entry** — 408 for 12 entries.
Projection to a 162-entry corpus: **~5,508 elements, not ~90,000.**

The difference is entirely the **diagrams-opt-in decision** (R2 corollary, P6.2):
an inventory entry ships no mermaid block, so it costs an order of magnitude less
than a Learn-tab concept. Bytes behave the same way — ~6 KB/entry, projecting to
~1 MB rather than the 8-12 MB feared.

⛔ The budget was still the right thing to build. It is what **measured** this, and
it caught the wave-1 batch on the author machine before any PR. But X8 magnitude
was an over-estimate, and the number is now bound to a gate that reports the
per-entry cost and the projection on every run.

---

## 5. The regeneration chain, wrapped

`scripts/regen-inventory.sh` runs the four steps in order —
`concepts.py` -> `render-concepts.py` (opt-in) -> `generate-dashboards.py` ->
`generate-index-dashboard.py` — then **re-checks the budgets**. Twelve batches
times four manual steps is 48 chances to regenerate out of order, and a stale
generated artifact reddens CI for the right reason in a way that looks like the
wrong reason.

⛔ Its render step is **skipped by default and says so loudly** — a skip is not a
pass, and diagrams are opt-in per entry.

---

## 6. Drift caught, and settled honestly

Editing a covered artifact after stamping tripped the digest tripwire **six times**
during this phase — each time correctly. Each was cleared with `--restamp
--reason` (substantive: the claim was re-read and re-confirmed), never
`--restamp-cosmetic`, and every one is recorded in
`tests/fixtures/inventory-restamp-log.jsonl` with both digests.

That log is what `coverage --report` reads to surface the **unchanged-nuance
ratio** — the rubber-stamp tell.

---

## 7. Acceptance — P9

- [x] All 12 pass `concepts.py --check` and the nuance floor.
- [x] All 12 have `verify.tier != none`, **or** a written rationale (2 carry one).
- [ ] The judge labels >=18/20 as `nuance` — **cannot run**: the judge reports
      `judge-uncalibrated` in this environment and therefore emits **no verdicts**,
      which is the designed behaviour, not a pass.
- [ ] The sampled review scores >=80% and its verdicts are in the committed ledger —
      **deliberately open**, see section 2.
- [x] They render with **no hand edit** to `dashboard.html` or `concepts.json` —
      both regenerated, and the R12 badge asserted in the generated HTML by Gate 240.
- [x] The 3-skill transferability test is recorded with a literal verdict (section 3).
