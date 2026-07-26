# report-regeneration plugin

> **Status: in active development (Phase 0).** No skills ship on disk yet — they land per release lane (see below). This README describes the target shape from the FORGE plan; treat anything not yet built as a plan, not a delivered feature.

Given an old, already-distributed report used as a **template** — HTML/web→PDF or Office/Word→PDF — plus new data and new source reports, this plugin produces a **same-format regenerated report** (a review-ready draft) and a tiered QA receipt. It does this by performing schema-validated **surgery on a copy of the original artifact**, not by re-rendering from an abstract model.

## The two output formats

| Format | What the gate certifies locally |
|---|---|
| **HTML / web→PDF** | value accuracy (DOM/PDF extraction; XMLA/REST recompute where the source is a Power BI model) + frozen-complement byte-diff + structural isomorphism + axe-core/veraPDF accessibility floor + Playwright render referee |
| **Office (docx→PDF)** | value accuracy + frozen-complement (OOXML) + isomorphism + LibreOffice PDF/UA→veraPDF + LibreOffice render referee |

Both formats are **fully locally certifiable** — no output leg is `not_captured`, and nothing ships with a qualified label.

## Power BI is an input, not an output

The plugin does **not** parse or emit PBIR/.pbix. Its Power BI ingestion adapter is source-side and feeds both output engines:

- **Data via XMLA** (the confirmed tenant route), with a macOS fallback to the Power BI REST `executeQueries` (DAX) endpoint. This is a genuine second execution path — a real re-query against the model — so it strengthens value verification rather than qualifying it.
- **A fresh Power BI report screenshot embedded as an image**, captured via the Power BI Service (or a user-provided image as the always-available fallback). It is always classed `regenerate` — never transplanted from the old template — and guarded by the period-coherence check so a stale-period image can't ship.

If neither data route nor auto-capture is reachable, the plugin degrades **fail-closed**: value accuracy for that node reports "unverified," never a false PASS, and the screenshot falls back to a user-provided image.

## The honest guarantee

The plugin **GUARANTEES two things and only two things:**

> **(a) No old-client-data leak** — no data value, identity string, or literal traceable to the *old* client's report survives into the new deliverable (proven by a blocking, inference-independent egress scan over the *decoded* container). **(b) Every low-confidence classification is surfaced for human review** — no node the classifier is unsure about, and no node bearing a data-shaped literal, ships silently.

It does **NOT** guarantee a human-free-correct report. Auto-QA proves the checked surfaces — value accuracy, byte-stable frozen chrome, structural isomorphism, the machine-checkable accessibility floor — never "the whole report is correct or accessible." **"Review-ready draft"** means exactly this: a draft on which auto-QA has removed the mechanical/QA burden, handed to a downstream human peer reviewer — not a claim of correctness.

## The review model

Human peer review, editing, and distribution stay **out of scope**. The plugin's job ends at a review-ready draft plus its QA receipt:

```
plugin: draft + auto-QA receipt  →  human peer review  →  reviewer feedback  →  Matt edits  →  distribute
```

The reviewer's real feedback (substantive vs. mechanical) is instrumented back into the Binding Manifest and the gold-standard rubric as the calibration signal across successive real reports — there is no in-plugin human-grader gate.

## Phased release train

Landing is a **sequence of `forge/report-regeneration-*` draft PRs**, never one mega-PR, never direct to `main`:

| Release | Adds |
|---|---|
| **v0.1.0** | HTML end-to-end: infer → manifest → surgical rebind → fidelity + accessible PDF copies → QA receipt |
| **v0.2.0** | Office (Word/PDF) path: same manifest/harness, OOXML-native rebinding + LibreOffice PDF/UA export |
| **v0.3.0** | Power BI ingestion adapter: XMLA/REST data-read + Service screenshot capture, feeding both output engines |

## Full plan

The committed design spec — architecture, the six-leg fidelity harness, the security model, and the JSON schemas — lives at [`knowledge/core-architecture-spec.md`](knowledge/core-architecture-spec.md). It was distilled from the deep FORGE planning run, whose raw record (`plan.md`) stays in the local `.ravenclaude/runs/forge/report-regeneration/` run dir and is not committed. This README is a summary for consumers; the architecture spec is the source of truth.

## Requires

- `ravenclaude-core@>=0.204.0`

## See also

- `CLAUDE.md` — the plugin constitution (honest-guarantee spine, format matrix, scope, house-rule compliance, milestones)
- `plugins/ravenclaude-core/CLAUDE.md` — the domain-neutral team constitution inherited by every plugin
