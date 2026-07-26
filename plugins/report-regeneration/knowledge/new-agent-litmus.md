# New-agent litmus — `report-regeneration-engineer`: **FOLD, do not create**

> **Status:** Phase-1 exit gate, decided **against real code** (plan §5 Phase-1 / §9, binding TB-5).
> This is the settlement the plan deferred so the call would rest on the actual prototype control
> flow, not the a-priori paper description. **Verdict: FOLD into core agents + the shipped skills +
> the `core-architecture-spec.md` knowledge, with the inline priors specified below. Do NOT register
> a `report-regeneration-engineer` agent.**
>
> Permissibility was already settled (`.ravenclaude/runs/forge/report-regeneration/fact-verdicts.md`,
> Conflict #2): **one** new domain agent is *allowed* — but only *iff* it is a genuinely new role,
> not a wrapper around `data-engineer` + skills. This file discharges the "genuinely new role?"
> question. The answer, on the evidence below, is **no**.

---

## The litmus question (verbatim, from the plan)

> *"Could a competent core agent (`data-engineer` + `backend-coder`) — handed these skills + the
> RSG/manifest/harness knowledge — orchestrate the infer→manifest→rebind→harness→QA→loop pipeline
> and produce indistinguishable output? Or is there genuine operational craft (like data-platform's
> `connector-developer` / power-platform's `dataverse-architect`) that a core generalist lacks?"*

**Answer: yes to the first, no to the second.** A core `data-engineer` driving the pipeline, with
`backend-coder` maintaining the stdlib output engine, produces output *indistinguishable* from a
dedicated agent's — because the domain craft has been **externalized into deterministic,
schema-validated skill code + one authoritative knowledge file**, not left as tacit judgment an
agent must carry in its head.

---

## The single strongest piece of evidence: the orchestrator is already a script

`scripts/e2e_acceptance.py` **is** the infer→manifest→rebind→harness→QA orchestrator, and it runs the
whole pipeline **with zero agent reasoning in the loop**. It `importlib`-loads the five stage modules
and drives their Python APIs in a linear composition:

```
infer.build_rsg  →  build_manifest.run  →  (amend data_query)  →  rebind_html.rebind
                                                                →  harness.run_harness  →  qa_gate.build_result
```

If a **plain stdlib script** can compose the pipeline end-to-end and settle both Phase-1 bets, then a
`backend-coder` can run and maintain that composition, and a `data-engineer` can supply the one
judgment-bearing step inside it (below). This is exactly the real-code evidence the plan deferred the
litmus to obtain — and it points at FOLD, hard.

---

## Where the judgment actually lives — and it maps onto existing core roles

The pipeline has exactly **two** steps that need judgment rather than mechanical execution. Neither is
a *new* role:

1. **The "human amendment" of the proposed manifest** (`e2e_acceptance.py:68-89`, per
   `core-architecture-spec.md` §3: *inference proposes the manifest, a human amends it*). Concretely:
   point each `surgical`/`regenerate` binding's `data_query` at a concrete new-data cell — a
   **source-cell → target-slot data-mapping** task. That is `data-engineer`'s core competency, and
   §5 already assigns the XMLA/REST data-read + recompute-path authoring to `data-engineer`.
2. **The Phase-5 gold-standard loop convergence decisions** — but the loop *mechanics* (stop =
   PASS/plateau(2)/cap(6), monotonic ratchet, per-node edit budget, N=3 median, do-no-harm zero-diff
   fixture) are **owned by the `report-gold-standard-rubric` skill's contract**. The agent *applies*
   the contract; it does not invent it. Non-convergence escalates to `architect` (already the plan's
   loop-escalation owner). No new role.

Everything else — the earned-frozen rule, the zero-literal construction invariant, V4
decoded-container egress scanning, the leg-to-defect map, `not_captured ⇒ PARTIAL (never a fake
PASS)` — is enforced in **code**, not by an agent remembering to check:

- `qa_gate.build_result` collapses the receipt mechanically; **an agent cannot soften the honest
  guarantee even if it wanted to** — FAIL > PARTIAL > PASS is a code rule.
- `rebind_html._assert_frozen_unchanged` proves frozen nodes didn't move — defensive, not trusted.
- V4 is a **blocking, ML-free** dictionary scan over the decoded container.
- `infer.py` schema-validates the RSG before writing (fail-closed); the earned-frozen demotion is a
  non-inference detector.

The plugin's *entire design philosophy* — "surgeon, not renderer"; "decidable diff, not open-ended
judgment"; "the ML-free legs catch the dominant failure mode" — is a deliberate move **away** from
craft-laden operational judgment **toward** codified determinism. That is the opposite of the profile
that earns a dedicated agent.

---

## Why this is NOT a `dataverse-architect` / `connector-developer` case

The CREATE precedents earn their agents because they carry **tacit platform knowledge that resists
codification** — knowledge that shapes a thousand small design decisions a decision-tree skill can't
capture:

| CREATE precedent | The irreducible tacit craft |
|---|---|
| `power-platform/dataverse-architect` | plug-in execution-pipeline stages, cascade-on-high-volume-child gotchas, customer-column polymorphism traps |
| `data-platform/connector-developer` | per-SaaS OAuth-flow quirks, pagination edge cases, throttling behaviors across dozens of APIs |

`report-regeneration` has no equivalent tacit body. Its hard parts are **the opposite of tacit** —
they are the schemas (`rsg.schema.json`, `binding-manifest.schema.json`,
`fidelity-receipt.schema.json`), the six deterministic checkers, and one authoritative spec
(`core-architecture-spec.md`, which every SKILL cites as *"if this skill and the spec disagree, the
spec wins"*). Hand a core agent those files and it has everything a dedicated agent would have — there
is no residue of judgment that lives only in an agent's character.

---

## The cost side of the ledger (both point the same way)

- **The ~15K agent-description budget** (memory `agent-description-budget`) scales with *enabled-plugin
  count*; every registered agent is a permanent tax on every consumer who enables this plugin. Spending
  it on a role that is `data-engineer` + `backend-coder` + skills is exactly the "thin wrapper" the
  fact-verdicts warned against.
- **Un-shipping a registered agent later is a breaking change** (house rule 3 — a marketplace-visible
  removal). The skills-first, promote-later direction is **additive and reversible**; the create-now
  direction is neither. When the cost of being wrong is asymmetric, take the reversible path.

---

## The FOLD wiring — inline priors (the deliverable)

Fold via **conditional inline priors on the reused core agents** (the same pattern data-platform's
`stack-selection` uses on `ravenclaude-core/architect`, and `jwt-embed-issuance` et al. use on
`ravenclaude-core/security-reviewer` — both already carry report-shaped priors, precedent verified in
`agents/architect.md` + `agents/security-reviewer.md`). Each prior fires only when the engagement is
**report-regeneration-shaped** (an old distributed report used as a template + new data → a same-format
regenerated draft). Wiring lives on the core agent's file; the skills + knowledge stay in this plugin.

| Core agent (never forked) | Inline prior — invoke when report-regeneration-shaped |
|---|---|
| **`data-engineer`** *(primary pipeline driver)* | Drive the pipeline: `infer-report-structure` (stage 1) → `rebind-manifest` (stage 2) → **amend** each `surgical`/`regenerate` binding's `data_query` to a concrete new-data cell (the source→slot mapping) → `powerbi-ingest` when PBI is a source (XMLA/REST data-read + the V1 recompute path) → `report-fidelity-harness` (stage 4) → `report-qa-gate` (stage 5) → `report-gold-standard-rubric` (Phase-5 loop). Authority: `knowledge/core-architecture-spec.md`. |
| **`backend-coder`** | Own/maintain the stdlib **output engine** — `rebind-html` (v0.1.0), `rebind-office` (v0.2.0 lane) — and the pipeline/checker scripts. Honor the macOS bash-3.2 / no-GNU floor (`_rc_timeout`, `_rc_pcre_match`, no `sed -i`). |
| **`security-reviewer`** *(binding, never forked)* | Review the leak-defense spine: the detect→strip→rebind→prove flow, V4 over the **decoded** container, the metadata/comment/tracked-change purge, and **PBI tenant-token handling** (least-privilege, never logged, local-only). Findings here are **un-waivable P0s**. Authority: `knowledge/threat-model-stride.md` + `core-architecture-spec.md` §6. |
| **`architect`** *(never forked)* | RSG closed-node-set review ("a wrong closed set is the most expensive wrong premise"); **loop-escalation** on rubric non-convergence (plateau/cap); the RSG/manifest **schema-change serialization** decision (a schema change re-triggers Phase-1 Bet-1 across formats). |
| **`documentarian`** | QA-report prose from the `report-qa-gate` receipt + the **manual-residue checklist** (never empty — an empty residue over a partially-auto-covered a11y surface is itself an over-claim). |
| **`viz-spec-reviewer`** | Any shipped chart spec on a `regenerate` chart node. |
| **`code-reviewer`** *(never forked)* | The Phase-6 correctness/quality loop over each build lane's diff (§6b). |

**Team-Lead dispatch rule:** for a report-regeneration run, dispatch **`data-engineer`** as the
primary pipeline driver, **`backend-coder`** for output-engine code, and the review loop
(**`security-reviewer`** + **`code-reviewer`**, per §6b) after each lane. No `report-regeneration`
specialist is spawned or needs to exist.

---

## The revisit tripwire (when to re-run this litmus — don't treat FOLD as permanent)

Re-run the litmus **against that lane's real code** (not this HTML-lane code) if a later lane surfaces
genuinely **tacit** operational craft that resists codification into a skill — the CREATE signal this
lane lacked. Concretely, revisit if:

- The **Office (v0.2.0) lane** shows OOXML byte-stability behaves so per-template-idiosyncratically
  that a specialist's per-template judgment call (not a checker) becomes load-bearing — i.e., the
  V2-decidability premise degrades into craft.
- The **Power-BI-ingest (v0.3.0) lane** shows XMLA/REST auth/throttling/tenant-quirk handling that a
  `data-engineer` generalist keeps getting wrong in ways a knowledge file can't fix.
- A cross-lane pattern emerges where the Team Lead **repeatedly mis-routes** report-regeneration work
  because no single agent holds the whole honest-guarantee spine coherently (dispatch ambiguity that
  the inline priors demonstrably fail to resolve).

Because the FOLD path is additive, promotion later costs only the new agent file; nothing shipped has
to be un-shipped. That asymmetry is the whole reason FOLD is the correct Phase-1 call **now**.

---

## Verdict, one line

**FOLD** — the orchestration is a demonstrated stdlib script composition, every invariant is enforced
in code, the two judgment steps map onto `data-engineer` (data mapping) + `architect` (loop
escalation), and the domain craft lives in the shipped skills + `core-architecture-spec.md`, not in
any un-codifiable agent character. Wire it via the inline priors above; keep the ~15K budget and the
one-way un-ship cost unspent.
