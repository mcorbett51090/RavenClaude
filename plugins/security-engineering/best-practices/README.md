# security-engineering — best-practice docs

Named, citable rules for the `security-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_22 rules._

| Doc | Status | Use when |
|---|---|---|
| [`a-committed-secret-is-compromised.md`](./a-committed-secret-is-compromised.md) | Absolute rule | A secret is found anywhere in version control |
| [`assume-breach-and-design-for-it.md`](./assume-breach-and-design-for-it.md) | Pattern | Designing any new system or feature |
| [`threat-model-at-design-time.md`](./threat-model-at-design-time.md) | Absolute rule | Starting the design of a significant feature |
| [`triage-by-exploitability-not-cvss.md`](./triage-by-exploitability-not-cvss.md) | Absolute rule | Triaging any security finding or CVE |
| [`pin-verify-and-bound-the-supply-chain.md`](./pin-verify-and-bound-the-supply-chain.md) | Absolute rule | Adding or updating a dependency |
| [`security-is-a-paved-road-not-a-gate.md`](./security-is-a-paved-road-not-a-gate.md) | Pattern | Designing the developer security experience |
| [`shift-left-find-it-in-design-and-ci.md`](./shift-left-find-it-in-design-and-ci.md) | Pattern | Placing security controls in the delivery pipeline |
| [`least-privilege-by-default.md`](./least-privilege-by-default.md) | Absolute rule | Granting any permission, role, or access |
| [`propose-controls-route-the-verdict.md`](./propose-controls-route-the-verdict.md) | Absolute rule | Reaching a ship/no-ship security decision |
| [`enumerate-before-you-assess.md`](./enumerate-before-you-assess.md) | Absolute rule | Starting any security assessment |
| [`make-the-secure-path-the-default.md`](./make-the-secure-path-the-default.md) | Pattern | Designing libraries, frameworks, or internal tooling |
| [`defense-in-depth-without-theater.md`](./defense-in-depth-without-theater.md) | Pattern | Evaluating a layered security architecture |
| [`rotate-credentials-on-a-schedule.md`](./rotate-credentials-on-a-schedule.md) | Absolute rule | Managing any stored credential |
| [`dast-in-staging-not-prod.md`](./dast-in-staging-not-prod.md) | Absolute rule | Setting up DAST in the CI/CD pipeline |
| [`sbom-is-the-inventory.md`](./sbom-is-the-inventory.md) | Absolute rule | Building or auditing any production artifact |
| [`sast-tune-for-signal.md`](./sast-tune-for-signal.md) | Pattern | Configuring or reviewing a SAST tool |
| [`access-review-on-a-cadence.md`](./access-review-on-a-cadence.md) | Absolute rule | Managing IAM, service accounts, or access grants |
| [`container-image-scanning-in-ci.md`](./container-image-scanning-in-ci.md) | Absolute rule | Adding container image builds to CI |
| [`threat-model-updates-follow-design-changes.md`](./threat-model-updates-follow-design-changes.md) | Absolute rule | Reviewing an architecture or design PR |
| [`dependency-updates-are-security-work.md`](./dependency-updates-are-security-work.md) | Pattern | Triaging dependency update PRs from Dependabot or Renovate |
| [`policy-as-code-prevents-not-detects.md`](./policy-as-code-prevents-not-detects.md) | Pattern | Responding to recurring CSPM misconfiguration findings |
| [`incident-response-includes-security-triage.md`](./incident-response-includes-security-triage.md) | Pattern | Running or reviewing any production incident |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
