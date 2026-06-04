---
description: Review an existing API spec or endpoint against the house design-review checklist — paradigm/contract, resource modeling, HTTP semantics, RFC 9457 errors, cursor pagination, idempotency/concurrency, the OWASP API security pass, and versioning/lifecycle.
argument-hint: "[path to openapi.yaml, or the endpoint/spec to review]"
---

# Review an API design

You are running `/api-engineering:review-api-design`. Review the spec/endpoint the user pointed at (`$ARGUMENTS`) against this plugin's [`../templates/api-design-review-checklist.md`](../templates/api-design-review-checklist.md).

## When to use this

A contract is up for review before it merges or ships. For the automated style gate, also run `/api-engineering:lint-api-spec`. For a deep security pass, `/api-engineering:harden-api`.

## Steps

1. **Load the spec** and run through the checklist sections in order: paradigm & contract, resource/operation modeling, cross-cutting build conventions, security, versioning/lifecycle, governance/testing.
2. **Flag each violation against a named rule** in [`../best-practices/`](../best-practices/) — don't hand-wave. RPC verbs in URLs, bespoke error shapes, offset pagination, a missing `Idempotency-Key` on a money POST, an unauthenticated operation, an unbounded page size, a breaking change with no version bump.
3. **Run the OWASP API 2023 pass** (object/function/property authorization, auth, consumption, misconfig, SSRF, inventory, unsafe consumption) — see the control map in [`../knowledge/api-security-decision-trees.md`](../knowledge/api-security-decision-trees.md).
4. **Produce a verdict** per the checklist's three lanes (design / security / governance), with the specific fixes and the routing for anything that needs a security sign-off.

## Guardrails

- Cite the rule file for every finding so the author can act without re-deriving it.
- Distinguish **must-fix** (absolute-rule violations, security gaps) from **should-fix** (patterns/deviations with a reason).
- The security verdict is not yours to issue — route it to `ravenclaude-core/security-reviewer` with the residual risk stated.
- Volatile facts (spec versions, OWASP edition, IETF draft status) carry a retrieval date / `[verify-at-build]`.
