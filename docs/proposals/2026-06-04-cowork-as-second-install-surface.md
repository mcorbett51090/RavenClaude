---
proposal_id: 2026-06-04-001
proposed_at: 2026-06-04
proposed_by: claude
status: awaiting-decision
topic: distribution / marketplace-positioning / install-surface
last_updated: 2026-06-04
related_asks:
  - From the features gap analysis (docs/research/2026-06-04-claude-features-gap-analysis/gap-analysis.md) gap B4
decision_owner: matt
---

# Proposal: should RavenClaude claim Claude Cowork as a second install surface?

_Prepared for RavenClaude review — 2026-06-04. This is a **decision write-up, not a build** — it gathers what adopting a second surface would take and gives a recommendation; the go/no-go is Matt's._

---

## Problem statement

The [features gap analysis](../research/2026-06-04-claude-features-gap-analysis/gap-analysis.md) (gap **B4**) noticed that the prompting article describes **Skills installing into Claude Cowork** ("Cowork → Customize → Skills … Browse plugins → install"), and lists **Cowork** (desktop app, filesystem access) and **Scheduled Tasks** as first-class consumer surfaces. RavenClaude today positions **exclusively** as a *Claude Code* plugin marketplace — every install path (`/plugin marketplace add`, `/plugin install …@ravenclaude`, the Bifröst wizard) targets Claude Code. The question: is Cowork a **second audience worth claiming**, or is Claude-Code-only a deliberate focus we should keep?

## What we actually know vs. assume

| Claim | Status |
|---|---|
| Cowork installs plugins/skills via a "Browse plugins → install" UI | `[unverified — from the article's screenshots; not checked against Anthropic docs this session]` |
| Cowork reads `CLAUDE.md` and skills like Claude Code does | `[unverified — training/likely; the article asserts CLAUDE.md works in "Cowork and Claude Code"]` |
| Cowork honors `PreToolUse`/`Stop` **hooks** (the guard layer) | `[unverified — and this is the load-bearing unknown — see Risks]` |
| RavenClaude's value is mostly skills + knowledge + agents (portable) **plus** hooks (maybe not) | Verified in-repo: the guard/tribunal layer is hook-driven |

**Before any build, the first action is to verify the three `[unverified]` rows against current Anthropic Cowork docs** — the whole cost/benefit pivots on whether Cowork fires hooks.

## What adopting Cowork would take (rough scope)

1. **Skills + knowledge + agents** — likely **already portable**. They are markdown under `.claude/skills` etc.; if Cowork reads those paths, most of the catalog "just works."
2. **Hooks (the guard layer)** — the open question. If Cowork has **no** `PreToolUse`/`Stop` hook lifecycle, then `enforce-layout.sh`, `guard-destructive.sh`, the tribunal, `runaway-brake.sh`, and `dod-gate.sh` **do not run** there — i.e. Cowork users would get the *agents and skills* but **not** the safety envelope. That is a materially weaker product and must be stated honestly, not papered over.
3. **A generated Cowork package** — mirror the existing `generate-copilot-plugin.py` pattern (we already project the canonical plugin into a Copilot package; a Cowork projection would be the same shape: generated, never hand-maintained, freshness-gated).
4. **Docs + an install path** — a Bifröst-style wizard tab or a README section.

This is **not** a small lift if hooks need a Cowork adapter (cf. the `copilot-hook-adapter.sh` effort), and is **near-zero** if Cowork reads `.claude/skills` directly and we ship skills-only with an explicit "no guard layer on this surface" caveat.

## Options

| Option | What it means | When it's right |
|---|---|---|
| **A — Don't claim Cowork (keep Claude-Code focus)** | Status quo. One surface, fully guarded. | If the guard layer is core to the product's identity and Cowork can't run hooks. **Recommended default.** |
| **B — Skills-only on Cowork, explicitly unguarded** | Ship the portable catalog (skills/knowledge/agents) to Cowork with a loud "the tribunal/guards don't run here" caveat. | If there's real demand and the verification shows skills port cleanly. Low cost, honest about the gap. |
| **C — Full Cowork port incl. a hook adapter** | Build a Cowork hook adapter so the guard layer runs there too. | Only if Cowork has a hook lifecycle **and** demand justifies the adapter cost. |

## Recommendation

**Default to Option A (don't claim Cowork yet), with a cheap, time-boxed verification gate before reconsidering.** Reasoning:

- The repo's differentiator is increasingly the **guard/tribunal/posture** layer, which is hook-driven. Shipping to a surface that can't run it (Option B) risks the brand promise ("opinionated, guarded") on the surface where users are *least* technical.
- There is **no observed consumer ask** for Cowork today — the same "wait for ≥1 real consumer ask" discipline the repo applied to decision-tree fork-with-attribution (proposal 2026-05-21-001) applies here.
- The verification is cheap: **confirm whether Cowork fires hooks**. If yes → Option C becomes plausible and worth a real plan. If no → Option B is the ceiling, and only worth it on demand.

**Concretely:** keep Claude-Code-only; revisit if (a) a real user asks for Cowork, **or** (b) Anthropic ships a documented hook lifecycle for Cowork. Until then this proposal sits at `status: awaiting-decision` and no packaging work starts.

## Decision (Matt)

- [ ] **A — keep Claude-Code-only** (recommended)
- [ ] **B — skills-only Cowork port, explicitly unguarded** (needs the hook-verification first)
- [ ] **C — full Cowork port with a hook adapter** (only if Cowork runs hooks + demand)

## See also

- [Features gap analysis (2026-06-04)](../research/2026-06-04-claude-features-gap-analysis/gap-analysis.md) — gap B4.
- [`plugins/ravenclaude-core/CLAUDE.md`](../../plugins/ravenclaude-core/CLAUDE.md) → "GitHub Copilot CLI bridge" — the precedent for projecting the canonical plugin onto a second host via a generated package + hook adapter.
