# Plugin-candidate audit — what else in `ravenclaude-core` belongs in a plugin

**Run:** `plugin-candidate-audit-20260902` · **Gate:** G6 (synthesis) · **Date:** 2026-09-02
**Status:** REPORT ONLY — nothing moved, nothing edited, no PR. Two independent panels audited all
58 skills in `plugins/ravenclaude-core/skills/`; this file reconciles them.

`[unverified — premise not disconfirmed: only the pbir-layout-engine finding (Phase 1) is grep-verified by both independent panels; the remaining flagged skills carry medium/low confidence and one genuine unresolved cross-panel disagreement — see "Open question for Matt" below]`

---

## The headline: almost nothing moves

**52 of 58 skills were reviewed and cleared as legitimately domain-neutral.** That is the finding,
not a footnote. Both panels went looking for violations of house rule #1 with different methods —
Panel A read frontmatter across all 58 plus 12 full bodies and ran reverse-reference sweeps; Panel B
ran a grep sweep for literal `plugins/<domain>/` path reads and then hunted its own false positives —
and both independently declined to manufacture a longer list. Panel B put it plainly: *"This is a
short plan because the evidence is short."*

Of the 6 that are flagged, **1 is a real, mechanical defect**; 2 are a defensible but arguable call
the repo currently rules the other way on; 2 are a genuine unresolved disagreement between the
panels; and 1 is flagged only so you can see it was considered and consciously left alone.

**Counting honestly:** 6 flagged / 52 cleared. If you accept both panels' recommendation on
`wireframe` (stay), then **53 of 58 skills end this audit where they started**, and the live
candidate set is four skills in three clusters.

---

## Reconciled findings

| # | Skill(s) | Target | Combined confidence | Strongest single piece of evidence | Status |
|---|---|---|---|---|---|
| 1 | `pbir-layout-engine` | `plugins/power-platform/` — **split**, checks 5–7 only | **HIGH** on the violation (both panels grep-verified it independently, from different entry points). **MEDIUM** on the fix shape — both landed on the same split; Panel B rates the *action* only low-medium because the coupling is already documented and fail-closed. | `check-7` parses `plugins/power-platform/knowledge/pbir-enhanced-reference.md` **at runtime**; the SKILL.md itself calls this "the one sanctioned cross-plugin read." Core reads a domain plugin — the exact inversion house rule #1 exists to prevent. | **CONFIRMED** |
| 2 | `brand-extraction` + `design-clone` (atomic pair) | `brand-identity-studio` / `web-design` — split-shaped | **MEDIUM**, and this one *rose* during reconciliation. Panel B originally cleared both as false positives on mechanism-reading, then re-ran Panel A's reverse-reference sweep itself and wrote: *"I was wrong to clear `brand-extraction` and `design-clone` as false positives on mechanism-reading alone."* Both panels now agree on direction. | The consumer set is vertical-concentrated, not fleet-wide: 6 referencing files under `plugins/generative-web-media/`, 3 under `plugins/brand-identity-studio/`, and **nothing** in the worktree / PR / dispatch / tribunal spine. Panel B re-verified this count independently. | **RECOMMENDED** (both panels agree post-reconciliation; still argued against by the repo's own CLAUDE.md — see Open question #2) |
| 3 | `declarative-visualization` + `svg-report-lint` | Panel A: **new** `plugins/data-visualization/` (method content only). Panel B: **stay in core**. | **LOW / unresolved.** Both panels rate their own position low-confidence and both explicitly say the tiebreaker should decide, not either of them. | Same fact, opposite readings: the two skills are referenced from **six** domain plugins (`tableau`, `power-platform`, `data-platform`, `web-design`, `frontend-engineering`, `report-regeneration`). Panel A: "no existing plugin is their natural home, therefore a new one." Panel B: "used by six unrelated plugins is the signature of correctly-placed shared infrastructure." | **OPEN DISAGREEMENT** |
| 4 | `wireframe` | `plugins/web-design/` (nominal) | **LOW — both panels recommend NO MOVE.** Panel A did the deeper work and Panel B conceded the gap: *"I did not catch this dependency and it's a real gap in my coverage."* | Its mechanism is *model → schema-validated → many surfaces* (ASCII / SVG / Mermaid / HTML Artifact) with a hard main-session constraint — substrate plumbing, not web craft. Flagged only because its in-repo justification at `CLAUDE.md:2001` cites `brand-extraction` as precedent, which finding #2 undermines. | **RECOMMENDED (no move)** — the action here is a doc edit: replace the precedent citation with a first-principles justification so it doesn't inherit #2's fate. |
| 5 | The other 52 | — | **HIGH** (both panels, independently) | Panel A's near-miss table and Panel B's false-positive sweep reach identical verdicts on the four hardest calls — `visual-feedback-loop`, `environment-discovery`, `design-link`, `pseudonymize`. A true negative that two different lenses agree on is worth more than either alone. | **CONFIRMED — no move** |

### Reconciled sub-verdicts (so nothing is silently dropped)

- **`data-platform` is a second, independent consumer of `pbir-layout-engine`.** Panel B found
  `plugins/data-platform/agents/dashboard-builder.md` citing the linter by name as "the free
  structural check" for any page-JSON dashboard, independent of Power BI. Panel A's claim 8 named
  only power-platform's consumers. **Verdict: Panel B's fact is adopted.** It doesn't contradict
  Panel A — it *strengthens* Panel A's own counter-evidence that a whole-move would relocate the
  defect rather than fix it. The split shape is now supported by two independent reasons.
- **A whole-move of `brand-extraction` would create a new inverted dependency.** Panel B's honest
  complication: `design-clone`, `repo-build-studio`, and `visual-feedback-loop` (all core) reference
  `brand-extraction` directly. **Verdict: adopted as a constraint on finding #2** — it forces the
  split shape (token-application half stays core; harvesting/inference half moves), exactly as in
  finding #1.
- **`pseudonymize` — Panel B was silent, Panel A examined and cleared it.** **Verdict: no move,
  Panel A's reasoning stands unopposed** (it's an egress guardrail on the agent's own prompt path,
  wired into `comfort-posture` / `claude-orchestrate.sh`; the privacy *craft* already correctly
  lives in `data-governance-privacy`). Recorded as a one-panel finding, not a two-panel one.
- **`wireframe` — both panels say stay, for different reasons.** Panel B cleared it as generic web
  tooling; Panel A cleared it on mechanism *and* traced the precedent chain. **Verdict: no move; the
  precedent-citation fix rides in whatever PR touches finding #2, if one ever does.**
- **Confidence on finding #1's *action* differs and is not being papered over.** Panel A: high on
  the violation, medium on shape. Panel B: the coupling is real but "minimized, documented,
  fail-closed" and already the marketplace's sanctioned pattern for "mostly-generic tool needs one
  small vendor fact," so it rates the move low-medium and says *"do NOT move the whole skill."*
  **Verdict: the finding is CONFIRMED; the remedy is a split or nothing.** Neither panel endorses a
  whole-skill relocation.

---

## Risk matrix — what breaks if you move the wrong thing

### ⚠️ Cross-cutting blocker, applies to every item on this page

**`scripts/audit-gates.sh` hardcodes `plugins/ravenclaude-core/skills/<name>/` paths for Gates 92,
100, 101, 103, and 145–149** (the last of which cross-calls `../svg-report-lint/lint.py`). Both
panels flagged this independently.

**None of these relocations is a plain `git mv`.** Each one is a gate-path edit *plus* re-proving the
gate's teeth bidirectionally — and a gate that merely *stops erroring* after a path change is the
exact silent-green defect class this repo already catalogs. Whatever subset you eventually pick, this
cost is fixed and applies first.

Good news, so the blocker is sized honestly: `.repo-layout.json` already allows `plugins/*/skills/**`
generically, so **no layout-allowlist edit is needed** for any of these moves.

| If you move… | What breaks | Severity |
|---|---|---|
| **`pbir-layout-engine` wholesale** (instead of splitting) | Core's `visual-feedback-loop` loses its structural referee, and `data-platform`'s `dashboard-builder` transitively needs `power-platform` installed to structurally check a Power-BI-unrelated dashboard. You'd trade one inverted dependency for two worse ones. Gate 92's 12 shared fixtures under `tests/fixtures/data-viz/` are one harness today and would need re-plumbing regardless. | **High — this is the failure mode both panels warn against** |
| **`brand-extraction` without `design-clone`** (or vice versa) | `design-clone/SKILL.md` names `../brand-extraction/extract_brand.py` as its capture half. Moving either alone leaves one reaching across the plugin boundary into the other — the same inverted shape as finding #1, at smaller scale. Plus `repo-build-studio` and `visual-feedback-loop` (core) also reference `brand-extraction`. | **High — atomic pair, one commit or none** |
| **`declarative-visualization` / `svg-report-lint` wholesale** | The `lint.py` halves are **security floors** (no remote `data.url`, no custom loader, no script element, no inline handlers, no foreignObject, no remote href/use — default-fail, no lenient option) enforced by Gates 101 and 103. Gate 148 has core's `wireframe` calling `svg-report-lint` to prove its own goldens clear Gate 103 — moving the linter turns Gate 148 into a core→plugin dependency. | **High — Gate 148 structurally blocks a wholesale move** |
| **`wireframe`** | Five CI gates (145–149) live with it, and it carries a main-session Artifact constraint a subagent can't satisfy. Both panels say don't. | **Medium — but nobody is recommending this** |
| **Any of the 52** | Not evaluated for move-risk; no panel found a case for moving them. | n/a |

---

## Open question for Matt

### 1. `declarative-visualization` + `svg-report-lint` — a genuine fork, not resolved here

Both panels looked at the *same* fact (six domain plugins consume these two skills) and drew opposite
conclusions. Neither is obviously right, both rate themselves low-confidence, and both explicitly
declined to overrule the other.

| | **Panel A — new `plugins/data-visualization/`** | **Panel B — stay in core** |
|---|---|---|
| Reading of the 6-plugin breadth | "No *existing* plugin is their natural home. Folding them into, say, `data-platform` makes five other verticals depend sideways on it — worse topology than today. A dedicated peer plugin gives all six one correctly-typed dependency target." | "Consumed across six genuinely unrelated plugins is the *signature* of correctly-placed shared infrastructure, not of miscategorized domain content." |
| What it concedes | The runnable halves are security floors and must stay in core regardless; only the *method* content (grammar selection, the six-step authoring method, `spec-patterns/`, the surface-to-delivery map) would move. "Lowest-confidence item in this plan. I would not press this over Panel B's objection." | "The `lint.py` security floors are the load-bearing part; the `spec-patterns/` grammar content, while genuinely craft, is closer to `prompt-pattern-library`-style reusable method than to a business vertical. I hold this at low confidence myself." |
| Cost if chosen | A new plugin: `plugin.json`, marketplace registration, README/architecture plugin counts, plus the six consumers' references re-pointed. Gates 101/103/148 stay put. | Zero. Status quo. |

**What actually decides it:** whether a body of reusable *method* with no single owning vertical is
(a) core's job, or (b) evidence that a vertical is missing from the marketplace. That's a taste call
about what this marketplace is for, which is why two competent lenses split on it.

### 2. The definitional crux behind finding #2 — *not* a panel disagreement, but an owner call

This one is an audit-vs-repo disagreement, and it's worth naming because one ruling would settle it
for every future skill instead of re-litigating case by case.

`plugins/ravenclaude-core/CLAUDE.md:1021` currently defends `brand-extraction` as domain-neutral
because *"brand extraction works for any project's brand."* Panel A's rebuttal, which Panel B
re-verified and accepted: **that argument proves client-neutrality, not domain-neutrality.**
`power-platform`'s `pbir-ref-integrity` also works for any client's Power BI report and is still
domain-specific. Every vertical plugin in this repo is client-neutral by construction.

**The question:** does house rule #1's "domain-neutral" mean *"works for any client"* or *"concerns
no specialty"*? Writing the answer into the rule makes it self-applying and stops it producing 50/50
calls. Finding #2 stands or falls on it.

---

## Dependency & sequencing

Three constraints both panels surfaced. They apply to *any* subset you pick.

1. **`design-clone` ↔ `brand-extraction` is an atomic pair (code-linked).** `design-clone/SKILL.md`
   hard-names `../brand-extraction/extract_brand.py` as its capture half. Move both in one commit or
   move neither — either half alone leaves a cross-plugin reach-back, which is the defect being
   fixed, reintroduced at smaller scale.
2. **`wireframe` ↔ `brand-extraction` is epistemically linked (not code-linked).** Core's
   `CLAUDE.md:2001` cites `brand-extraction` as the precedent for `wireframe` staying in core. If
   finding #2 ever lands, that citation evaporates and someone re-raises `wireframe` on a rationale
   nobody actually believes. **Fix:** the `CLAUDE.md` rewrite ships *in* finding #2's PR, not later.
   Panel B independently conceded it missed this chain.
3. **`audit-gates.sh`'s hardcoded skill paths block every move from being a plain rename** (Gates 92,
   100, 101, 103, 145–149; the last cross-calls `../svg-report-lint/lint.py`). Path edits plus
   bidirectional teeth re-proof, every time. See the risk matrix.

**If anything is ever executed:** finding #1 is independent and highest-value — ship it alone first.
Finding #2 is atomic and independent of #1 and #3. Finding #3 depends on nothing but is the lowest
confidence, so it goes last or not at all. Finding #4's doc edit rides in #2's PR.

**Within finding #1**, Panel B adds a constraint Panel A's DAG is consistent with: `lint.py`'s check
dispatch and Gate 92's fixture set are one codebase today, so a partial split would leave the repo in
a broken intermediate state. There is no parallelizable sub-work — it is one atomic engineering task
if you choose to do it.

---

## Alternatives (both panels' options, merged; overlaps marked)

| # | Approach | Raised by | Trade-off |
|---|---|---|---|
| 1 | **High-confidence only.** Do finding #1's split; record the rest as documented tension. | **A1 ≈ B1** — *the strongest overlap; each panel's own recommendation* | Fixes the one mechanical, provable violation at minimal blast radius. Leaves the brand/design contradiction unresolved, so it gets re-raised at the next audit. Panel B's variant is more conservative still: flag only grep-provable coupling and treat even the split as a follow-up ticket, not this cycle's work. Panel B names its own blind spot: this under-flags coupling that leaves no grep trace — e.g. a skill duplicating stale domain facts inline, which it did not separately audit for. |
| 2 | **Split-by-mechanism, generalized.** Any skill mixing generic + vendor-specific logic decomposes into a generic core (stays) + a shim (moves), regardless of whether the coupling is already "sanctioned." | **B3**, and it is the shape **A** independently recommends inside findings #1, #2 and #3 | The most principled answer and the one both panels' actual recommendations converge on. Also the most expensive: fixture re-plumbing, doubled CI gates, cross-reference updates — for a purity gain that the existing "one sanctioned read" pattern arguably already delivers. |
| 3 | **Flag everything, Matt triages.** Deliver all 6 as a ranked queue with evidence; owner rules item by item. | A2 | Maximum optionality, no premature commitment on the arguable calls. But it converts a finished audit into an owner-decision backlog — and 4 of the 6 turn on the *same* definitional question, which one ruling could settle instead of six. |
| 4 | **Settle the definition first, then re-derive.** Ship nothing; get the Open-question-#2 ruling, write it into house rule #1, re-run this audit mechanically against the sharpened rule. | A3 | Highest long-term leverage — the rule becomes self-applying. But it ships zero movement and defers finding #1, which is already provable without the ruling. |
| 5 | **Leave everything, document the tension — plus a new CI gate** that fails when a *new* core skill reads a `plugins/<domain>/` path at runtime. | **A4 ≈ B's Phase-2 acceptance test** (B proposes the same detector: scan `plugins/ravenclaude-core/skills/**/*.{md,py}` for `plugins/<name>/` literals outside a maintained allowlist) | Zero migration risk, and it stops the bleeding mechanically. **Both panels think this gate is worth building under any option** — it turns a manual one-time sweep into a standing detector instead of something that silently drifts again in six months. The cost: it institutionalizes the inverted `pbir-layout-engine` read as sanctioned, which is the precedent `.repo-layout.json` already rejected once for Power Platform content. |
| 6 | **Wholesale relocation of all 6, no splits** / **aggressive name-triage** (relocate anything naming Power BI, Tableau, Deneb, `pac`). | **A5 ≈ B2** — *both panels list it only to reject it* | Cleanest-looking directory listing, simplest story. Drags neutral geometry and two security floors out of core, breaks Gates 100/148 into cross-plugin calls, churns demonstrably-shared infrastructure for cosmetic purity, and produces a mostly-manufactured findings list. Not recommended by either panel. |

**Where the two panels' own recommendations land:** Panel A recommends option 1 now, with option 4's
ruling requested alongside, and option 5's CI gate adopted regardless. Panel B leans option 1 in its
most conservative form, with option 2 as "the only piece of unfinished business worth a follow-up
ticket." **These are compatible.** The reconciled reading: option 1 + the option-5 detector is the
convergent recommendation; option 4's ruling is what unblocks finding #2.

---

## Honest limits of this audit

Carried forward from both panels, because a report that hides its own gaps is worth less than one
that names them.

- **Coverage is frontmatter-deep, not body-deep.** Panel A read all 58 descriptions but only 12 full
  bodies. A skill whose description is neutral while its body is not would be missed. Mitigated by
  the reverse-reference sweep — which is what surfaced `design-clone` — but not eliminated.
- **The reverse-reference counts are a floor, not a census.** Substring matches over
  `*.md`/`*.json`/`*.py`/`*.sh`/`*.yml`; a reference by alias or slash command would not appear.
- **Panel B's grep method under-flags by construction, and says so:** a skill that *duplicates* stale
  domain facts inline rather than reading them from a domain plugin leaves no path literal to match.
  Neither panel audited for that failure mode.
- **No gate was run. No linter was executed.** Every acceptance test in either panel plan is an
  unexecuted *proposal*. Nothing in this report asserts that any gate currently passes or fails.
- **Finding #2 argues against a position this repo holds in writing** (`CLAUDE.md:1021`). That is
  deliberate and stated, not an oversight — and it is why Open question #2 exists rather than a
  verdict.
- **Panel B's coverage gaps, self-reported:** it did not examine `pseudonymize` individually, and did
  not trace `wireframe`'s precedent chain. Panel A covered both; neither gap produced a missed
  finding, but the corroboration on those two items is one-panel, not two.
