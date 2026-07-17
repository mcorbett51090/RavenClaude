# Inference failure modes — `report-regeneration`

**Status:** knowledge-bank deliverable (plan §9 — "inference-failure-modes (C17)"). Reference only — the taxonomy, RSG/manifest schemas, and the six-leg harness live in [`core-architecture-spec.md`](core-architecture-spec.md); this document does not restate them, it explains **why the classifier is wrong 5–15% of the time, in what specific ways, and how the system turns that into a surfaced review flag instead of a silent leak or a silent mistake.**

---

## 1. The ceiling (claims-table claim 17 — verified, carried verbatim)

> Structure-inference **failure modes**: ~**85–95% accuracy on well-structured docs**, lower on degraded/handwritten; VLMs **"don't see structure the way OCR does"** → **cross-contamination between sections** (e.g. mixing values between adjacent items); **reading-order errors in multi-column**; the *hard* problem is **structural consistency across variations of the same doc type** with a generic prompt.

Sources (claims-table, retrieved 2026-07-16): [unstract LLMs-for-PDF-extraction](https://unstract.com/blog/comparing-approaches-for-using-llms-for-structured-data-extraction-from-pdfs/), [vellum LLMs-vs-OCR](https://www.vellum.ai/blog/document-data-extraction-llms-vs-ocrs). Implication drawn there: **inference must be checked, never trusted blind — feeds the accuracy gate.** That implication is the spine of this document.

---

## 2. Why native-parse is NOT exempt for semantic labeling (REQ-3, R24 — binding)

The plan explicitly **strikes** the framing "the 85–95% ceiling does not apply to structured formats" (plan §2, REQ-3). The distinction that survives:

| Tier | What it does | ML? | Ceiling applies? |
|---|---|---|---|
| **Native structural parse** (HTML via selectolax/lxml or stdlib `html.parser`; docx via python-docx + manual `document.element.body` walk) | Determines the *tree* — what nodes exist, in what order, with what native anchor | **Zero** — exact syntax parsing | **No.** This tier produces exact anchors from a real file's real markup; there is nothing for an 85–95%-accuracy ceiling to apply *to*. |
| **Semantic role labeling** (which node is `kpi-value` vs `static-chrome` vs `narrative`, native-parse tier or model-assisted) | Decides what each already-correctly-parsed node *means* | **Model-assisted, checked** | **Yes.** This is the same LLM-graded task claim 17's ceiling was measured on, and — the load-bearing point — **it bites even on a perfectly parsed tree.** A perfect DOM/OOXML parse tells you a `<td>` exists in the right place; it does not tell you whether that `<td>` is a data-bound total or static boilerplate. That decision is where the ceiling lives. |

Having a real native file to operate on (the "surgeon, not a renderer" backbone, `core-architecture-spec.md` §1) makes the *addressing* problem exact. It does not make the *classification* problem exact. Confusing the two is precisely the framing REQ-3 forbids.

---

## 3. Named failure modes and what actually catches each one

| Failure mode (claim 17) | What it looks like here | What catches it | Residual (honest) |
|---|---|---|---|
| **Frozen-misclassification** — a data-bound node wrongly labeled `static-chrome`/`frozen` | The single highest-leverage inference error in the whole system: a `frozen` node ships byte-identical, with **no further scrutiny** from V1's recompute or from rebinding (`core-architecture-spec.md` §6, threat-model T1: "classify everything as frozen") | **(1)** The earned-frozen construction rule — an independent, non-inference deterministic detector (data-shaped-literal / old-taint-dictionary / new-dataset-value-domain) force-demotes to `needs-review` **regardless of classifier confidence**. **(2)** V6 (manifest-completeness/coverage) as backstop — audits the *output*, independently, for value-shaped tokens sitting in a `frozen` region; this is the only leg that audits the partition instead of trusting it. | R1 (plan §11): **5–15% classifier tail on genuinely ambiguous nodes → surfaced, not silent.** Not eliminated — converted. See §4 below. |
| **Cross-section contamination** — the VLM/LLM tier mixes a value from one section into an adjacent section's slot during semantic labeling | A KPI value or table cell gets attached to the wrong node — plausible-looking, wrong | **No single leg is named for this failure mode specifically.** It resolves into one of two shapes downstream, each already covered: **(a)** the misassigned binding produces a value that doesn't match what V1's independent recompute expects at that anchor, and V1's position-agnostic set-membership check flags "expected value appears nowhere" for the *correct* value; **(b)** if the contamination instead produces a *classification* error (right value, wrong role/class), it is the frozen-misclassification case above. Neither path is a dedicated "cross-contamination detector" — it is the general classifier-tail residual (R1), surfaced via confidence + the deterministic legs, not silently trusted. | Same R1 residual — this is explicitly one of the shapes the "5–15% genuinely ambiguous" tail can take. |
| **Reading-order errors in multi-column layouts** | The semantic-labeling tier misreads document flow | The RSG's node order is **load-bearing (document order)** and is established by the **native-parse tier — zero ML, exact** (`core-architecture-spec.md` §2). Reading-order confusion is a risk for the *rendered-only* Docling/VLM ingestion path (source-report data ingestion, not template reconstruction — `core-architecture-spec.md` §2 explicitly scopes VLM-only inference away from the template); for the template itself, the tree order never depends on the model. V3's isomorphism check + its rule-based coarse cross-check (section/table/visual counts read straight from the container) catch a structurally wrong *output*. | The template-side tree order is genuinely inference-independent; the residual risk is confined to the source-ingestion path, where V1's recompute-plus-set-membership is the backstop. |
| **Structural consistency across doc-type variations with a generic prompt** (claim 17's named "hard problem") | A classifier that works well on one instance of a recurring template drifts on the next instance of "the same" template type, because a generic prompt doesn't encode the specific template's idiosyncrasies | **Not solved by better prompting** — solved architecturally, by not re-trusting inference every run. A human-amended Binding Manifest, keyed to `template_id`, is reused and only amended on repeat runs of the *same* template — see [`manifest-reuse-contract.md`](manifest-reuse-contract.md). The manifest, not per-run inference, is the product (`core-architecture-spec.md` §3). | Genuinely new templates still pay the full classifier-tail cost on run 1; the dividend is specifically a recurring-template property (plan R20 residual: "one-shot retargeting supported but explicitly not the value case"). |

---

## 4. How confidence + provenance + `needs-review` surface the ceiling (guarantee (b), made mechanical)

The plugin's second guarantee — **"every low-confidence classification is surfaced for human review; no node the classifier is unsure about, and no node bearing a data-shaped literal, ships silently"** (`CLAUDE.md` §1) — is the direct, named answer to the 85–95% ceiling. It does not claim to close the gap; it claims to never let the gap ship silently. Mechanically:

1. **Every RSG node carries `confidence` ∈ [0,1] and `provenance {method, source, source_period, pbi_route}`** (`rsg.schema.json`). `method` distinguishes `native-parse` / `rule-based` (inference-independent, exempt from the ceiling) from `llm-labeled` (ceiling-bound, C17).
2. **Sub-threshold confidence on *any* tier is QA-flagged for human review** — not just the `llm-labeled` tier. The default confidence threshold in the current implementation is `0.7` (`skills/rebind-manifest/build_manifest.py --confidence-threshold`, verified this session).
3. **Confidence alone never earns "ship silently."** This is the load-bearing distinction from a naive confidence-threshold gate: even a *high*-confidence `frozen` classification is force-demoted to `needs-review` if the independent, non-inference detector fires on a data-shaped literal, a taint-dictionary member, or a new-dataset value-domain member. `rebind-manifest`'s own design note states this explicitly: *"the detector is deliberately non-inference: it fires on `'100%'` in a marketing tagline exactly as on a KPI's `'100%'`. Over-flagging a candidate-frozen node to `needs-review` is the safe direction (guarantee (b)); under-flagging a data-bound node classed frozen is what a leak looks like."* Confidence is a QA signal on the classifier's *labeling* task; it is never the authority on the *earned-frozen* safety property.
4. **`needs-review` is guarantee (b) made mechanical** (`core-architecture-spec.md` §4; `rebind-manifest/SKILL.md`). A node in this class cannot ship without a human sign-off, full stop — there is no confidence score high enough to bypass it once the deterministic detector or the sub-threshold check has fired.

The net shape: the ceiling is real and unclosed (R24: "inherent classifier ceiling — surfaced, never trusted"), but the system's response to it is structural, not aspirational — a wrong classification either gets caught by an ML-free leg (V2/V4/V6/period-coherence) or lands in `needs-review`, and the honest residual (R1's 5–15% tail) is exactly the size of "genuinely ambiguous nodes a human still has to look at," never the size of "nodes that silently shipped wrong."

---

## 5. Cross-references

- Node taxonomy, the earned-frozen rule, the six-leg harness: [`core-architecture-spec.md`](core-architecture-spec.md) §2, §4, §5.
- The prompt-injection flavor of frozen-misclassification (an attacker *inducing* the same failure mode deliberately): [`threat-model-stride.md`](threat-model-stride.md) §1, T1.
- Tool-level grounding for the native-parse tier: [`per-format-toolchain.md`](per-format-toolchain.md).
- How the manifest reuse dividend narrows the "structural consistency across variations" problem over successive runs: [`manifest-reuse-contract.md`](manifest-reuse-contract.md).
