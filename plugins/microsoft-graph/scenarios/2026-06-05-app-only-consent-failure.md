---
scenario_id: 2026-06-05-app-only-consent-failure
contributed_at: 2026-06-05
plugin: microsoft-graph
product: entra-id
product_version: "v1.0"
scope: likely-general
tags: [consent, application-permission, admin-consent, delegated, 403]
confidence: high
reviewed: false
---

## Problem

A background service that read mail from a set of shared mailboxes worked perfectly in the developer's own tenant and failed with `403 Forbidden` / `Access is denied` the moment it was deployed to the customer's tenant. The developer was convinced the permission was simply "missing" and kept asking the customer's admin to "grant Mail.Read again" — which the admin did, repeatedly, with no change. The real issue was a permission *type* and *consent* mismatch, not a missing grant.

## Constraints context

- Daemon service, no signed-in user, client-credentials flow — so it **must** use **application** permissions, never delegated.
- The app registration had `Mail.Read` configured as a **delegated** permission (added during interactive dev testing where the developer *was* the signed-in user). Delegated permissions require a user in the token; a client-credentials token has no user, so the delegated grant is inert.
- In the dev tenant it "worked" only because the developer had been testing interactively with their own sign-in — a different code path than the deployed daemon.

## Attempts

- Tried: re-granting `Mail.Read` (delegated) as admin, several times. Failed — admin-consenting a *delegated* permission does nothing for a token that carries no user. The grant existed; it just didn't apply to the app-only flow.
- Tried: adding `Mail.Read` as an **application** permission. This is the right type, but the app still 403'd until the next step — application permissions **always require admin consent**, and adding the permission in the manifest is not the same as consenting to it.
- Tried (worked): (1) add `Mail.Read` as an **application** permission; (2) have a tenant admin grant **admin consent** for it (the "Grant admin consent for <tenant>" button, or the admin-consent URL flow); (3) for mail specifically, scope the app to only the intended mailboxes via an **application access policy** (`New-ApplicationAccessPolicy`) so the app-only `Mail.Read` doesn't read *every* mailbox in the tenant — least-privilege, since application `Mail.Read` is otherwise tenant-wide.

## Resolution

Two distinct facts were conflated: **permission type** (delegated vs application) and **consent** (who granted it). A daemon needs *application* permissions; *all* application permissions need *admin* consent; and admin-consenting the wrong *type* (delegated) accomplishes nothing for an app-only token. The 403 was the correct, honest signal that the effective app-only permission set was empty.

This is a security-review touchpoint: an application `Mail.Read` is tenant-wide read of all mail by default — the application-access-policy scoping is the least-privilege control and the kind of decision that escalates to `ravenclaude-core/security-reviewer` (CLAUDE.md §3 #1).

**Action for the next engineer:** when a daemon 403s but "the permission is granted," verify the permission is **application** type (not delegated) *and* that **admin consent** was granted *for the application permission specifically*. Then ask whether the app-only scope is tenant-wide and needs a resource-scoping policy. Traverse the delegated-vs-application and the user-vs-admin-consent trees before touching the app registration.

**Sources (retrieved 2026-06-05):**
- Microsoft Graph permissions / auth concepts (delegated vs application) — https://learn.microsoft.com/graph/auth/auth-concepts
- Limiting application permissions to specific mailboxes (application access policy) — https://learn.microsoft.com/graph/auth-limit-mailbox-access

Permission names and per-resource availability are volatile — `[verify-at-use]`. Cross-reference: [`../best-practices/identity-delegated-vs-application-is-a-design-choice.md`](../best-practices/identity-delegated-vs-application-is-a-design-choice.md), [`../best-practices/identity-admin-consent-and-the-consent-framework.md`](../best-practices/identity-admin-consent-and-the-consent-framework.md), [`../best-practices/identity-least-privilege-permission-selection.md`](../best-practices/identity-least-privilege-permission-selection.md), and [`identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md).
