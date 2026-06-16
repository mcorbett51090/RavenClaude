# The quickstart is a CI-tested product, not a doc

**Status:** Absolute rule
**Domain:** Developer experience / docs reliability
**Applies to:** `developer-relations`

---

## Why this exists

The quickstart is where a developer forms their first judgment, so a quickstart that has drifted
from the real SDK burns trust at the highest-leverage moment — a copy-paste block that errors on
line 3 tells the developer the whole product is sloppy. Docs rot is silent: an SDK rename ships,
the quickstart still reads the old way, and nobody notices until activation quietly drops. Treating
the quickstart as a *product* with an owner, a conversion rate, and tests is what stops the rot.

## How to apply

Extract the quickstart's code blocks and run them, in order, against the published SDK in a clean
environment on every release. Assert the success signal appears. Drift fails the build.

```
CI job:
  1. parse code blocks out of quickstart.md
  2. run them in a clean env against the published SDK
  3. assert the documented success signal appears
  4. non-zero exit on any error   → docs drift == red build
```

**Do:**
- Give the quickstart a named owner and a CI test.
- Test against the *published* SDK version a developer would actually install.
- Treat a quickstart break like a production incident — it is one, for activation.

**Don't:**
- Rely on manual review to catch drift (it won't, reliably).
- Let the quickstart reference internal/pre-release APIs a developer can't use.

## Edge cases / when the rule does NOT apply

- A conceptual "what is X" overview with no runnable code has nothing to CI-test — but the moment
  it contains a copy-paste block, the block is in scope.
- Blocks that genuinely can't run in CI (require paid hardware, a human OAuth consent) should be
  minimized and clearly marked; everything around them still runs.

## See also

- [`../skills/quickstart-authoring/SKILL.md`](../skills/quickstart-authoring/SKILL.md)
- [`../templates/quickstart-template.md`](../templates/quickstart-template.md)

## Provenance

Codifies house opinion #4 ("The quickstart is a product, not a doc") in
[`../CLAUDE.md`](../CLAUDE.md) and the `docs-and-samples-engineer` agent's CI-test discipline.

---

_Last reviewed: 2026-06-16 by `claude`_
