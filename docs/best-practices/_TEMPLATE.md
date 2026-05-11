# <Short rule name — what this doc tells you to do or not do>

> Copy this file to a new slug (`docs/best-practices/<slug>.md`), then fill in every section. Delete this top blockquote and the inline comments before opening your PR.

**Status:** _Pick one — delete the others._
- **Absolute rule** — never break this. Violations are bugs, not preferences.
- **Primary diagnostic** — when symptom X appears, check this first.
- **Pattern** — strong default; deviate only with a written reason.

**Domain:** _e.g. ALM, Identity, Web API, Solution mechanics, Agent design, Cross-domain. Match an existing tag where possible so the index stays clean._

**Applies to:** _Which plugin(s), tool(s), or project type(s) this is relevant for. Examples: `ravenclaude-core`, `power-platform`, `any Claude Code project`._

---

## Why this exists

_2–5 sentences. The rationale, not the rule. Why is this worth a doc? What goes wrong if someone ignores it? If there's a specific incident or paper trail behind the rule, mention it here._

## How to apply

_Concrete, copy-paste-grade guidance. Code blocks, payloads, file snippets — whatever a reader needs to actually follow the rule without re-deriving it._

```
<example code, payload, config, or command — replace with the real thing>
```

_Optional: bulleted "do" and "don't" lists if the rule has clean opposite cases._

**Do:**
- _…_

**Don't:**
- _…_

## Edge cases / when the rule does NOT apply

_If the rule has known exceptions, list them here. A rule that admits no exceptions and a rule whose exceptions are documented are both defensible — a rule with quiet, undocumented exceptions is not._

## See also

_Cross-references to other best-practice docs, lessons-learned entries, or external authoritative sources (Microsoft Learn, RFCs, vendor docs). Use repo-relative links so they survive renames._

- [Related best-practice doc](./other-doc.md)
- [Related lesson](../memory-bank/lessons-learned.md#YYYY-MM-DD-anchor)
- _External link with a short note on why it's authoritative_

## Provenance

_Where this rule came from. Be specific. "Discovered while debugging X in Y project on 2026-MM-DD," or "From the Microsoft Learn page on Z," or "From a conversation with <named collaborator>." This is what makes the rule trustworthy a year from now._

---

_Last reviewed: YYYY-MM-DD by `<github-handle>`_
