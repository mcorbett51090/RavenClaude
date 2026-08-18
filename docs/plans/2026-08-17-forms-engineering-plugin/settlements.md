# G3b settlements — probes run to settle unsettled inferences

## Claim 21 — SETTLED 2026-08-17 (probe run; exit #1 of the G3b contract)

**The inference:** `.repo-layout.json`'s own top-of-file `description` says *"Add new globs here
when introducing a new top-level directory or a new plugin"* — which reads as the OPPOSITE of
G1a's finding that a new plugin dir needs no layout edit. Three phases (0, 6, 7) across the two
plans rest on the "no edit needed" reading.

**Why prose could not settle it:** the description is prose ABOUT the mechanism; the
`allowed_globs` list is the mechanism. They disagree. `enforce-layout.sh` reads the globs, not the
description, so the description is stale advisory text — but that is itself an inference until the
hook is actually run.

**The probe (bidirectional, run against the real hook):**

    printf '{"tool_name":"Write","tool_input":{"file_path":"<p>"}}' \
      | CLAUDE_PROJECT_DIR="$PWD" bash plugins/ravenclaude-core/hooks/enforce-layout.sh

| path | rc | meaning |
|---|---|---|
| `plugins/forms-engineering/skills/form-intake-design/SKILL.md` | **0** | ALLOWED — subject |
| `plugins/forms-engineering/.claude-plugin/plugin.json` | **0** | ALLOWED — subject |
| `plugins/forms-engineering/README.md` | **0** | ALLOWED — subject |
| `plugins/web-design/skills/conversion-design/SKILL.md` | **0** | positive control (known-good) |
| `plugins/forms-engineering/substrate/ravenpower.md` | **2** | DENIED — negative control |
| `some-random-toplevel-dir/thing.md` | **2** | DENIED — negative control |

**Verdict:** a genuinely NEW plugin directory IS auto-allowed by the `plugins/*/…` wildcards.
**No `.repo-layout.json` edit is required.** G1a was right; the description field is stale.

**Second, unplanned result — a design decision independently confirmed.** The negative control
`plugins/forms-engineering/substrate/**` returning rc=2 empirically proves Panel A's ruling that
"substrate separation must be a GATE, not a folder": a `substrate/` directory is denied by the
hook today. A's reasoning now has a measurement behind it rather than an inference.

**What would falsify this:** an edit to `.repo-layout.json` that narrows the `plugins/*/…`
wildcards to an explicit plugin allow-list. If that ever lands, re-run the probe above — the
subject rows would flip to rc=2 and three phases would need re-planning.

---

## Claim 31 — PARTIALLY FALSIFIED, ruling SURVIVES but plan boundaries CHANGE (2026-08-17)

**The inference:** that the legal-ops-clm intake precedent + the web-design seams support a
STANDALONE forms plugin. Panel A wired the falsifier as a hard Phase 0 gate: read the two
web-design agent files nobody had read in full; **if either already owns discipline (c) — form
engineering — EXTEND wins.**

**Probe:** read `plugins/web-design/agents/{frontend-implementer,accessibility-auditor}.md` in full.

**Result — A's claim "discipline (c) is homeless in web-design" is PARTIALLY WRONG:**

`frontend-implementer.md` DOES own part of form engineering:
- `:32` — "implement the form per the UX spec" is a named goal
- `:41` — form structure (`<label>` + `<input>` association)
- `:48` — "**Forms**: native HTML form patterns first; controlled React forms when needed;
  validation strategy (`required`, `pattern`, custom)"
- `:60` — "Form fields always paired with `<label>`. Placeholder is not a label."

`accessibility-auditor.md` owns form a11y:
- `:48` — "**Forms**: labels, instructions, error association (`aria-describedby`), required
  indication, validation timing"

**Why the STANDALONE ruling nonetheless SURVIVES — and this is the load-bearing half:**
`accessibility-auditor.md:92` routes *"Auth / login / CAPTCHA surfaces … → `ravenclaude-core`
`security-reviewer` (mandatory, zero-exception whenever the surface handles auth / sessions /
PII)"*. web-design does not merely lack a security lane — **it explicitly routes security OUT, by
rule.** So the genuinely unowned half of discipline (c) is precisely the half web-design
structurally excludes: server-side validation parity, bot defense, file uploads, idempotency,
webhook verification, PII handling. Those remain unowned repo-wide (rows 32, and confirmed by
G1a's zero-hit sweep).

**WHAT MUST CHANGE IN THE PLAN (this is not cosmetic):**
1. The forms plugin MUST NOT re-teach `frontend-implementer`'s client-side territory — native
   form patterns, `<label>` association, `required`/`pattern` validation attributes. Duplicating
   it creates the dispatch ambiguity the house rule's carve-out exists to prevent.
2. It MUST NOT re-teach `accessibility-auditor`'s form-a11y territory (labels, instructions,
   `aria-describedby` error association, validation timing).
3. Its owned territory is the **server/trust-boundary half**: validation parity, bot defense,
   uploads, idempotency, webhooks, PII, plus the process-instrumentation discipline (a) and the
   platform-selection discipline (d).
4. The reciprocal-priors phase must therefore declare an explicit BOUNDARY with these two agents,
   not merely a pointer at them.

**Net:** the fork ruling stands; the plugin's SCOPE is narrower than either panel drafted. Any
phase that assumed greenfield ownership of client-side form implementation is over-scoped.

---

## Claim 32 — SETTLED, CONFIRMED (2026-08-17)

**Instrument first (a zero-hit grep is a claim about the grep):**
`conversion` -> **425** files, `wcag` -> **138** files. The instrument returns large non-zero
numbers on topics that ARE owned, so a zero from it means something.

**Subject:** `honeypot` -> **0 files**. `form abandonment` -> **0 files**. Genuinely unowned.
`turnstile` -> 2, both `ravenclaude-core/knowledge/concepts/` teaching docs (passing mention,
no ownership). `multi-step form` -> 2: `power-platform/agents/power-pages-engineer.md`
(platform-specific) and a `frontend-engineering` Redux *scenario* — neither owns the pattern.
`form.*idempotenc` -> 7, all **data-pipeline** idempotency (`data-engineer`, test-data isolation),
not form-submission idempotency. Different concept, same word.

**Verdict:** confirmed unowned. The plugin is not duplicating an existing owner.

---

## Claims 104, 105, 36 — ACCEPTED as unsettled (G3b exit #3), NOT probed. Reason recorded.

These three are **direction-of-error safe**: if the inference is wrong, the plan is merely
over-cautious, and nothing is built on a false premise. Probing them would cost more than being
wrong about them, which is the wrong trade.

- **105** *(platform pricing goes stale within a quarter; unsafe as durable content)* — phases 2,3,4.
  The plan's response is to NOT publish pricing and to mark it `[unverified — volatile, verify at
  use]`. If the inference were false (pricing stable), the plan is over-cautious and loses nothing.
  There is no build resting on the pricing being unstable.
  `[unverified — premise not disconfirmed: direction-of-error safe; being wrong costs only caution]`

- **104** *(time-trap anti-abuse unvalidated for a fast/autofilling user)* — phase 2. Ships marked
  unverified with the settling experiment G1d proposed. If time-traps turn out to be validated,
  we shipped a hedge. No build rests on them being invalid.
  `[unverified — premise not disconfirmed: shipped hedged; a settling experiment is named]`

- **36** *(both process-improvement agents are genuine specialist craft, not wrappers)* — phase 9.
  G1b scored them 28/30 against the repo's own agent-quality-rubric. The harden plan does NOT
  propose deleting or demoting either agent, so if the inference is wrong the only cost is keeping
  two agents that could have been skills — reversible, and outside this run's scope to relitigate.
  `[unverified — premise not disconfirmed: no phase acts on it; being wrong is inert here]`

**Standing G3b state: 6 trips, all three classes above. No trip blocks the build. Every citing
phase carries its marker.**

---

## ⛔ CORRECTION — Claim 32's settlement was WRONG in part (G4a caught it, 2026-08-17)

My settlement above marked claim 32 "confirmed unowned". **Two of its topics ARE owned**, and the
error was mine, not the panels'.

**What I did wrong:** I ran `grep -rl -iE 'turnstile'`, got 2 hits, and dismissed
`ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md` as "a passing mention in a
teaching concept" **without opening it**. A grep answers *"is this string present"*. I converted
that to *"does anything own this topic"* — a different question — which is the exact
count-without-reading failure this repo has recorded before.

**What is actually there (read this session):**
- `plugins/ravenclaude-core/rules/security.md` §File handling — *"Filenames from users: never
  trust them. Generate your own; record the original name as data, not as a path component."* /
  path-traversal resolve-then-assert / *"Uploads: validate type by content (magic bytes), not
  extension. Cap size at the boundary."* **Upload hardening is owned by the constitution.**
- `plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md` — the **300-second token
  lifetime**, the **single-use replay rule**, server-side validation (with the Cloudflare
  server-side-validation docs URL), hostname management, and the Access-vs-Turnstile-vs-WAF
  boundary. **Turnstile is owned, substantively, with a refresh trigger.**

**Still genuinely unowned (these zeros were real):** `honeypot` -> 0 files,
`form abandonment` -> 0 files. Multi-step-form-as-a-named-pattern remains effectively unowned
(2 incidental hits, neither owning).

**CONSEQUENCE — this is a correlated error, not a footnote.** Both plans schedule content that
would DUPLICATE `ravenclaude-core`'s constitution on uploads and on Turnstile. That is precisely
the rubric-drift / dispatch-ambiguity the house rule exists to prevent, and no gap-delta could
have seen it because both panels agreed. The forms plugin must **cite and extend** these, never
restate them. G1a's rows 14 and 16 that seeded this are FALSE — both greps used a single literal
containing a slash (`"captcha/turnstile"`, `"file upload/file-upload"`), so neither ever tested
its topic; positive controls return 6 and 23 files.

**Claim 32 is re-marked: PARTIALLY FALSE. Unowned set shrinks to {honeypot, form abandonment,
multi-step-as-pattern}.**
