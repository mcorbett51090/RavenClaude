# Memory Engineering Decision Trees

**Last verified:** 2026-08-06 · the trees encode this plugin's six-decision spine; the evidence behind each leaf lives in the companion knowledge files.

> **Re-verify before quoting.** Anthropic beta→GA transitions invalidate this file independently of its age; the 90-day sweep surfaces it on a date, it does not check it.

> Traverse each tree top-to-bottom against the situation you actually have — do not keyword-match a symptom to a leaf. When two branches could apply, take the one with the smaller blast radius and escalate only when it demonstrably fails. The first node of trees 1 and 3 is a **stop**, on purpose.

## Tree 1 — Do you need memory at all, and which paradigm?

```mermaid
flowchart TD
    A[Want durable memory] --> B{Does a no-memory<br/>baseline actually lose?}
    B -- "Never measured" --> B1[STOP. Build the golden set first;<br/>measure the stateless baseline]
    B -- "No-memory is fine" --> B2[Do not build memory.<br/>The cheapest store is none]
    B -- "No-memory loses" --> C{Does flat retrieval<br/>BM25 or embedRAG lose?}
    C -- "Never measured" --> C1[STOP. Measure it.<br/>Lexical retrieval scored highest<br/>accuracy AND lowest cost in the suite]
    C -- "Flat retrieval wins" --> C2[Ship Paradigm II.<br/>Cheap build, amortizes almost at once]
    C -- "Flat retrieval loses" --> D{Do queries need<br/>linked entities or<br/>contradiction handling?}
    D -- "Linked entities" --> D1[Paradigm III.a structure-augmented.<br/>Large offline indexing batch]
    D -- "Evolving facts about a user" --> D2[Paradigm III.b consolidating store.<br/>LLM call on every write path]
    D -- "Model must decide<br/>when to write" --> D3[Paradigm IV agentic.<br/>Super-linear cost slope; justify it]
    C2 --> E{Does it amortize<br/>against a NAMED baseline?}
    D1 --> E
    D2 --> E
    D3 --> E
    E -- "No break-even" --> E1[Only accuracy can justify it now.<br/>Compare cost per correct answer]
    E -- "Break-even in range" --> F[Record paradigm · baseline · n*<br/>in the design record]
    B1 --> B
    C1 --> C
```

**Why the two stops.** A memory project that never measured its baselines has no way to know whether it improved anything, and the measured result that should worry you is that plain lexical retrieval was both the most accurate and the cheapest system in the benchmark suite. The evidence and its conditions: [paradigms](memory-engineering-paradigms.md). The break-even arithmetic: [economics](memory-engineering-economics.md).

## Tree 2 — Which surface owns this write?

```mermaid
flowchart TD
    A[A fact must survive the session] --> B{Who must hold<br/>the bytes?}
    B -- "We must, for residency<br/>or compliance" --> C{Who executes<br/>the write?}
    B -- "Vendor may hold them" --> G{Needs audit trail,<br/>versioning, redaction?}
    C -- "Our code, on our storage" --> C1[Client-side memory tool.<br/>You own path traversal,<br/>size caps, expiry, redaction]
    C -- "Nobody: it is repo convention" --> C2[Instruction file in the repo.<br/>Context, not enforcement]
    G -- "Yes" --> G1[Server-side memory store.<br/>Immutable versions + redact;<br/>read_only for reference material]
    G -- "No, it is per-developer" --> G2[Local auto memory.<br/>Machine-local, shared per git repo]
    A --> H{Is it durable at all,<br/>or just context pressure?}
    H -- "Tool results are<br/>bloating the prompt" --> H1[Context editing.<br/>Breaks the prompt cache<br/>at the clearing point]
    H -- "The whole conversation<br/>is too long" --> H2[Compaction.<br/>Costs an extra sampling pass]
    H -- "Duplicates and stale<br/>entries are piling up" --> H3[Offline consolidation job.<br/>Its own header, its own bill]
    C1 --> Z[Record surface · holder ·<br/>executor · status · date]
    C2 --> Z
    G1 --> Z
    G2 --> Z
    H1 --> Z
    H2 --> Z
    H3 --> Z
```

**The two questions that do all the work** are *who holds the bytes* and *who executes the write* — they set data residency, who owns the security controls, and who can be compelled to produce the data. Exact headers, statuses and limits, dated: [memory surfaces](memory-surfaces-2026.md).

**Note the split at the top.** The right-hand branch is not memory at all — context editing, compaction and consolidation manage *pressure*, and nothing there survives on its own. Memory is what must survive both.

## Tree 3 — The entry is wrong. Which failure mode, and what fixes it?

```mermaid
flowchart TD
    A[A stored entry produced a bad answer] --> B{Was the entry<br/>ever true?}
    B -- "Never true" --> C{Could untrusted input<br/>reach this write path?}
    B -- "True when written" --> D{Does a newer,<br/>conflicting entry exist?}
    C -- "Yes" --> C1[Treat as POISONING.<br/>Patching the prompt fixes nothing;<br/>go to the store]
    C -- "No, our code wrote it" --> C2[Extraction defect.<br/>Fix the write-path logic,<br/>then re-run the golden set]
    C1 --> C3{Is there an audit trail?}
    C3 -- "No" --> C4[You cannot scope the blast<br/>radius. Add versioning before<br/>anything else]
    C3 -- "Yes" --> C5[Scope by session · roll back ·<br/>make reference material read_only]
    D -- "Yes, both present" --> D1[CONTRADICTION.<br/>Decide where resolution runs:<br/>write path, offline, or read time]
    D -- "No, it just aged" --> D2[STALENESS.<br/>No TTL, no cap, no decay:<br/>nothing forgets by default]
    A --> E{Was it supposed to<br/>be deleted?}
    E -- "Yes, and it answered anyway" --> E1[ERASURE RESIDUE.<br/>Check vector rows, version history,<br/>derived summaries, backups]
    E1 --> E2{Redaction returned success?}
    E2 -- "Yes but data persists" --> E3[The current head cannot be<br/>redacted. Write a new version<br/>or delete first, THEN redact]
    E2 -- "No redaction path exists" --> E4[Erasure is unimplementable here.<br/>Escalate before promising it]
    C5 --> Z[Add the case to the golden set.<br/>An untested fix is a hope]
    C2 --> Z
    D1 --> Z
    D2 --> Z
    E3 --> Z
    E4 --> Z
```

**The distinction that matters most** is the first node. A never-true entry that arrived from untrusted input is a security incident whose defining property is persistence — it keeps acting after the session that planted it ends, and fixing the prompt does not fix the agent. A once-true entry that aged is a retention-policy defect. They look identical in the transcript and have nothing else in common. The evidence, controls and erasure residue: [memory security and privacy](memory-security-and-privacy.md).

## How to read these

- **Every leaf ends in a written record**, not a decision made in chat: paradigm, surface, who holds the bytes, who executes the write, the retention and erasure story, and the break-even against a named baseline.
- **A stop node is not an obstacle.** Trees 1 and 3 open with one because the two most expensive memory mistakes are building a store that never had to exist and patching a prompt when the store was the problem.
- **Smaller blast radius first.** Read-only before read-write; flat retrieval before an agentic write loop; a cap before a consolidation job.
- **Nothing here is enforcement.** These trees, and the files behind them, are context. To *block* an action, use a hook or a permission deny.
