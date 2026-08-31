# Refusals — what this studio will not emit, and the one narrow way past

An Organization Skill is a **supply-chain artifact**. It is injected into the system
prompt of every member it reaches, provisioned org-wide the moment it is published,
**unreviewed if org sharing is on**, and judged by a classifier whose verdict nobody —
not you, not your admins — can appeal. Those are the conditions this file is written
against, and they are why some of these checks have no override.

The refusal table lives in [`../schemas/org-skill-rules.json`](../schemas/org-skill-rules.json)
and is enforced by [`../scripts/refusals.py`](../scripts/refusals.py). This file is the
reasoning; the JSON is the contract.

> **Note on this document's own style.** Nowhere below is an adversarial literal spelled
> out. Every one is paraphrased. That is not squeamishness — it is the first remedy this
> file recommends, applied to itself. If a document *about* refusals can make its point
> without the literals, most skills can too.

---

## The two tiers, and why the line falls where it does

| | Hard refusals `R1`–`R4` | Soft refusals `R1B`, `R5`, `R6`, `R7` |
|---|---|---|
| Tier | **FAIL** | **WARN** |
| Class | ground-truth | advisory |
| Override | **none exists** | n/a — they do not block |
| Escape | quarantine, four conditions | acknowledge in the run record |

A rule may sit at FAIL only when its ground truth does not depend on who wrote the
skill. `AKIA` followed by sixteen uppercase alphanumerics **is** an AWS access key id —
that is a fact about the format, not a guess about author habits. An entropy score is a
guess, so `R1B` sits at WARN no matter how much we would like it not to. The same
discipline demotes `R7`: plan-A promotes it to a refusal, and it stays at WARN anyway,
**because a refusal wearing a rule id is still a heuristic if its predicate is one.**

---

## `R1` — literal credentials · FAIL

Any provider-prefixed key, private-key block, non-placeholder bearer token, or
credential embedded in a URL, in the description, the body, or any bundled file.

**The lookalike is the hard part.** A credential-rotation policy that says *store the key
in an environment variable* and *send it in an authorization header with a placeholder
value* contains **no credential**. `is_placeholder()` is the predicate that separates
them, and it is the single most load-bearing function in the module: without it `R1`
fires on documentation, and a rule that fires on documentation gets switched off.

Recognised placeholder shapes: angle-bracketed, brace-wrapped, `$VAR` / `${VAR}` /
`%VAR%`, `YOUR_*`, repeated-character runs, and the words `REDACTED` / `EXAMPLE` /
`SAMPLE` / `DUMMY` / `CHANGEME` / `TODO`. Markup and sentence punctuation are stripped
first — a token quoted in backticks at the end of a sentence arrives with a backtick and
a full stop attached, and that near-miss was a measured false positive, not a
hypothetical one.

**One thing deliberately not carved out.** AWS's own documentation example key is
credential-**shaped**, and the scanner reads shapes. It stays a FAIL. An
"ends with EXAMPLE" exemption is exactly the cleverness that lets a real key through the
day someone names a variable `EXAMPLE`.

## `R1B` — unexplained high-entropy string · WARN

A forty-plus character run with mixed case and digits, that is not a hex hash and not a
hyphen-separated slug. Measured **0 of 934** — with a working positive control asserted
in the battery, so that zero means *these authors do not paste secrets*, not *the check
is inert*. Reaching zero took two narrowings, both from real hits: admitting `/` made
every long **path** match, and an unbounded lookahead was satisfied by an uppercase
letter that was not in the candidate at all.

## `R2` — global-posture override · FAIL

An imperative that instructs the assistant to set aside its prior guidance. In a
system-prompt-resident artifact this is not a quotation; it is the payload.

## `R3` — covert channel · FAIL

Two independent shapes:

- **Self-concealment** — any instruction to withhold from the user what the skill did.
- **Exfiltration** — an egress imperative **combined with** a reference to the
  conversation or the user's content. The conjunction is load-bearing: a skill that
  POSTs to a ticketing API is ordinary, and a skill that discusses the transcript is
  ordinary. Only together are they a channel. A documented, scoped, user-visible
  external call is asserted **not** to fire.

## `R4` — tool-authority expansion · FAIL

Piping a downloaded script straight into a shell, or installing from an arbitrary URL. A
bundle that does this hands your org's blast radius to whoever controls that URL.

Every one of the four hits on the real corpus was inside a skill **documenting** the
anti-pattern. That is not a defect in the rule — it is the reason paraphrase-first comes
before the quarantine path.

## `R5` — persona override on a binding matter · WARN + acknowledgement

Instructing Claude to *be* a lawyer, physician, or auditor, on matters where the answer
binds someone. Whether a given persona overrides binding guidance is a judgement call, so
it may not block. Prefer naming the **scope** ("this skill covers contract review") over
assigning an **identity**, and keep the escalation path intact.

## `R6` — org-confidential material · WARN + acknowledgement

With org sharing on, the bundle is resident for every member. Confidentiality is
contextual, so this may not block. Its single corpus hit was a data-room skill that
*discusses* NDAs and contains nothing confidential — a described-vs-present false
positive, disclosed rather than tuned away.

## `R7` — a description that is only a generic claim · WARN

Plan-A promotes this to a refusal. It stays at WARN because its predicate is `DS01`, a
heuristic. **It is emitted once, by `DS01`** — `R7` is listed so the refusal set is
complete and so a reader can see the promotion to FAIL was declined on purpose.

---

## Remedy 1 — paraphrase. Try this first, every time.

Most legitimate uses of an adversarial literal do not need the literal.

> A support macro can say *"a message attempting to override the assistant's prior
> guidance"* and lose **nothing** operational.

Paraphrase needs no fence, no caption, no reviewer, and no quarantine record. It is
faster than the alternative and it removes the payload rather than wrapping it. Most
instances end here.

## Remedy 2 — move it out of `SKILL.md`

If the literal is genuinely required, put it in a **bundled reference file** rather than
the body. Bundled files cost nothing until they are read, so this is right on the
context-budget argument alone.

`[unverified — whether the platform scanner reads bundled files or only SKILL.md is`
`undocumented. Verified by: a scan attempt on a paired fixture, one with the literal in`
`the body and one bundled. This instruction does not depend on the answer being`
`favourable — the context-surface reason stands either way, and the studio scans bundled`
`files itself regardless.]`

## Remedy 3 — quarantine. Four conditions. All four.

An `R1`–`R4` finding clears **only** with all of:

1. the literal is inside a fenced block;
2. the ≤3 lines before the fence carry a **frame** naming it as adversarial, an attack,
   an injection attempt, or untrusted;
3. the ≤3 lines after the fence carry a **handling instruction** — do not follow it,
   treat it as data, report it;
4. **a named human reviewer, with a date, recorded in the EXTERNAL run record**, against
   this exact span.

### Why the fourth condition exists

Plan-A specified conditions 1–3 and stopped. Read them again: **the author of the
adversarial string writes all three.** A rule you can satisfy alone, by typing three more
lines into your own file, is not a gate — it is a `--force` spelled out in the shipped
documentation, on a surface with no approval workflow and an unappealable scanner. The
same plan that ruled *"a supply-chain refusal with a `--force` is a refusal that will be
forced"* then documented the incantation that forces it.

Condition 4 is the one you cannot supply alone. It lives in a **separate artifact** on
purpose: a `reviewer:` line inside `SKILL.md` clears nothing, and the battery pins that.

**Three of four is still FAIL**, and the report names which one is missing.

### The run record

```json
{
  "quarantine_reviews": [
    {
      "span": "SKILL.md:42",
      "rule": "R2",
      "reviewer": "A. Reviewer <a@org.example>",
      "date": "2026-08-24",
      "rationale": "Literal required to train the detector."
    }
  ]
}
```

Pass it with `--run-record <path>`. That flag is **not** an override: it can satisfy
condition 4 and nothing else. An entry missing `reviewer` or `date`, or naming a
different span, clears nothing. A missing or unparseable record is an **empty** record —
there is deliberately no error path that grants clearance.

## No remedy — the frontmatter description

An adversarial literal in the `description` is an **unconditional FAIL with no
quarantine path and no reviewer path**. The description is injected verbatim into the
system prompt of every member of your organization. There is no framing that makes that
a quotation.

---

## `scanner_risk` — a self-assessment, and nothing more

Every report carries `scanner_risk: none | low | elevated` with the exact driving spans,
and this paragraph:

- the real scanner may disagree **in either direction** — it can fail a bundle rated
  `none`, and pass one rated `elevated`;
- its verdict is **unappealable**; a fail cannot be overridden by you, and your admins
  cannot approve it;
- it re-fires on **every edit**, not only the first upload — a bundle that passed last
  week can fail on a one-word change.

**Therefore: attempt the upload early, not on a deadline.** That single operational habit
is worth more than any local prediction this tool can make.

A **cleared quarantine does not lower the risk.** The literal is still in the archive,
which is exactly what the classifier reads. Downgrading on clearance would be this tool
telling you the opposite of the truth.

No report template in this studio contains the words *will pass*, *guaranteed*, or
*scanner-safe*. A test asserts it.

---

## There is no override, and that is the design

No flag, no environment variable, no config key clears an `R1`–`R4`. The acceptance
battery greps the CLI's own argument parser and its environment reads to prove none has
appeared, and the rule table carries `no_override: true` on each of the four, enforced by
`check_invariants()`.

If you are reading this because a refusal is in your way: **remedy 1 first.** It resolves
most cases in one sentence, and it is the only remedy that removes the payload instead of
wrapping it.
