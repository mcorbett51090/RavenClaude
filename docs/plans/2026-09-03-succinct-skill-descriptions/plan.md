# plan.md — Succinct skill descriptions, marketplace-wide

**Gate:** G6 (synthesis) · **Status:** authoritative · **Date:** 2026-09-03
**Run dir:** `.ravenclaude/runs/forge/succinct-skill-descriptions/`
**Inputs merged:** `scope.md`, `claims-table.md`, `plan-A.md`, `plan-B.md`, `gap-delta.md`,
`critic-brief.md`, `tiebreaks.md`, `red-team.md`
**Binding authority:** every ruling in `tiebreaks.md` (T1–T5, m1–m10) is *folded into* the phases
below, not merely cited. Where a ruling amended a phase, the amendment is written into the phase
text and marked **[T-n]** / **[m-n]** / **[RT-n]**.

---

## 1. Executive summary

RavenClaude ships 946 `SKILL.md` files whose `description:` frontmatter totals ~308K characters
(three independent measurements: 310,359 / 307,672 / 308,229 — a 0.9% spread), and some subset of
that text is injected into every session's system context so the model can route to the right skill.
This plan builds a **procedure, not a cleanup**: a deterministic length/style linter, a
confusable-pair-heavy routing eval harness with a calibrated three-tier cost ladder, an
LLM-assisted rewrite engine sandwiched between deterministic pre- and post-validation, a
value-ordered waved rollout, and a standing CI gate (advisory-first, ratcheted, self-auditing) so
new and edited skills stay within budget going forward. The prize is context-budget headroom — more
plugins enabled before the orchestrator's token ceiling forces disabling them — and the risk the
whole design is built around is that the *most compressible-looking* text (the `NOT for X → Y`
disambiguation clauses) is the *least compressible-in-fact*: it is the entire mechanism keeping
confusable sibling skills apart, and a naive length optimizer deletes it first. Accordingly the plan
front-loads evidence over apparatus: it settles what actually reaches context, sizes the effect
shortening has on routing before building any machinery to protect against it, and starts with a
**95-file top-decile pass** rather than a 946-file rewrite — with an explicit, pre-committed
re-decision gate at which stopping is a legitimate outcome.

---

## 2. ⛔ Before you build anything — RT-1 is the #1 open risk and it is UNMITIGATED

> **This section outranks every phase below it. Do not authorise P1 or anything after it until the
> probe in §2.3 has been run and its answer written into `scope.md` and `description-baseline.json`.**

### 2.1 The finding, stated as observed

**Source:** `red-team.md` RT-1 (severity **HIGH**, marked **⛔ NO — unmitigated, no waiver
available**), extending `critic-brief.md` §1/C1 and §4/X1.

Two independent subagent sessions cross-read the on-disk `description:` field of
`plugins/ravenclaude-core/skills/*/SKILL.md` against **their own injected "available skills"
listing** and got the *identical* split:

| probe | result |
|---|---|
| `critic-brief.md` p1–p2 | 59/59 `ravenclaude-core` skills carry a non-empty on-disk `description:`; **10 of 59 render a description in the listing; 49 render name-only** |
| `red-team.md` q2 | same corpus, different subagent session, **same 10/59 split** ⇒ deterministic, not sampling noise |
| `critic-brief.md` p3 / `red-team.md` q3 | user-level `~/.claude/skills/` Cloudflare family: **4 of 11 render**; the 4 are exactly the first four alphabetically; all 11 have real on-disk descriptions |
| `critic-brief.md` p4 (**positive control**) | in the *same* system prompt, the **agent** listing renders a description for ~150/150 agents. The probe can see descriptions where the harness emits them — the empty result on the skill side is a genuine negative, not a blind probe |
| whole-listing eyeball | roughly **43 of ~330 entries (~13%)** carry description text |
| `red-team.md` q6–q7 | 5,763 transcripts scanned for `tool_use name == "Skill"` → 24 distinct skills, 49 invocations. **22 of 22** installed skills with any invocation history render their description. **Zero exceptions**, against a ~13% base rate (p ≈ 10⁻¹⁹ under independence) |

**Nine hypotheses tested and rejected across the two gates:** description length, prefix/ordinal
cutoff, frontmatter shape (present/absent), recency, YAML scalar style (plain vs quoted vs block),
and plugin-cache staleness (cached `ravenclaude-core/0.316.2` descriptions are **byte-identical** to
the repo tree; 0 differing).

### 2.2 Why this is the #1 risk — and why it may make the savings partly ENDOGENOUS

Stated as an **inference**, per this repo's Claim Grounding rule — the cause is *not* isolated:

1. **The baseline may be denominated on bytes that never reach the model.** If ~87% of descriptions
   render name-only, then the corpus total (~308K chars) is not the injected cost, and the
   per-turn token savings from shortening **all 946** descriptions is materially smaller than the
   raw corpus size implies. For the name-only majority, shortening saves **zero injected tokens
   today**.
2. **The savings may be partly self-eroding.** The 22-for-22 correlation with invocation history is
   consistent with **usage-gated** rendering. If that is the mechanism, then a rewrite that
   *succeeds* — better descriptions → more accurate routing → more invocations → more descriptions
   promoted into the rendered set → **more injected bytes**. Success and the success metric point in
   opposite directions. **Neither plan-A nor plan-B models any feedback loop between the
   intervention and its own denominator.**
3. **Four load-bearing design elements measure a listing production does not render**
   (`red-team.md` §2): plan-A's `--posture`-rendered listing (the T0/T1 input — posture is *enabled
   plugins*, and all 59 `ravenclaude-core` skills are enabled while only 10 render, so the object
   A specifies is not a stable function of posture); plan-A's corpus-total ratchet denominator;
   plan-B's captured-listing fixture (its Phase 0 deliverable 2, which is a snapshot of *one user's
   invocation history at one instant* and drifts every time a skill is used); and plan-B's
   headline requirement that each eval case be embedded in a full-size ~946-entry
   all-descriptions listing — which biases every measurement in the **optimistic** direction, and
   which B has pre-defended as "the single most important design decision in this phase", so the
   error will be argued for.
4. **Only the linter survives RT-1 being true.** `red-team.md` §2 is explicit: the gate design
   degrades gracefully in exactly one respect — the linter is a pure on-disk check and stays valid
   regardless. **Linter + ratchet + top-decile trim is the subset of this program that survives
   RT-1.**

### 2.3 The required probe (minutes, not days) — a harness-rendering audit

This is `critic-brief.md` §1's probe **plus** `red-team.md` RT-1's second, discriminating arm. Run
both arms; a single arm cannot separate the causes.

| arm | procedure | what it discriminates |
|---|---|---|
| **A — surface** | Capture the "available skills" block from a **main interactive session** (not a subagent), current posture. Diff the set of entries carrying description text against the on-disk corpus for the same posture. | **Class F** (subagent listings assemble differently — the plans' baseline survives *for main sessions only*, and subagent spend must be modelled separately) vs **Class H** (the harness selects, and the baseline is wrong everywhere). |
| **B — usage-gating** | Then **deliberately invoke 3 skills that have never appeared in the invocation set** (`red-team.md` q6's 24), start a **fresh** session, and re-capture. **Diff membership, not format.** | If those three now render, **usage-gating is confirmed**, G0 must be reopened with an explicit model of the injected subset *including its non-stationarity*, and the endogeneity in §2.2(2) is real rather than hypothetical. |

### 2.4 Standing constraints until the probe is answered

- **No phase may denominate savings in corpus chars.** (`red-team.md` RT-1 mitigation 3.)
- **No PR body, docs artifact, or plan output may state a marketplace-wide token saving.** The
  honest headline shape is "saves X tokens/turn *in this posture, for the descriptions actually
  rendered*", never "saves 78K tokens".
- **P8's re-decision gate is the natural stopping point** if the injected subset turns out to be
  small. `tiebreaks.md`'s Standing note says this plainly: *"T2's re-decision gate is where the
  program most plausibly stops, and that is a legitimate outcome, not a failure of this run."*
  This document is written so that outcome is expressible — see §7 P8's outcome (c).

**Recommendation:** run the §2.3 audit before committing to full-corpus rewrite economics. It costs
minutes; the cost of being wrong is the entire program.

---

## 3. Reconciled dependency DAG

Every `tiebreaks.md` verdict is reflected in the shape below, not merely referenced.

```
                    ┌─────────────────────────────────────────────┐
                    │ P0  Rendering & unit audit (THE PREMISE)     │  ⛔ blocks everything
                    │  RT-1 probe · tokenize · posture pin ·       │
                    │  claim 4 · scope.md amendment · baseline     │
                    └───────────────────────┬─────────────────────┘
                                            ▼
                    ┌─────────────────────────────────────────────┐
                    │ P1  Claim-6 effect-size study  [T3]          │  early, NON-CITING
                    │  3 arms × ~40 skills, pre-registered,        │  ⇒ gates whether the
                    │  claude plugin eval, ablation pre-flight     │     preservation apparatus
                    │  [T1#2], positive control [RT-1]             │     is ever built at all
                    └───────┬───────────────────┬─────────────────┘
                            │                   │  (null ⇒ P2's preservation half,
                            │                   │   category budgets, exemplar bank
                            │                   │   and 2-category human review are
                            │                   │   DROPPED as unearned cost)
              ┌─────────────┼───────────────────┼──────────────┐
              ▼             ▼                   ▼              ▼
     ┌────────────────┐ ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
     │ P2 Style       │ │ P3 Budget    │ │ P4 Golden   │ │ P5 Eval      │
     │ contract +     │ │ artifact +   │ │ set  [m1,m2]│ │ ladder       │
     │ linter [RT-3,  │ │ ratchet      │ │             │ │ T0/T1/T2     │
     │ RT-8]          │ │ [T4, RT-2,   │ │             │ │ [T1, RT-1]   │
     │                │ │  RT-5]       │ │             │ │              │
     └───────┬────────┘ └──────┬───────┘ └──────┬──────┘ └──────┬───────┘
             │                 │                └────────┬──────┘
             │                 │                         ▼
             │                 │            ┌──────────────────────────┐
             │                 │            │ P6 Calibration + TEETH   │
             │                 │            │  S1/S2/S3 + S4 [RT-3]    │
             │                 │            │  + MDE  [RT-7]           │
             │                 │            └────────────┬─────────────┘
             └────────┬────────┴──────────────────────────┘
                      ▼
          ┌──────────────────────────────────────┐
          │ P7  WAVE 1 — top-decile only (95)    │  [T2, T5#1]
          │  full rewrite + 100% human review     │
          └───────────────────┬──────────────────┘
                              ▼
          ┌──────────────────────────────────────┐
          │ P8  RE-DECISION GATE (hard)  [T2#2]  │  ⇦ the program may legitimately STOP here
          │  3 pre-committed outcomes            │
          └───────────────────┬──────────────────┘
                     (a) proceed broadly │ (b) next decile only │ (c) STOP
                              ▼
          ┌──────────────────────────────────────┐
          │ P9  WAVE 2 — ravenclaude-core pilot  │  [T5#2]
          │  the procedure pilot, densest         │
          │  disambiguation load                  │
          └───────────────────┬──────────────────┘
                              ▼
          ┌──────────────────────────────────────┐          ┌──────────────────────┐
          │ P10 Waves 3+ — mass-ordered value,   │◄────────►│ P11 Standing gate    │
          │  cluster-overlap-ordered review depth│  overlap │  advisory → blocking │
          │  [T5#3,#4,#5] · wave runbook [RT-4]  │          │  [m3, T4, RT-2]      │
          │  derived ceiling [RT-5]              │          └──────────┬───────────┘
          └───────────────────┬──────────────────┘                     │
                              └──────────────┬──────────────────────────┘
                                             ▼
                              ┌──────────────────────────────┐
                              │ P12 Gate registration        │  [m8] — INCREMENTAL,
                              │  (audit-gates.sh, 3 surfaces)│  registered as each phase
                              └──────────────┬───────────────┘  lands, NOT batched here
                                             ▼
                              ┌──────────────────────────────┐
                              │ P13 Steady-state operations  │
                              │  recalibration · membership   │
                              │  canary [RT-1] · aggregate    │
                              │  drift tracker [RT-7b, B P8]  │
                              └──────────────────────────────┘
```

### 3.1 Blocking / parallelising rules

- **P0 blocks everything.** No settled rendering model, no honest denominator, no Δ, no claim.
- **P1 blocks P2's preservation half, P4's cluster weighting, and P7 entirely.** `tiebreaks.md` T3:
  *"this study runs **before** P4/P5 machinery is built, not after."* Both input plans put the
  apparatus before the evidence; this DAG inverts that.
- **P2 ∥ P3 ∥ P4 ∥ P5** once P0 and P1 land — four independent workstreams. P2's *linter* half
  (caps, filler, charset, ratchet check) does not depend on P1; only its **preservation** half does.
- **P6 requires P4 and P5** (a golden set with no harness, or a harness with no set, measures
  nothing). **P6 is the single highest-risk node** after P0/P1: if T0 fails the S4 keyword-tail
  corpus (`red-team.md` RT-3, and it is *expected* to), T0 is disqualified for the rewrite lane and
  the per-PR gate on rewrite PRs escalates to T1 or T2 at real cost.
- **P7 requires P2, P3, P6.** **P8 requires P7.** **P9 requires P8 = outcome (a) or (b).**
- **P11 may *start* (workflow skeleton, fire-logging, advisory delivery) in parallel with P10**;
  only its **promotion to blocking** depends on P10 being substantially complete.
- **P12 is not a terminal phase.** Per `tiebreaks.md` m8 / `gap-delta.md` §9, teeth tests register
  **as their phases land** — baseline determinism after P0, linter preservation after P2, the
  S2/S4 boundary corpora after P6 — rather than sitting unregistered through the entire rollout,
  which is exactly the window where a regression on that failure mode does the most damage.
- **Waves do not parallelise on the ratchet artifact.** `red-team.md` RT-5: N concurrent wave PRs
  each rewriting `description-budget.json` guarantee a conflict on every concurrent pair, and
  `rerere` can silently merge a stale ceiling. The fix — a **derived** ceiling that wave PRs never
  touch — is folded into P3 and P11.

**Critical path:** `P0 → P1 → P4 → P6 → P7 → P8 → (P9 → P10) → P11`.

---

## 4. Risk matrix

Taken from `critic-brief.md` §4 and `red-team.md` §1 **as written** — not re-derived, not re-scored.

### 4.1 Premise & instrument risk (`critic-brief.md` §4; Score = P × I)

| # | Risk | P | I | Score | Earliest discriminating probe |
|---|---|---|---|---|---|
| **X1** | **The injected listing does not contain most descriptions** (C1) — baseline, savings target and eval fixture all denominated on bytes not in context | 0.55 | 5 | **2.75** | Capture a **main-session** skill listing; diff entries-carrying-description against the on-disk corpus for the same posture |
| **X3** | **"Zero regression" is an underpowered null** (C8) — a real few-point degradation ships green | 0.55 | 4 | **2.20** | Compute MDE at planned N and σ **before** freezing thresholds; if MDE > tolerable effect, say so in the plan |
| **X2** | **Claim 6 is false or small** (C5) — the preservation apparatus is unearned cost | 0.40 | 5 | **2.00** | 40-skill × 3-variant `claude plugin eval` effect-size study, `tool_used: Skill` graders, `--ablation none` |
| **X5** | **T2 configured so the routing grader is excluded from the score** (C7) | 0.50 | 4 | **2.00** | Run one case with a `tool_used: Skill` grader under both `--ablation with-without` and `none`; compare reported score |
| **X6** | **Precision measured by a stated-preference proxy** (C4) — false-fire/abstention numbers do not transfer | 0.50 | 4 | **2.00** | Report **T1-vs-T2 abstention divergence as a named metric**, not folded into aggregate agreement |
| **X4** | **Benefit unquantified in the owner's units** (C2+C3) — chars ≠ tokens, and the tokens may be cache-reads | 0.65 | 3 | **1.95** | Tokenize the baseline once; state which of {$/turn, context occupancy, attention} is the goal |
| **X7** | **−30–50% is a requirement, not a variable** (C6) — 600+ files rewritten for a back half that may not be worth it | 0.60 | 3 | **1.80** | Land the top-decile-only pass first (95 files, ~10%), re-measure token impact, then decide |
| **X8** | **Rewrite quality drifts across 182 batches** | 0.40 | 4 | **1.60** | Per-batch rejection budget + early-vs-late batch judge comparison |
| **X9** | **Standing gate gets disabled** — repo history is explicit | 0.35 | 4 | **1.40** | Silence on unmodified `main` + pre-stated fire budget + self-demotion |
| **X12** | **Golden set echoes descriptions** — B has no leakage probe | 0.35 | 4 | **1.40** | Leakage probe: synthetic near-ceiling while human subset materially lower |
| **X10** | **Other hosts regress unmeasured** (C9) — Copilot CLI / Codex CLI receive the same bytes | 0.35 | 3 | **1.05** | Scope out **explicitly** with a reason, or add one Copilot-lane spot check per wave |
| **X11** | **Posture unpinned across baselines** (C11) | 0.45 | 2 | **0.90** | Pin the posture (plugin set + versions) inside `description-baseline.json`; fail on posture drift |
| **X13** | **Program cost unbounded** — both plans budget a *run*, neither the *program* | 0.45 | 2 | **0.90** | Multiply per-run cost by planned run count at synthesis time and put the number in the plan |
| **X15** | **Baseline decimal drift** (0.9%, three measurements) | 0.90 | 1 | **0.90** | One named measurement method emitted with the baseline artifact |
| **X14** | **Scope's motivation is about the wrong token pool** (C10) | 0.55 | 1 | **0.55** | Settle claim 4; amend `scope.md`'s Baseline paragraph |

**The critic's reading of this matrix, carried forward verbatim in substance:** the top of the board
(X1, X3, X2, X5, X6) is dominated by **premise and instrument-validity risk, not execution risk** —
and every one of the top five is answerable by a probe measured in **hours**, before a single phase
is authorised. Both input plans allocated their heaviest machinery to the middle of the board
(X8, X9, X12). *"X1 and X2 must be settled first or the rest is scaffolding on an unverified
foundation."* This plan's P0/P1 ordering exists to honour that.

### 4.2 Execution risk (`red-team.md` §1 severity board)

| # | mode | severity | mitigated? | where mitigated in this plan |
|---|---|---|---|---|
| **RT-1** | Injected set small/selective/usage-gated; savings metric endogenous | **HIGH** | **⛔ NO — unmitigated, no waiver.** Probe is minutes; must be settled pre-synthesis | §2 + **P0** |
| **RT-2** | Ratchet gameable **across PRs** (pad back up after a shrink; A's AND-condition never fires on under-cap growth) | **HIGH** | ✅ `OR`-condition + committed ceiling + **two-PR** teeth test | **P3**, **P11** |
| **RT-3** | Rewriter games T0/linter via a **keyword tail**; T0 is the rewriter's own objective used as its examiner | **HIGH** | ✅ S4 sabotage corpus + structural preservation check + quarantined human subset | **P2**, **P6** |
| **RT-4** | `audit-gates.sh:2242` `git checkout --` reverts uncommitted version bumps ⇒ merged-but-undistributed rewrite (cache is version-keyed; *merged ≠ live*) | MED-HIGH | ✅ ordered wave runbook + per-plugin bump assertion | **P10** |
| **RT-5** | Parallel waves conflict on the ratchet artifact; `rerere` can pick a stale ceiling | MEDIUM | ✅ derive the ceiling; serialise only budget-change PRs | **P3**, **P10** |
| **RT-6** | Advisory hook absent in the rewrite context; substrate guard blocks a rewriter placed under a plugin's `scripts/`; 3 hosts, 1 measured router | MEDIUM | ✅ partial — (1)(2) mitigated in **P7**/**P11**; **(3) explicit accepted-risk waiver — see §6** | **P7**, **P11**, **§6** |
| **RT-7** | "Zero regression" underpowered at planned N; the blocking set collapses to never-flipping cases at 3σ | MEDIUM | ✅ MDE before thresholds; import B's aggregate drift tracker; **growing** cross-wave regression core | **P6**, **P10**, **P13** |
| **RT-8** | Descriptions feed generated artifacts (portal `index.html`, `generate-copilot-plugin.py`); YAML-hostile rewrite output blocks whole-tree `prettier --check .` for everyone | LOW-MED | ✅ wave checklist + charset round-trip teeth test | **P2**, **P10** |

---

## 5. Alternatives

### 5.1 The scope-shape decision — top-decile-only pilot vs full-corpus rewrite

**This is the alternative neither input plan had.** `critic-brief.md` C6/X7: both plans accepted
`scope.md`'s −30–50% as a **requirement**, so *"how much of the corpus to touch at all"* never
appeared as a decision with alternatives — A's D3 alternatives are four *cap shapes*, B's Decision 3
alternatives are three *budget shapes*.

Measured over n=946, total 308,229 chars (`critic-brief.md` p5/p10):

| lever | files touched | blast radius | chars saved | % of corpus |
|---|---|---|---|---|
| **trim top decile only to p75 (400)** | **95** | **10%** | 30,518 | **9.9%** |
| cap at 400 | 237 | 25% | 40,929 | 13% |
| cap at 300 | 422 | 45% | 73,419 | 24% |
| cap at 250 | 561 | 59% | 97,811 | 32% |
| cap at 200 | **699** | **74%** | 129,556 | **42%** |

The top decile is 22.2% of corpus mass; the bottom half (≤ median) is 31%. **To reach −30% you must
rewrite the median, already-well-formed description** — where the signal-to-filler ratio is worst
and the risk/benefit is poorest.

| option | trade-off |
|---|---|
| **A. Full-corpus rewrite to a −30–50% target** | Hits the scope's stated number; requires touching 600–700 files, i.e. 6× the blast radius of the defensible core, with the marginal files being the ones where compression is least justified. Combined with RT-1 (the injected cost may be a fraction of 308,229) and C3 (the saved tokens may be cache-reads at ~0.1× list price), the back half's value is **unproven**. |
| **B. Top-decile-only pass, then re-decide** ✅ **[T2 — SYNTHESIS/wave-1]** | 95 files for ~10% of corpus mass at ~10% blast radius. 95 files is a number a human genuinely reads, which makes plan-B's "a human reads every rewritten description" affordable at pilot scale and defers the question of whether it can ever be relaxed instead of answering it from fatigue. Buys the cheap 10% first and re-decides with real numbers. |
| **C. Do nothing but ship the linter + ratchet** | The subset that survives RT-1 being true (`red-team.md` §2: the linter is a pure on-disk check and stays valid regardless). This is P8's outcome (c) and it is a **legitimate landing**, not a failure. |

**Ruling adopted (`tiebreaks.md` T2, verdict SYNTHESIS):** *"plan.md's first mutating phase is the
top-decile-only pass, and −30–50% is demoted from a requirement to a variable re-decided after it."*
Three consequences written into the phases:

1. **Wave 1 = the 95 top-decile files, cross-plugin**, given the *full* treatment (rewrite + linter
   + eval + 100% human review). — P7.
2. **A hard re-decision gate after wave 1** measuring **realised token impact, not char impact**,
   with three pre-committed outcomes. — P8.
3. **The top decile is disproportionately the `router` category.** `claude-api` and its shape are
   trigger tables that are *legitimately* long. Wave 1 is explicitly **not** "mechanically trim to
   p75" — some files will correctly come out barely shorter, and any file that legitimately cannot
   compress is recorded as a **declared, reasoned exemption**, not as a failure. — P7.
4. **Target restated in this plan's own words:** *"−30–50% of corpus chars"* becomes **"a measured
   reduction, in the unit chosen in P0, re-decided after wave 1."** Do not carry an inherited
   percentage into a PR body as a commitment.

### 5.2 Eval-tier architecture — `tiebreaks.md` T1 (SYNTHESIS)

| option | trade-off |
|---|---|
| **A. plan-A's three-tier ladder** (T0 retrieval proxy → T1 single-shot router → T2 `claude plugin eval` as ground truth + calibrator) | Cost matches consequence; T0's authority is *borrowed* from T2 and expires. Requires maintaining three instruments and proving T0↔T2 agreement. |
| **B. plan-B's single bespoke harness** (functionally A's T1) | One thing to build; but it is simultaneously its own cheapest and most expensive instrument, with **nothing to calibrate against**, and B never evaluated `claude plugin eval` at all — a blind spot, not a considered rejection (B drafted before reading A). |
| **C. Adopt A's ladder with a corrected T2 mode + B's best import** ✅ **[T1]** | |

**Adopted, with all five T1 amendments folded into P5/P6:**

1. **T2 runs under an ablation mode that *scores* the routing grader.** `claude plugin eval --help`
   states that under `--ablation with-without` (the default whenever a plugin resolves), graders
   marked with-only — *including* `tool_used: Skill` — are "a plugin-fired indicator rather than
   part of the score". A `--threshold` gate under that mode passes/fails on the *other* graders
   while the routing signal contributes nothing: a **silent-green shape** (`critic-brief.md` C7/X5).
2. **Pre-flight probe before T2 is trusted**, promoted to a pre-build gate: run one case carrying a
   `tool_used: Skill` grader under both `--ablation none` and `--ablation with-without`; compare the
   *reported score*. Identical score ⇒ the grader is not contributing, settled empirically rather
   than from help text.
3. **Import from B:** each case's candidates embedded in a **realistic listing** rather than a toy
   pairwise choice — B's single best contribution, which A understates. **Corrected by RT-1:**
   "realistic listing" means *the listing production actually renders*, which is observed to be
   mostly name-only. B's version taken literally (a ~946-entry all-descriptions listing) measures a
   shape production never shows, in the optimistic direction.
4. **Add the missing metric:** report **T1-vs-T2 abstention divergence as a named, separately
   reported number**, not folded into aggregate agreement. T0 and T1 share the stated-preference
   distortion, so T0↔T1 agreement cannot reveal it; only the T1↔T2 abstention delta can
   (`critic-brief.md` C4/X6).
5. **Keep A's expiry discipline** — calibration `valid-until`, scheduled recalibration,
   self-demotion.
6. **Cross-ruling:** T0's eligibility to gate anything is *further* narrowed by `red-team.md` RT-3 —
   T0 is lexical over exactly the tokens the rewriter is instructed to preserve, i.e. the rewriter's
   own objective used as its examiner. RT-3 adds a required **fourth** sabotage corpus (**S4**,
   "keyword tail") that T0 must also fail before it may gate a *rewrite* PR.

### 5.3 Rollout ordering — `tiebreaks.md` T5 (SYNTHESIS)

A ordered by char mass + disambiguation load (wave 1 = `ravenclaude-core`); B ordered by
sibling-cluster overlap / misrouting exposure. **These answer different questions and are not
competing.**

- **Use A's axis to order *value capture*; use B's axis to order *review intensity*.**
- **Wave 1 is set by T2** (the 95 top-decile files), which is mass-selected *and* — per A's own
  F4/F5 — is where disambiguation load concentrates, so it satisfies A's "front-load the hard case"
  reasoning without needing `ravenclaude-core` to be the unit.
- **`ravenclaude-core` becomes wave 2**, as the *procedure* pilot on the single densest
  disambiguation load, run after wave 1 has produced real effect-size numbers to calibrate against.
- **From wave 2 onward** high-cluster-overlap plugins get full adversarial eval + 100% human review
  of `disambiguating`/`router`; solo-skill plugins get linter + sampled review. Order within that
  stays A's mass-ordering.
- **PR packaging stays per-plugin** — both plans agree; B's axis decides *order*, A's per-plugin
  boundary decides *packaging*, so they are not in tension.
- **Reversibility label:** A is right that the rollout is a **one-way door** once a version-bumped
  plugin is distributed; B's "two-way-door per batch" is optimistic in the phase with the largest
  blast radius. **A's forward-fix policy wins.**

### 5.4 Rewrite mechanism — `tiebreaks.md` m4 (default A, modified by T3)

| option | trade-off |
|---|---|
| **A. Three-stage sandwich** — deterministic pre-pass → LLM rewrite anchored to a frozen exemplar bank + versioned style contract → deterministic post-validation with **IDF-based discriminative-token preservation**, per-batch rejection budget (>10% fail ⇒ abort) | Statistical guard that does not depend on the literal phrase "NOT for X" appearing; the only option where "946 rewrites, nobody reads all 946" is defensible. |
| **B. Rule-based first, LLM only on files still over budget**, preservation checked by a **literal-phrase regex** ("not for", "NOT", "distinct from") | Minimal intervention; but the regex is **blind to a boundary phrased without a listed trigger word** — a narrower net for the exact failure mode both plans independently name as central. |
| **A + B's belt** ✅ | A's sandwich, plus B's explicit "preserve verbatim where possible" instruction as an additional belt. |

**Modified by T3:** *this entire apparatus is conditional on claim 6 surviving the effect-size
study.* **Modified by RT-3:** the preservation check must test **structure, not just tokens** —
retained discriminative tokens must appear inside a clause matching the canonical `NOT <x> → <skill>`
form, not merely anywhere in the string.

### 5.5 Length-budget shape — `tiebreaks.md` T4 (verdict A, amended)

A's per-file **category cap** (`leaf` ≤160 / `disambiguating` ≤280 / `router` ≤420, calibrated) plus
a **corpus-total ratchet** wins over B's cluster-density tiers with no ratchet: B has no defense
against the drift vector A designed against (946 files each legally one char under cap still blows
the budget), and A's is the only artifact in either plan that could ever express a corpus-level
goal. **Three binding amendments** (all folded into P3):

1. **Denominate in the unit the goal is stated in.** Both plans ratchet *chars* while the goal is
   *tokens*. `description-budget.json` records **both**, and this plan names explicitly which one
   gates. Skill descriptions are token-dense (backticked identifiers, `plugin:skill` ids, arrows,
   em-dashes) so a −40% char cut is not a −40% token cut, and the direction of the error is not
   knowable without measuring once.
2. **Pin the posture in the artifact.** The ratchet records the plugin set + versions it was
   measured over, and the gate **fails on posture drift** rather than silently comparing different
   populations. (Note RT-1: posture is *also not* the variable that governs what is injected.)
3. **Correction — A's AND-condition makes the ratchet unenforceable** (`red-team.md` RT-2). The
   condition changes from `over-cap AND total-rose` to **`over-cap OR total-above-committed-ceiling`**,
   with the ceiling movable upward only by a PR explicitly labelled as a budget raise, with a
   reason, counted in the job summary.

### 5.6 Gate enforcement — `tiebreaks.md` m3 (default A)

A's **hook (advisory, in-loop, never blocks) + CI (the actual gate)** two-layer design, advisory-first
with a **numerically pre-stated fire-rate budget**, a `--health` self-audit that demotes the gate
rather than waiting for a human to disable it, and a step-level repo-variable kill switch. **B is
silent on all five.** A's is the only design that survives this repo's documented history of
guardrails being turned off. See RT-6 for where A's hook layer will **not** fire.

### 5.7 Minor rulings folded in (`tiebreaks.md` m1–m10)

| # | ruling | folded into |
|---|---|---|
| m1 | A's description-withheld generator + leakage probe + frozen 60-case human subset; **modified by T2/T3** — required coverage N scales to the scope authorised after wave 1, and B's stratified sampling becomes the tail mechanism rather than A's universal 946×3 | **P4** |
| m2 | A's "human set wins any disagreement" kept **verbatim**; RT-3 adds that tuning the rewriter against this subset **burns it** | **P4**, **P7** |
| m3 | Hook + CI, advisory-first, numeric fire budget, `--health` self-demotion, repo-variable kill switch | **P11** |
| m4 | A's sandwich + IDF preservation + rejection budget; adopt B's verbatim-preservation instruction as a belt; **conditional on claim 6** | **P2**, **P7** |
| m5 | A's **data-driven** human-review exit criterion over B's permanent 100% across all 182 batches (for which B supplies no reduction path) | **P9**, **P10** |
| m6 | Baseline discrepancy: keep A's requirement to name one measurement method and a cause class, but **demote from hard blocker to a P0 deliverable** — 0.9% across three measurements is inside the error bars while a potentially ~85% chars-on-disk-vs-bytes-injected gap goes unexamined. *Right instinct, wrong magnitude.* | **P0** |
| m7 | Only A names claim-4 instruments (`claude plugin details`' projected token cost; `/plugin` Discover context cost). **Also amend `scope.md`'s Baseline paragraph** per C10 — B correctly refutes the agent-description-budget framing and neither plan owns the correction | **P0** |
| m8 | Register teeth tests **as their phases land**, not batched behind the standing gate | **P12** + every phase's DoD |
| m9 | Gate-number claim: A said ~281, B said 261; **measured this session: 263**. Re-count at implementation time; do not hardcode | **P12** |
| m10 | Cross-host coverage: **explicit waiver** | **§6** |

---

## 6. Accepted-risk waiver — cross-host (Copilot CLI / Codex CLI) eval coverage

**Origin:** `critic-brief.md` C9/X10, `red-team.md` RT-6(3), ruled an **explicit waiver** by
`tiebreaks.md` m10.

**The exposure, as observed.** `scripts/generate-copilot-plugin.py` (lines 13–14, 553):
*"Skills are delivered to the consumer's `.claude/skills`"* — the same description text is projected
to **GitHub Copilot CLI**. `AGENTS.md` documents the **Codex CLI** lane wiring skills to
`.agents/skills`. The repo's own worldview memory treats hosts as Claude Code ∪ Copilot. **Every
eval tier in this plan measures Claude Code routing only.** A rewrite tuned to keep Claude's router
happy is unmeasured on Copilot CLI and Codex CLI, whose selection behaviour is a different
mechanism. A regression on those two hosts is **invisible to every gate this plan builds**.

**The waiver, and the condition on it.** Building a Copilot/Codex routing eval is a second project.
`red-team.md` RT-6 offers and recommends the waiver, and it is accepted here — **but only because it
is declared**. An undeclared gap is the failure; a declared one is a trade.

**Required action (a P0 deliverable, not an intention):** add one sentence to `scope.md`'s
Out-of-scope list, in these words or equivalent:

> Cross-host routing evaluation (GitHub Copilot CLI and OpenAI Codex CLI, which receive the same
> projected skill descriptions via `scripts/generate-copilot-plugin.py` and `.agents/skills`) is
> **out of scope for this effort: no eval instrument exists for those routers, and cross-host
> routing regressions are an accepted, unmeasured risk of this change.**

**Optional cheap partial coverage, if the owner wants it later:** one Copilot-lane spot check per
wave (`critic-brief.md` X10's alternative probe). Not required by this waiver; named so the option
is not lost.

**Related accepted risks, declared here for the same reason (all from `red-team.md` RT-4..RT-8, and
all *mitigated* rather than waived — listed so the residual is visible):**

- **RT-4 residual.** The wave runbook ordering (§7 P10) is a *procedural* control on a mechanism
  (`audit-gates.sh:2242` `git checkout --`) that will still silently revert an uncommitted version
  bump if the runbook is not followed. The automatable half — "every plugin with a changed
  `SKILL.md` has a `version` bump in the same PR" — closes most of it; the ordering itself does not
  have a gate.
- **RT-5 residual.** Deriving the ceiling removes the artifact conflict. If the derived-ceiling
  design proves impractical, the fallback is to **serialise the waves**, which kills the
  parallelisation budget — *"acceptable, but say so in plan.md rather than discovering it at wave
  6."* It is said here.
- **RT-7 residual.** If the MDE computed in P6 exceeds the effect size measured in P1, the per-wave
  gate **cannot detect the effect it exists to detect**. That sentence must then be written into
  the plan and the detection burden moved to the scheduled aggregate run (P13).
- **RT-8 residual.** The charset teeth test covers YAML-hostile characters this plan anticipates; a
  novel one still surfaces as a whole-tree `prettier --check .` failure on somebody else's
  unrelated PR.

---

## 7. Phases

Each phase carries: **goal · `depends_on_claims` · `reversibility` · pre-build gates · build ·
acceptance tests · rollback · definition of done.**

Claim numbers refer to `claims-table.md` rows 1–6.

### Claim 6 — preserved verbatim (governs P1, P2, P4, P7, P9, P10)

> | # | Claim | kind | tier | source | settling-gate |
> |---|---|---|---|---|---|
> | 6 | A shorter description could reduce routing accuracy (the model picks skills less reliably) if it drops disambiguating detail | inference | N/A — the premise motivating the eval-harness requirement | `[unverified — premise not disconfirmed: this is the central hypothesis motivating the user's own eval-harness requirement; it cannot be settled by a <=300s probe because settling it IS the eval-harness deliverable itself]` | owner-gated — plan.md's synthesis phase must cap every citing phase to a single reversible file + flag it, until the eval harness (an early, non-citing phase) produces real evidence; open question carried to plan.md: "does deleting disambiguation clauses measurably hurt routing? build the golden-set eval FIRST, before any bulk rewrite" |

**How this plan discharges the owner-gate:** **P1** is that early, non-citing phase. It cites claim 6
for nothing; it *produces evidence about it*. Until P1 reports, every phase that cites claim 6 (P2's
preservation half, P4's cluster weighting, P7/P9/P10's rewrite) is **capped to a single reversible
file and flagged**, per the settling-gate's own words. P1 is specified in `tiebreaks.md` T3 as a
3-arm, ~40-skill, pre-registered effect-size study and is written out in full below.

---

### P0 — Rendering & unit audit (the premise phase)

**Goal.** Settle what actually reaches context, in what unit, under what posture — so that every
later number has an honest denominator. This is the phase §2 demands.

**`depends_on_claims`:** `[1, 2, 3, 4]`
**`reversibility`:** two-way-door (read-only measurement plus committed baseline artifacts and one
`scope.md` text amendment)

**Pre-build gates**

- **G-P0.1 — The RT-1 harness-rendering audit, both arms** (§2.3). Arm A (main-session capture,
  membership diff) and Arm B (invoke 3 never-invoked skills → fresh session → **membership** diff).
  Record the outcome and its cause class (E/F/G/H/I) or explicitly mark it an unresolved hypothesis.
  **⛔ No later phase is authorised until this gate reports.**
- **G-P0.2 — Settle claim 4** (only enabled plugins load) using the instruments `tiebreaks.md` m7
  names: `claude plugin details <name>`'s projected token cost and the `/plugin` Discover tab's
  per-plugin **Context cost** figure. This sets the denominator for every savings claim.
- **G-P0.3 — Tokenize once** (`critic-brief.md` C2/X4). Measure the corpus in **tokens**, not
  4-chars-per-token arithmetic, and state which benefit the program optimises: (i) $/turn — largely
  a **cache-read** cost at ~0.1× list price, since the skill listing lives in the canonical
  prompt-cache prefix; (ii) **context-window occupancy** — real regardless of caching and the
  strongest justification; (iii) **attention dilution / routing quality at scale** — plausible,
  entirely unmeasured, and would make the program worth doing at zero dollar savings. Pick one and
  name it. *(C3: neither input plan has a value-realisation acceptance test in the owner's units.)*

**Build**

1. `scripts/skill-description-baseline.py` — **the** single measurement instrument used by every
   later phase (repo-root `scripts/`, **not** under a plugin's guarded substrate — RT-6(2)). Emits
   `description-baseline.json`: per-skill `{plugin, skill, path, chars, tokens, sha256,
   description}`, corpus aggregates in **both** chars and tokens, the **method string**, and the
   **pinned posture** (plugin set + versions) per `tiebreaks.md` T4 amendment 2 / X11.
2. **A rendering model**, written down: for the current posture, which skills' description bytes
   actually appear in the listing, measured by the G-P0.1 audit — and, if usage-gating is confirmed,
   an explicit statement that **the injected subset is non-stationary** and why that makes the
   savings metric partly endogenous (§2.2).
3. `description-budget.json` — initialised (chars **and** tokens), posture-pinned. See P3 for its
   gating semantics.
4. **Baseline reconciliation, demoted to a deliverable** (`tiebreaks.md` m6). Three measurements
   exist: 310,359 (claims-table) / 307,672 (plan-A F3) / 308,229 (`critic-brief.md` p5). Name one
   measurement method, state which number it reproduces and why the others differ, or mark it an
   unresolved hypothesis with its cause class. **This is no longer a hard blocker** — a 0.9% spread
   is inside the error bars while a potentially ~85% chars-on-disk-vs-bytes-injected gap is the
   reconciliation that actually matters.
5. **`scope.md` amendments (two, both required):**
   - **(a)** Correct the Baseline paragraph's motivation (`critic-brief.md` C10/X14 · m7). The
     current text cites the `agent-description-budget` ~15K memory as if it governed the skill pool;
     plan-B §0 correctly refutes this — that budget is about **agent** frontmatter under
     `plugins/*/agents/*.md`, a different pool injected by a different mechanism. Neither input plan
     owned the correction. **This plan does.**
   - **(b)** Add the cross-host out-of-scope sentence from **§6**.
6. Re-count the current max gate number in `scripts/audit-gates.sh` (**263** as measured this
   session — `critic-brief.md` p8, `red-team.md` q9; A's "~281" and B's "261" are both stale).
   Record it; re-check again at implementation time (m9).

**Acceptance tests**

- **AT-P0.1** — Re-running the baseline script on an unchanged tree produces a byte-identical
  `description-baseline.json`. *(determinism)*
- **AT-P0.2** — **Must-fail teeth:** mutating one description by +50 chars and re-running changes
  exactly that file's entry and the corpus total by exactly +50. A baseline that does not move under
  a known mutation is not reading the subject.
- **AT-P0.3** — The G-P0.1 rendering audit's result is written down with a named cause class, or
  explicitly marked an unresolved hypothesis. **The document states, in one sentence, what fraction
  of on-disk description bytes reach a main session's context.**
- **AT-P0.4** — The savings denominator is stated as a number **with its posture and its rendering
  model**, never as a marketplace total presented as a per-turn saving.
- **AT-P0.5** — The baseline carries **both** chars and tokens, and the plan names which one gates.
- **AT-P0.6** — `scope.md` carries both amendments (5a, 5b) and they are diff-visible.
- **AT-P0.7** — **Charset round-trip teeth** (RT-8): a description containing each YAML-special
  character (`:`, `#`, leading `-`, `|`, `>`) round-trips byte-identically through
  `skill-description-baseline.py` and re-parses to the same string.

**Rollback.** Delete two JSON files; `git revert` the `scope.md` amendment.

**Definition of done**

- [ ] AT-P0.1 … AT-P0.7 all pass.
- [ ] G-P0.1 (both arms), G-P0.2, G-P0.3 reported in the run dir.
- [ ] **Version bumps:** none — `scripts/` and `scope.md` only, no plugin surface touched.
- [ ] **Gate registration:** register **baseline determinism (AT-P0.1/.2)** and the **charset
      round-trip (AT-P0.7)** in `scripts/audit-gates.sh` **now**, not at P12 (m8), in **all three
      required surfaces**: (1) a `── Gate N: … ──` header block with `gate "…" must_fail` +
      `gate "…" must_pass` assertions **after** the `--check` dispatcher (reachability — the Gate 184
      defect was a gate registered *only* inside the dispatcher arm while the suite printed "all
      gates audited and verified bidirectional"); (2) a `N)` **case arm** in the `--check <n>`
      dispatcher; (3) the number listed in the `*)` arm's **`Supported:`** line. Then
      `python3 scripts/check-gate-registration.py` must exit 0.
- [ ] **`/code-review`** — P0 lands a real script (`skill-description-baseline.py`) via PR: run
      `/code-review` on the diff before merge.
- [ ] Run `scripts/audit-gates.sh` **in full** on a clean tree; commit rewrites first (RT-4).

---

### P1 — Claim-6 effect-size study (early, non-citing) **[T3]**

**Goal.** Produce **real evidence about claim 6** — does deleting disambiguation clauses measurably
hurt routing, and by how much — before any preservation apparatus is built. This is the phase the
claims-table's own settling instruction demands.

**`depends_on_claims`:** `[6]` — and it **cites** claim 6 for nothing; it *tests* it.
**`reversibility`:** two-way-door (a study on scratch corpora; no repo surface mutated)

**Why this exists at all (the ruling, `tiebreaks.md` T3).** *"Neither design is a test of claim 6;
both test the instrument."* plan-A's AT-P3.2 reads a null result on the boundary-deletion corpus as
**instrument failure**, never as evidence claim 6 is false. plan-B's preservation check fails closed
on any dropped `NOT for X` clause **regardless of measured routing impact**. Neither plan has a
branch for *"the premise did not reproduce."* A test whose only two outcomes are "effect confirmed"
and "instrument broken" cannot disconfirm the hypothesis — that is the **inverted-audit** shape in
`silent-green-defects` — and the tool needed to run the real experiment is already installed.

**The specification (binding, from `tiebreaks.md` T3's table)**

| element | specification |
|---|---|
| **Sample** | ~**40 skills** spanning **≥12 confusable clusters**, each with ≥1 same-listing sibling. Chosen **before** any rewrite work. |
| **Arms** | **Three**, corpus otherwise byte-identical: **(a)** original; **(b)** mechanically truncated to ~200 chars mid-sentence; **(c)** carefully shortened to arm-(b)'s length *preserving* boundaries. |
| **Instrument** | `claude plugin eval`, real agent runs, `tool_used: Skill` graders, under the ablation mode that **scores** that grader (§5.2 amendments 1–2). `--runs` ≥5 to characterise variance. |
| **Pre-registration** | **Before the run:** state the effect size worth acting on (e.g. ≥5pp of sibling-confusion rate between arm (a) and arm (b)) **and** compute the **N required to detect it at the chosen σ**. This is the power calculation missing from both plans (`critic-brief.md` C8/X3), and computing it here rather than at threshold-freezing time is the only place it is still cheap. |
| **Positive control (mandatory)** | Verify that arm (b)'s and arm (c)'s manipulated text **actually appears in the rendered listing of the eval run** before scoring any arm. Per RT-1, if the manipulated descriptions are not rendered, arms (a) and (b) are **identical in context** and a null result is an artefact, not evidence. **Without this control the whole study is a blind probe.** |
| **Both outcomes pre-committed** | **Effect ≥ pre-registered size** ⇒ claim 6 is real; the preservation apparatus is **earned**; the arm-(c)−arm-(a) delta sets ε honestly. **Null at adequate power** ⇒ claim 6 is **not supported at this scale**; the category budgets, IDF-preservation guard, exemplar bank, and 100%-human-review of two categories are **dropped as unearned cost**, and the program collapses to **linter + ratchet + the top-decile pass**. |

**Pre-build gates**

- **G-P1.1 — P0 green**, including the rendering audit. The positive control above is impossible
  without it.
- **G-P1.2 — The ablation pre-flight probe** (§5.2 amendment 2 / X5): run one case carrying a
  `tool_used: Skill` grader under **both** `--ablation none` and `--ablation with-without`; compare
  the *reported score*. If identical, the grader contributes nothing under `with-without` and the
  study runs under `none`.
- **G-P1.3 — Pre-registration is committed to the run dir before the first run.** A floor set after
  seeing the number is not a test.

**Acceptance tests**

- **AT-P1.1** — The positive control passes: arm (b)/(c) manipulated text is confirmed present in
  the rendered listing of the eval run. **If it is not, the study is halted and reported as
  inconclusive-by-construction, not as a null.**
- **AT-P1.2** — Pre-registration (effect size + required N) exists in the run dir with a timestamp
  **preceding** the first run.
- **AT-P1.3** — The ablation pre-flight probe result is recorded, and the study's ablation mode
  follows from it.
- **AT-P1.4** — Variance across `--runs ≥5` is recorded per arm; σ is a measured number, not a
  guess.
- **AT-P1.5 — The falsifiability check on the test itself.** *This plan must contain the sentence
  that gets written if the null holds.* It does, and here it is, ready to be filled in and shipped:

  > **"Claim 6 is not supported at this scale: across ~40 skills in ≥12 confusable clusters,
  > mechanically truncating descriptions to ~200 chars produced no sibling-confusion effect at or
  > above the pre-registered ≥Npp threshold at adequate power (σ = _, N = _, MDE = _). The
  > preservation apparatus — category budgets, IDF-preservation guard, exemplar bank, and
  > 100%-human-review of the `disambiguating` and `router` categories — is therefore dropped as
  > unearned cost, and this program is reduced to the linter, the ratchet, and the top-decile
  > pass."**

  **If no phase can output that sentence, this ruling has not been implemented.**

**Rollback.** Delete the study artifacts; nothing in the repo tree was mutated.

**Definition of done**

- [ ] AT-P1.1 … AT-P1.5 pass.
- [ ] The **measured effect size** is recorded and becomes the input to ε (P6) and MDE (P6/RT-7).
- [ ] The outcome branch is **declared**: apparatus earned, or apparatus dropped (with AT-P1.5's
      sentence written).
- [ ] **Version bumps:** none.
- [ ] **Gate registration:** none yet (no standing check emerges from a study). The **S2/S4**
      sabotage-corpus teeth tests derived from this study register at **P6**.
- [ ] **`/code-review`:** only if the study ships helper code into `scripts/`; if it is run-dir-only
      scaffolding, no PR and no review.

---

### P2 — Style contract, category classifier, deterministic linter

**Goal.** The cheap, deterministic, on-disk floor — the **only** component that survives RT-1 being
true.

**`depends_on_claims`:** `[1, 2]` for the linter half; `[6]` for the preservation half
**`reversibility`:** two-way-door

**Pre-build gates**

- **G-P2.1 — Category taxonomy calibrated** against the measured distribution (`leaf` / `disambiguating`
  / `router`) so the initial mix does not put an unworkable share over cap on day one. Publish the
  projected over-cap count per category **before** adopting the numbers.
- **G-P2.2 — Precedent check.** `scripts/check-frontmatter.py` already enforces a ≤300-char cap on
  **agent** descriptions (gated by `_rel_parts[2] == "agents"`; `SKILL.md` frontmatter is checked
  only for description **presence**, never length — claim 5, settled). Extend that file's shape;
  do not create a parallel gate family.
- **G-P2.3 — Claim-6 conditionality [T3/m4].** The **preservation half** of this phase
  (category budgets, IDF guard, exemplar bank) is built **only if P1 earned it**. The linter half
  (caps, filler detection, name-restatement, charset, ratchet check) is built regardless.

**Build**

1. **Style contract** — `docs/best-practices/skill-description-style.md`, frozen and versioned:
   lead with the job in the user's vocabulary; no name restatement, no "This skill…", no "Use this
   agent to…", no example-phrase lists; **preserve every disambiguation boundary in the compressed
   canonical form `NOT <x> → <other-skill>`**; preserve every distinctive trigger token;
   category-appropriate length; **a constrained output charset** (RT-8) excluding YAML-hostile
   constructs; and **12 worked before/after exemplars** spanning all three categories — the few-shot
   bank the rewriter is anchored to. Style consistency across many files comes from a frozen
   exemplar bank plus deterministic validation, not from asking nicely in a prompt.
2. **Category classifier** — deterministic. `disambiguating` if the description or body references
   another skill or the skill sits in a confusable cluster; `router` if it contains an explicit
   trigger/skip contract; else `leaf`. Overridable via frontmatter `description_category:` with a
   reason.
3. **`scripts/check-skill-descriptions.py`** (repo-root `scripts/`, RT-6(2)) — the linter:
   - category cap check (chars **and** tokens);
   - filler-phrase detection, calibrated from the real corpus, not guessed;
   - name-restatement detection;
   - **discriminative-token preservation** — high-IDF n-grams from the baseline description must be
     retained above a threshold share;
   - **[RT-3] STRUCTURAL preservation, not just tokens** — retained discriminative tokens must
     appear **inside a clause matching the canonical `NOT <x> → <skill>` form**, not merely
     anywhere in the string. This is what defeats the keyword-tail degenerate solution
     (`"… NOT: forge, handoff, Grok, quota."`) that passes a pure token check *and* scores maximally
     on a lexical T0;
   - **[RT-8] charset validation** — reject YAML-hostile output deterministically in the linter
     rather than discovering it in a whole-tree `prettier --check .` failure on somebody else's PR;
   - corpus-total ratchet check against `description-budget.json` (semantics in **P3**);
   - `--fix` for the **provably-safe mechanical strips only**.

**Acceptance tests**

- **AT-P2.1** — The linter over the *unmodified* corpus reports the exact over-cap counts projected
  in G-P2.1 (±0). *(the linter and the projection measure the same thing)*
- **AT-P2.2 — Must-fail teeth:** a fixture description with its `NOT for X → Y` clause deleted fails
  the preservation check; the same description with the clause intact passes.
- **AT-P2.3 — [RT-3] Must-fail teeth, keyword-tail:** a fixture whose boundary clause is replaced by
  a bare comma-separated list **retaining every high-IDF token** **fails** the structural check. A
  linter that passes this fixture has not implemented RT-3's mitigation.
- **AT-P2.4** — `--fix` is idempotent: running twice equals running once.
- **AT-P2.5** — `--fix` never changes the routing-relevant token set — verified by running the T0
  tier before/after `--fix` on the full corpus with **zero** metric movement beyond ε.
- **AT-P2.6** — Every one of the 12 exemplars in the style contract **passes the linter**. A style
  guide whose own examples fail the gate is the inverted-audit defect this repo has catalogued.
- **AT-P2.7 — [RT-8]** A description containing each YAML-special character is rejected by the
  charset check with a specific message naming the character.

**Rollback.** Delete the linter and the contract; `--fix` is never run without a commit boundary.

**Definition of done**

- [ ] AT-P2.1 … AT-P2.7 pass (AT-P2.2/.3 conditional on P1 having earned the preservation half).
- [ ] **Version bumps:** none if the linter lives in repo-root `scripts/` and the contract in
      `docs/best-practices/` — neither is a plugin surface. If any part ships inside
      `plugins/ravenclaude-core/`, bump `plugins/ravenclaude-core/.claude-plugin/plugin.json`, run
      `python3 scripts/sync-plugin-versions.py`, **and** `python3 scripts/generate-copilot-plugin.py`.
- [ ] **Gate registration (all 3 surfaces, now — m8):** register **linter cap + structural
      preservation (AT-P2.2/.3)** and **charset (AT-P2.7)**: (1) `── Gate N: … ──` header + must_fail
      / must_pass assertions in the **full-suite body** after the dispatcher; (2) an `N)` **case arm**
      in the `--check` dispatcher; (3) the number in the `*)` arm's **`Supported:`** list.
      `check-gate-registration.py` exits 0. Claim gate numbers by reading the **current max at the
      moment of writing** (263 as measured; re-check) and re-check again before merge — number
      collision is a catalogued defect (m9).
- [ ] **`/code-review`** on the PR — this phase lands real code.
- [ ] `prettier --write .` → `prettier --check .` exit 0; `ruff check .` exit 0.
- [ ] `scripts/audit-gates.sh` run **in full** on a clean tree, **after** committing all edits
      (RT-4: the suite's `git checkout --` restore at line 2242 silently reverts uncommitted work).

---

### P3 — Budget artifact and ratchet **[T4 + RT-2 + RT-5]**

**Goal.** The corpus-level limit — the only instrument that protects the context budget, because
946 files each sitting one char under a per-file cap still blows it.

**`depends_on_claims`:** `[1, 2, 4]`
**`reversibility`:** two-way-door

**Pre-build gates**

- **G-P3.1 — P0 green.** The artifact records the posture it was measured over; there is no ratchet
  without a pinned population.
- **G-P3.2 — Unit decided.** P0's G-P0.3 named the gating unit. The artifact records **both** chars
  and tokens and this plan names which one gates (T4 amendment 1).

**Build**

1. `description-budget.json` — records **chars and tokens**, the **pinned posture** (plugin set +
   versions), the measurement method string, and the committed ceiling.
2. **The gate condition is `over-cap OR total-above-committed-ceiling`** — **not** plan-A's
   `over-cap AND total-rose`. **[RT-2, binding.]** A's AND-condition is trivially and legally
   gameable across PRs: PR#1 shrinks description *X* by 300 chars and the ratchet re-stamps the
   ceiling **downward**; PR#2, days later, grows description *Y* by 290 chars **under its category
   cap**, so the AND never fires and the total climbs back, permanently, one PR at a time. A's
   AT-P7.4 tests only the **single-PR** shape (trim one file, bloat another in the same commit) —
   *"nobody bloats and trims in one commit; the natural shape is temporal, and it is untested."*
3. **The ceiling moves upward only by a PR explicitly labelled a budget raise**, with a written
   reason, **counted in the job summary** — reusing A's declared-exemption pattern, which is the
   right shape.
4. **[RT-5] The ceiling is DERIVED, not stored per-PR.** The gate recomputes the corpus total from
   the tree and compares it to a ceiling that only a dedicated, **serialised** budget-change PR may
   edit. Wave PRs then never touch the artifact and never conflict on it. *This one change closes
   both RT-2 and RT-5.* **Fallback if the derived design proves impractical: serialise the waves,
   which kills the parallelisation budget — declared in §6, not discovered at wave 6.**
5. **Stamp-ordering rule ported inline.** `ratchet-freshness-stamp-timing-trap`: `--stamp`
   immediately after `checkout -b origin/main` captures the **parent** commit. Commit first, then
   stamp, then **re-stamp before merge**. Written as a comment next to the stamp step in the
   workflow (RT-2's second trigger: A's rollout phase knew this; A's *gate* had no equivalent
   guard, so a mis-timed stamp silently re-baselines the ceiling **upward** with no signal).
6. **Posture-drift failure.** The gate **fails** when the measured posture differs from the pinned
   one, rather than silently comparing different populations (X11).

**Acceptance tests**

- **AT-P3.1** — On an unmodified tree, the ratchet check is **silent**.
- **AT-P3.2 — Must-fail teeth, single-PR shape:** a PR that trims one description by 10 chars and
  bloats another by 300 **fails** (total above ceiling), proving the ratchet is not gameable
  file-by-file.
- **AT-P3.3 — [RT-2] Must-fail teeth, TWO-PR shape (the new one):** apply PR#1's 300-char shrink,
  re-stamp the ceiling, then apply PR#2's 290-char **under-cap** growth, and assert the gate
  **fires**. A ratchet that passes this sequence is decorative while continuing to report green.
- **AT-P3.4** — A budget-raise PR **without** the explicit label and reason fails; **with** them it
  passes and the raise appears in the job summary.
- **AT-P3.5** — A posture change (enable/disable a plugin) with no description edit **fails** the
  drift check rather than silently re-baselining.
- **AT-P3.6** — The artifact carries chars **and** tokens, and the gating unit is named in the file.

**Rollback.** Delete the artifact and the check; nothing else references them until P11.

**Definition of done**

- [ ] AT-P3.1 … AT-P3.6 pass.
- [ ] **Version bumps:** none (repo-root artifact + `scripts/`).
- [ ] **Gate registration (all 3 surfaces):** the **two-PR ratchet teeth test (AT-P3.3)** registers
      **when P11 lands** (it needs the live gate), per RT-2's *"register it when P7 lands, not
      batched at the end"*. The **single-PR** shape (AT-P3.2) and the **posture-drift** check
      (AT-P3.5) register now, in all three surfaces (body block + `N)` dispatcher arm + `Supported:`
      list), with `check-gate-registration.py` exit 0.
- [ ] **`/code-review`** on the PR — real code.
- [ ] Full `audit-gates.sh` on a clean tree, edits committed first (RT-4).

---

### P4 — Golden set **[m1, m2, T2-scaled]**

**Goal.** A labelled (prompt → expected skill | `none`) set that is **confusable-pair-heavy**, not
uniformly sampled, and that cannot be satisfied by echoing the descriptions it scores.

**`depends_on_claims`:** `[1, 3, 6]`
**`reversibility`:** two-way-door (new files only)

**Pre-build gates**

- **G-P4.1 — Confusable-cluster map exists first.** Cluster by description+name similarity **and**
  by explicit cross-references (any description naming another skill — the `NOT for X → Y` clauses
  are machine-extractable). **The clusters, not the skills, are the sampling frame.** Without this
  the set is uniformly sampled and will not exercise the failure mode.
- **G-P4.2 — The anti-echo control is designed and its leakage probe specified before a single
  prompt is generated.** The generator **must never see the `description` it will be scored
  against**; prompts come from the skill's **body**, name, and trigger phrases.
- **G-P4.3 — [m1/T2] Coverage N scales to the scope authorised after wave 1.** plan-A's universal
  946 × ≥3 positive cases (2,838+ prompts) is **not** built up front. Wave 1 needs full coverage of
  the 95 top-decile files and their clusters; **B's stratified sampling becomes the mechanism for
  the tail**, expanded only if P8 authorises broader scope.

**Build**

1. `evals/skill-routing/clusters.json` — confusable clusters with members and the cross-reference
   edges that separate them.
2. Prompt generation, **description withheld**: ≥3 positive prompts per in-scope skill; **≥2
   negative** prompts per confusable cluster (a prompt that fits sibling *A* and must **not** route
   to *B*); **≥1 `expect: none`** prompt per cluster (plausibly adjacent, genuinely out of scope).
3. **Mined anchor set** — the transcript-mined pairs (measured: **48 invocations across 24 distinct
   skills in 39 sessions**, i.e. **2.5% of the corpus**, heavily biased toward `ravenclaude-core`).
   These are a **calibration anchor and realism check, never the primary source** — this kills
   "mine from real sessions" as a primary strategy, which is exactly the kind of option that sounds
   obviously right and is wrong on the data. Also worth more per sample: the transcripts' **near-miss**
   signal (a skill clearly relevant and never invoked), which requires a judged pass, not a grep.
4. **Human acceptance subset — 60 prompts** the owner writes by hand across 20 clusters, **never
   regenerated**. This is the correlated-error detector. **[m2 kept verbatim]** *"If the synthetic
   set says 'fine' and the human set says 'worse', the human set wins."*
5. **[RT-3] Quarantine.** The human 60-case subset is **quarantined from every rewriter iteration**.
   Any tuning against it **burns it**. Stated here so the temptation is named: A's "rejected,
   retried once" rewrite loop *is* tuning against whatever set it scores on, and A's leakage probe
   detects **generator-side echo**, not **rewriter-side overfitting** — different failures.
6. Freeze: `evals/skill-routing/golden-v1.jsonl`, content-hashed, provenance per case
   (`source: synthetic|mined|human`, generator model + prompt version, seed).

**Acceptance tests**

- **AT-P4.1** — Every in-scope skill has ≥3 positive cases. *(no unmeasured skill within the
  authorised scope)*
- **AT-P4.2** — Every confusable cluster of size ≥2 has ≥2 negative cases and ≥1 `expect: none`.
- **AT-P4.3 — Leakage probe:** T0 recall@1 on synthetic positives is **not** >0.97 while the human
  subset is >0.15 lower. A near-ceiling synthetic score alongside a mediocre human score means the
  generator echoed the description and **the set is rejected**. *(the positive control on the golden
  set itself)*
- **AT-P4.4 — Positive control, from plan-B:** run the set against the **current, unmodified**
  descriptions first. It must show **non-trivial pass and non-trivial fail**. 100% pre-rewrite pass
  ⇒ not adversarial enough to detect a regression; near-0% ⇒ the harness is broken.
- **AT-P4.5** — Provenance: every case carries `source` + generator version; the set is reproducible
  from a recorded seed.
- **AT-P4.6 — Must-fail teeth:** injecting a deliberately-wrong label into 5% of cases causes the
  set's own self-consistency check to fail.
- **AT-P4.7 — [RT-3]** The quarantine is enforced mechanically (the human subset is in a separate
  file the rewrite loop cannot read), not merely stated.

**Rollback.** Delete `evals/skill-routing/`. *(Add the new directory to `.repo-layout.json`
`allowed_globs` before pushing — `validate-layout.yml` blocks unlisted paths.)*

**Definition of done**

- [ ] AT-P4.1 … AT-P4.7 pass.
- [ ] `.repo-layout.json` `allowed_globs` updated for `evals/skill-routing/**`.
- [ ] **Version bumps:** none.
- [ ] **Gate registration:** the golden set's **self-consistency teeth (AT-P4.6)** registers now in
      all three surfaces (body block + `N)` dispatcher arm + `Supported:` list);
      `check-gate-registration.py` exits 0.
- [ ] **`/code-review`** on the PR — generator + schema are real code.

---

### P5 — Eval harness ladder T0 / T1 / T2 **[T1]**

**Goal.** Three instruments whose costs match their consequences, where **the cheap tier's authority
is borrowed from the expensive one and expires**.

**`depends_on_claims`:** `[3, 5]`
**`reversibility`:** two-way-door

| tier | instrument | cost | fidelity | role |
|---|---|---|---|---|
| **T0** | **Retrieval proxy** — deterministic BM25/TF-IDF over the rendered listing + name. recall@1/@5, MRR, negative-case margin | free, seconds, no network | proxy only | **the CI gate — if and only if it earns it in P6** |
| **T1** | **Single-shot router** — one model call: system = the rendered listing; user = the prompt; response = a skill id or `none`. No agent loop, no tools | ~1 call/case | model-grounded, no agent dynamics | **the per-PR-batch gate** |
| **T2** | **`claude plugin eval`** — real agent runs, `tool_used: Skill` graders, `--runs` ≥3 | full agent run × N | **ground truth** | **the release gate + T0's calibrator** |

**Pre-build gates**

- **G-P5.1 — Cost probe before committing to the architecture.** Run `claude plugin eval` on a
  20-case pilot with `--max-cost-usd` set low; record wall-clock, cost, and variance across
  `--runs 3`. plan-A's estimate: 946 skills × ≥3 cases × 3 runs ≈ **8,500 agent runs per pass** —
  not something a per-PR gate can afford, and a plan that assumes it can produces a gate disabled in
  week two. **Falsifier:** if a full pass is under ~15 min and a few dollars, the ladder collapses
  and T2 moves down a rung — a genuinely better outcome.
- **G-P5.2 — Reuse-before-build.** `scripts/thing-golden-eval.py` is an existing golden-set
  regression harness with a deterministic CI lane and a `--live` model lane. **Its lane structure is
  the template**; do not invent a fourth pattern where a proven one exists. plan-B is right that
  `evals/runner.py` is the **wrong** base — it scores multi-agent run summaries on 4 fixed
  dimensions, a different shape entirely.
- **G-P5.3 — [T1#2] The ablation pre-flight probe** must have been run in P1's G-P1.2 and its result
  must govern T2's configuration here.

**Build**

1. **T0** `scripts/eval-skill-routing.py --tier retrieval` — zero network, per-metric scores +
   per-case detail.
2. **T1** `--tier router` — batched, cacheable, resumable.
3. **T2** `evals/skill-routing/**/case.yaml` for `claude plugin eval`, **under the ablation mode
   that scores `tool_used: Skill`** (§5.2 #1–2). Also model the two mechanical frictions plan-A did
   not: the eval **target is a plugin**, and `with-without` ablates **the whole plugin**, so
   cross-plugin confusable pairs (`ravenclaude-core:repo-review` vs the built-in `/code-review`;
   `claude-api` vs the Cloudflare family) **do not express naturally** as a with/without ablation of
   one plugin.
4. **[T1#3, RT-1-corrected] Realistic-listing construction.** Each case's candidates are embedded in
   a listing that matches **what production actually renders** — per P0's rendering model. **Not** a
   toy 2-skill choice (plan-B is right that isolation systematically overstates routing quality:
   primacy/recency and needle-in-haystack effects are real and worse at scale), and **not** a
   ~946-entry all-descriptions listing (plan-B's literal version, which measures a shape production
   never shows, in the optimistic direction).
5. **[T1#4] T1-vs-T2 abstention divergence** is computed and reported as a **named, separate
   number**, never folded into aggregate agreement.
6. **Variance characterisation** — run each tier 5× on an unchanged corpus; record per-metric σ.
   **ε for every threshold is set from this σ, not chosen.**
7. **Frozen metric definitions:** `recall@1`, `recall@5`, `MRR`; **false-fire rate** (fraction of
   negative cases where the target ranks #1 / is selected); **sibling-confusion rate** (within a
   confusable set, fraction routed to the wrong member); **abstention accuracy** (on `expect: none`,
   fraction correctly declining). **Δ gates, not the absolute value.**

**Acceptance tests**

- **AT-P5.1** — T0 on an unchanged corpus is bit-identical across runs. *(determinism)*
- **AT-P5.2** — Each tier's measured σ is recorded and every threshold is ≥3σ. **[RT-7 caveat, stated
  not hidden]** plan-A never states the detection-power trade its own ≥3σ rule buys: a wider band is
  a **less sensitive** gate. The MDE computed in P6 is what makes that trade visible.
- **AT-P5.3 — Must-fail teeth per tier:** with one skill's description replaced by the literal string
  `"x"`, each tier's recall@1 for that skill drops below 0.2. A tier that still finds it is not
  reading the description.
- **AT-P5.4** — Resumability: killing T1/T2 mid-run and re-invoking completes without re-paying for
  finished cases.
- **AT-P5.5** — Every tier exits **2** on internal error and **1** on threshold failure; **never 0 on
  a skipped run**. *A skip is not a pass* — an unrunnable tier prints `THIS IS NOT A PASS` and exits
  non-zero in CI.
- **AT-P5.6** — The T1↔T2 abstention divergence is present as a named field in the report.
- **AT-P5.7 — [X13]** The **program** cost is stated, not just the per-run cost: per-run cost ×
  planned run count, written into this plan. Both input plans budgeted a run; neither budgeted the
  program.

**Rollback.** Delete the scripts; nothing references them yet.

**Definition of done**

- [ ] AT-P5.1 … AT-P5.7 pass.
- [ ] **Version bumps:** none.
- [ ] **Gate registration:** the **per-tier must-fail teeth (AT-P5.3)** registers now in all three
      surfaces; the **S2/S4** corpora register at **P6**.
- [ ] **`/code-review`** on the PR — real code.

---

### P6 — Calibration, sabotage corpora, and MDE (the instrument-validity crux)

**Goal.** Determine whether T0 has earned the right to gate anything — and, per RT-3, whether it has
earned it **for rewrite PRs specifically**, which is a narrower question.

**`depends_on_claims`:** `[6]`
**`reversibility`:** two-way-door

**Pre-build gates**

- **G-P6.1 — P4 and P5 both green.** Calibrating an unvalidated set against an unvalidated harness
  measures nothing.

**Build / run**

1. **Agreement study.** 150 cases stratified across clusters; run T0, T1, T2. Compute pairwise
   agreement and — critically — **agreement on the cases where T2 says the routing changed**.
   Overall agreement dominated by easy cases is a vanity number. Report the **T1↔T2 abstention
   divergence separately** (T1#4).
2. **Sabotage corpora — the positive controls. Four, not three:**
   - **S1 — truncation:** every description hard-cut to 120 chars mid-sentence.
   - **S2 — boundary deletion:** every `NOT for X → Y` clause stripped, everything else intact.
     *This is the central failure mode.*
   - **S3 — homogenisation:** every description rewritten to the same generic template.
   - **S4 — [RT-3, NEW] keyword tail:** every boundary clause replaced by a bare comma-separated
     list **retaining every high-IDF token**. **T0 must fail S4 as a pre-condition of T0 gating a
     rewrite PR.** **Expect it to fail this test** — S4 preserves T0's entire lexical signal, so T0
     structurally cannot distinguish a boundary clause from a keyword tail. T0 is not an independent
     examiner of the rewriter; **it is the rewriter's own objective function used as its examiner.**
3. **Null-change study.** Apply a semantically-null edit (whitespace, a synonym swap changing no
   trigger token) and confirm **no tier reports a regression**. A harness that flags noise as
   regression will be ignored within a month.
4. **[RT-7a] Compute the MDE at the planned N and σ, before freezing any threshold**, using the
   effect size P1 produced.
5. Record everything in `evals/skill-routing/calibration-v1.json` with a **`valid-until`** date and
   the list of what invalidates it (model change, corpus drift >10%, golden-set version bump).

**Acceptance tests**

- **AT-P6.1** — T0 vs T2 agreement on the stratified sample ≥ a **pre-registered** floor (registered
  *before* looking at the result).
- **AT-P6.2 — S2 must fail every tier.** If T0 passes a corpus with all disambiguation clauses
  deleted, **T0 is disqualified from gating** and the CI lane escalates to T1.
- **AT-P6.3** — S1 and S3 fail every tier.
- **AT-P6.4 — [RT-3] S4 must fail T0 for T0 to gate a rewrite PR.** If T0 passes S4 — the expected
  outcome — then **T0 is disqualified for the rewrite lane specifically**, and the per-PR gate on
  *rewrite* PRs must be **T1 or T2**. **Say this out loud in the shipped plan rather than shipping a
  proxy blind to its own failure mode.**
- **AT-P6.5** — The null change passes every tier. *(false-positive floor)*
- **AT-P6.6** — The calibration record carries an expiry and names what invalidates it.
- **AT-P6.7 — [RT-7]** The MDE is computed and recorded. **If MDE > the P1 effect size, this plan
  must state that the per-wave gate cannot detect the effect it exists to detect**, and the
  detection burden moves to P13's scheduled aggregate run.

**Contingency.** If AT-P6.2 fails for T0, do **not** proceed with a proxy-based CI gate: the CI lane
becomes T1 on a **reduced per-PR case set** (only clusters touched by the diff), and the program
absorbs a real per-PR cost. If AT-P6.4 fails (T0 passes S4), the same escalation applies to rewrite
PRs only.

**Rollback.** Delete the calibration artifacts; no production surface touched.

**Definition of done**

- [ ] AT-P6.1 … AT-P6.7 pass, or their contingencies are executed **and written into the plan**.
- [ ] **Version bumps:** none.
- [ ] **Gate registration (all 3 surfaces, now — m8):** the **S2 boundary-deletion** teeth test and
      the **S4 keyword-tail** teeth test. `gap-delta.md` §9 is explicit that batching these behind
      the standing gate leaves *"arguably the single most important regression guard in the whole
      plan"* unregistered through the entire rollout — the exact window where a regression on that
      failure mode does the most damage. Register: (1) body block after the dispatcher with
      must_fail/must_pass; (2) `N)` dispatcher arm; (3) `Supported:` list.
      `check-gate-registration.py` exits 0.
- [ ] **`/code-review`** on the PR — real code.

---

### P7 — WAVE 1: top-decile-only rewrite (95 files) **[T2, T5#1]**

**Goal.** The first mutating phase. 95 files, ~9.9% of corpus mass, ~10% blast radius, full
treatment, 100% human review.

**`depends_on_claims`:** `[1, 5, 6]` — **and every claim-6 citation in this phase is capped to a
single reversible file and flagged**, per the claim's owner-gate, unless P1 earned the apparatus.
**`reversibility`:** two-way-door **for the git operation** (single PR, one `git revert`, plus a
byte-exact restore from `description-baseline.json`) — but see P10 for why the *distributed* effect
becomes one-way from the first merged wave.

**Pre-build gates**

- **G-P7.1** — P2, P3, P6 green, including AT-P6.2 and AT-P6.4's contingency if triggered.
- **G-P7.2 — A frozen baseline eval run** on the untouched corpus exists **with its scores
  committed**. There is no "after" without a recorded "before", and the before must be recorded
  *before* the rewrite, not reconstructed afterward.
- **G-P7.3 — [T2#3] Wave 1 is NOT "mechanically trim to p75".** The top decile is
  disproportionately the `router` category — `claude-api` and its shape are trigger tables that are
  **legitimately long**. Wave 1 is "the 95 highest-mass files get the full rewrite-and-review
  treatment, and some of them will correctly come out barely shorter." Any file that legitimately
  cannot compress is recorded as a **declared, reasoned exemption**, not as a failure.
- **G-P7.4 — [RT-6(2)] The rewriter is a repo-root `scripts/` tool.** A rewriter placed under a
  plugin's `scripts/` will be **denied at execution time, mid-rollout** — `ravenclaude-core/{hooks,scripts}/`
  are Bash-denied even read-only, and the guard cannot distinguish a command from a description of
  one.
- **G-P7.5 — [RT-6(1)] Advisory delivery verified in the REWRITE execution context**, not just an
  interactive one. The rewrite runs as a script or a batched subagent / headless `claude -p` loop,
  where the in-loop `additionalContext` path is not the surface the hook was designed against.
  Verify by **A/B on the live hook**, not by reading a version string — *merged ≠ live*, and the
  plugin cache is version-keyed.

**Build**

1. `scripts/rewrite-skill-descriptions.py` (repo-root):
   - deterministic pre-pass (P2 `--fix`);
   - **fence extraction** — disambiguation clauses and high-IDF tokens marked must-preserve, plus
     B's belt: *preserve verbatim where possible*;
   - LLM rewrite in batches of ~20, each batch carrying the **same frozen exemplar bank and the same
     style contract version** (consistency comes from a constant prompt, not a constant model mood);
   - deterministic post-validation via the P2 linter **including RT-3's structural check** on every
     output — a failing rewrite is **rejected, re-attempted once, then escalated to a human queue**,
     never accepted;
   - a **rejection budget**: >10% of a batch failing post-validation **aborts the whole batch** and
     surfaces the prompt/contract defect.
2. Select the 95 top-decile files **cross-plugin** from `description-baseline.json`.
3. **100% human review** of all 95. *(95 files is a number a human genuinely reads — which is what
   makes plan-B's "a human reads every rewritten description" affordable at pilot scale, and defers
   the relaxation question instead of answering it from fatigue.)*
4. Full T0 + T1 + T2 run; diff against the G-P7.2 baseline.

**Acceptance tests**

- **AT-P7.1** — Wave-1 reduction measured and **reported as the actual number in the chosen unit**
  (chars **and** tokens). **Do not round up to an inherited target**; there is no percentage
  commitment in this wave (T2#4).
- **AT-P7.2 — Zero regression** on recall@1, recall@5, MRR, false-fire rate, sibling-confusion, and
  abstention accuracy — each within ε of baseline or better — on T0, T1, **and** T2. **[RT-7 caveat]**
  "Zero regression" is a **null result**; read it against the MDE from AT-P6.7, not as proof.
- **AT-P7.3 — Precision does not degrade even if recall improves.** A rewrite that raises recall by
  broadening descriptions while raising false-fire is a **failure**, not a win. Stated explicitly
  because the aggregate score hides it.
- **AT-P7.4** — 100% of rewritten descriptions pass the P2 linter, **including the structural
  preservation check**.
- **AT-P7.5** — Human review of all 95 finds **zero** deleted disambiguation boundaries.
- **AT-P7.6** — Re-running the rewriter on the same inputs with the same seed/version produces
  outputs passing the same validators, and **the diff between two runs is reported** — wild
  disagreement means the consistency story for later waves is unproven.
- **AT-P7.7 — [m2 verbatim]** The human-written 60-case acceptance subset shows no regression.
  **If the synthetic set says "fine" and the human set says "worse", the human set wins and the wave
  fails.**
- **AT-P7.8 — [RT-3]** Confirm the human 60-case subset was **not** read by any rewriter iteration.
- **AT-P7.9 — [T2#3]** Every file that came out barely shorter carries a **declared, reasoned
  exemption**, and the exemptions are counted in the PR body.

**Rollback.** `git revert` the wave-1 PR; or
`scripts/skill-description-baseline.py --restore` rewrites every description back to its committed
baseline bytes. **The restore path is rehearsed here on a scratch branch and its output verified
byte-identical to `git show` of the pre-rewrite tree — an unrehearsed restore path is not a rollback
plan.** A `restore/descriptions-<date>` branch + tag is cut before this PR merges.

**Definition of done**

- [ ] AT-P7.1 … AT-P7.9 pass.
- [ ] **Version bumps:** **every plugin with a changed `SKILL.md` gets a `version` bump in the same
      PR** (RT-4's automatable assertion). Then `python3 scripts/sync-plugin-versions.py` — never
      hand-edit the catalog version. If `ravenclaude-core` is touched, also
      `python3 scripts/generate-copilot-plugin.py` or the freshness gate fails CI.
- [ ] **Wave runbook order (RT-4, non-optional):**
      `commit rewrites → run full audit-gates.sh → version-bump → sync-plugin-versions.py →
      re-stamp ratchet → push`. `audit-gates.sh:2242` runs `git checkout -- "$_f"`; an uncommitted
      version bump at that moment is **silently reverted**, CI's drift gates see no drift because
      both sides reverted consistently, the PR merges green, and **consumers never receive the
      rewrite** because the plugin cache is version-keyed.
- [ ] **Gate registration:** none new here; the standing-gate teeth register at P11.
- [ ] **`/code-review`** on the PR — this phase lands the rewriter **and** 95 content changes.
- [ ] `prettier --write .` → `--check .` exit 0; `ruff check .` exit 0;
      `python3 -m json.tool` on every touched manifest (RT-8).
- [ ] Restore path rehearsed and verified byte-identical; `restore/descriptions-<date>` tag cut.

---

### P8 — RE-DECISION GATE (hard) **[T2#2]** — the program may legitimately stop here

**Goal.** Decide, with real numbers, whether the remaining 20–40% justifies touching 600+ files.

**`depends_on_claims`:** `[2, 4, 6]`
**`reversibility`:** two-way-door (a decision, not a code change)

**Pre-build gate.** P7's acceptance tests are complete and written up, including the human-review
result and the exemption count.

**What is measured.** **Realised token impact — not char impact** (T2#2), against P0's rendering
model. If P0's audit confirmed usage-gating, the measurement must also state the **endogeneity**:
how much of any observed change is attributable to a shift in *which* descriptions render (§2.2).

**Three pre-committed outcomes:**

| outcome | condition | next |
|---|---|---|
| **(a) Proceed broadly** | Measured token reduction materially exceeds the wave-1 cost, zero high-severity regressions, human review clean | → **P9** then **P10** across the corpus |
| **(b) Proceed on the next decile only** | Reduction real but modest; marginal value of the tail unproven | → **P9**, then **P10 limited to decile 2**, then re-run this gate |
| **(c) STOP** | Injected subset is small (RT-1 confirmed), or savings are cache-reads at ~0.1×, or the effect does not justify 600+ files | → **Ship the linter + ratchet + wave 1 as the complete deliverable.** `tiebreaks.md`: *"T2's re-decision gate is where the program most plausibly stops, and that is a legitimate outcome, not a failure of this run."* `red-team.md` §2: *"linter + ratchet + top-decile trim is the subset of this program that survives RT-1 being true."* |

**Acceptance tests**

- **AT-P8.1** — The measurement is in **tokens**, against the rendering model, with the posture
  named.
- **AT-P8.2** — The outcome is one of (a)/(b)/(c) and is **written down with its reasoning** before
  any further wave begins.
- **AT-P8.3** — If (c), the closing write-up states what was shipped and what was deliberately not
  built — including, if P1 returned null, AT-P1.5's sentence.
- **AT-P8.4** — No outcome is chosen by inheriting `scope.md`'s −30–50%; that number is a variable
  here, not a requirement (T2#4).

**Definition of done**

- [ ] AT-P8.1 … AT-P8.4 pass.
- [ ] The decision is recorded in the run dir **and** in the wave-1 PR thread.
- [ ] **Version bumps / gate registration / `/code-review`:** none — this phase ships no code.

---

### P9 — WAVE 2: `ravenclaude-core` procedure pilot **[T5#2]**

**Goal.** Prove the *procedure* on the single densest disambiguation load, now that wave 1 has
produced real effect-size numbers to calibrate against.

**`depends_on_claims`:** `[1, 5, 6]`
**`reversibility`:** **one-way-door in practice** — see P10.

**Pre-build gates**

- **G-P9.1** — P8 returned (a) or (b).
- **G-P9.2** — `ravenclaude-core` is 26,702 chars / ~8.7% of corpus mass across ~59–85 skills and
  carries the densest disambiguation load (e.g. `cheap-lane-delegation` ↔ `session-handoff` mirror
  clauses; `repo-review` vs the built-in `/code-review`). **Piloting on an easy plugin proves nothing
  about the hard case.**

**Build.** The P7 rewriter, unchanged, on `ravenclaude-core`. **100% human review of every
`disambiguating` and `router` category rewrite** — a bounded, countable number.

**Acceptance tests.** AT-P7.1 … AT-P7.9 re-applied to this plugin, plus:

- **AT-P9.1 — [m5] The human-review exit criterion is decided by data, not fatigue.** If this pilot's
  human review finds **zero** boundary deletions across the entire `disambiguating` + `router`
  subset, P10 may drop to sampled review (**100% of `router`, 20% of `disambiguating`, 0% of
  `leaf`**) with the deterministic validators covering the rest. If it finds **any**, human review
  stays at 100% for those categories and the wave size shrinks accordingly. *(plan-B's alternative —
  permanent 100% across all 182 batches with no reduction path — is rejected: a proven procedure on
  a 50-file pilot is not a proven procedure on file #700 with a reviewer who has stopped reading
  closely, but the answer to that is data, not a permanent tax.)*

**Definition of done**

- [ ] All P7 acceptance tests + AT-P9.1 pass.
- [ ] **Version bumps:** `plugins/ravenclaude-core/.claude-plugin/plugin.json` bumped →
      `sync-plugin-versions.py` → **`generate-copilot-plugin.py`** (mandatory for this plugin, or the
      freshness gate fails CI).
- [ ] **Wave runbook order** (RT-4) followed exactly.
- [ ] **Gate registration:** none new.
- [ ] **`/code-review`** on the PR.

---

### P10 — WAVES 3+: mass-ordered value, overlap-ordered review depth **[T5#3–#5]**

**Goal.** Roll the proven procedure across the remaining plugins.

**`depends_on_claims`:** `[1, 2]`
**`reversibility`:** **one-way-door.** The git revert is available for days; but once consumers pull
a version-bumped plugin via `/plugin marketplace update`, the old descriptions are **distributed and
cannot be recalled — only superseded by a newer version**, and once N later PRs touch the same files
a mass revert is a merge-conflict exercise, not a button. **plan-B's "two-way-door per batch" is
optimistic in the phase with the largest blast radius; plan-A's forward-fix policy wins** (T5#5).

**Pre-build gates**

- **G-P10.1** — P9 green, including AT-P9.1.
- **G-P10.2 — Per-wave worktree hygiene.** One worktree per wave; `~/RavenClaude` stays on `main`;
  the ratchet is stamped **after** commit and **re-stamped before merge**. An **empty
  `forge/<slug>` branch is a LIVE run, not stale** — the natural cleanup reflex is destructive here.
  Verify `%p` has **two parents** before pushing any wave merge (`rerere` can yield a one-parent
  commit whose tree is a correct merge).
- **G-P10.3 — [RT-5]** Wave PRs **do not touch `description-budget.json`** — the ceiling is derived
  (P3). If the derived design was abandoned, waves **serialise**; say which regime is in force.

**Build**

- **Order (A's axis — value):** by measured char/token mass. After the top decile and
  `ravenclaude-core`: `power-platform` (10,544), `finance` (8,989), `edtech-partner-success` (7,682),
  `report-regeneration` (7,452), `web-design` (6,091), `data-platform` (5,732),
  `regulatory-compliance` (3,604), `staffing-operations` (2,918),
  `hoa-community-association-management` (2,623), `hospice-referral-sales` (2,533),
  `ai-coding-model-guidance` (2,506) — the top 12 are ~28% cumulative. Long tail batched 10–15
  plugins per PR.
- **Review depth (B's axis — exposure):** high-cluster-overlap plugins get the full adversarial eval
  + 100% human review of `disambiguating`/`router`; solo-skill plugins get linter + sampled review.
- **Packaging:** per-plugin PRs (both plans agree).
- **[RT-7c] The cross-wave regression core GROWS** with each landed wave. A fixed core leaves a
  coverage hole that widens monotonically as the rollout proceeds.
- **[RT-7b] Import plan-B's aggregate drift tracker** — the full golden set run on a schedule and
  **tracked over time**, so a slow, PR-by-PR erosion where each step is individually under the
  per-PR threshold is still visible in aggregate. **plan-A has no equivalent.** (Built in P13.)

**Acceptance tests (per wave, all must hold)**

- **AT-P10.1** — Wave reduction measured and reported in the chosen unit; corpus total strictly
  decreases (or the wave carries a declared budget-raise justification).
- **AT-P10.2 — Zero routing regression** on the wave's clusters **and** on the **growing** cross-wave
  regression core. A wave can degrade a *neighbouring* plugin's precision by broadening its own
  descriptions — this is why waves are not independent.
- **AT-P10.3** — T2 on the wave's clusters shows no regression.
- **AT-P10.4** — 100% linter pass, including structural preservation; zero un-exempted cap
  violations introduced.
- **AT-P10.5** — The per-G-P10.2 human-review sample finds **zero** boundary deletions. **Any finding
  halts the wave train and returns to the rewriter** — it is not patched per-file and waved on.
- **AT-P10.6 — [RT-4, automatable]** Every plugin with a changed `SKILL.md` has a `version` bump in
  the same PR.
- **AT-P10.7 — [RT-8]** `generate-copilot-plugin.py` re-run where required; `prettier --check .`
  exit 0 whole-tree; `ruff check .` exit 0; every touched manifest valid JSON.
- **AT-P10.8** — Final full-corpus acceptance (only if P8 chose (a)): the corpus total meets the
  target **re-decided at P8**, with every metric within ε on the human 60-case subset.
- **AT-P10.9 — the number to put in the PR body:** a **full T2 pass on the human-written acceptance
  subset** shows no regression versus the P7/P9 baseline. This is the only number in the program
  produced by **real agent runs on human-written prompts against the final corpus**.

**Rollback.** Per-wave: each wave PR is a single squashed commit whose SHA is recorded in the run
dir, so a single-wave revert is one command. **Consumer-facing: if a routing regression is discovered
post-distribution, the fix is a forward version bump restoring the affected descriptions, not a
yank.** State this in the wave-1 PR body so nobody plans for a recall that does not exist.

**Definition of done (per wave)**

- [ ] AT-P10.1 … AT-P10.9 pass for that wave.
- [ ] **Version bumps:** every touched plugin bumped in-PR; `sync-plugin-versions.py` run;
      `generate-copilot-plugin.py` run for `ravenclaude-core`.
- [ ] **Wave runbook order followed exactly** (RT-4).
- [ ] **Gate registration:** none new per wave; **AT-P10.6's bump assertion** registers once, in all
      three surfaces, at the first wave that uses it.
- [ ] **`/code-review`** on every wave PR — each lands real content changes to distributed plugin
      surfaces.
- [ ] Worktree hygiene verified (G-P10.2); merge commit has two parents.

---

### P11 — Standing gate (advisory-first → blocking) **[m3, T4, RT-2]**

**Goal.** The permanent half of the deliverable: new and edited skills stay in budget without a
human remembering to check.

**`depends_on_claims`:** `[1, 3, 4]`
**`reversibility`:** two-way-door **while advisory**; the **promotion to a required status check is
a one-way-door step**.

**Pre-build gates**

- **G-P11.1** — Wave 1 merged (the gate needs a real ceiling to sit on).
- **G-P11.2 — Required-check hazard review.** Per `AGENTS.md`/`CLAUDE.md`: a required workflow **must
  not carry `paths:` on its `pull_request` trigger**, or the PR hangs Pending forever. Gate the
  **step** with an `if:`, never the workflow. Write this as a comment **next to the trigger**, where
  the next person will see it.
- **G-P11.3 — Fire-rate budget stated numerically before shipping** (e.g. ≤3%, mirroring the 2.588%
  design target from the cause-taxonomy precedent). A gate with no stated fire budget cannot be
  judged noisy; it can only be resented.

**Build**

1. **Hook (advisory, in-loop, never blocks)** — `PostToolUse` on `Write|Edit` touching a `SKILL.md`,
   delivering the over-budget notice via **`additionalContext`** — *live to the model, silent to the
   terminal* (the split-delivery pattern from PR #1085, where four advisory hooks fired far above
   their 2.588% design target and the fix was split delivery, **not** a blanket disable).
   **`stderr`-at-exit-0 reaches the model on NO event; do not use it.**
2. **CI check** `.github/workflows/validate-skill-descriptions.yml` running
   `scripts/check-skill-descriptions.py --ratchet --diff-scoped`:
   - **[T4#3 / RT-2] fails on `over-cap OR total-above-committed-ceiling`** — never plan-A's AND;
   - legacy over-cap files never fire (ratchet, not absolute);
   - honours `description_budget_exempt: <reason>` and **reports every exemption in the job
     summary** — an exemption you must write down is honest; a silent bypass is what makes people
     delete the gate;
   - runs the calibrated tier (T0 if it earned it in P6; **T1 or T2 on rewrite PRs if AT-P6.4
     disqualified T0**) on the clusters touched by the diff, gating on Δ within ε;
   - **[RT-2] the ceiling is derived and only a labelled budget-raise PR may move it upward.**
3. **Advisory window** — ≥2 weeks / ≥20 PRs, non-blocking, logging every would-have-fired to
   `.ravenclaude/runs/description-budget/`.
4. **Self-audit** — `--health` computes the observed fire rate and false-positive rate (fires later
   exempted or overridden) and fails **its own audit**, not the PR, when over budget. *Never
   "someone turns it off."*

**Acceptance tests**

- **AT-P11.1** — On an unmodified `main`, the gate is **silent**. Zero fires across the legacy
  corpus. *(the single most important false-positive test — a gate that fires on the status quo is
  dead on arrival)*
- **AT-P11.2 — Must-fail teeth:** a PR adding a 900-char `leaf` description fails.
- **AT-P11.3 — Must-pass:** a PR adding a 900-char `router` description **with** a declared, reasoned
  exemption passes, and the exemption appears in the job summary.
- **AT-P11.4 — Ratchet teeth, single-PR:** trim one description by 10 and bloat another by 300 ⇒
  fails.
- **AT-P11.5 — [RT-2] Ratchet teeth, TWO-PR:** PR#1 shrinks by 300 and the ceiling re-stamps; PR#2
  grows an **under-cap** description by 290 ⇒ **must fire**. *This is the test plan-A did not have,
  and without it the standing gate is decorative while continuing to report green.*
- **AT-P11.6** — Measured fire rate over the advisory window is within the G-P11.3 budget. **If it is
  not, the gate is not promoted — it is recalibrated.**
- **AT-P11.7 — [RT-6(1)]** The hook's advisory text **reaches the model**, verified by **A/B on the
  actual hook** — including in the **rewrite execution context**, not only an interactive one.
  Not by reading a version string: *merged ≠ live*, and the plugin cache is version-keyed.
- **AT-P11.8** — The workflow file has **no `paths:`** on its `pull_request` trigger, or is provably
  not a required check. *(automatable; add to the workflow-hygiene checker)*
- **AT-P11.9** — The stamp-ordering comment (P3 build item 5) is present next to the stamp step.

**Rollback / kill switch**

- **While advisory:** delete the workflow; remove the hook entry. Zero blast radius.
- **After promotion (the one-way-door step):** **(a)** a documented single-line
  `if: ${{ vars.SKILL_DESC_GATE != 'off' }}` on the **step**, flipping a repo variable to disable in
  seconds without touching the ruleset; **and (b)** removal from the required-checks ruleset, which
  needs the owner and is the slow path. **(a) exists specifically so nobody has to reach for (b) at
  2am** — a gate whose only off-switch is a settings change is a gate people route around.
- **Promotion to required requires a FRESH, explicit owner approval.** A prior yes on the advisory
  ship is not approval for the promotion. *(Repo memory is explicit that an admin-merge/bypass-shaped
  permission needs a fresh ask every time.)*
- **Note:** required checks do **not** bind an admin merge in this repo (admin bypass is deliberate),
  so promotion buys discipline, not enforcement against the owner.

**Definition of done**

- [ ] AT-P11.1 … AT-P11.9 pass.
- [ ] Advisory window completed with a **measured** fire rate (verify by injecting one synthetic fire
      and confirming it appears — a `0` because nothing was logged is not a fire rate).
- [ ] **Version bumps:** if the hook ships inside `plugins/ravenclaude-core/hooks/`, bump
      `plugin.json` → `sync-plugin-versions.py` → `generate-copilot-plugin.py`, and register the hook
      in **both** required wirings: the plugin canonical `plugins/ravenclaude-core/hooks/hooks.json`
      (`${CLAUDE_PLUGIN_ROOT}` paths, what consumers get) **and** the marketplace-dev mirror in
      `.claude/settings.json` (`${CLAUDE_PROJECT_DIR}` paths, what fires while editing the
      marketplace). Missing the second means the *installed, possibly stale* plugin's hook fires
      instead of the one under development.
- [ ] **Gate registration (all 3 surfaces):** **gate silence on unmodified `main` (AT-P11.1)**, the
      **single-PR ratchet teeth (AT-P11.4)**, and the **two-PR ratchet teeth (AT-P11.5)**.
      Register each as: (1) a `── Gate N: … ──` header block with `gate "…" must_fail` /
      `gate "…" must_pass` in the **full-suite body after the dispatcher** — never only inside the
      dispatcher arm, which is precisely the Gate 184 defect (unreachable for an entire release while
      the suite printed "all gates audited and verified bidirectional"); (2) an `N)` **case arm** in
      the `--check <n>` dispatcher; (3) the number in the `*)` arm's **`Supported:`** list — the two
      dispatcher surfaces are independently hand-maintained and each is the other's oracle. Then
      `python3 scripts/check-gate-registration.py` exits 0.
- [ ] **Exit-2 specificity:** because this gate drives a `PreToolUse`-adjacent advisory path, any
      teeth test asserting only `must_fail` (any nonzero) would pass a hook exiting 1 — which Claude
      Code treats as **non-blocking** and runs the command anyway. Assert the specific exit code.
- [ ] **`/code-review`** on the PR — real code (workflow, linter wiring, hook).
- [ ] `scripts/audit-gates.sh` **full run on a clean tree**, edits committed first (RT-4).

---

### P12 — Gate registration discipline (incremental, not a terminal phase) **[m8]**

**Goal.** Ensure every teeth test is registered **when its phase lands**, and that the audit suite
itself stays honest.

**`depends_on_claims`:** `[]`
**`reversibility`:** two-way-door

**This phase is a standing obligation, not a batch.** `gap-delta.md` §9 and `tiebreaks.md` m8: only
two of plan-A's five registrations genuinely depend on the standing gate. Batching all five behind it
leaves the S2 boundary-deletion teeth test — *"arguably the single most important regression guard in
the whole plan"* — unregistered through the pilot, the procedure wave, and the entire rollout: the
exact window where a regression on that failure mode does the most damage.

**Registration schedule**

| teeth test | registers at |
|---|---|
| Baseline determinism + mutation (AT-P0.1/.2); charset round-trip (AT-P0.7) | **P0** |
| Linter cap + **structural** preservation (AT-P2.2/.3); charset reject (AT-P2.7) | **P2** |
| Single-PR ratchet (AT-P3.2); posture drift (AT-P3.5) | **P3** |
| Golden-set self-consistency (AT-P4.6) | **P4** |
| Per-tier must-fail (AT-P5.3) | **P5** |
| **S2 boundary-deletion** and **S4 keyword-tail** corpora (AT-P6.2/.4) | **P6** |
| Version-bump-in-same-PR assertion (AT-P10.6) | **first wave using it** |
| Gate silence on `main` (AT-P11.1); **two-PR** ratchet (AT-P11.5) | **P11** |

**Standing rules (apply to every registration above)**

- **Claim gate numbers by reading the current max at the moment of writing** — measured **263** this
  session (A's "~281" and B's "261" are both stale) — and **re-check before merge**. Number
  collision is a catalogued defect (the two-Gate-104 collision).
- **All three surfaces, every time** (see any phase's DoD for the full wording).
- **Bidirectional or it does not count:** proven to **fail on bad** and **pass on good**.
- **A skip is not a pass.** A missing dependency prints `THIS IS NOT A PASS` and is a **hard failure
  in CI**, never a silent skip.
- **`covers[]` entries never watch a toolchain-rewritten file** — `prettier`/`ruff` rewrite files; a
  gate watching one is self-invalidating.
- **Read `docs/best-practices/ci-gate-audit.md` first** — required reading before adding or changing
  any CI step.
- **Run the full `audit-gates.sh` on a clean tree, and version-bump only AFTER it completes** — the
  suite's teeth tests `git checkout` files and will silently revert uncommitted `plugin.json` /
  `marketplace.json` edits (RT-4).

**Acceptance tests**

- **AT-P12.1** — Every registered gate is **reachable in the full suite**, not only via the
  `--check <n>` dispatcher arm.
- **AT-P12.2** — No gate-number collision; dispatcher arms and the `Supported:` list agree exactly.
- **AT-P12.3** — Every new gate is genuinely bidirectional.
- **AT-P12.4** — No gate is a skip-that-reads-as-a-pass.
- **AT-P12.5** — `python3 scripts/check-gate-registration.py` exits **0** after every registration.

---

### P13 — Steady-state operations

**Goal.** Keep the instruments honest after the rollout, and detect the drift that would silently
invalidate them.

**`depends_on_claims`:** `[3, 4, 6]`
**`reversibility`:** two-way-door

**Build**

1. **Scheduled recalibration.** The P6 calibration carries an expiry. A monthly job re-runs the
   T0↔T2 agreement study on a fresh stratified sample and **fails loudly** when agreement drops
   below the pre-registered floor — **T0's authority is borrowed and it expires.** Triggered early
   by a model change, a golden-set version bump, or >10% corpus drift.
2. **[RT-1] Membership canary — not a format canary.** plan-B proposed a monthly canary diffing the
   captured listing's **format** against a fixture. **RT-1 shows that is blind to the drift that
   actually matters:** the fixture is a snapshot of one user's invocation history at one instant, it
   drifts every time a skill is used, and it is not portable to any other consumer. The canary here
   diffs **membership** — which skills' descriptions are rendered — against the P0 rendering model,
   and fails when the injected subset moves.
3. **[RT-7b] Aggregate drift tracker (imported from plan-B, which plan-A lacks).** The full golden
   set runs on a schedule (**not** per-PR, per the cost decision) and is **tracked over time**, so a
   slow, PR-by-PR erosion of routing quality — each step individually under the per-PR threshold —
   is still visible in aggregate. This is the instrument that carries the detection burden if
   AT-P6.7 showed MDE > effect size.
4. **Golden-set refresh.** New skills get cases generated automatically (a new skill with no eval
   case is itself a **warn-level** gate finding). **Cluster membership is recomputed, not assumed
   static** — this is where a *new* sibling silently degrades an *old* skill's precision.
5. **Continued transcript mining.** The mined set (48 invocations / 24 skills today) will grow. Once
   mined coverage exceeds ~15% of skills, re-run the leakage probe with the mined set as the
   reference — that is when the synthetic set can finally be validated against reality at scale.
6. **Gate health reporting.** Monthly fire-rate / false-positive-rate summary. Over budget ⇒
   recalibrate or **auto-demote to advisory**. Never "someone turns it off."
7. **Budget ratchet review.** Whether the ceiling can move down further, judged against the measured
   routing metrics, **not against ambition**.

**Acceptance tests**

- **AT-P13.1** — The recalibration job has run and reported at least once, output in the run dir.
- **AT-P13.2 — Must-fail teeth:** a deliberately-blinded T0 (scorer returning constant scores)
  causes the recalibration job to **fail**. A self-checking system that cannot detect its own
  detector being disabled is the **self-disabling-detector** defect this repo has catalogued.
- **AT-P13.3 — [RT-1] Must-fail teeth on the membership canary:** deliberately alter the recorded
  rendering model and confirm the canary fires. A canary that only checks format would pass this.
- **AT-P13.4** — A newly added skill with no golden-set case produces a warn-level finding within one
  cycle.
- **AT-P13.5** — The gate health report carries a **real** fire rate — verified by injecting one
  synthetic fire and confirming it appears, not a `0` because nothing was logged.
- **AT-P13.6** — The aggregate drift tracker has ≥2 datapoints and its trend is plotted/reported.

**Definition of done**

- [ ] AT-P13.1 … AT-P13.6 pass.
- [ ] **Version bumps:** as applicable if any scheduled job ships inside a plugin.
- [ ] **Gate registration (all 3 surfaces):** **T0-blinding teeth (AT-P13.2)** and **membership-canary
      teeth (AT-P13.3)**; `check-gate-registration.py` exits 0.
- [ ] **`/code-review`** on the PR — scheduled workflows are real code.

---

## 8. Appendix — phase index

| phase | `depends_on_claims` | `reversibility` | tiebreak/red-team amendments folded in |
|---|---|---|---|
| **P0** Rendering & unit audit | `[1, 2, 3, 4]` | two-way-door | RT-1 (both probe arms), m6 (discrepancy demoted), m7 (claim-4 instruments + scope.md correction), C2/C3/X4 (tokenize + benefit unit), X11 (posture pin), m9 (gate re-count), §6 waiver sentence, RT-8 (charset) |
| **P1** Claim-6 effect-size study | `[6]` (tests, does not cite) | two-way-door | **T3** in full (3 arms, ~40 skills, ≥12 clusters, pre-registration, power calc, mandatory RT-1 positive control, both outcomes pre-committed, the null sentence) · T1#2 (ablation pre-flight) |
| **P2** Style contract + linter | `[1, 2]`; `[6]` for preservation | two-way-door | m4 (A's sandwich + B's belt), **RT-3** (structural not just token preservation), RT-8 (charset), T3 (preservation half conditional), RT-6(2) (repo-root `scripts/`) |
| **P3** Budget artifact + ratchet | `[1, 2, 4]` | two-way-door | **T4** all three amendments (chars+tokens, posture pin, **OR**-condition), **RT-2** (two-PR gaming + stamp ordering), **RT-5** (derived ceiling) |
| **P4** Golden set | `[1, 3, 6]` | two-way-door | m1 (anti-echo + leakage probe + N scaled to authorised scope; B's stratified tail), m2 (human set wins, verbatim), **RT-3** (quarantine the human subset), B's positive control |
| **P5** Eval ladder T0/T1/T2 | `[3, 5]` | two-way-door | **T1** #1–#5 (ablation mode, pre-flight, B's realistic-listing import **corrected by RT-1**, T1↔T2 abstention divergence, expiry discipline), X13 (program cost) |
| **P6** Calibration + teeth + MDE | `[6]` | two-way-door | **RT-3** (S4 keyword-tail corpus + T0 disqualification for the rewrite lane), **RT-7a** (MDE before thresholds), T1#5 |
| **P7** Wave 1 — top decile (95) | `[1, 5, 6]` | two-way-door (git); one-way once distributed | **T2** #1/#3/#4, **T5#1**, RT-6(1)(2), m2, RT-3 |
| **P8** Re-decision gate | `[2, 4, 6]` | two-way-door | **T2#2** (three pre-committed outcomes, token not char, STOP is legitimate), RT-1 endogeneity |
| **P9** Wave 2 — `ravenclaude-core` | `[1, 5, 6]` | **one-way-door** | **T5#2**, m5 (data-driven review off-ramp) |
| **P10** Waves 3+ | `[1, 2]` | **one-way-door** (restore script + pre-wave tag + forward-fix policy) | **T5#3/#4/#5**, **RT-4** (wave runbook + bump assertion), **RT-5** (no artifact contention), **RT-7b/c** (aggregate tracker + growing core), RT-8 |
| **P11** Standing gate | `[1, 3, 4]` | two-way-door advisory; **one-way-door** on promotion | **m3** (all five A mechanisms), **T4#3 / RT-2** (OR-condition + two-PR teeth), RT-6(1) (hook A/B in the rewrite context), fresh owner approval for promotion |
| **P12** Gate registration | `[]` | two-way-door | **m8** (incremental, not batched), m9 (re-count), Gate-184 three-surface rule, exit-2 specificity |
| **P13** Steady-state ops | `[3, 4, 6]` | two-way-door | **RT-1** (membership canary replaces B's format canary), **RT-7b** (aggregate drift tracker imported from B), self-disabling-detector teeth |

---

## 9. What this plan does not claim

- It does **not** claim Claude Code omits skill descriptions in main sessions. The observation is
  from **two subagent sessions**, with a positive control (agents rendered ~150/150), and nine
  hypotheses rejected without isolating the cause. **The probe that splits the classes is named in
  §2.3 and costs minutes.**
- It does **not** claim claim 6 is false. It claims **neither input plan could find out**, because
  both wired the answer in as a requirement — and it specifies the study (P1) that can.
- It does **not** claim the effort is not worth doing. It claims **no artifact in this run yet states
  what it is worth in a measurable unit**, and that RT-1, C2 and C3 must be settled (P0) before that
  sentence can be written honestly.
- It does **not** claim the corpus totals are wrong: 310,359 / 307,672 / 308,229 across three
  independent measurements is a 0.9% spread, **inside the error bars**, and it is deliberately
  demoted from a blocker to a P0 deliverable.
