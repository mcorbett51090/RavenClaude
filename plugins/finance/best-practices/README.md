# Finance — best-practice docs

Named, citable rules for the `finance` plugin's specialists. Each file is **one rule**, grounded in this plugin's knowledge bank and agent opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) or the automated checks in the anti-pattern hook (§7). They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md) | Absolute rule | A material variance landed and you are about to write commentary naming a cause — tie the account to the GL first |
| [`inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) | Absolute rule | Building or reviewing a financial model — every rate / growth / margin belongs on the Inputs sheet, labelled and sourced, never buried in a formula |
| [`link-the-three-statements.md`](./link-the-three-statements.md) | Absolute rule | Building or reviewing a three-statement model — the cash flow must be derived from BS + P&L movements and the balance sheet must tie, never plugged |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — finance team constitution (§3 house opinions, §4 anti-patterns, §6 Output Contract).
- [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) — the variance decision tree both docs lean on.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
