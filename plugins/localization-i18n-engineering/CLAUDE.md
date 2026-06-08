# Localization i18n Engineering Plugin — Team Constitution

> Team constitution for the `localization-i18n-engineering` Claude Code plugin — **3** specialist
> agents covering the full internationalization and localization engineering lifecycle: designing
> software to be localizable, operating the localization pipeline, and validating quality through
> automated and manual QA.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution
> inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).
> For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`i18n-architect`](agents/i18n-architect.md) | Designing software to be localizable: string externalization, ICU MessageFormat, locale data architecture, RTL/bidi support, text expansion, encoding (Unicode/UTF-8) | "make this app localizable", "ICU MessageFormat for plurals", "add RTL support", "encoding issues", "how do I handle date/number formatting per locale" |
| [`l10n-pipeline-engineer`](agents/l10n-pipeline-engineer.md) | The localization pipeline: string extraction, TMS handoff workflows, translation memory, XLIFF/ARB/PO string catalog formats, continuous localization, branching strategies | "set up our localization pipeline", "integrate with Phrase/Lokalise/Crowdin", "TMS vs manual workflow", "extraction from React/Android/iOS", "how do we handle translation for a CD release cycle" |
| [`localization-qa-engineer`](agents/localization-qa-engineer.md) | Localization quality assurance: pseudo-localization CI gates, l10n linting (missing keys, untranslated strings, length overflows), visual/overflow QA, locale-coverage testing, false-positive triage | "pseudo-localize our build", "add l10n linting to CI", "strings are overflowing in German", "some locales missing keys", "how do I test RTL layout" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses
specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.

---

## 2. Cross-cutting house opinions (every agent enforces)

1. **Every user-facing string is externalized — no exceptions.** Hard-coded display strings in
   source code are bugs, not shortcuts. Externalization is not optional once you ship to more than
   one locale.
2. **Never concatenate translatable strings.** Word order differs across languages. Sentence
   assembly with `+` or template interpolation (e.g. `"Hello " + name + "!"`) produces untranslatable
   fragments. Use a single named-parameter message.
3. **ICU MessageFormat for plurals and gender — always.** An `if count == 1` branch is wrong in
   every language except a small subset. Arabic has six plural forms; Russian has three. Use
   `{count, plural, one{…} other{…}}` at minimum; extend to `zero`/`two`/`few`/`many` for languages
   that require them.
4. **Design for 30 % text expansion and RTL from day one.** Germanic languages run ~30 % longer than
   English; Finnish can run 50 %. UI that wraps at English-text length will break in German and
   Finnish. RTL (Arabic, Hebrew) is a bidirectional layout concern, not a CSS afterthought.
5. **Pseudo-localization is a CI gate, not a pre-release chore.** Running a pseudo-locale build
   in CI catches i18n bugs (hard-coded strings, concatenation, overflow, bidi) before translation
   costs are incurred and before they block a release.
6. **Translatable content stays out of code.** Logic that depends on translated string values
   (e.g. `if (label === "Yes")`) is fragile and untestable. Locale-aware branching is done on
   message keys or locale codes, never on translated text.

---

## 3. Seams (the bridges to neighbouring plugins)

- **Web UI implementation of locale-switching, lazy-loading, i18next/FormatJS wiring** →
  `frontend-engineering` (this plugin designs the i18n architecture; that plugin implements the
  component-level wiring and bundler config).
- **Mobile app i18n (Android `strings.xml`, iOS `.strings`/`.stringsdict`, Flutter ARB)** →
  `mobile-engineering` (this plugin advises on ICU, extraction strategy, and TMS integration; that
  plugin owns the platform-native implementation).
- **Translatable documentation, marketing copy, help content** → `technical-writing-docs` (this
  plugin handles engineering-side string catalogs; that plugin handles content authoring, style
  guides, and content-side TMS workflows).

---

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol
(decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured
Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in
each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the
dated capability map.

---

## 5. Knowledge bank

- **Canonical knowledge** (high trust): [`knowledge/i18n-l10n-decision-trees.md`](knowledge/i18n-l10n-decision-trees.md) —
  library/format choice, machine-vs-human translation, pseudo-loc CI gate, plus a dated 2026
  capability map of ICU/MessageFormat 2, i18next/FormatJS/gettext, TMS options (Phrase, Lokalise,
  Crowdin, Transifex). **Traverse the relevant Mermaid tree top-to-bottom before choosing.**

---

## 6. Milestones

- **v0.1.0** — initial build: 3 agents (i18n-architect, l10n-pipeline-engineer,
  localization-qa-engineer), 3 skills, 3 commands, 2 templates, the i18n/l10n decision-tree
  knowledge bank + dated 2026 capability map, 6 best-practice rules, and 1 advisory hook flagging
  i18n anti-patterns. Created 2026-06-08.

## 7. Runnable calculator (added v0.1.1)

[`scripts/i18n_calc.py`](scripts/i18n_calc.py) — stdlib-only, ruff-clean. Subcommands: `pseudo` (pseudo-localize a string with expansion + placeholder preservation), `expansion` (estimate target-language length growth + truncation risk vs a UI width), `plural-coverage` (check an ICU plural set covers a locale's CLDR categories). A calculator over user-supplied inputs, not a data source. _Cherry-picked from a parallel localization build during the 2026-06-08 marketplace reconciliation._
