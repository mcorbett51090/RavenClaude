<!--
  RavenClaude — value proposition copy (drop-in blocks for index.html).

  This is PROSE intended to be lifted into the landing page. It is deliberately
  plain markdown — no HTML wrapping — so it can be wrapped in the page's own
  markup (hero / section-title / card / chip) at paste time.

  Tone: measured / factual. Every concrete claim is grounded in a this-session
  source (README.md, docs/concepts.md, AGENTS.md, CLAUDE.md). Counts are quoted
  as the README states them on the source date below; where a figure is
  version-dependent it is phrased to age gracefully.

  Source date for all counts: 2026-06-04 (README.md "ships 24 plugins";
  ravenclaude-core component table: 14 specialists, 22 skills, 13 hooks).
  Re-verify the numbers against the README before publishing if time has passed.
-->

# RavenClaude — value proposition

## 1 · Headline + subhead

**An AI engineering team — and the harness that governs it — that travels with you across projects.**

RavenClaude is a private Claude Code plugin marketplace: one orchestrating lead, a roster of specialists, and the guardrails, memory, and verification that turn a single model into a team you can actually trust with real work. You decide what it's allowed to do on its own, with point-and-click settings rather than hand-edited config.

## 2 · What it is

RavenClaude is a **plugin marketplace for Claude Code** (and GitHub Copilot CLI). Its foundation is `ravenclaude-core` — a domain-neutral **Team Lead** plus 14 specialist agents (architect, coders, reviewers, designer, documentarian, researcher, project manager, and more), dispatch playbooks, 22 skills, 13 hooks, rules, and templates. Roughly two dozen domain plugins — for the Microsoft stack, Salesforce, web, data, finance, regulatory compliance, and more — all build on that one neutral core.

Underneath the catalog, RavenClaude is a **harness layer**: the software wrapping the model that supplies orchestration, memory, guardrails, and verification. A model on its own is stateless — it forgets earlier steps, tool calls fail quietly, and context fills with noise. RavenClaude rides on Claude Code's turn loop and adds the machinery that keeps a long task coherent and accountable.

## 3 · What it's trying to do

The goal is to make autonomous engineering work **dependable and bounded at the same time**:

- Turn one stateless model into a coordinated team that can carry a real task end to end.
- Keep every action inside an autonomy boundary the user sets — and shrink the interruptions down to genuine-preference calls, so you aren't asked to approve things a rule could already decide.
- Make accuracy something the system **enforces**, not something it hopes for. A turn doesn't end at "looks done"; it ends when the verification gates say it's done.

## 4 · How it creates value (how it does it)

Each point below is a real, shipped mechanism — not an aspiration.

- **An orchestrated team, not a single agent.** The Team Lead reads the request, picks the right specialist(s), and dispatches them through the `spawn-team` playbook. Every hand-off carries a structured-output envelope — summary, decisions, artifacts, open questions — so the next agent has full context. Sub-agents never spawn sub-agents; the Team Lead re-dispatches, keeping the dependency graph a flat, auditable tree.

- **Governance you own.** "Comfort posture" is a friendly front-end over Claude Code's permission model: set **deny / ask / allow** per *category* of action (file reads, code execution, remote changes…) and per *layer* (user / local / project), from a point-and-click dashboard instead of editing JSON. Permission level is deliberately separated from design judgment — relaxing permissions to move faster never silently mutes the architectural check-ins.

- **Tribunals instead of interruptions.** Two opt-in review panels adjudicate so the agent doesn't have to stop and ask you. *The Thing* (command review) votes ALLOW / EDIT / DENY on shell commands, with tiered routing that runs no panel at all on a clean low-risk read, a model-diversity rule so one model's blind spot can't pass the whole panel, and a Sága audit log that records every verdict. A sibling *decision-review* tribunal votes yes / no / defer on yes-or-no decisions. Both are off by default and fail safe — high-blast or irreversible calls always defer to you.

- **Oriented every session.** A SessionStart capability banner tells the agent what the project touches, what credentials it holds (names only — never values), and what its effective permissions are — so it never wastes a round-trip acting as if it has no access to something it's already authorized for.

- **Verification is enforced.** Every CI gate is itself tested: a meta-test proves each gate *fails* on a known-bad fixture and *passes* on a known-good one, so a gate can't quietly rot into a no-op. A definition-of-done gate and a claim-grounding discipline back it up. And a non-removable security floor — force-push, `rm -rf`, `curl | sh`, host-credential reads — cannot be edited away; the posture engine always unions it back in.

- **It travels with you.** The same agents, skills, and hooks run under both Claude Code and GitHub Copilot CLI, and updating is a `git pull` — no re-install. Your rules and team follow you from project to project, and a cross-project contribution-staging loop lets any consumer propose a hard-won lesson back to the marketplace without needing write access.

## 5 · Why it's different

Most plugins add a prompt, a slash command, or a handful of instructions. RavenClaude is a **system**: orchestration, governance, verification, and memory built on one neutral foundation, then extended across roughly two dozen domain plugins — each with citation-grounded knowledge banks and Mermaid decision trees the agent traverses *before* it picks a method.

Three differences stand out, stated plainly:

- **Governance is first-class and user-owned.** Permissions, review tribunals, and a security floor are part of the product — not an afterthought layered on by the user.
- **Accuracy is structural.** Self-testing gates, grounded claims, and decision-tree routing make correctness a property of the system rather than a matter of luck on any given run.
- **It's coherent, not a grab-bag.** Every domain plugin inherits the same neutral team and the same disciplines, so adding a specialty doesn't mean adopting a new mental model.

And the marketplace is built using its own discipline — RavenClaude develops RavenClaude — so the repository is the worked example of everything it claims.

## 6 · In short (single-block hero blurb)

RavenClaude is a governed AI engineering team for Claude Code. One orchestrating lead dispatches specialists; comfort-posture settings and review tribunals keep every action inside the autonomy boundary you set; and self-testing gates make accuracy something the system enforces rather than hopes for. Roughly two dozen domain plugins — Microsoft, Salesforce, web, data, finance, compliance, and more — all build on one neutral foundation, run under both Claude Code and Copilot CLI, and travel with you across projects.
