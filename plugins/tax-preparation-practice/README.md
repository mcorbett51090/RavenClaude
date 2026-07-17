# tax-preparation-practice

> The **tax-return-preparation layer** for Claude Code — the team that answers *"who do we serve and how do we survive busy season — and how do we prepare, review, and file this return right?"* and executes the answer. Two agents: the **tax-practice-lead** (sets the client-mix & niche, busy-season capacity & staffing, pricing/realization, the review standard & risk posture, and the Circular 230 / PTIN / EFIN governance) and the **tax-preparation-specialist** (drives the organizer, intakes documents, prepares 1040 / 1120 / 1120-S / 1065, self-reviews then routes to a separate reviewer, e-files, files extensions & estimates, responds to notices, and runs the planning calc).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

> **Not legal, tax, or accounting advice, and no substitute for a credentialed preparer.** Tax law, forms, thresholds, phase-outs, and filing deadlines are volatile and jurisdiction-specific — every rule carries a retrieval date, is verified against current IRS/state guidance before filing, and should be confirmed with a credentialed preparer.

## What it does

| You ask | It returns |
|---|---|
| "What client mix should our tax practice take, and who do we decline?" | A client-mix / niche recommendation (1040 vs business, complexity band) with an engagement-acceptance & risk-screen standard — grounded in the decision tree, with the conditions that would change it |
| "How do we survive busy season?" | A capacity plan: return volume × preparer-hours vs reviewed-hours, the preparer→reviewer staffing model, an extension policy as a load valve, and the realization targets that keep it sustainable |
| "Draft our engagement letter and client organizer." | The engagement letter (scope, fee basis, responsibilities, what's *not* included) and the organizer document-intake grid + completeness gate — the scope-creep and re-work control |
| "Prepare and e-file this 1040 / 1120-S / 1065." | A prepared return on the correct form & schedules, a completeness check, a self-review pass, the separate-reviewer sign-off gate, and the e-file/acknowledgment path |
| "We can't finish by the deadline." | An extension (4868 / 7004) filed to protect accuracy — with the estimated balance paid *with* it (file ≠ pay) — plus a quarterly-estimate schedule (safe-harbor vs annualized) |
| "The client got a CP2000." | A notice-response plan: the type & deadline, a reconciliation vs the return, the agree/partial/disagree response with substantiation, and the handle-vs-refer representation posture |
| "Should this client be an S-corp?" | A planning analysis: the SE-tax vs S-corp reasonable-comp trade-off, the QBI/§199A interaction, and retirement/timing levers — as scenarios with assumptions and a verify-against-current-law caveat |

**Two rules it never breaks:** *the engagement letter and organizer come before the first keystroke* (scope and documentation protect the client and the preparer), and *review is a separate step by a separate set of eyes* (self-prepared-and-self-reviewed is a risk, not an efficiency — a separate reviewer signs off before e-file).

## What's inside

- **2 agents** — `tax-practice-lead` (sets the client-mix & niche, busy-season capacity & staffing, pricing/realization, the review standard & risk posture, the representation stance, and the Circular 230 / PTIN / EFIN professional-standards governance) and `tax-preparation-specialist` (drives the organizer & document intake, prepares 1040 / 1120 / 1120-S / 1065 with schedules, self-reviews then routes to a separate reviewer, e-files & tracks the acknowledgment, files extensions & quarterly estimates, responds to IRS/state CP notices, and runs the entity/QBI/retirement/timing planning calc).
- **3 skills** — `plan-engagement-and-capacity`, `run-return-preparation-workflow`, `handle-notices-and-planning`.
- **2 knowledge files** — a Mermaid practice decision tree (engagement accept/decline, entity→form routing, prep→review→e-file, notice response, entity-choice/QBI + trade-off tables) and a 2026 tax-practice-patterns reference (the engagement/organizer intake, the entity→form map, the prep→separate-review→e-file pipeline, extensions & estimates, notices & representation, the planning levers, and the Circular 230 / PTIN / EFIN / WISP fence).
- **2 templates** — a client organizer & engagement letter and a return review & e-file checklist.

## Where it sits in the finance stack

```
tax-preparation-practice (HERE)  →  the RETURN and the PRACTICE that produces it  ("prepare, review, file — and run the firm that does")
accounting-bookkeeping           →  write-up / monthly close / the ledger          ("the books the return sits on")
wealth-management-ria            →  investment advisory & financial planning        ("the portfolio")
finance                          →  corporate FP&A / budgeting                       ("the earnings plan")
legal-small-firm                 →  entity-law / Tax-Court representation             ("the legal side")
```

This plugin is the **tax-return-preparation layer**: it prepares, reviews, and files the **return** and runs the **practice** that produces it, and stays clear of the *books* (`accounting-bookkeeping`), the *portfolio* (`wealth-management-ria`), and the *earnings plan* (`finance`).

## Domain stance

Concept-first (the engagement letter and organizer before the first keystroke, completeness-before-prep, the entity→form map — 1040 / 1120 / 1120-S / 1065 — separate-eyes review as a hard gate before e-file, the extension as a load valve that's to file not to pay, identify-notice-type-and-deadline-first, entity choice and QBI as one combined model, defensible-before-aggressive positions), fluent across **the busy-season capacity/realization model**, the **8879 / EFIN** e-file mechanics, **extensions (4868 / 7004) vs quarterly estimates** (safe-harbor vs annualized), **CP-notice response** and the **preparer-vs-attorney representation** line, the **SE-tax vs S-corp reasonable-comp** trade-off with **§199A / QBI**, and the **Circular 230 / PTIN / EFIN / WISP** professional-standards fence. Forms, line numbers, thresholds, phase-outs, safe-harbor percentages, and deadlines carry retrieval dates — re-verify against current IRS/state guidance (and confirm with a credentialed preparer) before filing. **Not legal, tax, or accounting advice.**

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install tax-preparation-practice@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
