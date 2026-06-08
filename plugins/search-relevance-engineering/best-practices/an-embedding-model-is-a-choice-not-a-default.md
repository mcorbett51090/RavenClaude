# An embedding model is a choice, not a default

**Status:** Pattern
**Domain:** Embedding model selection
**Applies to:** `search-relevance-engineering`

---

## Why this exists

"We use OpenAI embeddings" or "we use the default Sentence-Transformers model" is a procurement
decision disguised as an architecture decision. The embedding model determines the semantic
space in which retrieval happens — its domain coverage, its handling of out-of-vocabulary terms,
its token budget, its latency, and its cost all directly determine recall@k and precision@k.
A general-purpose model trained on web text will perform poorly on medical, legal, financial,
or code corpora unless it has been domain-adapted. There is no universally best embedding model.

The pattern failure: developers copy the embedding model from a tutorial or starter template,
deploy it to production, and only discover it underperforms when users complain — because they
never benchmarked it against their actual corpus.

## How to apply

- **Benchmark on your corpus, not on BEIR.** BEIR scores are a useful proxy for zero-shot
  general capability, but your corpus is not BEIR. Run recall@k on at least 50 representative
  query-document pairs before committing to a model.
- **Match domain, language, and modality.** Code → code-specific models; multilingual corpus
  → multilingual model (BGE-M3, multilingual-E5); medical → domain-adapted biomedical
  embeddings; general English → general-purpose models are fine.
- **Factor in operational constraints.** API-hosted models (OpenAI, Cohere, Voyage) have
  latency and cost implications; open-weight models (BGE, E5, Jina) require serving
  infrastructure. This is a real tradeoff, not a secondary concern.
- **Check the max-token limit.** OpenAI text-embedding-3-small supports 8191 tokens; BGE-large
  supports 512. If your chunks exceed the model's window, you are silently truncating context.

**Do:**

- Write an explicit model selection decision record: model name, benchmark recall@k on the
  corpus, latency, cost/1M tokens, max tokens, date evaluated.
- Re-evaluate when the corpus or query distribution changes significantly.
- Consider domain fine-tuning if a general model shows recall < 0.70 at k=20 after chunking
  is optimised.

**Don't:**

- Pick a model because it is the cheapest without measuring recall.
- Use a model with a token limit smaller than your chunk size.
- Treat the embedding model as fixed infrastructure that is never revisited.

## Edge cases / when the rule does NOT apply

- Prototype / proof-of-concept where corpus is < 1000 documents and any reasonable model
  will produce serviceable results. Even here, document the model as a variable to revisit.
- A system where the embedding model is dictated by an existing platform (e.g. a cloud AI
  service that bundles its own embeddings). In this case, document the constraint and
  benchmark the forced choice against an alternative to understand the gap.

## See also

- [`./chunk-for-the-question-not-the-document.md`](./chunk-for-the-question-not-the-document.md) — chunk size and model token limits interact.
- [`../knowledge/search-retrieval-decision-trees.md`](../knowledge/search-retrieval-decision-trees.md) — 2026 capability map of embedding models.
- [`../agents/vector-retrieval-engineer.md`](../agents/vector-retrieval-engineer.md) — embedding model selection owner.

## Provenance

BEIR benchmark (Thakur et al., 2021) established that embedding models have meaningfully
different recall across domains; subsequent work on MTEB (Muennighoff et al., 2022) extended
this across tasks. Domain-adapted fine-tuning literature (e.g. BioLinkBERT, CodeBERT,
LegalBERT) shows consistent gains on in-domain corpora. The practitioner argument against
defaults is repeated in every major RAG engineering post-mortem. [verify-at-use for current
MTEB rankings]

---

_Last reviewed: 2026-06-08 by `claude`._
