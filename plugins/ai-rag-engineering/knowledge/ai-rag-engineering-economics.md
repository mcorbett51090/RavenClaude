# AI / RAG Engineering Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/ai_rag_engineering_calc.py`](../scripts/ai_rag_engineering_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Recall@k caps everything (§3 #1)

```
recall_at_k    = relevant_retrieved_in_topk / total_relevant
precision_at_k = relevant_retrieved_in_topk / k
```

If recall@k is low, the answering passage never reaches the model — and no prompt change or bigger model recovers it. Measure recall before touching generation.

## 2. NDCG / DCG when relevance is graded

```
DCG@k  = sum( rel_i / log2(i + 1) for i in 1..k )   # i is the rank, starting at 1
IDCG@k = DCG of the ideal (relevance-sorted) ordering
NDCG@k = DCG@k / IDCG@k
```

NDCG rewards putting the most-relevant passages highest — relevant @ rank 1 is worth more than relevant @ rank 5.

## 3. Token cost is mostly context (§3 #5)

```
cost_per_request = (input_tokens + output_tokens) / 1000 * price_per_1k
monthly          = cost_per_request * requests_per_month
```

For RAG, retrieved context usually dominates `input_tokens`; stuffing more chunks raises cost AND can degrade quality (lost-in-the-middle). Fewest high-precision chunks wins.

## 4. The context budget is a hard constraint (§3 #5)

```
prompt_tokens = chunk_size * top_k + prompt_overhead
fits          = prompt_tokens + max_output_tokens <= context_window
```

Chunk size × top-k must leave room for the prompt scaffolding AND the output; a chunking choice that doesn't fit the window is a design error, not a tuning detail.
