# Produce deterministic output — same input must produce the same JSON and HTML

**Status:** Absolute rule
**Domain:** Team portfolio / engineering / reliability
**Applies to:** `team-portfolio`

---

## Why this exists

A portfolio run that produces different output for the same input on consecutive invocations cannot be diffed, cached, or trusted. The most common sources of nondeterminism in collection scripts are unsorted dictionary iteration (order changes between Python runs), timestamps injected into rendered bodies (not just the declared `generated_at` header), and randomized UUIDs or hash salts in IDs. Nondeterministic output means a "no-change" run produces a noisy commit diff, a cached dashboard becomes stale arbitrarily, and a developer debugging a regression cannot reproduce the exact output from a given input. The fix is free: sort all collections before serializing, restrict timestamps to the declared header, and use stable IDs.

## How to apply

Apply these three rules in every script that writes output:

**1. Sort all collections before serializing:**
```python
import json

# Bad — dict ordering depends on insertion order (Python 3.7+ is consistent but
# insertion order can vary if intermediate dicts are merged from API responses)
output = {"repos": repo_dict}

# Good — sort by a stable key
output = {
    "repos": sorted(repos, key=lambda r: r["name"]),
    "contributors": sorted(contributors, key=lambda c: c["login"]),
}
json.dumps(output, sort_keys=True, indent=2)
```

**2. Restrict timestamps to `generated_at` only:**
```python
from datetime import datetime, timezone

output["generated_at"] = datetime.now(timezone.utc).isoformat()
# Do NOT embed datetime.now() anywhere else in the output body
```

**3. Use stable IDs based on content, not random values:**
```python
import hashlib

def stable_id(project_name: str) -> str:
    return hashlib.sha256(project_name.encode()).hexdigest()[:8]
```

**Do:**
- Run `json.dumps(..., sort_keys=True)` when serializing the activity JSON.
- Sort contributor lists, repo lists, and event lists by a stable natural key (login, repo name, ISO timestamp).
- Verify determinism in the test suite: feed the same fixture twice and assert the outputs are identical.

**Don't:**
- Use `dict.items()` on a dict built from API responses without sorting — the order of API responses is not guaranteed.
- Embed `datetime.now()` inside a per-row label, a per-project HTML block, or any content field; the only timestamp in the output should be `generated_at`.
- Use `uuid.uuid4()` or random values for any ID field in the output JSON.

## Edge cases / when the rule does NOT apply

- The `generated_at` header is intentionally non-deterministic (it records the actual run time). This is the only allowed timestamp and it belongs at the document root, not inside item-level content.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — house opinion §4 #6 states this rule ("Deterministic output").
- [`./fail-soft-per-repo-one-bad-repo-never-sinks-the-run.md`](./fail-soft-per-repo-one-bad-repo-never-sinks-the-run.md) — deterministic error records in the output are part of this contract.

## Provenance

Derived from `team-portfolio` plugin CLAUDE.md §4 house opinion #6 ("Deterministic output"). Reinforced by standard reproducible-build and cache-correctness practice.

---

_Last reviewed: 2026-06-05 by `claude`_
