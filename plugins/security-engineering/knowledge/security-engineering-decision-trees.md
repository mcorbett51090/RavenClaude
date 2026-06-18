# Security Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-18 (OWASP Top 10 → 2025 edition)._

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
| OWASP Top 10 (web) | **2025 edition current** (verify Final vs RC at use) | 2021 superseded; new **A03 Software Supply Chain Failures** (expands 2021 A06 Vulnerable & Outdated Components) + **A10 Mishandling of Exceptional Conditions**; [owasp.org/Top10/2025](https://owasp.org/Top10/2025/), verified 2026-06-18 `[verify-at-use]` |
| SAST/SCA in CI | mature | Tune for signal; reachability where supported |
| Secret scanning | GitHub/GitLab native + tools | Pre-commit + CI + history scan |
| SLSA | v1.0 | Build levels; verify provenance on consume |
| CSPM | mature across clouds | Misconfig is #1 breach cause |
| Policy-as-code (OPA/Conftest, cloud policy) | GA | Preventive > detective; wire via terraform-iac |

## Decision Tree: Should a dependency update be emergency or scheduled?

**When this applies:** a new CVE advisory arrives for a dependency in use. The team must decide whether to drop everything and patch now, or schedule the update in the normal flow.

**Last verified:** 2026-06-05 against CISA KEV catalog guidance and supply-chain-security-engineer mandate.

```mermaid
flowchart TD
    START[A CVE in a dependency we use] --> Q1{Is the vulnerable code path reachable in our app?}
    Q1 -->|no, not reachable| SCHEDULE[Schedule on normal cadence - document reachability analysis]
    Q1 -->|yes or unknown| Q2{Is the vulnerability in the CISA KEV catalog or has a public working exploit?}
    Q2 -->|yes| EMERGENCY[Emergency patch - within 24h - route verdict to security-reviewer]
    Q2 -->|no| Q3{Is the service exposed to untrusted internet input?}
    Q3 -->|yes| Q4{CVSS >= 7 or High/Critical?}
    Q4 -->|yes| SPRINT[Patch this sprint - 7 day SLA]
    Q4 -->|no| SCHEDULE
    Q3 -->|no, internal only| SCHEDULE
```

**Rationale per leaf:**
- *Emergency patch* — exploited in the wild or public PoC means the attacker already has a recipe; exposure window must be zero.
- *Patch this sprint* — internet-exposed high/critical means a motivated attacker could develop an exploit; prioritize.
- *Schedule on cadence* — unreachable or low-impact can wait for the normal dependency update flow without meaningful risk increase.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Emergency patch | Interrupts current sprint | Release risk if rushed | Security-reviewer | KEV / public exploit |
| Sprint priority | Normal sprint overhead | Low | Sprint planning | Internet-exposed High/Critical |
| Scheduled update | Lowest effort | Lowest | PR review | Unreachable or low severity |

## Decision Tree: Discovered a secret in a repo — immediate response?

**When this applies:** a secret (API key, password, certificate private key, OAuth client secret) is found in a repository — in history, in a PR, or in a running config file. The response sequence matters.

**Last verified:** 2026-06-05 against GitHub secret scanning documentation and incident response best practices.

```mermaid
flowchart TD
    START[A secret found in a repo] --> Q1{Is it in git history or a public/shared clone?}
    Q1 -->|yes| COMPROMISED[Treat as COMPROMISED - rotate NOW before anything else]
    Q1 -->|no, working tree only, not pushed| Q2{Was the working tree shared - pair programming, screen share, exported?}
    Q2 -->|yes| COMPROMISED
    Q2 -->|no, isolated local only| SAFE_REMOVE[Remove + vault + add to scanner rule - not compromised]
    COMPROMISED --> ROTATE[1 - Rotate and revoke the old credential immediately]
    ROTATE --> VAULT[2 - Store the new credential in secrets manager]
    VAULT --> AUDIT[3 - Audit access logs for the old credential during exposure window]
    AUDIT --> SCANNER[4 - Add the pattern to secret scanner so it cannot recur]
    SCANNER --> VERDICT[5 - Route incident verdict to security-reviewer]
    SAFE_REMOVE --> SCANNER
```

**Rationale per leaf:**
- *Compromised path* — git history is permanent and cloned; rotation is the only remediation; deleting the commit does not help (clones exist).
- *Safe remove* — a working-tree-only, never-pushed secret can be cleaned without incident, but the scanner rule must still be added.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Rotate immediately | High - interrupt ops | Rotation may require deploy | Security-reviewer verdict | In history or shared |
| Remove and vault | Low - no rotation | None | PR review | Working tree, never shared |

## Decision Tree: Cloud misconfiguration found — preventive control or reactive fix?

**When this applies:** a CSPM scan or access audit surfaces a cloud misconfiguration (open security group, public bucket, overly broad IAM role). The team decides whether to fix it reactively and/or add a preventive policy control.

**Last verified:** 2026-06-05 against cloud-security-engineer mandate and OPA/Conftest practice.

```mermaid
flowchart TD
    START[A cloud misconfiguration found] --> Q1{Is the resource actively exposed to untrusted traffic or data?}
    Q1 -->|yes| FIX_NOW[Fix immediately - then add the preventive control]
    Q1 -->|no, internal or low-blast| Q2{Is this misconfiguration class common in our estate?}
    Q2 -->|yes, seen before| POLICY[Add a policy-as-code rule to prevent recurrence - then fix on cadence]
    Q2 -->|no, first occurrence| Q3{Is the fix captured in IaC - Terraform, CDK?}
    Q3 -->|yes, IaC controls it| FIX_IaC[Fix in IaC PR - lower urgency]
    Q3 -->|no, manual / out-of-band| POLICY
    FIX_NOW --> POLICY
```

**Rationale per leaf:**
- *Fix immediately + add preventive control* — active exposure needs instant remediation; a preventive control prevents the same class from recurring.
- *Add policy + fix on cadence* — common misconfiguration classes are higher ROI for preventive policy than one-off reactive fixes.
- *Fix in IaC* — if IaC already controls the resource, fix it there; the IaC review is the gate.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Immediate fix + policy | High effort | Closes exposure | Security-reviewer | Actively exposed resource |
| Policy first, then fix | Medium - policy authoring | Prevents recurrence | PR review + policy review | Common class, low blast |
| Fix in IaC | Low - PR only | Lowest | PR review | IaC-controlled, not exposed |
