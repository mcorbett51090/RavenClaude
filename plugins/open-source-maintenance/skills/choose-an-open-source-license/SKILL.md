---
name: choose-an-open-source-license
description: Recommend an open-source license for a project from its intent (permissive adoption vs reciprocal sharing), its dependency-license graph (the strongest copyleft constrains the whole), and its contribution-agreement need (CLA vs DCO vs neither). Returns a license recommendation, the LICENSE/NOTICE files to add, and the contribution posture. Used by `oss-maintainer-strategist` (primary).
---

# Skill: choose-an-open-source-license

> **Invoked by:** `oss-maintainer-strategist` (primary).
>
> **When to invoke:** "which license?"; "can I use MIT here?"; "do we need a CLA?"; before any first public release.
>
> **Output:** a license recommendation + the dependency-compatibility check that backs it + a CLA-vs-DCO call + the concrete LICENSE / NOTICE files to add.
>
> **Not legal advice.** This is the maintainer's working judgment; flag anything with commercial/patent stakes for a lawyer.

## Procedure

1. **State the intent.** Maximize adoption / let anyone embed it (→ permissive: MIT, Apache-2.0, BSD)? Or guarantee derivatives stay open (→ copyleft: GPL/AGPL/LGPL/MPL)? This is the top fork of [`../../knowledge/oss-licensing-decision-tree.md`](../../knowledge/oss-licensing-decision-tree.md).
2. **Inventory the dependency licenses FIRST.** The strongest copyleft in the graph constrains the whole work: a GPL dependency means a derivative you distribute is effectively GPL, no matter what you write in your LICENSE. Network-use (AGPL) and weak-copyleft (LGPL/MPL file-scope) have their own reach. Resolve incompatibility before recommending.
3. **Decide patent posture.** If patents are a concern (or contributors are corporate), prefer **Apache-2.0** (explicit patent grant + termination) over MIT/BSD.
4. **Pick the contribution agreement.** Default **DCO** (`Signed-off-by`, no extra paperwork). Recommend a **CLA** only with a real reason: relicensing optionality, a corporate steward needing aggregated rights, or a dual-license business model. Neither is fine for small projects — the inbound=outbound default (contributions licensed under the project license) covers most.
5. **Emit the files.** `LICENSE` (verbatim text), `NOTICE` if Apache-2.0 or attribution is owed, and a one-line license statement in the README. For dual-licensing, document both and the boundary.

## Quick map (verify against the decision tree)

| Goal | Default | Why |
|---|---|---|
| Maximum adoption, embeddable anywhere | **MIT** | Shortest, most permissive, universally understood |
| Permissive + patent protection | **Apache-2.0** | Explicit patent grant; preferred for corporate contributors |
| Derivatives must stay open (app) | **GPL-3.0** | Strong copyleft on distribution |
| Same, including SaaS/network use | **AGPL-3.0** | Closes the "hosted, not distributed" gap |
| Library: copyleft but linkable from closed code | **LGPL-3.0** or **MPL-2.0** | File/library-scope reciprocity |

## Guardrails
- **License before the first public commit.** Retrofitting is legally murky (prior contributions have ambiguous grants).
- **Never recommend a permissive license over an incompatible copyleft dependency** — it is unenforceable and misleads users.
- **Don't invent license text.** Use the canonical SPDX text verbatim; cite SPDX identifiers.
- A CLA is contributor friction — justify it or drop it. See [`../../best-practices/dco-or-cla-decide-before-contributions.md`](../../best-practices/dco-or-cla-decide-before-contributions.md).
