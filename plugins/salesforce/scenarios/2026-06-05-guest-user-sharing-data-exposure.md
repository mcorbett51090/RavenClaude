---
scenario_id: 2026-06-05-guest-user-sharing-data-exposure
contributed_at: 2026-06-05
plugin: salesforce
product: experience-cloud
product_version: "unknown"
scope: likely-general
tags: [security, guest-user, sharing, crud-fls, experience-cloud, without-sharing, owd]
confidence: high
reviewed: false
---

## Problem

A public Experience Cloud (Community) site had an `@AuraEnabled` Apex controller that returned a list of Cases for the logged-in contact. It worked in testing as an authenticated partner. After go-live, a security review found that an **unauthenticated** visitor hitting the same site's guest pages could retrieve **every** Case in the org, not just public ones — the controller leaked the whole object to the internet. Root cause: the controller class was declared `without sharing` (copied from an internal batch job), ran an unbounded `SELECT ... FROM Case`, and the org's Case OWD plus the Guest User profile combined to expose far more than intended. This is the highest-severity class of Salesforce defect — a public data exposure — and it escalates to `ravenclaude-core/security-reviewer` for the verdict; this plugin supplies the domain mechanism.

## Constraints context

- Guest users share a **single** Guest User profile across all anonymous visitors — there is no per-visitor record ownership to lean on, so a too-open `WHERE` clause or a `without sharing` controller exposes data to the entire public.
- The Case OWD had been loosened to Public Read/Write years earlier for an internal reason no one remembered, so record-level sharing wasn't protecting anything.
- The controller selected fields with no FLS check, so even fields the guest profile shouldn't see came back.
- `[verify-at-build]` guest-user security hardening defaults (e.g. guest users can't be record owners, the secure-guest-sharing settings) shift by release — confirm the current Salesforce guest-user security model before relying on a platform default.

## Attempts

- Tried: tightening the Guest User profile to remove Case object access entirely. Correct as defense-in-depth, but it broke the *legitimate* public use case (showing the visitor's own submitted Case by a token) — too blunt on its own.
- Tried: adding a `WHERE ContactId = :someId` filter. Better, but the controller was still `without sharing`, so a crafted id or a missing bind could still over-return; the filter was a band-aid over the wrong sharing posture.
- Tried (the fix): a layered correction — (a) make the controller `with sharing` so record-level access is enforced for the guest context, (b) enforce CRUD/FLS on the read with `WITH SECURITY_ENFORCED` (or `Security.stripInaccessible` / `USER_MODE`), (c) tighten the Case OWD back to Private and grant the narrow public slice via a scoped sharing mechanism, and (d) audit the Guest User profile to the minimum object/field access the site genuinely needs.

## Resolution

**`with sharing` by default; every `without sharing` is justified in a comment — and for a public/guest surface, record-level sharing alone is not the control: layer OWD + FLS + a minimal guest profile.** The reliable posture:

1. **Default `with sharing`.** A user-context controller — especially one reachable by a guest — enforces the running user's record access. `without sharing` is only for a *documented* system operation that must see all records, scoped narrowly; it should never be the copy-paste default (house opinion #6).
2. **Enforce CRUD/FLS explicitly.** `WITH SECURITY_ENFORCED` in the SOQL (hard-fail on an inaccessible field), or `Security.stripInaccessible` (graceful strip), or `AccessLevel.USER_MODE` end-to-end. A guest seeing a field its profile forbids is an FLS leak even if the records are right (house opinion #7).
3. **OWD most-restrictive, then open deliberately.** Start Private and open access through an explicit, auditable sharing mechanism — never leave an object Public Read because of a forgotten legacy decision.
4. **Audit the Guest User profile to least privilege.** Remove every object and field the public site doesn't strictly need; the single shared guest profile is the blast radius.
5. **Scope the `WHERE` clause to the visitor's legitimate slice** — but treat that as the *last* layer, never the only one.

The trap: a controller that's correct for an authenticated internal user is a public data leak when the same class is `without sharing` and reachable by the guest profile. The four controls are defense-in-depth — any one alone fails open.

**Action for the next engineer:** for anything reachable by an Experience Cloud guest, check the sharing keyword first (`with sharing` unless justified), confirm CRUD/FLS is enforced on every read, verify the object OWD isn't accidentally Public, and audit the Guest User profile to least privilege. Route the security verdict to `ravenclaude-core/security-reviewer` — this plugin supplies the mechanism, core owns the sign-off.

Cross-reference: canonical guidance in [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md), the **Apex Security** and **Experience Cloud auth** decision trees in [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md); rules [`../best-practices/enforce-sharing-and-crud-fls.md`](../best-practices/enforce-sharing-and-crud-fls.md), [`../best-practices/security-guest-user-and-experience-cloud-sharing.md`](../best-practices/security-guest-user-and-experience-cloud-sharing.md), and [`../best-practices/data-owd-most-restrictive-then-open-deliberately.md`](../best-practices/data-owd-most-restrictive-then-open-deliberately.md). House opinions #6 and #7.
