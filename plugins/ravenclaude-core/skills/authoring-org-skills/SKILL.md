---
name: authoring-org-skills
description: Authors, validates and packages a claude.ai Organization Skill — the intake questions, the trigger and scope exercises, then lint, pack and verify against measured platform constraints. Reach for this when someone wants to publish a Skill to their organization, or when an upload was rejected and the reason is unclear.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# authoring-org-skills

Gets a non-expert admin from *"I want everyone's drafts grounded in our own data"* to a
bundle that installs. The constraints are enforced by code, not by this document —
`schemas/org-skill-rules.json` is the contract and `scripts/orgskill.py` is the enforcer.

> **This is a Claude *Code* skill, and it does not fully conform to the rules it
> enforces.** Organization Skills are a different artifact with a different packaging
> contract, so `FM11`/`FM12` (frontmatter keys), the archive rules, and the body-length
> guidance do not literally apply here — this file carries `allowed-tools`, which an
> Organization Skill may not. What does transfer, and is honoured: a description that
> names both capability and trigger, third person throughout, and progressive disclosure.
> Saying so beats implying a self-conformance that is not there.

## Two entry points, deliberately not chained

| You want | Start at | Needs |
|---|---|---|
| **Ship a skill** | §1 → §6 | nothing else |
| **Judge a skill you already have** | the rubric lane | Phase 6 |

The seam between them is real. A quarterly admin ships and leaves; the rubric is the
deluxe version and is a **separate invocation**. Do not chain them by default.

---

## 1. Intake — five questions, before any file exists

1. **Who is the audience?** Every member of the org sees this in their system prompt.
2. **What situations should trigger it?** Not the capability — the *moments*. Keep the
   list; §2 needs it, and it is the ground truth for the invocation checks later.
3. **What data does it need**, and does a connector exist? If not, the data has to be
   maintained somewhere the skill can reach.
4. **How much latitude does Claude have?** The degrees-of-freedom call (S6): a
   compliance-shaped task wants a checklist, a judgement-shaped task wants principles and
   a worked example. Getting this backwards is the most common cause of a skill that is
   technically correct and useless.
5. **Who reviews it?** With org sharing on there is no approval step (S10). If the answer
   is "nobody", that is the answer — write it down.

## 2. The trigger-enumeration exercise

Write **six to ten concrete situations**, in the words a colleague would use.

> *"A customer replies asking why they were charged twice."*
> *"A renewal is 30 days out and the account has an open ticket."*

Then compress them into a description that **names both the capability and the trigger**
(S3 — the description is the discovery mechanism, and it is all Claude sees when choosing
among the org's other skills). Keep the list; it is not scaffolding.

⛔ **A description that names only the capability is the single most common defect in the
corpus.** `DS01` measures it, and its fire rate is printed with every finding.

## 3. The scope-negation exercise

Write **what this is NOT for, and what to use instead.** Three lines is enough.

This is the cheapest quality lever available. It costs a sentence, it prevents the skill
firing on adjacent work, and — because selection is relative to the whole field of skills
in the org — it is the only part of scope the author can actually control.

## 4. Layout — what stays in the body

Body: the procedure someone follows. Everything else becomes a bundled file, referenced
by a relative link, with a table of contents if it is long (S6).

Bundled files cost nothing until they are read, so the split is close to free. Two rules
that are not obvious:

- **Avoid deeply nested references** (S6). A file that points at a file that points at a
  file is one nobody reaches.
- **A bundled file must actually be in the archive.** `ZP08` checks the archive, not the
  disk, because a link that resolves in the working tree and not in the bundle fails only
  in production. Start from `templates/skeleton/`.

## 5. lint → fix → pack → verify

```bash
orgskill lint  <skill-dir>              # add --run-record <path> for a quarantine
orgskill pack  <skill-dir> -o <out.zip>
orgskill verify <out.zip>
```

`lint` exits 0 clean, 2 on a finding or a parse ambiguity — never 1, because a
non-blocking exit is the defect class this tool exists to avoid.

**FAIL blocks; WARN informs.** A warn is a heuristic, and every advisory finding prints
the rate it fired at and the population it was measured on, so it can be discounted on
sight rather than obeyed on reflex.

**Refusals `R1`–`R4` have no override.** No flag, no environment variable, no config key.
If one fires, read `reference/refusals.md`: the first remedy is to **paraphrase**, which
resolves most cases in one sentence and needs no reviewer.

`verify` re-opens the archive and re-runs the linter on the **extracted** tree. It shares
no state with `pack` — a packer that checks its own output is checking its own intent.

## 6. Ship it, and read the disclosure

Upload at **Organization settings → Skills**. Provisioning is immediate and org-wide.

⛔ **Whether the skill FIRES is not testable here, and this tool will never tell you it
will.** Selection is relative to the whole field of skills installed in the target org —
which the author does not have and cannot simulate (S18). A clean lint says the archive
is well-formed. It says nothing about whether the skill is ever chosen, whether it is
useful, or whether the platform's scanner will accept it. That scanner's verdict is
unappealable, it re-fires on every edit, and it is why the advice is to **attempt the
upload early rather than on a deadline**.

## Reference

- [`reference/refusals.md`](reference/refusals.md) — what the studio will not emit, and
  the four-condition quarantine path.
- [`reference/platform-constraints.md`](reference/platform-constraints.md) — the evidence
  file. Rules whose tier is derived read it; the zip-root question is still open there,
  and settling it is one upload each.
- [`schemas/org-skill-rules.json`](schemas/org-skill-rules.json) — every rule, its tier,
  its claim, and for advisories its measured fire rate and population.
- [`templates/skeleton/`](templates/skeleton/) — the starting tree.
- [`templates/examples/`](templates/examples/) — two skills authored through this
  procedure, in different domains, both lint-clean and verified.

Related, and not reimplemented here (S13): `refine-to-rubric` for the judged lane,
`prompt-pattern-library` for prompt shapes, and the `prompt-engineer` agent for wording.
