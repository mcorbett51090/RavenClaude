---
name: self-service-infrastructure
description: "Make infrastructure self-service: decide the button-vs-ticket boundary by frequency x reversibility x blast-radius, choose the mechanism (Crossplane composition vs Score spec vs portal-fronted Terraform/OpenTofu module), and guardrail the button with policy (OPA/Kyverno/Conftest), quotas, and bounded defaults so there's no human gate on the happy path."
---

# Self-Service Infrastructure

**Purpose:** turn common infra requests into safe self-service so the platform removes a wait instead
of relaying a ticket.

## The boundary (button vs ticket)

Traverse the self-service-boundary tree in
[`../../knowledge/platform-engineering-decision-trees.md`](../../knowledge/platform-engineering-decision-trees.md):

- **Rare / one-off** -> keep it a ticket; automation isn't worth it yet.
- **Frequent + easily reversible + small blast radius** -> self-service button with sane defaults.
- **Frequent + large blast radius** -> self-service **with guardrails** (policy + quotas + bounded
  defaults), *not* a human gate on the common case.

A "self-service" form that opens a ticket for the common case is a service desk in disguise.

## Choose the mechanism

| Mechanism | Use when |
|---|---|
| **Crossplane** composition | k8s-native estate; you want a k8s API + control plane for infra. |
| **Score** spec | You want the workload spec decoupled from the platform implementation. |
| **Portal-fronted Terraform/OpenTofu module** | You already have good IaC modules; front them with a template/portal action. |
| **Kratix** promises | You're building a platform-as-a-product with promise-based marketplace semantics. |

The IaC module itself is authored by `terraform-iac`; the cluster surface by
`cloud-native-kubernetes`. This skill designs the *self-service wrapper + guardrails*.

## Guardrails, not gates

- Policy: OPA/Gatekeeper, Kyverno, or Conftest enforce the safe envelope.
- Quotas + bounded defaults limit blast radius.
- The happy path has **no human in the loop**; exceptions take the escape hatch.

## Anti-patterns

- "Self-service" that still opens a ticket for the common case.
- A button with no guardrails (unbounded blast radius).
- Re-authoring IaC modules here instead of routing to `terraform-iac`.

## Output

A self-service infra design: the boundary call (with the tree leaf), the mechanism, the request ->
provision -> expose flow, and the guardrails. A security verdict on a default -> `ravenclaude-core/security-reviewer`.
