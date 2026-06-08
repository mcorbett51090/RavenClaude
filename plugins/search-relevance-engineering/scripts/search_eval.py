#!/usr/bin/env python3
"""
search_eval.py — Retrieval evaluation metrics (stdlib-only).

Computes nDCG@k, MRR, recall@k, and precision@k from a graded judgment set
and a ranked list of retrieved document IDs per query.

Usage
-----
As a library:
    from search_eval import ndcg_at_k, mrr, recall_at_k, precision_at_k

As a script (self-test + example):
    python3 search_eval.py

Input format
------------
judgments : list[dict]
    [{"query_id": str, "doc_id": str, "relevance": int (0–3)}, ...]

retrieved : dict[str, list[str]]
    {query_id: [doc_id_rank1, doc_id_rank2, ...]}  — ordered by rank, descending score

Relevance grades (NIST 4-point scale):
    0 = not relevant
    1 = marginally relevant
    2 = relevant
    3 = highly relevant
"""

import math
from typing import Dict, List


# ---------------------------------------------------------------------------
# Core metric functions
# ---------------------------------------------------------------------------


def _ideal_dcg(relevances: List[int], k: int) -> float:
    """Compute the Ideal DCG@k for a sorted (descending) list of relevance grades."""
    sorted_rels = sorted(relevances, reverse=True)
    idcg = 0.0
    for i, rel in enumerate(sorted_rels[:k]):
        idcg += (2**rel - 1) / math.log2(i + 2)  # i+2 because log2(1) = 0
    return idcg


def ndcg_at_k(
    judgments: List[Dict],
    retrieved: Dict[str, List[str]],
    k: int = 10,
) -> float:
    """
    Normalized Discounted Cumulative Gain at k, averaged over all queries.

    Parameters
    ----------
    judgments : list of {query_id, doc_id, relevance}
    retrieved : {query_id: [doc_id, ...]} ranked lists
    k         : cutoff rank

    Returns
    -------
    Mean nDCG@k over all queries that appear in retrieved.
    """
    # Build a lookup: query_id -> {doc_id -> relevance}
    qrels: Dict[str, Dict[str, int]] = {}
    for j in judgments:
        qid = j["query_id"]
        if qid not in qrels:
            qrels[qid] = {}
        qrels[qid][j["doc_id"]] = j["relevance"]

    scores = []
    for qid, ranked_docs in retrieved.items():
        rels_in_pool = qrels.get(qid, {})
        if not rels_in_pool:
            continue  # skip queries with no judgments

        # Compute DCG@k for the retrieved list
        dcg = 0.0
        for i, doc_id in enumerate(ranked_docs[:k]):
            rel = rels_in_pool.get(doc_id, 0)
            dcg += (2**rel - 1) / math.log2(i + 2)

        # Compute IDCG@k
        idcg = _ideal_dcg(list(rels_in_pool.values()), k)

        if idcg == 0.0:
            # All documents in the pool have relevance 0 — nDCG is undefined; treat as 0
            scores.append(0.0)
        else:
            scores.append(dcg / idcg)

    return sum(scores) / len(scores) if scores else 0.0


def mrr(
    judgments: List[Dict],
    retrieved: Dict[str, List[str]],
    relevance_threshold: int = 1,
) -> float:
    """
    Mean Reciprocal Rank: 1/rank of the first relevant result, averaged over queries.

    Parameters
    ----------
    judgments           : list of {query_id, doc_id, relevance}
    retrieved           : {query_id: [doc_id, ...]} ranked lists
    relevance_threshold : minimum relevance grade to count as 'relevant' (default 1)

    Returns
    -------
    MRR over all queries with at least one judged document.
    """
    qrels: Dict[str, Dict[str, int]] = {}
    for j in judgments:
        qid = j["query_id"]
        if qid not in qrels:
            qrels[qid] = {}
        qrels[qid][j["doc_id"]] = j["relevance"]

    scores = []
    for qid, ranked_docs in retrieved.items():
        rels_in_pool = qrels.get(qid, {})
        if not rels_in_pool:
            continue

        rr = 0.0
        for i, doc_id in enumerate(ranked_docs):
            if rels_in_pool.get(doc_id, 0) >= relevance_threshold:
                rr = 1.0 / (i + 1)
                break
        scores.append(rr)

    return sum(scores) / len(scores) if scores else 0.0


def recall_at_k(
    judgments: List[Dict],
    retrieved: Dict[str, List[str]],
    k: int = 100,
    relevance_threshold: int = 1,
) -> float:
    """
    Recall@k: fraction of relevant documents found in the top-k retrieved results,
    averaged over queries.

    Primary RAG retrieval metric — "was the relevant chunk in the top-k context?"

    Parameters
    ----------
    judgments           : list of {query_id, doc_id, relevance}
    retrieved           : {query_id: [doc_id, ...]} ranked lists
    k                   : cutoff rank (set to context-window budget for RAG)
    relevance_threshold : minimum relevance to count as relevant (default 1)

    Returns
    -------
    Mean recall@k over all queries with at least one relevant judged document.
    """
    qrels: Dict[str, Dict[str, int]] = {}
    for j in judgments:
        qid = j["query_id"]
        if qid not in qrels:
            qrels[qid] = {}
        qrels[qid][j["doc_id"]] = j["relevance"]

    scores = []
    for qid, ranked_docs in retrieved.items():
        rels_in_pool = qrels.get(qid, {})
        relevant_docs = {
            doc_id
            for doc_id, rel in rels_in_pool.items()
            if rel >= relevance_threshold
        }
        if not relevant_docs:
            continue

        retrieved_top_k = set(ranked_docs[:k])
        found = relevant_docs & retrieved_top_k
        scores.append(len(found) / len(relevant_docs))

    return sum(scores) / len(scores) if scores else 0.0


def precision_at_k(
    judgments: List[Dict],
    retrieved: Dict[str, List[str]],
    k: int = 10,
    relevance_threshold: int = 1,
) -> float:
    """
    Precision@k: fraction of the top-k retrieved results that are relevant,
    averaged over queries.

    Parameters
    ----------
    judgments           : list of {query_id, doc_id, relevance}
    retrieved           : {query_id: [doc_id, ...]} ranked lists
    k                   : cutoff rank
    relevance_threshold : minimum relevance to count as relevant (default 1)

    Returns
    -------
    Mean precision@k over all queries with at least one judged document.
    """
    qrels: Dict[str, Dict[str, int]] = {}
    for j in judgments:
        qid = j["query_id"]
        if qid not in qrels:
            qrels[qid] = {}
        qrels[qid][j["doc_id"]] = j["relevance"]

    scores = []
    for qid, ranked_docs in retrieved.items():
        rels_in_pool = qrels.get(qid, {})
        if not rels_in_pool:
            continue

        top_k = ranked_docs[:k]
        relevant_in_top_k = sum(
            1 for doc_id in top_k if rels_in_pool.get(doc_id, 0) >= relevance_threshold
        )
        scores.append(relevant_in_top_k / min(k, len(top_k)))

    return sum(scores) / len(scores) if scores else 0.0


def evaluate(
    judgments: List[Dict],
    retrieved: Dict[str, List[str]],
    k_ndcg: int = 10,
    k_recall: int = 100,
    k_precision: int = 10,
) -> Dict[str, float]:
    """
    Compute all four metrics in one call.

    Returns
    -------
    dict with keys: ndcg@k, mrr, recall@k, precision@k
    """
    return {
        f"ndcg@{k_ndcg}": ndcg_at_k(judgments, retrieved, k=k_ndcg),
        "mrr": mrr(judgments, retrieved),
        f"recall@{k_recall}": recall_at_k(judgments, retrieved, k=k_recall),
        f"precision@{k_precision}": precision_at_k(judgments, retrieved, k=k_precision),
    }


# ---------------------------------------------------------------------------
# Self-test  (python3 search_eval.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== search_eval.py self-test ===\n")

    # -----------------------------------------------------------------------
    # Toy judgment set: 3 queries, graded 0–3
    # -----------------------------------------------------------------------
    judgments = [
        # query q1: d1=highly relevant, d2=relevant, d3=marginally, d4=not relevant
        {"query_id": "q1", "doc_id": "d1", "relevance": 3},
        {"query_id": "q1", "doc_id": "d2", "relevance": 2},
        {"query_id": "q1", "doc_id": "d3", "relevance": 1},
        {"query_id": "q1", "doc_id": "d4", "relevance": 0},
        # query q2: d5=relevant, d6=not relevant
        {"query_id": "q2", "doc_id": "d5", "relevance": 2},
        {"query_id": "q2", "doc_id": "d6", "relevance": 0},
        # query q3: d7=highly relevant, d8=marginally relevant
        {"query_id": "q3", "doc_id": "d7", "relevance": 3},
        {"query_id": "q3", "doc_id": "d8", "relevance": 1},
    ]

    # -----------------------------------------------------------------------
    # Scenario A: perfect retrieval (ideal ranking)
    # -----------------------------------------------------------------------
    retrieved_perfect = {
        "q1": ["d1", "d2", "d3", "d4"],  # perfect order
        "q2": ["d5", "d6"],  # relevant first
        "q3": ["d7", "d8"],  # perfect order
    }
    metrics_perfect = evaluate(judgments, retrieved_perfect)
    print("Scenario A — perfect retrieval (expected nDCG@10=1.0, MRR=1.0):")
    for name, value in metrics_perfect.items():
        print(f"  {name}: {value:.4f}")
    assert abs(metrics_perfect["ndcg@10"] - 1.0) < 1e-6, "nDCG@10 should be 1.0 for perfect ranking"
    assert abs(metrics_perfect["mrr"] - 1.0) < 1e-6, "MRR should be 1.0 when top result is always relevant"
    assert abs(metrics_perfect["recall@100"] - 1.0) < 1e-6, "recall@100 should be 1.0 for perfect retrieval"
    # q1: 3/4 relevant in top-4; q2: 1/2 relevant in top-2; q3: 2/2 relevant in top-2
    # mean precision@10 = (3/4 + 1/2 + 1) / 3 = (0.75 + 0.5 + 1.0) / 3 = 0.75
    assert abs(metrics_perfect["precision@10"] - 0.75) < 0.01, "precision@10 should be 0.75 for this fixture"
    print("  PASS\n")

    # -----------------------------------------------------------------------
    # Scenario B: worst retrieval (reversed ranking)
    # -----------------------------------------------------------------------
    retrieved_worst = {
        "q1": ["d4", "d3", "d2", "d1"],  # worst order — not relevant first
        "q2": ["d6", "d5"],  # not relevant first
        "q3": ["d8", "d7"],  # marginally relevant first
    }
    metrics_worst = evaluate(judgments, retrieved_worst)
    print("Scenario B — reversed retrieval (expected nDCG@10 < 1.0, MRR < 1.0):")
    for name, value in metrics_worst.items():
        print(f"  {name}: {value:.4f}")
    assert metrics_worst["ndcg@10"] < 1.0, "nDCG@10 should be < 1.0 for reversed ranking"
    assert metrics_worst["mrr"] < 1.0, "MRR should be < 1.0 when first result is never the best"
    print("  PASS\n")

    # -----------------------------------------------------------------------
    # Scenario C: partial retrieval — relevant docs not in candidate set (RAG miss)
    # -----------------------------------------------------------------------
    retrieved_partial = {
        "q1": ["d4", "d99"],  # d1 (best) not retrieved
        "q2": ["d5"],  # correct
        "q3": ["d99", "d100"],  # d7 (best) not retrieved
    }
    recall_partial = recall_at_k(judgments, retrieved_partial, k=10)
    print(f"Scenario C — partial retrieval (q1 and q3 miss their best doc):")
    print(f"  recall@10: {recall_partial:.4f}  (expected < 1.0)")
    assert recall_partial < 1.0, "recall@10 should be < 1.0 when relevant docs are missing"
    print("  PASS\n")

    # -----------------------------------------------------------------------
    # Scenario D: MRR with binary relevance threshold
    # -----------------------------------------------------------------------
    retrieved_mrr = {
        "q1": ["d4", "d4", "d3", "d1"],  # first relevant at position 3
        "q2": ["d5"],  # first relevant at position 1
    }
    mrr_score = mrr(judgments, retrieved_mrr)
    print(f"Scenario D — MRR with mixed first-hit positions:")
    print(f"  MRR: {mrr_score:.4f}  (q1 hits at rank 3 → 1/3; q2 hits at rank 1 → 1/1; mean = 2/3)")
    # q1: first relevant (rel≥1) is d3 at position 3 → 1/3
    # q2: d5 at position 1 → 1/1
    # mean = (1/3 + 1) / 2 = 2/3
    expected_mrr = (1 / 3 + 1.0) / 2
    assert abs(mrr_score - expected_mrr) < 1e-6, f"MRR expected {expected_mrr:.4f}, got {mrr_score:.4f}"
    print("  PASS\n")

    # -----------------------------------------------------------------------
    # Demonstrate evaluate() convenience function
    # -----------------------------------------------------------------------
    print("Full evaluate() output for perfect retrieval:")
    all_metrics = evaluate(judgments, retrieved_perfect, k_ndcg=5, k_recall=10, k_precision=5)
    for name, value in all_metrics.items():
        print(f"  {name}: {value:.4f}")

    print("\nAll self-tests passed.")
