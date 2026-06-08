# Guardrails, not gates, on the happy path

**Status:** Pattern
**Domain:** Self-service infrastructure
**Applies to:** `platform-engineering-idp`

---

## Why this exists

The instinct when a self-service action *could* be misused is to add a human approver. But a human
gate on the common case re-introduces the wait the platform existed to remove, and approvers
rubber-stamp under load anyway. Guardrails — policy, quotas, and bounded defaults — make the button
safe *by construction*, so the happy path stays fast and the unsafe path is simply unavailable.

## How to apply

- Encode the safe envelope as policy (OPA/Gatekeeper, Kyverno, Conftest) checked automatically.
- Bound blast radius with quotas and sane defaults (size limits, environment scoping, naming/tagging).
- Reserve human review for actions that step *outside* the guardrails (the escape hatch).

**Do:**

- Make "the only thing the button can do" the safe thing.
- Fail closed when a request violates policy, with a clear message and the escape path.
- Keep the happy path human-free.

**Don't:**

- Put an approver on every self-service request "just in case."
- Rely on documentation/training as the only guardrail.
- Let guardrails become so tight they recreate the cage (pair with the escape hatch).

## Edge cases / when the rule does NOT apply

Irreversible, high-stakes, or regulated actions may warrant an explicit human gate — make that a
deliberate, narrow exception, logged and time-bounded, not the default.

## See also

- [`./self-service-means-no-ticket-for-the-common-case.md`](./self-service-means-no-ticket-for-the-common-case.md)
- [`./pave-the-80-keep-an-escape-hatch.md`](./pave-the-80-keep-an-escape-hatch.md)

## Provenance

Codifies policy-as-code guardrail practice (OPA/Kyverno) and the platform-engineering principle of
safe-by-default self-service over approval queues.

---

_Last reviewed: 2026-06-08 by `claude`._
