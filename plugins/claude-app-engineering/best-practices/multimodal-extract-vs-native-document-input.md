# Document input — native PDF/image vs pre-extracted text

**Status:** Pattern — strong default for any app feeding documents to Claude; deviate only with a written reason.

**Domain:** Input / multimodal

**Applies to:** `claude-app-engineering`

---

## Why this exists

Feeding documents to Claude is a very common app shape (contracts, invoices, reports, scanned forms), and there are three ways to get a document into the context window — send it **natively** (PDF/image to a vision-capable model), **pre-extract text** (OCR/parse, send the text), or route it through the **Files API** for reuse — with materially different cost, fidelity, and capability tradeoffs. Teams default to one (usually "just send the PDF") without weighing it, and pay for it: native document tokens are expensive at volume, while naive text extraction throws away layout/tables/figures the task needed. This rule makes the choice deliberate.

## How to apply

Choose by **what the task needs from the document** and **volume**:

- **Native PDF / image** — when layout, tables, figures, handwriting, or visual structure matter (a form's spatial layout, a chart, a scanned doc). Requires a **vision-capable model** (check the capability map). Costs more tokens per page; best when fidelity > cost and volume is modest.
- **Pre-extracted text** — when the document is genuinely text and you only need the words (a plain article, a text-only contract clause). Cheaper, faster; you control chunking. Lossy for anything visual — don't use it where layout carries meaning.
- **Files API** — when the **same** document is referenced across many requests/turns: upload once, reference by id, avoid re-sending bytes every call. Pairs with either native or extracted input.
- **RAG over the corpus** — when the question spans a large document set rather than one document (see the RAG rule; skip RAG under ~200K tokens — long-context may be simpler).

**Cost discipline:** at volume, native document input is a real line item — measure cost-per-resolved-task, and pre-extract where the visual layer adds nothing.

**Do:** match input mode to what the task reads from the document; use a vision model for genuinely visual docs; Files API for reused documents; pre-extract text-only docs to cut cost.

**Don't:** send native PDFs by reflex when plain text would do (cost); pre-extract a form/chart/scan and lose the layout the task needed (fidelity); re-send the same document's bytes every turn instead of the Files API.

## Edge cases / when the rule does NOT apply

A one-off, low-volume document read where engineering time > token cost: just send it natively and move on. Encrypted/password-protected or very large PDFs may need pre-processing regardless. Exact vision-model support, per-page token costs, and Files API retention/limits are volatile — check the capability map, don't quote from memory (`[verify-at-use]`).

## See also

- [`./rag-skip-it-under-200k.md`](./rag-skip-it-under-200k.md) — one document vs a corpus
- [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — which models are vision-capable; Files API limits (dated)
- [`../knowledge/server-side-tools-and-files.md`](../knowledge/server-side-tools-and-files.md) — Files API mechanics
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns context/input design

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01, both panels AGREE): the plugin covered Files API + RAG thoroughly but had no rule for the native-vs-pre-extract document-input fork — a common, frequently-mis-defaulted design decision. Vision-model support + token costs are `[verify-at-use]` against the capability map.

---

_Last reviewed: 2026-06-01 by `claude`_
