# sales-engineering

> A RavenClaude plugin: the **pre-sales / sales-engineering team** — the technical side of a B2B sale, from discovery to signature.

Three specialist agents cover the deal's technical arc:

- **sales-engineer** — value-based technical discovery (MEDDPICC), pain-mapped demo design (Great Demo!), technical objection handling, and the mutual action plan.
- **poc-evaluation-lead** — the proof-of-concept / pilot: the go/no-go gate, signed measurable success + exit criteria, the time-boxed plan, and the evaluation scorecard.
- **rfp-security-response-specialist** — RFP/RFI/RFQ go/no-go + response matrix, and security/vendor-risk questionnaires (SIG / CAIQ / VSA) mapped to SOC 2 / ISO 27001 evidence, plus a reusable trust-answer library.

## What it's for

| You want to… | Ask for… | The agent |
|---|---|---|
| Prep a discovery call / uncover quantified pain | "What should I uncover with `<prospect>`?" | sales-engineer |
| Build a demo that maps to pain, not features | "Build a demo for `<prospect>` who cares about `<pain>`" | sales-engineer |
| Handle a technical objection honestly | "They said `<objection>` — how do I respond?" | sales-engineer |
| Keep the deal on track to a decision | "Give me a mutual action plan" | sales-engineer |
| Decide whether a POC is even warranted | "Should we run a POC?" | poc-evaluation-lead |
| Write success criteria a champion will sign | "Define POC success criteria for `<prospect>`" | poc-evaluation-lead |
| Score a finished POC → technical win | "The POC is done — did we win?" | poc-evaluation-lead |
| Decide whether to bid an RFP | "Should we respond to this RFP?" | rfp-security-response-specialist |
| Structure a compliant RFP response | "Help me respond to this RFP" | rfp-security-response-specialist |
| Answer a security questionnaire honestly | "Fill out this SIG / CAIQ" | rfp-security-response-specialist |

## House opinions (what makes it opinionated)

1. **Discovery before demo — always.** A demo with no discovered, quantified pain is a feature tour, and a feature tour loses.
2. **Honesty over the fabricated yes.** Shipped / roadmap / not-supported, every time. The deals you win on a lie you lose in the POC.
3. **A POC needs signed, measurable exit criteria.** A POC you can't fail is one you can't win.
4. **No-bid is a strategy.** Decline the unwinnable and incumbent-wired RFPs.
5. **Map every security claim to evidence.** A "yes" with no control behind it is a clawback risk.

## What's inside

- **3 agents**, **5 skills**, a **4-doc knowledge bank** with 4 Mermaid decision trees, **5 templates**, **5 best-practices**, a **2-scenario bank**, and **1 advisory anti-pattern hook** (`flag-se-antipatterns.sh`).

## Boundaries (what this plugin is NOT)

- **Not `sales-revops`** — that owns CRM hygiene, forecast, quota, deal-desk, and comp (the systems and numbers of selling). This plugin owns the technical persuasion of a single deal.
- **Not `product-management`** — that owns what to build and why. This plugin routes a real product gap there.
- **Not a security-review authority** — every security claim routes to `ravenclaude-core/security-reviewer` for the verdict; the SOC 2 / ISO program lives in `cybersecurity-grc` / `security-engineering`.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install sales-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0` (inherits its Capability Grounding + Structured Output protocols).

## License

MIT © Matt Corbett. See the team constitution in [`CLAUDE.md`](CLAUDE.md).
