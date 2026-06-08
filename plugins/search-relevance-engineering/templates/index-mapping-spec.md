# Index Mapping Spec — `<index name>`

> Canonical mapping and settings spec for a search index. Produced by `search-architect` /
> `design-search-architecture` command. Keep in sync with the live index mapping.

- **Store:** `<Elasticsearch 8.x / OpenSearch 2.x / pgvector / …>`
- **Retrieval mode:** `<lexical-only / vector-only / hybrid>`
- **Date:** `<date>` · **Author:** `<name>`

---

## Index settings

```json
{
  "settings": {
    "number_of_shards": "<N — target ~20–50 GB per shard>",
    "number_of_replicas": "<1 for search; 0 for indexing-heavy>",
    "refresh_interval": "<1s for near-real-time; 30s for batch>",
    "analysis": {
      "analyzer": {
        "default_analyzer": {
          "type": "custom",
          "tokenizer": "<standard | whitespace | language-specific>",
          "filter": ["lowercase", "<stemmer | kstem | snowball>", "<stop>", "<synonym_graph — query-time only>"]
        }
      }
    },
    "similarity": {
      "bm25_tuned": {
        "type": "BM25",
        "k1": "<1.2 default — sweep 0.5–2.0>",
        "b": "<0.75 default — sweep 0.0–1.0>"
      }
    }
  }
}
```

_Replace bracketed values. BM25 k1 and b are starting-point defaults; run the parameter sweep_
_from the `relevance-tuning` skill before committing these values to production._

---

## Mappings

```json
{
  "mappings": {
    "properties": {

      "title": {
        "type": "text",
        "analyzer": "default_analyzer",
        "similarity": "bm25_tuned",
        "boost": "<3.0 — adjust via field-boost sweep>",
        "fields": {
          "keyword": { "type": "keyword", "ignore_above": 256 }
        }
      },

      "body": {
        "type": "text",
        "analyzer": "default_analyzer",
        "similarity": "bm25_tuned"
      },

      "tags": {
        "type": "text",
        "analyzer": "default_analyzer",
        "similarity": "bm25_tuned",
        "boost": "<2.0>",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },

      "embedding": {
        "type": "dense_vector",
        "dims": "<384 | 768 | 1536 — match embedding model output>",
        "index": true,
        "similarity": "<cosine | dot_product | l2_norm>",
        "index_options": {
          "type": "hnsw",
          "m": "<16 default — increase for higher recall at memory cost>",
          "ef_construction": "<100 default — increase for higher build-time recall>"
        }
      },

      "doc_id": { "type": "keyword" },
      "url": { "type": "keyword" },
      "published_at": { "type": "date" },
      "language": { "type": "keyword" }
    }
  }
}
```

_Remove `embedding` block if retrieval mode is lexical-only._
_Remove text fields' `similarity` override if using the index-level default._

---

## Query path sketch

### Hybrid query (BM25 + kNN + RRF)

```json
{
  "sub_searches": [
    {
      "query": {
        "multi_match": {
          "query": "<user query>",
          "fields": ["title^3", "body^1", "tags^2"],
          "type": "best_fields",
          "tie_breaker": 0.3
        }
      }
    },
    {
      "knn": {
        "field": "embedding",
        "query_vector": "<embedded user query — float32 array>",
        "k": "<100 — recall budget; 2× final result count minimum>",
        "num_candidates": "<200 — ef_search proxy>"
      }
    }
  ],
  "rank": {
    "rrf": {
      "window_size": 100,
      "rank_constant": 60
    }
  },
  "size": "<10 — final result count>"
}
```

_For lexical-only: use only the `multi_match` block, no `knn`, no `rrf`._
_For vector-only: use only the `knn` block._

---

## Freshness / indexing topology

| SLA | Pattern | Notes |
|---|---|---|
| `<sub-5s>` | Event-driven CDC (Debezium / Kafka Connect) | Requires `refresh_interval: 1s` |
| `<30s–5m>` | Micro-batch via streaming job | Balance throughput vs freshness |
| `<daily>` | Batch window | Acceptable for archival / catalogue corpora |

---

## Open questions / decisions pending

- [ ] BM25 k1/b parameters — pending parameter sweep
- [ ] Embedding model — pending corpus benchmark (see `vector-retrieval-engineer`)
- [ ] Shard count — pending document-count finalisation
- [ ] `<any other open decision>`

---

_Last updated: `<date>` by `<author>`._
