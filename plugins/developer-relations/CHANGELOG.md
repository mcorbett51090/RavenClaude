# Changelog — developer-relations

All notable changes to this plugin are documented here. Versions follow semver;
the `version` field in `.claude-plugin/plugin.json` is the source of truth.

## 0.3.0 — 2026-06-22

Added a **conference-talk / CFP** capability — the one coherent gap the shipped plugin
lacked. Folded in from a parallel `developer-relations` build (PR #448) after this plugin
had already merged; only the genuinely-additive, non-duplicative idea was kept (the rest
of that PR duplicated existing skills/best-practices and was dropped). Owned by the
`developer-advocate` seat as an awareness-stage play.

- `skills/conference-talk-and-cfp/SKILL.md` — shape a talk + write a CFP abstract that
  leads with the attendee takeaway, states concrete takeaways, matches the track, and stays
  engineer-to-engineer (not demand gen).
- `commands/draft-cfp-abstract.md` — the command surface for the skill.
- `templates/cfp-abstract.md` — the fill-in abstract with the first-sentence test.
- `best-practices/cfp-abstract-leads-with-the-attendee-takeaway.md` — the house rule.
- Wired into `CLAUDE.md` (skills list), the `developer-advocate` agent (skill + a CFP
  scenario), and the best-practices index. Now 5 skills / 7 best-practices / 6 templates /
  5 commands.

## 0.2.0 — 2026-06-22

Added two best-practices (no overlap with the existing four):

- `invest-at-the-weakest-funnel-stage.md` — diagnose the activation funnel's weakest
  stage by its leading indicator and invest there, rather than pouring effort into more
  awareness when the leak is activation.
- `attribution-is-honest-or-absent.md` — report self-reported attribution and name the
  dark funnel explicitly; never fabricate an attribution number (ties to the inherited
  Claim-Grounding protocol).

Folded in from a parallel, since-superseded `developer-relations` proposal (PR #439)
after that plugin had already merged — only the genuinely additive ideas were kept.

## 0.1.0 — 2026-06-14

Initial release.

- 3 agents: `developer-advocate`, `devrel-content-engineer`,
  `developer-community-manager`.
- 4 skills: `getting-started-audit`, `sample-app-design`,
  `devrel-content-strategy`, `community-health-review`.
- 2-doc knowledge bank with Mermaid decision trees (advocate-vs-docs-vs-community,
  fix-the-product-or-document-it, content-format choice) plus a developer-
  experience playbook.
- 4 best-practices, 5 templates, 4 commands.
- 1 advisory anti-pattern hook (`flag-devrel-antipatterns.sh`) — flags getting-
  started docs with no first-success milestone and sample code with hardcoded
  secrets / swallowed errors.
- 1 worked scenario.
