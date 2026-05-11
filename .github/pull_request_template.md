<!--
Thanks for opening a PR! Pick the section below that matches your change
and DELETE the others. Then fill in the checkboxes honestly — they tell
the maintainer what's been checked and what still needs review.
-->

## What kind of change is this?

_Delete the two sections that don't apply._

---

### Proposed lesson

**Title:** _<short rule name>_

**Domain:** _ALM / Identity / Web API / Solution mechanics / Agent design / Cross-domain / Other_

**Files added or changed:**
- `docs/best-practices/<slug>.md`
- `docs/memory-bank/lessons-learned.md` _(if you appended an entry there)_

**Required sections (per `docs/best-practices/_TEMPLATE.md`):**
- [ ] Status (absolute rule / primary diagnostic / pattern)
- [ ] Why it exists
- [ ] How to apply (with a concrete example)
- [ ] See also (cross-references to related docs)
- [ ] Provenance (where this rule came from)

**Has been:**
- [ ] Project-specific identifiers scrubbed (no client names, real tenant IDs, real GUIDs, real emails)
- [ ] Cross-references checked (links resolve, anchors land in the right place)
- [ ] Format matches `_TEMPLATE.md` and existing best-practice docs

---

### Plugin change

**Plugin:** _e.g. `ravenclaude-core` or `power-platform`_

**Change type:** _bug fix / new agent / new skill / agent prompt revision / hook change / rule update / template / other_

**Version bump applied in `plugin.json`?**
- [ ] Yes — bumped from `<old>` to `<new>` (patch / minor / major)
- [ ] No — explain why this doesn't need a version bump

**Consumer impact:**
- [ ] None — purely internal cleanup
- [ ] Behavior change — existing installs will see different agent/skill output after `marketplace update`. Described below.
- [ ] Breaking — existing installs need a migration step. Described below.

_Describe the consumer impact, if any, in 1–3 sentences._

---

### Marketplace / meta change

**What's changing:** _README, marketplace.json, devcontainer, CONTRIBUTING.md, .github/, etc._

**Affects:** _all plugins / specific plugin / docs only / dev workflow only_

**Has been:**
- [ ] JSON manifests still validate (`python3 -m json.tool` on any edited `.json`)
- [ ] Markdown links spot-checked
- [ ] No accidental secrets, emails, or internal URLs introduced

---

## Notes for the reviewer

_Anything unusual, anything you're unsure about, anything that needs Matt's explicit call. Keep it short — the diff says what; this section says why._
