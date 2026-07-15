---
name: structured-output-design
description: "Make an LLM return reliably machine-parseable output — choose the enforcement mechanism (native JSON/schema mode, tool/function calling, constrained grammar, or prose+parser), define the schema, and build the parse/validate/repair path. Reach for this when output format drifts, when downstream code parses model output, or when 'return JSON' in prose keeps failing. Pairs with prompt-pattern-selection."
---

# Skill: Structured-output design

Turn "please return JSON" (a wish) into an enforced contract. The mechanism
matters more than the wording.

## Step 0 — One opinion up front
**Prefer mechanism over pleading.** Reach for the strongest enforcement the model
supports before adding words that ask nicely. Prose instructions are the *last*
resort, not the first.

## Step 1 — Define the schema and the failure shape
Write the target schema (JSON Schema or a tool parameter schema). Then define the
*non-happy* paths: the refusal shape, the "I don't know" shape, and what an error
looks like. Downstream code needs a contract for failure too, not just success.

## Step 2 — Pick the enforcement mechanism
Trace [`../../knowledge/prompt-decision-trees.md`](../../knowledge/prompt-decision-trees.md) §2:
1. **Native structured / JSON-schema mode** (if the model has it).
2. **Tool / function calling** — define the output *as* a tool, force the call.
3. **Constrained decoding / grammar** (self-hosted runtimes).
4. **Prose + robust parser** — only if none of the above, always with delimiters.

## Step 3 — Build the parse → validate → repair path
**Never** trust the raw output, even from native modes:
- **Parse** into your type.
- **Validate** against the schema *and* the business rules (a valid JSON string
  can still violate an invariant).
- **Repair**: on failure, re-prompt with the specific validation error, bounded
  retries, then **fail closed** with a defined error the caller can handle.

## Step 4 — Fence any untrusted input
If user text, tool output, or retrieved docs go into the prompt, fence and label
them as data (see the injection best-practice) — structured output does not by
itself stop injection.

## Step 5 — Hand off
- The **regression set + CI gate** proving it stays valid → `prompt-reliability-engineer`.
- **Which model supports which mode** → `ai-coding-model-guidance` / `claude-api`.
- The **app-side parsing/validation code** → `backend-engineering`.

## Output
A structured-output implementation: the schema, the chosen enforcement mechanism
(with the tree path), the parse/validate/repair path, the fail-closed behavior,
and the fencing of any untrusted slots.
