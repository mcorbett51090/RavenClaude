# title-escrow-settlement

A RavenClaude plugin: a **title, escrow, and settlement operations** specialist team for the three engines of a settlement operation — the order-to-policy production workflow, title search and examination, and escrow settlement and disbursement — with the wire-fraud and escrow-trust-account controls that keep the money safe.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Advisory domain operations knowledge — not legal, title-underwriting, or financial advice.** Underwriter guidelines, ALTA best-practice pillars, CFPB/TRID specifics, good-funds rules, and recording requirements are volatile and jurisdiction-/underwriter-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed before it drives a commitment, a disbursement, or a recording. The agents are **wire-fraud sensitive** and store **no PII** — a wire destination is never sourced from a file or email; it is verified live by out-of-band callback.

## What it's for

Running a title/settlement operation well: files that move from order to policy on time, commitments that clear their requirements before closing, statements that balance to the lender's CD, disbursements only against collected funds, and an escrow trust account protected absolutely — with wire fraud designed out of the disbursement path.

## Agents

| Agent | Use for |
|---|---|
| **title-escrow-lead** | Order-to-policy workflow, production sequencing, ALTA/CFPB/TRID compliance coordination, wire-fraud control program |
| **title-examiner** | Title search & examination, chain of title, liens/encumbrances, the commitment (B-I requirements / B-II exceptions), curative |
| **closing-settlement-coordinator** | Escrow/settlement, CD/statement coordination, closing/signing, good-funds discipline, disbursement, recording, funding |

## What's inside

- **4 skills** — title-search-and-examination, commitment-and-curative, escrow-closing-and-disbursement, wire-fraud-and-trust-account-controls.
- **Knowledge bank** — [`title-escrow-decision-trees.md`](knowledge/title-escrow-decision-trees.md) (4 Mermaid trees: clear-a-title-exception, escrow disbursement authorization, wire verification, order-to-policy workflow) + [`title-escrow-reference-2026.md`](knowledge/title-escrow-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — title commitment worksheet, closing checklist.
- **2 commands** — `/clear-title-exceptions`, `/run-closing-checklist`.

## Seams

The lender's loan and CD → [`mortgage-lending`](../mortgage-lending/) · binding legal / contested title → [`legal-small-firm`](../legal-small-firm/) · commercial-transaction context → [`commercial-real-estate`](../commercial-real-estate/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install title-escrow-settlement@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the advisory scope, routing rules, house opinions, and the output contract.
