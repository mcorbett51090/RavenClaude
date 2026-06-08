# Workpapers Must Support Every Number

**Status:** Absolute rule
**Domain:** US public-accounting / CPA-firm operations
**Applies to:** accounting-firm-cpa

## Why this exists

An attest report is an opinion based on evidence. The workpapers are the evidence trail. A number
in a financial statement that is not supported by a workpaper reference is not evidence — it is
an assertion, and assertions are what the firm is attesting to, not what the firm is producing.
A workpaper file that cannot support every reported figure will not survive a peer review,
a regulatory inspection (PCAOB, state board), or a malpractice claim.

Beyond professional standards, the discipline of source-citing every number protects the firm
from its own errors. The reviewer who cannot find the source of a balance cannot know whether it
is correct. Unsupported numbers in workpapers are also a quality-control signal: if a preparer
skips tick marks, they may also be skipping the verification step itself.

## How to apply

**Do:**
- Assign every workpaper a unique reference (e.g., C-1 for cash, AR-1 for accounts receivable).
- Define a tick-mark legend at the front of the workpaper file; use it consistently.
- Cross-reference every number in every workpaper to a source: client schedule (number and
  cell), bank statement (page and line), confirmation (reference number), third-party document
  (document name, date, and location in the file).
- Write a purpose statement at the top of each workpaper: what audit objective this answers
  and what financial statement assertion it addresses.
- Describe the procedure performed, not just the result. "Agreed ending balance to bank
  statement" is a procedure; "balance is $X" is a result — write both.
- Track open items explicitly; clear them before sign-off.

**Don't:**
- Use "per client" as a tick mark without a reference to the specific client document.
- Write a conclusion workpaper with the conclusion but no procedure documentation.
- Carry forward a prior-year workpaper without updating sources for the current period.
- Mark an item "reviewed" without evidence that the review was performed.
- Leave unsupported balances in the file with a note to "follow up" — follow up before closing
  the file.

## Edge cases / when the rule does NOT apply

- **Compilation (AR-C 80):** a compilation does not require evidence-gathering procedures in
  the same sense as an audit or review. However, the firm's internal quality-control standards
  may still require documentation of the work performed and the information provided by
  management. The "no workpaper support" exception applies only to the level of assurance, not
  to the firm's own quality-control documentation.
- **Agreed-upon procedures (AUP):** the procedures are specified by the engaging party; the
  workpaper must document the specific procedure performed and the finding, but the level of
  assurance documentation is narrower than an audit.

## See also

- `skills/engagement-and-workpaper-management/SKILL.md` — workpaper standards section
- `templates/pbc-request-list.md` — source documents that workpapers will reference
- `hooks/check-accounting-firm-cpa-anti-patterns.sh` — flags numbers with no workpaper reference
- AICPA AU-C 230 (Audit Documentation) `[verify-at-use]`
- PCAOB AS 1215 (Audit Documentation) `[verify-at-use]`

## Provenance

AICPA AU-C 230 and PCAOB AS 1215 codify documentation requirements; the underlying principle
predates the codification. Applies to any attest engagement; the specific documentation
requirements vary by standard tier (audit vs. review vs. compilation vs. AUP).

_Last reviewed: 2026-06-08 by `claude`._
