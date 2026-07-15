# Prompt-engineering decision trees

Four Mermaid decision trees the agents traverse. Each ends at a leaf you can act
on; **record the path you took and the runner-up** when you use one. These encode
*durable* craft — the tradeoffs move slowly. Volatile facts (which model supports
which structured-output mode, current injection techniques) live in
[`prompt-engineering-2026-reference.md`](prompt-engineering-2026-reference.md),
retrieval-dated.

---

## §1 — Prompting-pattern selection

Pick the *cheapest* pattern that hits the reliability bar. Every step up buys
reliability with tokens and/or latency.

```mermaid
flowchart TD
    A[Task] --> B{Does a clear instruction alone<br/>already pass on the hard cases?}
    B -- Yes --> Z0[Zero-shot instruction<br/>Stop. Don't add tokens you don't need.]
    B -- No --> C{Is the failure about FORMAT/STYLE<br/>the model can't infer from words?}
    C -- Yes --> D[Few-shot: 2-5 examples of the HARD cases,<br/>formatted exactly like the target output]
    C -- No --> E{Does the task need multi-step<br/>REASONING to get right?}
    E -- Yes --> F{Is it ONE reasoning chain,<br/>or genuinely SEPARATE sub-tasks?}
    F -- One chain --> G[Chain-of-thought:<br/>ask for reasoning before the answer]
    F -- Separate sub-tasks --> H[Decomposition / prompt-chaining:<br/>one prompt per sub-task, wire the outputs]
    E -- No --> I{Is output quality sensitive to<br/>PERSONA / domain framing?}
    I -- Yes --> J[Role framing: set the expert role +<br/>audience, then the task]
    I -- No --> K{High-stakes answer where a wrong<br/>single sample is costly?}
    K -- Yes --> L[Self-consistency: sample N,<br/>take the majority/best — costs Nx tokens]
    K -- No --> D
    G --> M{Still failing after CoT?}
    M -- Yes --> H
```

Cautions: **few-shot** examples must cover the *hard* cases (easy examples teach
nothing and cost tokens); **CoT** trades latency/tokens for accuracy — skip it on
tasks that don't reason; **decomposition** is the answer when one prompt is doing
three jobs; **self-consistency** is expensive — reserve it for high-stakes single
answers.

---

## §2 — Structured-output method selection

Prefer the strongest mechanism the target model supports. Words asking for JSON
are a wish; an enforced mode is a contract.

```mermaid
flowchart TD
    A[Need machine-parseable output] --> B{Does the model expose native<br/>structured / JSON-schema mode?}
    B -- Yes --> C[Use native structured output:<br/>pass the schema, get validated JSON]
    B -- No --> D{Does the model support<br/>tool / function calling?}
    D -- Yes --> E[Define the output AS a tool schema;<br/>force the tool call]
    D -- No --> F{Can you run a constrained-decoding /<br/>grammar layer (e.g. GBNF)?}
    F -- Yes --> G[Constrain decoding to the grammar]
    F -- No --> H[Last resort: prose + robust parser<br/>with delimiters]
    C --> V[ALWAYS: parse + validate + repair/retry path]
    E --> V
    G --> V
    H --> V
    V --> W{Validation fails at runtime?}
    W -- Yes --> X[Repair pass: re-prompt with the<br/>validation error, bounded retries, then fail closed]
```

Rule: **never** skip the parse-and-validate step, even with native modes — a valid
JSON string can still violate business rules. Always define what "fail closed"
means for the caller.

---

## §3 — Context-window inclusion

The window is a budget, not a scratchpad. Decide what earns its tokens.

```mermaid
flowchart TD
    A[Candidate content for the window] --> B{Is it needed for EVERY call?}
    B -- Yes --> C[Static system context:<br/>instructions, schema, invariants, few-shot]
    B -- No --> D{Is it query-dependent knowledge?}
    D -- Yes --> E[Retrieve just-in-time -> ai-rag-engineering;<br/>cap the token budget for this slot]
    D -- No --> F{Is it conversation history?}
    F -- Yes --> G{History exceeding its budget?}
    G -- Yes --> H[Summarize/compress older turns;<br/>keep recent verbatim]
    G -- No --> I[Keep verbatim]
    F -- No --> J[Probably doesn't belong in the window]
    C --> K[ORDER for lost-in-the-middle:<br/>decisive material at start OR end, not buried]
    E --> K
    H --> K
    I --> K
    K --> L{Total near the window limit?}
    L -- Yes --> M[Define eviction order:<br/>what gets dropped/compressed first]
```

Rule: quality often *drops* as the window fills (the "lost in the middle" effect
and general dilution). If accuracy falls as you add context, remove context — do
not assume more is better.

---

## §4 — Prompt-injection defense (prompt layer)

Layered defense. **No prompt-layer control is complete** — the leaves feed
`ai-red-teaming` and app-layer controls in `security-engineering`.

```mermaid
flowchart TD
    A[Prompt includes untrusted input<br/>user text, tool output, retrieved docs] --> B[Fence it:<br/>clear delimiters + a labeled 'data' slot]
    B --> C[Instruct: treat fenced content as DATA,<br/>never as instructions to follow]
    C --> D{Does the model take a<br/>high-impact action from this output?}
    D -- Yes --> E[Constrain output to an allow-list contract;<br/>require human-in-the-loop / authz for the action]
    D -- No --> F[Constrain output to the expected schema]
    E --> G[Add injection/jailbreak cases<br/>to the regression suite]
    F --> G
    G --> H[STATE residual risk: prompt-layer defense<br/>is necessary, not sufficient]
    H --> I[Escalate whole-system attack -> ai-red-teaming;<br/>authz/rate-limit/output-moderation -> security-engineering]
```

Rule: the attacker reads your system prompt. Assume any instruction you put in
front of untrusted content can be contradicted by that content — which is why the
*mechanism* (fencing + output allow-list + out-of-band authz) matters more than
the wording.
