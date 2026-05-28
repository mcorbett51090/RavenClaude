# Prompt & caching design — <APP / FLOW>

> Owned by `prompt-and-context-engineer`. See `knowledge/prompt-caching-playbook.md`.

## Layout (stable above the breakpoint, volatile below)
```
[ tools          ] ← stable; cache_control on the LAST tool; never reorder/regenerate per request
[ system         ] ← stable
[ static context ] ← stable (examples, long reference)
[ -- BREAKPOINT - ]
[ conversation / per-request input ] ← volatile
```

## Caching
- **Breakpoint(s):** <where; automatic top-level or explicit (≤4)>
- **TTL:** <5-min default | 1-hour for async/agentic gaps>
- **Min tokens met?** <yes — prefix ≥ model minimum (see capability map)>
- **Pre-warm?** <yes/no + refresh cadence>
- **Hit-rate target:** <e.g. ≥ 0.8 cache_read / (cache_read + input)>

## Context budget (1M)
- **Strategy:** <pre-aggregate | summarize | context editing/compaction>
- **What's excluded and why:**

## Output
- **Structured?** <tool-based shape + forced tool_choice | prose + why>

## Thinking (dated — cite the capability map)
- **Config:** <adaptive (Sonnet 4.6) | extended budget | none>; temperature 1/unset with thinking.

## Untrusted-input handling
- <how tool results / retrieved docs are wrapped as data> → security design to `core/security-reviewer`
