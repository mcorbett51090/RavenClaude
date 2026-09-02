# repo-review test fixtures

`mini-repo/` is a small **synthetic** Python application (a toy task-tracker, "TaskFlow") used to
measure a bug-review pipeline's recall and precision. It plants exactly one clear, unambiguous bug
per dimension — `correctness`, `security`, `concurrency`, `resource-leaks`, `error-handling`,
`performance`, `dead-code-simplification` — in seven separate files, plus several clean control files
that a good reviewer should flag nothing in.

`mini-repo/` intentionally has **no nested `.git` directory** — a future test harness copies it into
its own throwaway git repo before running the review pipeline against it, so `git init` was
deliberately not run here.

See `mini-repo/PLANTED_DEFECTS.json` for the 7 planted-defect records (file, line range, dimension,
description, and a grep-able evidence hint — a recall check) and `mini-repo/CLEAN_FILES.json` for the
list of clean control files (a precision/false-positive check).
