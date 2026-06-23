# Decide DCO vs CLA before the first outside contribution

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Contribution agreements
**Applies to:** `open-source-maintenance`

---

## Why this exists

Every contribution carries rights questions: does the contributor have the right to submit this, and under what terms is it licensed to the project? Deciding *after* contributions arrive means either retrofitting an agreement onto existing contributors (friction, possible refusals) or leaving the question unanswered (legal ambiguity for downstream users). Decide the posture before the first outside PR.

## How to apply

Default to the **DCO** — a `Signed-off-by` line (`git commit -s`) certifying the right to submit; zero paperwork; enforce with the DCO app. Choose a **CLA** only with a real reason: a corporate steward needing aggregated rights, relicensing optionality, or a dual-license business model. State the chosen posture (and the inbound=outbound default if neither) in `CONTRIBUTING.md`.

**Do:**
- Prefer DCO unless a concrete need demands a CLA.
- If you adopt a CLA, use a well-known one (not a bespoke contract) and gate it with a bot.

**Don't:**
- Impose a heavyweight CLA on a small community project "just in case" — it suppresses contributions.
- Leave the question implicit on a project that may later want to relicense.

## Edge cases / when the rule does NOT apply

- **Solo project, no outside contributions yet** — defer, but decide before opening the door.
- **Foundation-governed projects** often mandate a specific CLA/DCO; follow the foundation's policy.

## See also
- [`../knowledge/community-health-and-governance.md`](../knowledge/community-health-and-governance.md)
- [`./license-before-first-public-commit.md`](./license-before-first-public-commit.md)
- [`../templates/contributing-guide.md`](../templates/contributing-guide.md)

## Provenance
Codifies the DCO (developercertificate.org) and the inbound=outbound GitHub ToS default. Last reviewed 2026-06-23. Not legal advice.

---

_Last reviewed: 2026-06-23 by `claude`_
