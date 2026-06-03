# Rename Power Automate actions from their auto-generated type names to descriptive names

**Status:** Pattern — every action in a production cloud flow must have a descriptive name. Auto-generated names (`Compose_2`, `Apply_to_each_3`, `Condition`, `HTTP`) are the flow equivalent of single-letter variable names: technically valid and practically unreadable.

**Domain:** Power Automate

**Applies to:** `flow-engineer`, `power-platform-tester`, any agent authoring or reviewing cloud flow JSON or the Power Automate designer

---

## Why this exists

Power Automate assigns action names automatically when a maker adds an action in the designer or when an agent writes flow JSON directly. The generated names follow the pattern of the action's type: `Compose`, then `Compose_2`, `Compose_3`; `Apply_to_each`, then `Apply_to_each_1`; `Condition`, `Condition_2`; `Scope`, `Scope_2`; `HTTP`, `Parse_JSON`, `Filter_array`, `Send_an_email_(V2)_3`. These names persist in four places that matter:

| Where the name appears | Why auto-generated names cause pain |
|---|---|
| **Run history** | A run that failed in `Compose_4` tells you nothing. A run that failed in `Get_Approval_Deadline_From_Config` tells you exactly where the problem is. |
| **Expression references** | Every downstream expression that reads this action's output uses `outputs('Compose_4')` — a rename after the fact cascades to every expression in the flow, and a missed update silently returns `null`. Renaming during authoring costs one drag; renaming later costs a search-and-replace with no automated safety net. |
| **Flow JSON diff in source control** | A git diff of a flow with action names like `Apply_to_each_3` is unreadable. A diff of `For_Each_Order_Line_Item` is self-documenting. Code review, conflict resolution, and PR descriptions all depend on the diff being human-parseable. |
| **The designer canvas** | A flow with 20 `Compose_N` shapes requires a developer to expand every shape to understand its purpose. A flow with descriptive names is readable at a glance. |

This is a BPA-class rule — it is the Power Automate equivalent of renaming a Power BI measure's empty `DisplayFolder` or a PCF control's default `PropertyName`. A prior session confirmed it is also the most common mechanically-detectable flow-quality gap in real customer solutions.

---

## Which names are auto-generated

The patterns to look for (and that the `validate-flow-action-names.sh` hook checks deterministically):

- **Bare type names with no suffix:** `Compose`, `Condition`, `Scope`, `HTTP`, `Apply_to_each`, `Parse_JSON`, `Filter_array`, `Initialize_variable`, `Set_variable`, `Append_to_array_variable`, `Increment_variable`, `Terminate`, `Delay`, `Response`
- **Type names with a numeric suffix:** `Compose_2`, `Apply_to_each_3`, `Condition_2`, `Scope_2`, `HTTP_1`, `Initialize_variable_4`
- **Connector-generated defaults with a version suffix:** `Send_an_email_(V2)`, `Send_an_email_(V2)_2`, `Get_items_3`, `Create_item_2`

Any action key in the flow JSON `actions` object that matches these patterns is a candidate for renaming.

---

## How to rename

### In the Power Automate designer

Right-click (or select the three-dot menu on) any action → **Rename**. The designer updates all downstream expression references that use the action name automatically `[unverified — verify your Power Automate environment version propagates the rename to all expression references before relying on this; manual review is still recommended]`. Rename at authoring time, before expressions that reference the action are written — the cascade problem is avoided entirely.

### In the flow JSON (`actions` object)

Flow JSON stores actions as a dictionary keyed by the action name. Renaming in JSON means:

1. Change the key in the `actions` dictionary.
2. Find every `runAfter` reference to the old name (other actions run-after this one) and update it.
3. Find every expression that references the old name via `outputs('OldName')` or `result('OldName')` and update it.
4. Find every `dependsOn` reference if present.

This is the reason to rename at authoring time rather than after the flow is complete. A search-replace in a large flow JSON is error-prone; the expression references are deep-nested strings and a missed one silently evaluates to `null` without a parse error.

### Naming conventions

- **Use plain Title Case English** — consistent with house rule §3 #6: "flow steps use plain Title Case English."
- **Name for the *what*, not the *how***: `Get Customer Record From Dataverse` rather than `Get_Items_3`. The type of action is visible from its icon; the name should add the context the type doesn't provide.
- **Be specific enough to distinguish siblings**: if a flow has two `Compose` actions — one formatting a date and one building an email body — their names should be `Format Due Date As ISO 8601` and `Build Approval Email Body`, not `Compose Date` and `Compose Email`.
- **Keep names short enough to read on the canvas**: three to six words is a useful guideline. A name longer than eight words will be truncated in the designer.
- **Use the scope name as a namespace prefix for actions inside it**: actions inside a `Try` scope can be prefixed with nothing (they're visually nested); actions inside a named child scope like `Validate Input Data` benefit from names like `Check Required Fields Present` and `Reject If Missing` rather than generic names that would clash with identically-named actions in the sibling scope.

---

## Do

- Rename every action before moving to the next action during authoring — one rename in place is cheaper than ten renames with expression cascade later.
- Use names that describe the business intent, not the connector type: `Send Approval Request To Manager` rather than `Start and wait for an approval`.
- Keep the `validate-flow-action-names.sh` hook enabled — it fires on flow JSON edits and flags `_<number>`-suffixed and bare-type names before the flow reaches source control.
- When reviewing a flow someone else built, treat every `_2`, `_3`, `_N` suffix as a comment requesting a rename — flag it in the review report and add it to the PR checklist.
- When referencing an action in an expression, confirm the name in the JSON after any rename to be sure no stale reference persists.

## Don't

- Don't rename actions in a prod-deployed managed flow's JSON directly — the rename must go through the dev → export → managed import ALM cycle to take effect in managed layers.
- Don't use abbreviations or jargon in action names: `Get WF Data` means nothing to a reviewer six months later; `Get Workflow Configuration From Environment Variables` is self-explaining.
- Don't leave a renamed action whose downstream expressions still use the old name — the flow will run but those expressions will evaluate to `null` or throw an error at runtime.
- Don't name an action after the connector rather than the task: `SharePoint` is not a name; `Get Approved Documents From Archive Library` is.
- Don't use numbers in names unless they are meaningful business numbers: `Apply to each Order Line` is fine; `Apply to each 2` is the auto-generated default.

---

## Connection to the hook

The `validate-flow-action-names.sh` hook fires on `PostToolUse` `Edit` / `Write` / `MultiEdit` operations on files matching `*/workflows/*.json` and `*/flows/*.json`. It inspects the `actions` dictionary keys and flags:

- Any key ending in `_<integer>` (e.g. `Compose_2`, `Condition_4`)
- Any key that exactly matches a known default type name (`Compose`, `HTTP`, `Scope`, `Condition`, `Apply_to_each`, `Parse_JSON`, `Filter_array`, `Initialize_variable`, `Set_variable`, `Terminate`, `Response`, `Delay`)

It is a **structural file check** — it does not evaluate whether a descriptive name is actually meaningful, nor does it detect connector-generated verbose defaults (e.g. `Send_an_email_(V2)_3`). Those still require human or agent review. The hook catches the most common mechanical pattern — the auto-incremented suffix — and surfaces it immediately rather than at CI time or in a post-deploy code review.

The hook is **advisory by default** (prints to stderr, does not block). To make it blocking in a session where flow quality is a hard gate, flip the final `exit 0` to `exit 1` in `hooks/validate-flow-action-names.sh`. See `hooks/README.md` for wiring.

---

## See also

- [`agentic-flow-build-recipe.md`](./agentic-flow-build-recipe.md) — Phase 2 (Construct) of the agentic flow build recipe, which includes this naming discipline as a mandatory step
- [`flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — companion rule on Try-Catch-Finally and retry-policy discipline
- [`flow-connection-references-and-environment-variables.md`](./flow-connection-references-and-environment-variables.md) — the other Construct-phase discipline for promotable flows
- [`../knowledge/power-platform-agentic-toolchain-2026.md`](../knowledge/power-platform-agentic-toolchain-2026.md) — the full agentic toolchain context where this rule lives
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — the agent that enforces this rule during flow authoring
- [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) — the agent that flags unnamed actions during flow review

---

## Provenance

Codifies house rule §3 #6 ("flow steps use plain Title Case English") as applied to action naming, and the BPA-style mechanical check for the most common auto-generated name patterns. The rule is widely documented as a maker best-practice in the Power Platform community `[unverified — training knowledge: no single authoritative MS Learn source confirmed this session; the pattern is consistent with the Power Automate guidance coding conventions at https://learn.microsoft.com/power-automate/guidance/coding-guidelines/ — verify against current coding guidelines before citing]`. The hook reference (`validate-flow-action-names.sh`) corresponds to the hook registered in `hooks/hooks.json` and the dev-mirror entry in `.claude/settings.json`.

---

_Last reviewed: 2026-06-03 by `claude`_
