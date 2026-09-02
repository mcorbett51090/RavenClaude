# repo-review reference — the 8 review dimensions

> Loaded by the repo-review Workflow **only when a review agent is actually dispatched** — progressive
> disclosure, mirroring how `forge-pipeline`'s `reference/` files are loaded only when the pipeline's
> depth reaches them (see [`../../forge-pipeline/reference/gates-standard.md`](../../forge-pipeline/reference/gates-standard.md)
> for the precedent). The orchestrating Workflow builds `review-plan.json` (via `scripts/repo_map.py`),
> then for each `(dimension, model, batch)` triple in the fan-out it reads the one `##` section below
> matching that dimension, fills the prompt template's placeholders, and dispatches a review agent with
> the filled text as its entire brief. Nothing here is read at plan time — only at dispatch time, once
> per fan-out cell.

**`dead-code-simplification` is the one dimension that defaults to single-model even when cross-model
review is on elsewhere in the pipeline.** Every other dimension benefits from dispatching the same
batch to two different model backbones and reconciling disagreement — a `correctness` or `security`
finding one model misses is exactly the case cross-model review exists to catch, because two models
trained differently are unlikely to share the same blind spot. A `dead-code-simplification` claim is
different in kind: "this branch is unreachable after the `return` two lines up" or "this file already
has a helper that does this" is close to mechanically verifiable by any competent reader — a second
model rarely disagrees with a well-evidenced dead-code claim, so paying for a second pass buys almost
no additional signal there. Spending the cross-model budget on `correctness` / `security` /
`concurrency` — where two models genuinely diverge — and running `dead-code-simplification`
single-model is the cheapest lever available to cut fan-out cost without losing the signal on the
dimensions where model divergence pays off.

## The finding schema (every dimension emits this)

Every review agent, regardless of dimension, writes a JSON **array** of finding objects to the path the
orchestrator hands it. Each finding is:

```json
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "<the dimension key, one of the 8 below>"
}
```

A review agent should report a finding only when it can point to a concrete `evidence_quote`
backing it — false positives are costly (a confirmed finding gets auto-fixed later), so a vague
"this looks risky" with no specific line is not a finding. If a batch turns up nothing for the
dimension, the required output is a written, empty JSON array — the file must still exist at
`{output_path}`, since an absent file is indistinguishable from a crashed agent to the orchestrator.

---

## 1. correctness

**Reading strategy.** Read line-by-line **within the enclosing function** — do not skim a whole file
looking for "smells"; pick one function at a time, trace its control flow from entry to every return,
and ask at each branch "is this condition the one the surrounding logic actually needs, and does it
handle every value the type system admits (including the falsy-but-legitimate ones)?" Cross-reference
variable names against what they're assigned a few lines up — a copy-pasted block that renamed one
occurrence of a variable but not the sibling occurrence is one of the highest-yield patterns to check
for. When a call crosses a function boundary, use `{repo_map_summary}` to locate the callee's
definition (even if it's outside this batch) rather than guessing its contract from the call site
alone.

**Example patterns/anti-patterns:**
- Inverted or off-by-one condition: a loop bound using `<=` where the collection is zero-indexed and
  `<` was intended, or a boundary check that should be `>` but reads `>=`.
- Falsy-zero bug: `if (count) { ... }` in JS/TS, or `if x:` in Python, where `count`/`x` can
  legitimately be `0` and the branch should have used an explicit `is not None` / `!= null` check.
- Missing `await` on a Promise/coroutine: the call returns a pending Promise object that is then used
  as if it were the resolved value (e.g. passed to a function expecting a string, or truthiness-checked
  when a Promise is always truthy).
- Copy-paste variable-name bug: a block duplicated for a second case where one internal reference to
  the first case's variable was never renamed to the second case's variable.
- Null/undefined dereference: accessing a field on a value returned from a lookup (`dict.get(key)`,
  `Array.find(...)`, an optional API response field) without checking it resolved before dereferencing.

**Prompt text:**

```
You are reviewing a batch of files for CORRECTNESS bugs only — wrong or inverted conditions,
off-by-one errors, null/undefined dereferences, a missing `await`, falsy-zero bugs (code that
treats a legitimately-zero/empty value as absent), and copy-paste variable-name bugs. Do not
report anything outside this dimension.

Files in this batch:
{files}

Repo map (directory tree + module-name summary — use this to reason about callers/callees
outside your own batch; do not assume a function's contract, look it up if it's listed here):
{repo_map_summary}

For each file, read line-by-line within each function's own control flow. Trace every branch
from entry to every return. For every conditional, ask: does this handle every legitimate value
the type admits, including zero/empty/falsy? For every external or cross-module call, check
whether its result is used correctly (awaited if async, null-checked if it can return null/None).

Report a finding only when you can point to a concrete line backing it. Do not report style
preferences, missing tests, or anything that isn't a genuine wrong-behavior bug. Severity ceiling
for this dimension is "blocking" — use it for a bug that would corrupt data, crash, or silently
produce the wrong result on realistic input.

Write your findings to: {output_path}

Each finding must be a JSON object with exactly these fields:
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "correctness"
}

If this batch turns up nothing for this dimension, write an empty JSON array `[]` to
{output_path} so the file still exists — do not omit the file, do not write prose instead.
Emit ONLY the JSON array, no prose.
```

---

## 2. security

**Reading strategy.** Trace every **trust boundary** the batch's files cross — anywhere data enters
from outside the process (an HTTP request body/query/header, a CLI arg, a file read whose path is
derived from user input, an environment variable holding a secret, a message from a queue/webhook) and
anywhere the process reaches back out (a shell command, a SQL query, an HTML render, a filesystem path,
an outbound HTTP call). For each boundary, ask "is this value validated/escaped/authorized before it's
used as a command, a query, a path, or a URL — and is the authorization check actually present, not
just assumed by a comment?" Grep-style scanning for sink function names (`exec`, `eval`, string-built
SQL, `innerHTML`, `pickle.loads`, `yaml.load` without `SafeLoader`) is a legitimate part of this read,
but every hit needs the surrounding data-flow traced back to confirm the input really is
attacker-reachable before it's reported.

**Example patterns/anti-patterns:**
- SQL injection: a query string built with f-string/`.format()`/string concatenation instead of a
  parameterized query, where any part of the interpolated value comes from a request.
- Shell/command injection: `subprocess.run(f"...{user_input}...", shell=True)` or Node's
  `child_process.exec(`...${input}...`)` instead of an argv-array call with `shell=False`/no shell.
- Missing authorization check: a handler that reads `request.user` or a role/tenant field but never
  compares it against the resource being accessed (an IDOR/BOLA shape — `getObject(id)` with no
  ownership check on `id`).
- Hardcoded secret: an API key, password, or private key literal in source rather than read from an
  env var or secret store.
- Unsafe deserialization: `pickle.load`/`yaml.load` (no `SafeLoader`)/`eval(json_like_string)` on data
  that originates outside the process.

**Prompt text:**

```
You are reviewing a batch of files for SECURITY bugs only — untrusted input parsed or used
without validation, missing authorization checks, hardcoded secrets, injection sinks (SQL,
shell, HTML/XSS), unsafe deserialization, path traversal, and SSRF. Do not report anything
outside this dimension.

Files in this batch:
{files}

Repo map (directory tree + module-name summary — use this to reason about callers/callees
outside your own batch; check whether a value crossing into this batch from elsewhere already
carries a validation guarantee before treating it as unvalidated):
{repo_map_summary}

For each file, trace every trust boundary: where does data enter from outside the process
(request body/query/header, CLI arg, env var, file/path derived from external input, a queue or
webhook message), and where does the process reach back out (shell command, SQL query, HTML
render, filesystem path, outbound network call). For each boundary, confirm whether the value is
validated, escaped, or authorization-checked before use — do not assume a comment claiming
"validated upstream" is true; look for the actual check.

Report a finding only when you can point to a concrete line backing it, with the
attacker-reachable data flow named in the failure_scenario. Severity ceiling for this dimension
is "blocking" — use it for anything that would let an attacker read/write data, execute code, or
bypass authorization.

Write your findings to: {output_path}

Each finding must be a JSON object with exactly these fields:
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "security"
}

If this batch turns up nothing for this dimension, write an empty JSON array `[]` to
{output_path} so the file still exists — do not omit the file, do not write prose instead.
Emit ONLY the JSON array, no prose.
```

---

## 3. concurrency

**Reading strategy.** Identify every piece of **shared mutable state** the batch's files touch — a
module-level variable, a class attribute shared across instances/requests, a row in a database, a file
on disk, a cache entry — and for each one, ask "what guards access to this across concurrent callers,
and does the guard's scope match the operation's actual atomicity requirement?" A lock that's acquired
right before the read but released right after it, with the write happening in a second, separately-
locked step, is a time-of-check/time-of-use (TOCTOU) gap even though each individual operation "looks"
protected in isolation. For async code, trace whether an operation the surrounding logic clearly needs
to complete before continuing (a fire-and-forget `asyncio.create_task(...)` or an un-awaited Promise)
is actually awaited or joined — and whether a batch of independent async operations that could run
concurrently is instead awaited one at a time in a loop. For anything retried (a queue consumer, a
webhook handler, a "retry on failure" wrapper), check whether the retried operation is idempotent —
does running it twice with the same input produce the same end state, or does it double-charge/
double-insert/double-send?

**Example patterns/anti-patterns:**
- TOCTOU: `if not os.path.exists(path): create(path)` — another process/thread can create `path`
  between the check and the create, or `if balance >= amount: debit(amount)` without holding a lock
  across both the check and the debit.
- Lock scope too narrow: a lock acquired only around the read of a value, released, then the computed
  write happens outside the lock — the invariant the lock exists to protect is broken by the gap.
  Lock scope too wide: holding a global lock across a slow I/O call (a network request, a disk write)
  serializes work that didn't need to be serialized, creating a throughput bottleneck or deadlock risk.
- Fire-and-forget that should be awaited: `asyncio.create_task(save_audit_log(...))` with no reference
  kept and no `await`/`gather` — the task can be garbage-collected mid-flight, or in JS a bare
  `somePromise.then(...)` with no `await` and no `.catch` in a request handler that then responds
  before the promise settles.
- Missing `Promise.all`/`asyncio.gather` for independent work: `for (const item of items) { await
  process(item) }` where each `process(item)` is independent — this becomes a concurrency defect when
  something downstream depends on total latency, or when the intent was clearly "run these together".
- Non-idempotent retry: a payment-charge or insert-row operation retried on a transient network
  failure with no idempotency key, so a retry after a successful-but-unacknowledged first attempt
  double-executes.

**Prompt text:**

```
You are reviewing a batch of files for CONCURRENCY bugs only — shared mutable state accessed
without a lock/guard, a lock whose scope is too narrow or too wide for the operation it protects,
time-of-check/time-of-use (TOCTOU) races, async ordering bugs (a fire-and-forget that should be
awaited, independent async work that should be gathered/batched but is awaited sequentially), and
retried operations that are not idempotent. Do not report anything outside this dimension.

Files in this batch:
{files}

Repo map (directory tree + module-name summary — use this to find where shared state defined in
this batch is also mutated from callers outside it, and whether a "retry" wrapper you can see
here is invoked from a queue/webhook handler elsewhere):
{repo_map_summary}

For each file, list every piece of shared mutable state it touches (module-level variables,
class attributes, database rows, cache entries, files on disk). For each, trace what guards
concurrent access and whether the guard's scope actually spans the full read-modify-write (or
check-then-act) sequence it needs to protect. For async/await code, check every fire-and-forget
call and every sequential-await-in-a-loop for whether it should instead be joined/gathered. For
anything retried, check whether re-running it with the same input is safe.

Report a finding only when you can point to a concrete line backing it. Severity ceiling for this
dimension is "blocking" — use it for a race that can corrupt shared state, double-execute a side
effect, or deadlock under realistic concurrent load.

Write your findings to: {output_path}

Each finding must be a JSON object with exactly these fields:
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "concurrency"
}

If this batch turns up nothing for this dimension, write an empty JSON array `[]` to
{output_path} so the file still exists — do not omit the file, do not write prose instead.
Emit ONLY the JSON array, no prose.
```

---

## 4. resource-leaks

**Reading strategy.** For every place the batch's files **acquire** a resource — opening a file, a
socket, a database connection or cursor, a lock, a subscription/event listener, a timer/interval — walk
**every exit path** from the acquisition point: the normal return, every early return, and every
exception that could be raised between acquisition and the intended release. This dimension exists
specifically to catch a release that's missing on the *error* path — a `try`/`finally` (or context
manager / `using` / `with`) that's absent, or present but scoped to only part of the code that can
raise. A resource released only at the end of a function body, with an early `return` above it, is a
leak on every code path that takes that early return. A listener/subscription registered in a
constructor or a mount/setup function with no matching removal in the corresponding destructor/
unmount/teardown is a leak on every instantiate-then-discard cycle.

**Example patterns/anti-patterns:**
- File/socket/connection opened without a context manager: `f = open(path); data = f.read(); f.close()`
  — an exception raised by `f.read()` skips the `close()` entirely; should be `with open(path) as f:`.
- DB cursor/connection not released on the exception path: `conn = pool.get(); cursor =
  conn.cursor(); cursor.execute(query)` with the `finally: conn.close()` missing or only covering the
  success path.
- Lock acquired but not released on an early return between `acquire()` and the matching `release()`
  — should use a context manager or a `try/finally` that spans every path.
- Event listener / subscription registered in a component's mount/init with no corresponding removal
  in its unmount/dispose — e.g. React `useEffect(() => { window.addEventListener(...) }, [])` with no
  cleanup function returned, or a class constructor that subscribes to an event bus with no matching
  unsubscribe in a destroy method.
- `setInterval`/`setTimeout` (or a language's timer equivalent) started and never cleared — no
  `clearInterval`/`clearTimeout` call reachable from the code path that ends the object's lifetime.

**Prompt text:**

```
You are reviewing a batch of files for RESOURCE-LEAK bugs only — a resource acquired (file,
socket, database connection/cursor, lock, subscription/event listener, timer/interval) without a
guaranteed release on EVERY exit path, including the error/exception path. Do not report anything
outside this dimension.

Files in this batch:
{files}

Repo map (directory tree + module-name summary — use this to check whether a resource acquired
in a constructor/setup function defined in this batch has its matching teardown in a
destructor/cleanup function that lives elsewhere):
{repo_map_summary}

For each file, find every place a resource is acquired. For each acquisition, walk every exit
path from that point forward: the normal return, every early return, and every statement between
acquisition and the intended release that could raise an exception. Confirm release happens on
ALL of those paths — a bare close() at the end of a function with no try/finally is a leak on
every early-return and every-exception path above it. For anything registered (a listener, a
subscription, a timer), confirm there is a reachable matching removal.

Report a finding only when you can point to a concrete line backing it. Severity ceiling for this
dimension is "blocking" — use it when the leak is on a hot/frequently-hit path (exhausts a
connection pool, file-descriptor limit, or accumulates listeners under normal traffic), and a
lower severity when the leak only manifests under a rare error path.

Write your findings to: {output_path}

Each finding must be a JSON object with exactly these fields:
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "resource-leaks"
}

If this batch turns up nothing for this dimension, write an empty JSON array `[]` to
{output_path} so the file still exists — do not omit the file, do not write prose instead.
Emit ONLY the JSON array, no prose.
```

---

## 5. error-handling

**Reading strategy.** Find every `try`/`except`/`catch` block (or a language's equivalent error-
handling construct) in the batch and, for each one, ask three questions in order: does it swallow the
exception (an empty or near-empty handler that logs nothing and re-raises nothing)? does it lose the
original exception/context on the way out (catching a specific error and re-raising a generic one
without chaining the cause, or logging only a message string instead of the exception object/
stack)? and if it retries, does the retry have a cap and a backoff, or can it spin/storm indefinitely
on a persistent failure? Separately, look for **partial-failure** shapes — a sequence of related writes
or state changes where an exception after the first N of them leaves the system in an inconsistent
state with no rollback or compensation (half a transaction committed, one of two related records
updated).

**Example patterns/anti-patterns:**
- Empty catch/except: `try: risky() except Exception: pass` or `try { risky() } catch (e) {}` — the
  failure is silently discarded with no log, no re-raise, no fallback behavior.
- Lost original exception: `except SpecificError as e: raise GenericError("failed")` with no `from e`
  (Python) / no `{ cause: e }` (JS `Error` options) — the stack trace and root cause are gone from the
  propagated error, making the eventual failure undiagnosable.
- Retry storm: a `while True: try: call() except: continue` or a fixed-delay retry loop with no
  maximum attempt count and no exponential backoff — a persistently-down dependency gets hammered at
  full request rate instead of backing off.
- Partial-failure left inconsistent: a function that writes to two systems/tables in sequence (e.g.
  debit account A, then credit account B) where an exception after the first write and before the
  second leaves the debit committed with no matching credit and no compensating transaction.
- Catching too broad and continuing as if nothing happened: catching a bare `Exception`/`Error`
  around a large block, logging nothing, and returning a default/empty value that the caller then
  treats as a legitimate successful result.

**Prompt text:**

```
You are reviewing a batch of files for ERROR-HANDLING bugs only — swallowed exceptions (an empty
or near-empty catch/except), an error path that loses the original exception/context on the way
out, retry logic with no backoff or cap (retry storms), and partial-failure states left
inconsistent (e.g. half a multi-step operation committed with no rollback/compensation). Do not
report anything outside this dimension.

Files in this batch:
{files}

Repo map (directory tree + module-name summary — use this to check whether a caught-and-swallowed
error here is actually expected to propagate to a handler defined elsewhere that never receives
it):
{repo_map_summary}

For each file, find every try/except/catch block. For each, check: is the exception swallowed
(no log, no re-raise, no fallback)? Does re-raising lose the original cause/stack (no chaining)?
If this is a retry loop, does it have both a maximum attempt count AND backoff between attempts?
Separately, find every multi-step operation (sequential writes to two systems, a multi-record
update) and check whether a failure partway through leaves the system in an inconsistent state
with no rollback or compensating action.

Report a finding only when you can point to a concrete line backing it. Severity ceiling for this
dimension is "blocking" — use it for a swallowed error that hides a real failure from the
caller/operator, an unbounded retry storm, or a partial-failure that corrupts data; use a lower
severity for a lost-context re-raise that is otherwise handled correctly.

Write your findings to: {output_path}

Each finding must be a JSON object with exactly these fields:
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "error-handling"
}

If this batch turns up nothing for this dimension, write an empty JSON array `[]` to
{output_path} so the file still exists — do not omit the file, do not write prose instead.
Emit ONLY the JSON array, no prose.
```

---

## 6. performance

**Reading strategy.** Look for the shape of an algorithm or a call pattern **relative to input size**,
not for a single slow-looking line in isolation — this dimension is about behavior that degrades as
data grows, not about a one-off inefficiency on a fixed-size input. For every loop that makes a
network/database call inside it, ask "could this be one call outside the loop instead of N calls
inside it?" (the N+1 pattern). For every nested loop or repeated linear scan over the same collection,
ask "is there a data structure (a set, a dict/map, an index) that would turn this into a single pass?"
For every place data is accumulated into memory (a list, a buffer, a cache with no eviction), ask
"is there a bound on how large this can grow, and what happens when the input is larger than expected?"
For anything reading a large/growing dataset, check for pagination or streaming rather than a single
unbounded fetch. This dimension's findings are always non-blocking — the ceiling is `major`, never
`blocking`.

**Example patterns/anti-patterns:**
- N+1 query: a loop over a list of parent records where each iteration issues a separate query/API
  call to fetch a related child record, instead of one batched query (`WHERE id IN (...)`, a
  `JOIN`, or a bulk-fetch API) before or outside the loop.
- Unbounded in-memory growth: a cache/dict that only ever gets keys added, never evicted or capped, so
  memory grows monotonically with traffic over the process's lifetime; or accumulating an entire
  paginated API response into one list before processing instead of streaming/processing page by page.
- Accidental O(n²) where O(n) is available: checking `if item in list` inside a loop over another list
  (linear membership test repeated n times) where converting the checked collection to a `set`/`dict`
  once would make each check O(1); or `list.index(x)` called inside a loop over the same list.
- Allocation inside a hot loop: constructing a new regex, a new database connection, or a new large
  object on every iteration of a loop instead of once before the loop, when the constructed value is
  loop-invariant.
- Missing pagination/index on a large dataset: a query with no `LIMIT`/pagination fetching a table
  expected to grow unbounded, or a full-table scan where an index on the filtered/sorted column would
  turn it into an index seek.

**Prompt text:**

```
You are reviewing a batch of files for PERFORMANCE issues only — N+1 query/call patterns,
unbounded in-memory growth, accidental O(n^2) where O(n) is achievable, allocation inside a hot
loop, and a missing index/pagination on a large or unbounded dataset. Do not report anything
outside this dimension. Findings in this dimension are NEVER "blocking" severity — the ceiling
is "major".

Files in this batch:
{files}

Repo map (directory tree + module-name summary — use this to check whether a function called
inside a loop here is itself doing a query/network call defined elsewhere, which is the N+1
shape even when the call site in this batch looks innocuous):
{repo_map_summary}

For each file, look for behavior that degrades with input size, not one-off slow lines. For
every loop containing a network/DB call, check whether it could be a single batched call instead.
For every nested loop or repeated linear scan, check whether a set/map/index would remove the
repeated scan. For every unbounded accumulation into memory (a cache, a buffer, a list built from
a paginated source), check whether it has a bound or a streaming alternative. For every allocation
inside a loop, check whether the allocated value is actually loop-invariant and could be hoisted
out.

Report a finding only when you can point to a concrete line backing it, and only when the input
size at which it becomes a real problem is realistic for this codebase, not a purely theoretical
scale. Severity ceiling for this dimension is "major" — never emit "blocking".

Write your findings to: {output_path}

Each finding must be a JSON object with exactly these fields:
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "performance"
}

If this batch turns up nothing for this dimension, write an empty JSON array `[]` to
{output_path} so the file still exists — do not omit the file, do not write prose instead.
Emit ONLY the JSON array, no prose.
```

---

## 7. ci-cd-actions-security

**Reading strategy.** Read every GitHub Actions workflow file (`.github/workflows/*.yml`/`*.yaml`) and
any CI-gate script it invokes (a numbered gate script, an `audit-gates.sh`-style meta-test, a
required-status-check config) as its **own trust-boundary problem, distinct from application code**: a
CI workflow runs with real credentials (`GITHUB_TOKEN`, repo secrets) against untrusted input (a fork's
PR title, branch name, commit message, issue body) far more often than application code does. For each
workflow, trace: does an `env:` or `run:` step interpolate `${{ github.event.* }}` (a PR title, branch
name, issue title/body, a commit message) **directly into a shell command** rather than passing it
through an environment variable first? Does the workflow's trigger include `pull_request_target`
(which runs with the base repo's secrets and permissions) while ALSO checking out the PR's head ref —
the classic secret-exfiltration/RCE combination? Does the workflow's `permissions:` block grant more
than the job actually needs? Are third-party Actions referenced by a mutable tag (`@v3`, `@main`)
instead of a pinned commit SHA? Separately — and specific to this class of finding rather than a
generic security bug — check whether a CI **gate** can be silently skipped, never actually invoked by
any workflow, or made to report success without genuinely asserting anything: an `if:` condition that's
always false, a step whose failure is swallowed by `continue-on-error: true` on a security-relevant
check, or a required status check carrying a `paths:` filter that leaves it perpetually pending on a
non-matching PR (this repo's own `AGENTS.md` documents having been burned by exactly that shape).

**Example patterns/anti-patterns:**
- Script injection via untrusted event data: a step that echoes `${{ github.event.pull_request.title
  }}` straight into a `run:` block — a PR titled with a shell metacharacter sequence that closes the
  quoted string early lets the rest of the title be interpreted as a second, attacker-chosen shell
  statement, because the `${{ }}` interpolation happens before the shell ever parses the line. The fix
  is passing the value through `env:` and referencing the environment variable inside `run:`, never
  interpolating `${{ }}` directly into a script body.
- `pull_request_target` + PR-head checkout: a workflow triggered on `pull_request_target` (secrets
  available) that then runs `actions/checkout@vN` with `ref: ${{ github.event.pull_request.head.sha }}`
  and executes the checked-out code — a fork PR can run arbitrary code with the base repo's secrets.
- Unpinned third-party Action: `uses: some-org/some-action@v1` (a mutable tag, not a commit SHA) from a
  third party — a compromised or malicious upstream release silently runs in every subsequent CI run
  with no diff for a reviewer to catch.
- Overly broad permissions: a workflow's `permissions:` block (or an unset default that inherits
  `write-all`) granting `contents: write`/`id-token: write`/`pull-requests: write` to a job that only
  needs to read code or post a comment.
- A gate that asserts nothing, or never runs: an `if:` condition on a security-relevant step that is
  always false given the trigger it's attached to; `continue-on-error: true` on a step whose failure
  should block the build; a required status check whose trigger carries a `paths:`/`branches:` filter,
  so a PR that never matches it leaves the check permanently pending and the merge gate silently
  unenforced; a numbered gate defined in a meta-test's dispatcher but never added to the main sequence
  that actually runs on every invocation (or the reverse).

**Prompt text:**

```
You are reviewing a batch of files for CI/CD AND GITHUB ACTIONS SECURITY issues only — script
injection via untrusted `${{ github.event.* }}` data interpolated directly into a shell command,
`pull_request_target` combined with checking out and executing the PR's head ref, unpinned
third-party Actions (a mutable tag instead of a commit SHA), overly broad `permissions:` grants,
and a CI gate that can be silently skipped, never actually invoked by any workflow, or made to
report success without genuinely asserting anything (a dead `if:` condition, `continue-on-error:
true` on a security-relevant step, a required check with a `paths:` filter that leaves it
perpetually pending). Do not report anything outside this dimension — and do not report generic
non-CI security issues here even if they're in a `.github/` file; that's the `security` dimension's
job.

Files in this batch:
{files}

Repo map (directory tree + module-name summary — use this to check whether a workflow file in
this batch invokes a gate script or reusable workflow defined elsewhere, and whether a claimed
"this check is required" is actually wired into branch protection rather than merely present):
{repo_map_summary}

For each workflow file (`.github/workflows/*.yml`/`*.yaml`), read its `on:` triggers, its
`permissions:` block, and every `run:`/`uses:` step. Check every `${{ github.event.* }}`
reference for direct shell interpolation vs. safe `env:` passthrough. Check whether
`pull_request_target` is combined with a checkout of the PR's own head ref. Check every `uses:`
for a pinned commit SHA vs. a mutable tag. Check `permissions:` against what the job's steps
actually need. For any file that defines or registers a CI gate/assertion (not just a workflow
YAML — a gate-runner script counts too), check whether the gate can be bypassed, is never invoked,
or has a condition/exception that neuters it.

Report a finding only when you can point to a concrete line backing it, with the actual
attacker-reachable data flow (whose input reaches the shell, and how) named in the
failure_scenario. Severity ceiling for this dimension is "blocking" — use it for anything that
would let an attacker exfiltrate a secret, run code with the base repo's credentials, or silently
disable a security-relevant CI gate.

Write your findings to: {output_path}

Each finding must be a JSON object with exactly these fields:
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "ci-cd-actions-security"
}

If this batch turns up nothing for this dimension, write an empty JSON array `[]` to
{output_path} so the file still exists — do not omit the file, do not write prose instead.
Emit ONLY the JSON array, no prose.
```

---

## 8. dead-code-simplification

**Reading strategy.** This dimension is near-deterministic, which is exactly why it defaults to
single-model (see the top of this file) — look for code whose removal or simplification a reader could
verify is safe just by reading the surrounding control flow and the repo map, without needing to guess
at runtime behavior. Check every `return`/`throw`/`raise`/`break`/`continue` for code immediately after
it in the same block that can never execute. Check every conditional whose branch is always-false (or
always-true) given the type or the value it's guarding, given what's visible in this batch. Use
`{repo_map_summary}` to check whether logic duplicated in this batch already exists as a named helper
elsewhere in the repo — a real duplication finding needs the helper's actual location, not a guess that
"surely something like this exists." Look for an abstraction (an interface, a factory, a strategy
pattern, a config-driven dispatch table) that has exactly one concrete implementation or one call site,
where a direct call would be simpler with no loss of flexibility ever exercised. Look for a feature flag
whose condition is now a compile-time/deploy-time constant (always true or always false) in every place
it's read, meaning one branch of every conditional guarding it is now dead. This dimension's findings
are always `nit` severity.

**Example patterns/anti-patterns:**
- Unreachable code after a `return`/`throw`: a statement following an unconditional `return` in the
  same block, or code after a `throw`/`raise` with no enclosing catch that could redirect control back
  to it.
- Always-false condition: a check for a value that the surrounding type/assignment already guarantees
  can't occur (e.g. checking `if x is None` right after `x = SomeClass()` with no reassignment in
  between), or a dead `elif`/`else if` branch whose condition is logically implied false by an earlier
  branch in the same chain.
- Duplicated logic with an existing helper: a hand-rolled implementation of something (a slugify
  function, a retry wrapper, a date-formatting routine) that duplicates a helper already defined and
  exported elsewhere in the repo — cite the helper's actual file/path from `{repo_map_summary}`, not a
  guess.
- Needlessly deep abstraction for a one-call-site function: an interface/abstract base class with
  exactly one concrete implementation and one call site, where nothing in the repo instantiates a
  second implementation and no test doubles/mocks require the seam — the interface adds indirection
  with no exercised benefit.
- Stale feature flag now unconditional: a flag read via a config/env lookup where every code path that
  sets the flag's value sets it to the same constant (e.g. every environment config in the repo sets
  `FEATURE_X = true`), making the `if not FEATURE_X:` branch dead in practice.

**Prompt text:**

```
You are reviewing a batch of files for DEAD-CODE / SIMPLIFICATION opportunities only —
unreachable code (after a return/throw/raise, or behind an always-false condition), duplicated
logic that an existing helper elsewhere in this repo already implements, a needlessly deep
abstraction for a function with exactly one call site, and a stale feature flag whose guarded
branch is now unconditional in practice. Do not report anything outside this dimension.
Findings in this dimension are always "nit" severity.

Files in this batch:
{files}

Repo map (directory tree + module-name summary — this is the source you MUST cite when claiming
duplicated logic already exists elsewhere; never claim a duplicate exists without naming its
actual file/path from this map, and never claim an abstraction has "only one implementation"
without checking the map for other implementers first):
{repo_map_summary}

For each file, check every return/throw/raise/break/continue for code after it in the same block
that can never run. Check every conditional for a branch that's always-false or always-true given
what's visible in this batch (a value's type, an immediately-preceding assignment, an earlier
branch in the same chain). Check whether logic in this batch duplicates a named helper you can
locate in the repo map. Check whether an interface/abstract class/strategy pattern in this batch
has exactly one concrete implementation and one call site with no second implementer anywhere in
the repo map. Check whether a feature flag's guarded branch is dead because every setter of that
flag in the repo sets it to the same value.

Report a finding only when you can point to a concrete line backing it — a duplication claim must
name the existing helper's real location, not a guess that one "probably" exists. Severity for
this dimension is always "nit".

Write your findings to: {output_path}

Each finding must be a JSON object with exactly these fields:
{
  "id": "<short stable slug, e.g. a short hash of file+line+title>",
  "file": "relative/path/from/repo/root.py",
  "line": 123,
  "severity": "blocking | major | minor | nit",
  "title": "one-line description",
  "failure_scenario": "concrete inputs/state that trigger it -> the wrong output or crash",
  "evidence_quote": "the exact line(s) from the file the finding rests on, quoted verbatim",
  "category": "dead-code-simplification"
}

If this batch turns up nothing for this dimension, write an empty JSON array `[]` to
{output_path} so the file still exists — do not omit the file, do not write prose instead.
Emit ONLY the JSON array, no prose.
```
