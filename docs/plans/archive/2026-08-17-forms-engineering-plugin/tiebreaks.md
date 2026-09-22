# G4b — Single-conflict expert tiebreak

**Run:** `forms-process-expertise` · **Date:** 2026-08-17 · **Question:** how many agents does the
proposed `forms-engineering` plugin ship, ruled under the CARVE-OUT clause
(`plugins/ravenclaude-core/CLAUDE.md:22`, `:24`) rather than the indistinguishable-output clause
(`:11`) both panels used.

---

## VERDICT: `zero-agents`

**Rationale (one line):** the panels reached the right number by the wrong clause — under the
carve-out the split is **not clean**, because forms' *hygiene* half is the deeper, better-evidenced
body (already owned at `ravenclaude-core/rules/security.md:42-45`,
`ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md:51,53`,
`web-design/agents/frontend-implementer.md:41,48,60`, `web-design/agents/accessibility-auditor.md:48`)
and the residue left for the plugin is a **seam between three existing owners**, not a specialist body
the carve-out was written to admit.

**This is a confirmed outcome reached by corrected reasoning, not a changed one.** The panels' stated
ground (`plan-A.md:60,75`; `plan-B.md:44-51`) does not survive; the conclusion does. Their cost
arithmetic (`plan-A.md:36,75`; `plan-B.md:51-54`) does **not** survive either — see *Budget cost*.

---

## The carve-out test, applied

### The clause, read in full

- `:22` — *"The rule's strictest grip is on **review** roles (security-reviewer, architect), which never
  fork. A **generalist** concern may earn its own plugin when it splits cleanly into 'domain-neutral
  hygiene' (stays core) and 'deep specialist craft' (the plugin)."* Litmus: *hygiene → core; running
  the project → the plugin.* Qualifier in the same line: *"it earns the split only because PMBOK/PMP +
  the Agile canon is a genuine specialist body the core generalist doesn't carry."*
- `:24` — the `memory-engineering` admission on the same litmus: *the discipline every agent inherits →
  core; engineering a memory system → the plugin.* Same line: **"Memory security does not fork a
  reviewer"** — ASI06 ships as `memory-engineering/skills/memory-poisoning-review/SKILL.md` invoked by
  core `security-reviewer` via an inline prior.

Both carve-out plugins did ship agents — verified: `ls plugins/project-management/agents/*.md | wc -l`
→ **4**; `ls plugins/memory-engineering/agents/*.md | wc -l` → **3**. Neither plan cites either
carve-out: `grep -c "carve-out" plan-A.md plan-B.md` → **0 / 0** (positive control: `grep -c "house
rule" plan-A.md` → **8**, so the instrument reads this corpus). The critic (CE-3) is correct on facts.

### The split, named explicitly

| Half | What lands there | Owner (verified path:line) |
|---|---|---|
| **HYGIENE — stays core / web-design** | Untrusted filenames; path-traversal resolve-then-assert; magic-byte type validation; size cap at the boundary | `plugins/ravenclaude-core/rules/security.md:43,44,45` |
| | Turnstile: 300-second token lifetime, single-use replay rule, server-side `siteverify` at submit, hostname-covers-subdomains / no wildcards, Access-vs-Turnstile-vs-WAF boundary — dated, sourced, with a `refresh_when:` clause | `plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md:10,20-21,51,53,73` |
| | Native HTML form patterns, `<label>`+`<input>` association, `required`/`pattern`/custom validation *strategy*, "placeholder is not a label" | `plugins/web-design/agents/frontend-implementer.md:32,41,48,60` |
| | Form a11y: labels, instructions, `aria-describedby` error association, required indication, validation timing | `plugins/web-design/agents/accessibility-auditor.md:48` |
| | Field-count / perceived-complexity → completion (Baymard 41,000+ checkouts), and mid-form abandonment as a **UX** diagnostic | `plugins/web-design/knowledge/gold-standard-website-references-2026.md:75`; `plugins/web-design/knowledge/web-design-decision-trees.md:240,261` |
| **CRAFT — candidate for the plugin** | (a) forms-as-instrumented-process: intake→triage→routing, field-level SLA, abandonment-as-defect, telemetry feeding a control chart | *unowned as a named pattern* |
| | (c-server-half) server validation parity, honeypot / time-trap bot defense, submission idempotency, webhook verification, PII minimisation | *partly unowned* |
| | (d) platform selection axes | *unowned* |

Genuinely-unowned probes re-run this session (instrument first): `grep -rl -i "abandonment" plugins/`
→ **23 files** across 10 plugins, so the instrument returns large non-zero on owned topics.
Subject: `grep -rl -i "honeypot" plugins/` → **0**; `grep -rl -i "form abandonment" plugins/` → **0**.
Those two zeros are real. But the 23-file control also **narrows the finding**: `web-design` already
owns mid-form abandonment as a conversion diagnostic (`web-design-decision-trees.md:240,261`). What is
unowned is abandonment *as a process defect stream*, not abandonment.

### Why the split is NOT clean — three independent reasons

**1. The direction of depth is inverted relative to both precedents.**
In `project-management`, the core half is thin hygiene (`ravenclaude-core/project-manager` — RAID log,
status, activity log) and the plugin half is a *larger, categorically different* body (PMBOK baselines,
earned value, Scrum ceremonies, quantified risk registers) — `CLAUDE.md:22`. In `memory-engineering`,
the core half is a **protocol** every agent inherits and the plugin half is the paradigm/surface/
retention/economics literature — `CLAUDE.md:24`. Forms inverts this: the hygiene half is the *deeper,
dated, sourced, refresh-triggered* body (`cloudflare-who-gets-in.md:10` carries an explicit
`refresh_when:`; `gold-standard-website-references-2026.md:75` carries a 41,000-checkout benchmark),
and the plugin residue is thinner than the half it is supposed to extend. The carve-out's own qualifier
— *"a genuine specialist body the core generalist doesn't carry"* — is not satisfied.

**2. The one candidate discipline is a slice of an existing agent's body, not a new body.**
Discipline (a) is the join of a form artifact with `process-improvement`'s DMAIC/SPC craft. Verified
roster: `plugins/process-improvement/agents/process-analyst.md` (SIPOC / swimlane / value-stream, *"plan
data collection for a baseline"*, 8 wastes, Pareto / cycle-time) and
`plugins/process-improvement/agents/lean-six-sigma-blackbelt.md` (full DMAIC, sigma/DPMO/capability,
control plan). A `form-process-analyst` would sit beside `process-analyst` with a *narrower* mandate on
the *same* rubric. That is textbook **dispatch ambiguity** and **rubric drift** —
`ravenclaude-core/CLAUDE.md:20`, the two failure modes the carve-out **relaxes the presumption
against but does not abolish**. `project-management` avoided this by taking a body core never had;
a forms agent cannot, because `process-improvement/CLAUDE.md`'s agents already hold the reasoning and
only the artifact changes.

**3. The genuinely-unowned half is the half the rule forbids forking even inside a carve-out.**
Settlement Claim 31 established that `web-design` *routes security OUT by rule* —
`plugins/web-design/agents/accessibility-auditor.md:92`: *"Auth / login / CAPTCHA surfaces … →
`ravenclaude-core` `security-reviewer` (mandatory, zero-exception whenever the surface handles auth /
sessions / PII)."* So the unowned residue of (c) is precisely a security-review lane. `CLAUDE.md:24`
settles this with a worked example: **memory-engineering, an admitted carve-out, still refused to fork
a reviewer** and shipped `memory-poisoning-review` as a skill on core's `security-reviewer`. The
carve-out therefore *cannot* license a forms security agent; it explicitly declines to.

**Net:** forms is a **seam**, not a generalist concern with two clean halves. It has three adjacent
owners (`web-design` for construction + a11y + conversion evidence, `process-improvement` for the
process reasoning, `ravenclaude-core` for the trust boundary and upload/Turnstile hygiene) and the
value it adds is the *join*. A join ships as skills with reciprocal priors — that is exactly what
`:11` prescribes and what the carve-out does not override.

---

## Per proposed agent

**Proposed count: 0.** The three candidates that survived to a serious hearing, and why each is refused:

### Candidate 1 — `form-intake-architect` (discipline (a): forms as instrumented process) — **REFUSED**
- **Mission it would carry:** first contact for "a form is the front door of a process" — field
  taxonomy that makes triage deterministic, routing rules, field-level SLA clocks, partial-submission /
  abandonment telemetry as a defect stream, baseline handed to SPC.
- **Why a core agent + skill CAN produce it:** the reasoning specialty is the process side, and
  `process-improvement/agents/process-analyst.md` already owns *"plan data collection for a baseline"*
  and current-state mapping; `lean-six-sigma-blackbelt.md` owns the control plan the telemetry feeds.
  What the agent would add over `process-analyst` + a `form-as-process-instrument` skill is a
  **telemetry-event taxonomy and a decision tree's worth of form-specific priors** — the precise
  artifact `ravenclaude-core/CLAUDE.md:13-16` deleted `data-platform-architect` for being.
- **The strongest counter, and why it loses:** `plan-B.md:392-402` admits the zero-agent shape produces
  a plugin nothing routes to — *"a documented rot pattern in this repo … a real, accepted trade-off,
  not a solved problem."* That is an argument for **discoverability**, and discoverability is not the
  carve-out's test. `CLAUDE.md:11` already names the sanctioned fix: *"ship a skill (with an inline
  prior on the relevant core agent pointing at it)"* — `plan-A.md` Phase 9. Buying reachability with an
  agent pays budget **and** rubric drift for a problem a prior solves for free.
- **Reversibility check:** adding one agent later if the priors measurably under-land is cheap;
  deleting a shipped agent after downstream `works_with` edges form is not. Zero is the cheap direction.

### Candidate 2 — `form-hardening-engineer` (discipline (c) server half) — **REFUSED, categorically**
- Would own server-side validation parity, honeypot/time-trap bot defense, uploads, idempotency,
  webhook verification, PII.
- **Refused not on the indistinguishable-output test but on `:22`/`:24` themselves:** review roles
  never fork, and the admitted carve-out `memory-engineering` demonstrates the compliant shape
  (`memory-poisoning-review` skill on core `security-reviewer`). Sibling precedent for the same content
  already exists at `plugins/web-commerce/agents/commerce-webhook-security-reviewer.md`, whose binding
  verdict still routes to `ravenclaude-core/security-reviewer`.

### Candidate 3 — `form-platform-selector` (discipline (d)) — **REFUSED**
- Decision-axis checklist. `data-platform/skills/stack-selection/SKILL.md` is the canonical shape and is
  the case the house rule was *extracted from* (`ravenclaude-core/CLAUDE.md:13-16`). Not arguable.

### Boundary the plugin must honour regardless of agent count (binding, from G3b Claim 31)
The plugin **MUST NOT** own:
- client-side form implementation — native form patterns, `<label>` association, `required`/`pattern`
  validation strategy → `plugins/web-design/agents/frontend-implementer.md:41,48,60`;
- form a11y — labels, instructions, `aria-describedby` error association, required indication,
  validation timing → `plugins/web-design/agents/accessibility-auditor.md:48`.

And it **MUST CITE, NEVER RESTATE**:
- `plugins/ravenclaude-core/rules/security.md:43-45` (upload hygiene);
- `plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md:51,53` (Turnstile 300s /
  single-use / server-side `siteverify` / hostname rules).
Restating either is the rubric drift `CLAUDE.md:20` names, and `cloudflare-who-gets-in.md:10`'s
`refresh_when:` clause means a copy silently rots the moment Cloudflare moves.

---

## Budget cost of this recommendation

**Against the ~15K agent-description budget: 0 bytes.** Literally true, and it is the only sense in
which the panels' "zero cost" claim holds.

**Against always-on session context: NOT zero, and larger than the agents would have been.** Measured
this session:

| Surface | Always-on frontmatter (`name`+`description`) |
|---|---|
| `memory-engineering` — 6 skills | **1,552 bytes** |
| `process-improvement` — 6 skills | **1,601 bytes** |
| `memory-engineering` — 3 agents | 327 + 278 + 332 = **937 bytes** |
| `web-design` — 7 agents | **1,890 bytes** |

Mechanism: *"A skill loads in three tiers — frontmatter (`name`+`description`) preloaded for **every**
skill every session"* — `docs/research/2026-06-24-claude-subreddit-scan/README.md:56`. And the
`/plugin` Discover tab prices install as *"tokens added to every turn"*, enumerating
*"commands/agents/skills/hooks/MCP+LSP servers"* together —
`docs/research/2026-06-21-claude-subreddit-scan/README.md:53`.

**Honest price of a ~6-skill + ~1-command zero-agent `forms-engineering`:** ≈ **1,600–1,800 bytes**
(~400–450 tokens) added to every session for anyone who enables it — roughly **1.7× what three agent
descriptions would have cost**. The critic (CE-4) is right: *zero agents ⇒ zero cost* is false. The
correct statement is **"zero agents ⇒ zero budget, and the skills are where this plugin's real
recurring cost lives"** — which means skill-count discipline, not agent-count discipline, is the lever
the plan should actually be pulling. Both plans should have their cost paragraphs rewritten to say so.

---

## What would falsify this ruling

1. **A named, citable specialist body for forms-as-process** — the equivalent of PMBOK/PMP for
   `project-management` (`CLAUDE.md:22`) or the memory-paradigm literature for `memory-engineering`
   (`CLAUDE.md:24`). If such a body exists (a standards corpus for intake instrumentation with its own
   vocabulary, methods and failure taxonomy that `process-analyst` demonstrably does not carry), the
   depth-inversion argument (reason 1) collapses and **1 agent** becomes correct. The right probe is
   not a grep: draft the (a) skill, hand it to `process-improvement/process-analyst`, and diff the
   output against what a dedicated agent would produce. If the outputs differ materially, I am wrong.
2. **`process-improvement`'s agents turning out not to reach form work.** Reason 2 rests on
   `process-analyst` being a viable receiver. If Phase 9's reciprocal-prior edit into
   `plugins/process-improvement/` is barred or refused (`plan-A.md:684` flags Phase 9 as the phase most
   likely to be under-done; CE-2 flags an in-flight branch collision), the (a) skill has **no** live
   receiver and the rot B predicted becomes structural rather than accepted. That does not by itself
   license an agent, but it forces the decision back to the owner rather than to this gate.
3. **A measured post-ship rot signal.** If, one release after shipping, the (a) and (c) skills are
   never invoked and no agent's `works_with` or inline prior names them, the discoverability failure is
   real and adding exactly **one** first-contact agent is the correct remedy — cheaper then than
   deleting one now.
4. **A gate requiring a non-empty `agents/`** would force the count regardless (plan-A's F2). Not
   found — zero-agent plugins already ship:
   `plugins/report-regeneration/` and `plugins/team-portfolio/` are registered with no `agents/`
   directory (`ls plugins/report-regeneration/` → CLAUDE.md, README.md, knowledge, scripts, skills; `ls plugins/team-portfolio/` → no `agents/`; verified this gate).

---

## Scope note

This gate ruled on the agent count only. It does **not** endorse or amend the standalone-vs-extend
ruling, the substrate-gate ruling, the phase DAG, or any other panel decision.

---RESULT_START---
{"gate":"G4b","status":"pass","artifact":"/Users/matthewcorbett/RavenClaude/.ravenclaude/runs/forge/forms-process-expertise/tiebreaks.md","bytes":0,"digest":["VERDICT: zero-agents — the panels' number survives, their reasoning does not","Under the carve-out (:22/:24) the split is NOT clean: forms' hygiene half is the DEEPER body (core security.md:43-45, cloudflare-who-gets-in.md:51,53, frontend-implementer.md:41,48,60, accessibility-auditor.md:48), inverting both precedents","The one candidate agent (forms-as-process) is a narrower slice of process-improvement/process-analyst's existing body, not a new specialist body — dispatch ambiguity + rubric drift (CLAUDE.md:20) which the carve-out relaxes but does not abolish","The genuinely-unowned half is a security-review lane, which even the admitted carve-out memory-engineering refused to fork (CLAUDE.md:24)","Cost is NOT zero: 6 skills = ~1,600 bytes always-on vs 937 bytes for memory-engineering's 3 agents — skill-count, not agent-count, is the real lever"],"blockers":[],"confidence":0.82}
---RESULT_END---
