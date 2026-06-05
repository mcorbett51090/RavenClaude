# Technical Writing & Docs — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before writing a doc or picking a docs tool.

## Decision Tree: Which kind of doc is this (Diataxis)?

Identify the reader's need; don't blend the four kinds.

```mermaid
graph TD
  A[Something to document] --> B{Is the reader learning the product for the first time?}
  B -- Yes --> C[Tutorial - hand-held, guaranteed-to-work path]
  B -- No --> D{Do they have a specific task/goal right now?}
  D -- Yes --> E[How-to guide - steps to accomplish the task]
  D -- No --> F{Do they need to look up facts e.g. params, endpoints?}
  F -- Yes --> G[Reference - complete, accurate, spec-driven]
  F -- No, they want to understand WHY --> H[Explanation - concepts, trade-offs, background]
```

_A 'tutorial' full of reference tables, or a reference that lectures on concepts, helps no one._

## Decision Tree: Docs tooling choice

Pick by maintenance, versioning, and design-control needs — not by popularity.

```mermaid
graph TD
  A[Need a docs site] --> B{Want hosted + polished out of the box?}
  B -- Yes --> C[Mintlify / hosted platform]
  B -- No, self-host --> D{Heavy customization / React components in docs?}
  D -- Yes --> E[Docusaurus / Starlight]
  D -- No, simple markdown site --> F{Python ecosystem?}
  F -- Yes --> G[MkDocs Material]
  F -- No --> E
  E --> H[Need docs versioning + i18n? confirm support]
  G --> H
```

## Decision Tree: Where does this content belong?

Diataxis says which kind; this says which page already owns the fact. Default to linking, not restating.

```mermaid
graph TD
  A[A fact to document] --> B{Does a canonical home already exist?}
  B -- Yes --> C[Link to it; do NOT restate - duplication drifts]
  B -- No --> D{Is the reader looking it up e.g. params/codes?}
  D -- Yes --> E[Reference - one authoritative page, spec-driven if possible]
  D -- No --> F{Are they doing a task?}
  F -- Yes --> G[How-to guide - steps; link the reference + concept]
  F -- No --> H{Do they need to understand WHY?}
  H -- Yes --> I[Explanation - concepts/trade-offs; link the how-to]
  H -- No --> J[Learning from zero -> Tutorial]
```

_The same fact in two places is one place that will go wrong. One owner, everything else links._

## Decision Tree: Is this doc worth writing (and keeping)?

A confidently-wrong or never-read doc is a liability; write to a real reader need, prune the rest.

```mermaid
graph TD
  A[A doc someone wants written] --> B{Is there a real reader with a real task for it?}
  B -- No --> C[Don't write it - it'll rot unread]
  B -- Yes --> D{Does the truth live in code/spec we can generate from?}
  D -- Yes --> E[Generate it; don't hand-maintain a copy]
  D -- No --> F{Can we commit to keeping it current with the product?}
  F -- No --> G[Either don't write it or date it + mark volatile]
  F -- Yes --> H{Already covered elsewhere?}
  H -- Yes --> I[Improve/link the existing page, don't fork]
  H -- No --> J[Write it - pick the Diataxis kind, tie to the release]
```

_Maintaining less but accurate beats hoarding more that quietly rotted._

## Decision Tree: How do I keep examples from going stale?

Examples must run; choose the mechanism by how the example is produced and tested.

```mermaid
graph TD
  A[A code example in the docs] --> B{Can it be extracted FROM tested code?}
  B -- Yes --> C[Embed from the tested source - single source of truth]
  B -- No --> D{Can the snippet be executed in CI as written?}
  D -- Yes --> E[Doc-test it - run the snippet, assert output, gate the build]
  D -- No --> F{Is it generated from a spec e.g. OpenAPI?}
  F -- Yes --> G[Regenerate on spec change; no hand-editing]
  F -- No --> H[Last resort: hand-written + a periodic manual verify + a date]
  C --> I[Broken example fails the build like any regression]
  E --> I
```

_A copy-paste snippet that errors destroys trust faster than a missing one._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Diataxis framework | established | The 4-kind model |
| Docusaurus / Starlight | GA | React-based, versioning, MDX |
| Mintlify | GA | Hosted, polished, API docs |
| MkDocs Material | GA | Simple, Python, fast |
| OpenAPI -> reference (e.g. Redocly) | GA | Spec-driven, no drift |
| Link-check / doc-test in CI | mature | Gate broken links + examples |

---

## Decision Tree: Should this be a new page or an update to an existing page?

**When this applies:** A writer or contributor wants to document something and is deciding whether to create a new doc, add a section to an existing page, or just add a link. Observable trigger: a PR description says "adding new docs page for X" or a Jira ticket says "document feature Y."

**Last verified:** 2026-06-05 against the `one-source-of-truth` and `right-home-for-the-content` best-practices.

```mermaid
graph TD
  A[Something new to document] --> B{Does a canonical page for this topic already exist?}
  B -- Yes --> C{Is the new content a deeper treatment of the same topic?}
  C -- Yes, same topic, more depth --> D[Add a section to the existing page and link from related pages]
  C -- No, related but distinct task or concept --> E[Create a new page and link from the canonical page]
  B -- No --> F{Is this a fact that belongs in an existing reference page e.g. a new parameter?}
  F -- Yes --> G[Add to the reference page - one authoritative page per fact]
  F -- No, genuinely new topic --> H{Which Diataxis kind?}
  H -- Tutorial --> I[New tutorial page - scope to one success]
  H -- How-to --> J[New how-to page - steps to accomplish one task]
  H -- Reference --> K[New reference page or section in the existing reference]
  H -- Explanation --> L[New explanation page - concepts or trade-offs]
```

**Rationale per leaf:**
- *Add a section* — same topic with more depth stays on the canonical page so there is one place to maintain and one place to link to.
- *New page, link from canonical* — a related but distinct task or concept warrants its own page to keep Diataxis kinds separate; the canonical page cross-links.
- *Add to reference* — facts like parameters, error codes, and config options belong in the single authoritative reference page, not scattered across prose guides.
- *New Diataxis-typed page* — a genuinely new topic starts a properly-typed page so the site doesn't accumulate unfiled blobs.

---

## Decision Tree: How to handle a doc that is out of date?

**When this applies:** A doc is discovered to be inaccurate, outdated, or no longer matches the current product behavior. Observable trigger: a reader reports an error, a developer notices a stale example, or a content audit flags a page with a last-verified date older than the threshold.

**Last verified:** 2026-06-05 against the `stale-docs-are-worse-than-none` and `annotate-volatile-content-with-dates` best-practices.

```mermaid
graph TD
  A[Out-of-date doc identified] --> B{Is the content still partially correct or entirely wrong?}
  B -- Entirely wrong or misleading --> C{Is there a correct replacement?}
  C -- Yes, a canonical page exists --> D[Delete the stale page and add a redirect to the canonical one]
  C -- No replacement exists yet --> E[Add a visible dated warning callout and open a fix ticket - do not leave it silently wrong]
  B -- Partially correct, volatile section --> F{Can the correct value be verified now?}
  F -- Yes --> G[Update the content and refresh the last-verified annotation]
  F -- No, cannot verify right now --> H[Add a dated warning callout with a link to the authoritative source and schedule a re-verify]
```

**Rationale per leaf:**
- *Delete + redirect* — an entirely wrong page with a replacement is a liability; removing and redirecting is better than letting readers find the wrong one.
- *Warning callout + ticket* — if the correct answer isn't known yet, warn the reader immediately and open a tracked fix; do not leave silence where a wrong answer sits.
- *Update + refresh annotation* — the lowest-cost path when the correct value is known; updating is faster than deleting and preserves the page's search ranking.
- *Warning + link + schedule* — when verification requires a live system check or a vendor lookup that can't happen right now; the callout is the interim protection.

---

## Decision Tree: API docs structure — should this information go in the quickstart, the reference, or a guide?

**When this applies:** You have a piece of API information to document and must decide which section owns it. Observable trigger: writing API docs and a fact could plausibly live in multiple places.

**Last verified:** 2026-06-05 against Diataxis (tutorial/how-to/reference/explanation) and the `api-auth-docs-before-feature-docs` best-practice.

```mermaid
graph TD
  A[A piece of API information to document] --> B{Is it a fact a developer will look up when they already know what they want?}
  B -- Yes - a parameter, type, error code, response shape --> C[API Reference page - spec-driven if possible]
  B -- No, it is instructional --> D{Is the reader learning the API for the first time?}
  D -- Yes, first contact, needs a working call fast --> E[Quickstart - authenticated first call in under 5 minutes]
  D -- No, knows the API, has a specific task --> F{Is this a sequence of steps to accomplish a task?}
  F -- Yes --> G[How-to guide - steps with a runnable example]
  F -- No, conceptual or background --> H[Explanation section - concepts, architecture, trade-offs]
  C --> I[Always put auth before endpoints - link auth from every reference page]
  E --> I
```

**Rationale per leaf:**
- *Reference* — look-up information (parameters, types, errors) belongs in spec-driven reference; it must be complete, accurate, and findable by name.
- *Quickstart* — the first-contact path must optimize for time-to-first-working-call; everything else is a distraction here.
- *How-to guide* — a specific task sequence (upload a file, handle pagination, implement a webhook) belongs in a how-to, not in reference or the quickstart.
- *Explanation* — concepts (how rate limiting works, the token refresh model) belong in explanation so they don't clutter the procedural guides; readers who want the why find them here.
- *Auth first* — enforces `api-auth-docs-before-feature-docs`: authentication information links into every surface.
