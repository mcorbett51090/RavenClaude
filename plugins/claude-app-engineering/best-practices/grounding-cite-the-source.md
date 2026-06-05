# Ground factual claims with source citations, not model assertions

**Status:** Pattern
**Domain:** RAG / grounding / hallucination reduction
**Applies to:** `claude-app-engineering`

---

## Why this exists

A Claude app that asks the model to answer from memory (or from a poorly-cited
RAG result) produces confident wrong answers — and the consumer has no signal
to distinguish them from correct ones. Forcing the model to cite the specific
retrieved document and passage it is drawing from gives the end-user a
verification path and gives the app a measurable grounding rate. Apps that skip
citations typically discover the hallucination rate only after a customer
escalation.

## How to apply

Structure the RAG prompt to require citation in the response schema, and return
citations alongside the answer as structured output.

```python
CITATION_TOOL = {
    "name": "answer_with_citations",
    "description": "Return an answer grounded in the retrieved documents. "
                   "Include a 'citations' list with doc_id and the exact quoted "
                   "passage that supports each claim.",
    "input_schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
            "citations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "doc_id": {"type": "string"},
                        "passage": {"type": "string"},
                        "claim_supported": {"type": "string"},
                    },
                    "required": ["doc_id", "passage", "claim_supported"],
                },
            },
        },
        "required": ["answer", "citations"],
    },
}

# System prompt addition:
# "Answer only from the retrieved documents. For every factual claim,
#  cite the doc_id and the exact passage. If the documents don't contain
#  the answer, say so — do not answer from training knowledge."
```

Evaluate the grounding rate in evals: for each citation, check that the `passage`
appears verbatim in the referenced document.

**Do:**
- Force citation via a structured tool call (not a "please cite" instruction) so
  the format is machine-verifiable.
- Include citation grounding rate as a metric in your eval harness.
- Show the source passages in the UI so end-users can verify.

**Don't:**
- Ask for citations in the system prompt and then parse them from prose — you'll
  get inconsistent formats and fabricated citation strings.
- Accept citations where the passage is paraphrased; require the verbatim quote
  so it's checkable.
- Use citation grounding as a substitute for retrieval quality — a low-quality
  retriever cites the wrong document confidently.

## Edge cases / when the rule does NOT apply

- Creative / generative tasks (story writing, brainstorming) where grounding to
  a source document is not the goal.
- Summarisation tasks where the entire document is in-context and every sentence
  is implicitly sourced.

## See also

- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns RAG + citation strategy
- [`./rag-retrieve-quality-over-quantity.md`](./rag-retrieve-quality-over-quantity.md) — grounding depends on retrieving the right chunk first
- [`./output-structured-via-forced-tool.md`](./output-structured-via-forced-tool.md) — use forced tool call for machine-verifiable citation format

## Provenance

Codifies the citation-grounding discipline from
`knowledge/retrieval-and-rag-2026.md` (retrieved 2026-05-28) §"Contextual
Retrieval" and the `prompt-engineering-techniques.md` hallucination-reduction
section. Standard RAG grounding practice.

---

_Last reviewed: 2026-06-05 by `claude`_
