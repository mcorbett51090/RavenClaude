---
name: diataxis-classification
description: "Practical guide for classifying documentation into the four Diataxis quadrants (tutorial, how-to, reference, explanation) — with a decision checklist, anti-pattern catalog, and remediation moves."
---

# Diataxis Classification

## When to Use This

Before writing a new doc or auditing existing content, to ensure you're writing the right kind of thing — serving the reader's actual need rather than mixing quadrants into docs that help nobody well.

## The Four Quadrants

| Type | Serves | Reader state | Success criterion |
|---|---|---|---|
| **Tutorial** | Learning | Newcomer; wants to be led | Reader completes it and has learned something real |
| **How-to guide** | Accomplishing a task | Practitioner; wants to do X | Reader achieves the specific goal |
| **Reference** | Information lookup | Expert; wants a fact | Reader finds the fact quickly and trusts its accuracy |
| **Explanation** | Understanding | Curious; wants to know why | Reader develops a mental model |

The axes are: **action vs cognition** (doing vs understanding) and **acquisition vs application** (learning vs working).

## Classification Checklist

Ask these questions about your document:

```
1. Is the reader already using the product, or just starting out?
   → Starting out: Tutorial
   → Already using: How-to, Reference, or Explanation

2. Does the reader want to DO something right now?
   → Yes: Tutorial (guided practice) or How-to (autonomous task)
   → No: Reference (lookup) or Explanation (understanding)

3. Is the reader a newcomer being guided, or a practitioner navigating alone?
   → Guided newcomer: Tutorial
   → Autonomous practitioner: How-to

4. Does the reader want a fact (value, parameter, behavior) or a mental model (why, how it works)?
   → Fact: Reference
   → Mental model: Explanation
```

## Anti-Pattern Catalog

| Anti-pattern | Symptom | Remediation |
|---|---|---|
| Tutorial-as-reference | Guided walkthrough ending with a giant parameter table | Split: keep walkthrough as tutorial; extract table to reference |
| How-to buried in tutorial | "Now that you've learned X, here's how to do Y and Z" | Write Y and Z as separate how-to guides; link from tutorial |
| Explanation mixed into reference | API reference with paragraphs about design philosophy | Move philosophy to an explanation doc; reference stays factual |
| Reference used as a tutorial | "See the parameter list to get started" | Write a tutorial that uses the reference; don't merge them |
| Giant catch-all "Overview" page | Contains tutorial steps + design rationale + parameter tables + task instructions | Decompose into one doc per quadrant; overview page links to all four |

## Reference vs How-to Decision

The most commonly confused pair:

| Scenario | Correct type |
|---|---|
| "Here are all the config options and their defaults" | Reference |
| "How to configure authentication with OAuth 2.0" | How-to |
| "Here are all the API endpoints, their parameters, and responses" | Reference |
| "How to authenticate a request" | How-to (uses reference for details) |
| "Here are all the error codes" | Reference |
| "How to handle a 429 rate-limit response" | How-to |

## Writing Signals by Type

**Tutorial signals** — present tense, active voice, guiding tone: "Click Save. You'll see a confirmation…" Minimal explanation, maximum forward momentum.

**How-to signals** — imperative mood, assumes prior knowledge, no hand-holding: "Configure the webhook endpoint." Reader can skip steps they've done before.

**Reference signals** — noun-heavy, consistent structure, scannable: function signatures, tables, parameter lists, exact values. No prose narrative.

**Explanation signals** — discusses trade-offs, uses "because," "in order to," "the reason": "Tokens expire after 15 minutes because long-lived tokens increase the blast radius of a compromise."

## Audit Worksheet

For each existing doc, complete:

```
Doc title: ___________
Intended type (by author): ___________
Actual type (by classification checklist): ___________
Mixed types present: ___________
Remediation: split / rewrite / move / keep
```

## Pitfalls

- Writing tutorials for practitioners — they skip the hand-holding and get lost; they need a how-to.
- Conflating "comprehensive" with "good" — a reference page that explains everything is harder to scan than one that just states facts.
- Writing explanation in the reference page to justify design choices — readers looking up a parameter don't want a philosophy essay; link to the explanation doc.
- Creating an "overview" page to avoid classifying — it becomes the junk drawer that nobody trusts.

## See Also

- [`../../agents/docs-architect.md`](../../agents/docs-architect.md) — Diataxis framework, information architecture, docs-as-code
- [`../../agents/api-reference-writer.md`](../../agents/api-reference-writer.md) — reference and how-to docs for developer APIs
