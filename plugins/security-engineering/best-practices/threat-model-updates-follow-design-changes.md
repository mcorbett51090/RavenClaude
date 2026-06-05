# Update the threat model when the design changes — it decays otherwise

**Status:** Absolute rule
**Domain:** Threat modeling
**Applies to:** `security-engineering`

---

## Why this exists

A threat model is a snapshot of the attack surface at a point in time. When the architecture changes — a new external integration, a new data store, a new authentication path, a new admin feature — the existing threat model no longer represents what you've built. Security controls designed for the old model may have gaps against the new one. A threat model that doesn't get updated misleads: it gives the impression of coverage while leaving new attack surfaces unreviewed.

## How to apply

Define the set of design changes that trigger a threat model review, and enforce it in the PR process. Not every PR needs a threat model update — define the threshold explicitly.

Threat model update triggers (any of these → update the threat model):
- New external trust boundary (new API integration, new third-party service)
- New data store or processing of a new data classification
- New authentication or authorization path
- New admin or privileged capability
- Significant change to the data flow through an existing component
- New network exposure (new public endpoint, new VPC peering, new port)

```markdown
# PR Template addition — security section
## Security checklist (complete for any PR touching architecture)
- [ ] This PR does NOT introduce a new trust boundary, data store, or auth path
      (if unchecked, tag @appsec-engineer for a threat model review)
- [ ] Existing threat model reviewed and updated (link: )
- [ ] New threats identified: (none / <list them>)
- [ ] New mitigations added: (none / <list them>)
```

**Do:**
- Version and date the threat model document; a stale date is a signal it needs review.
- Conduct a lightweight review ("did any of the triggers apply?") as part of every architecture PR, not just greenfield designs.
- Store the threat model in the repo alongside the code it describes — it must be reviewed like code.

**Don't:**
- Treat the threat model as a one-time design document that lives in a wiki and never changes.
- Review only the new component in isolation — re-examine the interaction between the new component and existing ones.
- Defer the threat model update to a follow-up ticket that never gets scheduled.

## Edge cases / when the rule does NOT apply

Pure refactors that don't change the external behavior, trust boundaries, or data flows don't require a threat model update — they require a confirmation that none of the triggers apply.

## See also

- [`../agents/threat-modeler.md`](../agents/threat-modeler.md) — owns threat model design, STRIDE analysis, and the update process.
- [`./threat-model-at-design-time.md`](./threat-model-at-design-time.md) — the initial threat model is created at design time; this rule governs its lifecycle.

## Provenance

Codifies Microsoft's Threat Modeling Tool guidance on threat model versioning and the OWASP Threat Modeling Cheat Sheet section on "Updating Your Threat Model."

---

_Last reviewed: 2026-06-05 by `claude`_
