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
research_date:       <unrecorded>
research_indicates:  unresolved
research_confidence: none
```

`research_indicates:` accepts `A`, `B`, or `unresolved`; `research_confidence:` accepts
`strong`, `moderate`, `weak`, or `none`. Findings and their citations go below this block.

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
