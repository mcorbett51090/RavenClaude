---
description: Audit an app's Microsoft Graph permission set for least-privilege — flag .ReadWrite.All/.All scopes a narrower or resource-scoped one would replace, mislabeled delegated-vs-application choices, unused scopes, and high-trust act-as-other-identity grants.
argument-hint: "[the app or scope list, e.g. 'these 8 application permissions on our sync daemon']"
---

# Audit Graph permissions

You are running `/microsoft-graph:audit-graph-permissions`. Review the Graph permission set for what the user described (`$ARGUMENTS`), following this plugin's `graph-identity-engineer` discipline — every scope is attack surface, and the verdict is a security control.

## When to use this

An existing app's consent/scope list needs tightening before a security review or admin consent. If the app is being designed fresh, run `/microsoft-graph:design-graph-auth` first. The verdict escalates to `ravenclaude-core/security-reviewer`.

## Steps

1. **For each permission, climb the ladder to the smallest scope that covers the actual operation** — flag any `.ReadWrite.All` where `.Read` would do, and any umbrella (`Directory.Read.All`) where a resource-specific one (`User.Read.All`) suffices (`identity-least-privilege-permission-selection.md`).
2. **Verify the true least-privilege permission against the permissions reference** — don't assume the obvious-named scope is narrowest (same file).
3. **Check delegated vs application is correct per scope** — is there a signed-in user for that operation? An application permission where delegated was right grants tenant-wide reach with no user ceiling; the reverse breaks an unattended job (`identity-delegated-vs-application-is-a-design-choice.md`).
4. **Find unused scopes** — any permission no current code path exercises should be dropped (`identity-least-privilege-permission-selection.md`).
5. **Flag high-trust scopes loudly** — `Application.ReadWrite.All`, `AppRoleAssignment.ReadWrite.All`, `RoleManagement.*` let the app act as other identities and deserve explicit justification (same file).
6. **Check the credential and consent posture** — production app-only access on a certificate/managed identity, not a client secret (`auth-certificates-not-secrets-in-production.md`); application permissions are admin-consent-only.

## Guardrails

- A genuinely broad admin tool may legitimately need a `.ReadWrite.All` scope — that breadth is the thing you document and route to review, not silently approve.
- Permission names and least-privilege mappings are volatile — carry a retrieval date and tag `[verify-at-build]`.
- This is advisory: produce the tightened scope list + one-line justification per scope, and escalate the verdict to `ravenclaude-core/security-reviewer` (mandatory) — this plugin supplies the selection, core owns the verdict.
