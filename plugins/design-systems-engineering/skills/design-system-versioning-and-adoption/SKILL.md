---
name: design-system-versioning-and-adoption
description: "Version a component library like the public contract it is (semver + changesets), ship breaking changes with codemods and loud deprecation, and drive adoption with metrics. Traverses the versioning branch of the design-systems decision tree: semver mapping → changesets/release flow → breaking-change/codemod policy → deprecation → adoption metrics. Reach for this when the user asks 'how do we version the library?', 'set up changesets', 'how do we ship this breaking change?', or 'how do we drive adoption / measure it?'. Used by design-systems-architect (policy) and design-tokens-and-component-engineer (release pipeline)."
---

# Skill: design-system-versioning-and-adoption

> **Invoked by:** `design-systems-architect` (the versioning/governance policy) and
> `design-tokens-and-component-engineer` (the release pipeline + codemods).
>
> **When to invoke:** "how do we version the library?"; "set up changesets/the release flow"; "how
> do we ship this breaking change without breaking consumers?"; "how do we drive/measure adoption?";
> any "how does this library get released and adopted" question.
>
> **Output:** a versioning & adoption plan — the semver mapping, the changesets/release flow, the
> breaking-change/codemod/deprecation policy, and the adoption metrics — so every change is
> versioned and consumers get a clean, mechanical upgrade path.

## Procedure

1. **Map semver honestly for a component library.** A library's contract is its component APIs and
   token names, plus *rendered output* consumers depend on. **Major:** a removed/renamed
   prop/token, a changed default that alters rendering, a raised peer-dependency floor, a
   markup/ARIA change that breaks a consumer's selectors/tests. **Minor:** a new component, prop,
   token, or variant (additive). **Patch:** a bug fix that preserves the contract. When in doubt
   between minor and major, it's major — the contract is sacred.
2. **Automate versioning with changesets (or equivalent).** Every PR that changes shipped code
   carries a changeset declaring its bump and a human-readable summary; release tooling aggregates
   them into the version bump + changelog. Nothing ships unversioned; the changelog writes itself
   from the changesets *(retrieval-dated 2026-07; verify the tool's API at use)*.
3. **Make every breaking change mechanical for consumers.** The sequence is: (a) ship a
   **deprecation** in a minor — the old API still works but warns, with the replacement named; (b)
   ship a **codemod** that rewrites consumer code automatically (rename the prop, swap the token);
   (c) write a **migration note**; (d) remove the deprecated API in the **next major**. A migration
   guide *alone* is homework you've handed the consumer — the codemod is the courtesy.
4. **Deprecate loudly, remove slowly.** A deprecated API lives at least one major cycle with a
   console/lint warning pointing to the replacement. Surprise removals are how a system loses
   consumer trust — and trust is the whole product.
5. **Set the contribution & governance model.** Who can add to the system, the review bar (a11y +
   API + docs + changeset required), and the promotion path from product-local to system. Keep the
   system opinionated: additions must be reused-and-stable, not one-offs.
6. **Instrument adoption — it's the success metric.** Pick 1–2 metrics: **% of surfaces on the
   current major**, **token coverage** (share of styles from tokens vs hardcoded), **component
   adoption** (system component vs bespoke), **escaped-hardcoded-value count**. A system nobody
   migrates to has failed regardless of its internal elegance.
7. **State the trigger conditions** — when the policy changes (e.g. "once >3 external teams consume,
   move to a scheduled release train instead of on-merge"; "if adoption stalls below X%, the
   blocker is usually migration cost — invest in codemods and defaults before new features").

## Worked example

> User: "We're renaming `<Button variant>` to `<Button tone>` and want to add changesets. How do
> we ship this without breaking the five apps consuming us?"

- **Semver:** renaming a public prop is **major**.
- **Release flow:** adopt changesets; every PR adds a changeset; releases aggregate to the bump +
  changelog.
- **Migration sequence:** (1) minor release — accept both `variant` and `tone`, `variant` logs a
  deprecation warning naming `tone`; (2) ship a codemod (`npx @ds/codemod button-variant-to-tone`)
  that rewrites `variant=` → `tone=` across a consumer's codebase; (3) migration note in the
  changelog; (4) next major — remove `variant`.
- **Adoption:** track "% of the five apps on the current major" weekly; the codemod makes the
  migration a one-command chore, so adoption should be fast.
- **Trigger:** if an app can't migrate (pinned old major), the deprecation stays until it does — do
  not remove on schedule if a consumer is stranded.

## Guardrails

- **When in doubt, it's a major** — under-calling a breaking change is how you break consumers silently.
- **Codemod, not just a guide** — make the upgrade mechanical; a guide alone offloads your work.
- **No unversioned change** — a changeset per shipped PR is the floor.
- **Deprecate at least a full major before removal** — loud warning, named replacement, slow removal.
- **Additive by default** — grow the system with minors; reserve majors for genuine contract breaks.
- **Adoption is the metric** — an elegant system nobody uses is a failed system; lower migration cost
  before adding features.
- **Retrieval-date the release tooling** (changesets/registry mechanics); the semver principle is durable.
