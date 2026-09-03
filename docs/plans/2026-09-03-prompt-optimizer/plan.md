# G6 — Synthesized plan: `prompt-optimizer` skill + `/optimize` command

**Status: reconciled, authoritative. Supersedes plan-A.md and plan-B.md as the document to act on.**
Every conflict tiebreaks.md ruled on is restated inline at the phase it governs. Every red-team
finding (1–5) is folded into phase text with an explicit resolution — none is left as a bare "known
risk." Sources merged: scope.md, claims-table.md, plan-A.md, plan-B.md, gap-delta.md, critic-brief.md,
tiebreaks.md, red-team.md.

## Ships DEFAULT OFF

**`prompt_optimizer.enabled: false` is the shipped default in `.ravenclaude/comfort-posture.yaml`.**
Every existing `ravenclaude-core` install is byte-identical in behavior before and after this ships,
until a consumer explicitly opts in (flips `enabled: true` and picks a `mode`). This is not aspirational
— Phase 2 and Phase 6 acceptance tests below require a positive-control proof of the zero-cost
short-circuit against the **real, nested** schema (not the flat scalar A originally authored it against
— see red-team Finding 1 and its mitigation in Phase 2/6).

---

## 1. Reconciled dependency DAG

```
P0 (design lock: schemas incl. nested posture shape + dispatch-delivery decision)
  │
  ▼
P1 (golden eval set — 30–50 entries, B's ordering, gates everything below)
  │
  ▼
P2 (Tier-0 free pre-filter + Tier-1 Haiku classifier; hook in scripts/, nested-schema short-circuit)
  │
  ├───────────────┐
  ▼               ▼
P3 (rewrite      P4 (dispatch-plan
    generator)       generator, reads
    [parallel]       agent-routing-matrix.json)
  │               │
  └───────┬───────┘
          ▼
P5 (additionalContext formatting + audit artifact + approval-gate wording +
    semantic screen + dispatch-plan file-pointer delivery)
          │
  ┌───────┴────────┐
  ▼                ▼
P6 (hook wiring +  P7 (/optimize slash
    posture/         command — reliable
    dashboard         approval-gate
    integration +     fallback)
    shadow rollout)
  │                │
  └───────┬────────┘
          ▼
P8 (skill doc completeness)
          │
          ▼
P9 (gate authoring — audit-gates.sh registration, judge scoped separately)
          │
          ▼
P10 (cross-link touch-ups)
```

**Critical path:** P0 → P1 → P2 → {P3|P4} → P5 → {P6|P7} → P8 → P9 → P10 — **9 phase-equivalents**
(down from A's un-reconciled 8-serial-plus-bundled-generators and up from B's 6 because P0/P8/P9/P10
are real added scope B folded inline or omitted — see gap-delta.md §2 and §3).

**Parallelizes, per tiebreak Conflict 5 (ruled B):** P3 (rewrite generator) and P4 (dispatch-plan
generator) are mutually independent once P2 ships — gap-delta.md's own adjudication found A's bundling
of these into one serial phase "confirmed avoidable, not legitimate added scope." Dispatch them
together. P6 (hook wiring) and P7 (`/optimize` command) are likewise independent once P5 ships (both
only consume P0–P5 artifacts). P9 (gate authoring) has no acceptance-test dependency on P8 (doc
completeness) — only on P0–P7 shipping — so it *could* run parallel to P8; kept serial here only for
review-load simplicity, noted as a legitimate compression opportunity if wall-time matters more than
review bandwidth.

**What blocks what:** P1 (golden set) blocks all generation-path work — no phase after it may claim
"measured" without it (B's eval-first bias, adopted by tiebreak Conflict 3). P2 blocks P3/P4 (nothing
generates without first passing the gate). P5 blocks P6/P7 (rollout/command need real output shapes to
format). P8's *completeness* acceptance test needs the whole mechanism (P0–P7) to exist, so it sits
after the P6/P7 join.

---

## 2. Risk matrix (critic-brief.md + red-team.md, deduplicated)

| # | risk | probability | impact | status in this plan |
|---|---|---|---|---|
| R1 | **Redundant-value premise** (critic-brief C1/premise-attack): a real share of the wild-assumption gate's value already exists as a standing AGENTS.md instruction ("ask ONE question on an under-specified request") + `ask-on-ambiguity.sh`. Neither panel checked "standing instruction" coverage, only "competing mechanism" coverage. | High — structurally evident from both plans' own text | High — undercuts the ROI case for a `standard`-depth build | **Named, not eliminated.** §7 below states the real counterfactual explicitly and re-derives the surviving value (coverage/consistency + cheap-before-expensive triage) rather than the "nothing exists today" framing both plans implicitly used. Carried forward as an open ROI caveat for the owner at rollout (P6). |
| R2 | **Approval-gate reliability** — the hook path is directive-not-enforced; `design_checkins` (the only cited precedent) is itself unenforced, and no acceptance test in either original plan actually drives the pause. Compounded by the 2–3s fail-open timeout silently dropping the whole directive exactly when the model would have complied. | Medium-High | High — this is scope.md's stated success signal | **Mitigated by design, residue named.** Tiebreak Conflict 2 (A) puts the *reliable* pause on `/optimize` (P7), where `AskUserQuestion` is genuinely synchronous-callable. The hook path (P2/P5/P6) remains best-effort by construction (claim 1 — no hook can block a turn) and P5's acceptance tests must include the fail-open-during-a-flagged-assumption compound case, not just cost fail-open alone. |
| R3 | **Free-text-field injection surface** (critic-brief C2, made concrete by red-team Finding 3): `rationale`/`ambiguity_reason`/`tailored_brief`/`wild_assumption.description` are model-*generated*, not raw-prompt-verbatim, so they clear the stated no-egress substring check while potentially carrying a paraphrased directive payload ("skip confirmation," "proceed without asking") into a channel both plans upgrade from advisory to operative/directive. | Medium (requires adversarial pasted content reaching the classifier/generator input — the domain prior's own named in-scope threat) | High — a successful case lands as an instruction the assistant is told to treat as authoritative | **Mitigated.** P5 adds a semantic/format screen on every generated free-text field before injection (red-team Finding 3's recommended resolution — added, not waived; see P5). |
| R4 | **No durable regression detection for "confidently wrong but well-formed" routing output** (critic-brief C3): A alone has a CI gate but only structural checks; B alone has an LLM-judge but no `audit-gates.sh` registration. Neither plan alone closes this — this repo's own "silent green defects" pattern. | High (structural gap in both plans individually) | Medium-High | **Mitigated by synthesis, scoped to avoid R-new below.** Tiebreak Conflict 3 merges B's judge design into A's durable gate mechanism — but see R-new (Finding 2) for the concrete failure mode that naive wiring reproduces, and its resolution in P9. |
| R-new-1 | **[Red-team Finding 1, HIGH] Posture-schema / hook-short-circuit mismatch.** Tiebreak Conflict 4 adopted B's nested schema (`prompt_optimizer: {enabled: false, mode: ...}`), but A's short-circuit was authored as a bare `grep` for a flat scalar (`prompt_optimizer: off`). A bare grep cannot correctly scope into the nested block, and `comfort-posture.yaml` already has other top-level `enabled: false` blocks (e.g. `dispatch_config`) that would false-match. | High if unmitigated (this is the modal case — every consumer who never touched the key) | High — directly reverses the "zero cost for non-adopters" claim | **Mitigated.** P2/P6 mandate a YAML-block-scoped check (`yq '.prompt_optimizer.enabled // false'`, with a documented `awk`/`grep` fallback for a `yq`-absent environment) and a regression fixture containing an *adjacent* unrelated `enabled: false` block (`dispatch_config`'s own) to prove the scoping is real, not lucky. |
| R-new-2 | **[Red-team Finding 2, HIGH] LLM-judge in `audit-gates.sh` reproduces the documented 600s-foreground-ceiling trap and taxes every future PR to the whole repo.** B's judge design is ~60–100 live model calls per run (30–50 entries × 2 output kinds); `audit-gates.sh` is whole-tree, run-on-every-PR. MEMORY.md already documents this exact shape failing (`inventory-nuance-judge.py` spawning a nested `claude` per nuance hitting the 600s clamp). | High — concrete, reproducible, not speculative | High — taxes every future marketplace PR, unrelated to this feature | **Resolved via explicit decision (P9), not accepted verbatim.** The full 30–50-entry judge pass is scoped to a **separate, non-required, scheduled gate** (weekly soak / on-demand invocation), matching B's own original "promotion gate" framing. `audit-gates.sh` itself carries only a **capped ≤5-fixture structural regression subset** (schema validity, fail-open teeth, no-egress) for per-PR coverage. |
| R-new-3 | **[Red-team Finding 4, HIGH] Tier-0 anchor-presence-only rule silently skips genuinely multi-domain prompts that name files** (e.g. "fix `payment.py`, also check `auth.py` and `db.py`, keep it fast" — 3 anchors, short, multi-domain — skips at zero cost under A's literal rule). Deterministic, not probabilistic — traceable directly from A's own stated Tier-0 text. | High (describable, common prompt shape) | High — defeats the plan's stated purpose for exactly the class scope.md's own worked example represents | **Mitigated.** P2's Tier-0 rule is bounded on **anchor COUNT** (not presence-of-any) **plus** B's multi-domain-keyword-cluster signal — a prompt clears Tier-0 only with exactly one anchor and no keyword-cluster hit. P1's golden set adds a **named "multi-anchor-multi-domain" category** (none of A's or B's original category lists (a)–(d) named this case) with a gated false-negative-rate bar before promotion out of `shadow`. |
| R-new-4 | **[Red-team Finding 5, MEDIUM-HIGH] Synthesis silently drops B's file-pointer mitigation for large dispatch-plan payloads** under the "minor conflicts default to A" rule, reintroducing a context-bloat problem this repo already paid to fix once (the FORGE-artifact-contract fix, v0.192.0, for a structurally similar payload-relay problem). | Medium (real for any N≥3-agent dispatch plan) | Medium-High — token/context-cost regression against a named prior fix | **Resolved via explicit adoption, not silent default.** P5 explicitly adopts B's file-pointer delivery **specifically for the `dispatch_plan` output_shape** (full plan written to the audit-artifact path, `additionalContext` carries only a pointer + one-line-per-domain summary); the `rewrite` output_shape stays inline (single small payload, no precedent conflict). Size ceiling: inline delivery is disallowed above 3 recommended agents in one plan — beyond that, file-pointer is mandatory regardless of any future edit to this phase. |
| R5 | Real (non-zero) tax on the "reaches Tier-1, resolves to skip" bucket — in tension with scope.md's "zero added latency/cost on trivial single-step asks" (true only for the Tier-0-caught subset). | Medium | Medium — expectations gap, not a defect | **Accepted, named.** P0's design note and P8's documentation state this bound explicitly rather than implying the whole "trivial" set is free. |
| R6 | Shallow/correlated engagement with `agent-routing-matrix.json`'s raw schema — both panels lean on the file's own prose description; A's "5 task classes" is uncorroborated in either plan's text. | Medium | Low-Medium | **Accepted, minor.** P4's acceptance tests require the *live* file to be read and its actual `task_classes` count asserted (not quoted from memory), closing this incidentally. |
| R7 | ~5–50x divergence in the dispatch-plan cost estimate between A (~$0.001–0.009) and B ($0.01–0.05). | Low (not load-bearing for architecture) | Low — but affects P6's shadow-soak budget projection | **Resolved by measurement.** P2/P4 acceptance tests record real latency/cost figures from the golden-set run; P0's design note is corrected against measured numbers rather than either plan's estimate, before P6's soak is budgeted. |

---

## 3. Alternatives considered per major fork (≥2 each, carried from the plans)

### Fork 1 — Hook file location (tiebreak Conflict 1 → **A**)
- **(A, chosen)** `scripts/prompt-optimizer-gate.sh`, registered with a `bash `-prefixed command in
  `hooks.json`/`settings.json`. *Why:* this repo's own `CLAUDE.md`/documented precedent already forces
  the same constraint on a real shipped file (`scripts/ask-on-ambiguity.sh`) — the tribunal's substrate
  guard denies `chmod +x` on a *new* file inside `hooks/`, and CI's "verify hooks executable" step
  hard-fails a non-executable file that *is* inside `hooks/`.
- **(B, rejected)** literal `hooks/prompt-optimizer-gate.sh`. *Why rejected:* would be denied on the
  first attempt to make it executable — not a style preference, a mechanical dead end confirmed by
  direct repo precedent (gap-delta.md §1.1 flagged this as fact-checkable, not preferential; the
  tiebreak resolved it as fact, favoring A).

### Fork 2 — Approval-gate escape hatch (tiebreak Conflict 2 → **A**, residue named)
- **(A, chosen as the reliable path)** `/optimize` slash command (P7) runs the identical
  classify→generate pipeline as the assistant's own in-turn action, where `AskUserQuestion` is
  genuinely synchronously callable.
- **(B, kept as the honest floor for the hook path)** instructional directive in `additionalContext`
  telling the assistant to self-issue `AskUserQuestion`. *Why not sufficient alone:* claim 1
  (`UserPromptSubmit` can only annotate, never block) means this can never be more than best-effort;
  scope.md's stated success signal requires "a real approval pause," which only A's command path can
  actually guarantee. B's mechanism is retained as what the hook path degrades to, not discarded.

### Fork 3 — Eval gating position and mechanism (tiebreak Conflict 3 → **synthesis**)
- **(A's structural check, alone insufficient)** ≥10-fixture discrimination test folded inside Phase 2
  — fast, but no independent gating phase and no LLM-judge for output *quality* vs. mere well-formedness.
- **(B's judge-first ordering, alone insufficient)** 30–50-entry golden set gating all downstream
  generation work, plus an LLM-judge pass — but never wired into a durable, re-run CI gate.
- **(Synthesis, chosen)** B's phase-ordering (golden set built and reviewed *before* any generator
  code) **and** B's LLM-judge design **and** A's durable `audit-gates.sh` registration — but scoped per
  red-team Finding 2 (R-new-2 above): the full judge pass is a separate scheduled gate; `audit-gates.sh`
  itself carries a capped ≤5-fixture structural subset. Neither original plan alone closed
  critic-brief C3's "silent green defect" risk; this is the one fork where picking a side was wrong.

### Fork 4 — `comfort-posture.yaml` schema shape (tiebreak Conflict 4 → **B**)
- **(A, rejected)** flat scalar `prompt_optimizer: off | shadow | live`.
- **(B, chosen)** nested `{enabled: false, mode: "shadow"|"advisory"|"binding-context"}`. *Why:* every
  existing multi-field posture knob in this repo (`dispatch_config`, `cheap_lane: {mode, agent}`,
  `context_handoff: {mode, spawn, ...}`) uses a nested object; the flat-scalar pattern is reserved for
  genuinely single-value knobs. `prompt_optimizer` plausibly needs at least a mode and a
  threshold/tier setting, matching the nested shape. **Consequence carried forward:** this choice is
  exactly what breaks A's originally-authored bare-grep short-circuit — see R-new-1 and its mitigation
  in Phase 2/6; the schema choice and the short-circuit mechanism must be co-designed, not
  independently inherited from two different plans.

### Fork 5 — Generator-path serialization (tiebreak Conflict 5 → **B**)
- **(A, rejected)** both `emit_optimized_prompt` and `emit_dispatch_plan` schemas/calls bundled into one
  serial phase, with formatting waiting on both.
- **(B, chosen)** independent parallel tracks (P3 | P4), converging only at the shared
  formatting/approval-gate step (P5). *Why:* gap-delta.md's own adjudication confirmed this as "avoidable,
  not legitimate added scope" — nothing in either generator's logic depends on the other; they consume
  the same upstream classifier output and produce disjoint downstream artifacts.

### Fork 6 — Roster-hallucination guard for dispatch-plan agent names (not in tiebreaks' top-5; explicit addition, not silent default)
- **(A's check, alone incomplete)** emitted `agents[]` entries must *cite* a matching
  `agent-routing-matrix.json` `task_class`'s recommendation — citation, not existence, and only covers
  prompts whose domain cleanly maps to a matrix cell.
- **(B's check, chosen as an addition, not a replacement)** every `recommended_agents` entry must
  resolve to a real, currently-enabled agent name, validated against the live roster before injection;
  on validation failure, drop the entry and lower confidence rather than inject a name that doesn't
  exist. *Why added explicitly rather than left to the "minor conflicts default to A" rule:* this is a
  near-zero-cost, purely additive safety check (a lookup, not a design fork) that closes a real
  hallucination path A's matrix-citation check does not cover unconditionally — per this gate's
  no-dangling-conflict mandate, it is called out here rather than silently dropped the way red-team
  Finding 5 warned against for the file-pointer fork.

### Fork 7 — Tier-0 free-pre-filter scope (folded into R-new-3's mitigation, not independently ranked by tiebreaks)
- **(A's original, insufficient alone)** skip-only on word-count + anchor *presence*; all domain-shape
  judgment deferred to paid Tier-1.
- **(B's original, partial answer)** additionally checks for multi-domain-keyword-cluster presence at
  zero cost.
- **(Synthesis, chosen — per R-new-3)** Tier-0 skip requires **both** a low anchor count (exactly one)
  **and** no multi-domain-keyword-cluster hit — neither original plan's literal rule alone avoided the
  false-negative red-team Finding 4 demonstrates; the combination closes it while keeping the
  free tier's decision genuinely free (no network call).

---

## 4. Phased plan — tiebreak verdicts + red-team mitigations folded into each phase

### Phase 0 — Design lock (schemas + file layout + posture schema, no code)

**Objective.** Freeze, in one committed design note under `docs/plans/`, the classifier output schema,
the rewrite-generator schema, the dispatch-plan-generator schema, the four `additionalContext` template
variants, the on-disk audit-artifact path convention
(`.ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json`, mirroring `adaptive-run-classifier`'s
precedent), **and the posture-knob schema per tiebreak Conflict 4**:
`prompt_optimizer: {enabled: false, mode: "shadow"|"advisory"|"binding-context"}` in
`.ravenclaude/comfort-posture.yaml`. **Explicitly documents the delivery-shape decision per red-team
Finding 5 (Fork 7 in §3):** `rewrite` output_shape is always inline; `dispatch_plan` output_shape is
inline only when it names ≤2 agents, and file-pointer (summary + `Read`-on-demand pointer to the audit
artifact) is **mandatory** above that.

**Pre-build gate.** None — first phase.

**Acceptance tests.**
1. All four `additionalContext` template variants enumerated, each reviewed against the
   "unmissable, derived-values-only" invariant, **extended per red-team Finding 3** to also state which
   free-text sub-fields (`rationale`, `ambiguity_reason`, `tailored_brief`, `wild_assumption.description`)
   will pass through P5's semantic screen (not just the no-egress substring check).
2. The dispatch-plan schema's field names diffed against `claude-orchestrate.sh`'s "decide" mode
   envelope (A's §2.6 reuse), divergence justified in writing.
3. The posture schema is diffed against `dispatch_config`'s and `cheap_lane`'s existing nested shapes
   to confirm structural consistency (tiebreak Conflict 4's stated rationale, verified not just asserted).
4. The dispatch-plan inline/file-pointer threshold (≤2 agents inline, >2 file-pointer) is written down
   as a testable number, not left as prose — this is what P5 acceptance tests will check against.

`depends_on_claims: [1, 2, 6]`
`reversibility: two-way-door` — a design note with no shipped code.

---

### Phase 1 — Golden eval set (B's ordering, adopted by tiebreak Conflict 3)

**Objective.** Build the ruler before the thing it measures. Ships
`plugins/ravenclaude-core/skills/prompt-optimizer/eval/golden-set.jsonl` — 30–50 hand-authored entries:
`{prompt, expected_gate_fire, expected_domain_count, expected_domains, expected_output_kind,
expected_wild_assumption, notes}`. Categories per B's original (a)–(d) **plus a fifth, named per
red-team Finding 4**: **(e) multi-anchor-multi-domain** — short prompts naming ≥2 file/code anchors
whose remediation spans ≥2 domains (the `payment.py`/`auth.py`/`db.py` case from red-team.md §4
verbatim, plus ≥2 more hand-authored variants). This category did not exist in either original plan's
category list and is the direct fixture proof for Phase 2's Tier-0 fix.

**Acceptance test.** Set exists, schema-valid, reviewer-confirmed defensible per-entry. Category (e)
has ≥3 entries, each engineered so A's original anchor-presence-only rule would have wrongly skipped it
(a documented negative control proving the fixture is load-bearing, not decorative).

**Pre-build gate.** None beyond G3 passing.

`depends_on_claims: [6]`
`reversibility: two-way-door` — a fixture file.

---

### Phase 2 — Tier-0 pre-filter + Tier-1 Haiku classifier (hook location per tiebreak Conflict 1; scope per red-team Finding 4; short-circuit per red-team Finding 1)

**Objective.** `scripts/prompt-optimizer-gate.sh` (per tiebreak Conflict 1 → **A's location**,
`bash `-prefixed registration — **not** `hooks/`, per Fork 1 in §3), implementing:

- **Tier 0 (free, no network call) — bounded per red-team Finding 4 / Fork 7's synthesis:** skip only
  when anchor **count == 1** *and* no multi-domain-keyword-cluster hit (B's signal, folded into A's
  originally presence-only rule). A prompt with 2+ anchors, or a domain-keyword-cluster hit regardless
  of anchor count, falls through to Tier 1 — closing the `payment.py`/`auth.py`/`db.py` false-negative
  deterministically, not probabilistically.
- **Tier 1 (paid, one Haiku forced-tool call)** — identical shape to `agent-dispatch-evaluator`'s proven
  pattern: `claude -p --bare --output-format json --model claude-haiku-4-5-<pinned-date> --tools ""`,
  same fail-open contract (timeout, missing-`claude`, missing-`jq`, unparseable-JSON → pass through with
  nothing emitted). Rubric discriminates on anchor-density-relative-to-scope, distinct-domain count, and
  assumption count — not raw length (A §2.2 item 2, carried verbatim; both plans agreed on this rubric
  shape).
- **Config gate — nested schema per tiebreak Conflict 4, short-circuit fixed per red-team Finding 1:**
  `prompt_optimizer.enabled == false` (absent key counts as `false`) → the hook exits before any
  subprocess call. **The short-circuit MUST be a YAML-block-scoped read** (`yq
  '.prompt_optimizer.enabled // false' comfort-posture.yaml`, with a documented `awk`/`grep` fallback
  for a `yq`-absent environment that correctly scopes to the `prompt_optimizer:` block rather than a
  bare unanchored `grep "enabled: false"`) — a bare grep cannot distinguish `prompt_optimizer`'s
  `enabled: false` from `dispatch_config`'s adjacent one, and red-team Finding 1 traced this exact
  failure mode to a silent loss of the "zero cost for non-adopters" guarantee for the entire installed
  base (the modal case: nobody has touched the key).

**Acceptance tests.**
1. Run the hook against Phase 1's full golden set (including category (e)). Target: **zero
   false-fires/false-skips on category (b)** (complex-but-clear) **and zero false-skips on category (e)**
   (multi-anchor-multi-domain) — both are explicit promotion gates, not advisory.
2. **Short-circuit regression fixture, per red-team Finding 1 directly:** a `comfort-posture.yaml`
   fixture containing `dispatch_config`'s own `enabled: false` block **adjacent to** an absent/false
   `prompt_optimizer` block — assert zero subprocess calls (positive-control instrumentation, same
   pattern A's Phase 1 acceptance test 1 used) and assert the result is unaffected by which block
   appears first in the file (ordering-independence, proving the scoping is real YAML parsing, not a
   grep that got lucky on file layout).
3. No-egress invariant on the classifier's raw verdict (Gate 19 family) — only derived fields ever leave
   the subprocess boundary; the classifier's own `ambiguity_reason` free-text field is flagged here as
   requiring P5's semantic screen before any downstream injection (cross-reference, not a duplicate
   check).
4. Fail-open teeth: kill `claude` mid-test, assert exit 0, no `additionalContext`, no crash.
5. Low-confidence non-mutation: engineered `confidence: "low"` fixture resolves to `action: "skip"`
   regardless of other fields.
6. Latency/cost measured across the full golden set and recorded — corrects P0's design note against
   real numbers rather than either original plan's estimate (resolves R7).

`depends_on_claims: [1, 2, 3, 5]` (claim 5 — the documented SessionStart-matcher incident — is the
direct precedent for why the short-circuit's correctness, not just its existence, is a promotion gate)
`reversibility: two-way-door` — additive, not yet wired into `hooks.json` (Phase 6).

---

### Phase 3 — Rewrite generator (parallel with Phase 4, per tiebreak Conflict 5)

**Objective.** `emit_optimized_prompt` forced-tool schema authored in `skills/prompt-optimizer/SKILL.md`,
invoked when `domain_count <= 1` (A §2.3's deterministic rule, uncontested by either plan). Fast tier via
`substrate-tier-map.json`'s `resolve_tier()`. Output: rewritten prompt, persona, explicit constraints,
surfaced missing context, `wild_assumption: {present, description, confidence}`.

**Pre-build gate.** Phase 2 ships and passes its promotion-gated acceptance tests (1–2 above).

**Acceptance tests.**
1. `domain_count <= 1` fixture produces a well-formed result at the resolved fast tier.
2. Rewrite preserves every constraint present in the original prompt (mechanical diff-style check
   against Phase 1's category (b) subset, B's acceptance-test design).
3. A held-out LLM-judge pass (a model distinct from the generator, per critic-brief's
   self-preferential-bias concern) scores each rewrite against the golden entry's notes — **this is
   the scheduled/on-demand judge pass per Phase 9's scoping (red-team Finding 2's resolution), not a
   per-PR `audit-gates.sh` run.**
4. `wild_assumption.description`, when present, is flagged for P5's semantic screen (cross-reference).
5. Fail-open teeth, mirroring Phase 2.

`depends_on_claims: [1]`
`reversibility: two-way-door`.

---

### Phase 4 — Dispatch-plan generator (parallel with Phase 3, per tiebreak Conflict 5)

**Objective.** `emit_dispatch_plan` forced-tool schema, invoked when `domain_count >= 2`. Balanced tier.
Reads `agent-routing-matrix.json` as read-only, consulted context (A §2.6's reuse, uncontested — the
single largest SSOT-reuse decision in either plan). Output: `{domains[], per_domain: [{domain,
recommended_agents: [{agent, rationale, matrix_basis}], tailored_brief}], wild_assumption}`.

**Roster-hallucination guard (§3 Fork 6 — explicit addition, not a silent A-default):** every
`recommended_agents` entry MUST resolve to a real, currently-enabled agent name, validated against the
live roster before injection. On validation failure, drop the entry and lower confidence rather than
inject a name that doesn't exist. This is B's check, adopted as an **addition** to A's matrix-citation
check (both run — citation quality AND existence are both asserted).

**Never-dispatches invariant.** The generator's tool definition is asserted, by static inspection, to
grant no `Agent`/`Bash`/`Write`/`Edit` tool access — pure JSON-emitting, matching scope.md's out-of-scope
line (this build never invokes the agents it names).

**Pre-build gate.** Phase 2 ships and passes acceptance.

**Acceptance tests.**
1. `domain_count >= 2` fixture (including Phase 1's category (e) entries) produces a well-formed
   dispatch plan whose recommended agents, where the fixture's domains overlap a real matrix
   `task_class`, cite that class's recommendation.
2. Every `recommended_agents` entry is checked against the **live, currently-enabled** agent roster
   (not the repo-wide 636-file count — claim 4) — the roster-hallucination guard above, run as a hard
   acceptance gate, not a soft check.
3. The live `agent-routing-matrix.json`'s actual `task_classes` count is read and asserted in-test
   (resolves R6 — no plan's "5 task classes" claim is trusted uncorroborated).
4. `tailored_brief` and `wild_assumption.description` flagged for P5's semantic screen.
5. Never-dispatches invariant verified by static inspection of the skill file + invocation code.
6. Fail-open teeth.

`depends_on_claims: [1, 3, 4, 6]`
`reversibility: two-way-door`.

---

### Phase 5 — Formatting, audit artifact, approval-gate wording, semantic screen, delivery shape

**Objective.** Implement the four `additionalContext` template variants frozen in Phase 0, the
wild-assumption `AskUserQuestion`-instruction wording, and the audit-artifact write. Three red-team
mitigations land here, all as explicit adoptions:

1. **Semantic screen (red-team Finding 3 — ADDED, not waived).** Before any generated free-text field
   (`rationale`, `ambiguity_reason`, `tailored_brief`, `wild_assumption.description`) is injected into
   `additionalContext`, run a cheap keyword/regex screen for imperative/directive-shaped language
   ("skip confirmation," "proceed without," "do not ask," "full access," and similar phrasings),
   mirroring the tribunal substrate's own `_scrub.sh` pattern (already cited by A's Phase 4). A field
   that trips the screen is either rewritten to strip the directive framing or the whole
   `additionalContext` degrades to a neutral "the generator produced content flagged for review" state
   rather than injecting the raw generated text. This closes the paraphrase-based injection path
   red-team Finding 3 demonstrated is schema-deterministic (clears the substring no-egress check while
   still carrying directive semantics).
2. **Dispatch-plan delivery shape (red-team Finding 5 — explicit adoption per §3 Fork 7, not a silent
   A-default).** `rewrite` output_shape: always inline (small, single payload — no conflict). `dispatch_plan`
   output_shape: inline **only** when ≤2 agents recommended; **file-pointer mandatory above that**
   (full plan written to the audit-artifact path, `additionalContext` carries a short pointer + one
   line per domain, instructing the assistant to `Read` the full file before acting). This is B's
   FORGE-artifact-contract-precedented mitigation, explicitly carried forward rather than dropped by
   the "minor conflicts default to A" rule.
3. **Approval-gate wording (tiebreak Conflict 2 — A, residue named).** When `wild_assumption.present ==
   true`, the injected block instructs the assistant to call `AskUserQuestion` as its first tool call
   this turn, presenting the flagged assumption. **This is best-effort on the hook path** (claim 1 — no
   hook can block a turn) — the reliable version of this pause lives on `/optimize` (Phase 7). Composition
   with `decision-review`: even under `decision_review: binding`, a wild-assumption question is a
   genuine-preference call the tribunal's own guardrails already defer, so the pause survives regardless
   of a consumer's decision-review posture (A §2.4 item 2, live-verified in acceptance test 3 below).

**Pre-build gate.** Phase 3 and Phase 4 both ship.

**Acceptance tests.**
1. Each of the four `(action, output_shape, wild_assumption)` combinations produces the frozen template
   variant, byte-diffed against Phase 0's design note.
2. **Semantic-screen teeth (red-team Finding 3):** a fixture whose generated `tailored_brief` contains
   injected directive-shaped language ("skip confirmation... proceed without waiting") is asserted to
   be caught by the screen and neutralized before injection — a must-fail-then-pass proof the screen is
   load-bearing, not a no-op.
3. Wild-assumption composition: a wild-assumption-shaped yes/no question is routed through
   `thing-decide.py decide` with `decision_review: binding` set, and the verdict is asserted `defer`
   (live proof the approval pause survives a binding posture, A §2.4 item 2's claim made concrete).
4. **Delivery-shape teeth (red-team Finding 5):** a fixture dispatch plan naming 4 agents is asserted to
   produce file-pointer delivery (small `additionalContext`, full plan on disk); a fixture naming 1 agent
   is asserted to produce inline delivery — both branches of Phase 0's threshold exercised.
5. No-egress on the on-disk audit artifact, same bar as Phase 2's in-memory check.
6. Must-fail teeth: strip the scrub step, confirm a planted secret-shaped string in a fixture prompt
   *does* leak into the artifact — proving the scrub is load-bearing.

`depends_on_claims: [1, 4]`
`reversibility: two-way-door`.

---

### Phase 6 — Hook wiring + posture/dashboard integration + shadow rollout

**Objective.** Register `scripts/prompt-optimizer-gate.sh` (tiebreak Conflict 1's location) as a
`UserPromptSubmit` hook in both `hooks/hooks.json` and the dev-mirror `.claude/settings.json`. Gated by
the nested `prompt_optimizer: {enabled: false, mode: ...}` knob (tiebreak Conflict 4), with the
YAML-scoped short-circuit fix from Phase 2 (red-team Finding 1) carried through unchanged — this phase
wires, it does not re-derive, the short-circuit. Adds a dashboard control (Pipeline tab, mirroring
`cheap_lane`/`context_handoff`'s existing round-trip precedent) with the `enabled`/`mode` state slot
wired through `state`/`emitYaml`/`applyGuardrailConfig`/`/__save` (B's Phase 6, folded in — the v0.61.0
data-loss class this repo has hit repeatedly on every new posture key must not repeat here). Rollout
path: default `off` → `shadow` (log-only, no injection, for a defined soak period) → owner decision to
flip a shipped-template default, never an existing consumer's posture.

**Pre-build gate.** Phases 2–5 all pass their acceptance tests independently — this phase wires
already-proven pieces together.

**Acceptance tests.**
1. `prompt_optimizer` absent or `enabled: false` → zero subprocess calls, verified against the
   multi-block regression fixture from Phase 2 acceptance test 2 (re-asserted here as the wired,
   end-to-end version — not just the isolated function).
2. `mode: "shadow"` → the audit artifact is written but `additionalContext` is empty in the emitted hook
   output.
3. `mode: "advisory"`/`"binding-context"` end-to-end: pre-filter → classify → generate → format → emit,
   hook stdout asserted well-formed `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit",
   "additionalContext":"..."}}`.
4. Multiple-hooks-coexist regression: with `ask-on-ambiguity.sh` and `stream-prompt-attribute.sh` also
   registered on `UserPromptSubmit`, all three fire on one prompt and none's output is corrupted or
   dropped by the others.
5. Dashboard round-trip test (Gate 35's pattern): emit-when-non-default, hydrate-back, a must-fail
   mutant that strips the emit line.
6. A real shadow-mode soak run (minimum N real sessions, N set by the owner at rollout time) with the
   false-fire rate and judge-scores from Phases 2–4 holding in production-shaped traffic — the golden
   set proves it *can* work; the soak is the only way to learn whether it works at the tail the golden
   set didn't cover.

`depends_on_claims: [1, 2, 5]`
`reversibility: two-way-door`, rollback: `enabled: false` (one line, already the default; no version
bump needed) or remove the two `hooks.json` entries for full retraction.

---

### Phase 7 — `/optimize` slash command (the reliable approval-gate fallback, tiebreak Conflict 2)

**Objective.** `commands/optimize.md` invokes the identical skill (Phases 0–4 artifacts, no new logic)
as the assistant's own in-turn action — so it can call `AskUserQuestion` directly and synchronously on
a wild assumption, closing the reliability gap Phase 5/6's hook path cannot close by construction
(claim 1). Usable regardless of the `prompt_optimizer` posture knob.

**Pre-build gate.** Phases 0–4 ship.

**Acceptance tests.**
1. `/optimize "make this faster and more secure"` produces a dispatch-plan result and, in a live
   session engineered to trigger `wild_assumption: true`, the assistant's next action is a real
   `AskUserQuestion` call — the one acceptance test in this plan requiring a live interactive assertion,
   because it specifically proves the reliability gap the tiebreak ruled on is actually closed.
2. `/optimize` with `prompt_optimizer.enabled: false` in the active posture still runs (independent of
   the hook's opt-in knob).
3. The command's output uses the identical schema Phase 5 formats for the hook path (diff-based
   regression check) — a user does not learn two output vocabularies depending on entry point.

`depends_on_claims: [1, 4]`
`reversibility: two-way-door` — a single command file.

---

### Phase 8 — Skill documentation completeness

**Objective.** Bring `skills/prompt-optimizer/SKILL.md` to the bar `adaptive-run-classifier` and
`agent-dispatch-evaluator` set: ≥3 worked examples (skip / rewrite / dispatch-plan), the composition
section (§2.6-equivalent) written as prose in the skill file, the Structured Output Protocol block, a
self-score against `agent-quality-rubric`, and an explicit written statement of R1/R5 (the redundant-
value premise and the non-zero Tier-1-reaches-but-skips cost) so a future reader inherits the honest
ROI picture, not an inflated one.

**Pre-build gate.** Phases 0–7 all ship.

**Acceptance tests.**
1. `agent-quality-rubric`'s 6-dimension checklist applied and scored in the file itself.
2. Every cross-reference (`agent-routing-matrix.json`, `substrate-tier-map.json`, `claude-orchestrate.sh`,
   `decision-review`, `agent-dispatch-evaluator`) present as a real Markdown link (never inside a
   backtick span, per this repo's known `check-md-links.py` blind spot), re-verified this pass.

`depends_on_claims: []`
`reversibility: two-way-door`.

---

### Phase 9 — Gate authoring, with judge scoping decided explicitly (red-team Finding 2's resolution)

**Objective.** Register the mechanism's regression coverage in `scripts/audit-gates.sh` — but **the
30–50-entry LLM-judge pass is explicitly NOT part of `audit-gates.sh`**, per red-team Finding 2's
recommended resolution:

- **`audit-gates.sh` (per-PR, required, whole-tree):** a capped **≤5-fixture structural subset** —
  schema validity of all three JSON shapes, the fail-open teeth (Phase 2/3/4), the no-egress checks
  (Phase 2/5), the semantic-screen teeth (Phase 5), and the short-circuit regression fixture (Phase
  2/6). Zero live-judge-model calls in this path. This is the durable, re-run-on-every-future-edit floor
  A's original design wanted, sized to avoid the 600s-clamp/whole-repo-tax trap.
- **A separate, non-required, scheduled gate** (weekly soak or on-demand invocation — new script,
  e.g. `scripts/prompt-optimizer-judge-soak.sh`, not folded into `audit-gates.sh`'s dispatcher): runs
  the full golden set through the LLM-judge pass B originally scoped as a one-time "promotion gate."
  This is where quality drift ("confidently wrong but well-formed") gets caught, at a cost/latency
  profile that does not touch every future unrelated PR.

**Pre-build gate.** Phases 1–8 all ship.

**Acceptance tests.**
1. Gate number resolved by grepping the current max header in `scripts/audit-gates.sh` at build time,
   never hardcoded (the `forge-receipt.py` incident precedent).
2. The ≤5-fixture subset's must-fail teeth (neuter one fail-open guarantee) proven to redden the gate,
   then reverted.
3. `grep -c` for the new gate's number across `--check` dispatcher / main sequence / `Supported:` string
   returns 3 (once each) — the Gate 184/263 three-surface-registration lesson, run and recorded, not
   merely asserted.
4. **The scheduled judge-soak script is proven to run standalone, outside `audit-gates.sh`'s own
   invocation path** — a negative-space check: `audit-gates.sh`'s own runtime is measured before/after
   this phase and asserted to have added no more than the ≤5-fixture subset's cost (closing red-team
   Finding 2 concretely, not just in prose).

`depends_on_claims: [5]`
`reversibility: two-way-door`.

---

### Phase 10 — Cross-link documentation touch-ups

**Objective.** One-paragraph pointers in `spawn-team/SKILL.md`, `agent-dispatch-evaluator/SKILL.md`'s
References section, and `claude-orchestrate/SKILL.md`, matching `agent-routing-matrix.md`'s own
prose-only, zero-code-change precedent when it was added as a cited sibling to these same three files.

**Pre-build gate.** Phase 8 ships.

**Acceptance tests.**
1. Each added pointer is a single paragraph; diffed to confirm only net-new lines, no edits to existing
   prose.
2. `route-task.py --self-test` re-run and asserted unchanged (`N/N`, same N) — negative-space proof this
   build touched zero of that script's logic.

`depends_on_claims: []`
`reversibility: two-way-door`.

---

## 5. Reversibility summary

Every phase is `two-way-door`. The mechanism only ever (a) reads existing, already-committed data
(`agent-routing-matrix.json`, `substrate-tier-map.json`), (b) writes new, gitignored artifacts under
`.ravenclaude/runs/`, and (c) injects advisory `additionalContext` the assistant may or may not act on.
No phase deletes, mutates, or gates access to anything that existed before this build. The single
rollback lever for the entire mechanism is Phase 6's posture knob (`prompt_optimizer.enabled: false` —
already the shipped default), or full retraction by removing the two `hooks.json` entries.

---

## 6. What this plan deliberately does NOT do

- Does not edit `agent-dispatch-evaluator.sh`, `dispatch-config.json`, `evaluate-dispatch.js`,
  `adaptive-run-classifier`'s schema/templates, `agent-routing-matrix.json`/`.schema.json`, or
  `route-task.py` — every one is cited, none modified.
- Does not attempt cross-host portability in this build (Copilot/Codex/Gemini) — `prompt_optimizer`
  defaults `enabled: false`, hook registration is Claude-Code-only.
- Does not build a new blocking primitive for the approval gate — composes with `AskUserQuestion` +
  `decision-review`'s `defer` carve-out instead.
- Does not retune or audit the ~150-agent roster's own descriptions.
- Does not fold the full LLM-judge pass into `audit-gates.sh` (red-team Finding 2's resolution, Phase 9)
  — this is a deliberate, explicit scope boundary, not an omission.

---

## 7. Honest ROI note (R1, ROI/premise caveat — not a phase, carried forward for the owner)

Per critic-brief.md's premise attack: the real counterfactual this build competes against is not "the
assistant blindly guesses" — it is a standing AGENTS.md instruction ("ask ONE question on an
under-specified request") plus `ask-on-ambiguity.sh`'s existing advisory sliver plus `spawn-team`'s
playbook already pointing at `agent-routing-matrix.json`. What genuinely survives as new value: (a)
coverage/consistency — a cheap gate fires on every prompt regardless of the main assistant's own
attention that turn, and (b) triage — offloading the "is this worth stopping for" judgment onto a cheap
model before the expensive one spends tokens. Both are real. Neither is "produces a routing decision
that wouldn't otherwise exist." This plan proceeds on that thinner, honestly-stated margin — Phase 8's
documentation is required to state it this way for any future reader, not the stronger, implicit
"nothing exists today" framing either original plan carried.

---

## 8. G8 DoD addendum — regen discipline + code-review (added by the orchestrator at G8; not covered by
either draft or by the synthesis pass above)

This build adds a new skill (`prompt-optimizer`) and slash command (`/optimize`) to `ravenclaude-core`,
which changes counted artifacts referenced in marketplace prose. Per this repo's own
`reference/regen-discipline.md` (the 2026-06-03 hotfix-chain lesson, PRs #244-#247), the phase that lands
this skill's manifest changes MUST include the following in its own acceptance criteria — folded in here
rather than left implicit, since a missed item here is a documented, real 3-PR hotfix pattern:

1. **Quote `description:` in the new `SKILL.md`/command frontmatter** if it contains `:` / `{` / `}` —
   `scripts/check-frontmatter.py`'s strict-YAML check parses unquoted scalars and will fail the build on
   an unquoted colon (the common trip: a backtick-wrapped example like `enabled: false` in the
   description text).
2. **Bump skill count strings** in `.claude-plugin/marketplace.json` (top `metadata.description` + the
   `ravenclaude-core` entry description) and `plugins/ravenclaude-core/.claude-plugin/plugin.json`'s
   description — Gate 12 (`marketplace-claims`) compares these against the real filesystem count.
3. **Regenerate `dashboard.html`** — `python3 scripts/generate-dashboards.py` (Gate 13 freshness).
4. **Regenerate the portal** — `python3 scripts/generate-index-dashboard.py` (folds dashboard + catalog
   natively; its own `--check` freshness gate runs inside the repo-wide gate suite).
5. **Regenerate the Copilot package** — `python3 scripts/generate-copilot-plugin.py` (its own freshness
   gate) — even though this feature is Claude-Code-only at v1, the agent/skill roster projection into
   `copilot/` still needs to stay in sync, or that gate fails independently of this feature's own scope.
6. **Update any hardcoded skill-count literal** in the repo-wide gate-suite script's own fixtures (search
   for a pattern like `s.replace('<N> skills', '<old-count> skills', 1)` in its must-fail fixture) — if
   left pointing at the pre-build count, that gate's bad-input test silently stops testing anything.
7. **Strip session-bound posture mutations** (`.ravenclaude/comfort-posture.yaml` changes a hook wrote
   during the build session, e.g. a live toggle used for manual testing) before the commit that lands
   this feature — only the substantive `prompt_optimizer:` default-off block belongs in the diff.
8. **Version bump on every user-visible change** — per this repo's own single-source-of-truth
   convention: bump `version` in `plugins/ravenclaude-core/.claude-plugin/plugin.json` only (never
   hand-edit the marketplace catalog entry), then run `python3 scripts/sync-plugin-versions.py` to derive
   the catalog version. Two hand-edited copies of the same version number is a documented merge-conflict
   generator in this repo's own history.
9. **`/code-review`** — per this repo's own G8 convention, any phase that lands as a PR with real code
   changes names `/code-review` in that phase's own DoD as the pre-merge completion step, alongside
   `prettier`/the repo-wide gate suite. This is a checklist line, not a replacement for the security
   review Finding-3's injection-screen mitigation (§ Phase 5 above) already requires.

Note this is a **planning-phase addendum, not evidence any of the above has been executed** — this
FORGE run produced a plan, not an implementation. The build phase that actually lands the skill is
responsible for running all nine items and cannot claim done without them.
