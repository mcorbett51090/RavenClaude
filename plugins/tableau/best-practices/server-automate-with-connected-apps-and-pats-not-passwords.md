# Authenticate automation with Connected Apps / PATs, never an admin password in a script

**Status:** Absolute rule — interactive admin credentials in a promotion/automation script are a secret-leak and a single point of failure. Headless auth uses Connected Apps or Personal Access Tokens.

**Domain:** Server / ALM / automation auth

**Applies to:** `tableau`

---

## Why this exists

A promotion pipeline or scheduled REST job that signs in with a human admin's username and password embeds a long-lived, high-privilege secret in a script (or a CI variable), ties the automation to one person's account (it breaks when they change their password or leave), and bypasses MFA. The supported headless paths exist precisely to avoid this: a **Personal Access Token (PAT)** is a named, revocable, scoped credential you can rotate without touching the account password; a **Connected App** issues short-lived JWTs for app-to-Tableau auth. Either lets you authenticate CI/CD and scheduled jobs without a human password in the loop, and either can be revoked the instant it leaks — which a password shared across five scripts cannot. The rule is simple: no `password` field in any automation sign-in.

## How to apply

Sign in with a PAT (named, revocable) for scripted/REST automation; use a Connected App JWT for app-to-Tableau.

```bash
# DO — PAT sign-in (no password anywhere). Token name + secret come from a vault/CI secret store.
curl -s -X POST "$SERVER/api/3.x/auth/signin" \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"credentials":{
        "personalAccessTokenName":"ci-promote",
        "personalAccessTokenSecret":"'"$TABLEAU_PAT_SECRET"'",
        "site":{"contentUrl":"prod"}}}' | jq -r .credentials.token

# DON'T — password in the script (long-lived, person-bound, MFA-bypassing, unrevocable-without-reset):
#   -d '{"credentials":{"name":"admin@corp.com","password":"'"$ADMIN_PW"'", ...}}'
```

**Do:**
- Use a **PAT** for scripted REST / `tabcmd` automation — named, scoped, revocable, rotatable.
- Use a **Connected App** JWT for app-to-Tableau (embedding, app-driven REST) auth.
- Store the PAT secret / Connected App secret in a **vault or CI secret store**, injected at runtime.
- Give automation its own **service identity** (not a person's account) with least-privilege site role.

**Don't:**
- Put an admin username + password in a promotion script or CI variable.
- Share one PAT across many unrelated jobs — you can't revoke one without breaking all.
- Let a PAT outlive its purpose — PATs expire/idle out `[verify-at-build]`; rotate and prune.

## Edge cases / when the rule does NOT apply

- **PAT availability/expiry policy** is site-configured and differs Cloud vs Server `[verify-at-build]` — confirm PATs are enabled and check the expiry policy before designing around them.
- **One-time interactive run** — a human running a one-off command interactively (with MFA) is fine; the rule targets *unattended* automation.
- **Connected App vs PAT** — embedding/app-to-Tableau leans Connected App JWT; pure CI publish/promote leans PAT. Pick per the auth context, but never a password for either.

## See also

- [`./server-promote-content-dont-rebuild.md`](./server-promote-content-dont-rebuild.md) — the REST promotion that consumes this auth
- [`./embed-connected-apps-jwt-not-trusted-tickets.md`](./embed-connected-apps-jwt-not-trusted-tickets.md) — the Connected App JWT path for embedding
- [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md) — `## Decision Tree: Content promotion` (auth is the `requires:` on the REST leaf)
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule
- Tableau Help, "Personal Access Tokens" + "Connected Apps" `[verify-at-build]`

## Provenance

Extends the `tableau-admin` discipline #3 ("Promote, don't rebuild" — promotion auth) and #5 (Connected Apps). Grounded in Tableau PAT + Connected App auth — re-verify PAT expiry/idle policy and Cloud-vs-Server availability against current Tableau Help. Secret-handling verdicts escalate to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-05-30 by `claude`_
