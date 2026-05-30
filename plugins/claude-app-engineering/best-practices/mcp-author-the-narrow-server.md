# Author the narrow MCP server — fewest tools, idempotent, auth every request

**Status:** Pattern — strong default; a sprawling server with 40 thin tools, non-idempotent effects, and trust-the-client auth is the failure shape.

**Domain:** MCP

**Applies to:** `claude-app-engineering`

---

## Why this exists

An MCP server is a long-lived attack surface and a tool menu the model has to reason over — both get worse as the server grows. Too many tools dilutes the model's choice (it picks the wrong one, or calls three where one would do) and bloats the cached tool array; non-idempotent tools turn an agent's natural retry-on-timeout into a double charge / duplicate record; and a server that trusts the client for auth is a server anyone who reaches it can drive. The discipline for authoring (once [`mcp-vs-in-process-tool.md`](./mcp-vs-in-process-tool.md) said "yes, a server"): expose the **fewest, highest-leverage tools**, make every state-changing tool **idempotent**, **authenticate every request**, honor the client's **roots**, and treat all tool arguments as **untrusted**. A narrow, idempotent, authenticated server is both safer and easier for the model to use well.

## How to apply

Expose few tools with the contract discipline, make writes idempotent with a client-supplied key, and authenticate + scope every request.

```python
# Fewest tools: one capable `search_orders` beats search_by_id + by_date + by_status + ...
@server.tool()
async def refund_order(order_id: str, amount_cents: int, idempotency_key: str) -> dict:
    # AuthN every request; AuthZ the action against the *caller's* scope, not the client's claim.
    principal = authenticate(ctx.request)          # reject if unauthenticated
    authorize(principal, "refund", order_id)        # least privilege
    # Idempotent: a retried call with the same key returns the first result, no double refund.
    if (prior := seen(idempotency_key)):
        return prior
    if not valid_uuid(order_id):                    # tool args are UNTRUSTED — validate/parameterize
        return {"error": "order_id must be a UUID; got an unrecognized value."}
    return remember(idempotency_key, _refund(order_id, amount_cents))
```

**Do:**
- Expose the **fewest tools that cover the job** — prefer one parameterized tool over many near-duplicates; each tool's description is still the prompt ([`tools-design-as-a-contract.md`](./tools-design-as-a-contract.md)).
- Make every **state-changing** tool **idempotent** (client-supplied idempotency key, or natural idempotency) so an agent's retry can't double-apply an effect.
- **Authenticate every request** and authorize the *action* against the caller's scope; honor the client's **roots** (never read outside the granted scope).
- Treat **all tool arguments as untrusted** — validate, parameterize, never string-interpolate into a shell/SQL ([`untrusted-content-stays-untrusted.md`](./untrusted-content-stays-untrusted.md)); route the auth + sandboxing design to `ravenclaude-core/security-reviewer`.

**Don't:**
- Ship 40 thin tools because "more capability" — it dilutes tool-choice accuracy and bloats the cached tool array.
- Leave a write tool non-idempotent — the agent loop *will* retry on a timeout, and a duplicate charge/record is the result.
- Trust the client's identity claim, read outside the client's roots, or put a secret in the server's source ([`cost-and-secrets-observability.md`](./cost-and-secrets-observability.md) covers the secret-handling seam; auth verdict is core).

## Edge cases / when the rule does NOT apply

- **Genuinely distinct capabilities** justify more tools — "fewest" means no *near-duplicates*, not artificially merging unrelated functions into one overloaded tool.
- **Read-only tools** don't need idempotency keys (they're naturally idempotent) — the rule targets state-changing effects.
- **Local stdio servers** launched by the Agent SDK as a subprocess still validate inputs and scope filesystem access, but the network-auth posture differs from a remote Streamable-HTTP server ([`../knowledge/mcp-server-authoring.md`](../knowledge/mcp-server-authoring.md)).
- The full **auth / sandboxing review** is not this rule — it escalates to `ravenclaude-core/security-reviewer` (mandatory). This rule is the authoring posture that review checks against.

## See also

- [`../knowledge/mcp-server-authoring.md`](../knowledge/mcp-server-authoring.md) — capabilities, transports, security posture, MCP-vs-tool
- [`./mcp-vs-in-process-tool.md`](./mcp-vs-in-process-tool.md) — the decision that precedes authoring a server
- [`./tools-design-as-a-contract.md`](./tools-design-as-a-contract.md) — per-tool contract discipline the server's tools must follow
- [`../agents/mcp-and-server-tools-engineer.md`](../agents/mcp-and-server-tools-engineer.md) — owns MCP server authoring

## Provenance

Codifies the MCP-authoring posture from [`../knowledge/mcp-server-authoring.md`](../knowledge/mcp-server-authoring.md) (security section: authenticate every request, honor roots, validate inputs, untrusted args) plus house opinions #7 (untrusted content) and #9 (idempotency for non-idempotent effects) in [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in modelcontextprotocol.io + Agent SDK MCP docs, retrieved 2026-05-28. Auth/sandboxing verdicts escalate to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-05-30 by `claude`_
