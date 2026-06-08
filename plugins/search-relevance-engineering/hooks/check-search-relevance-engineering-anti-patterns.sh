#!/usr/bin/env bash
# check-search-relevance-engineering-anti-patterns.sh — advisory PreToolUse hook for the
# search-relevance-engineering plugin. Flags mechanically-detectable search/retrieval
# anti-patterns on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice);
# set SEARCH_RE_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text / config files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.py | *.txt | *.sh | *.ts | *.js) ;;
*) exit 0 ;;
esac

findings=()

# 1. Vector-only design with no lexical/hybrid consideration noted.
# Flag files that reference only vector/embedding/ANN search and have no mention of BM25,
# lexical, keyword, or hybrid search — suggests lexical coverage was not considered.
if grep -nEi "\b(vector.only|dense.only|embedding.only|pure.vector)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(bm25|lexical|hybrid|keyword.search)\b" "$file" >/dev/null 2>&1; then
    findings+=("Vector-only design detected with no lexical/hybrid consideration noted. Most real corpora benefit from hybrid (BM25 + dense + RRF). Add a rationale if vector-only is intentional, or consider hybrid.")
  fi
fi

# 2. Chunk size hard-coded with no rationale.
# Flag lines that set a specific chunk size (common values) with no adjacent measurement reference.
if grep -nEi "(chunk.size|chunk_size|max.chunk|chunksize)\s*[=:]\s*[0-9]+" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(recall|measure|benchmark|evaluation|experiment|tested)" "$file" >/dev/null 2>&1; then
    findings+=("Chunk size appears hard-coded with no measurement rationale. Chunk size is corpus+query-specific; document why this size was chosen (e.g. 'recall@20 measured at 256 vs 512 tokens — 256 won').")
  fi
fi

# 3. Relevance/quality claim with no judgment set or metric.
# Flag phrases asserting search is "better" or "improved" without a metric reference.
if grep -nEi "(search (quality|relevance) (improved?|is (better|good|great))|relevance (improved?|is (better|good))|(better|improved) (results?|ranking|relevance))" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(ndcg|mrr|recall@|precision@|judgment.set|evaluation)" "$file" >/dev/null 2>&1; then
    findings+=("Relevance/quality claim detected with no judgment set or metric referenced. A claim of 'better search' requires a before/after nDCG@k, MRR, or recall@k comparison against a judgment set.")
  fi
fi

# 4. Reranker added with no recall/latency note.
# Flag reranker references without a recall@k or latency mention.
if grep -nEi "\b(rerank|cross.encoder|cohere.rerank|bge.reranker|reranker)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(recall@|latency|recall_at|recall at|ms\b|millisecond)" "$file" >/dev/null 2>&1; then
    findings+=("Reranker reference detected without a recall@k or latency note. A reranker requires: (1) bi-encoder recall@k sufficient (>= 0.70) — it cannot retrieve what the bi-encoder missed; (2) latency budget for cross-encoder inference.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── search-relevance-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${SEARCH_RE_STRICT:-0}" = "1" ]; then
  echo "(blocking: SEARCH_RE_STRICT=1)" >&2
  exit 2
fi
exit 0
