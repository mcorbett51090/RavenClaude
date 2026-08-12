# Memory is context, not enforcement — to block an action, use a hook or a permission deny.

**Status:** Absolute rule. **Constitution:** §3 #6, §4.

## Use when

Any time a design, a runbook, or a threat model answers "what stops this?" with a document.

## The rule

**A remembered rule does not bind behaviour.** It is one more input the model may weigh or ignore. To actually *block* an action, use a hook or a permission deny — a mechanism that runs before the tool call and can refuse it.

So: **never cite a memory, an instruction file, or a stored policy as the control that prevents something.** Not in a threat model's mitigation column, not in a security review, not in a compliance answer.

## Why it matters

The vendor states it plainly for its own instruction and auto-memory surfaces: they are *"context, not enforced configuration,"* and blocking an action regardless of what the model decides is what a **PreToolUse** hook is for. A mitigation column that reads "documented in the memory file" is not a weak control — it is **no control**, described in the grammar of one, and it will be read as satisfied by every reviewer downstream.

This rule is cross-cutting rather than paradigm-specific, and it is the one most likely to be violated by a well-written document. The better the prose, the more it reads like enforcement.

## How to apply

- When writing a mitigation, ask: **what code runs, and what does it return, when the prohibited thing is attempted?** If the answer is "the model reads a paragraph," you have context, not a control.
- Put the mechanism in the mitigation column and the document in an evidence column beside it — never the document alone.
- Prefer platform primitives that fail closed: a read-only mount refuses the write at the filesystem, an approval gate on an out-of-tree import can be declined permanently, and a precondition on a write rejects a stale one. Those are controls. A stored instruction is not.
- When a stored rule *is* the right tool — steering, defaults, house style — say so, and say explicitly that it is advisory.
- Review the [memory threat model](../templates/memory-threat-model.md) for any mitigation whose subject is a file.

## The anti-pattern this prevents

The §4 failure mode: **citing an instruction file or a stored rule as the reason an action *cannot* happen.** The tell is a passive mitigation ("agents are instructed not to…") with no named mechanism and no failure mode.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) §3 #6 — the house opinion this rule encodes.
- [`../knowledge/memory-surfaces-2026.md`](../knowledge/memory-surfaces-2026.md) — the sharp-edges list, where this appears as a documented property of the surface.
- [`../knowledge/memory-security-and-privacy.md`](../knowledge/memory-security-and-privacy.md) — the control that is not one, and the three that are.
- [`../../ravenclaude-core/CLAUDE.md`](../../ravenclaude-core/CLAUDE.md) — the always-on Memory Engineering Protocol states the same rule for every agent; this file is the plugin's deeper reading of it, not a second copy.
