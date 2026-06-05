---
scenario_id: 2026-06-05-api-plugin-obo-auth-loop
contributed_at: 2026-06-05
plugin: microsoft-365-copilot
product: api-plugin
product_version: "unknown"
scope: likely-general
tags: [api-plugin, oauth, on-behalf-of, entra, operationid, consent, security-reviewer]
confidence: medium
reviewed: false
---

## Problem

An API plugin was meant to fetch the signed-in user's records from a downstream Entra-protected API. In Copilot it sat in a loop: the agent kept asking the user to sign in, the consent screen reappeared, and the call never completed. Where it *did* return, it returned **another user's** data in a test tenant — a per-user-authorization failure, not just a UX annoyance. Separately, one operation in the OpenAPI never fired because the `operationId` in the spec didn't match the plugin manifest's function reference.

## Context

- API plugin (four-file architecture: app manifest + plugin manifest + OpenAPI + color/outline icons), wired in Agents Toolkit.
- The downstream API needed the **user's** identity carried through (the plugin calls a downstream API *as the user*) — an on-behalf-of (OBO) / Entra delegated scenario per the API-plugin auth tree.
- The auth had been set up as client-credentials (app-only) — the app authenticated *as itself*, which is why it could return data for the wrong user and why the per-user consent flow misbehaved.
- The Entra app registration / consent lives in `azure-cloud`; the auth-scheme verdict is a mandatory `ravenclaude-core/security-reviewer` gate (CLAUDE.md §10).

## Attempts

- Tried: re-prompting the user / clearing the Copilot session. No effect — the loop was a wrong-auth-scheme symptom, not a transient session issue.
- Tried: traversing the API-plugin auth-scheme tree in [`../knowledge/copilot-extensibility-decision-trees.md`](../knowledge/copilot-extensibility-decision-trees.md). The signals — *exposes user-specific data* + *must be scoped to the signed-in user* + *must call a downstream API as the user* — land on the **Entra delegated / on-behalf-of (OBO)** leaf, not client-credentials. The wrong leaf was the root cause.
- Tried (the moves that worked): (a) reconfigured the auth as OAuth2/Entra **delegated (OBO)** with the correct downstream scopes, declared as a **connection reference — never a literal secret** in the manifest (CLAUDE.md anti-patterns); (b) had `azure-cloud` own the app registration + admin consent and `security-reviewer` sign off on the delegated-scope design; (c) fixed the silent operation by mapping `operationId` ↔ the plugin-manifest function reference **both ways** — the names must match exactly or the operation never surfaces as an action.

## Resolution

The loop and the wrong-user data were the same bug: **app-only auth used where per-user (delegated/OBO) was required.** Switching to Entra delegated/OBO with the right downstream scopes (registration in `azure-cloud`, verdict from `security-reviewer`, secret as a reference) fixed both. The silent-operation issue was an independent `operationId`↔manifest mismatch.

**Action for the next engineer hitting this pattern:** a sign-in loop or wrong-user data on an API plugin almost always means the **auth scheme is wrong for the data sensitivity** — traverse the auth-scheme tree against the *observable signals* (public? per-user? downstream-as-user?) before wiring, don't default to client-credentials. Carry secrets as a connection reference, route the registration to `azure-cloud` and the verdict to `security-reviewer` (mandatory). If an action never fires, check the `operationId`↔plugin-manifest mapping both ways. Note the **GCC-High** caveat: API-plugin auth is not supported there `[verify-at-build]` — surface it on any sovereign-cloud question.

**Sources (retrieved 2026-06-05):**
- Copilot plugin authentication schemes (None / API key / OAuth2 / Entra app-only / Entra delegated-OBO) — Microsoft Learn API-plugin auth docs. `[verify-at-build]`.
- `operationId`↔plugin-manifest function mapping and the four-file API-plugin architecture — Microsoft Learn API-plugin / OpenAPI-for-Copilot docs. `[verify-at-build]`.
