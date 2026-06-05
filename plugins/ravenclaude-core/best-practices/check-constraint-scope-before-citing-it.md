# Check a constraint's actual scope before citing it — "forbidden" has a boundary

**Status:** Absolute rule
**Domain:** Agent design / Capability Grounding / Constraint interpretation
**Applies to:** `ravenclaude-core`

---

## Why this exists

An agent that reads a rule's headline ("Forbidden infrastructure") and recommends against an adjacent thing it doesn't actually govern has failed closed on incorrect reasoning. The pattern is insidious because it mimics caution — the agent sounds careful — but it is wrong in a way that costs a round-trip when the user asks "did you read the rule?" and the agent discovers the rule was scoped to something else. A rule cited out of its scope is as wrong as a hallucinated capability, and it damages trust faster because the user expected the rule to be read carefully. The four-step scope-check is cheap and takes seconds; citing a constraint without it is the shortcut that produces the failure.

## How to apply

Before relying on a constraint to refuse, recommend against, or tell a user "you can't":

**1. Read the constraint's actual scope and rationale** — not just its headline. Find the "why this exists" section, the paper-trail it links, or the proposal it was extracted from. A rule about a "forbidden format" may be specific to one problem shape, not the broader domain.

**2. Check whether it applies to THIS case** — constraints are scoped:
- To a **format** ("this rule applies to tree-traversal parsers, not permission reconcilers")
- To an **environment** ("this rule applies to PROD, not DEV")
- To a **tool version** ("this behavior changed in version X")
- To a **problem shape** ("this rule applies when doing X, not when doing Y")

**3. Check whether its premise still holds** — rules written against an older state can be stale:
- A deferral ("v0.2.0+, wait for signal") may have since been met
- A "no real consumer ask yet" condition may have changed
- A tool that lacked a command may have since added it

**4. Then decide honestly:**
- Constraint genuinely binds → obey and cite it **with its real scope** ("this rule forbids X in the context of Y; your case is Z, which the rule doesn't cover")
- Constraint doesn't apply / premise is stale / trigger fired → say so with the `file:line` that shows it, and proceed (or surface "this would overturn rule X — your call" to the human, never a silent reversal)

**Do:**
- Cite the rule's actual scope alongside the headline when recommending against something: "Rule X forbids Y in context Z; your case is [within/outside] that scope because [evidence]."
- Use a this-session `file:line` citation when asserting a constraint applies — the same bar as a capability claim.
- When a deferral's trigger condition has been met (e.g., "build on real signal" and the real signal now exists), note this and treat the deferral as satisfied.

**Don't:**
- Cite a rule by headline and assume it covers the adjacent case without reading its scope.
- Treat a force-push deny, a `security_deny` floor, or a tribunal stop as a constraint to check scope on — those you obey first and question second (never act against them to "test the premise").
- Re-open a binding tribunal verdict by applying this rule — the tribunal's verdict is final; this rule applies to constraint docs and config rules, not tribunal decisions.

## Edge cases / when the rule does NOT apply

- High-blast / irreversible / security-floor denies always apply first; scope-check second. An agent should never rationalize past a force-push block or a security_deny by finding a scope exception.
- The rule that an agent must not re-open a tribunal verdict is not subject to this scope-check (it has no scope exception).

## See also

- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — CGP's alternate-methods rule is the action-side complement; this rule handles the constraint-citation side.
- [`./read-the-error-before-you-reroute.md`](./read-the-error-before-you-reroute.md) — the same "read first, act second" discipline applied to error messages vs. constraint documents.
- [`../CLAUDE.md`](../CLAUDE.md) — "Check why a constraint exists before obeying (or citing) it — don't take 'forbidden' at face value (added 2026-05-31)".

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Check why a constraint exists before obeying (or citing) it" (added 2026-05-31). Real case: a permission-reconciler recommended-against on the strength of a no-parser rule scoped to a tree format, with an explicit deferral that had since been satisfied.

---

_Last reviewed: 2026-06-05 by `claude`_
