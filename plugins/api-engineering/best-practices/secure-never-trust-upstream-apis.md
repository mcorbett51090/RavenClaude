# Never trust upstream APIs (OWASP API10)

**Status:** Absolute rule — a response from an API you call is untrusted input; the verdict escalates to security-reviewer.

**Domain:** API security / consumption

**Applies to:** `api-engineering`

---

## Why this exists

**Unsafe Consumption of APIs** (OWASP API10:2023) is the blind spot: developers harden their own endpoints against hostile clients but then trust *third-party* and upstream API responses implicitly — following their redirects, injecting their data into queries unescaped, accepting unbounded payloads, and assuming they're always available. A compromised or buggy upstream becomes your vulnerability. Data crossing a trust boundary *into* your service is input, no matter how reputable the source.

## How to apply

Treat every upstream response as untrusted: validate, bound, time out, and don't blindly follow.

```
Calling an upstream API:
  - validate the response against an expected schema before using it
  - bound it: max size, timeout, and a circuit breaker on repeated failure
  - do NOT auto-follow redirects to unvalidated hosts
  - sanitize/escape upstream data before putting it in a query, a shell, or HTML
  - use TLS; verify certificates; keep upstream credentials in a secret store
  - retry with backoff + jitter; degrade gracefully when the upstream is down
```

**Do:**
- Schema-validate and size-bound upstream responses; set aggressive timeouts and a circuit breaker.
- Pin/verify TLS; allow-list the hosts you'll call (overlaps SSRF / API7).

**Don't:**
- Pass upstream data into a query/command/template without escaping; follow arbitrary redirects; assume the upstream is always up or always honest.

## Edge cases / when the rule does NOT apply

A tightly-controlled internal upstream you own has a higher (not infinite) trust level — still bound and time it out. The SSRF control (API7) is the inbound twin: there the *client* supplies the URL you fetch; here you initiate the call but still don't trust the response.

## See also

- [`../knowledge/api-security-decision-trees.md`](../knowledge/api-security-decision-trees.md)
- [`./secure-limit-resource-consumption.md`](./secure-limit-resource-consumption.md)
- [OWASP API10:2023 — Unsafe Consumption of APIs](https://owasp.org/API-Security/editions/2023/en/0xaa-unsafe-consumption-of-apis/) — authoritative

## Provenance

Codifies OWASP API10:2023 (a 2023-edition addition). Web-verified 2026-06-04. **Verdict escalates to `ravenclaude-core/security-reviewer`.**

---

_Last reviewed: 2026-06-04 by `claude`_
