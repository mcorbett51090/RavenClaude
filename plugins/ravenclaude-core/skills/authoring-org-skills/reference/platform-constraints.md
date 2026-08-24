# Platform constraints — the evidence file

Constraints the studio enforces that come from the **platform**, not from this repo.
This file is the evidence; the rule table
([`../schemas/org-skill-rules.json`](../schemas/org-skill-rules.json)) is the contract.

Some rules read their **tier** out of this file rather than carrying a hand-set one.
Where that is true it is stated on the rule, and the derivation is mechanical — see
`derive_zp02_tier()` in the packer. Promoting such a rule is a **data edit here plus a
fixture flip**, never a code change.

---

## zip-root-settlement

**Status: UNSETTLED.** `ZP02` is therefore at **WARN**.

### The question

S7 reads *"the ZIP root must be the skill folder itself, not a wrapper."* That sentence
does not disambiguate the two things it could mean:

| Reading | Archive layout |
|---|---|
| **A — folder at root** | `my-skill/SKILL.md`, `my-skill/reference/…` |
| **B — flat at root** | `SKILL.md`, `reference/…` |

Both readings satisfy "not a wrapper" in their author's eyes: A treats *the skill folder*
as the root entry, B treats *the skill folder's contents* as the root.

⛔ **The two planning panels read this in OPPOSITE directions and neither marked it
unverified.** That is the reason this file exists. A confident, unmarked disagreement
between two independent readers is the signature of a sentence that does not say what
either of them thought it said.

### Why it is not settled by reasoning

It cannot be. The answer is a property of the platform's unpacking code, and no amount of
re-reading the sentence produces it. Guessing costs a silent failure at upload time on an
artifact provisioned org-wide.

### The probe — one upload each, five minutes

Two fixture archives ship for exactly this:

- `rootA-folder.zip` — layout A
- `rootB-flat.zip` — layout B

Build them with `orgskill fixtures --out <dir>`. Then, at
**Organization settings → Skills**, upload each and record the outcome below.

⛔ **Record BOTH outcomes, not just the one that worked.** "A installed" and "A installed,
B was rejected with <message>" are different findings: the first is consistent with the
platform accepting either layout, and only the second settles the rule. If both install,
the constraint is looser than S7 implies and `ZP02` stays at WARN **as a correct
description of reality**, not as an unresolved to-do.

### Two kinds of evidence, and they are not interchangeable

|  | What it is | What it moves |
|---|---|---|
| `settled:` + `accepted_layout:` | an upload was **attempted and observed** | `ZP02`'s **tier** (WARN -> FAIL) *and* the packer's default |
| `research_indicates:` + `research_confidence:` | documentation and tooling were **read** | the packer's **default layout only** |

⛔ **Research never promotes the tier, at any confidence.** Reading Anthropic's docs — even
reading the exact zip-writing line in Anthropic's own packaging tool — tells you what the
platform *emits*. It cannot tell you what the platform's unpacker *accepts*, because nobody
ran it. Letting a documentary conclusion block a user's archive would be a confident
inference drawn from a true observation, wired into a linter: the precise failure mode the
rest of this studio is built to prevent. So research improves the **guess** and never the
**verdict**, and `derive_default_layout()` returns the basis alongside the value so the
packer can print which one the user is getting.

Precedence: **upload-verified > research > fallback A.** A recorded upload outranks any
research, including research that disagrees with it.

### Result — upload attempt

```
date:            <unrecorded>
rootA-folder.zip: <unrecorded>
rootB-flat.zip:   <unrecorded>
settled:         no
```

**The parser reads the `settled:` line.** While it says anything other than `yes`, `ZP02`
is WARN. To settle it: fill in the outcomes, set `settled: yes`, and set `accepted_layout:`
to `A` or `B` on its own line.

### Result — research

```
research_date:       2026-08-24
research_indicates:  A
research_confidence: moderate
```

`research_indicates:` accepts `A`, `B`, or `unresolved`; `research_confidence:` accepts
`strong`, `moderate`, `weak`, or `none`.

#### ⛔ The ambiguity was manufactured by OUR OWN PARAPHRASE

The question above was framed around a quote this project recorded as verbatim:
*"the ZIP root must be the skill folder itself, not a wrapper."*

**That sentence does not exist.** The phrase "not a wrapper" appears nowhere in Anthropic's
skills corpus — not on support.claude.com, docs.claude.com, platform.claude.com,
code.claude.com, `package_skill.py`, or `skill-creator/SKILL.md`. Independently confirmed by
direct fetch, 2026-08-24.

The real text, [article 12512198](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills):

> "The ZIP should contain the skill folder as its root (not a subfolder)."
>
> **Correct structure:** `my-skill.zip └── my-skill/ ├── skill.md └── resources/`
>
> **Incorrect structure:** `my-skill.zip └── (files directly in ZIP root)`

Layout B is not a competing reading of an ambiguous sentence — Anthropic labels it
**"Incorrect structure"** beside a Correct diagram that is Layout A. Read in isolation,
"not a subfolder" does sound like B, and that is how the paraphrase drifted.

⛔ **The lesson is worth more than the answer.** A paraphrase was written into a claims
table as a quotation, carried a source citation and a BLOCK tier, and then two independent
review panels reasoned from it and reached opposite conclusions — because the sentence they
were reasoning about was not the sentence Anthropic wrote. Neither panel checked the quote.
The disagreement looked like genuine platform ambiguity and was an artifact of our own
record. **Quote verbatim or do not present it as a quote.**

#### Supporting evidence for A

- **Anthropic's own packager emits A, and only A.** `anthropics/skills` →
  `skills/skill-creator/scripts/package_skill.py` computes
  `arcname = file_path.relative_to(skill_path.parent)`, writing every member as
  `my-skill/...`. There is no code path that emits flat-at-root.
- **The upload-error list presupposes a named folder inside the archive.**
  [12512180](https://support.claude.com/en/articles/12512180-use-skills-in-claude) gives
  "Skill folder name doesn't match the skill name" as a failure cause — a check that is only
  computable under Layout A. *(Inference, flagged as such.)*
- A is also legal under the strictest reading of the separate API rule, so it is the one
  layout no source rejects.

#### Why this is NOT `settled: yes`

- **The org-console article is silent on layout.** Measured, not eyeballed: a grep of
  [13119606](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization)
  returns exactly one `zip` hit ("Select a .zip file containing your skill") and **zero**
  layout hits, with a positive control confirming the extraction worked. The A-rule is
  inherited from a sibling page describing the **personal** uploader.
- **Nothing states the two ingests share a validator.** That single hop is inference, and it
  is the load-bearing gap. The enterprise docs actively distinguish pipelines ("Scanning
  doesn't cover the Claude API") and the overview says custom Skills "do not sync across
  surfaces."
- **Every source establishes that Anthropic DOCUMENTS A. Not one establishes that the console
  REJECTS B.** The uploader may well be tolerant; the docs would read identically either way.
- Instrument gaps, reported rather than hidden: reddit.com is unreachable to the search
  agent, so zero coverage there is an instrument gap and not an absence; `gh search issues`
  returned `[]` for queries WebSearch did surface; one first-hand Medium account 403'd unread.

#### Unresolved side-issues this research surfaced

- **Filename case.** Article 12512198 writes lowercase `skill.md` throughout and never uses
  `SKILL.md`; article 13119606 and `anthropics/skills` write `SKILL.md`. Anthropic's own
  sources disagree and none adjudicates. **Emit `SKILL.md`; do not hard-reject lowercase.**
- **Folder-name equality.** The doc says "matches your skill's name", but its own example
  pairs a `name:` of `Brand Guidelines` with a folder `my-skill/`, so byte-equality is not
  demonstrated and nothing states an upload fails on mismatch.
- **Doc staleness.** The platform Agent Skills overview still asserts claude.ai "does not
  support centralized admin management or org-wide distribution of custom Skills," which the
  existence of the console contradicts. Treat platform-docs claims about the claude.ai
  surface as lagging.
- Undocumented anywhere: the rejection error string, and the numeric ZIP size limit that
  12512180 lists as a failure cause without giving a number.

---

## non-shippable entries

The Finder-artifact and VCS patterns the packer excludes and `verify` rejects live in the
rule table under `non_shippable`, so the two code paths read the **same data** without
sharing **code**. That split is deliberate: a packer that builds an archive and then
asserts the layout with its own constants is checking its own intent, which is why
`verify` re-derives everything from the archive bytes.

The macOS `Compress "folder"` context-menu action is the specific failure this guards. It
produces `__MACOSX/` sidecar entries and `._*` resource forks that the author never sees
in Finder and that appear inside the uploaded archive.

`[verified 2026-08-24 — locally reproduced: `ditto -c -k --sequesterRsrc` emits`
`__MACOSX/. Whether the platform's unpacker rejects, ignores, or mis-reads those entries`
`is NOT verified and is not claimed; the rule excludes them because an entry the author`
`cannot see is an entry they cannot audit.]`
