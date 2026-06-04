# Feature flag spec

| Field | Value |
|---|---|
| Name | <feature.action> |
| Type | release / experiment / ops(kill) / permission |
| Owner | <name> |
| Removal date (if temporary) | <date> |
| Targeting | <segments / %> |
| Default (service unreachable) | <fail-safe value> |
| Kill switch | yes |
| Evaluation | server-side, deterministic, sticky |
