# report-regeneration Plugin — Team Constitution

> Team constitution for the `report-regeneration` Claude Code plugin. **Status: v0.1.0 — 11 skills ship on disk.** The **HTML / web→PDF lane is end-to-end certified** (30/30 acceptance checks, 14/14 seeded defects caught crisply); the **Office (docx→PDF) lane is built + unit-tested with its end-to-end assembly deferred** (see the FORGE run's `BUILD-STATE.md`); **Power-BI ingest is scaffolded, pending a service principal** (the v0.3.0 lane). Nothing in this file should be read as "already built" unless the Milestones section below says so.
>
> **Orientation:** this file is domain-specific to report-regeneration work. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).
>
> **The committed authoritative design spec is [`knowledge/core-architecture-spec.md`](knowledge/core-architecture-spec.md)** — with the JSON schemas beside it, the frozen contract this plugin is built against. It was distilled from the deep FORGE planning run, whose raw record (`plan.md`) stays in the local `.ravenclaude/runs/forge/report-regeneration/` run dir and is **not committed**. This CLAUDE.md restates the spec's binding spine; if the two ever disagree, the architecture spec wins and this file is stale.

---

## 1. The honest guarantee (the spine — do not restate it more softly anywhere)

The plugin **GUARANTEES two things and only two things:**

> **(a) No old-client-data leak** — no data value, identity string, or literal traceable to the *old* client's report survives into the new deliverable (proven by a blocking, inference-independent egress scan over the *decoded* container). **(b) Every low-confidence classification is surfaced for human review** — no node the classifier is unsure about, and no node bearing a data-shaped literal, ships silently.

It does **NOT** guarantee a human-free-correct report. Auto-QA proves the checked surfaces — never "the whole report is correct/accessible." Every agent, skill, and doc in this plugin restates this guarantee **verbatim** or points here — never a softened paraphrase ("mostly accurate," "high confidence," "production-ready without review").

---

## 2. Format matrix

| Format | What the gate certifies locally | Success-signal label |
|---|---|---|
| **HTML / web→PDF** | value accuracy (DOM/PDF extraction; XMLA/REST recompute where the source is a PBI model) + frozen-complement byte-diff + structural isomorphism + axe-core/veraPDF a11y floor + Playwright render referee | Locally certifiable — full review-ready draft |
| **Office (docx→PDF)** | value accuracy + frozen-complement (OOXML) + isomorphism + LibreOffice PDF/UA→veraPDF + LibreOffice render referee | Locally certifiable — full review-ready draft |

Power BI is an **input** source only (XMLA data-read, REST `executeQueries` macOS fallback, plus a fresh Service-captured or user-provided screenshot embedded as an image) — never an output format. No PBIR/.pbix is parsed or emitted.

---

## 3. Architecture summary

The engine is a **surgeon, not a renderer**: it ingests the template as a real native-format file (HTML or Office), works on a **copy**, and rebinds only the nodes that carry data, so template fidelity is a decidable diff rather than an open-ended rendering problem. A Report Structure Graph plus a versioned, human-reviewable **Binding Manifest** address and verify — they never generate. Every node is classed `frozen` (verified data-free chrome, byte-identical in output — **earned, never the default**, since a stale data-bound node classed frozen is indistinguishable from a leak), `surgical` (byte-edit at the anchor under a **zero-literal construction rule**: the moment the strip runs, the node carries no old instance value, by construction, not by downstream check), or `regenerate` (rebuilt from new data; any raster or embedded-data-cache node is forced here, since a transplanted binary cannot be proven data-free). All three classes are checked by a **six-leg fidelity harness** — V1 value accuracy, V2 frozen-complement diff, V3 re-inference isomorphism, V4 taint-dictionary egress (blocking, over the decoded container), V5 render referee, V6 manifest-completeness/value-coverage — plus a period-coherence check guarding that every value and PBI-sourced screenshot/figure matches the *new* reporting period; V2, V4, V6, and period-coherence are fully **ML-free**, and the dominant failure mode (semantic misclassification) is caught by exactly those ML-free legs.

---

## 4. Scope

**In scope:**
- Structure inference + Binding Manifest generation from an HTML or Office template
- Surgical rebind of `frozen`/`surgical`/`regenerate` nodes to new data
- Power BI ingestion as a source: XMLA/REST data-read, Service/user-provided screenshot embed
- The six-leg + period-coherence fidelity harness, per format
- The no-old-client-data-leak egress scan and metadata/comment/tracked-change purge
- Emitting a review-ready draft + tiered QA receipt

**Out of scope:**
- Human peer review, editing, or distribution of the draft (stays with the client/Matt, outside the plugin)
- PBIR/.pbix regeneration or any Power BI *output* path
- A secured in-plugin human-grader gate (replaced by instrumenting real client peer-review feedback as the calibration signal)
- Any claim of "correct" or "accessible" beyond what the checked surfaces prove

---

## 5. House-rule compliance

- **Reuses core agents — never forked.** `code-reviewer` and `security-reviewer` run the review loops (security-reviewer's verdict is binding; PBI token-handling findings route here as un-waivable P0s); `architect` handles design + loop-escalation; `data-engineer` authors XMLA/REST data-read and recompute-path code; `documentarian` writes QA-report prose; `viz-spec-reviewer` covers any shipped chart spec.
- **`report-regeneration-engineer`: FOLDED — no new agent** (Phase-1 litmus discharged 2026-07-16; see [`knowledge/new-agent-litmus.md`](knowledge/new-agent-litmus.md)). Ran against real code: `scripts/e2e_acceptance.py` orchestrates the whole infer→manifest→rebind→harness→QA pipeline as a plain stdlib script with **zero agent reasoning in the loop**, and every invariant (earned-frozen, zero-literal, V4-blocking, `not_captured⇒PARTIAL`) is code-enforced — no un-codifiable role justifies an agent. The work folds onto core agents via inline priors: **`data-engineer`** drives the pipeline + amends each binding's `data_query`; **`backend-coder`** owns the stdlib output engines + scripts; **`security-reviewer`** (binding) owns the V4 leak spine + PBI token handling (un-waivable P0); **`architect`** owns RSG closed-set review + loop-escalation + schema serialization; **`documentarian`**/`viz-spec-reviewer`/`code-reviewer` per §6b. **Revisit tripwire:** re-run the litmus on the Office (v0.2.0) / PBI (v0.3.0) lanes if either surfaces genuinely tacit craft. Follow-up (v0.1.0 PR): write these priors onto the six `ravenclaude-core/agents/*.md` files.
- **Local-only for sensitive data.** Privacy classification is SENSITIVE; execution is LOCAL-only; this is a hard cap, not an Ultraplan candidate, and never lands direct to `main`.
- **macOS bash-3.2 / no-GNU floor.** Every shell script in this plugin (hooks, checkers, audit-gate fixtures) is bash-3.2-safe: no `declare -A`, no `mapfile`, no `${v^^}`; use `_rc_timeout` not bare `timeout`, `_rc_pcre_match` not `grep -P`, no `sed -i` GNU-isms. Run under `env -i PATH=/usr/bin:/bin`.

---

## 6. Milestones

- **Milestone 0 — DONE:** FORGE deep-plan synthesized (`plan.md` rev.2) + Phase-0 scaffold.
- **Milestone 1 — v0.1.0 (this PR):** HTML / web→PDF lane end-to-end certified (30/30 acceptance, 14/14 seeded defects caught); Office lane built + unit-green (E2E assembly deferred); PBI ingest scaffolded. **11 skills, 0 agents** — the `report-regeneration-engineer` agent FOLDED (no new agent — see §5). Skill/agent counts reconciled against Gate 12. The six-round security + code-review loop converged: 1 P0 (V4 comment-leak) plus a chain of P1/P2/P3 leak-surface findings, each empirically demonstrated then fixed with a passing regression test (~325 tests).
- **Milestone 2 — v0.2.0 (next):** Office end-to-end assembly (annotated docx fixture + role/position binding strategy).
- **Milestone 3 — v0.3.0:** Power-BI ingest live (XMLA/REST data-read + `exportToFile` screenshot embed), once a service principal is provisioned.

---

## 7. References

- The committed design spec: [`knowledge/core-architecture-spec.md`](knowledge/core-architecture-spec.md) — distilled from the deep FORGE run `plan.md`, which stays under the local `.ravenclaude/runs/forge/report-regeneration/` run dir (not committed)
- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Meta-repo developer guide: [`../../AGENTS.md`](../../AGENTS.md)
