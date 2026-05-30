# Mark write/transactional actions consequential (require confirmation) and attest function behavior with `security_info`

**Status:** Absolute rule — an unconfirmed write action lets Copilot mutate a backend without the user agreeing; the confirmation flag and the behavior attestation are the guardrails.

**Domain:** Grounding / API-plugin response & action safety

**Applies to:** `microsoft-365-copilot`

> **Security-sensitive.** Whether an action's consequence framing and `security_info` attestation are *sufficient* is a verdict for **`ravenclaude-core/security-reviewer`** (mandatory). This plugin sets the posture; core rules on it.

---

## Why this exists

An API plugin can do anything the API can — including create, update, and delete. Copilot decides when to invoke an action from its description, which means a write action can fire as a side effect of a natural-language prompt. Two manifest mechanisms keep that safe. **Consequential-action confirmation**: an action that changes state should prompt the user to confirm before it executes. By default OpenAPI **GET** operations are treated as non-consequential (read-only, no confirmation) and non-GET operations as consequential — but you control this with the confirmation object's `isNonConsequential` flag, and v2.4 specifically refined `isNonConsequential` behavior for GET actions. Mis-flagging a state-changing operation as non-consequential removes the user's chance to stop it. **`security_info`** (plugin-manifest v2.2+) lets you *attest* to a function's behavior (e.g. that it only reads, or what data it touches) so the orchestrator and reviewers can assess the risk of calling it. Together they make the difference between "Copilot answered a question" and "Copilot silently deleted a record". The verdict that the gating is adequate is core's.

## How to apply

Treat every state-changing operation as consequential (confirmation required) unless you have a reviewed reason otherwise. Keep GETs non-consequential only when they are genuinely side-effect-free. Attest behavior with `security_info`.

```jsonc
{
  "schema_version": "v2.4",
  "functions": [
    {
      "name": "deleteTicket",
      "description": "Permanently deletes a support ticket. Destructive.",
      "capabilities": {
        "confirmation": {
          "type": "AdaptiveCard",
          "title": "Delete ticket?",
          "body": "This permanently deletes ticket {id}. This can't be undone."
        }
      },
      // attest the function's behavior so the orchestrator/reviewer can assess risk (v2.2+)
      "security_info": { "data_handling": ["write", "delete"] }
    },
    {
      "name": "getTicketById",
      "description": "Reads one ticket by ID. Side-effect free.",
      "capabilities": { "confirmation": { "isNonConsequential": true } }  // GET, safe to skip
    }
  ]
}
```

**Do:**
- Require **confirmation** on every create/update/delete (state-changing) action.
- Leave `isNonConsequential: true` only for genuinely side-effect-free reads (GETs) — and re-check that under v2.4's refined GET behavior.
- Populate **`security_info`** to attest what each function does/touches (v2.2+).
- Route the consequence-framing + attestation to `ravenclaude-core/security-reviewer` for the verdict.

**Don't:**
- Flag a state-changing operation as non-consequential to skip the confirmation prompt.
- Assume a GET is always safe — a GET with side effects (e.g. a "send" disguised as a fetch) is consequential.
- Ship destructive actions without a clear, model-readable description of the consequence.

## Edge cases / when the rule does NOT apply

A read-only API plugin (all GETs, no mutations) may legitimately run without confirmations — but confirm that the GETs are truly side-effect-free first. The exact `confirmation` / `security_info` field shapes and the v2.4 GET-confirmation behavior are `[verify-at-build]`; re-confirm against the current plugin-manifest schema. For an **MCP**-runtime plugin, consequence handling is governed at the tool/server level and the server's admin consent (Agent Registry) is the additional gate.

## See also

- [`./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md`](./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md) — the manifest these flags live in
- [`./apiplugin-choose-and-route-auth-never-embed-secrets.md`](./apiplugin-choose-and-route-auth-never-embed-secrets.md) — the auth that unlocks the write actions you're gating
- [`../knowledge/api-plugins-and-auth-2026.md`](../knowledge/api-plugins-and-auth-2026.md) · [`../agents/api-plugin-engineer.md`](../agents/api-plugin-engineer.md)
- [Plugin manifest schema 2.4](https://learn.microsoft.com/microsoft-365/copilot/extensibility/plugin-manifest-2.4) (GET `isNonConsequential` change) · [schema 2.2](https://learn.microsoft.com/microsoft-365/copilot/extensibility/plugin-manifest-2.2) (`security_info`)

## Provenance

Grounded in the Microsoft Learn plugin-manifest schema pages: v2.2's `security_info` ("attest to the behavior of the plugin in order to assess the risks of calling the function") and v2.4's "Updated Confirmation object `isNonConsequential` property behavior for OpenAPI GET actions", retrieved 2026-05-30. The sufficiency verdict escalates to `ravenclaude-core/security-reviewer` per [`../CLAUDE.md`](../CLAUDE.md) §10. Field shapes are `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
