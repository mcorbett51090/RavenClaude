# Blockchain & Web3 Engineering KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Contracts & security

| Term | Definition | Note |
|---|---|---|
| **Reentrancy** | An external call re-enters the contract before state is updated | Apply checks-effects-interactions + a guard (§3 #2). |
| **Checks-Effects-Interactions** | Validate, update state, THEN make external calls | The core reentrancy defense (§3 #2). |
| **Access control** | Who may call privileged functions (modifiers, roles, init) | Unprotected init / missing modifier is a top exploit (§3 #2). |
| **Invariant** | A property that must always hold (supply conserved, no value created) | Specify and fuzz, don't assume (§3 #5). |
| **Immutability** | Deployed bytecode is permanent on a non-upgradeable contract | No hotfix — audit is the gate (§3 #1). |

## Gas & storage

| Term | Definition | Note |
|---|---|---|
| **Gas** | Unit metering EVM computation; user pays gas × gas price | UX and cost; optimize the dominant ops (§3 #3). |
| **SSTORE** | Storage-write opcode; among the most expensive operations | Pack slots, cache reads, minimize writes (§3 #3). |
| **Gwei** | 10^-9 of the native token; the usual gas-price unit | Volatile — date it (§3 #8). |
| **On-chain vs off-chain** | What consensus needs vs what can live in IPFS/Arweave/indexers | On-chain is paid-for-forever and public (§3 #4). |

## Protocol & economics

| Term | Definition | Note |
|---|---|---|
| **MEV** | Maximal Extractable Value — reordering/front-running for profit | Part of the threat model (§3 #7). |
| **Oracle** | On-chain feed of off-chain data (e.g. price) | Use TWAP / multiple sources, never a spot DEX price (§3 #7). |
| **Flash loan** | Uncollateralized loan repaid in one tx | Amplifies economic attacks (§3 #7). |
| **Proxy / upgradeability** | Pattern allowing logic upgrade behind a stable address | Trades immutability for admin-key + storage-layout risk (§3 #6). |
| **Staking APR** | Gross reward rate net of validator commission | Illustrative engineering, not financial advice (§3 #8, §2). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
