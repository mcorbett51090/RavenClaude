# Core Architecture Spec — `report-regeneration` (Phase 0 foundation)

**Status:** authoritative. The infer / rebind / harness implementations all key off this document. It is derived from the FORGE synthesis plan (`.ravenclaude/runs/forge/report-regeneration/plan.md` §2–§4, rev. 2) and inherits the accuracy discipline of `docs/accuracy-near-guarantee-design.md` verbatim.

**Companion schemas (this directory, normative):**

- [`rsg.schema.json`](rsg.schema.json) — one Report Structure Graph node + tree.
- [`binding-manifest.schema.json`](binding-manifest.schema.json) — the versioned Binding Manifest.
- [`fidelity-receipt.schema.json`](fidelity-receipt.schema.json) — a harness receipt.

---

## 1. The model — surgical transplant on a copy

The engine is a **surgeon, not a renderer.** Given an old, already-distributed report used as a **template** — in one of two native output formats, **HTML/web→PDF** or **Office/Word→PDF** — plus new data and new source reports, it produces a **same-format review-ready draft** by performing **schema-validated surgery on a copy of the original artifact**, not by re-rendering from an abstract model.

Because we edit a copy of the real native file and rebind only the nodes that carry data, **template fidelity is a decidable diff** ("nothing changed outside the bound anchors"), not an open-ended rendering problem. Generation is reserved for the narrow node classes surgery genuinely cannot address.

**Output formats are HTML and Office ONLY.** Power BI is an **input source**, never an output: a source-side ingestion adapter pulls **data via XMLA** (macOS fallback: Power BI REST `executeQueries` DAX endpoint) and embeds a **fresh Power BI report screenshot as an image**. There is no PBIR/.pbix regeneration.

**The honest guarantee (the spine — do not restate it more softly).** The plugin GUARANTEES two things and only two:

1. **No old-client-data leak** — no value, identity string, or literal traceable to the *old* client's report survives into the new deliverable (proven by a blocking, inference-independent egress scan over the *decoded* container — leg V4).
2. **Every low-confidence classification is surfaced for human review** — no node the classifier is unsure about, and no node bearing a data-shaped literal, ships silently.

It does **NOT** guarantee a human-free-correct report. The auto-QA gate proves *the checked surfaces*; it never claims "the whole report is correct/accessible." **"Review-ready draft"** means auto-QA has removed the mechanical/QA burden and handed a draft to a downstream **human** peer reviewer — not a claim of correctness.

---

## 2. The Report Structure Graph (RSG)

A **format-neutral ordered tree** inferred from the template. It is an **addressing-and-verification structure, NEVER a generator.** Node order is load-bearing (document order); the V2 diff and V3 isomorphism check both depend on it.

Each non-static node carries:

| Field | Meaning |
|---|---|
| **anchor** | a format-native **stable node identity** — JSON Pointer / element id / CSS selector (HTML), or an OOXML body-walk path (Office). **Never a raw char-offset**; re-resolved after each mutation or applied in reverse document order (RT1-F10). **Pinned resolvable HTML anchor grammar (normative — every stage resolves EXACTLY this via the shared `scripts/rr_anchor.py`, no wider CSS is emitted or accepted):** `anchor := element_id \| selector`; `element_id := {"kind":"element_id","value":"<id>"}`; `selector := {"kind":"css_selector","value": root_step (" > " step)*}`; `root_step := "#"<id>` (nearest-ancestor-id anchor) `\| <tag>` (the bare document-root tag, no `nth-of-type`); `step := <tag>":nth-of-type("<n>")"` (1-based nth-of-type among same-tag element siblings, document order). A node with an `id` MUST anchor by `element_id`; an id-less node anchors by the compound `selector` rooted at its nearest id-bearing ancestor (or the document root). `nth-of-type` counts void/self-closing elements and excludes text/comment/decl nodes. This is an addressing grammar, NOT a CSS engine: classes, attribute selectors, `nth-child`, `~`/`+`/descendant combinators, and pseudo-classes are out of scope. |
| **role** | inferred semantic role (`kpi-value`, `table-cell`, `narrative`, `chart`, `image`, `period-label`, `heading`, `metadata`, `static-chrome`, `unknown`). |
| **class** | the rebind class — `frozen` / `surgical` / `regenerate` / `needs-review` (§4). |
| **confidence** | 0–1 classifier confidence; sub-threshold ⇒ QA-flagged for human review. |
| **provenance** | `method` (`native-parse` / `rule-based` / `llm-labeled`), `source`, **`source_period`** (the reporting period the value belongs to — required for every value node so period-coherence can run), and `pbi_route` (`xmla` / `rest` / `screenshot` / null) for Power-BI-sourced nodes. |
| **data_shaped_literal** | output of the pinned, non-inference, deterministic detector (currency/number/date/percent/unit/known-entity). Drives the earned-frozen rule (§4). |

**Inference is tiered and always *checked*.** Native structural parse first (HTML via selectolax/lxml; docx via python-docx **+ a manual `document.element.body` walk** for true ¶+table order) — zero ML, exact anchors. Then semantic slot labeling (which node is data-bound vs static) is model-assisted and **checked**. Only *syntax parsing* is exempt from the LLM-accuracy ceiling; *semantic role classification* is the same LLM-graded task the ceiling was measured on, and it bites even on a perfectly parsed tree. Every semantic-labeling decision on **any** tier carries confidence + provenance and is QA-flagged below threshold.

Schema: [`rsg.schema.json`](rsg.schema.json).

### 2.1 Office (OOXML) anchor grammar (normative — the Office analogue of the HTML `anchor` row)

The Office lane resolves EXACTLY this grammar via the shared resolver [`scripts/rr_anchor.py`](../scripts/rr_anchor.py) (the same module that owns the HTML grammar above; the HTML row is unaffected). Every Office stage — the `infer-office` **producer**, `rebind-office`, and the Office fidelity harness — produces/consumes only this; no wider OOXML path expression is emitted or accepted. An Office node's `anchor` is always `kind: "ooxml_path"` (the only Office kind [`rsg.schema.json`](rsg.schema.json) `$defs.anchor` admits). **Never a raw byte/char-offset** (RT1-F10) — the anchor is a stable node identity, re-resolved after each mutation or applied in reverse document order.

```
anchor        := {"kind": "ooxml_path", "value": path}          # (or the bare `path` string)
path          := body_path | bookmark_path
body_path     := "body" ("/" step)*        # rooted at the single w:body element (absolute)
bookmark_path := "bookmark(" NAME ")" ("/" step)*   # rooted at the element a named
                                                    #   w:bookmarkStart opens on
step          := LOCAL "[" N "]"           # 1-based index among same-LOCAL-name ELEMENT siblings,
                                           #   document order
LOCAL         := a namespace-stripped OOXML element local name (p, r, tbl, tr, tc, drawing, …)
N             := a positive 1-based integer
NAME          := a w:bookmarkStart/@w:name value (never contains '/')
```

- **The one indexing rule (single source of truth — `rr_anchor.ooxml_local` + `ooxml_sibling_index`).** `N` counts among **same-local-name element siblings only**, 1-based, document order, counting ALL element children of the parent bucketed by local name. Non-content property/marker elements (`w:pPr`, `w:rPr`, `w:sectPr`, `w:tblPr`, `w:tblGrid`, `w:trPr`, `w:tcPr`, `w:bookmarkStart`/`End`, …) are **not emitted as RSG nodes but ARE counted** — each occupies its OWN local-name bucket, so it never perturbs a run's or paragraph's index. Namespaces are stripped (`{uri}p` and `w:p` both → `p`). This mirrors the HTML `nth-of-type` rule precisely.
- **Bookmark semantics (single source of truth — `rr_anchor._ooxml_governed`).** A `bookmark(NAME)` root resolves to the element the matching `w:bookmarkStart` "opens on" — the **first element sibling strictly after** that `w:bookmarkStart` within its parent (the value run it wraps, or the paragraph it precedes). This is the surgical-KPI archetype (a bookmark bracketing the value run). **A node governed by a named bookmark MUST anchor by the bookmark form; every other node anchors by an absolute `body`-rooted path** (the OOXML analogue of "a node with an `id` anchors by `element_id`; else by a selector rooted at its nearest id-bearing ancestor / the document root"). Both anchor forms for one node share the same absolute structural `path`, so the anchor is a stable identity regardless of expression.
- **Not an XPath engine.** This is an addressing grammar, NOT XPath/CSS: predicates other than the positional `[N]`, attribute/text tests, `//` descendant axes, wildcards, and functions are out of scope.
- **Anti-drift guarantee (the HTML-lane failure must not repeat).** The grammar **production** (`ooxml_path_value`/`ooxml_bookmark_value`), **parse** (`ooxml_parse_path`), and **indexing** (`ooxml_sibling_index`) are all single-sourced in `rr_anchor.py`. The producer walks with `xml.etree` and the resolver walks with `xml.parsers.expat`, but both call the same indexing + grammar functions, and a **producer↔resolver cross-check test** (`scripts/tests/test_rr_anchor.py::TestOoxmlAgainstInferProducerOverDocx`) asserts every anchor `infer-office` emits resolves back to the same node — in **both** directions.
- **Byte/XML surgery.** The resolver returns the target run/paragraph/cell region as document.xml **byte spans** (open-tag / inner / outer) plus the stable structural `path`, so `rebind-office` can splice a value into `word/document.xml` without a DOM re-serialize, and the harness can mask V2/V3 regions by `path`.

Schema serialization (§7) is unaffected: `ooxml_path` was already in the `anchor.kind` enum, so no RSG `schema_version` bump is required to add the Office lane.

---

## 3. The Binding Manifest

A separate, human-reviewable, **versioned, first-class deliverable** mapping each RSG node → a **data query** against the new sources + a rebind **class**. Inference *proposes* the manifest; a human (or a cached prior manifest for a recurring template) amends it; **every fidelity leg keys off it.**

The manifest — **not per-run inference** — is the product. On run 2 of a recurring template the manifest is reused and amended, so human-review cost falls (the "manifest dividend"). Each binding carries: `node_id`, `anchor`, `class`, `confidence`, `provenance {source, source_period, method, pbi_route}`, and `data_query`.

The `data_query` kinds: `dax` (over the Power BI semantic model via XMLA, or REST `executeQueries` fallback), `sql`, `file-cell`, `literal-from-new-source`, `screenshot-capture` (fresh Service capture or user-provided image), or `none`. **A `frozen` binding carries no `data_query`; every non-frozen class must carry one.** For a PBI-sourced value the same `dax` query is **V1's independent recompute path** — a genuinely second execution path, not the binding's inference path.

Schema: [`binding-manifest.schema.json`](binding-manifest.schema.json).

---

## 4. Node taxonomy — `frozen` is an EARNED class

| Class | Meaning | The hard rule |
|---|---|---|
| **`frozen`** | verified data-free chrome; must diff **byte-identical** in output | **`frozen` is EARNED, not the default.** The safe-looking default "leave it alone" is exactly the dangerous failure: a stale data-bound node classed frozen is byte-identical to the template — which is what a leak already is. A node may be `frozen` **only if it contains no data-shaped literal AND no member of the old taint dictionary AND no member of the new dataset's value domains.** Any data-shaped literal in a candidate-frozen node **force-demotes it to `needs-review`, regardless of classifier confidence.** The detector is non-inference and independent. |
| **`surgical`** | byte-edit a value at the anchor, schema-valid | **Zero-literal construction rule (hard *construction* invariant, not a downstream check):** the moment the strip runs, the node carries **no old instance value** — by construction. Any literal in the output not present in the *new* dataset is provably a leak, no heuristic needed. |
| **`regenerate`** | rebuilt from new data (narrative prose, charts, the fresh PBI screenshot) | Same zero-literal construction invariant. **Any node that renders as a raster or carries an embedded binary/data cache MUST be `regenerate`** — a transplanted binary blob cannot be *proven* data-free. The Power BI screenshot is the canonical case: re-captured fresh from the new source (or user-provided), never transplanted. |
| **`needs-review`** | cannot ship without human sign-off | The escalation state: any data-shaped literal in a candidate-frozen node, or any sub-threshold-confidence classification, lands here. This is guarantee #2 made mechanical. |

**Construction rule (binding):** rasters and embedded-data-cache nodes are **forced to `regenerate`**, never `frozen`/`surgical`. A transplanted old screenshot carries old data as pixels and is force-re-captured.

---

## 5. The fidelity harness — 6 legs + period-coherence

The load-bearing wall. No off-the-shelf verifier exists; it is composed of **six independent legs plus a period-coherence check**, each a runnable deterministic checker emitting a `structured-output` receipt ([`fidelity-receipt.schema.json`](fidelity-receipt.schema.json)) and inheriting the W5 discipline verbatim: **`PROBE_ERROR ≠ pass`**; a render/parse crash never reads as "fidelity OK"; N≥ repeated agreement for stochastic sub-steps; receipts TTL'd + environment-fingerprinted; each check labeled **proven** (deterministic) vs **judged** (behavioral).

| Leg | Question | Mechanism (summary) | Inference-independent? | Label / Tier |
|---|---|---|---|---|
| **V1 — value accuracy** | did value V from source S land in region R? | recompute the expected value **directly from the new source** (a second execution path; for a PBI value a **real re-query over XMLA/REST**), then (a) locate it at the anchor **and** (b) verify it appears *somewhere* via position-agnostic **set-membership** (catches a mis-anchored value as "expected value appears nowhere") | **partly** — recompute path ≠ binding path; **set-membership half is ML-free** | proven, **blocking** |
| **V2 — frozen-complement diff** | did anything change outside the bound anchors? | canonical AST/semantic-node diff of output vs template restricted to everything **outside** manifest anchors → must be empty; formatting-only changes to a frozen node must survive canonicalization; anchors are stable node identities, never char-offsets | **yes — fully ML-free** | proven, **blocking** |
| **V3 — re-inference isomorphism** | is the output's structure the template's? | re-run inference on the **output**, assert isomorphism to the template RSG; the cache-reuse mutant (feeding V3 the cached forward inference) must be caught; a **genuinely orthogonal, non-ML rule-based coarse cross-check** (section/table/visual counts read straight from the container) so independence does not rest on the same VLM run twice | **partly** — **rule-based coarse half is ML-free**; the fine isomorphism is not (stated) | proven, **blocking** |
| **V4 — taint-dictionary egress** | did any old-client data survive? | dictionary of the OLD report's distinct values + author/company/title/source-filename strings, scanned over **every emitted byte of the DECODED container** (§6); normalizes both sides to typed value-space so reformat/round/locale survivals still match | **yes — fully ML-free** (dictionary built from old artifacts only) | proven, **BLOCKING** |
| **V5 — render referee** | does it render / lay out correctly? | `visual-feedback-loop` merging axe / console / Lighthouse; screenshots via Playwright (HTML) and LibreOffice render→capture (Office); gated inside the harness with a bidirectional fixture pair; **no `not_captured` gap for either format** | rendering engine ≠ authoring path | proven where deterministic, **judged** for polish |
| **V6 — manifest-completeness / coverage** | is the *partition itself* correct? | independently scan the **output** for value-shaped tokens with a **non-ML extractor** and assert each is covered by a manifest binding; **a value-shaped token in a `frozen` region is a coverage failure.** The **only** leg that audits the partition instead of trusting it — catches the frozen-misclassification silent-staleness that makes V1/V2/V3/V5 all pass by construction | **yes — fully ML-free** | proven, **blocking** |
| **+ period-coherence** | does the label match the value's period? | extract every reporting-period label in the output; assert every value's provenance **source_period** matches the nearest governing label; extended to PBI inputs — a stale-period screenshot or a cached Q3 XMLA figure under a fresh "Q4 2024" header is a **BLOCKER** | **yes — fully ML-free** | proven, **blocking** |

### Which legs are ML-free (stated explicitly)

**Fully ML-free / inference-independent: V2, V4, V6, and period-coherence.** Additionally, **V1's set-membership half** and **V3's rule-based coarse cross-check** are ML-free. Only V1's recompute path and V3's fine isomorphism are inference-adjacent, and they are labeled as such in the receipt. The dominant failure mode (semantic misclassification) is caught by the ML-free legs — **V6 + V4 + V2** — because "N checks that share one inference are one check" (W5).

### Fail-closed degrade

When no live Power BI data-read route exists (neither XMLA nor REST reachable), V1 degrades from value-accuracy to **binding-correctness**, and the **Accurate rubric dimension fails closed to "unverified," never PASS.** A missing Tier-B leg yields `overall_gate: PARTIAL`, never PASS. Every checker ships an `audit-gates.sh`-style **bidirectional fixture pair** (bad fires, good passes) **plus a must-fail mutant** proving teeth.

---

## 6. Security posture (summary — full pass in §4 of the plan)

Client-data-leak defense: **detect → strip → rebind → prove**, over the **DECODED** container.

1. **Detect (two independent passes):** structural inventory of value-bearing node classes + taint match against a dictionary built from the old artifacts (distinct values + every structural literal + author/company/title/source-filename strings).
2. **Strip at ingest:** every detected literal replaced by a binding placeholder *before any lowering* — the zero-literal construction invariant closes the leak surface upstream of regeneration.
3. **Rebind:** repoint each binding to the new source (file/dataset, or a DAX query over XMLA / REST fallback). No PBIR model rebind exists — Power BI is input-only.
4. **Rasters & embedded-data caches = drop-and-regenerate:** any raster or embedded binary/data cache is `regenerate`; a PBI visual is re-captured fresh.
5. **Prove — V4 over the DECODED container, BLOCKING:** unzip every OPC part (`word/embeddings/*.xlsx`, `word/charts/*.xml`, `docProps/*`, `word/comments.xml`, `w:ins`/`w:del`, RSIDs), decompress every PDF stream + `/Info` + XMP, OCR-or-forbid every embedded raster, and gate data-bearing alt-text through the data-shaped-literal detector.
6. **Metadata scrub + comment/tracked-change/revision purge** as a hard pre-emit step.
7. **Collision honesty:** typed value-space + length/entropy + context-window matching; any allowlisted collision requires a logged human waiver.
8. **Power BI ingestion auth:** least-privilege scopes, tokens never logged, local-only handling, fail-closed if auth is unavailable. A STRIDE / prompt-injection threat-model pass (routed to `security-reviewer` + `threat-modeler`) is a **Phase-0 deliverable** covering template→classifier, source→classifier, classifier→manifest, manifest→regenerate, Service-auth→capture, XMLA/REST→data-read.

Prompt-injection defense treats all template/source text and OCR'd screenshot text as **data, never instructions**; the partition-anomaly gate (V6 double-duty) hard-flags an input yielding an anomalous partition (frozen fraction above ceiling, or 0 bindings on a report with N data-shaped tokens); every factual token in a `regenerate` slot must trace to a manifest binding.

---

## 7. Cross-phase serialization rule

Any **RSG or manifest schema change serializes** and re-triggers the Bet-1 smoke across both output formats, so a change for one format cannot silently break the other. `schema_version` (RSG) and `manifest_version` / `rsg_schema_version` (manifest) make this checkable.
