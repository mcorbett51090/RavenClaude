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
| "Write the actual end-user product docs / API reference style guide" | `technical-writing-docs` |
| "Set product strategy / roadmap / discovery" | `product-management` |
| "Run martech / demand-gen / lifecycle campaigns" | `marketing-operations` |

---

## What's inside

- **4 agents** — `devrel-lead`, `developer-advocate`, `docs-and-dx-engineer`,
  `community-and-ecosystem-manager`.
- **3 skills** — [`devrel-program-design`](skills/devrel-program-design/SKILL.md),
  [`developer-content-and-advocacy`](skills/developer-content-and-advocacy/SKILL.md),
  [`developer-experience-measurement`](skills/developer-experience-measurement/SKILL.md).
- **3 commands** — `/design-devrel-program`, `/audit-developer-onboarding`, `/build-devrel-metrics`.
- **2 templates** — a DevRel strategy one-pager and a developer journey map.
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **A decision-tree knowledge bank** — [`knowledge/devrel-decision-trees.md`](knowledge/devrel-decision-trees.md).
- **An advisory hook** flagging DevRel anti-patterns (vanity metrics, content with no journey
  stage, community claims with no funnel).
- **A calculator** — [`scripts/devrel_calc.py`](scripts/devrel_calc.py) (stdlib only): time-to-first-value,
  activation rate, funnel conversion, content ROI, community health.

---

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install developer-relations@ravenclaude
```

Requires `ravenclaude-core` (inherited protocols). See [`CLAUDE.md`](CLAUDE.md) for the team
constitution and house opinions.
