# Best-practices — prompt-engineering

Short, enforceable house opinions the agents apply on every engagement. Each file
is one practice: a **Do**, a **Don't**, and a **Flag** (what to surface when you
see the anti-pattern). They operationalize the cross-cutting opinions in
[`../CLAUDE.md`](../CLAUDE.md) §4.

| Practice | One-line |
| --- | --- |
| [show-dont-tell-with-examples](show-dont-tell-with-examples.md) | Teach format/behavior with the *hard* examples; each must earn its tokens. |
| [contract-the-output-format](contract-the-output-format.md) | Enforce the output format with a mechanism + validation, don't request it in prose. |
| [the-context-window-is-a-budget](the-context-window-is-a-budget.md) | Budget tokens per section; more context isn't free and past a point hurts. |
| [evaluate-prompts-like-code](evaluate-prompts-like-code.md) | Regression set + pinned model + CI gate; judge the judge. |
| [untrusted-input-is-not-instructions](untrusted-input-is-not-instructions.md) | Fence untrusted input as data; prompt-layer defense is necessary, not sufficient. |
