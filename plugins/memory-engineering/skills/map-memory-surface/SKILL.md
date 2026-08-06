---
name: map-memory-surface
description: "Name the storage surface a write actually lands on — who holds the bytes, who executes the write, and what trust model comes with it. Reach for this before writing any memory design down."
---

# Skill: Map the memory surface

**Decision 2 of the six-decision spine — *who holds the bytes, and who executes the write?*** Two surfaces can share an API shape and have **opposite** trust and data-residency models. Collapsing them misstates the only part that matters (§3 #4).

**This skill deliberately carries no header strings, status labels, caps or multipliers.** Those are the fastest-moving facts in the plugin, and they live in exactly one place so a staleness sweep can see them: [memory surfaces (2026)](../../knowledge/memory-surfaces-2026.md). Read them there, at the moment you write the design — never from recall.

## Step 1 — Answer the two questions, in writing

| Question | What it decides |
|---|---|
| **Who holds the bytes?** Your storage, or the vendor's? | Data residency, DPA scope, and who can be compelled to produce them |
| **Who executes the write?** Your code, or the vendor's runtime? | Who owns path traversal, size caps, expiry and redaction |

A design that cannot answer both is not a memory design yet. If a platform cannot answer them *and* tell you whether a historical value can be redacted, you do not have a memory surface — you have a bucket.

## Step 2 — Separate durable memory from context pressure

This is where most designs go wrong before they start.

| Symptom | Mechanism | Does anything survive? |
|---|---|---|
| Tool results are bloating the prompt | Context editing | **No** — it deletes from the prompt |
| The whole conversation is too long | Compaction | **No** — it summarizes, and the pre-summary blocks are dropped |
| Duplicates and stale entries are piling up | An offline consolidation job | Yes, into a **new** store — the input store is untouched |
| A fact must be readable by a *later* session | **A durable memory surface** | Yes — this is the memory decision |

The vendor's own pairing guidance is the cleanest frame available: *context editing clears specific tool results; compaction summarizes the whole conversation; memory is what must survive both.*

## Step 3 — Name the surface, as one of five

Anthropic currently ships **five distinct surfaces**, and they are not one product with five names. Teach them as five; the most common error in circulation is the collapsed version of this table.

| # | Surface | Who holds the bytes | Who executes the write |
|---|---|---|---|
| 1 | **Memory tool** (Messages API) | **You** | **You** — the model only *requests* file operations; your application performs them |
| 2 | **Context editing** | n/a — it removes content from the prompt | The API, server-side, before the prompt reaches the model |
| 3 | **Compaction** | n/a — it summarizes the conversation | The API, server-side, in an extra sampling pass you are billed for |
| 4 | **Claude Code instruction files + auto memory** | Your machine — repo files and a local per-project directory | You write the instruction file; Claude writes auto memory |
| 5 | **Managed Agents memory stores** | **The vendor** — a workspace-scoped server-side resource | The agent, via file tools in its sandbox, or you, via REST |

**Consolidation ("dreams") is a sixth mechanism attached to surface 5, not a free feature of it** — its own access gate, its own header, its own bill. Decide it separately.

Surfaces 1 and 5 are the pair people fuse. They are the **opposite** answer to question 1: surface 1 is client-side and you own every control on it; surface 5 is server-side and the vendor ships the controls. Current status, exact header and type strings, and every hard cap: [memory surfaces (2026)](../../knowledge/memory-surfaces-2026.md).

## Step 4 — Read today's status, strings and caps from the knowledge file

Open [memory surfaces (2026)](../../knowledge/memory-surfaces-2026.md) and copy out, **with its `Last verified` date**:

1. The surface's release status. A beta-to-GA transition changes required headers; a GA-to-deprecated transition changes everything.
2. The exact header or type string, if the surface takes one. Two endpoint families on the same product can require **different** headers, and sending the wrong one is a failed request, not a mislabel.
3. Every hard cap — per-item size, items per store, stores per session, index load budget.
4. **What happens *at* the cap.** This is the question nobody asks, and the answer differs by surface: some caps make new writes **fail loudly**; others **silently drop** the overflow at load time. Same word, opposite failure mode, opposite design.

The freshness sweep reports **age, never correctness**. Re-verify against the vendor's current docs before any of this reaches a deliverable.

## Step 5 — Walk the sharp edges for the surface you picked

Each of these has bitten someone and none is obvious from a skim. The full list, with sources, is in [memory surfaces (2026)](../../knowledge/memory-surfaces-2026.md); the ones that change a design are:

- **A client-side memory path prefix is virtual, and path traversal is your problem.** The docs warn explicitly that a crafted relative path can escape, and put the responsibility on the implementer — prefix check, canonicalize, containment-check, reject encoded traversal.
- **The other client-side safeguards are named for you but not enforced for you:** stripping sensitive content, size caps, capping what a read returns, and expiry.
- **An instruction file is context, not enforced configuration.** To *block* an action regardless of what the model decides, use a hook or a permission deny (§3 #6). Never write a design whose control column says "documented in the memory file."
- **Auto memory is keyed per git repo, not per worktree** — concurrent sessions in two worktrees write to one index.
- **Server-side stores attach only at session creation**, and read-only versus read-write is enforced at the filesystem level. There is no mid-session promotion.
- **Rollback may be retrieve-then-rewrite**, which itself creates a new version. Rehearse it before you need it.
- **A prefix cache is an optimisation, not a memory tier** — it is opportunistic and replica-local, so it is never durable persistence (§3 #4).

## Step 6 — Record it

Into the [memory design record](../../templates/memory-design-record.md): **surface · who holds the bytes · who executes the write · release status · the date you read that status · the caps and what happens at each.** Then hand the write path to [memory-poisoning-review](../memory-poisoning-review/SKILL.md) and the retention story to [design-forgetting-policy](../design-forgetting-policy/SKILL.md).

## Porting this off one vendor

The vendor changes; the questions do not. For any platform, answer: who holds the bytes · who executes the write · what is the status and the exact string today · what are the caps and what happens at each · is there an audit trail and can a historical value be redacted · does anything consolidate or forget on its own. The last one's answer is almost always **no** (§3 #3).

## Output

A named surface with its byte-holder, its write executor, its dated release status, its caps and their failure modes, and the sharp edges that apply. Traverse Tree 2 in [the decision trees](../../knowledge/memory-engineering-decision-trees.md).
