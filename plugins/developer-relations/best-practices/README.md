# Developer-relations — best-practice docs

Named, citable rules for the `developer-relations` plugin's two agents (`devrel-strategist`, `developer-advocate`). Each file is **one rule**, grounded in this plugin's knowledge bank and the agents' house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) or the automated smell checks in the advisory hook (§7). They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_3 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`optimize-time-to-first-hello-world.md`](./optimize-time-to-first-hello-world.md) | Absolute rule | Building or auditing a quickstart / sample app — TTFHW gates activation, so measure it on a clean machine and cut everything before first hello-world. |
| [`sample-apps-must-run-unmodified.md`](./sample-apps-must-run-unmodified.md) | Absolute rule | Authoring any developer-facing code — every block is language-tagged and the path runs unmodified, with an explicit success check; a sample that doesn't run spends trust. |
| [`close-the-product-feedback-loop.md`](./close-the-product-feedback-loop.md) | Absolute rule | Setting up DevRel measurement or operating model — run the product-feedback motion as a standing artifact and anchor headline metrics in developer success, not vanity reach. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — developer-relations team constitution (§3 house opinions, §4 anti-patterns, §6 Output Contracts, §7 smell hook).
- [`../knowledge/devrel-strategy-decision-tree.md`](../knowledge/devrel-strategy-decision-tree.md) — the goal→motion→metric tree the rules lean on.
- [`../knowledge/devrel-metrics.md`](../knowledge/devrel-metrics.md) — the AAARRP funnel, TTFHW, and vanity-metric traps the rules cite.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
