# Error Messages Are Documentation — Write Them for the Fixer

**Status:** Pattern
**Domain:** Technical Writing — Developer experience / API docs
**Applies to:** `technical-writing-docs`

---

## Why this exists

A developer hits an error at 11 PM before a deadline. The error message they see is often the only documentation they will read. An error that says `Error: invalid input` offers nothing to act on. An error that says `Invalid API key format: expected 32-character hex string, got 15 characters. See docs/auth.md for key provisioning` gives the fixer the cause, the expected state, the actual state, and a pointer to the resolution. Error messages written as user-facing documentation — specific, actionable, with a pointer to more context — dramatically reduce support burden and developer frustration.

## How to apply

**Error message anatomy (the four parts):**

```
[What went wrong] + [What was expected] + [What was received/found] + [How to fix it or where to look]
```

**Examples:**

| Before | After |
|---|---|
| `Authentication failed` | `Authentication failed: the provided API key has expired. Rotate your key at https://dashboard.example.com/keys.` |
| `Invalid parameter` | `Invalid parameter: 'timeout' must be a positive integer (received: -1).` |
| `Not found` | `Resource not found: collection 'users-prod' does not exist in workspace 'acme'. Check the workspace ID or create the collection first.` |

**For HTTP APIs — minimum error response payload:**

```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "API key format invalid: expected 32-character hex string.",
    "docs_url": "https://docs.example.com/auth#api-keys",
    "request_id": "req_8fa3c2b1"
  }
}
```

**Do:**
- Include a `docs_url` or link in the error payload for all recoverable errors.
- Use a machine-readable `code` field in API errors so clients can programmatically distinguish error types.
- Include the `request_id` so the user can reference it in a support ticket.

**Don't:**
- Expose internal stack traces or implementation details in error messages returned to end users.
- Use the same generic message for fundamentally different failure modes.
- Write error messages in the imperative past tense ("failed to authenticate") — write them to address the reader ("your API key has expired").

## Edge cases / when the rule does NOT apply

- **Security-sensitive errors** (authentication, authorization): balance specificity against enumeration risk. "Invalid credentials" is intentionally vague on login to prevent username enumeration; but a *developer* hitting an API-key format error in a developer context should still get specificity.
- **Internal / server-side errors (500)**: present a generic "unexpected error" + `request_id` + support contact to the end user; log the full detail internally.

## See also

- [`../agents/api-reference-writer.md`](../agents/api-reference-writer.md) — owns error documentation in the API reference
- [`./document-the-unhappy-path.md`](./document-the-unhappy-path.md) — the parent rule: the unhappy path is where the reader hits the docs

## Provenance

Codifies house opinion #6 ("Show the unhappy path — errors, edge cases, and limits") applied to the error message surface. Error message design guidance from Kate Voss (Write the Docs, "Error Messages Are Documentation") and Stripe API documentation standards. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
