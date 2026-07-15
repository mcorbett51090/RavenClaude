# Prompt spec — `<prompt name / feature>`

> Output of `prompt-architect` + `prompt-implementation-engineer`. One spec per prompt (or per
> prompt in a chain). Keep it in version control next to the prompt file.

## 1. Job (one responsibility)
- **This prompt's single job:** `<…>`
- **If it's doing more than one job:** split it — link the sibling specs.

## 2. Pattern
- **Chosen pattern:** `<zero-shot | few-shot | CoT | decomposition | role | self-consistency>`
- **Tree path taken (§1):** `<…>`
- **Runner-up + why it lost:** `<…>`
- **Token/latency cost of the choice:** `<…>`

## 3. Context plan (§3)
| Section | Source | Token budget | Order |
| --- | --- | --- | --- |
| System / instructions | static | `<…>` | first (cacheable) |
| Few-shot examples | static | `<…>` | early |
| Retrieved context | `ai-rag-engineering` | `<…>` | mid |
| Conversation history | runtime | `<…>` | recent verbatim |
| User input (UNTRUSTED) | runtime | `<…>` | fenced + labeled |
| Output headroom | — | `<…>` | — |
- **Eviction order when full:** `<…>`

## 4. Output contract (§2)
- **Schema:** `<JSON Schema / tool schema>`
- **Enforcement mechanism:** `<native JSON mode | tool-calling | grammar | prose+parser>`
- **Refusal / error shape:** `<…>`
- **Validation (schema + business rules):** `<…>`
- **Repair/retry + fail-closed behavior:** `<…>`

## 5. Untrusted-input handling
- **Which slots are untrusted:** `<…>`
- **Fencing + data-labeling:** `<…>`
- **High-impact actions gated by external authz / human-in-the-loop:** `<…>`

## 6. Model assumptions (dated — verify)
- **Target model + version:** `<…>` — *retrieval date: `<YYYY-MM-DD>`*
- **Window size / structured-output support / caching:** `<…>`
- **Determinism (temperature / seed):** `<…>`

## Hand-offs
- [ ] Regression set + CI gate → `prompt-reliability-engineer`
- [ ] Model choice / limits → `ai-coding-model-guidance` / `claude-api`
- [ ] Retrieval for context slots → `ai-rag-engineering`
- [ ] App wiring / parsing code → `backend-engineering`
