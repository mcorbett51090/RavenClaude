---
name: store-submission-readiness
description: "A pre-submission readiness checklist for shipping a browser extension to the Chrome Web Store, Edge Add-ons, and Firefox AMO: required listing metadata, the privacy + permissions justification, single-purpose conformance, data-disclosure forms, and the common rejection reasons to pre-empt. Reach for this before a first submission, after a rejection, or when adding a new store target. Store-policy specifics are volatile — verify against current store docs."
---

# Skill: Store-Submission Readiness

A technically-correct extension still gets rejected for listing/policy reasons.
This skill is the pre-submission checklist across the three major stores. Driven
by `extension-architect`. **Store policies evolve** — treat the specifics here as
a durable *shape* and verify the exact current requirements against each store's
developer documentation before submitting (per the marketplace accuracy
discipline).

## Step 0 — One opinion up front: the listing must match the behavior

The fastest rejections come from a mismatch between what the extension *does*,
what it *asks for*, and what the listing *says*. Make all three agree before
anything else: single, clearly-stated purpose; permissions that map to that
purpose; a description that doesn't over-claim.

## Step 1 — Pre-flight (all stores)

- [ ] Run the [`manifest-permissions-audit`](../manifest-permissions-audit/SKILL.md)
      skill first — least-privilege permissions, MV3-conformant, no remotely-hosted code.
- [ ] **Single purpose** — the extension does one clear thing; permissions don't
      exceed it.
- [ ] **Privacy** — a privacy policy if any user data is handled; data use
      disclosed honestly.
- [ ] Required listing assets — name, description, icons (multiple sizes),
      screenshots, category.
- [ ] A permissions **justification** ready for each requested permission
      (reviewers ask "why do you need this?").

## Step 2 — Chrome Web Store specifics

- Developer-dashboard data-use disclosures (the "data collection" form) completed
  honestly.
- Justification field per permission + for any broad host access + for remote code
  (you should have none).
- Common rejections: excessive/unjustified permissions, broad host access without
  need, a description that doesn't match behavior, obfuscated code,
  remotely-hosted code.

## Step 3 — Microsoft Edge Add-ons specifics

- Largely Chromium/MV3-compatible — the same package usually works.
- Its own listing + certification process and store metadata.
- Confirm the same least-privilege/single-purpose bar; Edge runs its own review.

## Step 4 — Firefox AMO specifics

- Promise-based `browser.*` APIs — confirm the `chrome.*`→`browser.*` migration
  or polyfill is in place (see [`../../knowledge/cross-browser-and-stores.md`](../../knowledge/cross-browser-and-stores.md)).
- An extension `id` (e.g. via `browser_specific_settings.gecko.id`).
- AMO may perform source-code review; `web-ext lint` should pass and minified code
  may need accompanying source.
- Common rejections: minified/obfuscated code without source, undeclared remote
  resources, permission overreach.

## Step 5 — Output: a go / no-go readiness report

- Per-store checklist status (pass / fix-needed) with the specific blocker.
- The permissions-justification text, ready to paste.
- The list of pre-empted common-rejection reasons.
- A re-verify note: which store-policy specifics were assumed and should be
  confirmed against current docs before clicking submit.

Hand the actual manifest fixes to `extension-implementation-engineer`; hand any
privacy/data-handling verdict to `security-engineering` /
`ravenclaude-core/security-reviewer`.
