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


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| OWASP Top 10 (web) | 2021 edition current | 2025 refresh tracked; verify at build |
| SAST/SCA in CI | mature | Tune for signal; reachability where supported |
| Secret scanning | GitHub/GitLab native + tools | Pre-commit + CI + history scan |
| SLSA | v1.0 | Build levels; verify provenance on consume |
| CSPM | mature across clouds | Misconfig is #1 breach cause |
| Policy-as-code (OPA/Conftest, cloud policy) | GA | Preventive > detective; wire via terraform-iac |
