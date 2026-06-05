# Technical Writing & Docs — best-practice docs

Named, citable rules for the `technical-writing-docs` plugin's specialists. Each file is **one rule** — read, applied, and cited as a whole. These deepen the Diataxis-driven docs-as-code methodology and the three specialist agents: `docs-architect`, `api-reference-writer`, and `docs-site-engineer`.

---

## Index

_22 rules._

| Doc | Status | Use when |
|---|---|---|
| [`know-which-diataxis-kind.md`](./know-which-diataxis-kind.md) | Absolute rule | Before writing any new page — identify tutorial/how-to/reference/explanation; mixing the four kinds produces a doc that serves no one. |
| [`docs-as-code.md`](./docs-as-code.md) | Absolute rule | Setting up or auditing a docs workflow — documentation must live in the repo, be reviewed in PRs, and be CI-checked. |
| [`version-docs-with-the-product.md`](./version-docs-with-the-product.md) | Absolute rule | Any change to a feature — docs ship in the same PR as the code change; docs-in-a-separate-wiki rot immediately. |
| [`examples-must-run.md`](./examples-must-run.md) | Absolute rule | Writing or reviewing any code sample — untested examples break trust faster than missing ones. |
| [`stale-docs-are-worse-than-none.md`](./stale-docs-are-worse-than-none.md) | Primary diagnostic | When a reader reports confusion — confidently-wrong docs are a liability; prune or correct before adding. |
| [`one-source-of-truth.md`](./one-source-of-truth.md) | Absolute rule | Any time the same fact appears in two docs — duplication is a future divergence bug; one owner, everything else links. |
| [`write-for-the-readers-task.md`](./write-for-the-readers-task.md) | Pattern | Organizing a docs site or a page — structure around what the reader is trying to do, not the system's module layout. |
| [`right-home-for-the-content.md`](./right-home-for-the-content.md) | Pattern | Placing new content — find the existing canonical home before creating a new page. |
| [`link-dont-duplicate.md`](./link-dont-duplicate.md) | Absolute rule | Reviewing a PR that adds a new page explaining a concept already covered elsewhere — link; never fork the truth. |
| [`document-the-unhappy-path.md`](./document-the-unhappy-path.md) | Pattern | Reviewing any guide or reference — errors, edge cases, and limits must appear; the golden path alone is insufficient. |
| [`progressive-disclosure.md`](./progressive-disclosure.md) | Pattern | Designing a page for a mixed-expertise audience — lead with the minimal correct answer, expand for depth below the fold. |
| [`optimize-time-to-first-success.md`](./optimize-time-to-first-success.md) | Pattern | Designing a quickstart or getting-started guide — minimize the steps between "I found the docs" and "it worked." |
| [`spec-driven-reference-not-hand-maintained.md`](./spec-driven-reference-not-hand-maintained.md) | Absolute rule | Authoring API reference when an OpenAPI / AsyncAPI / GraphQL spec exists — generate from the spec; never hand-maintain a copy. |
| [`changelog-is-a-reader-document.md`](./changelog-is-a-reader-document.md) | Pattern | Writing a changelog entry — write for the upgrader ("what do I need to change?"), not as a commit-log dump. |
| [`readme-covers-start-stop-and-why.md`](./readme-covers-start-stop-and-why.md) | Pattern | Writing or reviewing a repository or SDK README — it must cover what it is, how to install, a quick-start, and how to uninstall. |
| [`error-messages-are-docs.md`](./error-messages-are-docs.md) | Pattern | Designing or reviewing API error responses and CLI error output — the error message is often the only doc the reader sees at the moment they need help. |
| [`audience-before-architecture.md`](./audience-before-architecture.md) | Pattern | Designing the information architecture of a new docs site — define reader personas and top tasks before drawing the sitemap. |
| [`ci-gate-broken-links-and-examples.md`](./ci-gate-broken-links-and-examples.md) | Absolute rule | Setting up or auditing a docs CI pipeline — both broken links and failing code examples must be mechanically gated. |
| [`scope-the-tutorial-to-one-success.md`](./scope-the-tutorial-to-one-success.md) | Pattern | Scoping a new tutorial — one tutorial, one observable successful outcome; everything else is a how-to or a separate tutorial. |
| [`annotate-volatile-content-with-dates.md`](./annotate-volatile-content-with-dates.md) | Pattern | Writing or reviewing content that changes frequently (pricing, rate limits, third-party SDK compatibility) — annotate with a last-verified date and staleness trigger. |
| [`api-auth-docs-before-feature-docs.md`](./api-auth-docs-before-feature-docs.md) | Absolute rule | Structuring an API reference or quickstart — authentication must be documented first; no feature is usable without it. |
| [`navigation-labels-are-user-tasks.md`](./navigation-labels-are-user-tasks.md) | Pattern | Naming nav items in a docs site — labels name the reader's task (verb phrase), not the product feature (internal name). |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
