---
description: Audit the developer getting-started experience — walk it from a clean state, measure time-to-first-success, rank friction by drop-off, and make a fix-or-document call on each (file the bug before writing around it).
argument-hint: "[the product/API, e.g. 'our payments API getting-started']"
---

# Audit getting-started

You are running `/developer-relations:audit-getting-started`. Audit the
getting-started experience for `$ARGUMENTS` using the `developer-advocate`
discipline: time-to-first-success is the metric.

## Steps

1. **Walk it from a genuinely clean state** — new account, no cached creds, no
   insider knowledge. Treat anything you "already knew" as friction.
2. **Time it to first success** and record the milestone that counts as "it worked."
3. **Log every friction point** with its funnel step and drop-off impact.
4. **Make a fix-or-document call per friction point** (tree 2 in
   [`../knowledge/devrel-engagement-decision-trees.md`](../knowledge/devrel-engagement-decision-trees.md)):
   product-pain → file a product-feedback ticket FIRST; undiscoverable → content task.
5. **Capture it** in the
   [`getting-started-audit`](../templates/getting-started-audit.md) template and name
   the top 3 to fix now.

## Guardrails

- Don't paper over a product flaw with a longer tutorial — file the bug.
- "Improving onboarding" with no TTFS number to move is not an audit.
