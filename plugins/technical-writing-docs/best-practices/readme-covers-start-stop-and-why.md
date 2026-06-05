# A README Covers What It Is, How to Start, and How to Stop

**Status:** Pattern
**Domain:** Technical Writing — Repository / SDK documentation
**Applies to:** `technical-writing-docs`

---

## Why this exists

A README is the first doc a developer reads and the last one they have patience for. Most READMEs either contain one paragraph that says "this is a widget library" and nothing else, or a 4,000-word monolith that embeds the full user guide. The first fails anyone who wants to try it; the second sends the reader to search for the 10 lines they need. The job of a README is to answer three questions in the minimum number of words: *What does this do (and should I use it)? How do I get it running? How do I stop or uninstall it cleanly?*

## How to apply

**Minimum viable README structure:**

```markdown
# <Package or project name>

<One sentence: what it does and who it is for.>

## Install

```shell
npm install my-package   # or pip install / go get / etc.
```

## Quick Start

<The shortest path from zero to a working result — one code block.>

## Usage

<The most common use case, with a runnable example.>

## Configuration

<Key config options as a table or annotated example.>

## Uninstall / Clean up

<How to remove it cleanly — reverse the install, what state is left behind.>

## Contributing

<One line pointing to CONTRIBUTING.md or equivalent.>

## License
```

**Rules:**
- The quick-start code block must be copy-paste-runnable; test it in a clean environment before publishing.
- The "one sentence" description answers "what + for whom" — e.g., "A lightweight rate-limiter for Node.js APIs, with Redis or in-memory backends."
- Configuration table: key | type | default | description. Not prose.
- "Uninstall / Clean up" is frequently omitted; include it — it signals that the author thought about reversibility and sets expectations about what state the library manages.

**Do:**
- Keep the README to the top-level entry point; link to `/docs` for everything else.
- Update the quick-start example in the same PR as the feature it documents.
- Include a badge row (CI status, coverage, version) only if the badges are current — stale badges mislead.

**Don't:**
- Embed the full API reference in the README — link to the generated reference.
- Put architecture diagrams in the README unless the project is primarily an architecture.
- Write a README in future tense ("this will support…") — READMEs document the present.

## Edge cases / when the rule does NOT apply

- **Monorepo workspace packages**: individual package READMEs follow this pattern; the root README links to them rather than duplicating their content.
- **CLI tools**: add a "Commands" section (help output) as a fifth section; the quick-start is `my-tool --help`.

## See also

- [`../agents/api-reference-writer.md`](../agents/api-reference-writer.md) — owns SDK and library READMEs
- [`./optimize-time-to-first-success.md`](./optimize-time-to-first-success.md) — the parent principle that the README's quick-start optimizes for

## Provenance

Codifies the `api-reference-writer` agent's README guidance. Structure informed by Make a README (makeareadme.com) and review of high-quality open-source project READMEs. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
