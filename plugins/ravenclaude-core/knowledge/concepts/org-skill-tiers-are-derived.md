---
id: org-skill-tiers-are-derived
title: "An unsettled constraint ships as a WARN, not a guess"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 904
summary: "How the org-skill studio represents a platform constraint nobody has verified, instead of guessing one."
last_verified: 2026-08-25
covers:
  - plugins/ravenclaude-core/skills/authoring-org-skills/SKILL.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/schemas/org-skill-rules.json
  - plugins/ravenclaude-core/skills/authoring-org-skills/reference/platform-constraints.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/reference/refusals.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/reference/ds02-markers.json
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/orgskill.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/lint_rules.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/refusals.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/packer.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/derive_markers.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/test_lint.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/test_refusals.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/test_pack.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/scripts/test_procedure.py
  - plugins/ravenclaude-core/skills/authoring-org-skills/templates/skeleton/SKILL.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/templates/skeleton/reference/details.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/templates/examples/drafting-customer-replies/SKILL.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/templates/examples/drafting-customer-replies/reference/categories.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/templates/examples/drafting-customer-replies/reference/tone.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/templates/examples/screening-vendor-invoices/SKILL.md
  - plugins/ravenclaude-core/skills/authoring-org-skills/templates/examples/screening-vendor-invoices/reference/tolerances.md
covers_digest: "sha256:8139a1422d1d0ab1fbee7a0d713fa0e6e3d39dc50679b58fa0e02a28f2ca3d9a"
nuance: "A rule's tier is READ from `reference/platform-constraints.md`, never hand-set, so a constraint the vendor contradicts itself on ships as WARN instead of a guess. Research moves the packer's default and never the tier: docs say what the platform emits, not what its unpacker accepts."
nuance_evidence:
  measured: 2026-08-25
  control: "settled:yes plus accepted_layout promotes the tier to fail; settled:yes alone does not; and research at strong confidence moved the default while the tier stayed warn"
  falsifier: "a tier that changes without an edit to the evidence file, or research promoting one"
  probe: "plugins/ravenclaude-core/skills/authoring-org-skills/scripts/test_pack.py"
nuance_source: "plugins/ravenclaude-core/skills/authoring-org-skills/scripts/packer.py:34-100"
verify:
  tier: "effect"
  strength: "executed"
  class: "static-resolution"
  probe: "plugins/ravenclaude-core/skills/authoring-org-skills/scripts/test_pack.py"
  teeth_exit: 1
sources:
  - label: "claude.ai Organization Skills — provisioning"
    url: https://support.claude.com/en/articles/13119606
  - label: "claude.ai skills — packaging structure"
    url: https://support.claude.com/en/articles/12512198
---

# An unsettled constraint ships as a WARN, not a guess

The studio enforces claude.ai **Organization Skill** packaging — a different artifact
from the Claude Code skills this repo is built from. Three of its constraints cannot be
settled by reading, because **Anthropic's own sources contradict each other**:

| Rule | The contradiction |
|---|---|
| `ZP02` root layout | the org-console article is silent; the rule is inherited from the sibling personal-uploader page |
| `ZP10` filename case | one article writes `skill.md` throughout, another and the repo write `SKILL.md` |
| `FM09` folder-name equality | the doc says "matches your skill's name" and its own example pairs `Brand Guidelines` with `my-skill/` |

Each could have been guessed. Guessing wrong blocks a correct archive on a coin flip,
on an artifact provisioned org-wide.

## The mechanism

`derive_zp02_tier()` reads the evidence file and returns the tier. **Nothing hand-sets
it.** While the file records no settlement the rule is WARN; a recorded upload promotes
it to FAIL. Settling is a data edit, never a code change.

`derive_default_layout()` adds a second, weaker channel with a strict precedence:

```
upload-verified  >  research  >  fallback
```

Research moves only the packer's **default**. It never promotes a tier, at any
confidence — and a test asserts exactly that, because the asymmetry is the whole point:
reading a doc tells you what the platform **emits**, not what its unpacker **accepts**.
Promoting a rule on a documentary inference would block a real archive on a conclusion
nobody ran, which is the failure the rest of the studio exists to catch.

Demotion runs the other way and is admissible: `FM09` went FAIL → WARN once Anthropic's
own worked example was found to violate it. Removing an unjustified block needs only the
demonstration that the ground truth was never there; adding one needs an observation.

## What the basis buys the user

The packer prints which channel it used, on every non-verified build:

```
packed out.zip (2 entries, root layout A)
NOTE: root layout A chosen on basis 'research' — RESEARCH ONLY, NOT UPLOAD-TESTED
      (confidence: moderate).
```

A user told "layout A" and not told *why* cannot tell an observation from a guess, and
those carry very different odds of the upload working.

## Limit

⛔ This makes the uncertainty **representable**, not smaller. All three rules stay
unsettled until someone with an org owner seat uploads the two probe fixtures
(`orgskill fixtures --out <dir>`). The mechanism's honesty is the deliverable; the
answer is still missing.
