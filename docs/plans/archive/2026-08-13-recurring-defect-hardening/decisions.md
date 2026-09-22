# Owner decisions — recurring-defect hardening (resolved 2026-08-13)

The build plan gated 4 PRs on owner decisions; 3 were answered directly by the owner, 1 was routed
(at the owner's request) to a fresh 3-model decision panel. Decisions 5–7 carry the agent's
recommendation to proceed on unless the owner overrides.

## The 4 gating decisions

### D1 — Count-SSOT / RC_BASELINE render oracle (gates PR 12) → **KEEP GOLDEN (option b)**
Routed to a 3-seat cross-model panel (Opus · Sonnet · Fable) at the owner's request.
**Verdict: (b), 2–1** — Sonnet + Opus for keep-golden, Fable for de-hardcode.
- The redundant `"N skills"`-style **prose counts are dropped everywhere** (README + `plugin.json` +
  `marketplace.json` descriptions) — this closes the copilot-freshness cascade and is settled.
- **RC_BASELINE stays a hand-maintained golden oracle**, NOT de-hardcoded. Reasoning: independence
  would be real (not a tautology), but (a) buys nothing on the actual dropped-card hazard (both go RED),
  goes blind to a consistent source deletion the golden catches, sheds the human "did you mean this?"
  checkpoint, and adds a demonstrated definition-drift footgun (`_scan_scripts` counts all `*.py`=19 vs a
  scanner spec of 18 → false RED). RC_BASELINE is a **test oracle, not consumer data**; its ~4-bump
  lifetime cost is trivial and was never the cascade count-SSOT targeted.
- **Build-plan effect:** PR 12 simplifies — drop the prose counts, add a one-line comment marking
  RC_BASELINE a *deliberate golden* (not a drift-target), and **do not** build the independent-scanner.
- Full panel record: `.ravenclaude/runs/forge/recurring-defects/rc-baseline-panel/seat-{opus,sonnet,fable}.md`.

### D2 — Sanctioned guard-escape door (gates PR 17) → **FUND THE RED-TEAM + BUILD IT**
Build the widened intent-vs-description escape for self-referential guards, behind a security review.
Justified by the run's own evidence — 5+ live guard false-positives on legitimate planning/verification
work (R6, the highest-frequency live failure). The low-risk half (nested-worktree + Write-scoped-matcher
fix) ships now regardless as **PR 2**, un-gated.

### D3 — macOS portability lint enforcement (gates PR 3) → **HYBRID warn→block knob, default WARN**
Matches the shipped `git_protocol` precedent: warns in-loop by default, settable to hard-block; the CI
`macos-latest` runner remains the backstop.

### D4 — Host behavioral-canary (gates PR 10) → **ADVISORY FIRST**
Non-blocking; surfaces a warning if a host's guardrails don't fire after install/update, gathers signal
before any move to a mandatory bar.

## Decisions 5–7 (agent recommendation — proceed unless overridden)
- **D5 — Sequencing:** keep the keystone-first P0→P1→P2 order as planned (gate-introspection meta-gate
  first, since it guards every subsequent gate). No change recommended.
- **D6 — DOM-budget ratchet formalization (PR 16, owner-optional):** **defer.** Formalizing the ratchet
  as a standing gate is low-leverage vs. the P0/P1 work; revisit if DOM churn recurs.
- **D7 — Advisory-only residual tail:** build the advisory phases that carry real signal (e.g. the
  delegation/claim-grounding-style nudges); drop any that would be pure ceremony. Agent's call at build
  time unless the owner wants to review the specific list.

## Net state
Build plan is decision-ready and unblocked: PR 2/3/4 (P0 band) can start immediately; PR 12 is simplified
per D1; PR 10 ships advisory; PR 17 proceeds once the security red-team is scheduled. **Nothing has been
built** — this initiative's DoD is the design plan + build plan + these decisions.
