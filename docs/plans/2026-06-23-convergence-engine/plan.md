> **FORGE plan** — synthesized 2026-06-23 from a cross-model two-panel review (opus architecture + sonnet pragmatism/skeptic) + a cited G1 research brief on self-improvement-loop failure modes. Both panels independently converged on **a ravenclaude-core SKILL (`refine-to-rubric`), not a plugin** (house-rule test). Route: `use_local`, landing `main`. The non-negotiables: objective signals before any model judge, never same-model self-grade, keep-best/regression-revert, and the engine NEVER claims "perfect" (claim-grounding). Owner: Matt.

# FORGE plan — Convergence Engine ("refine-to-rubric")

A domain-neutral "iterate an artifact until it measurably passes a bounded rubric" capability.
Ships as a **ravenclaude-core SKILL** (not a plugin) + knowledge + a deterministic helper.

## Locked (Matt) + panel-delegated decisions
- General engine (any artifact) with visual-feedback-loop as an OPTIONAL specialization.
- Vehicle + termination delegated to the panels → **both panels: SKILL in core** (house-rule test passes; the data-platform precedent deleted wrapper-agents). **Name `refine-to-rubric`, NOT "iterate-to-perfect"** (claim-grounding applied to the engine itself).

## Grounded findings (G1 researcher, cited 2026-06-23) — the design constraints
- Pure self-critique WITHOUT an external signal does NOT reliably improve and often DEGRADES (Huang et al. 2310.01798, verified numbers). → **objective gates are the primary stop; self-grading is never the sole authority.**
- Self-preference + sycophancy biases are real (2410.21819, 2311.08596). → **the judge must be a DIFFERENT model than the author; "the critic found something" is NOT evidence the artifact was wrong.**
- Goodhart/reward-hacking on any fixed proxy (Gao et al. 2210.10760). → **the rubric is a proxy; cap how hard any one dim is optimized; decomposed binary checks (CheckEval 2403.18771) over one scalar.**
- Rubric derivation from artifact+domain is real but only PARTIALLY automatable (needs a seed taxonomy). → **externalized rubric library, not runtime model-invention.**
- Gains are front-loaded; round-2 regressions are real. → **low iteration cap + keep-best + regression-revert.**

## Synthesis (both panels reconciled)
The loop: **derive-rubric → evaluate (objective gates first, cross-model judge second) → refine (one highest-severity finding) → re-evaluate → terminate (deterministic predicate)**, emitting `argmax`(best) iteration, never the last.
- **Rubric (tiebreak verdict):** externalized versioned library `knowledge/convergence-rubrics.md` (per-artifact-kind dimensions, each bound to an objective signal where one exists) is the SPINE; explicit user requirements are weight-max; an **additive-only LLM "commonly-missed" pass** proposes the unknown-unknowns marked `[unverified — derived]`, surfaced to the human, NOT auto-graded. For `agent-file` → delegate to existing `agent-quality-rubric`.
- **Termination (deterministic, model-free `converge.py`):** stop when ALL of {hard objective gates green, no NEW high/critical findings, score-Δ<ε, score≥floor}; HARD stops on {iteration cap (default ~6), model-call budget (default ~12), regression→revert-to-best}. Verdict vocabulary: `rubric-pass | capped | plateaued | budget-exhausted` — **never "perfect"**; residual gaps reported (Last-Mile).
- **Cost bound (3 layers):** ≤2 model calls/iteration (judge+refine), objective-first short-circuit (broken artifact → 0 judge calls), inherits `runaway-brake.sh`.

## Reuse ledger (NO duplication)
- visual-feedback-loop `driver.py` → the visual objective-evaluator module (subprocess, versioned JSON envelope — unchanged).
- `dod-gate.sh` → OUTER loop (Stop floor); this skill is the INNER mid-task loop (they compose).
- `agent-quality-rubric` → a rubric-library entry (delegated, not reimplemented).
- FORGE model-diversity + P0/P1 severity rubric → the cross-model judge borrows them; `superpowers:verification-before-completion` → the pre-emit check; `.ravenclaude/runs/` + `_emit-event.sh` → per-iteration scorecards (derived labels only, no raw artifact echo).

## Phases + DAG
- **P0** `scripts/converge.py` (terminate predicate + scorecard/score math, MODEL-FREE) + scorecard/rubric JSON schemas — **Gate** (7 termination cases + keep-best argmax + a must-fail half that wrongly converges with a red hard-gate).
- **P1** `knowledge/convergence-rubrics.md` rubric library + `derive-rubric` (retrieval + additive `[unverified]` commonly-missed pass; agent-file delegation) — **Gate** (rubric schema valid, explicit=weight-max, derived dims carry provenance).
- **P2** `evaluate` objective-gate subprocess fan-in (driver.py/svg-lint/declarative-viz/pbir/dod cmd), short-circuit-to-refine, judge only after objective pass — **Gate** (broken artifact ⇒ 0 judge calls; judge-before-gates mutant caught).
- **P3** full loop + `skills/refine-to-rubric/SKILL.md` + cross-model judge (diff backbone) + keep-best + constrained report + inline priors on author agents — **Gate** (e2e flawed fixture converges ≤cap, emits BEST not last, report has no "perfect"; strip-keep-best teeth).
- **P4 (opt-in)** Observe card + `rc converge` verb + optional dod-gate scorecard consult — dashboard render + parity gate.
- DAG: P0 → P1 → P2 → P3 → (P4). Critical path P0→P3.

## Top risks (red-team = researcher failure-modes + Panel B gap-delta)
1. **Self-grading / sycophancy false-"done"** → objective gates first + cross-model judge + deterministic terminate; never the word "perfect".
2. **Rubric reward-hacking** → externalized non-mutable library + additive-only derived dims + deterministic stop outside any model.
3. **Over-polishing / regression** → keep-best argmax + regression-revert + Δ<ε.
4. **Cost blow-up** → call budget + objective-first short-circuit + runaway-brake.
5. **Over-claim ("essentially perfect")** → constrained verdict vocab + plateau-below-floor escalates to human (Last-Mile residual list).
6. **Wrong-kind detection → wrong gates** → kind surfaced for inspection; low-confidence kind → generic rubric + design-checkin pause.
7. **Duplication** → reuse ledger above; this is the INNER loop, dod-gate the OUTER.

## DoD
Each phase: bidirectional gate green; bash -n/ruff/prettier/frontmatter clean; version bump + regen; security-reviewer on the cross-model `claude -p` judge path (P3); core stays domain-neutral.
