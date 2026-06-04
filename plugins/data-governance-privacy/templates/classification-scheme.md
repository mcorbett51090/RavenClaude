# Data classification scheme

| Level | Definition | Access | Encryption | Retention | DSR-in-scope |
|---|---|---|---|---|---|
| Public | intended for public | open | optional | n/a | no |
| Internal | non-public, low harm | employees | at rest | per policy | maybe |
| Confidential | harmful if disclosed | need-to-know | rest+transit | defined | if PII |
| Restricted | PII / special-category | least-privilege + audit | rest+transit+masking | minimal, basis-bound | yes |

**PII/sensitive flag** orthogonal to level. Each rule -> control in data-platform/security-engineering.
