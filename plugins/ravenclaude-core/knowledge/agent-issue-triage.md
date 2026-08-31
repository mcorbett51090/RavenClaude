# Agent issue-triage — operating GitHub Issues as a primary actor

> **Last verified:** 2026-08-13. **Refresh trigger:** re-verify if GitHub changes the closing-keyword
> auto-close rules, the issues REST `state_reason` semantics, or the frontier resolver trigger tokens.
> The external facts here were sourced from the GitHub docs on 2026-08-13 and live in the run's
> `research/external.md` §1.

This file is the **issue-triage half** of "an agent as a GitHub actor" — the companion to
[claude-in-ci.md](claude-in-ci.md) (the in-CI wiring), [agent-pr-identity.md](agent-pr-identity.md)
(identity & attribution), and [github-actions-hardening.md](github-actions-hardening.md) (workflow
security). It answers one question: **when a RavenClaude agent triages, labels, links, and closes
GitHub issues, what is the minimal, referenced, verifiable action shape — and which API behaviors do
naive agents silently break on?**

**Who consumes it:** an agentic AI CLI that is about to comment on, label, link, or close a GitHub
issue as a primary actor. Each point is either a rule the agent applies or a fact it should not
misstate — never just "nice to know." Every point carries a provenance marker.

**Provenance legend** — **[obs]** = a source demonstrably says this, checked 2026-08-13 (with the
backing claim from `research/external.md` where external) · **[inf]** = a conclusion drawn from named
evidence · **[unverified — training knowledge]** = recalled, not checked this session (with what would
verify it).

---

## 1. The minimal triage action shape — comment → label → link → close-with-a-reason

Treat a triage action as this ordered, minimal, **referenced** sequence — never a bare mutation
**[obs, claim 3; inf for the synthesis]**:

1. **Comment a plan on the issue *before* mutating.** State the classification and what the agent will
   attempt, so a human reading the thread sees the intent before any label or state change lands
   **[obs, claim 3]**.
2. **Apply at most one or two labels — from the repo's OWN existing label set.** Read the repo's label
   set first (via the API) and pick from it; **never invent a label**. Labels are free-form per-repo,
   so a label the agent guesses at is either a no-op or noise **[obs, claim on label taxonomies;
   unverified — training knowledge for any *specific* default-label list]**.
3. **Link the resolving PR.** Put `Closes #N` (or `Fixes #N`) in the PR body when — and only when —
   the PR targets the repository's default branch (§2); otherwise link the PR explicitly and close the
   issue via the API **[obs, claim 1]**.
4. **Close with a reference AND a reason.** Send `state: "closed"` together with
   `state_reason: "completed"` **and** a reference to the resolving PR/commit; use `not_planned` or
   `duplicate` for a triage disposition rather than a fix (§3) **[obs, claim 2]**.

**Confidence for the sequence as a whole: Medium** — the individual conventions in §2–§3 are
High-confidence sourced facts; this ordering is their synthesis, not a single cited "best-practice"
doc **[inf]**.

---

## 2. Trap 1 — closing keywords auto-close ONLY on a default-branch PR

A PR body (or a commit message) carrying a closing keyword followed by an issue reference —
`Closes #N`, `Fixes #N`, `Resolves #N`, and their conjugations — **auto-closes that issue AND creates
a bidirectional cross-reference** between the PR and the issue **when the PR is merged**
**[obs, claim 1]**.

> ⛔ **The load-bearing restriction: DEFAULT BRANCH ONLY.** GitHub's docs state the keywords are
> interpreted *"only when the pull request targets the repository's default branch"* **[obs, claim 1]**.
> So a PR opened into a **release/feature base** does not get its issue auto-closed by the keyword; the
> documented remedy is to close the issue explicitly (§3) rather than depend on the keyword **[obs,
> claim 1]**.

- **Same-repo form:** `Closes #123`. **Cross-repo form:** `Fixes owner/repo#100`. Colon and case are
  tolerated (`Closes: #10`, `CLOSES #10`); multiple issues take repeated keywords
  (`Resolves #10, resolves #123`) **[obs, claim 1]**.
- **The fallback an agent must build in:** when the resolving PR does **not** target the default
  branch, the agent closes the issue **explicitly via the API** (§3) and links the PR by hand rather
  than depending on the keyword **[obs, claim 1]**. An agent that opens PRs into a non-default base and
  trusts the keyword risks a **silent no-close** — the issue stays open because the auto-close never
  fired **[inf]**.

---

## 3. Trap 2 — `state_reason` is ignored without a `state` change, and the API silently drops what it can't do

Closing an issue and *resolving* it are distinct. The REST call
`PATCH /repos/{owner}/{repo}/issues/{n}` carries a `state_reason` alongside `state` **[obs, claim 2]**:

- **Values:** `completed` (resolved/fixed), `not_planned` (won't be actioned), `duplicate`,
  `reopened`, and `null` (clears the reason) **[obs, claim 2]**.
- ⛔ **`state_reason` is IGNORED unless `state` is also changed in the same call.** To set a reason the
  agent must send `state: "closed"` (or `open`) in the same request **[obs, claim 2]**.
- **Duplicate marking:** close with `state_reason: "duplicate"` **and** provide `duplicate_issue_id` to
  record which issue it duplicates **[obs, claim 2]**.
- ⛔ **The issues API SILENTLY DROPS a change the caller lacks permission for** — the *silently-drops*
  behavior. Per the docs, only push/triage roles can reliably set state + reason, so an under-scoped
  token's "close" is silently dropped and can look successful while nothing changed **[obs, claim 2]**.

**The rule that falls out:** the agent must (a) hold the right token scope, and (b) **verify the close
actually landed** — re-read the issue's `state`/`state_reason` after the call rather than assuming it
took effect **[obs, claim 2; inf for the verify-after-write rule]**. This is exactly what the
`srm.issue-close-without-reference` tribunal anchor now enforces (§5).

---

## 4. The rate- and blast-conscious guardrails

Four disciplines keep a triage loop cheap and quiet:

- **Duplicate-search BEFORE create.** Run a search query for an existing issue before opening a new
  one; GitHub's own agent tooling treats *"search issues before creating new issues to avoid
  duplicates"* as mandatory **[obs, claim from the github MCP server guidance, this session]**.
- **Never close `completed` without a reference.** A `completed` close with no linking PR/commit is
  unauditable and often wrong **[obs, claim 2; inf]**.
- **Bounded bulk relabel — a per-run cap.** Bulk label churn is low-value, high-noise, and the classic
  runaway signal. Bound it with a rate limit **and** a per-run cap on how many issues one triage pass
  relabels **[inf, mirroring the marketplace's runaway-brake ethos]**.
- **Read throttling.** The API enforces secondary rate limits on rapid access, and agents in tight
  `view`-loops have broken downstream tooling — batch reads and throttle. See the
  `shr.gh-api-rate-limit-risk` concern in [concerns-catalog.md](concerns-catalog.md), whose resolution
  names the search-before-create dedupe as part of the same rate-conscious pattern **[obs — internal]**.

---

## 5. Safety — issue mutation at scale is a mutating GitHub action

An agent that closes or relabels issues is performing a **mutating GitHub action**, so it sits behind
the same review posture as any remote mutation. The tribunal anchor is
`srm.issue-close-without-reference` in [concerns-catalog.md](concerns-catalog.md) — a `judgment_only`
concern that now names the `state_reason`-needs-a-state-change and *silently-drops* traps and calls for
a reference plus a verified-landing close **[obs — internal]**. Bulk churn is additionally bounded by
the per-run cap in §4 and the marketplace's runaway brake **[inf]**.

---

## 6. Frontier resolver shape — mirror the flow, not the trigger token

The frontier issue-resolvers (OpenHands, SWE-agent) follow an **issue → attempt → a PR that links the
issue → a status comment back on the issue** flow **[obs, claim 4]**. Mirror that *shape*; do **not**
hard-code the trigger.

- **OpenHands** ships a GitHub issue resolver triggered historically by applying a label or an
  `@`-mention on an issue, which attempts a fix in a sandbox and opens a (draft) PR referencing the
  issue **[unverified — training knowledge for the exact 2026 trigger token; the docs page 404'd this
  session]**. **`[verify-at-use]`** — resolve the current trigger token against the live OpenHands docs
  at the moment you wire it; **do not hard-code a historical token** into any automation **[obs,
  claim 4]**.
- **SWE-agent** takes a GitHub issue and produces a fix **patch** via an agent-computer interface;
  SWE-bench is the separate evaluation benchmark, **not** a component of the agent **[obs, claim 4]**.

---

## What this means for RavenClaude

- A triage action is **never a bare close** — it is comment → label-from-the-repo's-own-set → link →
  close-with-a-reference-and-a-reason, then **verify the close landed** `[inf]`.
- The two facts naive agents break on are **default-branch-only auto-close** (§2) and **`state_reason`
  ignored without a `state` change / silently-dropped mutations** (§3) — encode both, don't relearn
  them at 2 a.m. `[obs, claims 1–2]`.
- Issue mutation is a **mutating GitHub action**; it is governed by the existing
  `srm.issue-close-without-reference` anchor, not a new enforced surface — this file is the reference
  an agent reads, enforced by nothing new `[inf]`.
