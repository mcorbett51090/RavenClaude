# Navigation Labels Name the User's Task, Not the Feature

**Status:** Pattern
**Domain:** Technical Writing — Information architecture / navigation
**Applies to:** `technical-writing-docs`

---

## Why this exists

Navigation labels written from the product's perspective ("Webhook Configuration Manager", "Data Ingestion Pipeline API") require the reader to translate the product vocabulary into their own task vocabulary before they can pick the right link. Navigation labels written from the reader's perspective ("Set up webhooks", "Import your data") do that translation for them. The difference is seconds per click but multiplied by every reader and every session. Discoverability problems — "I couldn't find it" — are almost always labeling problems, not content problems.

## How to apply

**Labeling heuristic — test each nav label with this question:**

> "Could a reader who hasn't used the product yet correctly predict what they'll find behind this label?"

**Renaming examples:**

| Product-centric (avoid) | Task-centric (prefer) |
|---|---|
| Webhook Configuration Manager | Set up webhooks |
| Data Ingestion Pipeline | Import data |
| Authentication & Authorization Module | Log in / Manage access |
| Rate Limiting Policies | Understand rate limits |
| Error Codes Reference | Troubleshoot errors |
| SDK Integration Guide | Add the SDK to your app |

**Rules:**
- **Use verb phrases** for how-to sections ("Set up…", "Configure…", "Migrate…").
- **Use noun phrases** for reference sections ("API reference", "Error codes", "Glossary") — these are looked up, not navigated by task.
- **Keep labels to 3–5 words**: longer labels are truncated on mobile and skimmed-past on desktop.
- **Avoid internal project names and code names** that mean nothing to a first-time reader.

**Top-level nav architecture:**

| Section | Label style | Diataxis kind |
|---|---|---|
| Learning | "Get started", "Tutorials" | Tutorial |
| Task guides | Verb phrases — "Connect X", "Configure Y" | How-to |
| Reference | Noun — "API reference", "CLI reference" | Reference |
| Concepts | "How [product] works", "Architecture" | Explanation |

**Do:**
- Run a short tree-test (5 tasks, 5 participants) to validate labels before a major nav redesign ships.
- Check that the label matches the `<h1>` of the page it links to — mismatch breaks scent.
- Review nav labels alongside a content audit — a label that maps to three different pages is a duplication signal.

**Don't:**
- Use feature names as nav labels unless the feature is so well-known that users search for it by name.
- Create a "Miscellaneous" or "Other" nav item — everything deserves a real category.
- Mix task-centric and product-centric labels in the same level of the navigation.

## Edge cases / when the rule does NOT apply

- **Developer portals where the audience already knows the feature vocabulary**: SDK authors, platform developers, and power users navigate by feature name. A "Webhooks API reference" is correct for the reference section even though "webhooks" is product vocabulary — because the reader is explicitly looking up webhook specs.
- **Changelog and release notes**: these are intrinsically product-centric ("v2.3.0 Release Notes") and should not be renamed.

## See also

- [`../agents/docs-architect.md`](../agents/docs-architect.md) — designs the site IA and navigation taxonomy
- [`./write-for-the-readers-task.md`](./write-for-the-readers-task.md) — the same principle applied at the page level

## Provenance

Codifies house opinion #4 ("Write for the reader's task, not the system's structure") applied to navigation. Label design informed by Peter Morville & Louis Rosenfeld, "Information Architecture for the World Wide Web," and Nielsen Norman Group wayfinding research. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
