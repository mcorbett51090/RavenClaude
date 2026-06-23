# Add the license before the first public commit

**Status:** Absolute rule
**Domain:** Licensing
**Applies to:** `open-source-maintenance`

---

## Why this exists

Code published with no license is, by default, **all rights reserved** — nobody may legally use, modify, or redistribute it, even though it's visible. Adding a license later is legally messier than adding it now: every contribution made before the license existed has an ambiguous grant, and retroactively licensing other people's commits can require chasing down each contributor. The clean state is: license first, then accept contributions.

## How to apply

Choose the license ([`../skills/choose-an-open-source-license/SKILL.md`](../skills/choose-an-open-source-license/SKILL.md)) and commit the `LICENSE` file (verbatim SPDX text) in the **first** public commit, alongside a one-line license statement in the README. Add a `NOTICE` file if the license (e.g. Apache-2.0) or bundled third-party code requires attribution.

**Do:**
- Verify dependency-license compatibility before choosing — the strongest copyleft in the graph constrains the whole.
- Use canonical SPDX text verbatim and reference the SPDX identifier.

**Don't:**
- Publish "I'll add a license later" — that's all-rights-reserved code masquerading as open source.
- Hand-edit license text.

## Edge cases / when the rule does NOT apply

- **A private repo with no external contributors** can defer, but add the license before making it public or accepting the first outside PR.
- **Relicensing an existing project** is a genuine project — it needs contributor consent (or a CLA that anticipated it); that's a separate, deliberate effort, not a casual fix.

## See also
- [`../knowledge/oss-licensing-decision-tree.md`](../knowledge/oss-licensing-decision-tree.md)
- [`./dco-or-cla-decide-before-contributions.md`](./dco-or-cla-decide-before-contributions.md)

## Provenance
Codifies choosealicense.com / GitHub "no license" default (exclusive copyright). Last reviewed 2026-06-23. Not legal advice.

---

_Last reviewed: 2026-06-23 by `claude`_
