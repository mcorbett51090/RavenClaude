# Policy as code prevents misconfigurations — detection alone is too late

**Status:** Pattern
**Domain:** Cloud security / policy enforcement
**Applies to:** `security-engineering`

---

## Why this exists

CSPM tools detect cloud misconfigurations after they've been deployed. Detection is valuable, but the misconfiguration is already live and potentially exploitable from the moment it's created until the alert is acted on. Policy as code (OPA/Conftest, AWS SCPs, Azure Policy, GCP Organization Policy) enforces configuration guardrails before deployment — the misconfigured resource never gets created. Prevention is structurally cheaper and safer than detection: there's no exposure window.

## How to apply

Wire policy checks into the infrastructure pipeline (terraform plan → policy check → terraform apply). Use admission controllers in Kubernetes (OPA/Gatekeeper, Kyverno) to enforce pod security at the API server level.

```rego
# OPA/Conftest policy: deny S3 buckets without server-side encryption
package main

deny[msg] {
  input.resource.aws_s3_bucket[bucket].server_side_encryption_configuration == null
  msg := sprintf("S3 bucket '%s' must have server-side encryption enabled", [bucket])
}

deny[msg] {
  input.resource.aws_s3_bucket_public_access_block[block].block_public_acls == false
  msg := sprintf("S3 bucket '%s' must block public ACLs", [block])
}
```

```yaml
# CI: Conftest check in Terraform pipeline
- name: Validate Terraform plan against policy
  run: |
    terraform plan -out=tfplan.binary
    terraform show -json tfplan.binary > tfplan.json
    conftest test tfplan.json --policy policies/
    # Fails if any deny rule fires — blocks terraform apply
```

```yaml
# Kubernetes: Kyverno ClusterPolicy — deny privileged containers
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-containers
spec:
  validationFailureAction: Enforce    # deny, not audit
  rules:
    - name: check-privileged
      match:
        resources:
          kinds: [Pod]
      validate:
        message: "Privileged containers are not allowed"
        pattern:
          spec:
            containers:
              - securityContext:
                  privileged: "false"
```

**Do:**
- Start policies in `audit` mode (log violations, don't block) to build the violation baseline before switching to `enforce`.
- Write policies for the top misconfigurations in your CSPM findings — preventive policy for the most common findings.
- Store policies in the repo alongside the infrastructure code — they're reviewed in the same PR.

**Don't:**
- Remove a failing policy check to unblock a deploy — escalate the exception and document it.
- Run policy checks only in CI; wire them as admission controllers in Kubernetes and as AWS SCPs so they also catch out-of-band changes.
- Let the policy library go stale — review and update when new misconfig classes emerge in CSPM findings.

## Edge cases / when the rule does NOT apply

Legacy resources that predate the policy engine may require exemptions during migration. Use a time-bounded `exceptions` block in OPA/Conftest with a review date, and track the migration to remove the exemption.

## See also

- [`../agents/cloud-security-engineer.md`](../agents/cloud-security-engineer.md) — owns CSPM posture and policy-as-code enforcement.
- [`./defense-in-depth-without-theater.md`](./defense-in-depth-without-theater.md) — preventive controls are the highest-value layer in the defense-in-depth stack.

## Provenance

Codifies the OPA/Conftest CI integration pattern (conftest.dev) and the Kyverno admission controller documentation (kyverno.io), grounded in the NIST SP 800-190 Container Security Guide.

---

_Last reviewed: 2026-06-05 by `claude`_
