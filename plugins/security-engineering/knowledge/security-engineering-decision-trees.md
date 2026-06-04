# Security Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before triaging a finding or handling a secret. Remember: this team proposes; security-reviewer decides.

## Decision Tree: Vulnerability triage priority

Rank by exploitability and blast radius, not CVSS alone — then route the verdict.

```mermaid
graph TD
  A[A finding] --> B{Reachable / exploitable in our usage?}
  B -- No --> C[Low priority: track, patch on cadence]
  B -- Yes --> D{Exposed to untrusted input / internet?}
  D -- No, internal only --> E[Medium: fix in normal cycle]
  D -- Yes --> F{Auth required to reach?}
  F -- Yes --> G[High: prioritize this sprint]
  F -- No, unauthenticated --> H[Critical: stop-and-fix; route verdict to security-reviewer]
  C --> I[Fix the CLASS + add a lint/scan rule]
  E --> I
  G --> I
  H --> I
```

_Every ship/no-ship call routes to `ravenclaude-core/security-reviewer`._

## Decision Tree: A secret was found — what now?

A committed secret is compromised. Deleting the commit is not remediation.

```mermaid
graph TD
  A[Secret detected] --> B{In source control history or a clone/fork?}
  B -- Yes --> C[Treat as COMPROMISED: rotate/revoke NOW]
  B -- No, only working tree --> D{Was it ever pushed/shared?}
  D -- Yes --> C
  D -- No --> E[Remove + add to vault + scanner rule]
  C --> F[Rotate -> vault the new one -> short-lived/OIDC if possible]
  F --> G[Add detection so it can't recur]
  E --> G
```


## Decision Tree: Where does this security control belong (shift-left placement)?

Place the control at the earliest, cheapest stage that can actually catch the class — earlier is cheaper, but the verdict still routes.

```mermaid
graph TD
  A[A control to add] --> B{Is it an architectural / trust-boundary risk?}
  B -- Yes --> C[Design time: threat model; change the design, not bolt on]
  B -- No --> D{Detectable by static analysis of the diff?}
  D -- Yes --> E[CI gate: SAST/SCA/secret-scan on the PR, comment a fix]
  D -- No --> F{Detectable only at runtime / against a deployment?}
  F -- Yes --> G[DAST / runtime guardrail / policy-as-code at deploy]
  F -- No --> H[Last resort: pre-launch pen-test - expensive + late]
  C --> I[Route any ship/no-ship verdict to security-reviewer]
  E --> I
  G --> I
```

_Shift the detection left; never shift the verdict. The earlier you catch it, the cheaper the fix._

## Decision Tree: Auth-vs-authz failure triage

"Access denied" and "access wrongly granted" are different bugs with different blast radii — separate them before you fix.

```mermaid
graph TD
  A[An access-control failure] --> B{Did the system establish WHO the caller is?}
  B -- No, identity unproven --> C[Authentication failure]
  C --> D{Failing OPEN - unauthenticated reaches protected resource?}
  D -- Yes --> E[Critical: stop-and-fix, route to security-reviewer]
  D -- No, failing closed --> F[Fix the auth flow; lower urgency]
  B -- Yes, identity known --> G[Authorization failure]
  G --> H{Can a user reach data/actions of ANOTHER tenant/user?}
  H -- Yes --> I[Critical: broken object/function-level authz - escalate]
  H -- No, over-broad within own scope --> J[Tighten to least privilege]
```

_Authn = are you who you claim? Authz = are you allowed? A failing-open authn check and a cross-tenant authz hole are both critical; route the verdict._

## Decision Tree: Patch now vs schedule (exploitability gate)

Reachability and exposure decide urgency, not the CVSS number on the advisory.

```mermaid
graph TD
  A[A new CVE in a dependency] --> B{Is the vulnerable code reachable in our usage?}
  B -- No --> C[Schedule on normal cadence; record the why]
  B -- Yes --> D{Exposed to untrusted/internet input?}
  D -- No, internal only --> E{Known exploited in the wild / public PoC?}
  E -- Yes --> F[Patch this sprint]
  E -- No --> E2[Normal cycle, prioritized]
  D -- Yes --> G{Unauthenticated to trigger?}
  G -- Yes --> H[Patch now / emergency change; route verdict]
  G -- No --> F
```

_A 9.8 in an unreachable path waits; a 6.5 unauthenticated and exploited-in-the-wild does not. Verdict to security-reviewer._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| OWASP Top 10 (web) | 2021 edition current | 2025 refresh tracked; verify at build |
| SAST/SCA in CI | mature | Tune for signal; reachability where supported |
| Secret scanning | GitHub/GitLab native + tools | Pre-commit + CI + history scan |
| SLSA | v1.0 | Build levels; verify provenance on consume |
| CSPM | mature across clouds | Misconfig is #1 breach cause |
| Policy-as-code (OPA/Conftest, cloud policy) | GA | Preventive > detective; wire via terraform-iac |
