---
name: privacy-mechanics
description: "Engineer privacy: build executable data-subject-rights pipelines (access/erasure/portability) that locate data via the catalog, track lawful basis + granular revocable consent, minimize collection, automate retention/deletion, and distinguish pseudonymization from anonymization."
---

# Privacy Mechanics

## Data-subject rights = a pipeline
Access/erasure/portability executed across **every** system holding the person's data (located via catalog/lineage). 'Couldn't find it all' = failed DSR.

## Lawful basis + consent
Each use has a recorded basis; consent (where it's the basis) is **granular, timestamped, revocable**, and revocation **propagates**.

## Minimize + retain
Challenge every field (need it? how long? what basis?). **Automate** retention/deletion — indefinite retention is unbounded risk.

## Pseudonymization != anonymization
Pseudonymized (re-identifiable with a key) is **still personal data**. True anonymization is a high bar. Name which you achieved. Legal interpretation -> route out.

**Runnable engine (reversible).** To actually pseudonymize text before it reaches a model — reversibly, restored on the way back — use `ravenclaude-core`'s **`pseudonymize`** skill (`scripts/pseudonymize.py`): a deterministic known-entity denylist (the reliable core) + structured-PII regex + optional NER, with a local key **vault**. It enforces exactly the caveat above — the vault **is** the re-identification key, so the output is *still personal data*; keep the vault local (0600, out of git) and never send it to the model. It states its honest ceiling plainly: it reliably removes the entities you list, not every free-text name, and never claims anonymity (any unlisted variant leaks; quasi-identifiers re-identify even with names gone).
