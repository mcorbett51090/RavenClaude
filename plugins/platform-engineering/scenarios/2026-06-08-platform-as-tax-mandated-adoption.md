---
scenario_id: 2026-06-08-platform-as-tax-mandated-adoption
contributed_at: 2026-06-08
plugin: platform-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [platform-as-product, paved-road, adoption, mandate, devex, walled-garden]
confidence: medium
reviewed: false
---

## Problem

Adoption of a platform's golden path had stalled at ~35% after a year. Leadership's fix was a mandate: an architecture-review gate that blocked any new service not built on the platform, plus an OKR penalizing teams that went off-road. Coverage shot to ~95% on paper within a quarter, and the platform team declared victory. Underneath, developers were miserable — the path was slower and more constrained than rolling their own for several common cases — and a shadow-infrastructure problem grew: teams smuggled real work into "exception" repos and quietly maintained off-the-books tooling the platform team couldn't see.

## Constraints context

- The platform genuinely solved some workflows well, but had real ergonomic gaps for others (long-running data jobs, anything needing a non-default runtime).
- "Adoption" was reported as coverage % only — a number a mandate can move without the path getting any better.
- The mandate hid the signal: high coverage made the gaps invisible to leadership precisely when they most needed to see them.

## Attempts

- Tried: tightening the gate and the OKR penalty to close the "exception" loophole. Failed — it deepened the walled garden, drove the shadow work further underground, and burned trust in the platform team.
- Tried: a satisfaction survey to "prove" the platform was fine. Failed — coverage was high so the survey looked acceptable in aggregate, masking that the loudest pain was concentrated in the teams with the worst-fit workflows.
- Tried: dropping the mandate, treating low adoption as a product signal, and re-instrumenting. Paired paved-road coverage with a DevEx pulse and the DORA lead-time key *per path*, then funded closing the two worst ergonomic gaps so the road was genuinely the easy default. This worked — voluntary coverage climbed past the mandated number within two quarters, and the shadow repos came back onto the road on their own.

## Resolution

Removing the mandate restored the signal: where coverage dropped, it pointed straight at a path that wasn't yet better than the alternative, and fixing those spots won adoption on ergonomics. Pairing coverage with a DevEx experience signal stopped the vanity-metric trap where a number rises while developer experience falls. The platform was treated as a product whose customers can choose not to use it — which is exactly what made it improve.

## Lesson

Platform-as-product, not platform-as-tax — adoption is earned on ergonomics, not mandated by policy, and a paved road is the easy default, never a walled garden. Mandating usage hides the signal that the road isn't actually better and breeds shadow infrastructure; always pair paved-road coverage with a DevEx signal so coverage can't rise while experience falls.
