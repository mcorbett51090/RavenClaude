# developer-relations

The **developer-experience operating engine** for a DevRel team — designing the DevRel program,
running developer advocacy, building the docs and onboarding that get a developer to first value,
and growing a healthy community and ecosystem.

> **The one-line philosophy:** developer experience is the product. Every talk, doc, demo, and
> community thread is justified by how much it moves a developer from *signed up* to *activated* to
> *successful in production*.

---

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Design our DevRel program / make the case to the exec team" | **developer-relations** (`devrel-lead`) |
| "Plan our content, conference talks, demos, and advocacy" | **developer-relations** (`developer-advocate`) |
| "Fix our onboarding / quickstart / time-to-first-value" | **developer-relations** (`docs-and-dx-engineer`) |
| "Grow our community / ambassador program / contribution funnel" | **developer-relations** (`community-and-ecosystem-manager`) |
| "Fix our positioning / who we reach / which channels drive activations" | **developer-relations** (`developer-marketing-and-growth-strategist`) |
| "Which conferences to invest in / set up content ops / operating review" | **developer-relations** (`devrel-programs-and-operations-manager`) |
| "Write the actual end-user product docs / API reference style guide" | `technical-writing-docs` |
| "Set product strategy / roadmap / discovery" | `product-management` |
| "Run martech / demand-gen / lifecycle campaigns" | `marketing-operations` |

---

## What's inside

- **6 agents** — `devrel-lead`, `developer-advocate`, `docs-and-dx-engineer`,
  `community-and-ecosystem-manager`, `developer-marketing-and-growth-strategist`,
  `devrel-programs-and-operations-manager`.
- **8 skills** — `devrel-program-design`, `developer-content-and-advocacy`,
  `developer-experience-measurement`, `developer-onboarding-funnel-engineering`,
  `sample-app-and-demo-engineering`, `conference-talk-and-cfp-strategy`,
  `developer-community-funnel-design`, `developer-marketing-positioning-and-roi`.
- **6 commands** — `/design-devrel-program`, `/audit-developer-onboarding`, `/build-devrel-metrics`,
  `/plan-developer-content`, `/design-community-program`, `/prepare-conference-talk`.
- **5 templates** — a DevRel strategy one-pager, a developer journey map, a content plan by journey
  stage, a community-health scorecard, and a conference-talk brief.
- **12 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **A 5-doc knowledge bank** — [`knowledge/devrel-decision-trees.md`](knowledge/devrel-decision-trees.md)
  plus onboarding/activation, content/advocacy, community/ecosystem, and metrics/ROI references.
- **A scenarios bank** — [`scenarios/README.md`](scenarios/README.md) (field-tested cases).
- **An advisory hook** flagging DevRel anti-patterns (vanity metrics, content with no journey
  stage, community claims with no funnel).
- **A calculator** — [`scripts/devrel_calc.py`](scripts/devrel_calc.py) (stdlib only): time-to-first-value,
  activation rate, funnel conversion, content ROI, community health, cost-per-activation.

---

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install developer-relations@ravenclaude
```

Requires `ravenclaude-core` (inherited protocols). See [`CLAUDE.md`](CLAUDE.md) for the team
constitution and house opinions.
