# DevRel engagement decision trees

Traverse these top-to-bottom before picking a move. They keep this team from
papering over product flaws with content, from drifting into demand gen, and from
choosing a content format by habit.

## 1. Advocate vs. docs vs. community — who owns this?

```mermaid
flowchart TD
    A[A developer-facing need lands] --> B{Is it reference material:<br/>API/SDK reference, config tables,<br/>endpoint docs?}
    B -- Yes --> DOCS[Route to technical-writing-docs]
    B -- No --> C{Is it a developer getting stuck<br/>or asking in public channels?}
    C -- Yes --> COMM[developer-community-manager —<br/>answer, then capture the<br/>canonical answer]
    C -- No --> D{Is it about the activation funnel,<br/>a DX audit, or product feedback?}
    D -- Yes --> ADV[developer-advocate]
    D -- No --> E{Is it a runnable artifact:<br/>getting-started, sample app, quickstart?}
    E -- Yes --> CONTENT[devrel-content-engineer]
    E -- No --> F{Is it really demand gen<br/>or brand?}
    F -- Yes --> MKT[Route to marketing-operations]
    F -- No --> ADV
```

## 2. Fix the product or document around it?

```mermaid
flowchart TD
    A[A getting-started step is painful] --> B{Is the step painful because the<br/>PRODUCT is confusing/broken<br/>not because it's undocumented?}
    B -- Yes --> C{Is the fix small/owned<br/>e.g. a default, an error message?}
    C -- Yes --> FIX[File a product-feedback ticket FIRST<br/>route to product-management;<br/>document only as a stopgap]
    C -- No --> FIXBIG[File the brief with frequency+severity<br/>evidence; add a clearly-marked<br/>workaround until it's fixed]
    B -- No --> D{Is the path sound but<br/>hard to discover?}
    D -- Yes --> DOC[Now a content task —<br/>write the getting-started / sample]
    D -- No --> FIX
```

**Rule:** DevRel's highest-leverage output is the friction it *removes*. A longer
tutorial that papers over a product flaw is technical debt with a smile. File the
bug first; document as a stopgap, clearly marked.

## 3. Content-format choice

```mermaid
flowchart TD
    A[A content need + an activation goal] --> B{Goal: get a brand-new dev<br/>to first success?}
    B -- Yes --> GS[Getting-started / quickstart —<br/>optimize time-to-first-success]
    B -- No --> C{Goal: show the real<br/>value path end-to-end?}
    C -- Yes --> SAMPLE[Sample app —<br/>production-grade, shows the hard parts]
    C -- No --> D{Goal: explain a concept<br/>or pattern?}
    D -- Yes --> GUIDE[Conceptual guide / tutorial]
    D -- No --> E{Goal: reach/awareness<br/>among developers?}
    E -- Yes --> TALK[Talk / post / video —<br/>engineer-to-engineer, not marketing]
    E -- No --> GS
```

**Rule:** the format follows the activation goal, not the channel that's trendy.
Optimize the getting-started path before any reach play — reach that lands a dev on
a broken first-run wastes the reach.
