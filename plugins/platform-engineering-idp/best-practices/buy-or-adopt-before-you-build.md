# Buy or adopt before you build (and build before you framework)

**Status:** Pattern
**Domain:** IDP / portal technology choice
**Applies to:** `platform-engineering-idp`

---

## Why this exists

Backstage is powerful and genuinely the right answer for some orgs — but it's a build-and-maintain
commitment, not a product you install. Many teams choose it for prestige, under-budget the upkeep, and
end up with a half-upgraded portal nobody trusts. The cheaper failure-avoiding default is: adopt a
managed portal if your needs are standard; build on Backstage only when deep customization is a real
requirement *and* a team will own the upgrades.

## How to apply

- Traverse the buy-vs-build tree: standard needs + thin maintenance budget → managed (Port, Cortex,
  OpsLevel, Spotify Portal/Roadie). Deep customization + a dedicated team → Backstage.
- Before either, ask whether you need a portal *yet* — a paved road + README may be enough.
- Whichever you pick, keep the catalog as code and every entity owned.

**Do:**

- Match the tool to your maintenance budget honestly.
- Pilot a managed portal to get value in weeks.
- Reserve Backstage for genuine bespoke needs with an owner.

**Don't:**

- Choose Backstage for prestige with no upkeep budget.
- Build a custom portal from scratch when a managed one fits.
- Stand up any portal before there's something worth surfacing.

## Edge cases / when the rule does NOT apply

If your differentiation genuinely depends on a custom developer portal (rare), building is the right
call — make it a funded, owned product, not a side project.

## See also

- [`./catalog-as-code-every-entity-owned.md`](./catalog-as-code-every-entity-owned.md)
- [`./start-with-the-thinnest-viable-platform.md`](./start-with-the-thinnest-viable-platform.md)

## Provenance

Codifies the build-vs-buy guidance in the platform-engineering community (Backstage adopter
retrospectives; Humanitec/Roadie analyses) and the marketplace's buy-before-build doctrine.

---

_Last reviewed: 2026-06-08 by `claude`._
