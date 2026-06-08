# Blockchain & Web3 Engineering Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Are we safe to deploy?

```mermaid
flowchart TD
    A[Ready to deploy?] --> B{Top-3 classes<br/>audited?}
    B -- "No" --> B1[Audit reentrancy/access/arith<br/>FIRST — no hotfix, §3 #1 #2]
    B -- "Yes" --> C{Invariants<br/>fuzzed?}
    C -- "Happy-path only" --> C1[Specify + fuzz invariants;<br/>exploit lives off-path, §3 #5]
    C -- "Fuzzed" --> D{Economic surface<br/>modeled?}
    D -- "Code-only" --> D1[Add oracle/flash-loan/MEV;<br/>code-correct can still drain, §3 #7]
    D -- "Modeled" --> E{Upgradeable?}
    E -- "Proxy" --> E1[Protect init + admin key +<br/>storage layout, §3 #6]
    E -- "Immutable" --> E2[Gate cleared — go/no-go]
    B1 --> F[Findings gate the deploy ·<br/>route legal/securities to counsel, §2 #8]
    C1 --> F
    D1 --> F
    E1 --> F
    E2 --> F
```

## Tree 2 — Should this data live on-chain?

```mermaid
flowchart TD
    A[Where to put data?] --> B{Consensus-critical?<br/>balances/ownership}
    B -- "Yes" --> B1[On-chain — pack storage,<br/>minimize SSTORE, §3 #3 #4]
    B -- "No" --> C{Sensitive/private?}
    C -- "Yes" --> C1[NEVER on-chain — public<br/>forever; off-chain only, §3 #4]
    C -- "No" --> D{Large / mutable?}
    D -- "Yes" --> D1[Off-chain IPFS/Arweave +<br/>on-chain hash pointer, §3 #4]
    D -- "No, tiny+static" --> D2[Price both via storage-cost;<br/>cheapest wins, §3 #4]
    B1 --> E[Placement + cost/privacy<br/>rationale recorded]
    C1 --> E
    D1 --> E
    D2 --> E
```

## Tree 3 — Could we be drained without a code bug?

```mermaid
flowchart TD
    A[Economic-drain risk?] --> B{Price oracle<br/>source?}
    B -- "Spot DEX price" --> B1[Manipulable — move to TWAP /<br/>multi-source, §3 #7]
    B -- "TWAP/multi" --> C{Flash-loan<br/>amplifiable?}
    C -- "Yes" --> C1[Cap/guard the amplified path;<br/>test under flash loan, §3 #7]
    C -- "No" --> D{MEV exposure?}
    D -- "Front-run/sandwich" --> D1[Commit-reveal / slippage<br/>bounds / private mempool, §3 #7]
    D -- "Low" --> D2{Upgrade admin<br/>key risk?}
    D2 -- "Single key" --> D3[Multisig/timelock the admin,<br/>§3 #6]
    D2 -- "Hardened" --> D4[Economic surface mapped]
    B1 --> E[Threat model + mitigations ·<br/>not investment advice, §2 #8]
    C1 --> E
    D1 --> E
    D3 --> E
    D4 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
