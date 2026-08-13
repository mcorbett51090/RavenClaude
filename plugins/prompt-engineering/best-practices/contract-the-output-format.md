# Contract the output format — don't ask for it

If downstream code parses the model's output, the format is a **contract**, not a
polite request. "Return JSON" in prose is a wish that fails silently at 3am.

**Do:** enforce the format with the strongest mechanism the model supports (native
structured/JSON mode → tool/function calling → constrained grammar → prose+parser),
and always add a parse → validate → repair → fail-closed path.

**Don't:** trust raw output even from native modes — a valid JSON string can still
violate a business rule. Validate the schema *and* the invariants.

**Flag:** any prompt whose output is parsed by code but whose format lives only in
prose instructions, with no enforcement mechanism and no validation step.
