# Search & Relevance Engineering Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Did the relevance change help?

```mermaid
flowchart TD
    A[Proposed relevance change] --> B{Is there a graded<br/>judgment list?}
    B -- "No judgment list" --> B1[Build judgment list + offline<br/>harness FIRST, §3 #3]
    B -- "Have judgment list" --> C{Offline NDCG/MRR<br/>improved vs baseline?}
    C -- "No / regressed" --> C1[Don't ship; the change<br/>didn't earn it, §3 #1]
    C -- "Improved offline" --> D{Confirmed with an<br/>online A/B?}
    D -- "No A/B yet" --> D1[Run A/B on CTR/conversion;<br/>offline gains may not transfer, §3 #6]
    D -- "A/B confirms" --> D2[Ship with offline + online<br/>delta, §3 #1 #6]
    D -- "A/B flat/negative" --> D3[Offline metric diverged from<br/>intent; revisit judgments, §3 #6]
    B1 --> C
    D2 --> E[Owner · date · offline + online delta]
    D3 --> E
```

## Tree 2 — A query returns bad/no results

```mermaid
flowchart TD
    A[Bad or no results] --> B{Is the right doc in<br/>the candidate set?}
    B -- "Not retrieved (recall)" --> C{Why didn't it match?}
    C -- "Tokenization/stemming" --> C1[Analyzer bug: fix analysis,<br/>not the boost, §3 #2]
    C -- "Wrong field type/mapping" --> C2[Mapping bug: correct field<br/>type/analyzer, §3 #2]
    C -- "Vocabulary mismatch" --> C3[Query expansion / synonyms<br/>for recall, §3 #5]
    B -- "Retrieved but ranked low" --> D{Measured on the<br/>judgment list?}
    D -- "Not measured" --> D1[Measure NDCG first, then tune<br/>ranking, §3 #1]
    D -- "Measured low precision" --> D2[Ranking/boost tuning on a<br/>recall-secured set, §3 #5]
    C1 --> E[Re-measure NDCG · owner · date, §3 #1]
    C2 --> E
    C3 --> E
    D2 --> E
```

## Tree 3 — Search is too slow

```mermaid
flowchart TD
    A[Latency too high] --> B{Is there a p95<br/>latency budget?}
    B -- "No budget" --> B1[Set a p95 budget first;<br/>relevance lives inside it, §3 #4]
    B -- "Budget set" --> C{Which stage is<br/>slow?}
    C -- "Match/fetch" --> C1[Index sizing / sharding;<br/>route capacity, §3 #4 #7]
    C -- "Rescore/expansion" --> C2[Relevance work over budget:<br/>trim candidate set / rescore depth, §3 #4]
    C -- "Mapping/analysis cost" --> C3[Analyzer/mapping efficiency,<br/>route to indexing, §3 #2]
    C1 --> D{Within budget after<br/>the fix?}
    C2 --> D
    C3 --> D
    D -- "Yes" --> D1[Tune relevance within the<br/>headroom, §3 #4 #5]
    D -- "No" --> D2[Trade relevance depth for<br/>latency explicitly, §3 #4]
    B1 --> C
    D1 --> E[Owner · date · p95 + relevance held]
    D2 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
