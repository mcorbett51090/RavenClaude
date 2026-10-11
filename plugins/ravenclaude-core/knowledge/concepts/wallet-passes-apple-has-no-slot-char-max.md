---
id: wallet-passes-apple-has-no-slot-char-max
title: "Apple field slots are counts, not character maxima"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 943
summary: "How Apple Wallet and Google Wallet document front-field capacity, and what an agent may treat as a contract."
last_verified: 2026-10-11
covers:
  - plugins/ravenclaude-core/skills/wallet-passes/SKILL.md
  - plugins/ravenclaude-core/skills/wallet-passes/references/apple.md
  - plugins/ravenclaude-core/skills/wallet-passes/references/google.md
  - plugins/ravenclaude-core/skills/wallet-passes/references/business-card-layout.md
covers_digest: "sha256:40900d7aa12ef469a1f7bd083fb8725df771f211c97fbdc4619ddffbabceaae0"
nuance: "Apple `PassKit_PG/Creating.html` names `headerFields` counts and says overflow hides fields; it never publishes a per-slot character maximum. Google `generic/resources/brand-guidelines` Content does publish English caps. An invented Apple char-limit table is working guidance, not a contract."
nuance_evidence:
  measured: 2026-10-11
  control: "Apple Creating.html field section lists header/primary/secondary/auxiliary counts and the overflow-hides-fields sentence; the same page has no per-slot char max. Google brand-guidelines Content table lists English caps (card title < 47, field label < 20, field data < 15)."
  falsifier: "an Apple developer page that publishes a per-slot character maximum for headerFields or primaryFields, or a Google brand-guidelines page that withdraws the English Content table"
  probe: "unprobed: official Apple/Google HTML is not staged in CI; re-read the cited Creating.html field section and Brand guidelines Content table"
nuance_source: "plugins/ravenclaude-core/skills/wallet-passes/references/apple.md"
verify:
  tier: "none"
  rationale: "This is an official-docs capacity fact, not offline-stageable in CI. Re-verification is re-reading the cited Apple Creating.html field section and Google Brand guidelines Content table, not a staged probe."
sources:
  - label: "Apple Wallet Developer Guide — Pass Design and Creation"
    url: https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html
  - label: "Google Wallet Brand guidelines — Generic"
    url: https://developers.google.com/wallet/generic/resources/brand-guidelines
---

## What a reader would have assumed instead

That both wallets publish the same kind of front-field contract, so an agent can
copy a per-slot character table from one platform onto the other, or invent Apple
maxima to match Google's published English caps.

## The discriminator

control: Apple Creating.html field section lists header/primary/secondary/auxiliary counts and the overflow-hides-fields sentence; the same page has no per-slot char max. Google brand-guidelines Content table lists English caps.

Measured 2026-10-11: Apple documents how many fields fit a slot and that extra
text drops fields from the face. Google documents English character caps on
named surfaces. Those are different contracts.

## Why it matters

A shipping pass that treats a guessed Apple character table as a hard max will
either underfill the face or hide fields Wallet would have shown. The
wallet-passes skill keeps that split explicit so a later editor cannot "helpfully"
add an Apple char-limit table without marking it non-contract.
