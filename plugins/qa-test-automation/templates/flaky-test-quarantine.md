# Flaky test quarantine log

| Test | First flagged | Suspected cause | Owner | Quarantined? | Due | Status |
|---|---|---|---|---|---|---|

**Policy:** intermittent failure -> auto-flag -> quarantine out of the required gate -> assign owner + deadline -> fix determinism or delete. Never 're-run until green'.
