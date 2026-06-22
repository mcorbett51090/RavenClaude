# Trust & Safety — best-practice docs

Named, citable rules for the `trust-and-safety` plugin's two agents (`trust-safety-policy-lead`, `abuse-detection-engineer`). Each file is **one rule**, grounded in this plugin's knowledge bank and the agents' house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) or the advisory smell hook (§7). They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_3 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`enforcement-ladder-proportionality.md`](./enforcement-ladder-proportionality.md) | Absolute rule | Deciding what action a violation earns — the response must fit severity × the user's history; reserve the irreversible top rungs for clear, severe, or repeat cases. |
| [`appeals-are-due-process-not-optional.md`](./appeals-are-due-process-not-optional.md) | Absolute rule | Shipping any enforcement action — it carries notice + reason + a route to contest; a high appeal-overturn rate is feedback, not noise. |
| [`measure-prevalence-not-just-volume.md`](./measure-prevalence-not-just-volume.md) | Absolute rule | Reporting program health — lead with prevalence (impressions), not "items removed"; report precision/recall as a pair on a named eval. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — trust-and-safety team constitution (§3 house opinions, §4 anti-patterns, §6 Output Contract, §7 smell hook).
- [`../knowledge/enforcement-decision-tree.md`](../knowledge/enforcement-decision-tree.md) — the severity-triage + action-ladder + appeal tree the proportionality and appeals rules lean on.
- [`../knowledge/trust-safety-metrics.md`](../knowledge/trust-safety-metrics.md) — the metric catalogue the prevalence rule cites.
