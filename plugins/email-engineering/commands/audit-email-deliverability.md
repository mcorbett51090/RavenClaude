---
description: "Audit a sending domain's deliverability by traversing the triage tree (auth -> alignment -> reputation -> list hygiene -> content -> bulk-sender compliance) and return the failing layer, the fix, and how to confirm recovery."
argument-hint: "[domain / situation, e.g. 'newsletters from news.example.com going to spam']"
---

# Audit email deliverability

You are running `/email-engineering:audit-email-deliverability`. For the situation in `$ARGUMENTS`, find the failing layer and the fix — the diagnosis discipline of the `email-deliverability-architect` (top-down: a lower layer is meaningless if a higher one fails).

## When to use this

Mail is landing in spam, or you want a pre-flight check before a large/first send. NOT for first-time record setup (that is `/email-engineering:set-up-email-authentication`).

## Steps

1. **Traverse the diagnosis tree** in `knowledge/email-authentication-decision-tree.md` (Tree 2) top-to-bottom: authentication → alignment → reputation/warm-up → list hygiene → content → bulk-sender compliance.
2. **Demand population evidence, not anecdote** — Google Postmaster Tools + DMARC RUA aggregate reports, not "it reached my Gmail."
3. **Name the single failing layer** (or give a clean bill), the specific fix, and the signal that confirms recovery.
4. **Run the pre-send checklist** from `skills/deliverability-audit/SKILL.md` for a verdict.
5. For bulk senders, verify the Gmail/Yahoo gates (authenticated + one-click unsubscribe + spam rate under threshold), each with a retrieval date.

## Guardrails

- Don't fix content before auth/alignment — you'll chase ghosts.
- A sudden spam jump on a previously-good domain is usually reputation (complaints / a cold stream), not content.
- Alignment failures masquerade as "but we have SPF!" — check DMARC pass, not SPF pass.
