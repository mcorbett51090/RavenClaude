# AI / RAG Engineering Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Build/trust a RAG change

```mermaid
flowchart TD
    A[Want to change the RAG system] --> B{Is there an<br/>offline eval set?}
    B -- "No eval" --> B1[Build judgment set + harness FIRST;<br/>no eval, no ship, §3 #3]
    B -- "Eval exists" --> C{Recorded a<br/>baseline?}
    C -- "No baseline" --> C1[Record recall@k / faithfulness<br/>baseline before changing, §3 #3]
    C -- "Baseline set" --> D{Change improves<br/>the eval?}
    D -- "Retrieval metric up" --> D1[Ship with the before/after<br/>delta, §3 #1 #3]
    D -- "Generation up, retrieval flat" --> D2[Check faithfulness + citations<br/>before trusting it, §3 #7]
    D -- "No improvement / regress" --> D3[Don't ship; the change<br/>didn't earn it, §3 #3]
    B1 --> C1
    D1 --> E[Owner · date · eval delta]
    D2 --> E
```

## Tree 2 — RAG gives wrong answers

```mermaid
flowchart TD
    A[Wrong answers] --> B{Recall@k:<br/>is the passage retrieved?}
    B -- "Low recall" --> C{Why is retrieval<br/>missing it?}
    C -- "Answer split across chunks" --> C1[Chunking bug: structure-aware<br/>chunking, route to ingestion, §3 #2]
    C -- "Keyword/ID query" --> C2[Add hybrid (BM25 + vector),<br/>§3 #6]
    C -- "Semantic gap" --> C3[Embedding choice; benchmark<br/>on the corpus, §3 #4]
    B -- "High recall, still wrong" --> D{Faithful to the<br/>retrieved context?}
    D -- "Not grounded" --> D1[Grounding/guardrail problem:<br/>citations + refuse-on-empty, §3 #7]
    D -- "Too much context" --> D2[Lost-in-the-middle: fewer,<br/>higher-precision chunks, §3 #5]
    C1 --> E[Re-measure eval · owner · date, §3 #3]
    C2 --> E
    C3 --> E
    D1 --> E
    D2 --> E
```

## Tree 3 — Quality vs cost tradeoff

```mermaid
flowchart TD
    A[Cost or latency too high] --> B{Sending more context<br/>than needed?}
    B -- "Stuffing many chunks" --> B1[Cut to fewest high-precision;<br/>cheaper AND often better, §3 #5]
    B -- "Lean context" --> C{Model choice<br/>justified by eval?}
    C -- "Picked by leaderboard" --> C1[Benchmark candidates on YOUR<br/>eval at cost+latency, §3 #4]
    C -- "Eval-justified" --> D{Repeated/cacheable<br/>prompts?}
    D -- "Yes" --> D1[Prompt/embedding caching cuts<br/>cost without quality loss]
    D -- "No" --> D2[At the cost/quality frontier;<br/>verify prices live, §3 #8]
    B1 --> E[Owner · date · cost delta + eval held]
    C1 --> E
    D1 --> E
    D2 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
