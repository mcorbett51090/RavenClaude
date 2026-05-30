# Keep policy and procedure in separate documents — mix them and drift is guaranteed

**Status:** Absolute rule
**Domain:** Policy and procedure authoring
**Applies to:** `regulatory-compliance`

---

## Why this exists

Policy and procedure answer different questions, move at different speeds, and are approved by different people — so binding them into one document guarantees drift. A **policy** states board-level commitments and principles (what the firm commits to and why), changes rarely, and is approved by the board or a committee. A **procedure** states how the policy is operationalized (the actual steps), changes whenever the process changes, and is approved by an executive owner. When procedure is buried inside policy, every operational tweak either drags the board through a re-approval it shouldn't need, or — far more common — the procedure quietly updates and the policy text goes stale, so the document in force no longer describes what people do. The four-layer taxonomy (policy → procedure → standard → guideline) exists precisely so each layer can change at its own cadence under its own approval. A 100-page policy nobody reads is worse than a 12-page policy everyone reads; the length usually comes from procedure that doesn't belong there.

## How to apply

Separate the layers, give each its own approval and cadence, and keep one source of truth per document:

```
POLICY      principles + board-level commitments; approver = board/committee; changes rarely
PROCEDURE   how the policy is operationalized (steps); approver = exec owner; changes with the process
STANDARD    specific required configuration/threshold (the "what good looks like")
GUIDELINE   recommended-but-not-mandatory practice
Every layer cite the regulator's actual section it implements  [verify-at-build — primary source]
            named accountable owner (a person/role, not "the team")
            defined review cycle + last-reviewed date
            an exceptions section (who authorizes, on what basis, with what record)
```

A policy without an exceptions section makes every deviation a violation; a policy with definitions that don't actually define ("customer", "material") guarantees inconsistent application. Write what the firm actually does, then fix the gap — not the aspirational version.

**Do:**
- Put principles in policy and steps in procedure, each with its own approver and review cadence.
- Name accountable owners ("the Compliance Officer is accountable for X"), not functions ("Compliance handles X").
- Include a real definitions section and a real exceptions section in every policy.

**Don't:**
- Bury procedure inside policy — drift is then guaranteed and the in-force text goes stale.
- Let multiple "versions" of the same policy float in different drives — one source of truth per policy.
- Ship copy-pasted vendor-template text (the vendor's company name still in it is a real, recurring miss).

## Edge cases / when the rule does NOT apply

- **Very small policy areas** may legitimately collapse standard/guideline into the procedure — but policy and procedure still separate; the split that matters most is principle vs step.
- **Jurisdictional adaptation** changes the *definitions, thresholds, and escalation paths* across borders, not usually the principle — adapt those layers per regime (house opinion #12), keep the principle stable.
- **Legal-opinion gate** — whether a policy commitment creates legal obligation/liability routes to counsel; the drafting and structuring continue.

## See also

- [`./scope-the-jurisdiction-before-you-map.md`](./scope-the-jurisdiction-before-you-map.md) — what diverges across jurisdictions is the lower layers, not the principle.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: Policy vs procedure vs standard vs guideline`.
- [`../agents/policy-and-procedure-writer.md`](../agents/policy-and-procedure-writer.md) — "Short policy, detailed procedures"; "One source of truth per policy."

## Provenance

Codifies the `policy-and-procedure-writer` opinions "Short policy, detailed procedures," "One source of truth per policy," "Roles and responsibilities are named," "Exceptions are documented in policy," and "Definitions section actually defines," plus the anti-patterns "policy and procedure mixed in one document," "different copies of 'the' policy floating," and "vendor-template policy with the vendor's company name still in it" ([`../agents/policy-and-procedure-writer.md`](../agents/policy-and-procedure-writer.md)), and house opinions #6, #7, #12 in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
