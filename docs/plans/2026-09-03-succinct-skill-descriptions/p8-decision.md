# P8 — RE-DECISION GATE — outcome (c): STOP

**2026-09-08.** Per `plan.md` §P8 ("the program may legitimately stop here"), this
document records the pre-committed decision now that P1 has closed and P2/P3 have
shipped (PR #1100, PR #1130).

## Stated deviation from P8's literal pre-build gate

`plan.md`'s P8 pre-build gate reads *"P7's acceptance tests are complete and written
up."* P7 (the top-decile LLM-rewrite wave) was never built — this decision is reached
**without** running P7, by direct application of P1's own pre-committed collapse rule
(`plan.md` §P1's outcome table: *"Null at adequate power ⇒ ... the program collapses
to linter + ratchet + the top-decile pass"*) combined with §2's RT-1 finding, which
`plan.md` states **outranks every phase**. This is a shorter path to the same
pre-committed outcome, not a different outcome — named explicitly so nobody reads this
as a silent reinterpretation of the gate.

## The two independent signals, both already pointing the same direction

1. **Claim 6 — inconclusive-by-construction, not null.** Per `p1-status.md`: the
   substitute-instrument pilot (30 dispatches, ~1.45M tokens, 5 independent
   trigger-construction methods) never established genuine base-case ambiguity for any
   tested pair, so no arm comparison was ever scored (`plan.md` AT-P1.1's own
   vocabulary). This is **weaker** ground for building the preservation apparatus than
   a null result would be — a null result means "we looked and found nothing"; this
   means "we never got the instrument to look with." Native `claude plugin eval`
   remains blocked by an account-level early-access gate this session cannot resolve.
2. **RT-1 — usage-gating CONFIRMED**, per `rendering-audit.md`: ~87% of
   `ravenclaude-core` skill descriptions render name-only in a fresh listing; only
   invoked skills render in full (3/3 tested, p ≈ 10⁻¹⁹ under independence against the
   ~13% base rate). `plan.md` §2 states this finding **outranks every phase below it**.
   It directly satisfies P8 outcome (c)'s stated condition: *"the injected subset is
   small (RT-1 confirmed) ... the effect does not justify 600+ files."*

Neither signal alone would be dispositive — an inconclusive instrument doesn't prove
the hypothesis false, and a confirmed-small injected subset doesn't by itself rule out
value in the ~13% that do render. Together they remove the two things that would have
justified building P4–P10: a validated effect size to protect (claim 6) and a
denominator large enough to make the protection worth its apparatus cost (the RT-1
finding narrows that denominator to ~13% of the corpus, non-stationary and self-erosive
per §2.2's endogeneity concern).

## Decision: outcome (c) — STOP

**Ship the linter + ratchet as the complete deliverable.** Per `plan.md`'s own
sentence for this outcome: *"linter + ratchet + top-decile trim is the subset of this
program that survives RT-1 being true."* **The top-decile trim is deliberately not
executed as a semantic LLM rewrite** (that is P7, gated behind the very apparatus this
decision declines to build) — running P7 without P4–P6's eval ladder would mean
rewriting 95 files' worth of disambiguation-bearing descriptions with no instrument to
detect a routing regression, which is precisely the failure mode (`NOT for X → Y`
clause deletion) the whole plan's executive summary names as the risk the design is
built around. The mechanical linter (`check-skill-descriptions.py`) has already been
run against the live corpus (2026-09-08): 594 informational findings, ratchet clean,
zero live silent-truncation bugs remaining beyond the two already fixed in PR #1100
(both were unquoted plain scalars; every colon-space finding spot-checked this session
is inside an already-quoted value and is not a live bug — see below).

**What shipped (merged, distributed):**
- **P0** — the corpus baseline instrument (`skill-description-baseline.py`), the
  rendering audit (usage-gating confirmed), claim-4 settled (`claude plugin details`
  scopes to one installed plugin). PR #1100.
- **P2** — the style contract (`docs/best-practices/skill-description-style.md`), the
  category classifier, the deterministic linter (`check-skill-descriptions.py`,
  Gate 281 — renumbered from 280 at merge time). PR #1130.
- **P3** — the budget artifact + ratchet (`description-budget.json`, seeded at the
  measured corpus total, OR-not-AND gate condition, append-only raise log). PR #1130.

**What was deliberately NOT built, and why:**
- **P1's full native-instrument study** — blocked on an Anthropic account-level
  early-access gate this session cannot resolve; the substitute pilot's
  pre-registrations and trigger examples remain reusable if access is ever granted.
- **P4 (golden set), P5 (eval harness ladder), P6 (calibration/MDE)** — the apparatus
  that would validate a semantic rewrite is safe. Building it now, with claim 6
  unresolved, would be building an expensive instrument to protect an effect nobody
  has measured.
- **P7 (Wave 1 LLM rewrite)** — gated on P6; not attempted. Doing the semantic rewrite
  without the eval ladder is the specific hazard §2 of `plan.md` names.
- **P8's own further branches (a)/(b)**, **P9 (`ravenclaude-core` pilot)**, **P10
  (mass rollout)** — all downstream of P7.
- **P11 (standing gate promotion to a required check)** — its own pre-build gate
  (G-P11.1) requires "wave 1 merged," which never happened. The linter (Gate 281)
  already exists as a non-blocking, always-on check on every PR; that is the
  deliverable this program produces for "new and edited skills stay within budget,"
  short of the originally-envisioned required-status-check promotion.
- **P12 (gate-registration discipline)**, **P13 (steady-state ops)** — both presuppose
  the wave rollout exists to operate.

## AT-P8.1 … AT-P8.4

- **AT-P8.1** — No wave-1 token measurement exists (P7 was not run), so this
  acceptance test does not apply in the form written; the applicable evidence is
  `rendering-audit.md`'s posture-named usage-gating measurement, cited above.
- **AT-P8.2** — Outcome (c), reasoning written above, before any further wave begins
  (none will).
- **AT-P8.3** — This section is the closing write-up; P1 returned
  inconclusive-by-construction rather than null, so AT-P1.5's literal sentence does not
  apply verbatim — its substance (apparatus dropped as unearned cost, program reduced
  to linter + ratchet) is restated above with the correct outcome label.
- **AT-P8.4** — This outcome was not chosen by inheriting `scope.md`'s original
  −30–50% target; no percentage target is claimed or met. The corpus's actual
  reduction is whatever P0's two live-bug fixes recovered (~412 chars / ~97 tokens),
  stated honestly as a bug fix, not a compression result.

## Definition of done

- [x] Decision recorded (this file) and cross-linked from `p1-status.md`.
- [x] What shipped vs. what was deliberately not built is stated.
- [ ] **Version bumps / gate registration / `/code-review`:** none — this phase ships
      no code (per `plan.md`'s own DoD for P8).
